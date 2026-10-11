"""Local synthetic product engine: append-only persisted actions and frozen closes."""
from __future__ import annotations

import base64
import copy
import csv
import hashlib
import io
import json
import threading
from collections import defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal, localcontext
from pathlib import Path
from uuid import uuid4

from .core import ValidationError, canonical, create_file, digest, require
from .product_seed import seed


def D(value):
    require(not isinstance(value, (float, bool)), 'Số tiền cần được gửi dưới dạng chuỗi thập phân.')
    try:
        result = Decimal(str(value))
    except Exception as exc:
        raise ValidationError('Số tiền không hợp lệ.') from exc
    require(result.is_finite() and len(result.as_tuple().digits) <= 30 and abs(result.as_tuple().exponent) <= 12,
            'Số tiền nằm ngoài phạm vi hỗ trợ.')
    return result


def S(value):
    return format(value, 'f')


def uid():
    return str(uuid4())


def item(items, key):
    found = next((x for x in items if x['id'] == key), None)
    require(found is not None, 'Không tìm thấy tài khoản hoặc tài sản đã chọn.')
    return found


def validate_date(value, state):
    try:
        valid = date.fromisoformat(value).isoformat() == value
    except (ValueError, TypeError):
        valid = False
    require(valid and '1900-01-01' <= value <= '2200-12-31', 'Ngày không hợp lệ (1900–2200).')


def projection(state, cutoff=None):
    with localcontext() as ctx:
        ctx.prec = 60
        from .continuous import enrich
        return enrich(state, _projection(state, cutoff or state['as_of']), cutoff or state['as_of'])


def _projection(state, cutoff):
    accounts = {a['id']: D(a['opening']) if a.get('effective_date',state['opening_date']) <= cutoff else Decimal(0) for a in state['accounts']}
    quantities = {a['id']: D(a['quantity']) for a in state['assets']}
    debt = {a['id']: D(a['opening']) if a.get('effective_date',state['opening_date']) <= cutoff else Decimal(0) for a in state['liabilities']}
    flows = defaultdict(lambda: {'income': Decimal(0), 'expense': Decimal(0), 'principal': Decimal(0)})
    transactions = sorted((t for t in state['transactions'] if t['date'] <= cutoff), key=lambda t: (t['date'], t.get('order', 0)))
    for tx in transactions:
        account = item(state['accounts'], tx['account'])
        amount = D(tx['amount']) * tx.get('direction', 1)
        fee = D(tx.get('fee', '0')) * tx.get('direction', 1)
        rate = D(state['rates'][account['currency']])
        month = flows[tx['date'][:7]]
        k = tx['kind']
        if k == 'income':
            accounts[account['id']] += amount
            month['income'] += amount * rate
        elif k == 'expense':
            accounts[account['id']] -= amount
            month['expense'] += amount * rate
        elif k == 'transfer':
            target = item(state['accounts'], tx['to_account'])
            accounts[account['id']] -= amount
            accounts[target['id']] += D(tx['received_amount'])*tx.get('direction',1) if 'received_amount' in tx else amount * rate / D(state['rates'][target['currency']])
        elif k in ('buy', 'sell'):
            sign = 1 if k == 'buy' else -1
            accounts[account['id']] -= sign * amount
            quantities[tx['asset']] += sign * D(tx['quantity']) * tx.get('direction', 1)
        elif k in ('unclassified_in','transfer_in'):
            accounts[account['id']] += amount
        elif k in ('unclassified_out','transfer_out'):
            accounts[account['id']] -= amount
        elif k in ('lend','collect'):
            sign = 1 if k == 'lend' else -1
            accounts[account['id']] -= sign * amount
            debt[tx['liability']] += sign * amount
        elif k in ('borrow', 'repay'):
            sign = 1 if k == 'borrow' else -1
            accounts[account['id']] += sign * amount
            debt[tx['liability']] += sign * amount
            if k == 'repay':
                month['principal'] += amount * rate
        accounts[account['id']] -= fee
        month['expense'] += fee * rate
    cash_rows = [{**a, 'balance': S(accounts[a['id']]), 'base_value': S(accounts[a['id']] * D(state['rates'][a['currency']]))}
                 for a in state['accounts'] if a.get('effective_date',state['opening_date']) <= cutoff]
    assets = []
    for asset in state['assets']:
        if asset.get('effective_date', state['opening_date']) > cutoff:
            continue
        price = D(asset['price'])
        valued_at = state['opening_date']
        source = 'Bộ dữ liệu giả lập ban đầu'
        for val in sorted((v for v in state['valuations'] if v['asset'] == asset['id'] and v['date'] <= cutoff), key=lambda v: v['date']):
            price, valued_at, source = D(val['price']), val['date'], val['source']
        gross = price * quantities[asset['id']] * D(asset['ownership'])
        embedded = sum((debt[d['id']] for d in state['liabilities'] if d.get('asset_id') == asset['id'] and d.get('loan_direction','BORROWED')=='BORROWED'), Decimal(0))
        net = gross - embedded
        assets.append({**asset, 'quantity': S(quantities[asset['id']]), 'price': S(price), 'value': S(gross),
                       'embedded_debt': S(embedded), 'equity': S(net), 'base_value': S(gross * D(state['rates'][asset['currency']])),
                       'base_equity': S(net * D(state['rates'][asset['currency']])), 'valued_at': valued_at, 'valuation_source': source})
    debts = [{**d, 'balance': S(debt[d['id']]), 'base_value': S(debt[d['id']] * D(state['rates'][d['currency']]))}
             for d in state['liabilities'] if d.get('effective_date',state['opening_date']) <= cutoff]
    cash_total = sum((D(a['base_value']) for a in cash_rows), Decimal(0))
    receivables = [d for d in debts if d.get('loan_direction')=='LENT']
    debts = [d for d in debts if d.get('loan_direction','BORROWED')=='BORROWED']
    receivable_total = sum((D(d['base_value']) for d in receivables), Decimal(0))
    debt_total = sum((D(d['base_value']) for d in debts), Decimal(0))
    transit_total = sum((D(m['amount_out'])*D(state['rates'][m['currency_out']]) for m in state.get('transfer_matches',[]) if m['from_date']<=cutoff<m['to_date']),Decimal(0))
    gross_total = transit_total + receivable_total + cash_total + sum((D(a['base_value']) for a in assets), Decimal(0))
    liquid = cash_total + sum((D(a['base_value']) for a in assets if a['liquid']), Decimal(0))
    allocation = defaultdict(Decimal)
    allocation['CASH'] = cash_total
    if receivable_total: allocation['RECEIVABLE'] = receivable_total
    if transit_total: allocation['IN_TRANSIT'] = transit_total
    for a in assets:
        allocation[a['class']] += D(a['base_equity'])
    economic = sum(allocation.values())
    risks = []
    for a in assets:
        weight = D(a['base_equity']) / economic * 100 if economic > 0 else Decimal(0)
        a['weight'] = S(weight)
        if weight > D(state['policy']['single_asset_limit']):
            risks.append({'id': 'concentration-' + a['id'], 'title': 'Tập trung vào ' + a['name'],
                          'detail': f"Tỷ trọng {weight:.1f}% vượt mức thử nghiệm {state['policy']['single_asset_limit']}%.",
                          'severity': 'review', 'asset': a['id']})
    if economic > 0 and allocation['CRYPTO'] / economic * 100 > D(state['policy']['crypto_limit']):
        risks.append({'id': 'crypto', 'title': 'Crypto vượt tỷ trọng thử nghiệm', 'detail': 'Review cơ cấu vốn; không tự động bán.', 'severity': 'review'})
    reserve = sum((D(a['base_value']) for a in cash_rows if a['pool'] == 'RESERVE'), Decimal(0))
    if reserve < D(state['policy']['cash_floor']):
        risks.append({'id': 'reserve', 'title': 'Dự phòng dưới mức mục tiêu', 'detail': 'Xem xét bổ sung quỹ dự phòng.', 'severity': 'review'})
    current = flows[cutoff[:7]]
    reconciled = []
    for a in cash_rows:
        candidates = [r for r in state['reconciliations'] if r['account'] == a['id'] and r['cutoff'] == cutoff]
        latest = candidates[-1] if candidates else None
        valid = latest is not None and D(latest['observed']) == D(a['balance']) and latest['transaction_digest'] == transaction_digest(state, cutoff)
        reconciled.append({'account': a['id'], 'name': a['name'], 'balance': a['balance'], 'currency': a['currency'],
                           'matched': valid, 'observed': latest['observed'] if latest else None})
    pending = sum(row['status'] == 'PENDING' for batch in state['imports'] for row in batch['rows'])
    return {'cutoff': cutoff, 'accounts': cash_rows, 'assets': assets, 'liabilities': debts, 'receivables':receivables, 'receivable_total':S(receivable_total), 'in_transit_total':S(transit_total),
            'net_worth': S(gross_total - debt_total), 'gross_assets': S(gross_total), 'cash': S(cash_total),
            'debt': S(debt_total), 'liquid_assets': S(liquid), 'liquid_net_worth': S(liquid - debt_total),
            'income': S(current['income']), 'expense': S(current['expense']), 'free_cash_flow': S(current['income'] - current['expense']),
            'principal_paid': S(current['principal']), 'reserve': S(reserve),
            'allocation': [{'class': k, 'value': S(v), 'weight': S(v / economic * 100 if economic else Decimal(0))} for k, v in allocation.items()],
            'flows': [{'month': k, **{x:S(v) for x,v in f.items()}, 'free_cash_flow': S(f['income']-f['expense'])} for k,f in sorted(flows.items())],
            'risks': risks, 'reconciliation': reconciled, 'pending_imports': pending,
            'can_close': all(r['matched'] for r in reconciled) and pending == 0 and not any(b['issues'] and not b['archived'] for b in state['imports']),
            'performance_available': False}


def transaction_digest(state, cutoff):
    return digest([t for t in state['transactions'] if t['date'] <= cutoff])


def make_transaction(state, data):
    kind = data.get('kind')
    require(kind in {'income','expense','transfer','buy','sell','borrow','repay','lend','collect','unclassified_in','unclassified_out'}, 'Chọn loại giao dịch hợp lệ.')
    account = item(state['accounts'], data.get('account'))
    validate_date(data.get('date'), state)
    require(data['date'] >= account.get('effective_date',state['opening_date']), 'Giao dịch trước ngày số dư đầu tài khoản; khai báo tài khoản với mốc bắt đầu phù hợp.')
    amount = D(data.get('amount'))
    fee = D(data.get('fee', '0'))
    require(amount > 0 and fee >= 0, 'Số tiền phải lớn hơn 0; phí không âm.')
    description = str(data.get('description', '')).strip()
    require(description and len(description) <= 500, 'Nhập nội dung giao dịch (tối đa 500 ký tự).')
    tx = {'id': uid(), 'date': data['date'], 'kind': kind, 'account': account['id'], 'amount': S(amount),
          'fee': S(fee), 'currency': account['currency'], 'description': description,
          'source': str(data.get('source', 'Người dùng nhập · thử nghiệm'))[:200], 'direction': 1,
          'order': len(state['transactions'])}
    for key in ('party','component','group','source_row_id','source_batch','source_reference','distinct_reason','correction_of'):
        if data.get(key): tx[key]=str(data[key])[:500]
    if 'economic_order' in data: tx['economic_order']=int(data['economic_order'])
    if data.get('party'): item(state.get('parties',[]),data['party'])
    if data.get('component')=='interest': require(data.get('liability'),'Tiền lãi cần gắn khoản vay.')
    if kind == 'transfer':
        target = item(state['accounts'], data.get('to_account'))
        require(target['id'] != account['id'], 'Chọn hai tài khoản khác nhau.')
        if account['pool'] == 'INVESTMENT' and target['pool'] == 'TRADING':
            decision = item(state['decisions'], data.get('decision'))
            require(decision['status'] == 'APPROVED' and decision['category'] == 'CAPITAL' and
                    decision.get('from_account') == account['id'] and decision.get('to_account') == target['id'] and
                    D(decision['amount']) == amount and not decision.get('executed'), 'Cần quyết định phân bổ đúng số tiền, đã duyệt và chưa thực hiện.')
            tx['decision'] = decision['id']
        elif data.get('decision'):
            decision = item(state['decisions'], data['decision'])
            require(decision['status'] == 'APPROVED' and not decision.get('executed') and
                    decision.get('from_account') == account['id'] and decision.get('to_account') == target['id'] and
                    D(decision['amount']) == amount, 'Quyết định không khớp giao dịch.')
            tx['decision'] = decision['id']
        require(data['date'] >= target.get('effective_date',state['opening_date']), 'Tài khoản nhận chưa bắt đầu theo dõi tại ngày này.')
        if data.get('received_amount'):
            require(D(data['received_amount'])>0, 'Số nhận thực tế phải dương.')
            if target['currency']==account['currency']: require(D(data['received_amount'])==amount,'Chuyển cùng đơn vị phải khớp số tiền; phí nhập riêng.')
            tx['received_amount']=S(D(data['received_amount']))
        elif target['currency']!=account['currency']:
            require(state.get('continuous_version') is None, 'Chuyển khác tiền tệ cần số tiền thực nhận; không dùng tỷ giá báo cáo để đoán.')
        tx['to_account'] = target['id']
    if kind in ('buy','sell'):
        asset = item(state['assets'], data.get('asset'))
        require(asset['class'] in {'STOCK','CRYPTO'} and asset['currency'] == account['currency'], 'Tài sản mua/bán phải cùng đơn vị với tài khoản thanh toán.')
        require(asset.get('effective_date',state['opening_date']) <= data['date'],'Giao dịch trước ngày bổ sung tài sản.')
        quantity = D(data.get('quantity'))
        require(quantity > 0, 'Số lượng phải lớn hơn 0.')
        custody=data.get('custody_account') or account['id']
        holding_account=item(state['accounts'],custody)
        require(data['date']>=holding_account.get('effective_date',state['opening_date']),'Nơi giữ chưa bắt đầu tại ngày giao dịch.')
        tx.update(asset=asset['id'], quantity=S(quantity),custody_account=custody)
    elif data.get('asset'):
        item(state['assets'], data['asset'])
        tx['asset'] = data['asset']
    if kind in ('borrow','repay','lend','collect') or data.get('liability'):
        debt = item(state['liabilities'], data.get('liability'))
        require(debt.get('effective_date',state['opening_date']) <= data['date'],'Giao dịch trước ngày bổ sung khoản nợ.')
        require(debt['currency'] == account['currency'], 'Khoản nợ và tài khoản cần cùng đơn vị.')
        if kind in ('borrow','repay','lend','collect'):
            require((debt.get('loan_direction','BORROWED')=='LENT')==(kind in ('lend','collect')), 'Loại giao dịch không khớp chiều vay / cho vay.')
        if data.get('component')=='interest':
            require(kind==('income' if debt.get('loan_direction')=='LENT' else 'expense'),'Chiều tiền lãi không khớp khoản vay.')
        tx['liability'] = debt['id']
    return tx


def check_balances(state):
    # Validate each day's closing position, including backdated entries.
    cutoffs=sorted({t['date'] for t in state['transactions']} | {x['date'] for x in state.get('custody_moves',[])} | {state['as_of']})
    for cutoff in cutoffs:
        view = projection(state,cutoff)
        require(all(D(a['balance']) >= 0 for a in view['accounts']), 'Không đủ tiền trong tài khoản ở ngày '+cutoff+'. Bản thử không cho phép thấu chi.')
        require(all(D(a['quantity']) >= 0 for a in view['assets']), 'Không đủ số lượng tài sản để bán ở ngày '+cutoff+'.')
        require(all(D(a['balance']) >= 0 for a in view['liabilities']+view.get('receivables',[])), 'Số tiền trả gốc vượt dư nợ ở ngày '+cutoff+'.')

        if state.get('continuous_version'):
            require(all(D(h['quantity'])>=0 for h in view['holdings']), 'Không đủ số lượng tại nơi giữ. Phân bổ tài sản chưa gắn tài khoản trước khi bán/chuyển.')

class ProductStore:
    def __init__(self, directory):
        self.root = Path(directory)
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.lock = threading.RLock()
        if not list(self.root.glob('*.json')):
            initial = seed()
            # Recorded as simulated evidence; never presented as bank reconciliation.
            view = projection(initial)
            initial['reconciliations'] = [{'account': a['id'], 'observed': a['balance'], 'cutoff': initial['as_of'],
                                           'source':'Số dư đối chiếu giả lập', 'transaction_digest': transaction_digest(initial, initial['as_of'])} for a in view['accounts']]
            for cutoff in ('2026-07-31','2026-08-31'):
                report = projection(initial, cutoff)
                initial['snapshots'].append({'id':uid(), 'cutoff':cutoff, 'version':1, 'report':report,
                                             'hash':digest(report), 'note':'Kỳ lịch sử giả lập; dùng để thử so sánh.', 'restates':None})
            self._write('INITIALIZE', initial, None, 'seed')

    def events(self):
        result, previous = [], None
        for index, path in enumerate(sorted(self.root.glob('*.json')), 1):
            event = json.loads(path.read_text())
            checksum = event.pop('hash')
            require(path.name == f'{index:08d}.json' and event['previous'] == previous and digest(event) == checksum,
                    'Lịch sử lưu trữ không khớp. Hãy khôi phục từ bản sao lưu đã kiểm tra.')
            event['hash'] = checksum
            result.append(event)
            previous = checksum
        return result

    def _write(self, kind, state, previous, request_id):
        index = len(list(self.root.glob('*.json'))) + 1
        event = {'id':uid(), 'sequence':index, 'kind':kind, 'state':state, 'previous':previous,
                 'request_id':request_id, 'at':datetime.now(timezone.utc).isoformat()}
        event['hash'] = digest(event)
        create_file(self.root / f'{index:08d}.json', canonical(event))

    def state(self):
        with self.lock:
            return copy.deepcopy(self.events()[-1]['state'])

    def view(self):
        with self.lock:
            events = self.events()
            state = copy.deepcopy(events[-1]['state'])
            from .continuous import duplicate_candidates
            for batch in state['imports']:
                for row in batch['rows']:
                    if row['status']=='PENDING': row['duplicate_candidates']=duplicate_candidates(state,row)
            return {'state':state,'report':projection(state),'version':events[-1]['sequence']}

    def apply(self, action, data, request_id):
        with self.lock, localcontext() as ctx:
            ctx.prec = 60
            require(isinstance(request_id,str) and 1 <= len(request_id) <= 100, 'Yêu cầu cần mã định danh.')
            events = self.events()
            if any(e['request_id'] == request_id for e in events):
                return self.view()
            s = copy.deepcopy(events[-1]['state'])
            detail = self._change(s, action, data)
            s['audit'].append({'id':uid(),'at':datetime.now(timezone.utc).isoformat(),'action':action,
                               'detail':detail,'actor':'Dũng · vai trò thử nghiệm'})
            self._write(action, s, events[-1]['hash'], request_id)
            return self.view()

    def _change(self, s, action, d):
        from .continuous import dispatch
        handled=dispatch(self,s,action,d)
        if handled is not None:
            s['continuous_version']=1
            return handled
        if action == 'transaction':
            tx = make_transaction(s,d)
            s['transactions'].append(tx)
            s['as_of']=max(s['as_of'],tx['date'])
            check_balances(s)
            if tx.get('decision'):
                item(s['decisions'],tx['decision'])['executed'] = tx['id']
            return tx['description']
        if action == 'correct':
            original = item(s['transactions'], d.get('id'))
            require(original.get('direction',1) == 1 and not original.get('correction_of') and not original.get('decision') and not original.get('source_row_id') and not original.get('group'),
                    'Chọn giao dịch gốc thông thường; giao dịch thực thi quyết định cần review riêng.')
            require(not any(c['original'] == original['id'] for c in s['corrections']), 'Giao dịch đã có bản sửa.')
            require(str(d.get('reason','')).strip(), 'Nhập lý do sửa sai.')
            reversal = {**original,'id':uid(),'direction':-1,'correction_of':original['id'],'order':len(s['transactions'])}
            replacement = make_transaction(s, {**original, 'amount':d.get('amount'), 'description':d.get('description') or original['description']})
            replacement['correction_of'] = original['id']
            s['transactions'].extend([reversal,replacement])
            s['corrections'].append({'id':uid(),'original':original['id'],'reversal':reversal['id'],'replacement':replacement['id'],'reason':str(d['reason'])[:500]})
            check_balances(s)
            return 'Sửa bằng bản đảo và bản thay thế: ' + original['description']
        if action == 'valuation':
            asset = item(s['assets'], d.get('asset'))
            validate_date(d.get('date'), s)
            price = D(d.get('price'))
            require(price > 0 and str(d.get('source','')).strip(), 'Cần giá trị dương và nguồn định giá.')
            s['valuations'].append({'id':uid(),'asset':asset['id'],'date':d['date'],'price':S(price),'source':str(d['source'])[:300]})
            return 'Cập nhật định giá ' + asset['name']
        if action == 'asset':
            require(d.get('class') in {'STOCK','CRYPTO','PROPERTY','BUSINESS'}, 'Chọn nhóm tài sản.')
            require(d.get('currency') in s['rates'], 'Đơn vị chưa hỗ trợ.')
            require(str(d.get('name','')).strip(), 'Nhập tên tài sản.')
            quantity,price,ownership = D(d.get('quantity')),D(d.get('price')),D(d.get('ownership','1'))
            require(quantity>=0 and price>0 and 0<ownership<=1,'Số lượng không âm, giá dương và sở hữu trong (0, 1].')
            require(d.get('reason'), 'Ghi lý do bổ sung tài sản vào phạm vi.')
            s['assets'].append({'id':uid(),'name':str(d['name'])[:100],'class':d['class'],'currency':d['currency'],
                                'quantity':S(quantity),'price':S(price),'ownership':S(ownership),
                                'liquid':d['class'] in {'STOCK','CRYPTO'},'pool':'INVESTMENT','detail':{},
                                'effective_date':s['as_of'],'scope_note':str(d['reason'])[:300]})
            return 'Bổ sung phạm vi tài sản: ' + d['name']
        if action == 'liability':
            require(d.get('currency') in s['rates'] and str(d.get('name','')).strip() and d.get('reason'),'Nhập tên, đơn vị và lý do bổ sung nợ.')
            require(D(d.get('opening'))>=0 and D(d.get('interest'))>=0 and D(d.get('next_payment'))>=0,'Số dư và lãi không âm.')
            date.fromisoformat(d.get('due',''))
            if d.get('asset_id'):
                asset=item(s['assets'],d['asset_id'])
                require(asset['currency']==d['currency'],'Nợ bảo đảm cần cùng đơn vị với tài sản.')
            s['liabilities'].append({'id':uid(),'name':str(d['name'])[:100],'currency':d['currency'],'opening':S(D(d['opening'])),
                'interest':S(D(d['interest'])),'next_payment':S(D(d['next_payment'])),'due':d['due'],'asset_id':d.get('asset_id') or None,
                'effective_date':s['as_of'],'scope_note':str(d['reason'])[:300]})
            return 'Bổ sung khoản nợ: '+str(d['name'])
        if action == 'reconcile-demo':
            view=projection(s)
            for a in view['accounts']:
                s['reconciliations'].append({'account':a['id'],'observed':a['balance'],'cutoff':s['as_of'],
                    'source':'Nguồn đối soát giả lập lấy từ sổ; không phải xác nhận bank','transaction_digest':transaction_digest(s,s['as_of'])})
            return 'Đối soát tất cả bằng nguồn giả lập.'
        if action == 'reconcile':
            account = item(s['accounts'],d.get('account'))
            amount = D(d.get('observed'))
            require(amount>=0 and str(d.get('source','')).strip(),'Nhập số dư đối chiếu và nguồn.')
            cutoff = d.get('cutoff',s['as_of'])
            validate_date(cutoff,s)
            s['reconciliations'].append({'account':account['id'],'observed':S(amount),'cutoff':cutoff,
                                         'source':str(d['source'])[:300],'transaction_digest':transaction_digest(s,cutoff)})
            return 'Đối soát ' + account['name']
        if action == 'decision':
            category = d.get('category','REVIEW')
            require(category in {'REVIEW','CAPITAL'},'Loại quyết định không hợp lệ.')
            require(d.get('title') and d.get('reason'),'Nhập nội dung và lý do quyết định.')
            decision = {'id':uid(),'title':str(d['title'])[:150],'reason':str(d['reason'])[:500],
                        'category':category,'status':'PROPOSED','date':s['as_of'],'executed':None}
            if category=='CAPITAL':
                source,target = item(s['accounts'],d.get('from_account')),item(s['accounts'],d.get('to_account'))
                require(source['id']!=target['id'] and D(d.get('amount'))>0,'Kiểm tra tài khoản và số tiền phân bổ.')
                decision.update(from_account=source['id'],to_account=target['id'],amount=S(D(d['amount'])),currency=source['currency'])
            s['decisions'].append(decision)
            return 'Đề xuất: '+decision['title']
        if action == 'approve':
            decision = item(s['decisions'], d.get('id'))
            require(decision['status']=='PROPOSED','Quyết định không còn chờ duyệt.')
            decision.update(status='APPROVED',approved_by=s['owner'],approved_at=datetime.now(timezone.utc).isoformat())
            return 'Duyệt thử nghiệm: '+decision['title']
        if action == 'execute':
            decision = item(s['decisions'],d.get('id'))
            require(decision['category']=='CAPITAL' and decision['status']=='APPROVED' and not decision.get('executed'),'Quyết định chưa sẵn sàng thực hiện.')
            return self._change(s,'transaction',{'kind':'transfer','account':decision['from_account'],'to_account':decision['to_account'],
                                                'amount':decision['amount'],'date':s['as_of'],'description':decision['title'],'decision':decision['id']})
        if action == 'policy':
            for key in ('single_asset_limit','crypto_limit','cash_floor'):
                value = D(d.get(key))
                require(value>=0 and (value<=100 if key!='cash_floor' else value<=1000000000),'Policy nằm ngoài giới hạn hợp lệ.')
                s['policy'][key] = S(value)
            return 'Cập nhật policy thử nghiệm; policy cũ giữ trong lịch sử.'
        if action == 'close':
            cutoff = d.get('cutoff',s['as_of'])
            validate_date(cutoff,s)
            report = projection(s,cutoff)
            require(report['can_close'],'Chưa chốt được: hãy đối soát tài khoản và xử lý các dòng nhập còn chờ.')
            require(str(d.get('note','')).strip(),'Nhập ghi chú duyệt kỳ.')
            old = [c for c in s['snapshots'] if c['cutoff']==cutoff]
            if old:
                require(d.get('restates')==old[-1]['id'],'Kỳ đã chốt; chọn lập bản restatement, không ghi đè.')
            s['snapshots'].append({'id':uid(),'cutoff':cutoff,'version':len(old)+1,'report':report,'hash':digest(report),'policy':copy.deepcopy(s['policy']),'rates':copy.deepcopy(s['rates']),
                                   'note':str(d['note'])[:500],'restates':old[-1]['id'] if old else None,'approved_by':s['owner']})
            return f'Chốt báo cáo tại {cutoff}, phiên bản {len(old)+1}'
        if action == 'import':
            require(d.get('filename') and d.get('content'),'Chọn file nhập.')
            try:
                raw = base64.b64decode(d['content'],validate=True)
            except Exception as exc:
                raise ValidationError('Nội dung file không hợp lệ.') from exc
            require(len(raw)<=3_000_000,'File thử nghiệm tối đa 3 MB.')
            sha=hashlib.sha256(raw).hexdigest()
            require(not any(b['sha256']==sha for b in s['imports']),'File này đã được nhập. Không tạo giao dịch trùng.')
            rows,issues=[],[]
            if d['filename'].lower().endswith('.csv'):
                try:
                    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
                    require({'date','amount','account','description'} <= set(reader.fieldnames or []),'CSV cần date, amount, account, description; có thể thêm kind.')
                    for n,row in enumerate(reader,2):
                        require(len(rows)<1000,'Tối đa 1.000 dòng mỗi lần nhập.')
                        try:
                            validate_date(row['date'],s);account=item(s['accounts'],row['account']);amount=D(row['amount'])
                            require(amount>0,'Số tiền dương.')
                            kind=row.get('kind','')
                            require(kind in {'income','expense',''},'CSV thử nghiệm chỉ nhận thu/chi; loại khác nhập trực tiếp.')
                            rows.append({'id':uid(),'date':row['date'],'amount':S(amount),'account':account['id'],
                                         'currency':account['currency'],'description':row['description'],'suggested_kind':kind,
                                         'status':'PENDING','source_row':n})
                        except (ValidationError,KeyError) as exc:
                            issues.append(f'Dòng {n}: {exc}')
                except UnicodeError as exc:
                    raise ValidationError('CSV cần mã hóa UTF-8.') from exc
            elif d['filename'].lower().endswith('.xlsx'):
                from .bank_statement import parse_statement
                try:
                    result=parse_statement(raw)
                except Exception as exc:
                    raise ValidationError('XLSX không khớp mẫu bank đã hỗ trợ.') from exc
                issues=[i['code'] for i in result['issues']]
                issues.append('Sao kê bank cần xác nhận mapping tài khoản và số dư. Bản thử chỉ lưu vào vùng chờ; không tự ghi sổ.')
                rows=[{'id':t['raw_record_id'],'date':t['effective_date'],'amount':str(abs(D(t['signed_amount']))),
                       'currency':t['currency'],'description':t['description'],'status':'PENDING','source_row':t['source_row'],
                       'suggested_kind':'','account':None} for t in result['transactions']]
            else:
                raise ValidationError('Chọn CSV hoặc XLSX sao kê theo mẫu.')
            require(rows or issues,'File không có giao dịch.')
            s['imports'].append({'id':uid(),'filename':str(d['filename'])[:150],'sha256':sha,'raw_base64':d['content'],
                                 'rows':rows,'issues':issues,'archived':False})
            return 'Nhập vào vùng chờ: '+d['filename']
        if action=='import-row':
            batch=item(s['imports'],d.get('batch'));row=item(batch['rows'],d.get('row'))
            require(row['status']=='PENDING','Dòng đã được xử lý.')
            if d.get('reject'):
                require(d.get('reason'),'Nhập lý do không ghi sổ.')
                row.update(status='REJECTED',reason=str(d['reason'])[:300])
            else:
                require(not batch['issues'],'File có lỗi; không tự bỏ qua để ghi sổ.')
                tx=make_transaction(s,{**row,'kind':d.get('kind'),'source':batch['filename']})
                s['transactions'].append(tx);check_balances(s)
                row.update(status='ACCEPTED',transaction=tx['id'])
            return 'Review dòng nhập: '+row['description'][:100]
        if action=='archive-import':
            batch=item(s['imports'],d.get('id'))
            require(d.get('reason'),'Nhập lý do lưu lại và không ghi sổ.')
            for row in batch['rows']:
                if row['status']=='PENDING':row.update(status='REJECTED',reason=str(d['reason'])[:300])
            batch['archived']=True
            return 'Giữ chứng từ, không ghi sổ: '+batch['filename']
        raise ValidationError('Thao tác chưa được hỗ trợ.')

    def backup(self):
        with self.lock:
            events=self.events()
            return {'format':'pcms-backup-1','events':events,'checksum':digest(events)}

    def restore(self, bundle, request_id):
        with self.lock:
            require(bundle.get('format')=='pcms-backup-1' and digest(bundle.get('events'))==bundle.get('checksum'),'Bản sao lưu không khớp checksum.')
            previous=None
            events=bundle['events']
            require(events,'Backup rỗng.')
            for index,e in enumerate(events,1):
                body={k:v for k,v in e.items() if k!='hash'}
                require(e['sequence']==index and e['previous']==previous and digest(body)==e['hash'],'Lịch sử backup không hợp lệ.')
                previous=e['hash']
            state=copy.deepcopy(events[-1]['state'])
            require(state.get('mode')=='SYNTHETIC' and state.get('schema')=='pcms-product-1','Chỉ khôi phục bản thử PCMS.')
            for snap in state['snapshots']:
                require(digest(snap['report'])==snap['hash'],'Snapshot backup không khớp.')
            check_balances(state)
            current=self.events()
            if any(e['request_id']==request_id for e in current):return self.view()
            state['audit'].append({'id':uid(),'at':datetime.now(timezone.utc).isoformat(),'action':'RESTORE','detail':'Khôi phục thành phiên bản mới; lịch sử trước vẫn lưu.','actor':state['owner']})
            self._write('RESTORE',state,current[-1]['hash'],request_id)
            return self.view()
