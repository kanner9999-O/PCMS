"""Continuous account workflow, source review and counterparty loan subledger.
All mutations run inside ProductStore's single atomic, append-only action.
"""
import base64
import copy
import csv
import hashlib
import io
from collections import defaultdict
from decimal import Decimal
from datetime import date
from .core import require, ValidationError, digest


def active_transactions(s, cutoff=None):
    retired={c['original'] for c in s['corrections']}
    return [t for t in s['transactions'] if t.get('direction',1)==1 and t['id'] not in retired and (cutoff is None or t['date']<=cutoff)]


def cash_delta(t, account):
    from .product import D
    sign=t.get('direction',1)
    amount=D(t['amount']); fee=D(t.get('fee','0'))
    if t['account']==account:
        incoming=t['kind'] in {'income','borrow','collect','unclassified_in','transfer_in','sell'}
        return ((amount if incoming else -amount)-fee)*sign
    if t.get('to_account')==account:
        return D(t.get('received_amount',t['amount']))*sign
    return Decimal(0)


def holdings(s, cutoff):
    from .product import D,S
    q=defaultdict(Decimal)
    for a in s['assets']:
        if a.get('effective_date',s['opening_date'])<=cutoff:
            q[(a.get('custody_account','UNASSIGNED'),a['id'])]+=D(a['quantity'])
    for t in s['transactions']:
        if t['date']<=cutoff and t['kind'] in {'buy','sell'}:
            q[(t.get('custody_account','UNASSIGNED'),t['asset'])]+=D(t['quantity'])*t.get('direction',1)*(1 if t['kind']=='buy' else -1)
    for p in s.get('custody_moves',[]):
        if p['date']<=cutoff:
            q[(p['from_account'],p['asset'])]-=D(p['quantity'])
            q[(p['to_account'],p['asset'])]+=D(p['quantity'])
    return [{'account':a,'asset':b,'quantity':S(v)} for (a,b),v in q.items() if v]


def enrich(s, report, cutoff):
    from .product import D,S
    loans=[]
    totals=defaultdict(lambda: {'borrowed':Decimal(0),'lent':Decimal(0),'interest_payable':Decimal(0),'interest_receivable':Decimal(0)})
    for loan in s['liabilities']:
        if loan.get('effective_date',s['opening_date'])>cutoff:continue
        direction=loan.get('loan_direction','BORROWED')
        principal=D(loan['opening']);paid=Decimal(0)
        history=[]
        for t in sorted(active_transactions(s),key=lambda t:(t['date'],t.get('economic_order',t.get('order',0)),t.get('order',0))):
            if t['date']>cutoff or t.get('liability')!=loan['id']:continue
            sign=t.get('direction',1);amount=D(t['amount'])*sign
            change=amount if t['kind'] in {'borrow','lend'} else -amount if t['kind'] in {'repay','collect'} else Decimal(0)
            principal+=change
            if t.get('component')=='interest':paid+=amount
            history.append({**t,'principal_change':S(change),'principal_balance':S(principal)})
        assessed=sum((D(x['amount']) for x in s.get('interest_records',[]) if x['loan']==loan['id'] and x['date']<=cutoff),Decimal(0))
        interest=max(Decimal(0),assessed-paid)
        row={**loan,'balance':S(principal),'interest_assessed':S(assessed),'interest_paid':S(paid),'interest_due':S(interest),
             'interest_credit':S(max(Decimal(0),paid-assessed)),'history':history,'loan_direction':direction,
             'overdue':loan.get('due','9999-12-31')<cutoff and (principal>0 or interest>0)}
        loans.append(row)
        g=totals[(loan.get('party','UNASSIGNED'),loan['currency'])]
        g['borrowed' if direction=='BORROWED' else 'lent']+=principal
        g['interest_payable' if direction=='BORROWED' else 'interest_receivable']+=interest
    unknown=[t for t in active_transactions(s,cutoff) if t['kind'] in {'unclassified_in','unclassified_out'}]
    currency_totals=defaultdict(lambda: defaultdict(Decimal))
    for (_,currency),values in totals.items():
        for key,value in values.items():currency_totals[currency][key]+=value
    report['loan_currency_totals']=[{'currency':c,**{k:S(v) for k,v in vals.items()}} for c,vals in currency_totals.items()]
    report.update(loans=loans,loan_totals=[{'party':p,'currency':c,**{k:S(v) for k,v in vals.items()}} for (p,c),vals in totals.items()],
                  holdings=holdings(s,cutoff),unclassified=len(unknown),unclassified_transactions=unknown,
                  can_close=report['can_close'] and not unknown,
                  data_status='INCOMPLETE_CLASSIFICATION' if unknown else 'CLASSIFIED')
    return report


def account_history(s, account, start, end):
    from .product import D,S,item,validate_date
    a=item(s['accounts'],account);validate_date(start,s);validate_date(end,s)
    require(start<=end,'Ngày bắt đầu phải trước ngày kết thúc.')
    opening_date=a.get('effective_date',s['opening_date'])
    balance=D(a['opening']) if opening_date<=end else Decimal(0)
    opening=balance if opening_date<=start else Decimal(0)
    rows=[];incoming=Decimal(0);outgoing=Decimal(0)
    if start<opening_date<=end:
        rows.append({'id':'opening','date':opening_date,'description':'Số dư bắt đầu theo dõi · không phải thu nhập',
                     'kind':'opening','change':S(balance),'balance':S(balance),'source':a.get('opening_source','Dữ liệu mẫu')})
    for t in sorted(active_transactions(s),key=lambda t:(t['date'],t.get('economic_order',t.get('order',0)),t.get('order',0))):
        if t['date']>end:continue
        delta=cash_delta(t,account)
        if not delta and t['account']!=account and t.get('to_account')!=account:continue
        # Old cross-currency transfers predate explicit received_amount.
        if t.get('to_account')==account and 'received_amount' not in t:
            source=item(s['accounts'],t['account'])
            delta=D(t['amount'])*D(s['rates'][source['currency']])/D(s['rates'][a['currency']])*t.get('direction',1)
        balance+=delta
        if t['date']<start:opening=balance
        else:
            incoming+=max(delta,Decimal(0));outgoing+=max(-delta,Decimal(0))
            rows.append({**t,'change':S(delta),'balance':S(balance)})
    return {'account':a,'from':start,'to':end,'opening':S(opening),'opening_adjustment':a['opening'] if start<opening_date<=end else '0',
            'incoming':S(incoming),'outgoing':S(outgoing),'closing':S(balance),'rows':rows,
            'coverage_note':'Sổ tính từ số dư ban đầu đã khai báo. Không tự chứng minh đã nhận đủ sao kê; đối chiếu nguồn ở từng mốc.'}


def dispatch(store,s,action,d):
    from .product import D,S,uid,item,validate_date,make_transaction,check_balances,projection
    supported={'account','party','loan','loan-link','loan-payment','interest-record','custody-move','classify','match-transfer',
               'continuous-import','import-map','import-row','import-duplicate','report-date'}
    if action not in supported:return None
    s['continuous_version']=1
    def valid_day(day):validate_date(day,s)
    def advance(day):s['as_of']=max(s['as_of'],day)
    def append(data):
        tx=make_transaction(s,data);s['transactions'].append(tx);advance(tx['date']);return tx
    def retire(tx):
        require(tx in active_transactions(s),'Giao dịch đã được thay thế.')
        rev={**tx,'id':uid(),'direction':-1,'correction_of':tx['id'],'order':len(s['transactions'])}
        s['transactions'].append(rev)
        return rev
    if action=='report-date':
        valid_day(d.get('date'));s['as_of']=d['date'];return 'Đổi ngày xem báo cáo: '+d['date']
    if action=='account':
        valid_day(d.get('effective_date'))
        require(d.get('name') and d.get('owner') and d.get('opening_source'),'Cần tên, chủ sở hữu và nguồn số dư ban đầu.')
        require(d.get('type') in {'BANK','EXCHANGE'} and d.get('currency') in s['rates'],'Chọn loại tài khoản và nguyên tệ.')
        require(d.get('pool') in {'OPERATING','RESERVE','INVESTMENT','TRADING'},'Chọn mục đích tài khoản.')
        require(D(d.get('opening'))>=0,'Số dư đầu không âm.')
        s['accounts'].append({'id':uid(),'name':str(d['name'])[:100],'owner':str(d['owner'])[:100],'type':d['type'],
            'currency':d['currency'],'pool':d['pool'],'opening':S(D(d['opening'])),'effective_date':d['effective_date'],
            'opening_source':str(d['opening_source'])[:300]})
        advance(d['effective_date']);return 'Khai báo tài khoản: '+d['name']
    if action=='party':
        require(str(d.get('name','')).strip(),'Nhập tên người / tổ chức.')
        s.setdefault('parties',[]).append({'id':uid(),'name':str(d['name']).strip()[:100],'note':str(d.get('note',''))[:300]})
        return 'Thêm bên liên quan: '+d['name']
    if action=='loan':
        party=item(s.get('parties',[]),d.get('party'));valid_day(d.get('effective_date'));valid_day(d.get('due'))
        require(d['due']>=d['effective_date'],'Ngày đáo hạn trước ngày bắt đầu.')
        require(d.get('loan_direction') in {'BORROWED','LENT'} and d.get('currency') in s['rates'],'Chọn chiều vay và nguyên tệ.')
        require(d.get('name') and d.get('source'),'Nhập mã/tên khoản vay và nguồn xác nhận.')
        require(D(d.get('opening'))>=0 and D(d.get('annual_rate','0'))>=0,'Gốc và lãi suất không âm.')
        s['liabilities'].append({'id':uid(),'name':str(d['name'])[:100],'party':party['id'],'loan_direction':d['loan_direction'],
            'opening':S(D(d['opening'])),'currency':d['currency'],'effective_date':d['effective_date'],'due':d['due'],
            'annual_rate':S(D(d.get('annual_rate','0'))),'terms':str(d.get('terms',''))[:500],'opening_source':str(d['source'])[:300],
            'asset_id':None,'next_payment':'0'})
        advance(d['effective_date']);return 'Khai báo khoản vay: '+d['name']
    if action=='loan-link':
        loan=item(s['liabilities'],d.get('loan'));party=item(s.get('parties',[]),d.get('party'))
        require(d.get('reason'),'Nhập căn cứ gắn chủ nợ.');loan['party']=party['id']
        return 'Gắn '+loan['name']+' với '+party['name']+': '+str(d['reason'])[:300]
    if action=='interest-record':
        loan=item(s['liabilities'],d.get('loan'));valid_day(d.get('date'))
        require(d['date']>=loan.get('effective_date',s['opening_date']) and D(d.get('amount'))>0 and d.get('source'),'Kiểm tra ngày, tiền lãi và căn cứ.')
        s.setdefault('interest_records',[]).append({'id':uid(),'loan':loan['id'],'date':d['date'],'amount':S(D(d['amount'])),'source':str(d['source'])[:300]})
        advance(d['date']);return 'Ghi nhận lãi đã xác nhận: '+loan['name']
    if action=='loan-payment':
        loan=item(s['liabilities'],d.get('loan'));account=item(s['accounts'],d.get('account'))
        require(account['currency']==loan['currency'],'Tài khoản và khoản vay phải cùng đơn vị.')
        principal,interest,fee=D(d.get('principal','0')),D(d.get('interest','0')),D(d.get('fee','0'))
        require(min(principal,interest,fee)>=0 and principal+interest>0,'Gốc/lãi/phí không âm và có số tiền thanh toán.')
        require(D(d.get('total'))==principal+interest,'Tổng gốc + lãi phải bằng số thanh toán (phí ngân hàng nhập riêng).')
        incoming=loan.get('loan_direction','BORROWED')=='LENT';group=uid()
        common={'date':d.get('date'),'account':account['id'],'liability':loan['id'],'party':loan.get('party'),
                'description':d.get('description','Thanh toán '+loan['name']),'group':group,'source':d.get('source','Thanh toán nhập tay')}
        if principal:append({**common,'amount':S(principal),'kind':'collect' if incoming else 'repay','component':'principal','fee':S(fee if not interest else Decimal(0))})
        if interest:append({**common,'amount':S(interest),'kind':'income' if incoming else 'expense','component':'interest','fee':S(fee)})
        check_balances(s);return 'Thanh toán tách gốc / lãi: '+loan['name']
    if action=='custody-move':
        asset=item(s['assets'],d.get('asset'));valid_day(d.get('date'))
        require(asset['class'] in {'STOCK','CRYPTO'},'Chọn cổ phiếu hoặc crypto.')
        target=item(s['accounts'],d.get('to_account'))
        if d.get('from_account')!='UNASSIGNED':item(s['accounts'],d.get('from_account'))
        require(target.get('type','EXCHANGE' if target['pool'] in {'INVESTMENT','TRADING'} else 'BANK')=='EXCHANGE','Nơi nhận phải là tài khoản sàn.')
        require(d.get('from_account')!=target['id'] and D(d.get('quantity'))>0 and d.get('source'),'Cần hai nơi giữ khác nhau, số lượng dương và căn cứ.')
        s.setdefault('custody_moves',[]).append({'id':uid(),'asset':asset['id'],'date':d['date'],'from_account':d['from_account'],
            'to_account':target['id'],'quantity':S(D(d['quantity'])),'source':str(d['source'])[:300]})
        advance(d['date']);check_balances(s);return 'Phân bổ / chuyển nơi giữ: '+asset['name']
    if action=='classify':
        tx=item(s['transactions'],d.get('id'))
        require(tx['kind'] in {'unclassified_in','unclassified_out','income','expense','borrow','repay','lend','collect','buy','sell'} and not tx.get('decision'),'Giao dịch này cần xử lý trong luồng chuyển nội bộ / quyết định.')
        parts=d.get('parts',[]);require(isinstance(parts,list) and 1<=len(parts)<=20,'Cần 1–20 phần phân loại.')
        require(sum((D(p.get('amount')) for p in parts),Decimal(0))==D(tx['amount']),'Tổng các phần phải bằng số tiền gốc.')
        require(D(tx.get('fee','0'))==0,'Phân loại phí từ giao dịch riêng.')
        allowed={'income','borrow','collect','sell'} if cash_delta(tx,tx['account'])>0 else {'expense','repay','lend','buy'}
        require(all(p.get('kind') in allowed for p in parts),'Phân loại phải cùng chiều tiền. Chuyển nội bộ dùng Ghép chuyển tiền.')
        require(d.get('reason'),'Nhập căn cứ phân loại.')
        reversal=retire(tx);ids=[]
        for p in parts:
            require(D(p.get('fee','0'))==0,'Không thêm phí làm thay đổi số tiền nguồn; ghi phí riêng.')
            new=append({**tx,**p,'date':tx['date'],'account':tx['account'],'fee':'0','group':tx['id'],
                        'source':tx['source'],'source_row_id':tx.get('source_row_id'),'correction_of':tx['id'],'economic_order':tx.get('economic_order',tx.get('order',0))})
            ids.append(new['id'])
        s['corrections'].append({'id':uid(),'original':tx['id'],'reversal':reversal['id'],'replacement':ids[0],'replacements':ids,'reason':str(d['reason'])[:500]})
        check_balances(s);return 'Phân loại giao dịch: '+tx['description']
    if action=='match-transfer':
        out=item(s['transactions'],d.get('outgoing'));inc=item(s['transactions'],d.get('incoming'))
        require(out['kind']=='unclassified_out' and inc['kind']=='unclassified_in' and out['account']!=inc['account'],'Chọn hai đầu chuyển chưa phân loại khác tài khoản.')
        require(out in active_transactions(s) and inc in active_transactions(s),'Một đầu chuyển đã được xử lý.')
        require(d.get('reason'),'Nhập căn cứ ghép chuyển tiền.')
        require(out['date']<=inc['date'],'Ngày nhận trước ngày gửi; xác minh ngày nguồn trước khi ghép.')
        source=item(s['accounts'],out['account']);target=item(s['accounts'],inc['account'])
        require(not(source['pool']=='INVESTMENT' and target['pool']=='TRADING') or d.get('decision'),'Chuyển đầu tư sang Trading cần quyết định đã duyệt.')
        # Preserve each leg's original date and amount; no synthetic same-day posting.
        group=uid()
        for old in (out,inc):
            rev=retire(old)
            new={**old,'id':uid(),'kind':'transfer_out' if old is out else 'transfer_in','group':group,'matched_transfer':group,
                 'economic_order':old.get('economic_order',old.get('order',0)),'peer_account':inc['account'] if old is out else out['account'],'correction_of':old['id'],'order':len(s['transactions'])}
            s['transactions'].append(new)
            s['corrections'].append({'id':uid(),'original':old['id'],'reversal':rev['id'],'replacement':new['id'],'reason':str(d['reason'])[:500]})
        if source['currency']==target['currency']:
            require(D(out['amount'])==D(inc['amount']),'Hai đầu cùng tiền tệ phải bằng nhau. Phí cần tách thành giao dịch riêng trước khi ghép.')
        if d.get('decision'):
            dec=item(s['decisions'],d['decision'])
            require(dec['status']=='APPROVED' and not dec.get('executed') and dec.get('from_account')==out['account'] and dec.get('to_account')==inc['account'] and D(dec['amount'])==D(out['amount']),'Quyết định không khớp.')
            dec['executed']=group
        s.setdefault('transfer_matches',[]).append({'id':group,'outgoing':out['id'],'incoming':inc['id'],'from_date':out['date'],'to_date':inc['date'],
            'amount_out':out['amount'],'currency_out':source['currency'],'amount_in':inc['amount'],'currency_in':target['currency'],'reason':str(d['reason'])[:500]})
        check_balances(s);return 'Ghép chuyển nội bộ; giữ nguyên ngày và số tiền hai đầu.'
    if action=='continuous-import':
        try:raw=base64.b64decode(d.get('content',''),validate=True)
        except Exception as exc:raise ValidationError('File không hợp lệ.') from exc
        require(0<len(raw)<=3_000_000,'File cần có dữ liệu, tối đa 3 MB.')
        sha=hashlib.sha256(raw).hexdigest();require(not any(b['sha256']==sha for b in s['imports']),'File này đã được nhập; không ghi trùng.')
        filename=str(d.get('filename',''))[:150];rows=[];issues=[]
        if filename.lower().endswith('.csv'):
            try:reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
            except UnicodeError as exc:raise ValidationError('CSV phải mã hóa UTF-8.') from exc
            require({'date','amount','account','description'}<=set(reader.fieldnames or []),'CSV cần date, amount, account, description; thêm kind hoặc direction để xác định chiều tiền.')
            for n,row in enumerate(reader,2):
                require(n<=1001,'Tối đa 1.000 dòng.')
                try:
                    valid_day(row['date']);a=item(s['accounts'],row['account']);amount=D(row['amount'])
                    require(row['date']>=a.get('effective_date',s['opening_date']),'Giao dịch trước số dư đầu tài khoản.')
                    require(amount>0 and row['description'],'Số tiền dương và có nội dung.')
                    k=row.get('kind','');direction=row.get('direction','').upper()
                    if not direction:direction='IN' if k in {'income','borrow','collect','sell','unclassified_in'} else 'OUT' if k in {'expense','repay','lend','buy','unclassified_out'} else ''
                    require(direction in {'IN','OUT'},'Thiếu chiều tiền IN/OUT; không suy đoán từ số tiền dương.')
                    rows.append({'id':uid(),'date':row['date'],'amount':S(amount),'account':a['id'],'currency':a['currency'],
                        'description':row['description'],'suggested_kind':k,'cash_direction':direction,'status':'PENDING','source_row':n,
                        'reference':row.get('reference',''),'reported_balance':row.get('balance',''),'raw':row})
                except (ValidationError,KeyError) as exc:issues.append(f'Dòng {n}: {exc}')
            batch={'format':'CSV'}
        elif filename.lower().endswith('.xlsx'):
            from .bank_statement import parse_statement
            result=parse_statement(raw)
            issues=[x['code'] for x in result['issues'] if x['code']!='REPEATED_BANK_REFERENCE']
            rows=[{'id':uid(),'date':x['effective_date'],'amount':S(abs(D(x['signed_amount']))),'account':None,'currency':x['currency'],
                   'description':x['description'],'suggested_kind':'','cash_direction':'IN' if D(x['signed_amount'])>0 else 'OUT',
                   'status':'PENDING','source_row':x['source_row'],'reference':x['bank_reference'],'reported_balance':x['reported_balance'],'raw':x}
                  for x in result['transactions']]
            batch={'format':'XLSX','mapping_required':True,'source_account':result['account_reference'],
                   'period_start':result['period_start'],'period_end':result['period_end'],'source_opening':result['reported_opening_balance'],
                   'source_closing':result['reported_closing_balance'],'source_warnings':result['issues']}
        else:raise ValidationError('Chọn CSV hoặc XLSX đúng mẫu.')
        require(rows or issues,'File không có dữ liệu.')
        # Check successive reported balances without pretending a missing opening is known.
        previous={};checked=0
        for row in rows:
            key=row.get('account') or 'unmapped-bank'
            try:
                observed=row.get('reported_balance','')
                initial=row.get('raw',{}).get('opening_balance','')
                if initial and key not in previous:previous[key]=D(initial)
                if observed:
                    current=D(observed)
                    if key in previous:
                        expected=previous[key]+D(row['amount'])*(1 if row['cash_direction']=='IN' else -1)
                        require(expected==current,f"Dòng {row['source_row']}: số dư nguồn không khớp; dự kiến {S(expected)}, nguồn {S(current)}.")
                        checked+=1
                    previous[key]=current
                elif key in previous:
                    del previous[key]  # never bridge over a row with no observed balance
            except ValidationError as exc:issues.append(str(exc));previous.pop(key,None)
        batch['source_balance_checks']=checked
        batch['coverage_note']='Chỉ kiểm tra các mốc số dư có trong nguồn; chưa chứng minh đủ toàn bộ lịch sử.'
        s['imports'].append({**batch,'id':uid(),'filename':filename,'sha256':sha,'raw_base64':d['content'],'rows':rows,'issues':issues,'archived':False})
        return 'Nhập liên tục vào vùng kiểm tra: '+filename
    if action=='import-map':
        b=item(s['imports'],d.get('batch'));a=item(s['accounts'],d.get('account'))
        require(b.get('mapping_required') and not any(x['status']=='ACCEPTED' for x in b['rows']),'File không còn chờ mapping.')
        require(a['currency']=='VND' and a.get('type','BANK')=='BANK','Mẫu bank yêu cầu tài khoản ngân hàng VND.')
        require(all(x['date']>=a.get('effective_date',s['opening_date']) for x in b['rows']),'Cần tài khoản có số dư đầu trước các giao dịch trong file.')
        require(d.get('reason'),'Xác nhận tài khoản sao kê và căn cứ mapping.')
        for row in b['rows']:row['account']=a['id']
        b.update(mapping_required=False,mapped_account=a['id'],mapping_reason=str(d['reason'])[:300])
        return 'Gắn sao kê với '+a['name']
    if action in {'import-row','import-duplicate'}:
        b=item(s['imports'],d.get('batch'));row=item(b['rows'],d.get('row'))
        require(row['status']=='PENDING' and not b['archived'],'Dòng đã được xử lý hoặc file đã lưu trữ.')
        if d.get('reject'):
            require(d.get('reason'),'Nhập lý do không ghi sổ.');row.update(status='REJECTED',reason=str(d['reason'])[:300]);return 'Không ghi sổ: '+row['description']
        require(not b['issues'] and not b.get('mapping_required'),'File có sai lệch hoặc chưa gắn tài khoản; chưa ghi sổ.')
        candidates=duplicate_candidates(s,row)
        if action=='import-duplicate':
            require(d.get('transaction') in candidates and d.get('reason'),'Chọn giao dịch trùng phù hợp và ghi căn cứ.')
            row.update(status='DUPLICATE',transaction=d['transaction'],reason=str(d['reason'])[:300]);return 'Liên kết chứng từ trùng, không ghi tiền lần hai.'
        require(not candidates or (d.get('distinct_reason') and str(d['distinct_reason']).strip()),'Có giao dịch tương tự: liên kết bản đã ghi hoặc giải thích đây là giao dịch khác.')
        kind=d.get('kind')
        incoming=row.get('cash_direction')=='IN' or row.get('suggested_kind')=='income'
        require(kind in ({'income','unclassified_in'} if incoming else {'expense','unclassified_out'}),'Chọn đúng chiều tiền; khoản vay/đầu tư ghi chưa phân loại rồi gắn nghiệp vụ.')
        tx=append({**row,'kind':kind,'source':b['filename'],'source_row_id':row['id'],'source_batch':b['id'],
                   'source_reference':row.get('reference',''),'distinct_reason':d.get('distinct_reason','')})
        check_balances(s);row.update(status='ACCEPTED',transaction=tx['id'])
        return 'Ghi nhận số tiền từ nguồn: '+row['description'][:100]


def duplicate_candidates(s,row):
    from .product import D
    incoming=row.get('cash_direction')=='IN' or row.get('suggested_kind')=='income'
    candidates=[]
    # Include replaced source entries as evidence, so corrected imports cannot silently re-enter.
    for t in s['transactions']:
        if t.get('direction',1)!=1 or t.get('correction_of'):continue
        if t['account']!=row.get('account') or t['date']!=row['date']:continue
        delta=cash_delta(t,t['account'])
        if abs(delta)!=D(row['amount']) or (delta>0)!=incoming:continue
        same_reference=row.get('reference') and row['reference']==t.get('source_reference')
        same_text=row['description'].strip().casefold()==t['description'].strip().casefold()
        if same_reference or same_text:candidates.append(t['id'])
    return candidates
