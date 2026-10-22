import tempfile
import unittest
from uuid import uuid4
from decimal import Decimal
from pcms.p01 import P01Store
from test_p07_acceptance import seed


class P08Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name);self.store.require_membership=False;self.loans=seed(self.store)
    def tearDown(self):self.tmp.cleanup()
    def act(self,a,**d):return self.store.apply(a,d,str(uuid4()))
    def debts(self):return self.store.view()['debts']

    def test_summary_matches_people_and_keeps_person_rows(self):
        db=self.debts();sm=db['summary']
        self.assertEqual(Decimal(sm['receivable_total']),Decimal('100000000'));self.assertEqual(Decimal(sm['payable_total']),0)
        self.assertEqual(sm['people'],3);self.assertEqual(sm['loans_by_status'],{'ACTIVE':2,'COMPLETED':1,'NEEDS_REVIEW':0})
        self.assertEqual((sm['needs_setup'],sm['excluded']),(0,0))
        self.assertEqual(sum(Decimal(p['receivable']) for p in db['people']),Decimal(sm['receivable_total']))
        self.assertEqual(sum(Decimal(p['payable']) for p in db['people']),Decimal(sm['payable_total']))
        self.assertEqual([(p['name'][:3],p['receivable'],p['payable']) for p in db['people']],[('An ','0','0'),('Bìn','100000000','0'),('Chi','0','0')])
        self.assertEqual(sum(sm['loans_by_status'].values()),len(db['loans']))

    def test_unset_loan_counted_not_summed(self):
        self.act('profile',kind='LOAN',name='Khoản chưa thiết lập',party=self.store.state()['profiles'][0]['id'])
        sm=self.debts()['summary'];self.assertEqual(sm['needs_setup'],1)
        self.assertEqual(Decimal(sm['receivable_total']),Decimal('100000000'))
        loan=next(l for l in self.debts()['loans'] if l['name']=='Khoản chưa thiết lập')
        self.assertEqual(loan['completion_blocker'],{'code':'NEEDS_SETUP'})

    def test_completion_blocker_states(self):
        by={l['name'][6:8]:l for l in self.debts()['loans']}
        self.assertIsNone(by['An']['completion_blocker'])
        self.assertIsNone(by['Bì']['completion_blocker'])
        self.assertEqual(by['Ch']['completion_blocker']['code'],'BLOCKED');self.assertTrue(by['Ch']['completion_blocker']['message'])
        self.act('loan-reopen',profile=self.loans[0],reason='QA mở lại để kiểm gợi ý')
        an=next(l for l in self.debts()['loans'] if l['id']==self.loans[0])
        self.assertEqual(an['completion_status'],'ACTIVE');self.assertEqual(an['completion_blocker'],{'code':'READY'})

    def test_read_only(self):
        before=self.store.backup()['events'];state=self.store.state()
        self.debts();self.debts()
        self.assertEqual(self.store.backup()['events'],before);self.assertEqual(self.store.state(),state)
        self.assertEqual(self.store.completion_status(state,self.loans[0]),'COMPLETED')

    def test_cash_report_unchanged(self):
        r=self.store.loan_cash_report(dict(date='2026-09-15',period='month'))
        self.assertEqual((Decimal(r['totals']['interest_received']),Decimal(r['totals']['tagged_expenses']),Decimal(r['cash_difference'])),(Decimal('2700000'),Decimal('200000'),Decimal('2500000')))
        self.assertEqual(Decimal(r['totals']['principal_recovered']),Decimal('200000000'))
