import base64
import copy
import tempfile
import unittest
from decimal import Decimal
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError, digest
from p01_fixtures import statement

ROWS=[('02/09/2026','Thanh toan dat B','B-1','200000000','','201000000'),('03/09/2026','Chi chua phan loai','X-1','1000000','','200000000')]

def D_(x):return Decimal(str(x))

class P15Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name);self.store.require_membership=False;self.build()
    def tearDown(self):self.tmp.cleanup()
    def act(self,a,**d):return self.store.apply(a,d,str(uuid4()))
    def err(self,a,**d):
        with self.assertRaises(ValidationError):self.act(a,**d)
    def view(self):return self.store.view()['assets']
    def pid(self,name):return next(p['id'] for p in self.store.state()['profiles'] if p['name']==name)
    def group(self,cur,side,key):return next(g for g in self.view()['currencies'][cur][side]['groups'] if g['key']==key)
    def build(self):
        a=self.act
        a('account',name='QA tài sản',reference='000123',opening='401000000',effective_date='2026-09-01',opening_source='QA')
        acc=self.store.state()['accounts'][0]['id']
        a('import',account=acc,filename='as.xlsx',content=base64.b64encode(statement(ROWS,401000000,200000000,start='01/09/2026',end='30/09/2026')).decode());a('publish',batch=self.store.state()['imports'][-1]['id'])
        a('object-quick-create',kind='PROPERTY',name='Đất A');a('object-quick-create',kind='PROPERTY',name='Đất B');a('object-quick-create',kind='PROPERTY',name='Đất C')
        b=next(t for t in self.store.state()['transactions'] if t['reference']=='B-1')
        a('classify',ids=[b['id']],parts=[dict(category='investment',profile=self.pid('Đất B'))])
        a('realty-valuation',property=self.pid('Đất A'),value='900000000',date='2026-10-01',source='Báo giá')
        a('object-quick-create',kind='LOAN',party_name='Người vay',name='Cho vay 1');a('loan-setup',profile=self.pid('Cho vay 1'),direction='RECEIVABLE',opening='100000000',effective_date='2026-09-01',source='HĐ',reason='QA')
        a('object-quick-create',kind='LOAN',party_name='Ngân hàng',name='Vay NH');a('loan-setup',profile=self.pid('Vay NH'),direction='PAYABLE',opening='300000000',effective_date='2026-09-01',source='HĐ',reason='QA')
        a('object-quick-create',kind='LOAN',party_name='Người lạ',name='Chưa thiết lập')
        a('realty-mortgage',property=self.pid('Đất A'),loan=self.pid('Vay NH'),purpose='Mua nhà')
        a('crypto-place',name='Ví 1',kind='WALLET');a('crypto-place',name='BingX',kind='EXCHANGE');w=next(p['id'] for p in self.store.view()['crypto']['places'] if p['name']=='Ví 1');x=next(p['id'] for p in self.store.view()['crypto']['places'] if p['name']=='BingX')
        for place,t,q,bucket in ((w,'BTC','0.5','HOLDING'),(w,'ETH','10','HOLDING'),(w,'XYZ','1000','HOLDING'),(x,'BTC','5','OPEN_POSITION'),(x,'BTC','0.05','MARGIN_DEBT')):a('crypto-balance',place=place,ticker=t,network='',bucket=bucket,quantity=q,date='2026-10-01',source='s')
        a('crypto-price',ticker='BTC',price='60000',date='2026-10-01',source='s');a('crypto-price',ticker='ETH',price='2500',date='2026-10-01',source='s')
        a('trx-customer',name='Khách A');cust=self.store.view()['trx']['customers'][0]['id']
        a('trx-order',customer=cust,date='2026-10-01',terms=dict(mode='POSTPAID'),evidence='HĐ',lines=[dict(type='ENERGY_MONTHLY',plan='1M',quantity='1000000',amount_usdt='400',service_start='2026-10-01',service_end='2026-10-30')])
        line=self.store.view()['trx']['customers'][0]['orders'][0]['lines'][0]['id']
        a('trx-receipt',customer=cust,date='2026-10-02',currency='USDT',received='100',evidence='e',allocations=[dict(line=line,amount_usdt='100')]);a('trx-receipt',customer=cust,date='2026-10-03',currency='USDT',received='100',evidence='e2')
        a('trx-reward',date='2026-10-04',trx_amount='12.5',note='thưởng')

    def test_two_separate_blocks_totals_and_weights(self):
        v=self.view();vnd,usdt=v['currencies']['VND'],v['currencies']['USDT']
        self.assertEqual((D_(vnd['assets']['total']),D_(vnd['liabilities']['total']),D_(vnd['net']['value'])),(1400000000,300000000,1100000000))
        self.assertEqual({g['key']:g['weight'] for g in vnd['assets']['groups']},{'bank':'14.29','receivable':'7.14','realty':'78.57'})
        self.assertEqual((D_(usdt['assets']['total']),D_(usdt['liabilities']['total']),D_(usdt['net']['value'])),(55300,100,55200))
        self.assertEqual({g['key']:g['weight'] for g in usdt['assets']['groups']},{'crypto':'99.46','trx_receivable':'0.54'})
        blob=str(v).lower();self.assertFalse(any(k in blob for k in ("'fx'","'rate'","exchange_rate","combined","'total_all'")));self.assertEqual(set(v['currencies']),{'VND','USDT'})
        self.assertTrue(any('Không quy đổi' in n for n in v['notes']))

    def test_basis_warnings_and_empty_groups(self):
        v=self.view();realty=self.group('VND','assets','realty')
        self.assertEqual((D_(realty['value']),realty['by_basis']),(1100000000,{'VALUE':'900000000','COST':'200000000'}))
        rows={r['name']:r for r in v['realty_basis']['rows']};self.assertEqual((rows['Đất A']['basis'],rows['Đất B']['basis'],rows['Đất C']['basis']),('VALUE','COST','NONE'))
        self.assertEqual([r['name'] for r in v['realty_basis']['none']],['Đất C'])
        w={x['code']:x for x in v['warnings']};self.assertEqual({k:w[k]['count'] for k in w},{'UNCLASSIFIED':1,'LOAN_ISSUES':1,'UNPRICED_COIN':1,'REALTY_COST_BASIS':1,'REALTY_NO_VALUE':1})
        self.assertEqual(w['REALTY_COST_BASIS']['target'],'realty');self.assertEqual(w['UNCLASSIFIED']['target'],'account')
        self.assertIn('đến ngày 2026-09-30',self.group('VND','assets','bank')['basis'])
        empty=P01Store(self.tmp.name+'/empty').view()['assets']
        self.assertTrue(all(g['value'] is None or not g['has_data'] for g in empty['currencies']['VND']['assets']['groups']+empty['currencies']['USDT']['assets']['groups']))
        self.assertTrue(all(g['weight'] is None for g in empty['currencies']['VND']['assets']['groups']));self.assertFalse(empty['currencies']['VND']['has_data'])

    def test_no_double_count_no_accrual_and_exclusions(self):
        before=copy.deepcopy(self.view());self.assertEqual(D_(self.group('VND','assets','realty')['value']),1100000000)   # thế chấp 300 triệu không trừ BĐS
        self.assertEqual(D_(self.group('VND','liabilities','payable')['value']),300000000)
        self.assertEqual(D_(self.group('VND','assets','receivable')['value']),100000000)                                       # chỉ gốc, khoản chưa thiết lập không vào
        self.assertEqual(D_(self.group('USDT','assets','crypto')['value']),55000)                                              # vị thế 5 và nợ margin không tính, XYZ không giá
        self.assertEqual(D_(self.group('USDT','liabilities','trx_advance')['value']),100)
        self.act('crypto-balance',place=next(p['id'] for p in self.store.view()['crypto']['places'] if p['name']=='BingX'),ticker='BTC',network='',bucket='OPEN_POSITION',quantity='99',date='2026-10-05',source='s')
        self.assertEqual(self.view()['currencies']['USDT'],before['currencies']['USDT'])
        loan=self.pid('Chưa thiết lập');self.act('loan-setup',profile=loan,direction='PAYABLE',opening='50000000',effective_date='2026-09-01',source='HĐ',reason='QA')
        self.assertEqual(D_(self.group('VND','liabilities','payable')['value']),350000000);self.assertFalse(any(x['code']=='LOAN_ISSUES' for x in self.view()['warnings']))
        self.act('crypto-place-archive',place=next(p['id'] for p in self.store.view()['crypto']['places'] if p['name']=='Ví 1'),reason='bán ví')
        self.assertFalse(self.group('USDT','assets','crypto')['has_data']);self.assertIsNone(self.group('USDT','assets','crypto')['value'])

    def test_negative_net_label(self):
        self.act('loan-setup',profile=self.pid('Chưa thiết lập'),direction='PAYABLE',opening='5000000000',effective_date='2026-09-01',source='HĐ',reason='QA')
        net=self.view()['currencies']['VND']['net'];self.assertLess(D_(net['value']),0);self.assertEqual(net['label'],'Nợ lớn hơn tài sản')

    def test_snapshots_immutable_and_deltas(self):
        self.assertIsNone(self.view()['delta']);self.assertEqual(self.view()['snapshots'],[])
        others={k:copy.deepcopy(self.store.state().get(k)) for k in ('accounts','transactions','profiles','snapshots','realty','crypto','trx')}
        self.act('assets-snapshot',note='Cuối tháng');s1=self.view()['snapshots'][0];frozen=copy.deepcopy(s1['data'])
        self.assertEqual({k:self.store.state().get(k) for k in others},others)
        self.assertEqual((s1['note'],s1['delta_vs_previous']),('Cuối tháng',None));d0=self.view()['delta'];self.assertEqual((d0['vs'],d0['VND']['net'],d0['USDT']['net']),(s1['id'],'0','0'))
        self.act('realty-valuation',property=self.pid('Đất A'),value='950000000',date='2026-10-06',source='Mới')
        d1=self.view()['delta'];self.assertEqual((d1['VND']['assets'],d1['VND']['net'],d1['USDT']['net']),('50000000','50000000','0'))
        self.assertEqual(self.view()['snapshots'][0]['data'],frozen);self.assertEqual(digest({k:v for k,v in self.view()['snapshots'][0].items() if k not in ('hash','delta_vs_previous')}),self.view()['snapshots'][0]['hash'])
        self.act('assets-snapshot');top=self.view()['snapshots'][0];self.assertEqual((len(self.view()['snapshots']),top['delta_vs_previous']['VND']['assets']),(2,'50000000'))
        self.assertEqual(self.view()['snapshots'][1]['data'],frozen);self.assertEqual(self.view()['snapshots'][1]['id'],s1['id'])
        self.err('assets-delete',snapshot=s1['id']);self.err('assets-edit',snapshot=s1['id'],note='x')
        restore=P01Store(self.tmp.name+'/restore');restore.restore(self.store.backup(),'restore');self.assertEqual(restore.view()['assets']['snapshots'],self.view()['snapshots']);self.assertIn('assets',self.store.view()['capabilities'])

    def test_view_read_only_and_trx_reward_excluded(self):
        events=self.store.backup()['events'];self.view();self.assertEqual(self.store.backup()['events'],events)
        self.assertNotIn('12.5',str(self.view()['currencies']))
