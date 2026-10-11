"""Explicit immutable completion evidence and allocation-based VND cash reports."""
import copy
from datetime import date, timedelta
from decimal import Decimal
from .core import require, digest, ValidationError
from .product import D, S, uid, item
from .interest_settlement import precise

class LoanCompletion:
    def closure_basis(self,s,profile):
        p=item(s['profiles'],profile)
        transactions=[{k:copy.deepcopy(t.get(k)) for k in ('id','account','date','reference','signed_amount','allocations','sources')} for t in s['transactions'] if any(a.get('profile')==profile for a in t['allocations'])]
        return dict(profile={k:copy.deepcopy(p.get(k)) for k in ('id','kind','party','debt_setup','interest_terms')},transactions=transactions,statements=copy.deepcopy([st for st in s.get('interest_statements',[]) if st['profile']==profile]))

    def completion_status(self,s,profile):
        p=item(s['profiles'],profile);history=p.get('completion_history',[])
        if not history or history[-1]['action']=='REOPEN':return 'ACTIVE'
        unchanged=history[-1]['basis_hash']==digest(self.closure_basis(s,profile))
        valid=all(not any(self.interest_status(s,st).values()) for st in s.get('interest_statements',[]) if st['profile']==profile)
        return 'COMPLETED' if unchanged and valid else 'NEEDS_REVIEW'

    @precise
    def closure_preview(self,d,s=None):
        from .p01 import day
        s=s or self.state();profile=d.get('profile');p=item(s['profiles'],profile)
        require(p['kind']=='LOAN','Chọn khoản vay.')
        closing=day(d.get('closing_date'));setup=p.get('debt_setup')
        require(setup and setup['effective_date']<=closing,'Cần thiết lập hợp lệ và ngày hoàn tất từ mốc mở khoản.')
        loan=next(x for x in self.debt_register(s)['loans'] if x['id']==profile)
        require(not loan['issues'] and D(loan['current_principal'])==0,'Chỉ hoàn tất khi gốc bằng 0 và không có lỗi khoản vay.')
        relevant=[t for t in s['transactions'] if any(a.get('profile')==profile for a in t['allocations'])]
        require(all(t.get('sources') and t['date']<=closing for t in relevant),'Có giao dịch thiếu nguồn hoặc sau ngày hoàn tất.')
        statements=[st for st in s.get('interest_statements',[]) if st['profile']==profile]
        require(statements and all(st['versions'] and not st.get('editing') for st in statements),'Cần bảng kê lãi đã duyệt; không được còn bản nháp.')
        end=(date.fromisoformat(closing)+timedelta(days=1)).isoformat();cursor=setup['effective_date']
        for st in sorted(statements,key=lambda st:st['versions'][-1]['draft']['start']):
            v=st['versions'][-1];status=self.interest_status(s,st)
            require(not any(status.values()) and D(v['remaining'])==0,'Bảng kê còn lãi hoặc nguồn/phân bổ đã thay đổi; cần kiểm tra lại.')
            require(v.get('confirm_convention') and v['draft'].get('convention_basis'),'Thiếu xác nhận thỏa thuận bảng kê.')
            require(v['draft']['start']<=cursor,'Thiếu kỳ lãi trong khoảng từ mốc mở đến hết ngày hoàn tất.')
            cursor=max(cursor,v['draft']['end'])
        require(cursor>=end,'Chưa có bảng kê bao phủ hết ngày hoàn tất (ngày cuối có tính).')
        # Recompute also proves rates are explicit, including agreed zero rates.
        self.interest_preview(dict(profile=profile,start=setup['effective_date'],end=end,acknowledge=True),s)
        basis=self.closure_basis(s,profile)
        return dict(profile=profile,closing_date=closing,basis=basis,basis_hash=digest(basis),review_token=digest(dict(basis=basis,closing_date=closing)))

    def completion_blocker(self,s,profile):
        """Read-only hint for the debt screen; reuses closure_preview so the rules cannot drift."""
        p=item(s['profiles'],profile);setup=p.get('debt_setup')
        if p['kind']!='LOAN' or self.completion_status(s,profile)!='ACTIVE':return None
        if not setup:return dict(code='NEEDS_SETUP')
        loan=next(x for x in self.debt_register(s)['loans'] if x['id']==profile)
        if loan['current_principal'] is None or D(loan['current_principal'])!=0:return None
        dates=[t['date'] for t in s['transactions'] if any(a.get('profile')==profile for a in t['allocations'])]
        try:self.closure_preview(dict(profile=profile,closing_date=max(dates+[setup['effective_date']])),s)
        except ValidationError as e:return dict(code='BLOCKED',message=str(e))
        return dict(code='READY')

    def change_completion(self,s,action,d):
        from .p01 import now
        p=item(s['profiles'],d.get('profile'));require(p['kind']=='LOAN','Chọn khoản vay.')
        history=p.setdefault('completion_history',[]);reason=str(d.get('reason','')).strip();require(reason,'Cần lý do.')
        if action=='loan-reopen':
            require(history and history[-1]['action']=='COMPLETE','Khoản chưa hoàn tất.')
            snap=dict(id=uid(),action='REOPEN',reason=reason[:500],actor='Thạch',at=now(),previous=history[-1]['id'])
        else:
            require(not history or history[-1]['action']=='REOPEN','Mở lại có lý do trước khi xác nhận hoàn tất mới.')
            r=self.closure_preview(d,s)
            require(d.get('review_token')==r['review_token'],'Dữ liệu đã đổi; kiểm tra lại trước khi hoàn tất.')
            basis=str(d.get('basis','')).strip();require(basis and d.get('confirm') is True,'Cần căn cứ và xác nhận hoàn tất rõ ràng.')
            snap=dict(r,id=uid(),action='COMPLETE',reason=reason[:500],agreement_basis=basis[:1000],actor='Thạch',at=now(),confirmed=True)
            snap.pop('review_token')
        snap['hash']=digest(snap);history.append(snap)
        return 'Đã hoàn tất, giữ lịch sử.' if action=='loan-complete' else 'Đã mở lại khoản vay, giữ bằng chứng hoàn tất cũ.'

    @precise
    def loan_cash_report(self,d,s=None):
        from .p01 import day
        s=s or self.state();chosen=date.fromisoformat(day(d.get('date')));period=d.get('period');require(period in {'week','month','quarter'},'Chọn tuần, tháng hoặc quý.')
        if period=='week':start=chosen-timedelta(days=chosen.weekday());end=start+timedelta(days=7)
        else:
            month=chosen.month if period=='month' else ((chosen.month-1)//3)*3+1
            start=date(chosen.year,month,1);next_month=month+(1 if period=='month' else 3);end=date(chosen.year+(next_month-1)//12,(next_month-1)%12+1,1)
        totals={k:Decimal(0) for k in ('interest_received','interest_paid','principal_recovered','principal_disbursed','new_borrowings','principal_repaid','tagged_expenses','expense_refunds')};entries=[]
        loans={p['id']:p for p in s['profiles'] if p['kind']=='LOAN'}
        for t in s['transactions']:
            if not t.get('sources') or not start.isoformat()<=t['date']<end.isoformat():continue
            incoming=D(t['signed_amount'])>0
            for a in t['allocations']:
                p=loans.get(a.get('profile'))
                if not p:continue
                category=a['category'];key=None
                if category=='interest':key='interest_received' if incoming else 'interest_paid'
                elif category=='expense':key='expense_refunds' if incoming else 'tagged_expenses'
                elif category=='principal' and p.get('debt_setup'):
                    key=('principal_recovered' if incoming else 'principal_disbursed') if p['debt_setup']['direction']=='RECEIVABLE' else ('new_borrowings' if incoming else 'principal_repaid')
                if key:
                    totals[key]+=D(a['amount']);entries.append(dict(transaction=t['id'],date=t['date'],reference=t['reference'],profile=p['id'],name=p['name'],category=key,amount=a['amount'],sources=copy.deepcopy(t['sources'])))
        return dict(start=start.isoformat(),end=end.isoformat(),period=period,totals={k:S(v) for k,v in totals.items()},cash_difference=S(totals['interest_received']-totals['interest_paid']-totals['tagged_expenses']+totals['expense_refunds']),entries=entries)
