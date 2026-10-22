import copy
import tempfile
import unittest
from decimal import Decimal
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError
import base64
from test_p07_acceptance import seed
from p01_fixtures import statement


def D_(x):return Decimal(str(x))

def month_lines(n=3,amount='100'):
    return [dict(type='ENERGY_MONTHLY',plan='1M Energy',quantity='1000000',amount_usdt=amount,service_start=f'2026-0{7+i}-01',service_end=f'2026-0{7+i}-30') for i in range(n)]

class P09Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name);self.store.require_membership=False;self.loans=seed(self.store)
        self.act('trx-customer',name='Khách A',note='QA');self.customer=self.trx()['customers'][0]['id']
    def tearDown(self):self.tmp.cleanup()
    def act(self,a,**d):return self.store.apply(a,d,str(uuid4()))
    def trx(self):return self.store.view()['trx']
    def bank_income(self):
        s=self.store.state();account=s['accounts'][0]['id']
        rows=[('02/10/2026','Khach TRX tra tien','TRX-IN-1','','2500000','215000000')]
        self.act('import',account=account,filename='trx-qa.xlsx',content=base64.b64encode(statement(rows,212500000,215000000,start='01/10/2026',end='02/10/2026')).decode())
        self.act('publish',batch=self.store.state()['imports'][-1]['id'])
        tx=next(x for x in self.store.state()['transactions'] if x['reference']=='TRX-IN-1')
        self.act('classify',ids=[tx['id']],parts=[dict(category='income')],reason='QA')
        return next(x for x in self.store.state()['transactions'] if x['reference']=='TRX-IN-1')
    def order(self,lines=None,due=None,mode='POSTPAID',date='2026-10-01'):
        self.act('trx-order',customer=self.customer,date=date,terms=dict(mode=mode,due_date=due),evidence='Thỏa thuận QA',lines=lines or month_lines())
        return self.trx()['customers'][0]['orders'][-1]
    def err(self,a,**d):
        with self.assertRaises(ValidationError):self.act(a,**d)

    def test_orders_balance_and_validation(self):
        o=self.order();c=self.trx()['customers'][0]
        self.assertEqual((D_(c['billed']),D_(c['outstanding']),c['overdue']),(300,300,False))   # không có hạn → không quá hạn
        self.err('trx-customer',name='khách a')
        self.err('trx-order',customer=self.customer,date='2026-10-01',terms=dict(mode='POSTPAID'),evidence='x',lines=[dict(type='ENERGY_MONTHLY',plan='P',quantity='1',amount_usdt='1',service_start='2026-10-01')])
        self.err('trx-order',customer=self.customer,date='2026-10-01',terms=dict(mode='POSTPAID'),evidence='',lines=month_lines(1))
        self.err('trx-order',customer=self.customer,date='2026-10-01',terms=dict(mode='X'),evidence='x',lines=month_lines(1))
        self.err('trx-order',customer=self.customer,date='2026-10-01',terms=dict(mode='PREPAID'),evidence='x',lines=[dict(type='ENERGY_ONCE',quantity='0',amount_usdt='5')])
        self.err('trx-nonsense')
        self.assertEqual(len(o['lines']),3)

    def test_overdue_only_with_due_date(self):
        self.order(due='2026-09-01');c=self.trx()['customers'][0];self.assertTrue(c['overdue'])
        self.act('trx-order-void',order=c['orders'][0]['id'],reason='QA');self.assertFalse(self.trx()['customers'][0]['overdue'])

    def test_receipts_allocation_and_vnd(self):
        o=self.order();l=[x['id'] for x in o['lines']]
        self.act('trx-receipt',customer=self.customer,date='2026-10-05',currency='USDT',received='200',evidence='Ví QA',allocations=[dict(line=l[0],amount_usdt='100'),dict(line=l[1],amount_usdt='100')])
        c=self.trx()['customers'][0];self.assertEqual((D_(c['outstanding']),D_(c['unallocated'])),(100,0))
        self.assertEqual([x['status'] for x in c['orders'][0]['lines']],['PAID','PAID','UNPAID'])
        self.err('trx-allocate',receipt=c['receipts'][0]['id'],allocations=[dict(line=l[2],amount_usdt='1')])      # hết USDT
        self.act('trx-receipt',customer=self.customer,date='2026-10-06',currency='VND',received='2500000',rate='25000',evidence='Ngân hàng QA')
        r=self.trx()['customers'][0]['receipts'][-1];self.assertEqual(D_(r['usdt_equivalent']),100)
        self.assertEqual(D_(self.trx()['customers'][0]['unallocated']),100)
        self.err('trx-allocate',receipt=r['id'],allocations=[dict(line=l[2],amount_usdt='100.000001')])               # vượt dòng/khoản thu
        self.act('trx-allocate',receipt=r['id'],allocations=[dict(line=l[2],amount_usdt='100')])
        c=self.trx()['customers'][0];self.assertEqual((D_(c['outstanding']),D_(c['unallocated'])),(0,0))
        self.act('trx-receipt',customer=self.customer,date='2026-10-07',currency='VND',received='2600000',rate='26000',evidence='Lần 2')
        again=self.trx()['customers'][0]['receipts'];self.assertEqual((again[1]['rate'],again[-1]['rate']),('25000','26000'))   # tỷ giá lần trước không đổi
        self.assertEqual(D_(again[1]['usdt_equivalent']),100)
        self.err('trx-receipt',customer=self.customer,date='2026-10-07',currency='VND',received='1000',evidence='x')   # thiếu tỷ giá

    def test_loan_allocated_transaction_cannot_be_linked(self):
        loan_tx=next(t for t in self.store.state()['transactions'] if D_(t['signed_amount'])>0 and any(a.get('profile') for a in t['allocations']))
        self.err('trx-receipt',customer=self.customer,date='2026-10-01',currency='VND',received='1',rate='25000',evidence='x',bank_transaction=loan_tx['id'])

    def test_bank_transaction_link_once(self):
        incoming=self.bank_income()
        amount=D_(incoming['signed_amount']);before=copy.deepcopy(self.store.state()['transactions'])
        self.act('trx-receipt',customer=self.customer,date='2026-10-01',currency='VND',received=str(int(amount)),rate='25000',evidence='Gắn QA',bank_transaction=incoming['id'])
        self.err('trx-receipt',customer=self.customer,date='2026-10-01',currency='VND',received='1',rate='25000',evidence='trùng',bank_transaction=incoming['id'])
        self.err('trx-receipt',customer=self.customer,date='2026-10-01',currency='USDT',received='1',evidence='x',bank_transaction=incoming['id'])
        outgoing=next(t for t in self.store.state()['transactions'] if D_(t['signed_amount'])<0)
        self.err('trx-receipt',customer=self.customer,date='2026-10-01',currency='VND',received='1',rate='25000',evidence='x',bank_transaction=outgoing['id'])
        rid=self.trx()['customers'][0]['receipts'][0]['id'];self.act('trx-receipt-void',receipt=rid,reason='Gắn nhầm')
        self.act('trx-receipt',customer=self.customer,date='2026-10-01',currency='VND',received=str(int(amount)),rate='25000',evidence='Gắn lại',bank_transaction=incoming['id'])
        self.assertEqual(self.store.state()['transactions'],before)       # sổ ngân hàng không đổi

    def test_void_rules_history_and_report(self):
        o=self.order(lines=[dict(type='ENERGY_ONCE',quantity='5000000',amount_usdt='40'),dict(type='TRX_SALE',quantity='1000',amount_usdt='60')])
        a,b=[x['id'] for x in o['lines']]
        self.act('trx-receipt',customer=self.customer,date='2026-10-05',currency='USDT',received='120',evidence='QA',allocations=[dict(line=a,amount_usdt='40'),dict(line=b,amount_usdt='60')])
        self.act('trx-receipt',customer=self.customer,date='2026-10-06',currency='VND',received='1250000',rate='25000',evidence='QA')
        self.act('trx-reward',date='2026-10-03',trx_amount='12.5',note='Thưởng QA')
        r=self.store.trx_report(dict(date='2026-10-15',period='month'))
        self.assertEqual((D_(r['received_usdt']),D_(r['received_vnd']),D_(r['by_type']['ENERGY_ONCE']),D_(r['by_type']['TRX_SALE']),D_(r['by_type']['UNALLOCATED'])),(170,1250000,40,60,70))
        self.assertEqual((D_(r['trx_sold']),D_(r['trx_rewards'])),(1000,Decimal('12.5')))
        self.assertFalse({'profit','loss','revenue'}&set(r))
        self.err('trx-order-void',order=o['id'],reason='còn phân bổ')
        c=self.trx()['customers'][0]
        for x in c['receipts']:self.act('trx-receipt-void',receipt=x['id'],reason='QA')
        self.act('trx-order-void',order=o['id'],reason='QA')
        r2=self.store.trx_report(dict(date='2026-10-15',period='month'));self.assertEqual((D_(r2['received_usdt']),r2['entries']),(0,[]))
        c=self.trx()['customers'][0];self.assertEqual((len(c['orders']),len(c['receipts']),c['orders'][0]['status']),(1,2,'VOID'))
        self.assertEqual(D_(self.store.trx_report(dict(date='2026-10-15',period='week'))['received_usdt']),0)

    def test_other_domains_untouched_and_backup(self):
        keys=('accounts','transactions','profiles','snapshots','interest_statements')
        before={k:copy.deepcopy(self.store.state().get(k)) for k in keys}
        self.order();after=self.store.state()
        self.assertEqual({k:after.get(k) for k in keys},before)
        restore=P01Store(self.tmp.name+'/restore');restore.restore(self.store.backup(),'restore');self.assertEqual(restore.view()['trx'],self.store.view()['trx'])
