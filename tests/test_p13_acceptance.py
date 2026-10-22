import base64
import copy
import tempfile
import unittest
from decimal import Decimal
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError
from p01_fixtures import statement

# Ba lần thanh toán Đất A (200 + 150 + 250 triệu), một khoản chi phí, một hoàn chi, một khoản vào Đầu tư (nhận lại), lương.
ROWS=[('02/09/2026','Thanh toan dat A lan 1','D-1','200000000','','800000000'),('15/09/2026','Thanh toan dat A lan 2','D-2','150000000','','650000000'),('20/09/2026','Thanh toan dat A lan 3','D-3','250000000','','400000000'),
      ('21/09/2026','Phi cong chung dat A','D-COST','5000000','','395000000'),('22/09/2026','Hoan phi cong chung','D-REF','','1000000','396000000'),('23/09/2026','Nhan lai coc','D-BACK','','10000000','406000000'),('24/09/2026','Luong','D-SAL','','20000000','426000000')]

def D_(x):return Decimal(str(x))

class P13Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name);self.store.require_membership=False
    def tearDown(self):self.tmp.cleanup()
    def act(self,a,**d):return self.store.apply(a,d,str(uuid4()))
    def err(self,a,**d):
        with self.assertRaises(ValidationError):self.act(a,**d)
    def tx(self,ref):return next(t for t in self.store.state()['transactions'] if t['reference']==ref)
    def view(self):return self.store.view()['realty']
    def prop(self,name):return next(p for p in self.view()['properties'] if p['name']==name)
    def pid(self,name):return next(p['id'] for p in self.store.state()['profiles'] if p['name']==name)
    def load(self):
        self.act('account',name='QA BĐS',reference='000123',opening='1000000000',effective_date='2026-09-01',opening_source='QA')
        self.account=self.store.state()['accounts'][0]['id']
        self.act('import',account=self.account,filename='bds.xlsx',content=base64.b64encode(statement(ROWS,1000000000,426000000,start='01/09/2026',end='30/09/2026')).decode())
        self.act('publish',batch=self.store.state()['imports'][-1]['id'])
    def classify(self,refs,parts):self.act('classify',ids=[self.tx(r)['id'] for r in refs],parts=parts)
    def setup_land(self):
        self.load();self.act('object-quick-create',kind='PROPERTY',name='Đất A');a=self.pid('Đất A')
        self.classify(['D-1','D-2','D-3'],[dict(category='investment',profile=a)]);return a

    # ---- US1 -----------------------------------------------------------
    def test_capital_costs_history_and_empty(self):
        a=self.setup_land();self.act('object-quick-create',kind='PROPERTY',name='Đất B')
        self.classify(['D-COST'],[dict(category='expense',profile=a)]);self.classify(['D-REF'],[dict(category='expense',profile=a)])
        self.classify(['D-BACK'],[dict(category='investment',profile=a)]);self.classify(['D-SAL'],[dict(category='income')])
        p=self.prop('Đất A');self.assertEqual((D_(p['capital']['paid']),D_(p['capital']['received']),D_(p['capital']['net']),p['capital']['transactions']),(600000000,10000000,590000000,6))
        self.assertEqual((D_(p['costs']['spent']),D_(p['costs']['refunded']),D_(p['costs']['net'])),(5000000,1000000,4000000))
        h=self.store.realty_history(dict(property=a));self.assertEqual((h['evidence'],len(h['rows'])),('HAS_DATA',6))
        self.assertEqual(sorted(r['kind'] for r in h['rows']),['CAPITAL']*4+['COST']*2);self.assertEqual({r['status'] for r in h['rows']},{'DRAFT'});self.assertTrue(all(r['sources'] for r in h['rows']))
        b=self.prop('Đất B');self.assertEqual((b['evidence'],b['capital']['transactions']),('EMPTY',0));self.assertIn('Kỳ nguồn',self.store.realty_history(dict(property=self.pid('Đất B')))['source_notice'])
        self.assertEqual(self.view()['unclassified'],0)
        fresh=P01Store(self.tmp.name+'/fresh');fresh.apply('profile',dict(kind='PROPERTY',name='X'),str(uuid4()));self.assertEqual(fresh.view()['realty']['properties'][0]['evidence'],'EMPTY_NO_SOURCE')
        self.err('realty-valuation',property=self.pid('Đất A') if False else 'khong-co',value='1',date='2026-09-01',source='x')

    def test_split_part_counts_only_the_property_share(self):
        self.load();self.act('object-quick-create',kind='PROPERTY',name='Đất A');a=self.pid('Đất A')
        self.classify(['D-1'],[dict(category='investment',profile=a,amount='150000000'),dict(category='expense',amount='50000000')])
        p=self.prop('Đất A');self.assertEqual((D_(p['capital']['paid']),p['capital']['transactions'],D_(p['costs']['spent'])),(150000000,1,0))

    # ---- US2 -----------------------------------------------------------
    def test_valuation_gap_history_and_void(self):
        a=self.setup_land();p=self.prop('Đất A');self.assertEqual((p['gap'],p['valuation']['current']),(None,None))
        self.act('realty-valuation',property=a,value='900000000',date='2026-10-01',source='Báo giá môi giới X')
        p=self.prop('Đất A');self.assertEqual((D_(p['gap']['amount']),D_(p['valuation']['current']['value'])),(300000000,900000000));self.assertIn('không phải lãi/lỗ',p['gap']['label'])
        self.act('realty-valuation',property=a,value='950000000',date='2026-10-05',source='Thẩm định Y');new=self.prop('Đất A')['valuation']['current']
        self.assertEqual(D_(new['value']),950000000);self.assertEqual(len(self.prop('Đất A')['valuation']['history']),2)
        self.act('realty-valuation',property=a,value='880000000',date='2026-09-20',source='Cũ hơn');self.assertEqual(D_(self.prop('Đất A')['valuation']['current']['value']),950000000)  # theo ngày mới nhất
        self.err('realty-valuation-void',valuation=new['id'],reason='')
        self.act('realty-valuation-void',valuation=new['id'],reason='Nhập nhầm')
        p=self.prop('Đất A');self.assertEqual(D_(p['valuation']['current']['value']),900000000);self.assertIn('VOID',[v['status'] for v in p['valuation']['history']])
        self.err('realty-valuation-void',valuation=new['id'],reason='lần hai')
        for bad in (dict(value='0'),dict(value='-5'),dict(value='1.5'),dict(value='abc'),dict(date='bad'),dict(source=''),dict(source='   ')):
            args=dict(property=a,value='100',date='2026-10-01',source='s');args.update(bad);self.err('realty-valuation',**args)
        self.err('realty-valuation',property=self.store.state()['accounts'][0]['id'],value='1',date='2026-10-01',source='x')

    # ---- US3 -----------------------------------------------------------
    def test_mortgage_links_do_not_change_value_or_debts(self):
        a=self.setup_land();self.act('object-quick-create',kind='PROPERTY',name='Đất B');b=self.pid('Đất B')
        self.act('object-quick-create',kind='LOAN',party_name='Ngân hàng 1',name='Vay NH 1');loan=self.pid('Vay NH 1')
        self.act('realty-valuation',property=a,value='900000000',date='2026-10-01',source='s');before=copy.deepcopy(self.prop('Đất A')['gap']);debts=copy.deepcopy(self.store.view()['debts']);income=self.store.view()['categories']['roots'][0]['totals']
        self.err('realty-mortgage',property=a,loan=loan,purpose='');self.err('realty-mortgage',property=a,loan=self.pid('Ngân hàng 1'),purpose='x')   # thiếu mục đích; không phải khoản vay
        self.act('realty-mortgage',property=a,loan=loan,purpose='Mua căn hộ')
        m=self.prop('Đất A')['mortgages'][0];self.assertEqual((m['loan_name'],m['purpose'],m['status'],m['principal']),('Vay NH 1','Mua căn hộ','ACTIVE',None));self.assertIn('NEEDS_SETUP',m['issues'])
        self.assertEqual(self.prop('Đất A')['gap'],before)                                                      # không trừ nợ
        self.assertEqual(self.store.view()['debts']['summary'],debts['summary']);self.assertEqual(self.store.view()['categories']['roots'][0]['totals'],income)
        self.err('realty-mortgage',property=b,loan=loan,purpose='lần hai')                                       # một khoản vay một BĐS
        self.act('realty-mortgage-end',mortgage=m['id'],reason='Tất toán thế chấp')
        self.assertEqual(self.prop('Đất A')['mortgages'][0]['status'],'ENDED');self.err('realty-mortgage-end',mortgage=m['id'],reason='x')
        self.act('realty-mortgage',property=b,loan=loan,purpose='Vay mới');self.assertEqual(self.prop('Đất B')['mortgages'][0]['status'],'ACTIVE')
        self.act('loan-setup',profile=loan,direction='PAYABLE',opening='300000000',effective_date='2026-09-01',source='HĐ',reason='QA')
        self.assertEqual(D_(self.prop('Đất B')['mortgages'][0]['principal']),300000000)                          # dư gốc theo công nợ, chỉ hiển thị

    # ---- US4 -----------------------------------------------------------
    def test_contributions_separate_no_percentages(self):
        a=self.setup_land();self.act('profile',kind='PERSON',name='Anh A');self.act('profile',kind='PERSON',name='Anh B');pa,pb=self.pid('Anh A'),self.pid('Anh B')
        self.act('realty-contribution',property=a,party=pa,amount='300000000',evidence='Biên nhận 1',date='2026-09-02')
        self.act('realty-contribution',property=a,party=pb,amount='200000000',evidence='Biên nhận 2')
        c=self.prop('Đất A')['contributions'];self.assertEqual((len(c['items']),D_(c['total'])),(2,500000000));self.assertEqual({i['party_name'] for i in c['items']},{'Anh A','Anh B'})
        self.assertEqual(D_(self.prop('Đất A')['capital']['paid']),600000000)                                     # vốn của Thạch từ sao kê tách riêng
        blob=str(self.view()).lower();self.assertTrue(all(k not in blob for k in ('percent','ratio',"'share'",'quyền lợi')))
        for bad in (dict(evidence=''),dict(amount='0'),dict(amount='1.5'),dict(party=a),dict(party='khong-co'),dict(date='bad')):
            args=dict(property=a,party=pa,amount='1',evidence='e');args.update(bad);self.err('realty-contribution',**args)
        self.act('realty-contribution-void',contribution=c['items'][0]['id'],reason='Ghi nhầm');c=self.prop('Đất A')['contributions']
        self.assertEqual((len(c['items']),D_(c['total']),c['items'][0]['status']),(2,200000000,'VOID'))
        self.err('realty-contribution-void',contribution=c['items'][0]['id'],reason='x');self.err('realty-contribution-void',contribution=c['items'][1]['id'],reason='')

    # ---- cross-cutting ---------------------------------------------------
    def test_read_only_and_existing_results_unchanged(self):
        a=self.setup_land();report=copy.deepcopy(self.store.report(self.store.state(),self.account)['totals']);events=self.store.backup()['events']
        self.view();self.store.realty_history(dict(property=a));self.assertEqual(self.store.backup()['events'],events)
        self.act('realty-valuation',property=a,value='900000000',date='2026-10-01',source='s')
        self.assertEqual(self.store.report(self.store.state(),self.account)['totals'],report)
        self.act('approve',account=self.account,confirm_unknown=True,reason='Duyệt');h=self.store.realty_history(dict(property=a));self.assertEqual({r['status'] for r in h['rows']},{'APPROVED'})
        restore=P01Store(self.tmp.name+'/restore');restore.restore(self.store.backup(),'restore');self.assertEqual(restore.view()['realty'],self.store.view()['realty'])
        self.assertIn('realty',self.store.view()['capabilities'])
