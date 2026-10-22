import base64
import copy
import tempfile
import unittest
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError, digest
from p01_fixtures import statement


def seed(store):
    def act(action,**d):return store.apply(action,d,str(uuid4()))
    act('account',name='P07 ngân hàng giả lập',reference='000123',opening='10000000',effective_date='2026-09-01',opening_source='QA giả lập')
    account=store.state()['accounts'][0]['id'];loans=[]
    for name in ['An · đã hoàn tất','Bình · đang hoạt động','Chi · hết gốc còn lãi']:
        act('profile',kind='PERSON',name=name);person=store.state()['profiles'][-1]['id']
        act('profile',kind='LOAN',name='Khoản '+name,party=person);loan=store.state()['profiles'][-1]['id'];loans.append(loan)
        act('loan-setup',profile=loan,direction='RECEIVABLE',opening='100000000',effective_date='2026-09-01',source='Gốc theo thỏa thuận QA',reason='QA')
        act('interest-terms',profile=loan,unit='VND_MILLION_DAY',value='500',effective_date='2026-09-01',source='Thỏa thuận QA 500',reason='QA',acknowledge=True)
    rows=[('25/09/2026','Lai A','P07-INT-A','','1200000','11200000'),('25/09/2026','Goc A','P07-PR-A','','100000000','111200000'),('28/09/2026','Lai B','P07-INT-B','','1500000','112700000'),('29/09/2026','Chi phi co gan','P07-COST','200000','','112500000'),('30/09/2026','Goc C','P07-PR-C','','100000000','212500000')]
    act('import',account=account,filename='p07-qa.xlsx',content=base64.b64encode(statement(rows,10000000,212500000,start='01/09/2026',end='30/09/2026')).decode());act('publish',batch=store.state()['imports'][-1]['id'])
    for t,category,loan in zip(store.state()['transactions'],['interest','principal','interest','expense','principal'],[loans[0],loans[0],loans[1],loans[0],loans[2]]):act('classify',ids=[t['id']],parts=[dict(category=category,profile=loan)],reason='QA')
    payment=store.state()['transactions'][0]['id']
    for loan,payments in [(loans[0],[dict(transaction=payment,amount='1200000')]),(loans[2],[])]:
        act('interest-draft',profile=loan,start='2026-09-01',end='2026-10-01',payments=payments,waiver='0',convention_basis='Thỏa thuận tính ngày cuối và xác nhận QA')
        st=store.state()['interest_statements'][-1];r=store.settlement_preview(dict(st['draft'],statement=st['id']))
        act('interest-approve',statement=st['id'],review_token=r['review_token'],confirm_convention=True,confirm_coverage=True)
    d=dict(profile=loans[0],closing_date='2026-09-30');r=store.closure_preview(d)
    act('loan-complete',**d,review_token=r['review_token'],reason='Đã trả đủ',basis='Biên nhận tất toán QA',confirm=True)
    return loans

class P07Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name);self.store.require_membership=False;self.loans=seed(self.store)
    def tearDown(self):self.tmp.cleanup()
    def act(self,a,**d):return self.store.apply(a,d,str(uuid4()))
    def test_completion_reopen_stale_immutable_backup(self):
        s=self.store.state();p=next(x for x in s['profiles'] if x['id']==self.loans[0]);snap=copy.deepcopy(p['completion_history'][0]);cash=copy.deepcopy(s['transactions']);bank=copy.deepcopy(s['snapshots'])
        self.assertEqual(self.store.completion_status(s,self.loans[0]),'COMPLETED')
        self.act('interest-terms',profile=self.loans[0],unit='VND_MILLION_DAY',value='600',effective_date='2026-09-01',source='Changed rate',reason='Correction',acknowledge=True)
        self.assertEqual(self.store.completion_status(self.store.state(),self.loans[0]),'NEEDS_REVIEW')
        self.act('loan-reopen',profile=self.loans[0],reason='Recheck')
        p=next(x for x in self.store.state()['profiles'] if x['id']==self.loans[0]);self.assertEqual(p['completion_history'][0],snap)
        self.assertEqual(self.store.state()['transactions'],cash);self.assertEqual(self.store.state()['snapshots'],bank)
        restore=P01Store(self.tmp.name+'/restore');restore.restore(self.store.backup(),'restore');self.assertEqual(restore.state(),self.store.state())
        bundle=self.store.backup();e=bundle['events'][-1];next(p for p in e['state']['profiles'] if p['id']==self.loans[0])['completion_history'][0]['reason']='tamper';e['hash']=digest({k:v for k,v in e.items() if k!='hash'});bundle['checksum']=digest(bundle['events'])
        with self.assertRaises(ValidationError):self.store.validate_bundle(bundle)
    def test_unpaid_draft_missing_coverage_and_postdate(self):
        with self.assertRaises(ValidationError):self.store.closure_preview(dict(profile=self.loans[2],closing_date='2026-09-30'))
        base=self.store.state();d=dict(profile=self.loans[0],closing_date='2026-09-30')
        for change in ['draft','missing','hole','postdate','source']:
            s=copy.deepcopy(base);st=s['interest_statements'][0]
            if change=='draft':st['editing']=True
            if change=='missing':s['interest_statements']=[]
            if change=='hole':st['versions'][-1]['draft']['end']='2026-09-29'
            if change=='postdate':s['transactions'][0]['date']='2026-10-01'
            if change=='source':s['transactions'][0]['sources']=[]
            with self.assertRaises(ValidationError,msg=change):self.store.closure_preview(d,s)
        self.act('loan-reopen',profile=self.loans[0],reason='QA');r=self.store.closure_preview(d)
        with self.assertRaises(ValidationError):self.act('loan-complete',**d,review_token='stale',confirm=True,reason='QA',basis='QA')
        with self.assertRaises(ValidationError):self.act('loan-complete',**d,review_token=r['review_token'],confirm=False,reason='QA',basis='QA')
    def test_explicit_zero_rate_and_relevant_source_invalidation(self):
        loan=self.loans[1]
        self.act('loan-setup',profile=loan,direction='RECEIVABLE',opening='0',effective_date='2026-09-01',source='Confirmed zero opening',reason='QA zero',confirm_zero=True)
        self.act('interest-terms',profile=loan,unit='VND_MILLION_DAY',value='0',effective_date='2026-09-01',source='Explicit interest-free agreement',reason='QA',acknowledge=True)
        d=dict(profile=loan,closing_date='2026-09-30')
        with self.assertRaises(ValidationError):self.store.closure_preview(d)
        self.act('interest-draft',profile=loan,start='2026-09-01',end='2026-10-01',payments=[],waiver='0',convention_basis='Explicit zero interest agreement')
        st=self.store.state()['interest_statements'][-1];r=self.store.settlement_preview(dict(st['draft'],statement=st['id']))
        self.act('interest-approve',statement=st['id'],review_token=r['review_token'],confirm_convention=True,confirm_coverage=True)
        r=self.store.closure_preview(d)
        self.act('loan-complete',**d,review_token=r['review_token'],reason='Agreed paid',basis='QA',confirm=True)
        self.assertEqual(self.store.completion_status(self.store.state(),loan),'COMPLETED')
        s=self.store.state();p=next(x for x in s['profiles'] if x['id']==loan);snapshot=copy.deepcopy(p['completion_history'][0])
        t=s['transactions'][2];self.act('classify',ids=[t['id']],parts=[dict(category='income')],reason='Correct classification')
        self.assertEqual(self.store.completion_status(self.store.state(),loan),'NEEDS_REVIEW')
        self.assertEqual(next(x for x in self.store.state()['profiles'] if x['id']==loan)['completion_history'][0],snapshot)

    def test_shared_coverage_staleness_and_expense_refunds(self):
        s=self.store.state();loan=self.loans[0]
        before=digest(self.store.closure_basis(s,loan))
        # Coverage changes can invalidate a statement without changing any loan transaction.
        s['accounts'][0]['effective_date']='2026-08-01'
        self.assertEqual(before,digest(self.store.closure_basis(s,loan)))
        self.assertEqual(self.store.completion_status(s,loan),'NEEDS_REVIEW')
        s=self.store.state();t=copy.deepcopy(s['transactions'][3]);t.update(id='refund',signed_amount='50000');t['allocations']=[dict(category='expense',profile=loan,amount='50000')];s['transactions'].append(t)
        r=self.store.loan_cash_report(dict(date='2026-09-15',period='month'),s)
        self.assertEqual(r['totals']['expense_refunds'],'50000');self.assertEqual(r['cash_difference'],'2550000')
        self.assertTrue(any(e['transaction']=='refund' and e['sources'] for e in r['entries']))

    def test_report_exact_scope_partial_and_calendar(self):
        r=self.store.loan_cash_report(dict(date='2026-09-30',period='month'))
        self.assertEqual((r['totals']['interest_received'],r['totals']['tagged_expenses'],r['cash_difference']),('2700000','200000','2500000'))
        self.assertEqual(r['totals']['principal_recovered'],'200000000')
        for chosen,period,start,end in [('2026-09-27','week','2026-09-21','2026-09-28'),('2026-09-28','week','2026-09-28','2026-10-05'),('2026-12-31','quarter','2026-10-01','2027-01-01'),('2028-02-29','month','2028-02-01','2028-03-01')]:
            r=self.store.loan_cash_report(dict(date=chosen,period=period));self.assertEqual((r['start'],r['end']),(start,end))
        s=self.store.state();t=s['transactions'][3];person=next(p for p in s['profiles'] if p['kind']=='PERSON')['id'];t['allocations']=[dict(category='expense',profile=self.loans[0],amount='123456'),dict(category='expense',profile=person,amount='76544')]
        s['interest_statements'][0]['versions'][0]['waiver']='999999999'
        r=self.store.loan_cash_report(dict(date='2026-09-01',period='quarter'),s);self.assertEqual(r['totals']['tagged_expenses'],'123456');self.assertEqual(r['cash_difference'],'2576544')
        self.assertEqual(sum(int(e['amount']) for e in r['entries'] if e['category']=='interest_received'),2700000)

if __name__=='__main__':unittest.main()
