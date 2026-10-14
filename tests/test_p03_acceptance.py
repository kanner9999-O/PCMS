"""P03 readiness and immutable approval checks; isolated synthetic data only."""
import copy
import unittest
import test_p02_acceptance as helpers
from p01_fixtures import statement

class P03Acceptance(unittest.TestCase):
    setUp=helpers.P02Acceptance.setUp
    tearDown=helpers.P02Acceptance.tearDown
    act=helpers.P02Acceptance.act
    account=helpers.P02Acceptance.account
    stage=helpers.P02Acceptance.stage
    publish=helpers.P02Acceptance.publish
    reject=helpers.P02Acceptance.reject
    # Reuse setup/helpers, not the inherited P02 cases in this suite.
    def ready(self):return next(r for r in self.store.view()['readiness'] if r['account']==self.a)
    def approve(self,**data):return self.act('approve',account=self.a,confirm_unknown=True,**data)
    def test_p03_unchanged_approval(self):
        self.publish('01-first.xlsx')
        data={'account':self.a,'confirm_unknown':True}
        self.store.apply('approve',data,'p03-idempotent-approval')
        before=copy.deepcopy(self.store.state())
        self.store.apply('approve',data,'p03-idempotent-approval')
        self.assertEqual(self.store.state(),before)
        snap=copy.deepcopy(self.store.state()['snapshots'][0])
        self.assertEqual(self.ready()['next_action'],'updated')
        self.act('account-edit',account=self.a,name='Display rename')
        self.act('profile',kind='PERSON',name='Unrelated person')
        self.act('begin-adjustment',account=self.a,reason='No financial changes yet')
        self.assertFalse(self.ready()['financial_changed'])
        self.reject('approve',account=self.a,confirm_unknown=True,reason='Different note')
        self.assertEqual(self.store.state()['snapshots'][0],snap)
    def test_p03_amendment(self):
        self.publish('01-first.xlsx');self.approve();snap=copy.deepcopy(self.store.state()['snapshots'][0]);tx=self.store.state()['transactions'][0]
        self.act('begin-adjustment',account=self.a,reason='Classify')
        self.act('classify',ids=[tx['id']],parts=[{'category':'income','amount':'20000000'}],reason='Evidence')
        self.assertTrue(self.ready()['financial_changed']);self.assertTrue(self.ready()['can_approve'])
        self.approve(reason='Classification changed');self.assertEqual(self.store.state()['snapshots'][0],snap)
        self.assertEqual(self.ready()['next_action'],'updated')
        self.act('begin-adjustment',account=self.a,reason='Same allocation new reason')
        self.act('classify',ids=[tx['id']],parts=[{'category':'income','amount':'20000000'}],reason='New nonfinancial note')
        self.assertFalse(self.ready()['financial_changed'])
    def test_p03_gap_confirmation_and_recovery(self):
        self.files['gap.xlsx']=statement([('03/10/2026','Gap deposit','GAP','','100','100000100')],100000000,100000100,start='03/10/2026',end='03/10/2026')
        b=self.stage('gap.xlsx');self.assertEqual(self.ready()['next_action'],'staged')
        self.act('dismiss-import',batch=b,reason='Synthetic recovery')
        self.assertEqual(self.ready()['next_action'],'recover')
        self.act('reopen-import',batch=b);self.act('publish',batch=b)
        self.approve()                                                                  # không còn khoảng ngày phải xác nhận (R108)
        snap=self.store.state()['snapshots'][0]
        self.assertEqual(snap['confirmed_gaps'],[])
        self.assertEqual(snap['report']['opening'],'100000000')
        self.assertEqual(self.ready()['next_action'],'updated')
        self.stage('09-unsupported.xlsx');self.assertEqual(self.ready()['next_action'],'blocked');self.assertFalse(self.ready()['can_approve'])
    def test_p03_financial_projection_and_legacy(self):
        self.publish('01-first.xlsx');self.approve();s=self.store.state();r=self.store.report(s,self.a);old=s['snapshots'][0]
        old.pop('confirmed_gaps');self.assertFalse(self.store.financial_changed(s,r,old))
        for field,value in [('signed_amount','20000001'),('sources',[{'batch':'another','row':8,'sheet':'Statement'}])]:
            changed=copy.deepcopy(r);changed['transactions'][0][field]=value
            self.assertTrue(self.store.financial_changed(s,changed,old))
        profile={'id':'linked','kind':'PERSON','name':'Person','party':None}
        s['profiles'].append(profile);r['transactions'][0]['allocations']=[{'category':'income','amount':'20000000','profile':'linked'}]
        original=self.store.financial_content(r,s['accounts'][0],s['profiles']);profile['name']='Updated person'
        self.assertNotEqual(original,self.store.financial_content(r,s['accounts'][0],s['profiles']))
