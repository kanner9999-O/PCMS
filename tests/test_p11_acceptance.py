from pcms.reclassify import RECLASS_GRANT   # quyền nội bộ của "Sửa phân loại" (spec 043); API không gửi được — kiểm ở test_p45
import copy
import tempfile
import unittest
from decimal import Decimal
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError


import base64
from p01_fixtures import statement
from test_p10_acceptance import ROWS


class P11Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name);self.store.require_membership=False
    def tearDown(self):self.tmp.cleanup()
    def act(self,a,**d):return self.store.apply(a,d,str(uuid4()))
    def err(self,a,**d):
        with self.assertRaises(ValidationError):self.act(a,**d)
    def tx(self,ref):return next(t for t in self.store.state()['transactions'] if t['reference']==ref)
    def node(self,name):return next(n for n in self.store.view()['categories']['nodes'] if n['name']==name)
    def load(self):
        self.act('account',name='QA phân loại',reference='000123',opening='10000000',effective_date='2026-09-01',opening_source='QA')
        self.account=self.store.state()['accounts'][0]['id']
        self.act('import',account=self.account,filename='cls.xlsx',content=base64.b64encode(statement(ROWS,10000000,14840000,start='01/09/2026',end='30/09/2026')).decode())
        self.act('publish',batch=self.store.state()['imports'][-1]['id'])

    def profiles(self,kind=None):return [p for p in self.store.state()['profiles'] if kind is None or p['kind']==kind]

    # ---- US1: lý do tùy chọn -------------------------------------------------
    def test_reason_optional_for_classify_and_adjustment(self):
        self.load()
        self.act('classify',_reclass=RECLASS_GRANT,ids=[self.tx('C-1')['id']],parts=[dict(category='expense')])                         # không có khóa reason
        self.act('classify',_reclass=RECLASS_GRANT,ids=[self.tx('C-2')['id'],self.tx('C-3')['id']],parts=[dict(category='expense')],reason='   ')
        self.assertEqual([h['reason'] for h in self.tx('C-1')['classification_history']],[''])
        self.act('classify',_reclass=RECLASS_GRANT,ids=[self.tx('C-4')['id']],parts=[dict(category='income')],reason='Hoàn tiền')
        self.assertEqual(self.tx('C-4')['classification_history'][-1]['reason'],'Hoàn tiền')
        self.err('classify',ids=[self.tx('C-5')['id']],parts=[])                                                  # vẫn cần ít nhất một phần
        self.act('classify',_reclass=RECLASS_GRANT,ids=[self.tx('C-5')['id']],parts=[dict(category='income')])
        self.act('approve',account=self.account,reason='Duyệt 1')
        self.act('begin-adjustment',account=self.account)                                                         # không lý do vẫn mở được
        self.assertTrue(self.store.state()['accounts'][0]['adjustment_open'])
        self.act('object-quick-create',kind='LOAN',party_name='Bình');loan=self.profiles('LOAN')[0]['id']
        self.act('classify',_reclass=RECLASS_GRANT,ids=[self.tx('C-1')['id']],parts=[dict(category='principal',profile=loan)])
        self.err('approve',account=self.account)                                                                  # duyệt bản mới vẫn đòi lý do (R21)
        self.act('approve',account=self.account,reason='Điều chỉnh')

    # ---- US3: tạo nhanh đối tượng --------------------------------------------
    def test_quick_loan_with_new_person_is_atomic_and_usable(self):
        self.load();snap=copy.deepcopy({k:self.store.state()[k] for k in ('transactions','snapshots','accounts')});before=len(self.store.backup()['events'])
        self.act('object-quick-create',kind='LOAN',party_name='Bình')
        people,loans=self.profiles('PERSON'),self.profiles('LOAN')
        self.assertEqual(([p['name'] for p in people],[l['name'] for l in loans],loans[0]['party']==people[0]['id']),(['Bình'],['Khoản Bình'],True))
        self.act('object-quick-create',kind='LOAN',party=people[0]['id'])                                         # người có sẵn, tên mặc định trùng → hậu tố
        self.assertEqual([l['name'] for l in self.profiles('LOAN')],['Khoản Bình','Khoản Bình (2)'])
        self.act('classify',ids=[self.tx('C-1')['id']],parts=[dict(category='principal',profile=loans[0]['id'])])
        self.assertEqual({k:self.store.state()[k] for k in ('snapshots','accounts')},{k:snap[k] for k in ('snapshots','accounts')})
        self.assertEqual(len(self.store.backup()['events']),before+3)                                              # 2 tạo nhanh + 1 phân loại, không sự kiện lạ
        debts=self.store.view()['debts'];loan=next(l for l in debts['loans'] if l['id']==loans[0]['id'])
        self.assertEqual(loan['completion_blocker'],{'code':'NEEDS_SETUP'});self.assertIn('NEEDS_SETUP',loan['issues'])  # chưa thiết lập gốc → cần thiết lập
        self.assertTrue(any(a['action']=='object-quick-create' for a in self.store.state()['audit']))

    def test_quick_property_category_and_duplicates(self):
        self.load()
        self.act('object-quick-create',kind='PROPERTY',name='Đất E');prop=self.profiles('PROPERTY')[0]['id']
        self.err('object-quick-create',kind='PROPERTY',name='  đất e ');self.err('object-quick-create',kind='PROPERTY',name='')
        self.act('classify',ids=[self.tx('C-3')['id']],parts=[dict(category='investment',profile=prop)])
        self.act('object-quick-create',kind='CATEGORY',parent='expense',name='Ăn uống');node=self.node('Ăn uống')['id']
        self.err('object-quick-create',kind='CATEGORY',parent='expense',name='ăn uống');self.err('object-quick-create',kind='CATEGORY',parent='transfer',name='X')
        self.act('classify',ids=[self.tx('C-1')['id']],parts=[dict(category='expense',node=node)])
        self.assertEqual(self.tx('C-1')['allocations'][0]['node'],node)
        self.act('object-quick-create',kind='LOAN',party_name='An',name='Vay An 1');self.err('object-quick-create',kind='LOAN',party_name='Cường',name='vay an 1')
        self.assertEqual([p['name'] for p in self.profiles('PERSON')],['An'])                                       # lỗi sau không để lại người mồ côi
        self.err('object-quick-create',kind='LOAN',party_name='Dũng',name='x'*101);self.err('object-quick-create',kind='LOAN',party_name='An')
        self.assertEqual([p['name'] for p in self.profiles('PERSON')],['An'])
        self.err('object-quick-create',kind='LOAN',party='khong-co');self.err('object-quick-create',kind='NOPE')
        self.act('object-quick-create',kind='PROPERTY',name='Đất F')                                               # đối tượng tồn tại dù không phân loại
        self.assertIn('Đất F',[p['name'] for p in self.profiles('PROPERTY')])

    def test_capability_and_money_untouched(self):
        self.load();self.assertIn('quick-object',self.store.view()['capabilities'])
        before=copy.deepcopy(self.store.state()['transactions']);self.act('object-quick-create',kind='PROPERTY',name='Đất G')
        self.assertEqual(self.store.state()['transactions'],before)
