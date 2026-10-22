import base64
import copy
import tempfile
import unittest
from decimal import Decimal
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError
from p01_fixtures import statement

COM=[('02/09/2026','Tra tien com 3 nguoi','R-OUT','1000000','','9000000'),('03/09/2026','Ban A tra lai','R-IN-A','','300000','9300000'),('03/09/2026','Ban B tra lai','R-IN-B','','300000','9600000'),('05/09/2026','Luong','R-SAL','','5000000','14600000')]

def D_(x):return Decimal(str(x))

class P12Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name);self.store.require_membership=False
    def tearDown(self):self.tmp.cleanup()
    def act(self,a,**d):return self.store.apply(a,d,str(uuid4()))
    def err(self,a,**d):
        with self.assertRaises(ValidationError):self.act(a,**d)
    def tx(self,ref):return next(t for t in self.store.state()['transactions'] if t['reference']==ref)
    def cats(self):return self.store.view()['categories']
    def root(self,key):return next(r for r in self.cats()['roots'] if r['key']==key)
    def load(self,rows=COM,closing=14600000):
        self.act('account',name='QA hoàn chi',reference='000123',opening='10000000',effective_date='2026-09-01',opening_source='QA')
        self.account=self.store.state()['accounts'][0]['id']
        self.act('import',account=self.account,filename='r.xlsx',content=base64.b64encode(statement(rows,10000000,closing,start='01/09/2026',end='30/09/2026')).decode())
        self.act('publish',batch=self.store.state()['imports'][-1]['id'])
    def classify(self,refs,parts,reason=''):
        self.act('classify',ids=[self.tx(r)['id'] for r in refs],parts=parts,reason=reason)

    def test_incoming_can_be_refund_but_income_for_outgoing_stays_blocked(self):
        self.load()
        self.err('classify',ids=[self.tx('R-OUT')['id']],parts=[dict(category='income')],reason='x')       # Thu nhập cho tiền ra vẫn bị chặn
        self.classify(['R-OUT'],[dict(category='expense')])
        self.classify(['R-IN-A','R-IN-B'],[dict(category='expense')])                                       # hàng loạt hoàn chi
        self.classify(['R-SAL'],[dict(category='income')])                                                  # Thu nhập cho tiền vào vẫn được
        t=self.store.report(self.store.state(),self.account)['totals']
        self.assertEqual((D_(t['expense_out']),D_(t['expense_in']),D_(t['income_in']),'income_out' in t),(1000000,600000,5000000,False))
        self.assertEqual(self.tx('R-IN-A')['allocations'][0]['amount'],'300000')                            # tiền nguồn không đổi

    def test_split_node_and_totals_chi_hoan_chi_ro(self):
        self.load();self.act('category-create',name='Ăn uống',description='',parent='expense');eat=next(n['id'] for n in self.cats()['nodes'] if n['name']=='Ăn uống')
        self.classify(['R-OUT'],[dict(category='expense',node=eat)])
        self.classify(['R-IN-A'],[dict(category='expense',node=eat,amount='200000'),dict(category='income',amount='100000')])   # tách: 200k hoàn chi + 100k thu nhập
        self.classify(['R-IN-B'],[dict(category='expense',node=eat)])
        ex=self.root('expense')['totals'];node=next(n for n in self.cats()['nodes'] if n['id']==eat)['totals']
        self.assertEqual((D_(ex['out']),D_(ex['in']),D_(ex['net_spend']),ex['transactions']),(1000000,500000,500000,3))
        self.assertEqual((D_(node['out']),D_(node['in']),D_(node['net_spend'])),(1000000,500000,500000))
        self.assertEqual(D_(self.root('income')['totals']['in']),100000);self.assertNotIn('net_spend',self.root('income')['totals'])
        h=self.store.category_history(dict(category='expense'));self.assertEqual((h['root'],D_(h['totals']['net_spend']),len(h['rows'])),('expense',500000,3))
        self.assertEqual(sorted(r['direction'] for r in h['rows']),['IN','IN','OUT'])
        self.assertEqual(D_(self.store.category_history(dict(category=eat))['totals']['net_spend']),500000)
        self.assertNotIn('net_spend',self.store.category_history(dict(category='income'))['totals'])

    def test_net_spend_negative_when_refund_exceeds_spend(self):
        self.load();self.classify(['R-OUT'],[dict(category='expense',amount='100000'),dict(category='transfer_pending',amount='900000')])
        self.classify(['R-IN-A','R-IN-B'],[dict(category='expense')])
        ex=self.root('expense')['totals'];self.assertEqual((D_(ex['out']),D_(ex['in']),D_(ex['net_spend'])),(100000,600000,-500000))

    def test_old_data_unchanged_and_adjustment_path(self):
        self.load();self.classify(['R-OUT'],[dict(category='expense')]);self.classify(['R-IN-A','R-IN-B'],[dict(category='income')]);self.classify(['R-SAL'],[dict(category='income')])
        self.act('approve',account=self.account,reason='Duyệt 1');s1=copy.deepcopy(self.store.state()['snapshots'][0])
        self.assertEqual(D_(s1['report']['totals']['income_in']),5600000)                                    # bản cũ: hoàn tiền đang là thu nhập
        self.err('classify',ids=[self.tx('R-IN-A')['id']],parts=[dict(category='expense')],reason='')        # đã duyệt: cần mở điều chỉnh
        self.act('begin-adjustment',account=self.account)
        self.classify(['R-IN-A','R-IN-B'],[dict(category='expense')])
        self.assertEqual(self.store.state()['snapshots'][0],s1)                                              # snapshot cũ nguyên vẹn
        self.err('approve',account=self.account)                                                              # duyệt bản mới vẫn đòi lý do (R21)
        self.act('approve',account=self.account,reason='Hoàn tiền là hoàn chi');s2=self.store.state()['snapshots'][-1]
        t=s2['report']['totals'];self.assertEqual((D_(t['expense_in']),D_(t['income_in'])),(600000,5000000))
        self.assertEqual(self.store.state()['snapshots'][0]['hash'],s1['hash'])

    def test_loan_cash_report_counts_refund_with_loan_profile(self):
        self.load();self.act('profile',kind='PERSON',name='Bình');person=self.store.state()['profiles'][-1]['id']
        self.act('profile',kind='LOAN',name='Khoản Bình',party=person);loan=self.store.state()['profiles'][-1]['id']
        self.act('loan-setup',profile=loan,direction='RECEIVABLE',opening='100000000',effective_date='2026-09-01',source='QA',reason='QA')
        self.classify(['R-OUT'],[dict(category='expense',profile=loan)]);self.classify(['R-IN-A'],[dict(category='expense',profile=loan)])
        r=self.store.loan_cash_report(dict(date='2026-09-15',period='month'))
        self.assertEqual((D_(r['totals']['tagged_expenses']),D_(r['totals']['expense_refunds']),D_(r['cash_difference'])),(1000000,300000,-700000))

    def test_read_only_and_other_roots_unchanged(self):
        self.load();self.classify(['R-OUT'],[dict(category='expense')]);before=self.store.backup()['events']
        self.cats();self.store.category_history(dict(category='expense'));self.assertEqual(self.store.backup()['events'],before)
        for key in ('principal','interest','investment','transfer','unknown'):self.assertNotIn('net_spend',self.root(key)['totals'])
