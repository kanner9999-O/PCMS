"""P01 bank workflow: immutable source movements, separate allocations and approvals."""
import base64
import copy
import hashlib
import threading
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal, localcontext, ROUND_HALF_UP
from pathlib import Path
from uuid import uuid4

from .core import ValidationError, require, digest, canonical, create_file
from .product import ProductStore, D, S, uid, item
from .bank_statement import parse_statement


def day(value):
    require(isinstance(value, str), 'Cần ngày YYYY-MM-DD.')
    try: date.fromisoformat(value)
    except ValueError: raise ValidationError('Ngày không hợp lệ.')
    return value


def display_day(value):
    return date.fromisoformat(value).strftime('%d/%m/%Y')


def money(value):
    value = D(value)
    require(value == value.to_integral_value(), 'P01 chỉ nhận số nguyên VND.')
    return value


def now(): return datetime.now(timezone.utc).isoformat()


from .interest_settlement import InterestSettlement


from .loan_completion import LoanCompletion
from .trx_energy import TrxEnergy
from .categories import Categories, root_key
from .business import Business
from .objects import Objects
from .realty import Realty
from .crypto_ledger import CryptoLedger
from .assets import AssetOverview
from .account_history import AccountHistory
from .legacy_import import LegacyImport

class P01Store(Objects, Business, LegacyImport, AccountHistory, AssetOverview, CryptoLedger, Realty, Categories, TrxEnergy, LoanCompletion, InterestSettlement, ProductStore):
    def __init__(self, directory):
        self.root = Path(directory)
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.lock = threading.RLock()
        if not list(self.root.glob('*.json')):
            self._write('INITIALIZE', {'schema':'pcms-p01-1','mode':'TRIAL','owner':'Thạch','accounts':[],
                'imports':[],'transactions':[],'profiles':[],'snapshots':[],'audit':[]}, None, 'seed')
        require(self.state().get('schema') == 'pcms-p01-1', 'Thư mục này chứa ứng dụng cũ; chọn thư mục P01 riêng.')

    def coverage_gaps(self,s,account,extra=None):
        """Kept for compatibility: continuity is enforced by running balance (R108), so there are no date gaps to confirm."""
        return []

    def report(self, s, account):
        with localcontext() as ctx:
            ctx.prec=60
            return self._report(s,account)

    def _report(self, s, account):
        a = item(s['accounts'], account)
        txs = sorted([t for t in s['transactions'] if t['account'] == account], key=lambda t:(t['date'],t['order']))
        totals = {}; unknown = 0
        for t in txs:
            if not t['allocations'] or any(p['category']=='unknown' for p in t['allocations']): unknown += 1
            for p in t['allocations'] or [{'category':'unknown','amount':S(abs(D(t['signed_amount'])))}]:
                key = p['category'] + ('_in' if D(t['signed_amount']) > 0 else '_out')
                totals[key] = S(D(totals.get(key,'0')) + D(p['amount']))
        batches=[b for b in s['imports'] if b['account']==account and b['status']=='PUBLISHED']
        return {'account':account,'opening':a['opening'],'balance':S(D(a['opening'])+sum((D(t['signed_amount']) for t in txs),Decimal(0))),
                'transaction_count':len(txs),'unknown_count':unknown,'totals':totals,'transactions':copy.deepcopy(txs),
                'source_periods':[{'batch':b['id'],'start':b['period_start'],'end':b['period_end']} for b in batches],
                'source_end':max([b['period_end'] for b in batches],default=None),
                'tracking_date':a['effective_date'],'coverage_gaps':self.coverage_gaps(s,account),
                'coverage_note':'Chỉ xác nhận các kỳ nguồn liệt kê. Ngoài kỳ nguồn chưa có bằng chứng đầy đủ; không suy là không phát sinh giao dịch.'}

    def view(self):
        with self.lock:
            events=self.events();s=copy.deepcopy(events[-1]['state'])
            for b in s['imports']:
                b['tracking_date']=item(s['accounts'],b['account'])['effective_date']
                b['coverage_gaps']=self.coverage_gaps(s,b['account'],b)
                if b['status']=='DISMISSED':b['current_issues']=self.check_batch(s,b)[0]
            reports=[self.report(s,a['id']) for a in s['accounts']]
            return {'state':s,'reports':reports,'readiness':[self.readiness(s,r) for r in reports], 'version':events[-1]['sequence'],'debts':self.debt_register(s,extras=True), 'interest_statements':self.interest_statement_view(s), 'trx':self.trx_view(s), 'categories':self.category_view(s), 'realty':self.realty_view(s), 'crypto':self.crypto_view(s), 'assets':self.asset_view(s), 'business':self.business_view(s), 'objects':self.object_view(s), 'loan_options':self.loan_options(s), 'capabilities':['transaction-identity','loan-category','loan-completion','loan-cash-report','trx-energy','category-tree','quick-object','realty','crypto','assets','business-objects','default-group','object-management'], 'build':'P44-2026-10-22'}

    def debt_register(self,s,extras=False):
        """Draft projection only; never infer missing opening facts or net parties."""
        with localcontext() as ctx:
            ctx.prec=60
            loans=[]
            for p in s['profiles']:
                if p['kind']!='LOAN':continue
                setup=p.get('debt_setup');issues=[];entries=[]
                principal_in=principal_out=interest_in=interest_out=Decimal(0)
                current=D(setup['opening']) if setup else None
                if not setup:issues.append('NEEDS_SETUP')
                for t in sorted(s['transactions'],key=lambda x:(x['date'],x['order'])):
                    parts=[a for a in t['allocations'] if a.get('profile')==p['id'] and a['category'] in {'principal','interest'}]
                    if not parts:continue
                    before=bool(setup and t['date']<setup['effective_date'])
                    if before:issues.append('PRE_OPENING_ALLOCATION')
                    if not t.get('sources'):issues.append('MISSING_SOURCE')
                    for part in parts:
                        amount=D(part['amount']);incoming=D(t['signed_amount'])>0
                        if part['category']=='interest':
                            if incoming:interest_in+=amount
                            else:interest_out+=amount
                        else:
                            if incoming:principal_in+=amount
                            else:principal_out+=amount
                            if setup and not before:
                                delta=-amount if incoming else amount
                                current+=delta if setup['direction']=='RECEIVABLE' else -delta
                                if current<0:issues.append('NEGATIVE_PRINCIPAL')
                    entries.append({'transaction':t['id'],'account':t['account'],'date':t['date'],'reference':t['reference'],
                                    'signed_amount':t['signed_amount'],'parts':copy.deepcopy(parts),'pre_opening':before})
                loans.append({'id':p['id'],'party':p['party'],'name':p['name'],'setup':copy.deepcopy(setup),
                    'current_principal':S(current) if current is not None else None,'issues':list(dict.fromkeys(issues)),
                    'principal_in':S(principal_in),'principal_out':S(principal_out),'interest_received':S(interest_in),
                    'interest_paid':S(interest_out),'entries':entries})
            for loan in loans:loan['completion_status']=self.completion_status(s,loan['id'])
            people=[]
            for p in s['profiles']:
                if p['kind']!='PERSON':continue
                own=[x for x in loans if x['party']==p['id']]
                people.append({'id':p['id'],'name':p['name'],'loans':own,
                    'receivable':S(sum((D(x['current_principal']) for x in own if not x['issues'] and x['setup']['direction']=='RECEIVABLE'),Decimal(0))),
                    'payable':S(sum((D(x['current_principal']) for x in own if not x['issues'] and x['setup']['direction']=='PAYABLE'),Decimal(0))),
                    'excluded_count':sum(bool(x['issues']) for x in own)})
            for person in people:
                statuses=[x['completion_status'] for x in person['loans']]
                person['completion_status']='NEEDS_REVIEW' if 'NEEDS_REVIEW' in statuses else ('COMPLETED' if statuses and all(x=='COMPLETED' for x in statuses) else 'ACTIVE')
            result={'people':people,'loans':loans,'draft':True}
            if extras:
                for loan in loans:loan['completion_blocker']=self.completion_blocker(s,loan['id'])
                counts={k:sum(x['completion_status']==k for x in loans) for k in ('ACTIVE','COMPLETED','NEEDS_REVIEW')}
                result['summary']={'receivable_total':S(sum((D(x['receivable']) for x in people),Decimal(0))),'payable_total':S(sum((D(x['payable']) for x in people),Decimal(0))),
                    'people':len(people),'loans_by_status':counts,'needs_setup':sum(not x['setup'] for x in loans),'excluded':sum(x['excluded_count'] for x in people),'draft':True}
            return result

    def interest_preview(self,d,s=None):
        """Read-only daily closing principal projection; no receivable or event is booked."""
        with self.lock, localcontext() as ctx:
            ctx.prec=80
            require(d.get('acknowledge') is True,'Cần xác nhận quy ước chỉ dùng để xem dự tính.')
            s=s or self.state();p=item(s['profiles'],d.get('profile'))
            require(p['kind']=='LOAN','Chọn khoản vay VND.')
            setup=p.get('debt_setup');require(setup,'Chưa thiết lập gốc đầu mốc.')
            start=day(d.get('start'));end=day(d.get('end'))
            require(setup['effective_date']<=start<end,'Khoảng xem phải từ mốc gốc, ngày kết thúc sau ngày bắt đầu.')
            terms=sorted(p.get('interest_terms',[]),key=lambda t:t['effective_date'])
            require(terms and terms[0]['effective_date']<=start,'Thiếu lãi suất có hiệu lực ở đầu khoảng xem.')
            entries=[];changes={};cash_in=cash_out=Decimal(0)
            for t in sorted(s['transactions'],key=lambda t:(t['date'],t['order'])):
                parts=[a for a in t['allocations'] if a.get('profile')==p['id'] and a['category'] in {'principal','interest'}]
                if not parts or t['date']>=end:continue
                require(t['date']>=setup['effective_date'],'Có phân bổ trước mốc gốc; cần kiểm tra thiết lập trước khi dự tính.')
                require(t.get('sources'),'Giao dịch thiếu liên kết nguồn; cần kiểm tra trước khi dự tính.')
                entries.append(t['id'])
                for a in parts:
                    amount=D(a['amount']);incoming=D(t['signed_amount'])>0
                    if a['category']=='principal':
                        delta=-amount if incoming else amount
                        if setup['direction']=='PAYABLE':delta=-delta
                        changes[t['date']]=changes.get(t['date'],Decimal(0))+delta
                    elif start<=t['date']<end:
                        if incoming:cash_in+=amount
                        else:cash_out+=amount
            principal=D(setup['opening']);require(principal>=0,'Gốc không được âm.')
            for when,delta in sorted(changes.items()):
                if when>=start:break
                principal+=delta;require(principal>=0,'Dư gốc cuối ngày âm; cần kiểm tra phân bổ.')
            points=sorted({start,end}|{x for x in changes if start<=x<end}|{t['effective_date'] for t in terms if start<t['effective_date']<end})
            segments=[];total=Decimal(0)
            for left,right in zip(points,points[1:]):
                principal+=changes.get(left,Decimal(0));require(principal>=0,'Dư gốc cuối ngày âm; cần kiểm tra phân bổ.')
                term=next(t for t in reversed(terms) if t['effective_date']<=left)
                require(term.get('unit') in {'VND_MILLION_DAY','PERCENT_30_DAY'},'Đơn vị lãi suất không hợp lệ.')
                value=D(term['value']);require(value>=0,'Lãi suất không được âm.')
                daily=value/Decimal(1000000) if term['unit']=='VND_MILLION_DAY' else value/Decimal(3000)
                days=(date.fromisoformat(right)-date.fromisoformat(left)).days
                interest=principal*daily*days;total+=interest
                segments.append({'start':left,'end':right,'days':days,'principal':S(principal),'term':copy.deepcopy(term),'raw_interest':S(interest)})
            return {'profile':p['id'],'start':start,'end':end,'segments':segments,'raw_total':S(total),
                'total':S(total.quantize(Decimal(1),rounding=ROUND_HALF_UP)),
                'interest_received':S(cash_in),'interest_paid':S(cash_out),'evidence':entries,
                'coverage':[self.report(s,a['id']) for a in s['accounts']]}

    def financial_content(self,report,account,profiles):
        """Stable financial projection, also usable on immutable pre-P03 snapshots."""
        keys=('id','account','date','order','reference','description','signed_amount','reported_balance','allocations','sources','transfer_match')
        transactions=[{k:t[k] for k in keys if k in t} for t in report['transactions']]
        linked={p['profile'] for t in transactions for p in t['allocations'] if p.get('profile')}
        linked.update(p['party'] for p in profiles if p['id'] in linked and p.get('party'))
        return {'account':{k:account.get(k) for k in ('id','reference','currency','effective_date','opening','opening_source')},
                'transactions':transactions,'source_periods':report['source_periods'],
                'profiles':sorted([{k:p.get(k) for k in ('id','kind','name','party','debt_setup','interest_terms')} for p in profiles if p['id'] in linked],key=lambda p:p['id'])}

    def financial_changed(self,s,report,previous):
        if not previous:return True
        a=item(s['accounts'],report['account'])
        old=previous.get('account_details') or {**a,'opening':previous['report']['opening'],'effective_date':previous['report'].get('tracking_date',a['effective_date'])}
        return digest(self.financial_content(report,a,s['profiles']))!=digest(self.financial_content(previous['report'],old,previous.get('profiles',[])))

    def readiness(self,s,r):
        a=item(s['accounts'],r['account']);batches=[b for b in s['imports'] if b['account']==a['id']]
        counts={status:sum(b['status']==status for b in batches) for status in ('STAGED','BLOCKED','DISMISSED','PUBLISHED')}
        latest=next((x for x in reversed(s['snapshots']) if x['account']==a['id']),None)
        changed=self.financial_changed(s,r,latest)
        if a.get('status','ACTIVE')!='ACTIVE':action='restore'
        elif counts['BLOCKED']:action='blocked'
        elif counts['STAGED']:action='staged'
        elif not r['source_periods']:action='recover' if counts['DISMISSED'] else 'import'
        elif latest and not changed:action='updated'
        elif r['unknown_count']:action='classify'
        else:action='review'
        ms=latest.get('milestone') if latest else None;since=None
        if ms and ms.get('anchor'):
            later=[t for t in s['transactions'] if t['account']==a['id'] and t['order']>ms['anchor']['order']]
            since=dict(count=len(later),unclassified=sum(1 for t in later if not t['allocations'] or any(p['category']=='unknown' for p in t['allocations'])))
        return {'account':a['id'],'counts':counts,'financial_changed':changed,'next_action':action,'milestone':ms,'since_milestone':since,
                'latest_approval':{'id':latest['id'],'version':latest['version'],'approved_at':latest['approved_at']} if latest else None,
                'can_approve':bool(r['source_periods']) and changed and not(counts['STAGED'] or counts['BLOCKED']) and a.get('status','ACTIVE')=='ACTIVE'}

    def apply(self, action, data, request_id):
        with self.lock, localcontext() as ctx:
            ctx.prec=60
            require(isinstance(request_id,str) and 1<=len(request_id)<=100,'Thiếu mã yêu cầu.')
            events=self.events()
            if any(e['request_id']==request_id for e in events):return self.view()
            s=copy.deepcopy(events[-1]['state'])
            detail=self.change(s,action,data)
            s['audit'].append({'id':uid(),'at':now(),'actor':'Thạch · sử dụng bản thử','action':action,'detail':detail})
            self._write(action,s,events[-1]['hash'],request_id)
            return self.view()

    def check_batch(self,s,b):
        """Continuity by running balance: the file must continue from the last recorded transaction (R105-R108); dates are never compared."""
        a=item(s['accounts'],b['account']); issues=list(b.get('parse_issues',[]));rows=b['rows']
        if b.get('source_account') != a['reference']:issues.append('Số tài khoản nguồn khác tài khoản đã chọn.')
        existing=sorted([t for t in s['transactions'] if t['account']==a['id']],key=lambda t:t['order'])
        from .legacy_import import norm_ref
        seen={norm_ref(t['reference']):t for t in existing}
        for r in rows:
            for e in s.get('legacy_entries',[]):
                active=any(b['id']==e['batch'] and b['status']=='ACTIVE' for b in s.get('legacy_batches',[]))
                if active and self.legacy_account(s,e)==a['id'] and norm_ref(e['reference'])==norm_ref(r['reference']):
                    signed=e['amount'] if e['direction']=='IN' else '-'+e['amount']
                    if (e['date'],D(signed),e['description'])!=(r['date'],D(r['signed_amount']),r['description']):issues.append(f"Mã {r['reference']} xung đột lịch sử cũ trong tài khoản; cần đối chiếu trước khi nhập.")
        new=[];duplicates=[];flags=[];file_refs=set()
        for r in rows:
            ref=norm_ref(r['reference'])
            if ref in file_refs:
                issues.append(f"Dòng {r['source_row']}: mã lặp trong cùng file; đối chiếu nguồn trước khi nhập.");flags.append('conflict');continue
            file_refs.add(ref)
            old=seen.get(norm_ref(r['reference']))
            if old:
                if any(old[k]!=r[k] for k in ('date','signed_amount','description','reported_balance')):
                    issues.append(f"Dòng {r['source_row']}: tham chiếu {r['reference']} xung đột với dữ liệu đã có.");flags.append('conflict')
                else:duplicates.append((r,old));flags.append('dup')
            else:seen[norm_ref(r['reference'])]=r;new.append(r);flags.append('new')
        if not issues and rows:
            tail_balance=D(a['opening'])+sum((D(t['signed_amount']) for t in existing),Decimal(0));tail=existing[-1] if existing else None
            where=f"giao dịch cuối đã ghi {tail['reference']} ngày {display_day(tail['date'])}, số dư {S(tail_balance)}" if tail else f"số dư đầu tài khoản {S(tail_balance)}"
            if tail and tail.get('reported_balance') is not None and D(tail['reported_balance'])!=tail_balance:
                issues.append(f"Sổ cái tài khoản ({S(tail_balance)}) không khớp số dư của giao dịch cuối đã ghi ({tail['reported_balance']}); kiểm tra mốc đầu tài khoản trước khi nạp thêm.")
            dup_index=[i for i,f in enumerate(flags) if f=='dup']
            if dup_index:
                last=dup_index[-1]
                if new and any(flags[i]!='dup' for i in range(last)):issues.append(f"File có giao dịch chưa ghi nằm trước hoặc xen giữa các giao dịch đã có; không nối liền mạch với {where}.")
                elif new and norm_ref(rows[last]['reference'])!=norm_ref(tail['reference']):issues.append(f"File chồng lên dữ liệu đã có nhưng phần chồng không kết thúc ở {where}; không nối liền mạch.")
            elif D(b['source_opening'])!=tail_balance:
                issues.append(f"File chưa nối tiếp: số dư đầu file {b['source_opening']}, cần bằng {where}. Bổ sung file nối tiếp hoặc kiểm tra file.")
            if not issues and new:
                after=tail_balance+sum((D(r['signed_amount']) for r in new),Decimal(0))
                if after!=D(b['source_closing']):issues.append(f"Số dư cuối chưa khớp: tính {S(after)} từ {where}, nguồn {b['source_closing']}.")
        return issues,new,duplicates

    def stage_import(self,s,d):
        item(s['accounts'],d.get('account'))
        try:raw=base64.b64decode(d.get('content',''),validate=True)
        except Exception:raise ValidationError('Nội dung file không hợp lệ.')
        require(0<len(raw)<=8_000_000,'File rỗng hoặc vượt 8 MB.')
        sha=hashlib.sha256(raw).hexdigest()
        existing=next((b for b in s['imports'] if b['account']==d['account'] and b['sha256']==sha),None)
        if existing:
            require(existing['status']!='DISMISSED','File này đã được loại khỏi đợt trước. Mở file trong danh sách nguồn và chọn “Đưa lại vào kiểm tra” để kiểm tra theo mốc tài khoản hiện tại; không cần tải lại file.')
            return 'File đã có trong lịch sử nhập; không ghi thêm tiền.'
        b={'id':uid(),'account':d['account'],'filename':Path(str(d.get('filename',''))).name[:150], 'sha256':sha,
           'content':d['content'],'status':'STAGED','rows':[],'parse_issues':[],'imported_at':now()}
        try:
            require(b['filename'].lower().endswith('.xlsx'),'Chỉ hỗ trợ XLSX ngân hàng theo mẫu đã nhận diện. Xem file mẫu trong hướng dẫn nhập.')
            parsed=parse_statement(raw)
            b.update(source_account=parsed['account_reference'],period_start=parsed['period_start'],period_end=parsed['period_end'],
                     source_opening=parsed['reported_opening_balance'],source_closing=parsed['reported_closing_balance'])
            labels={'RUNNING_BALANCE_MISMATCH':'Số dư tại dòng không khớp','PERIOD_BALANCE_MISMATCH':'Tổng phát sinh không khớp số dư kỳ','CLOSING_BALANCE_MISMATCH':'Số dư dòng cuối khác số dư cuối kỳ','DATE_OUTSIDE_PERIOD':'Ngày giao dịch ngoài kỳ nguồn','DATE_ORDER':'Thứ tự ngày nguồn chưa đúng','INVALID_TRANSACTION_ROW':'Dòng nguồn không hợp lệ','REPEATED_BANK_REFERENCE':'Tham chiếu bị lặp trong file; cần xác minh'}
            b['parse_issues']=[f"Dòng {i.get('source_row') or 'tổng'}: {labels.get(i['code'],i['code'])}. {i.get('reason','')}"+(f" Tính {i['expected']} VND; nguồn {i.get('reported')} VND; chênh {i.get('difference')} VND." if 'expected' in i else '') for i in parsed['issues']]
            b['rows']=[{'id':uid(),'reference':r['bank_reference'],'date':r['effective_date'],'signed_amount':r['signed_amount'],
                 'description':r['description'],'reported_balance':r['reported_balance'],'source_row':r['source_row'],'sheet':r['sheet']} for r in parsed['transactions']]
            b['issues'],_,_=self.check_batch(s,b)
        except Exception as exc:
            b['parse_issues']=[f'Mẫu chưa hỗ trợ hoặc file không hợp lệ: {exc}'];b['issues']=b['parse_issues'][:]
        if b['issues']:b['status']='BLOCKED'
        s['imports'].append(b)
        return 'Đã giữ file nguồn; '+('cần xử lý lỗi trước khi ghi.' if b['issues'] else 'sẵn sàng ghi toàn đợt.')

    def account_from_file(self,s,d):
        """Create an account from its first statement: number, opening balance and start date come from the file (R109)."""
        try:raw=base64.b64decode(d.get('content',''),validate=True)
        except Exception:raise ValidationError('Nội dung file không hợp lệ.')
        require(0<len(raw)<=8_000_000,'File rỗng hoặc vượt 8 MB.')
        filename=Path(str(d.get('filename',''))).name[:150];require(filename.lower().endswith('.xlsx'),'Chỉ hỗ trợ XLSX ngân hàng theo mẫu đã nhận diện.')
        try:parsed=parse_statement(raw)
        except Exception as exc:raise ValidationError(f'Mẫu chưa hỗ trợ hoặc file không hợp lệ: {exc}')
        reference=str(parsed['account_reference']).strip();require(reference.isdigit(),'Không đọc được số tài khoản từ file.')
        require(not any(a['reference']==reference for a in s['accounts']),'Số tài khoản đã tồn tại; chọn tài khoản đó và nạp file nối tiếp (kiểm tra cả tài khoản lưu trữ hoặc đã xóa nhầm).')
        opening=money(parsed['reported_opening_balance']);require(opening>=0,'Số dư đầu không âm.')
        name=str(d.get('name') or '').strip() or f'Tài khoản {reference}'
        account={'id':uid(),'name':name[:100],'reference':reference,'opening':S(opening),'currency':'VND','effective_date':day(parsed['period_start']),
                 'opening_source':f'Số dư đầu của file sao kê {filename}','status':'ACTIVE','history':[]}
        s['accounts'].append(account)
        message=self.stage_import(s,{'account':account['id'],'filename':filename,'content':d['content']})
        return f"Tạo tài khoản {account['name']} từ file nguồn; {message}"

    def change(self,s,action,d):
        if action.startswith('legacy-'):return self.change_legacy(s,action,d)
        if action.startswith('assets-'):return self.change_assets(s,action,d)
        if action.startswith('crypto-'):return self.change_crypto(s,action,d)
        if action.startswith('realty-'):return self.change_realty(s,action,d)
        if action.startswith('category-'):return self.change_category(s,action,d)
        if action.startswith('business-'):return self.change_business(s,action,d)
        if action=='loan-regroup':return self.change_category(s,action,d)
        if action=='transaction-note':return self.change_note(s,d)
        if action in {'object-create','object-edit','object-archive','object-restore','object-delete'}:return self.change_object(s,action,d)
        if action=='object-quick-create':return self.change_quick_object(s,d)
        if action.startswith('trx-'):return self.change_trx(s,action,d)
        if action in {'loan-complete','loan-reopen'}:return self.change_completion(s,action,d)
        if action in {'interest-draft','interest-reopen','interest-approve'}:return self.change_interest(s,action,d)
        guarded={'import','approve','begin-adjustment','account-edit'}
        accounts=[]
        if action in guarded:accounts=[d.get('account')]
        elif action in {'publish','recheck-import','reopen-import','dismiss-import'}:accounts=[item(s['imports'],d.get('batch'))['account']]
        elif action=='classify':accounts=[item(s['transactions'],key)['account'] for key in d.get('ids',[])]
        elif action=='match-transfer':accounts=[item(s['transactions'],d.get(key))['account'] for key in ('outgoing','incoming')]
        for account_id in accounts:
            require(item(s['accounts'],account_id).get('status','ACTIVE')=='ACTIVE','Tài khoản đang lưu trữ hoặc đã xóa nhầm; khôi phục tài khoản trước khi thay đổi.')
        if action=='account-edit':
            a=item(s['accounts'],d.get('account'));before=copy.deepcopy(a)
            name=str(d.get('name',a['name'])).strip();require(name,'Tên tài khoản không được để trống.')
            locked=any(t['account']==a['id'] for t in s['transactions']) or any(x['account']==a['id'] for x in s['snapshots']) or any(b['account']==a['id'] and b['status']=='PUBLISHED' for b in s['imports'])
            fields={'reference','effective_date','opening','opening_source'}
            changes={key:d[key] for key in fields if key in d}
            if 'opening' in changes:changes['opening']=S(money(changes['opening']))
            if locked:require(all(str(value)==str(a[key]) for key,value in changes.items()),'Đã có lịch sử ghi hoặc bản duyệt: chỉ đổi tên hiển thị. Mốc và số dư được giữ để bảo toàn lịch sử. Bản dùng thử chưa hỗ trợ sửa trực tiếp số dư đã ghi; đối chiếu lại chứng từ trước khi điều chỉnh. Số tài khoản cũ vẫn được giữ kể cả khi lưu trữ.')
            candidate={**a,**changes,'name':name[:100]}
            candidate['reference']=str(candidate['reference']).strip();candidate['opening_source']=str(candidate['opening_source']).strip()[:500]
            require(candidate['reference'].isdigit() and candidate['opening_source'],'Cần số tài khoản và căn cứ số dư đầu.')
            require(not any(x['id']!=a['id'] and x['reference']==candidate['reference'] for x in s['accounts']),'Số tài khoản đã tồn tại; kiểm tra cả tài khoản lưu trữ hoặc đã xóa nhầm.')
            day(candidate['effective_date']);require(money(candidate['opening'])>=0,'Số dư đầu không âm.')
            a.update(candidate)
            for b in s['imports']:
                if b['account']==a['id'] and b['status'] in {'STAGED','BLOCKED'}:
                    issues,new,duplicates=self.check_batch(s,b)
                    b.update(issues=issues,status='BLOCKED' if issues else 'STAGED',checked_at=now(),pending_new_count=len(new),pending_duplicate_count=len(duplicates))
            a.setdefault('history',[]).append({'at':now(),'action':'EDIT','before':{k:before.get(k) for k in fields|{'name'}},'after':{k:a[k] for k in fields|{'name'}}})
            return 'Cập nhật tài khoản '+a['name']+'; đã kiểm tra lại các file chờ.'
        if action in {'account-delete','account-archive','account-restore'}:
            a=item(s['accounts'],d.get('account'));status=a.get('status','ACTIVE')
            reason=str(d.get('reason','')).strip() or {'account-delete':'Tạo nhầm','account-archive':'Ngừng sử dụng tài khoản','account-restore':'Khôi phục để sử dụng'}[action]
            if action=='account-restore':
                require(status in {'DELETED','ARCHIVED'},'Tài khoản đang hoạt động.')
                target='ACTIVE'
            else:
                require(status=='ACTIVE' and d.get('confirm') is True,'Xác nhận thao tác với tài khoản đang hoạt động.')
                if action=='account-delete':
                    require(not any(x['account']==a['id'] for collection in ('imports','transactions','snapshots') for x in s[collection]),'Tài khoản đã có nguồn hoặc lịch sử. Dùng Lưu trữ để giữ nguyên chứng từ và số liệu.')
                    target='DELETED'
                else:target='ARCHIVED'
            a['status']=target
            a.setdefault('history',[]).append({'at':now(),'action':action,'before':status,'after':target,'reason':reason[:500]})
            return {'DELETED':'Đã xóa nhầm có thể hoàn tác: ','ARCHIVED':'Đã lưu trữ, giữ nguyên lịch sử: ','ACTIVE':'Đã khôi phục tài khoản: '}[target]+a['name']
        if action=='account':
            name=str(d.get('name','')).strip();reference=str(d.get('reference','')).strip()
            require(name and reference.isdigit() and d.get('opening_source'),'Nhập tên, số tài khoản và căn cứ số dư đầu.')
            require(not any(a['reference']==reference for a in s['accounts']),'Số tài khoản đã tồn tại; kiểm tra danh sách tài khoản đang hoạt động, lưu trữ hoặc đã xóa nhầm để khôi phục.')
            opening=money(d.get('opening'));require(opening>=0,'Số dư đầu không âm.')
            s['accounts'].append({'id':uid(),'name':name[:100],'reference':reference,'opening':S(opening),'currency':'VND',
                'effective_date':day(d.get('effective_date')),'opening_source':str(d['opening_source'])[:500],'status':'ACTIVE','history':[]})
            return 'Tạo tài khoản '+name
        if action=='profile':
            require(d.get('kind') in {'PERSON','LOAN','PROPERTY'} and str(d.get('name','')).strip(),'Chọn loại và nhập tên hồ sơ.')
            require(d.get('kind')!='LOAN' or d.get('party'),'Khoản vay cần gắn người / tổ chức.')
            if d.get('party'):require(item(s['profiles'],d['party'])['kind']=='PERSON','Chủ thể phải là hồ sơ người.')
            if d['kind']=='LOAN':
                self.require_free_name(s,d['name'])
                s['profiles'].append({'id':uid(),'kind':'LOAN','name':str(d['name']).strip()[:100],'party':d.get('party') or None})
            else:self.create_profile(s,d['name'],d['kind'])
            return 'Tạo hồ sơ '+d['name']
        if action=='interest-terms':
            p=item(s['profiles'],d.get('profile'));require(p['kind']=='LOAN','Chọn khoản vay VND.')
            require(p.get('debt_setup'),'Thiết lập khoản vay trước khi nhập lãi suất.')
            require(d.get('acknowledge') is True,'Cần xác nhận quy ước chỉ dùng để xem dự tính.')
            require(d.get('unit') in {'VND_MILLION_DAY','PERCENT_30_DAY'},'Chọn một đơn vị lãi suất.')
            value=D(d.get('value'));require(value>=0,'Lãi suất không được âm.')
            effective=day(d.get('effective_date'));require(effective>=p['debt_setup']['effective_date'],'Ngày lãi suất không được trước mốc gốc.')
            source=str(d.get('source','')).strip();reason=str(d.get('reason','')).strip()
            require(source and reason,'Cần căn cứ lãi suất và lý do thay đổi.')
            term={'unit':d['unit'],'value':str(d['value']),'effective_date':effective,'source':source[:500],'reason':reason[:500],'preview_convention':'daily-closing-half-up-v1'}
            terms=p.setdefault('interest_terms',[]);before=next((t for t in terms if t['effective_date']==effective),None)
            p.setdefault('interest_history',[]).append({'at':now(),'before':copy.deepcopy(before),'after':copy.deepcopy(term)})
            p['interest_terms']=sorted([t for t in terms if t['effective_date']!=effective]+[term],key=lambda t:t['effective_date'])
            return 'Lưu điều khoản lãi dự tính '+p['name']+': '+reason[:500]
        if action=='loan-setup':
            p=item(s['profiles'],d.get('profile'));require(p['kind']=='LOAN','Chọn hồ sơ khoản vay.')
            require(d.get('direction') in {'RECEIVABLE','PAYABLE'},'Chọn rõ phải thu hoặc phải trả.')
            opening=money(d.get('opening'));require(opening>=0,'Gốc đầu mốc không âm.')
            require(opening!=0 or d.get('confirm_zero') is True,'Xác nhận rõ gốc đầu mốc bằng 0.')
            source=str(d.get('source','')).strip();reason=str(d.get('reason','')).strip()
            require(source and reason,'Cần căn cứ gốc đầu mốc và lý do thiết lập / điều chỉnh.')
            setup={'direction':d['direction'],'opening':S(opening),'effective_date':day(d.get('effective_date')),'source':source[:500]}
            before=copy.deepcopy(p.get('debt_setup'))
            p['debt_setup']=setup
            p.setdefault('debt_history',[]).append({'at':now(),'before':before,'after':copy.deepcopy(setup),'reason':reason[:500]})
            return 'Thiết lập công nợ nháp '+p['name']+': '+reason[:500]
        if action=='import':return self.stage_import(s,d)
        if action=='account-from-file':return self.account_from_file(s,d)
        if action=='reopen-import':
            b=item(s['imports'],d.get('batch'))
            require(b['status']=='DISMISSED','Chỉ đưa lại file đã loại khỏi đợt vào kiểm tra.')
            b.setdefault('review_history',[]).append({'at':now(),'action':'REOPEN','previous_status':b['status'],'previous_issues':copy.deepcopy(b.get('issues',[])),'dismiss_reason':b.get('dismiss_reason')})
            issues,new,duplicates=self.check_batch(s,b)
            b.update(issues=issues,status='BLOCKED' if issues else 'STAGED',checked_at=now(),pending_new_count=len(new),pending_duplicate_count=len(duplicates))
            return 'Đã đưa nguồn trở lại kiểm tra theo thông tin tài khoản hiện tại; chưa ghi giao dịch.'
        if action=='recheck-import':
            b=item(s['imports'],d.get('batch'))
            require(b['status'] in {'STAGED','BLOCKED'},'Chỉ kiểm tra lại file đang chờ; file đã ghi hoặc đã loại được giữ nguyên.')
            issues,new,duplicates=self.check_batch(s,b)
            b.update(issues=issues,status='BLOCKED' if issues else 'STAGED',checked_at=now(),pending_new_count=len(new),pending_duplicate_count=len(duplicates))
            return 'Đã kiểm tra lại nguồn: '+('còn lỗi cần xử lý.' if issues else 'sẵn sàng ghi toàn đợt.')
        if action=='publish':
            b=item(s['imports'],d.get('batch'))
            if b['status']=='PUBLISHED':return 'Đợt đã ghi; không thêm giao dịch.'
            require(b['status'] in {'STAGED','BLOCKED'},'File đã loại khỏi đợt; không ghi nguồn đã loại.')
            issues,new,duplicates=self.check_batch(s,b)
            require(not issues,'Không thể ghi đợt: '+'; '.join(issues))
            for r in new:
                tx={**copy.deepcopy(r),'id':uid(),'account':b['account'],'order':len(s['transactions']),'allocations':[],
                    'sources':[{'batch':b['id'],'row':r['source_row'],'sheet':r['sheet']}],'classification_history':[]}
                s['transactions'].append(tx);r['transaction']=tx['id']
            for r,old in duplicates:
                # Same-file duplicate references are blocked by parser, so old is a stored transaction.
                old['sources'].append({'batch':b['id'],'row':r['source_row'],'sheet':r['sheet']});r['transaction']=old['id']
            b.update(status='PUBLISHED',issues=[],published_at=now(),new_count=len(new),duplicate_count=len(duplicates))
            return f'Đã ghi {len(new)} giao dịch mới, liên kết {len(duplicates)} dòng trùng.'
        if action=='begin-adjustment':
            a=item(s['accounts'],d.get('account'))
            require(any(x['account']==a['id'] for x in s['snapshots']),'Chưa có bản duyệt cần điều chỉnh.')
            a.update(adjustment_open=True,adjustment_reason=str(d.get('reason','')).strip()[:500])
            return 'Mở phiên điều chỉnh'+(': '+a['adjustment_reason'] if a['adjustment_reason'] else '')
        if action=='classify':
            ids=d.get('ids',[]);parts=d.get('parts',[])
            require(isinstance(ids,list) and ids and len(ids)==len(set(ids)),'Chọn các giao dịch khác nhau.')
            require(isinstance(parts,list) and 1<=len(parts)<=20,'Cần ít nhất một phần phân loại.')
            reason=str(d.get('reason','')).strip()[:500]
            require(len(ids)==1 or (len(parts)==1 and not parts[0].get('amount')),'Phân loại hàng loạt chỉ một loại, toàn bộ tiền mỗi dòng.')
            selected=[item(s['transactions'],i) for i in ids]
            require(len({t['account'] for t in selected})==1,'Chỉ phân loại các dòng trong cùng tài khoản.')
            for t in selected:
                self.require_adjustment(s,t)
                require(not t.get('transfer_match'),'Giao dịch đã ghép chuyển nội bộ; không phân loại lại.')
                allocated=[]
                for p in parts:
                    category=p.get('category');require(category in {'income','expense','principal','interest','investment','transfer_pending','unknown'},'Loại phân bổ không hợp lệ.')
                    signed=D(t['signed_amount'])
                    require(not(category=='income' and signed<0),'Thu nhập chỉ dành cho tiền vào. Chi tiêu nhận cả tiền ra (chi) và tiền vào (hoàn chi).')
                    profile=p.get('profile') or None
                    amount=money(p.get('amount') or S(abs(signed)));require(amount>0,'Số phân bổ phải dương.')
                    part={'category':category,'amount':S(amount),'profile':profile}
                    if p.get('node'):
                        node=next((n for n in s.get('categories',[]) if n['id']==p['node']),None)
                        require(node is not None and node['status']=='ACTIVE' and node['root']==root_key(category),'Danh mục con không tồn tại, đã lưu trữ hoặc không thuộc loại phân bổ đã chọn.')
                        part['node']=node['id']
                    if profile:
                        target=item(s['profiles'],profile);key=part.get('node') or root_key(category)
                        require(target.get('status')!='ARCHIVED' or any(x.get('profile')==profile for tt in selected for x in tt['allocations']),'Đối tượng đã lưu trữ; khôi phục ở màn Đối tượng trước khi phân loại mới.')
                        members={e['profile'] for e in s.get('category_objects',[]) if e['status']=='ACTIVE' and e['category']==key}
                        kept={x.get('profile') for t in selected for x in t['allocations'] if x.get('profile')}
                        legacy={'principal':{'LOAN'},'interest':{'LOAN'},'investment':{'PROPERTY'},'expense':{'LOAN','PROPERTY'}}.get(category,set())
                        native={'principal':{'LOAN'},'interest':{'LOAN'},'investment':{'PROPERTY'}}.get(category,set())
                        require(profile in members or profile in kept or (not members and target['kind'] in legacy) or target['kind'] in native,'Đối tượng không thuộc danh mục này. Thêm đối tượng vào danh mục ở màn Danh mục trước.')
                    allocated.append(part)
                require(sum((D(p['amount']) for p in allocated),Decimal(0))==abs(D(t['signed_amount'])),'Tổng phân bổ phải khớp giao dịch nguồn.')
                t['classification_history'].append({'at':now(),'before':copy.deepcopy(t['allocations']),'after':copy.deepcopy(allocated),'reason':reason})
                t['allocations']=[] if len(allocated)==1 and allocated[0]['category']=='unknown' else allocated
                need=any(self.cat_flag(s,x.get('node'),'note_required') for x in allocated);final=str(d['note']).strip() if d.get('note') is not None else t.get('note','')
                require(final or not need,'Danh mục này yêu cầu ghi chú (khoản chi không chứng từ cần ghi rõ mục đích).')
                self.apply_note(t,d.get('note'),d.get('voucher'))
            return f'Phân loại {len(selected)} giao dịch'+(': '+reason if reason else '')
        if action=='match-transfer':
            out=item(s['transactions'],d.get('outgoing'));inc=item(s['transactions'],d.get('incoming'))
            require(out['account']!=inc['account'] and D(out['signed_amount'])<0 and D(inc['signed_amount'])==-D(out['signed_amount']),'Chọn hai đầu khác tài khoản, ngược chiều và cùng số tiền.')
            require(not out.get('transfer_match') and not inc.get('transfer_match') and str(d.get('reason','')).strip(),'Hai đầu chưa ghép và cần căn cứ.')
            require(all(not t['allocations'] or all(p['category']=='transfer_pending' for p in t['allocations']) for t in (out,inc)),'Hai đầu cần chưa phân loại hoặc chờ đối ứng.')
            self.require_adjustment(s,out);self.require_adjustment(s,inc)
            match=uid()
            for t in (out,inc):
                t['classification_history'].append({'at':now(),'before':copy.deepcopy(t['allocations']),'reason':d['reason']})
                t['allocations']=[{'category':'transfer','amount':S(abs(D(t['signed_amount']))),'profile':None}];t['transfer_match']=match
            return 'Ghép chuyển nội bộ; giữ nguyên nguồn, ngày và số tiền hai đầu.'
        if action=='approve':
            account=d.get('account');report=self.report(s,account)
            require(report['source_periods'],'Chưa có kỳ nguồn hợp lệ để duyệt.')
            require(not any(b['account']==account and b['status'] not in {'PUBLISHED','DISMISSED'} for b in s['imports']),'Còn file chờ xử lý; xử lý hoặc loại khỏi đợt trước khi duyệt.')
            require(not report['unknown_count'] or d.get('confirm_unknown') is True,'Xác nhận còn giao dịch chưa phân loại trước khi duyệt.')
            previous=next((x for x in reversed(s['snapshots']) if x['account']==account),None)
            require(self.financial_changed(s,report,previous),'Đã cập nhật: nội dung tài chính giống bản duyệt gần nhất; không tạo thêm phiên bản.')
            require(not report['coverage_gaps'] or d.get('confirm_gaps') is True,'Xác nhận riêng các khoảng chưa có nguồn trước khi duyệt.')
            if previous:require(str(d.get('reason','')).strip(),'Nhập lý do tạo phiên bản mới; bản cũ được giữ nguyên.')
            snap={'id':uid(),'account':account,'version':1+(previous['version'] if previous else 0),'approved_at':now(),'actor':'Thạch',
                 'report':report,'account_details':copy.deepcopy(item(s['accounts'],account)),'profiles':copy.deepcopy(s['profiles']),'reason':str(d.get('reason','Duyệt đợt đầu'))[:500],
                 'restates':previous['id'] if previous else None,'confirmed_unknown':bool(d.get('confirm_unknown')),
                 'confirmed_gaps':copy.deepcopy(report['coverage_gaps']) if d.get('confirm_gaps') is True else []}
            txs=sorted([t for t in s['transactions'] if t['account']==account],key=lambda t:t['order']);tail=txs[-1] if txs else None
            snap['milestone']=dict(anchor=dict(transaction=tail['id'],reference=tail['reference'],date=tail['date'],order=tail['order']) if tail else None,balance=report['balance'],transactions=len(txs),classified=len(txs)-report['unknown_count'],unclassified=report['unknown_count'])
            if s.get('categories'):snap['category_tree']=[dict(id=n['id'],name=n['name'],parent=n['parent'],root=n['root'],status=n['status'],path=self.cat_path(s,n['id'])) for n in s['categories']]
            snap['hash']=digest(snap);s['snapshots'].append(snap)
            item(s['accounts'],account)['adjustment_open']=False
            return 'Đã lưu bản duyệt '+str(snap['version'])
        if action=='dismiss-import':
            b=item(s['imports'],d.get('batch'));require(b['status']!='PUBLISHED' and str(d.get('reason','')).strip(),'Chỉ loại file chưa ghi; cần lý do.')
            b['status']='DISMISSED';b['dismiss_reason']=str(d['reason'])[:500];b['dismissed_at']=now();b['dismissed_tracking_date']=item(s['accounts'],b['account'])['effective_date']
            return 'Giữ nguồn, loại file khỏi đợt duyệt.'
        raise ValidationError('Thao tác P01 chưa được hỗ trợ.')

    def require_adjustment(self,s,t):
        approved=any(any(x['id']==t['id'] for x in snap['report']['transactions']) for snap in s['snapshots'] if snap['account']==t['account'])
        require(not approved or item(s['accounts'],t['account']).get('adjustment_open'), 'Dòng đã duyệt. Tạo phiên điều chỉnh có lý do trước khi sửa.')

    def backup(self):
        with self.lock:
            events=self.events();return {'format':'pcms-p01-backup-1','events':events,'checksum':digest(events)}

    def validate_bundle(self,bundle):
        require(bundle.get('format')=='pcms-p01-backup-1' and digest(bundle.get('events'))==bundle.get('checksum'),'Bản sao lưu P01 không khớp checksum.')
        events=bundle['events'];require(bool(events),'Bản sao lưu rỗng.');previous=None
        for n,e in enumerate(events,1):
            require(e['sequence']==n and e['previous']==previous and digest({k:v for k,v in e.items() if k!='hash'})==e['hash'],'Lịch sử sao lưu không hợp lệ.')
            previous=e['hash']
        s=events[-1]['state'];require(s.get('schema')=='pcms-p01-1','Sai phiên bản dữ liệu.')
        for b in s['imports']:
            require(hashlib.sha256(base64.b64decode(b['content'],validate=True)).hexdigest()==b['sha256'],'File nguồn sai checksum.')
        for snap in s['snapshots']:require(digest({k:v for k,v in snap.items() if k!='hash'})==snap['hash'],'Bản duyệt sai checksum.')
        for st in s.get('interest_statements',[]):
            for snap in st['versions']:require(digest({k:v for k,v in snap.items() if k!='hash'})==snap['hash'],'Bảng kê lãi sai checksum.')
        for p in s['profiles']:
            for snap in p.get('completion_history',[]):require(digest({k:v for k,v in snap.items() if k!='hash'})==snap['hash'],'Bằng chứng hoàn tất sai checksum.')
        return copy.deepcopy(s)

    def restore(self,bundle,request_id):
        with self.lock:
            require(len(self.events())==1 and not self.state()['accounts'],'Chỉ khôi phục vào bộ dữ liệu mới, không ghi đè bộ đang dùng.')
            s=self.validate_bundle(bundle)
            self._write('RESTORE',s,self.events()[-1]['hash'],request_id)
            return self.view()

    def clone_restore(self,bundle):
        self.validate_bundle(bundle)
        target=self.root.parent/(self.root.name+'-restore-'+uuid4().hex[:10])
        restored=P01Store(target);restored.restore(bundle,uid())
        return {'directory':str(target.resolve()),'account_count':len(restored.state()['accounts']),'transaction_count':len(restored.state()['transactions'])}
