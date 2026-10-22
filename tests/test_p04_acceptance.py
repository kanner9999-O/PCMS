"""P04 explicit debt facts, sourced allocations, and immutable snapshots."""
import base64
import copy
import tempfile
import unittest
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError
from p01_fixtures import statement


def seed(store):
    def act(action,**data):return store.apply(action,data,str(uuid4()))
    act('account',name='P04 synthetic bank',reference='000123',opening='200000000',effective_date='2026-10-01',opening_source='Synthetic QA')
    a=store.state()['accounts'][0]['id']
    act('profile',kind='PERSON',name='QA · Nguyễn An');person=store.state()['profiles'][-1]['id']
    ids=[]
    for name,direction,opening in [('Cho vay lần 1','RECEIVABLE','100000000'),('Cho vay lần 2','RECEIVABLE','50000000'),('Đi vay','PAYABLE','80000000'),('Khoản cũ chưa thiết lập',None,None)]:
        act('profile',kind='LOAN',name=name,party=person);loan=store.state()['profiles'][-1]['id'];ids.append(loan)
        if direction:act('loan-setup',profile=loan,direction=direction,opening=opening,effective_date='2026-10-01',source='Synthetic signed opening statement',reason='QA opening')
    rows=[('01/10/2026','Disburse loan 1','D1','20000000','','180000000'),('02/10/2026','Repay loan 1 and interest','R1','','31000000','211000000'),('02/10/2026','Repay loan 2','R2','','10000000','221000000'),('03/10/2026','Pay borrowed principal','P1','5000000','','216000000')]
    raw=statement(rows,200000000,216000000)
    act('import',account=a,filename='p04-synthetic.xlsx',content=base64.b64encode(raw).decode());act('publish',batch=store.state()['imports'][-1]['id'])
    for t,parts in zip(store.state()['transactions'],[[('principal','20000000',ids[0])],[('principal','30000000',ids[0]),('interest','1000000',ids[0])],[('principal','10000000',ids[1])],[('principal','5000000',ids[2])]]):
        act('classify',ids=[t['id']],parts=[dict(category=c,amount=n,profile=p) for c,n,p in parts],reason='Synthetic exact allocation')
    return a,ids

class P04Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name);self.store.require_membership=False;self.a,self.ids=seed(self.store)
    def tearDown(self):self.tmp.cleanup()
    def act(self,action,**data):return self.store.apply(action,data,str(uuid4()))
    def setup_loan(self,**kw):return self.act('loan-setup',**dict(profile=self.ids[0],direction='RECEIVABLE',opening='100000000',effective_date='2026-10-01',source='Evidence',reason='Correct fact',**kw))
    def test_separate_loans_directions_and_interest(self):
        d=self.store.view()['debts'];ls=d['loans']
        self.assertEqual([l['current_principal'] for l in ls],['90000000','40000000','75000000',None])
        self.assertEqual(ls[0]['interest_received'],'1000000');self.assertEqual(ls[0]['interest_paid'],'0')
        self.assertEqual(d['people'][0]['receivable'],'130000000');self.assertEqual(d['people'][0]['payable'],'75000000');self.assertEqual(d['people'][0]['excluded_count'],1)
        self.assertEqual(ls[3]['issues'],['NEEDS_SETUP']);self.assertEqual(len(ls[0]['entries']),2)
    def test_payable_inflow_and_missing_source(self):
        # Projection over a copy verifies both signs without mutating saved sources.
        state=self.store.state();loan=state['profiles'][3]
        self.assertEqual(loan['id'],self.ids[2])
        tx=state['transactions'][0];tx['allocations'][0]['profile']=loan['id'];tx['signed_amount']='20000000'
        debts=self.store.debt_register(state);self.assertEqual(debts['loans'][2]['current_principal'],'95000000')
        tx['sources']=[]
        self.assertIn('MISSING_SOURCE',self.store.debt_register(state)['loans'][2]['issues'])

    def test_explicit_zero_validation_and_audit(self):
        data=dict(profile=self.ids[3],direction='PAYABLE',opening='0',effective_date='2026-10-01',source='Confirmed zero',reason='Setup')
        for change in [{},{'confirm_zero':True,'opening':'0.5'},{'confirm_zero':True,'source':' '},{'confirm_zero':True,'direction':''}]:
            with self.assertRaises(ValidationError):self.act('loan-setup',**(data|change))
        self.act('loan-setup',**data,confirm_zero=True)
        self.assertEqual(self.store.state()['profiles'][-1]['debt_history'][0]['before'],None)
    def test_flags_and_snapshot_immutability(self):
        self.act('approve',account=self.a);snap=copy.deepcopy(self.store.state()['snapshots'][0])
        self.act('loan-setup',profile=self.ids[0],direction='RECEIVABLE',opening='1',effective_date='2026-10-01',source='Correction',reason='Check negative')
        self.assertIn('NEGATIVE_PRINCIPAL',self.store.view()['debts']['loans'][0]['issues'])
        self.assertTrue(self.store.view()['readiness'][0]['financial_changed'])
        self.assertEqual(self.store.state()['snapshots'][0],snap)
        self.act('loan-setup',profile=self.ids[0],direction='RECEIVABLE',opening='90000000',effective_date='2026-10-03',source='After repayments',reason='Move opening')
        l=self.store.view()['debts']['loans'][0];self.assertEqual(l['current_principal'],'90000000');self.assertIn('PRE_OPENING_ALLOCATION',l['issues'])
        restored=P01Store(self.tmp.name+'/restored');restored.restore(self.store.backup(),'restore');self.assertEqual(restored.view()['debts'],self.store.view()['debts'])
