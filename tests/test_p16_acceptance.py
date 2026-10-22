import base64
import copy
import tempfile
import unittest
from decimal import Decimal
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError
from p01_fixtures import statement

ROWS=[('02/09/2026','Tra com','R-OUT','1000000','','9000000'),('03/09/2026','Ban A tra lai','R-IN-A','','300000','9300000'),('05/10/2026','Mua hang','K-OUT','400000','','8900000'),
      ('06/10/2026','Ban B tra lai','R-IN-B','','300000','9200000'),('07/10/2026','Luong','R-SAL','','5000000','14200000'),('08/10/2026','Chua phan loai','U-1','20000','','14180000')]

def D_(x):return Decimal(str(x))

class P16Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name);self.store.require_membership=False;self.load()
    def tearDown(self):self.tmp.cleanup()
    def act(self,a,**d):return self.store.apply(a,d,str(uuid4()))
    def err(self,a,**d):
        with self.assertRaises(ValidationError):self.act(a,**d)
    def cats(self):return self.store.view()['categories']
    def node(self,name):return next(n for n in self.cats()['nodes'] if n['name']==name)
    def root(self,key):return next(r for r in self.cats()['roots'] if r['key']==key)
    def tx(self,ref):return next(t for t in self.store.state()['transactions'] if t['reference']==ref)
    def load(self):
        self.act('account',name='QA danh mục 2',reference='000123',opening='10000000',effective_date='2026-09-01',opening_source='QA');self.account=self.store.state()['accounts'][0]['id']
        self.act('import',account=self.account,filename='c2.xlsx',content=base64.b64encode(statement(ROWS,10000000,14180000,start='01/09/2026',end='31/10/2026')).decode());self.act('publish',batch=self.store.state()['imports'][-1]['id'])
    def classify(self,refs,parts):self.act('classify',ids=[self.tx(r)['id'] for r in refs],parts=parts)
    def biz(self):
        self.act('category-create',name='Kinh doanh nhỏ',type='expense');biz=self.node('Kinh doanh nhỏ')['id']
        self.act('category-create',name='Nhập hàng',description='',parent=biz);return biz,self.node('Nhập hàng')['id']

    # ---- US1 -----------------------------------------------------------
    def test_custom_root_lifecycle_and_names(self):
        biz,goods=self.biz();n=self.node('Kinh doanh nhỏ');self.assertEqual((n['parent'],n['root'],n['depth'],n['path']),(None,'expense',1,'Kinh doanh nhỏ'));self.assertEqual((self.node('Nhập hàng')['depth'],self.node('Nhập hàng')['path']),(2,'Kinh doanh nhỏ › Nhập hàng'))
        for bad in (dict(name='chi tiêu',type='expense'),dict(name='  CHI TIÊU ',type='income'),dict(name='kinh doanh NHỎ',type='income'),dict(name='X',type='principal'),dict(name='X',type='unknown'),dict(name='',type='expense'),dict(name='a'*101,type='expense')):self.err('category-create',**bad)
        self.act('category-create',name='Chi tieu',type='expense')                     # khác dấu tiếng Việt = tên khác
        a=self.node('Nhập hàng')['id'];self.act('category-create',name='Cấp 3',description='',parent=a);c3=self.node('Cấp 3')['id'];self.act('category-create',name='Cấp 4',description='',parent=c3);self.err('category-create',name='Cấp 5',description='',parent=self.node('Cấp 4')['id'])
        self.err('category-edit',category=biz,type='income');self.err('category-edit',category=biz,parent='income')                    # loại/cha gốc tự tạo không đổi
        self.act('category-edit',category=biz,name='Kinh doanh',reason='đổi');self.assertEqual(self.node('Kinh doanh')['name'],'Kinh doanh');self.assertEqual(self.node('Nhập hàng')['path'],'Kinh doanh › Nhập hàng')
        self.err('category-edit',category=biz,name='Chi tiêu')
        self.err('category-archive',category=biz,reason='x')                          # còn con hoạt động
        for nid in (self.node('Cấp 4')['id'],c3,goods):self.act('category-archive',category=nid,reason='dọn')
        self.act('category-archive',category=biz,reason='không dùng');self.err('category-create',name='kinh doanh',type='income')       # trùng gốc đã lưu trữ
        self.err('category-restore',category=goods);self.act('category-restore',category=biz);self.act('category-restore',category=goods)
        self.assertEqual(self.root('expense')['totals']['transactions'],0)

    def test_rules_by_type_and_separate_totals_report_unchanged(self):
        biz,goods=self.biz();self.act('category-create',name='Thu phụ',type='income');inc=self.node('Thu phụ')['id']
        self.act('category-create',name='Đầu tư nhỏ',type='investment');inv=self.node('Đầu tư nhỏ')['id'];self.act('object-quick-create',kind='PROPERTY',name='Đất A');prop=next(p['id'] for p in self.store.state()['profiles'] if p['name']=='Đất A')
        self.classify(['K-OUT'],[dict(category='expense',node=goods)]);self.classify(['R-IN-B'],[dict(category='expense',node=goods)])            # chi và hoàn chi dưới gốc nhóm chi
        ex=self.root('expense')['totals'];kd=self.node('Kinh doanh nhỏ')['totals'];ng=self.node('Nhập hàng')['totals']
        self.assertEqual((D_(kd['out']),D_(kd['in']),D_(kd['net_spend']),kd['transactions']),(400000,300000,100000,2));self.assertEqual((D_(ng['out']),D_(ng['in'])),(400000,300000))
        self.assertEqual((D_(ex['out']),D_(ex['in']),ex['transactions']),(0,0,0))                                                                    # gốc hệ thống không bị cộng
        rep=self.store.report(self.store.state(),self.account)['totals'];self.assertEqual((D_(rep['expense_out']),D_(rep['expense_in'])),(400000,300000))   # báo cáo theo loại vẫn gộp
        self.err('classify',ids=[self.tx('K-OUT')['id']],parts=[dict(category='income',node=inc)],reason='x');self.classify(['R-SAL'],[dict(category='income',node=inc)])  # nhóm thu chỉ nhận tiền vào
        self.err('classify',ids=[self.tx('U-1')['id']],parts=[dict(category='income',node=inc)],reason='x')
        self.classify(['U-1'],[dict(category='investment',node=inv,profile=prop)])      # nhóm đầu tư gắn BĐS (đối tượng không còn bắt buộc, R120)
        self.err('classify',ids=[self.tx('R-OUT')['id']],parts=[dict(category='expense',node=inc)],reason='x')                                       # sai loại
        self.assertEqual(self.tx('K-OUT')['allocations'][0]['category'],'expense');self.assertEqual(self.tx('K-OUT')['allocations'][0]['node'],goods)
        self.assertEqual(D_(self.node('Thu phụ')['totals']['in']),5000000);self.assertEqual(D_(self.root('income')['totals']['in']),0)
        # chuyển nút con: cùng loại được, khác loại bị chặn
        self.act('category-create',name='Ăn uống',description='',parent='expense');eat=self.node('Ăn uống')['id'];self.act('category-edit',category=eat,parent=biz);self.assertEqual(self.node('Ăn uống')['path'],'Kinh doanh nhỏ › Ăn uống')
        self.err('category-edit',category=eat,parent=inc);self.act('category-edit',category=eat,parent='expense');self.assertEqual(self.node('Ăn uống')['path'],'Chi tiêu › Ăn uống')

    def test_snapshot_freezes_custom_root(self):
        biz,goods=self.biz();self.classify(['R-OUT','K-OUT'],[dict(category='expense',node=goods)]);self.classify(['R-IN-A','R-IN-B','R-SAL'],[dict(category='income')]);self.classify(['U-1'],[dict(category='expense')])
        self.act('approve',account=self.account,reason='Duyệt');s1=self.store.state()['snapshots'][-1];paths={n['name']:n['path'] for n in s1['category_tree']};self.assertEqual(paths,{'Kinh doanh nhỏ':'Kinh doanh nhỏ','Nhập hàng':'Kinh doanh nhỏ › Nhập hàng'})
        old=s1['hash'];self.act('category-edit',category=biz,name='Doanh nghiệp');frozen=self.store.state()['snapshots'][0];self.assertEqual((frozen['hash'],{n['name'] for n in frozen['category_tree']}),(old,{'Kinh doanh nhỏ','Nhập hàng'}))

    # ---- US2 -----------------------------------------------------------
    def test_period_totals_history_and_validation(self):
        self.classify(['R-OUT','K-OUT'],[dict(category='expense')]);self.classify(['R-IN-A','R-IN-B'],[dict(category='expense')]);self.classify(['R-SAL'],[dict(category='income')])
        full=self.store.category_view(self.store.state());self.assertEqual(full['period'],None)
        sept=self.store.category_view(self.store.state(),'2026-09-01','2026-09-30');ex=next(r for r in sept['roots'] if r['key']=='expense')['totals'];self.assertEqual((D_(ex['out']),D_(ex['in']),D_(ex['net_spend']),ex['transactions']),(1000000,300000,700000,2));self.assertEqual(sept['period'],{'start':'2026-09-01','end':'2026-09-30'})
        octo=next(r for r in self.store.category_view(self.store.state(),'2026-10-01','2026-10-31')['roots'] if r['key']=='expense')['totals'];self.assertEqual((D_(octo['out']),D_(octo['in'])),(400000,300000))
        edge=next(r for r in self.store.category_view(self.store.state(),'2026-09-02','2026-09-02')['roots'] if r['key']=='expense')['totals'];self.assertEqual((D_(edge['out']),edge['transactions']),(1000000,1))   # hai đầu bao gồm
        h=self.store.category_history(dict(category='expense',start='2026-09-01',end='2026-09-30'));self.assertEqual((len(h['rows']),D_(h['totals']['net_spend']),h['period']['start']),(2,700000,'2026-09-01'));self.assertEqual({r['date'][:7] for r in h['rows']},{'2026-09'})
        self.assertEqual(sum(D_(r['amount']) if r['direction']=='OUT' else -D_(r['amount']) for r in h['rows']),D_(h['totals']['net_spend']))
        empty=self.store.category_history(dict(category='principal',start='2026-09-01',end='2026-09-30'));self.assertEqual((empty['evidence'],empty['rows']),('EMPTY',[]));self.assertIn('Kỳ nguồn',empty['source_notice'])
        for a,b in (('2026-10-01','2026-09-01'),('bad','2026-09-01'),('2026-09-01','2026-13-40')):
            with self.assertRaises(ValidationError):self.store.category_view(self.store.state(),*self.store.cat_period(dict(start=a,end=b)))
        events=self.store.backup()['events'];self.store.category_view(self.store.state(),'2026-09-01','2026-09-30');self.assertEqual(self.store.backup()['events'],events)

    # ---- US3 -----------------------------------------------------------
    def test_review_by_category_with_reconciliation(self):
        biz,goods=self.biz();self.act('object-quick-create',kind='PROPERTY',name='Đất A');prop=next(p['id'] for p in self.store.state()['profiles'] if p['name']=='Đất A')
        self.classify(['R-OUT'],[dict(category='expense',amount='600000'),dict(category='investment',amount='400000',profile=prop)])                    # giao dịch tách
        self.classify(['K-OUT'],[dict(category='expense',node=goods)]);self.classify(['R-IN-A','R-IN-B'],[dict(category='expense')]);self.classify(['R-SAL'],[dict(category='income')])
        r=self.store.category_review(dict(account=self.account));g={x['key']:x for x in r['groups']}
        self.assertTrue(r['reconciled']);self.assertEqual({k:v['ok'] for k,v in r['checks'].items()},{'transactions':True,'money_in':True,'money_out':True});self.assertEqual(r['checks']['transactions']['source'],6)
        ex=g['expense'];self.assertEqual((ex['transactions'],D_(ex['out']),D_(ex['in']),D_(ex['net_spend'])),(3,600000,600000,0))                           # R-OUT (phần 600k) + hoàn A, B; K-OUT thuộc gốc tự tạo
        self.assertEqual((g['investment']['transactions'],g['investment']['objects'],D_(g['investment']['out'])),(1,1,400000))
        self.assertEqual((g['unknown']['transactions'],D_(g['unknown']['out'])),(1,20000))                                                                   # U-1 chưa phân loại
        custom=next(x for x in r['groups'] if x['key']==biz);self.assertEqual((custom['system'],custom['type'],custom['transactions'],D_(custom['out']),D_(custom['net_spend'])),(False,'expense',1,400000,400000))
        self.assertEqual([(c['name'],c['transactions']) for c in custom['children']],[('Nhập hàng',1)]);self.assertEqual(D_(g['income']['in']),5000000)
        self.assertEqual(sum(x['transactions'] for x in r['groups'])-1,6)                                                                                       # R-OUT đếm ở hai nhóm → tổng nhóm = 7
        bad=copy.deepcopy(self.store.state());next(t for t in bad['transactions'] if t['reference']=='R-IN-A')['allocations'][0]['amount']='299000'
        r2=self.store.category_review(dict(account=self.account),bad);self.assertFalse(r2['reconciled']);self.assertFalse(r2['checks']['money_in']['ok']);self.assertEqual(D_(r2['checks']['money_in']['difference']),-1000);self.assertTrue(r2['checks']['money_out']['ok'])
        self.assertEqual(self.store.category_review(dict(account=self.account))['reconciled'],True)

    def test_review_empty_account_detail_scope_and_read_only(self):
        self.act('account',name='Trống',reference='000999',opening='0',effective_date='2026-09-01',opening_source='QA');empty=self.store.state()['accounts'][1]['id']
        r=self.store.category_review(dict(account=empty));self.assertTrue(r['empty']);self.assertTrue(r['reconciled']);self.assertTrue(all(g['transactions']==0 for g in r['groups']))
        self.classify(['R-OUT','K-OUT'],[dict(category='expense')]);h=self.store.category_history(dict(category='expense',account=self.account));other=self.store.category_history(dict(category='expense',account=empty))
        self.assertEqual((len(h['rows']),len(other['rows'])),(2,0));self.err('classify',ids=[self.tx('R-OUT')['id']],parts=[dict(category='expense',node='khong-co')],reason='x')
        with self.assertRaises(ValidationError):self.store.category_review(dict(account='khong-co'))
        events=self.store.backup()['events'];self.store.category_review(dict(account=self.account));self.assertEqual(self.store.backup()['events'],events)
        restore=P01Store(self.tmp.name+'/restore');restore.restore(self.store.backup(),'restore');self.assertEqual(restore.view()['categories'],self.store.view()['categories'])
