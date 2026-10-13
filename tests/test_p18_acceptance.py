import base64
import copy
import tempfile
import unittest
from decimal import Decimal
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError
from p01_fixtures import statement

ROWS=[('20/09/2026','Cho Ket vay 5tr','K1','5000000','','995000000'),('25/09/2026','Cho Ket vay 10tr','K2','10000000','','985000000'),('26/09/2026','Ket tra goc','K3','','3000000','988000000'),
      ('27/09/2026','Ket tra lai','K4','','200000','988200000'),('28/09/2026','Tien luong','S1','','20000000','1008200000'),('29/09/2026','Chua dung','X1','10000','','1008190000')]

def D_(x):return Decimal(str(x))

class P18Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name);self.build()
    def tearDown(self):self.tmp.cleanup()
    def act(self,a,**d):return self.store.apply(a,d,str(uuid4()))
    def err(self,*a,**k):
        with self.assertRaises(ValidationError):self.act(*a,**k)
    def tx(self,ref):return next(t for t in self.store.state()['transactions'] if t['reference']==ref)
    def classify(self,refs,parts):self.act('classify',ids=[self.tx(r)['id'] for r in refs],parts=parts)
    def nodes(self):return {n['name']:n for n in self.store.view()['categories']['nodes']}
    def review(self,s=None):return self.store.classification_review(dict(account=self.account),s)
    def group(self,r,name):return next(g for g in r['groups'] if g['name']==name)
    def loans(self):return {l['id']:l for l in self.store.view()['loan_options']}
    def build(self):
        self.act('account',name='QA vay',reference='000123',opening='1000000000',effective_date='2026-09-01',opening_source='QA');self.account=self.store.state()['accounts'][0]['id']
        self.act('import',account=self.account,filename='k.xlsx',content=base64.b64encode(statement(ROWS,1000000000,1008190000,start='01/09/2026',end='30/09/2026')).decode());self.act('publish',batch=self.store.state()['imports'][-1]['id'])
        self.act('object-quick-create',kind='LOAN',party_name='Kết',name='Kết 5tr');self.act('object-quick-create',kind='LOAN',party=next(p['id'] for p in self.store.state()['profiles'] if p['kind']=='PERSON'),name='Kết 10tr')
        pr={p['name']:p['id'] for p in self.store.state()['profiles']};self.person=pr['Kết'];self.l5,self.l10=pr['Kết 5tr'],pr['Kết 10tr']
        for loan,when in ((self.l5,'2026-09-20'),(self.l10,'2026-09-25')):self.act('loan-setup',profile=loan,direction='RECEIVABLE',opening='0',confirm_zero=True,effective_date=when,source='QA',reason='QA')
        self.act('category-create',name='Kết',description='',parent='principal');self.act('category-create',name='Loans',description='',parent='principal')
        self.act('category-create',name='Long debt',description='',parent=self.nodes()['Loans']['id'])
        self.classify(['K1'],[dict(category='principal',profile=self.l5,node=self.nodes()['Kết']['id'])]);self.classify(['K2'],[dict(category='principal',profile=self.l10)])
        self.classify(['K3'],[dict(category='principal',profile=self.l10)]);self.classify(['K4'],[dict(category='interest',profile=self.l10)]);self.classify(['S1'],[dict(category='income')])

    def test_loan_options_labels_and_person_filter(self):
        o=self.loans();a,b=o[self.l5],o[self.l10]
        self.assertEqual((a['party_name'],a['date'],D_(a['gross']),D_(a['current'])),('Kết','2026-09-20',5000000,5000000))
        self.assertEqual((b['date'],D_(b['gross']),D_(b['current'])),('2026-09-25',10000000,7000000))
        self.assertEqual({l['party'] for l in o.values()},{self.person})
        self.act('object-quick-create',kind='LOAN',party_name='Mới',name='Chưa thiết lập');n=next(l for l in self.loans().values() if l['name']=='Chưa thiết lập')
        self.assertFalse(n['setup']);self.assertIsNone(n['gross']);self.assertIsNone(n['current'])

    def test_object_rules_and_optional_child(self):
        self.err('classify',ids=[self.tx('X1')['id']],parts=[dict(category='income',profile=self.l5)])
        self.err('classify',ids=[self.tx('X1')['id']],parts=[dict(category='expense',profile=self.person)])
        self.err('classify',ids=[self.tx('K4')['id']],parts=[dict(category='transfer_pending',profile=self.l5)])
        self.classify(['X1'],[dict(category='expense',profile=self.l5)])                      # chi hộ khoản vay: hành vi cũ vẫn được
        self.classify(['K1'],[dict(category='principal',profile=self.l5)])                    # danh mục con tùy chọn

    def test_review_one_group_per_object_and_child_is_label(self):
        r=self.review();g=self.group(r,'Gốc vay · Kết 5tr');self.assertEqual(g['rows'][0]['label'],'Gốc vay › Kết')
        self.assertFalse(any(x['name']=='Gốc vay › Kết · Kết 5tr' for x in r['groups']))
        self.classify(['K2'],[dict(category='principal',profile=self.l5,node=self.nodes()['Kết']['id'])])
        r=self.review();g=self.group(r,'Gốc vay · Kết 5tr');self.assertEqual(g['transactions'],2);self.assertEqual(sorted(x['label'] for x in g['rows']),['Gốc vay › Kết','Gốc vay › Kết'])
        self.assertTrue(r['reconciled'])
        self.assertIn('Lãi vay · Kết 10tr',[x['name'] for x in r['groups']])

    def test_regroup_moves_whole_loan_without_changing_debt(self):
        before=self.store.view();debts=copy.deepcopy(before['debts']);total0=D_(before['categories']['roots'][2]['totals']['out'])
        self.act('loan-regroup',profile=self.l10,node=self.nodes()['Long debt']['id'],effective_date='2026-10-01',reason='Thành nợ dài hạn')
        v=self.store.view();self.assertEqual(v['debts'],debts)
        ld=self.nodes()['Long debt'];self.assertEqual((D_(ld['totals']['out']),D_(ld['totals']['in'])),(10000000,3200000))
        loans=self.nodes()['Loans'];self.assertEqual((D_(loans['totals']['out']),D_(loans['totals']['in'])),(10000000,3200000))
        root=next(r for r in v['categories']['roots'] if r['key']=='principal');self.assertEqual(D_(root['totals']['out']),total0)       # gốc hệ thống vẫn gộp mọi con
        r=self.review();g=self.group(r,'Gốc vay › Loans › Long debt · Kết 10tr');self.assertEqual(g['transactions'],3);self.assertTrue(r['reconciled'])
        self.assertNotIn('Lãi vay · Kết 10tr',[x['name'] for x in r['groups']]);self.assertEqual(sorted(x['label'] for x in g['rows']),['Gốc vay','Gốc vay','Lãi vay'])   # lãi đi cùng khoản vay (R96)
        hist=self.store.category_history(dict(category=self.nodes()['Long debt']['id']));self.assertEqual({x['reference'] for x in hist['rows']},{'K2','K3','K4'})
        h=self.loans()[self.l10]['history'];self.assertEqual((len(h),h[0]['to'],h[0]['reason']),(1,ld['id'],'Thành nợ dài hạn'))
        self.act('loan-regroup',profile=self.l10,node='principal',effective_date='2026-10-02',reason='Quay lại');self.assertEqual(len(self.loans()[self.l10]['history']),2)
        self.assertEqual((D_(self.nodes()['Long debt']['totals']['out']),D_(self.nodes()['Long debt']['totals']['in'])),(0,0))
        self.assertIn('Lãi vay · Kết 10tr',[x['name'] for x in self.review()['groups']])                                       # về Gốc vay: lãi trở lại Lãi vay

    def test_regroup_validation_and_snapshot_untouched(self):
        ld=self.nodes()['Long debt']['id'];good=dict(profile=self.l10,node=ld,effective_date='2026-10-01',reason='x')
        for bad in (dict(good,profile=self.person),dict(good,node=self.nodes()['Ăn']['id'] if 'Ăn' in self.nodes() else 'nope'),dict(good,reason=''),dict(good,effective_date=''),dict(good,effective_date='2026-13-40')):self.err('loan-regroup',**bad)
        self.act('category-create',name='Thu thêm',description='',parent='income');self.err('loan-regroup',**dict(good,node=self.nodes()['Thu thêm']['id']))
        self.err('loan-regroup',**dict(good,node='principal'))                                                                  # đã ở Gốc vay
        self.act('category-archive',category=self.nodes()['Kết']['id'],reason='Dọn');self.err('loan-regroup',**dict(good,node=self.nodes()['Kết']['id']))
        snaps=len(self.store.state()['snapshots']);self.act('approve',account=self.account,confirm_unknown=True,confirm_gaps=True,reason='QA') if self.store.view()['readiness'][0]['can_approve'] else None
        frozen=copy.deepcopy(self.store.state()['snapshots']);self.assertTrue(frozen,'cần có bản duyệt để kiểm tra bất biến');self.act('loan-regroup',**good);self.assertEqual(self.store.state()['snapshots'],frozen)

    def test_archive_blocked_while_loan_attached_and_delete_rules(self):
        ld=self.nodes()['Long debt'];self.act('loan-regroup',profile=self.l10,node=ld['id'],effective_date='2026-10-01',reason='x')
        self.err('category-archive',category=ld['id'],reason='không được')
        self.err('category-delete',category=ld['id'],reason='không được')
        self.err('category-delete',category=self.nodes()['Loans']['id'],reason='còn con')
        self.err('category-delete',category=self.nodes()['Kết']['id'],reason='đã dùng')            # K1 từng phân loại vào Kết
        self.classify(['K1'],[dict(category='principal',profile=self.l5)])
        self.err('category-delete',category=self.nodes()['Kết']['id'],reason='đã dùng rồi bỏ')    # đã từng dùng, vẫn chỉ lưu trữ
        self.act('category-create',name='Thử',description='',parent='expense');n=self.nodes()['Thử'];self.assertTrue(n['deletable'])
        self.err('category-delete',category=n['id'],reason='')
        self.act('category-delete',category=n['id'],reason='Tạo nhầm');self.assertNotIn('Thử',self.nodes());d=self.store.view()['categories']['deleted'];self.assertEqual((d[-1]['name'],d[-1]['reason']),('Thử','Tạo nhầm'))
        self.err('category-delete',category='expense',reason='gốc hệ thống')
        self.assertFalse(self.nodes()['Kết']['deletable']);self.assertFalse(self.nodes()['Long debt']['deletable'])

    def test_read_only_and_backup(self):
        n=len(self.store.events());self.store.view();self.review();self.store.loan_options(self.store.state());self.assertEqual(len(self.store.events()),n)
        self.act('loan-regroup',profile=self.l5,node=self.nodes()['Loans']['id'],effective_date='2026-10-01',reason='x')
        b=self.store.backup();other=P01Store(tempfile.mkdtemp());other.restore(b,str(uuid4()))
        self.assertEqual(next(l for l in other.view()['loan_options'] if l['id']==self.l5)['group'],self.nodes()['Loans']['id'])

if __name__=='__main__':unittest.main()
