"""Explicit statement allocation, amendment and source-change regression cases."""
import base64
import copy
import tempfile
import unittest
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError, digest
from p01_fixtures import statement


def seed(store):
    def act(action,**data):return store.apply(action,data,str(uuid4()))
    act('account',name='P06 · Ngân hàng giả lập',reference='000123',opening='10000000',effective_date='2026-10-01',opening_source='Dữ liệu QA giả lập')
    account=store.state()['accounts'][0]['id']
    act('profile',kind='PERSON',name='QA · Nguyễn An');person=store.state()['profiles'][-1]['id'];loans=[]
    for name,direction in [('Khoản A · 100 triệu','RECEIVABLE'),('Khoản B · 100 triệu','RECEIVABLE'),('Khoản C · đi vay','PAYABLE')]:
        act('profile',kind='LOAN',name=name,party=person);loan=store.state()['profiles'][-1]['id'];loans.append(loan)
        act('loan-setup',profile=loan,direction=direction,opening='100000000',effective_date='2026-10-01',source='Gốc đầu kỳ giả lập',reason='QA')
        act('interest-terms',profile=loan,unit='VND_MILLION_DAY',value='500',effective_date='2026-10-01',source='Thỏa thuận giả lập 500 VND/triệu/ngày',reason='QA',acknowledge=True)
    rows=[('31/10/2026','Lai khoan A','INT-A','','1200000','11200000'),('01/11/2026','Lai khoan B','INT-B','','2000000','13200000'),('01/11/2026','Tra lai khoan C','INT-C','1200000','','12000000')]
    raw=statement(rows,10000000,12000000,end='01/11/2026')
    act('import',account=account,filename='p06-qa.xlsx',content=base64.b64encode(raw).decode());act('publish',batch=store.state()['imports'][-1]['id'])
    for t,loan in zip(store.state()['transactions'],loans):act('classify',ids=[t['id']],parts=[dict(category='interest',profile=loan)],reason='QA phân bổ đúng khoản')
    return account,loans,[t['id'] for t in store.state()['transactions']]

class P06Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name);self.store.require_membership=False;self.account,self.loans,self.payments=seed(self.store)
    def tearDown(self):self.tmp.cleanup()
    def act(self,action,**data):return self.store.apply(action,data,str(uuid4()))
    def data(self,**kw):return dict(profile=self.loans[0],start='2026-10-01',end='2026-10-31',payments=[dict(transaction=self.payments[0],amount='1200000')],waiver='0',convention_basis='Thỏa thuận giả lập riêng cho bảng kê')|kw
    def draft(self,**kw):
        self.act('interest-draft',**self.data(**kw));return self.store.state()['interest_statements'][-1]
    def approve(self,st,**kw):
        r=self.store.settlement_preview(dict(st['draft'],statement=st['id']))
        return self.act('interest-approve',**(dict(statement=st['id'],review_token=r['review_token'],confirm_convention=True,confirm_coverage=True,confirm_waiver=True)|kw))
    def test_a36_a37_immutable_waiver_and_actual_cash(self):
        before=self.store.view()['debts'];st=self.draft();self.approve(st);old=copy.deepcopy(self.store.state()['interest_statements'][0]['versions'][0]);self.assertEqual((old['expected'],old['applied'],old['remaining']),('1500000','1200000','300000'))
        self.act('interest-reopen',statement=st['id'],reason='Đồng ý giảm lãi');st=self.draft(statement=st['id'],waiver='300000',waiver_date='2026-10-31',waiver_reason='Khách và Thạch thống nhất')
        self.assertEqual(self.store.state()['interest_statements'][0]['versions'][0],old)
        with self.assertRaises(ValidationError):self.approve(st,confirm_waiver=False)
        self.approve(st);versions=self.store.state()['interest_statements'][0]['versions'];self.assertEqual(versions[0],old);self.assertEqual((versions[1]['applied'],versions[1]['waiver'],versions[1]['remaining']),('1200000','300000','0'));self.assertEqual(self.store.view()['debts'],before)
        self.act('interest-reopen',statement=st['id'],reason='Nothing changed')
        with self.assertRaises(ValidationError):self.approve(st)
    def test_explicit_partial_no_double_use_overlap_other_loan_direction(self):
        r=self.store.settlement_preview(self.data(payments=[]));self.assertEqual(r['applied'],'0');self.assertEqual(len(r['candidates']),1)
        st=self.draft(payments=[dict(transaction=self.payments[0],amount='600000')]);self.approve(st)
        for kw in [dict(start='2026-10-15',end='2026-11-15',payments=[]),dict(start='2026-10-31',end='2026-11-30'),dict(payments=[dict(transaction=self.payments[1],amount='100')],profile=self.loans[2])]:
            with self.assertRaises(ValidationError):self.draft(**kw)
        second=self.draft(start='2026-10-31',end='2026-11-30',payments=[dict(transaction=self.payments[0],amount='600000')]);self.approve(second)
        with self.assertRaises(ValidationError):self.draft(start='2026-11-30',end='2026-12-30',payments=[dict(transaction=self.payments[0],amount='1')])
        r=self.store.settlement_preview(self.data(profile=self.loans[2],payments=[dict(transaction=self.payments[2],amount='1200000')]));self.assertEqual(r['applied'],'1200000')
    def test_invalid_amounts_acknowledgements_excess_and_stale(self):
        for kw in [dict(waiver='-1'),dict(waiver='0.5'),dict(waiver='NaN'),dict(waiver='300001'),dict(waiver='300000'),dict(payments=[dict(transaction=self.payments[0],amount='0')]),dict(payments=[dict(transaction=self.payments[0],amount='Infinity')])]:
            with self.assertRaises(ValidationError):self.draft(**kw)
        r=self.store.settlement_preview(self.data(profile=self.loans[1],payments=[dict(transaction=self.payments[1],amount='1500000')]));self.assertEqual(r['unapplied'],'500000')
        with self.assertRaises(ValidationError):self.draft(profile=self.loans[1],payments=[dict(transaction=self.payments[1],amount='1500001')])
        st=self.draft()
        for kw in [dict(confirm_convention=False),dict(confirm_coverage=False)]:
            with self.assertRaises(ValidationError):self.approve(st,**kw)
        r=self.store.settlement_preview(dict(st['draft'],statement=st['id']))
        self.act('classify',ids=[self.payments[0]],parts=[dict(category='interest',amount='1100000',profile=self.loans[0]),dict(category='income',amount='100000')],reason='Source classification correction')
        with self.assertRaises(ValidationError):self.approve(st,review_token=r['review_token'])
    def test_shared_source_shrink_can_be_corrected_without_deadlock(self):
        st=self.draft(payments=[dict(transaction=self.payments[0],amount='600000')]);self.approve(st)
        second=self.draft(start='2026-10-31',end='2026-11-30',payments=[dict(transaction=self.payments[0],amount='600000')]);self.approve(second)
        self.act('classify',ids=[self.payments[0]],parts=[dict(category='interest',amount='300000',profile=self.loans[0]),dict(category='income',amount='900000')],reason='Correct source')
        self.assertTrue(all(x['invalid_payments'] for x in self.store.view()['interest_statements']))
        self.act('interest-reopen',statement=st['id'],reason='Remove allocation');self.act('interest-draft',**self.data(statement=st['id'],payments=[]));self.approve(self.store.state()['interest_statements'][0])
        self.act('interest-reopen',statement=second['id'],reason='Reduce allocation');self.act('interest-draft',**self.data(statement=second['id'],start='2026-10-31',end='2026-11-30',payments=[dict(transaction=self.payments[0],amount='300000')]));self.approve(self.store.state()['interest_statements'][1]);self.assertFalse(any(x['invalid_payments'] for x in self.store.view()['interest_statements']))
    def test_stable_basis_unrelated_changes_and_legacy_backup(self):
        st=self.draft();self.approve(st)
        self.act('account',name='Unrelated',reference='99999',opening='0',effective_date='2026-10-01',opening_source='Unrelated')
        self.act('interest-terms',profile=self.loans[0],unit='VND_MILLION_DAY',value='500',effective_date='2026-10-01',source='Thỏa thuận giả lập 500 VND/triệu/ngày',reason='Audit only',acknowledge=True)
        self.assertFalse(self.store.view()['interest_statements'][0]['source_changed'])
        restored=P01Store(self.tmp.name+'/restored');restored.restore(self.store.backup(),'restore');self.assertEqual(restored.view()['interest_statements'],self.store.view()['interest_statements'])
        empty=P01Store(self.tmp.name+'/legacy');legacy=empty.backup();other=P01Store(self.tmp.name+'/other');other.restore(legacy,'legacy');self.assertEqual(other.view()['interest_statements'],[])
        bundle=self.store.backup();snap=bundle['events'][-1]['state']['interest_statements'][0]['versions'][0];snap['applied']='1'
        e=bundle['events'][-1];e['hash']=digest({k:v for k,v in e.items() if k!='hash'});bundle['checksum']=digest(bundle['events'])
        with self.assertRaises(ValidationError):self.store.validate_bundle(bundle)

    def test_stale_token_rechecked_and_large_integer_difference(self):
        st=self.draft();r=self.store.settlement_preview(dict(st['draft'],statement=st['id']))
        self.act('interest-terms',profile=self.loans[0],unit='VND_MILLION_DAY',value='600',effective_date='2026-10-01',source='New agreement',reason='Rate correction',acknowledge=True)
        with self.assertRaises(ValidationError):self.approve(st,review_token=r['review_token'])
        self.approve(st)
        self.assertEqual(self.store.state()['interest_statements'][0]['versions'][0]['expected'],'1800000')
        s=self.store.state();s['interest_statements']=[]
        p=next(p for p in s['profiles'] if p['id']==self.loans[0]);p['debt_setup']['opening']='999999999999999999999999999999';p['interest_terms'][0]['value']='1000000'
        t=s['transactions'][0];t['signed_amount']='999999999999999999999999999998';t['allocations'][0]['amount']=t['signed_amount']
        r=self.store.settlement_preview(self.data(end='2026-10-02',payments=[dict(transaction=t['id'],amount=t['signed_amount'])]),s)
        self.assertEqual(r['remaining'],'1');self.assertEqual(r['unapplied'],'0')

    def test_reclassification_other_loan_cannot_reuse_reserved_cash(self):
        st=self.draft();self.approve(st)
        self.act('classify',ids=[self.payments[0]],parts=[dict(category='interest',profile=self.loans[1])],reason='Correct linked loan')
        self.assertTrue(self.store.view()['interest_statements'][0]['invalid_payments'])
        other=self.draft(profile=self.loans[1])
        with self.assertRaises(ValidationError):self.approve(other)
        self.act('interest-reopen',statement=st['id'],reason='Release incorrect link');self.act('interest-draft',**self.data(statement=st['id'],payments=[]));self.approve(self.store.state()['interest_statements'][0]);self.approve(other)

    def test_ui_save_reload_preview_response_envelope_then_approve(self):
        st=self.draft()
        reloaded=P01Store(self.tmp.name)
        st=reloaded.view()['interest_statements'][0]
        self.assertEqual(st['draft']['payments'],[dict(transaction=self.payments[0],amount='1200000')])
        self.assertEqual(st['draft']['convention_basis'],'Thỏa thuận giả lập riêng cho bảng kê')
        # server.py adds its CSRF token to every response. The review token must survive.
        response={**reloaded.settlement_preview(dict(st['draft'],statement=st['id'])),'token':'session-csrf-token'}
        reloaded.apply('interest-approve',dict(statement=st['id'],review_token=response['review_token'],confirm_convention=True,confirm_coverage=True,confirm_waiver=False),str(uuid4()))
        self.assertEqual(reloaded.state()['interest_statements'][0]['versions'][0]['remaining'],'300000')
