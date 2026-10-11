"""Versioned, explicit settlement of sourced VND interest; never books cash."""
import copy
from decimal import Decimal, localcontext
from functools import wraps
from .core import require, digest, ValidationError
from .product import D, S, uid, item

def precise(fn):
    @wraps(fn)
    def call(*args,**kwargs):
        with localcontext() as ctx:
            ctx.prec=80
            return fn(*args,**kwargs)
    return call

class InterestSettlement:
    @precise
    def interest_basis(self,s,d):
        p=item(s['profiles'],d.get('profile'))
        preview=self.interest_preview(dict(profile=p['id'],start=d.get('start'),end=d.get('end'),acknowledge=True),s)
        # Freeze financial/source facts, excluding audit history and unrelated account reports.
        selected={x['transaction'] for x in d.get('payments',[])}
        relevant=[]
        for t in s['transactions']:
            parts=[x for x in t['allocations'] if x.get('profile')==p['id'] and x['category'] in {'principal','interest'}]
            if not (parts and t['date']<d['end'] or t['id'] in selected):continue
            relevant.append({k:copy.deepcopy(t[k]) for k in ('id','account','date','reference','description','signed_amount','allocations','sources') if k in t})
        accounts={t['account'] for t in relevant}
        preview['coverage']=[{k:copy.deepcopy(r[k]) for k in ('account','source_periods','coverage_gaps','unknown_count','tracking_date','coverage_note')} for r in preview['coverage'] if r['account'] in accounts]
        profile={k:copy.deepcopy(p.get(k)) for k in ('id','name','party','kind','debt_setup')}
        return dict(preview=preview,profile=profile,transactions=relevant)

    def interest_basis_hash(self,basis):
        financial=copy.deepcopy(basis)
        for segment in financial['preview']['segments']:
            segment['term'].pop('reason',None)
        return digest(financial)

    @precise
    def interest_candidates(self,s,profile):
        p=item(s['profiles'],profile);incoming=p.get('debt_setup',{}).get('direction')=='RECEIVABLE';result=[]
        for t in s['transactions']:
            if not t.get('sources') or (D(t['signed_amount'])>0)!=incoming:continue
            amount=sum((D(a['amount']) for a in t['allocations'] if a.get('profile')==profile and a['category']=='interest'),Decimal(0))
            if amount>0:result.append(dict(transaction=t['id'],date=t['date'],reference=t['reference'],amount=S(amount),account=t['account']))
        return result

    @precise
    def interest_status(self,s,statement):
        latest=statement.get('versions',[])[-1] if statement.get('versions') else None
        if not latest:return dict(source_changed=False,invalid_payments=False)
        try:changed=self.interest_basis_hash(self.interest_basis(s,latest['draft']))!=latest['basis_hash']
        except (ValidationError,KeyError):changed=True
        candidates={x['transaction']:D(x['amount']) for x in self.interest_candidates(s,statement['profile'])}
        used={}
        for st in s.get('interest_statements',[]):
            if st['profile']!=statement['profile'] or not st['versions']:continue
            for x in st['versions'][-1]['draft']['payments']:used[x['transaction']]=used.get(x['transaction'],Decimal(0))+D(x['amount'])
        invalid=any(used.get(x['transaction'],Decimal(0))>candidates.get(x['transaction'],Decimal(0)) for x in latest['draft']['payments'])
        return dict(source_changed=changed,invalid_payments=invalid)

    @precise
    def interest_statement_view(self,s):
        return [dict(copy.deepcopy(st),**self.interest_status(s,st)) for st in s.get('interest_statements',[])]

    @precise
    def settlement_preview(self,d,s=None):
        from .p01 import money, day
        with self.lock:
            s=s or self.state();basis=self.interest_basis(s,d);profile=d['profile'];statement=d.get('statement')
            for st in s.get('interest_statements',[]):
                if st['id']==statement or st['profile']!=profile:continue
                periods=[st['draft']]+[v['draft'] for v in st['versions'][-1:]]
                require(not any(d['start']<x['end'] and x['start']<d['end'] for x in periods),'Kỳ chồng với bảng kê khác của khoản vay; mở bảng kê đó để điều chỉnh.')
            used={};invalid=[]
            selected_ids={x.get('transaction') for x in d.get('payments',[])}
            for st in s.get('interest_statements',[]):
                if st['id']==statement or not st['versions']:continue
                linked=st['profile']==profile or bool(selected_ids & {x['transaction'] for x in st['versions'][-1]['draft']['payments']})
                if linked and self.interest_status(s,st)['invalid_payments']:invalid.append(st['id'])
                if st['profile']==profile:
                    for x in st['versions'][-1]['draft']['payments']:used[x['transaction']]=used.get(x['transaction'],Decimal(0))+D(x['amount'])
            candidates=self.interest_candidates(s,profile)
            for c in candidates:c['available']=S(max(Decimal(0),D(c['amount'])-used.get(c['transaction'],Decimal(0))))
            available={c['transaction']:D(c['available']) for c in candidates};payments=d.get('payments',[])
            require(isinstance(payments,list),'Danh sách phân bổ không hợp lệ.');seen=set();applied=Decimal(0)
            for x in payments:
                amount=money(x.get('amount'));key=x.get('transaction')
                require(key not in seen and amount>0,'Chọn giao dịch riêng biệt và số tiền nguyên VND dương.');seen.add(key)
                require(amount<=available.get(key,Decimal(0)),'Tiền lãi không còn đủ, sai khoản vay / chiều tiền hoặc nguồn đã đổi; kiểm tra bảng kê liên quan.')
                applied+=amount
            expected=D(basis['preview']['total']);waiver=money(d.get('waiver','0'))
            require(applied<=expected,'Chỉ phân bổ tối đa lãi dự tính; tiền dư giữ chưa phân bổ.')
            require(0<=waiver<=expected-applied,'Miễn giảm phải từ 0 đến phần còn lại sau phân bổ.')
            if waiver:require(str(d.get('waiver_reason','')).strip(),'Cần lý do miễn giảm.');day(d.get('waiver_date'))
            remaining=expected-applied-waiver
            payload={k:copy.deepcopy(d.get(k,'')) for k in ('profile','start','end','waiver_date','waiver_reason','convention_basis')}
            payload.update(payments=sorted([dict(transaction=x['transaction'],amount=S(money(x['amount']))) for x in payments],key=lambda x:x['transaction']),waiver=S(waiver))
            token=digest(dict(basis=basis,draft=payload,used={k:S(v) for k,v in used.items()},invalid=invalid))
            return dict(draft=payload,basis=basis,basis_hash=self.interest_basis_hash(basis),review_token=token,expected=S(expected),applied=S(applied),waiver=S(waiver),remaining=S(remaining),unapplied=S(sum((D(c['available']) for c in candidates),Decimal(0))-applied),candidates=candidates,invalid_statements=invalid,coverage_warning=True)

    @precise
    def change_interest(self,s,action,d):
        from .p01 import now
        statements=s.setdefault('interest_statements',[])
        if action=='interest-reopen':
            st=item(statements,d.get('statement'));require(st['versions'],'Chưa có bản duyệt.')
            require(not st.get('editing'),'Đã mở bản nháp điều chỉnh.')
            reason=str(d.get('reason','')).strip();require(reason,'Cần lý do điều chỉnh.')
            st.update(editing=True,correction_reason=reason[:500],draft=copy.deepcopy(st['versions'][-1]['draft']))
            return 'Mở điều chỉnh bảng kê lãi; giữ bản duyệt cũ.'
        if action=='interest-draft':
            st=item(statements,d['statement']) if d.get('statement') else None
            require(not st or st.get('editing'),'Mở điều chỉnh có lý do trước khi sửa bản đã duyệt.')
            if st:require(st['profile']==d.get('profile'),'Không đổi khoản vay của bảng kê.')
            r=self.settlement_preview(d,s)
            if not st:st=dict(id=uid(),profile=d['profile'],versions=[],editing=True,correction_reason='');statements.append(st)
            st['draft']=r['draft'];st['saved_at']=now()
            return 'Lưu nháp bảng kê lãi '+st['id']
        st=item(statements,d.get('statement'));require(st.get('editing'),'Bảng kê đã duyệt; mở điều chỉnh trước.')
        r=self.settlement_preview(dict(st['draft'],statement=st['id']),s)
        require(d.get('review_token')==r['review_token'],'Dữ liệu đã thay đổi; xem lại bảng kê hiện tại trước khi duyệt.')
        if r['invalid_statements']:
            previous_payments={x['transaction']:D(x['amount']) for x in st['versions'][-1]['draft']['payments']} if st['versions'] else {}
            current_payments={x['transaction']:D(x['amount']) for x in r['draft']['payments']}
            reduces=all(v<=previous_payments.get(k,Decimal(0)) for k,v in current_payments.items()) and sum(current_payments.values(),Decimal(0))<sum(previous_payments.values(),Decimal(0))
            require(reduces,'Có bảng kê đã duyệt dùng tiền không còn hợp lệ; cần giảm / bỏ phân bổ của bảng kê liên quan trước.')
        require(d.get('confirm_convention') is True and str(st['draft'].get('convention_basis','')).strip(),'Xác nhận quy ước thực sự áp dụng cho bảng kê và nhập căn cứ thỏa thuận.')
        require(d.get('confirm_coverage') is True,'Xác nhận phạm vi nguồn có thể chưa đầy đủ.')
        require(not D(r['waiver']) or d.get('confirm_waiver') is True,'Thạch cần xác nhận riêng quyết định miễn giảm.')
        previous=st['versions'][-1] if st['versions'] else None
        require(not previous or digest(dict(draft=r['draft'],basis_hash=r['basis_hash']))!=digest(dict(draft=previous['draft'],basis_hash=previous['basis_hash'])),'Nội dung không đổi; không tạo bản duyệt trùng.')
        snap={k:copy.deepcopy(r[k]) for k in ('draft','basis','basis_hash','expected','applied','waiver','remaining','unapplied','candidates')}
        snap.update(id=uid(),version=len(st['versions'])+1,actor='Thạch',approved_at=now(),reason=st['correction_reason'],restates=previous['id'] if previous else None,confirm_convention=True,confirm_coverage=True,confirm_waiver=bool(d.get('confirm_waiver')))
        snap['hash']=digest(snap);st['versions'].append(snap);st['editing']=False
        return 'Đã duyệt bảng kê lãi phiên bản '+str(snap['version'])
