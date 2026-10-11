import base64
import copy
import tempfile
import time
import unittest
from decimal import Decimal
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError
from p01_fixtures import statement

ROWS=[('02/09/2026','An sang','C-1','50000','','9950000'),('03/09/2026','Di grab','C-2','30000','','9920000'),('04/09/2026','Mua do chung','C-3','100000','','9820000'),('05/09/2026','Hoan tien','C-4','','20000','9840000'),('06/09/2026','Luong','C-5','','5000000','14840000')]

def D_(x):return Decimal(str(x))

class P10Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def act(self,a,**d):return self.store.apply(a,d,str(uuid4()))
    def err(self,a,**d):
        with self.assertRaises(ValidationError):self.act(a,**d)
    def cats(self):return self.store.view()['categories']
    def node(self,name):return next(n for n in self.cats()['nodes'] if n['name']==name)
    def root(self,key):return next(r for r in self.cats()['roots'] if r['key']==key)
    def tx(self,ref):return next(t for t in self.store.state()['transactions'] if t['reference']==ref)
    def load(self,rows=ROWS,opening=10000000,closing=14840000):
        self.act('account',name='QA danh mục',reference='000123',opening=str(opening),effective_date='2026-09-01',opening_source='QA')
        self.account=self.store.state()['accounts'][0]['id']
        self.act('import',account=self.account,filename='cat.xlsx',content=base64.b64encode(statement(rows,opening,closing,start='01/09/2026',end='30/09/2026')).decode())
        self.act('publish',batch=self.store.state()['imports'][-1]['id'])
    def classify(self,refs,category,node=None,parts=None):
        p=parts or [dict(category=category,**({'node':node} if node else {}))]
        self.act('classify',ids=[self.tx(r)['id'] for r in refs],parts=p,reason='QA')
    def tree(self):
        self.load();self.act('category-create',name='Ăn uống',description='',parent='expense');self.act('category-create',name='Đi lại',description='',parent='expense')
        return self.node('Ăn uống')['id'],self.node('Đi lại')['id']

    def test_crud_and_rules(self):
        self.act('category-create',name='Chi nhà',description='x',parent='expense');a=self.node('Chi nhà')['id']
        self.err('category-create',name='  chi NHÀ ',description='',parent='expense')               # trùng tên (hoa/thường, cùng cha)
        self.act('category-create',name='Chi nhà',description='',parent='income')                    # khác cha thì được
        self.err('category-create',name='X',description='',parent='transfer');self.err('category-create',name='X',description='',parent='unknown')
        self.err('category-create',name='',description='',parent='expense');self.err('category-create',name='a'*101,description='',parent='expense')
        self.act('category-create',name='Con',description='',parent=a);b=self.node('Con')['id']
        self.act('category-create',name='Cháu',description='',parent=b);c=self.node('Cháu')['id']
        self.err('category-create',name='Chắt',description='',parent=c)                              # cấp 5 bị chặn
        self.err('category-edit',category=a,parent=c)                                                 # vòng lặp
        self.err('category-edit',category=a,parent=a)
        self.err('category-edit',category=b,parent='income')                                          # khác gốc
        self.act('category-edit',category=c,parent=a);self.assertEqual(self.node('Cháu')['parent'],a)
        self.act('category-edit',category=a,name='Chi nhà cửa',reason='đổi');self.assertEqual([h['action'] for h in self.node('Chi nhà cửa')['history']],['CREATE','RENAME'])
        self.err('category-edit',category=a)                                                           # không thay đổi
        self.err('category-archive',category=a,reason='')                                             # thiếu lý do
        self.err('category-archive',category=a,reason='x')                                            # còn con hoạt động
        self.act('category-archive',category=c,reason='không dùng');self.act('category-archive',category=b,reason='không dùng');self.act('category-archive',category=a,reason='không dùng')
        self.err('category-create',name='Chi nhà cửa',description='',parent='expense')                # trùng tên nút đã lưu trữ
        self.err('category-create',name='Mới',description='',parent=a)                                # cha đã lưu trữ
        self.err('category-restore',category=b)                                                       # cha còn lưu trữ
        self.act('category-restore',category=a);self.act('category-restore',category=b)
        self.act('category-root-describe',root='expense',description='Mô tả gốc');self.assertEqual(self.root('expense')['description'],'Mô tả gốc')
        self.err('category-root-describe',root='nope',description='x');self.err('category-edit',category='expense',name='Khác')

    def test_totals_count_once_and_split_across_branches(self):
        eat,go=self.tree()
        self.classify(['C-1'],'expense',eat);self.classify(['C-2'],'expense',go)
        self.classify(['C-3'],None,parts=[dict(category='expense',node=eat,amount='60000'),dict(category='expense',node=go,amount='40000')])
        self.classify(['C-5'],'income')
        ex,e,g,inc,unk=self.root('expense')['totals'],self.node('Ăn uống')['totals'],self.node('Đi lại')['totals'],self.root('income')['totals'],self.root('unknown')['totals']
        self.assertEqual((D_(ex['out']),D_(ex['in']),ex['transactions'],ex['parts']),(180000,0,3,4))     # C-3 đếm một lần ở cha
        self.assertEqual((D_(e['out']),e['transactions']),(110000,2));self.assertEqual((D_(g['out']),g['transactions']),(70000,2))
        self.assertEqual((D_(inc['in']),D_(unk['in']),unk['transactions']),(5000000,20000,1))            # C-4 chưa phân loại → gốc Chưa phân loại
        txs=self.store.state()['transactions'];self.assertEqual(sum(D_(t['signed_amount']) for t in txs),D_(self.store.report(self.store.state(),self.account)['balance'])-10000000)

    def test_node_validation_and_bulk(self):
        eat,go=self.tree()
        self.err('classify',ids=[self.tx('C-1')['id']],parts=[dict(category='income',node=eat)],reason='x')   # node thuộc gốc khác
        self.err('classify',ids=[self.tx('C-1')['id']],parts=[dict(category='expense',node='khong-co')],reason='x')
        self.act('category-archive',category=go,reason='x');self.err('classify',ids=[self.tx('C-1')['id']],parts=[dict(category='expense',node=go)],reason='x')
        before=copy.deepcopy(self.store.state()['transactions'])
        self.classify(['C-1','C-2','C-3'],'expense',eat)
        after=self.store.state()['transactions']
        for b,a in zip(before,after):
            self.assertEqual((b['signed_amount'],b['date'],b['reference']),(a['signed_amount'],a['date'],a['reference']))
            if b['reference'] in {'C-4','C-5'}:self.assertEqual(b['allocations'],a['allocations'])        # chỉ dòng được chọn đổi
        self.assertEqual(self.tx('C-2')['allocations'][0]['node'],eat)
        self.classify(['C-5'],'income');self.assertNotIn('node',self.tx('C-5')['allocations'][0])            # không dùng node → dạng cũ

    def test_history_evidence_archived_and_status(self):
        eat,go=self.tree()
        self.classify(['C-1'],'expense',eat);self.classify(['C-2'],'expense',go)
        h=self.store.category_history(dict(category='expense'));self.assertEqual((h['evidence'],len(h['rows']),h['path']),('HAS_DATA',2,'Chi tiêu'))
        self.assertEqual({r['status'] for r in h['rows']},{'DRAFT'});self.assertTrue(all(r['sources'] for r in h['rows']))
        self.assertEqual([r['reference'] for r in h['rows']],['C-1','C-2'])
        self.assertEqual(self.store.category_history(dict(category=eat))['path'],'Chi tiêu › Ăn uống')
        self.act('category-create',name='Trống',description='',parent='expense');empty=self.node('Trống')['id']
        e=self.store.category_history(dict(category=empty));self.assertEqual((e['evidence'],e['rows']),('EMPTY',[]));self.assertIn('Kỳ nguồn',e['source_notice'])
        self.act('category-archive',category=go,reason='x');self.assertEqual(D_(self.root('expense')['totals']['out']),80000)   # đã lưu trữ vẫn tính
        self.assertEqual(self.store.category_history(dict(category='expense'))['rows'][1]['node_status'],'ARCHIVED')
        self.err('classify',ids=[self.tx('C-3')['id']],parts=[dict(category='expense',node=go)],reason='x')
        fresh=P01Store(self.tmp.name+'/fresh');self.assertEqual(fresh.category_history(dict(category='expense'))['evidence'],'EMPTY_NO_SOURCE')
        with self.assertRaises(ValidationError):self.store.category_history(dict(category='nope'))

    def test_snapshot_freezes_names_and_old_data_unchanged(self):
        self.load();report_before=self.store.report(self.store.state(),self.account)
        self.classify(['C-1','C-2','C-3'],'expense');self.classify(['C-4','C-5'],'income')
        self.act('approve',account=self.account,reason='Duyệt 1');s1=self.store.state()['snapshots'][-1]
        self.assertNotIn('category_tree',s1)                                                                 # chưa dùng cây → snapshot như cũ
        self.act('category-create',name='Ăn uống',description='',parent='expense');eat=self.node('Ăn uống')['id']
        self.act('begin-adjustment',account=self.account,reason='phân nhóm');self.classify(['C-1'],'expense',eat)
        self.act('approve',account=self.account,reason='Duyệt 2');s2=self.store.state()['snapshots'][-1];self.assertEqual(s2['category_tree'][0]['name'],'Ăn uống')
        old_hash=s2['hash'];self.act('category-edit',category=eat,name='Bữa ăn',reason='đổi tên')
        frozen=next(x for x in self.store.state()['snapshots'] if x['id']==s2['id']);self.assertEqual((frozen['category_tree'][0]['name'],frozen['hash']),('Ăn uống',old_hash))
        self.assertEqual(self.node('Bữa ăn')['path'],'Chi tiêu › Bữa ăn');self.assertEqual(self.store.state()['snapshots'][0]['hash'],s1['hash'])
        self.assertNotIn('Ăn uống',[n['name'] for n in self.cats()['nodes']])

    def test_read_only_and_report_unchanged(self):
        self.load();self.classify(['C-1','C-2','C-3'],'expense');r1=copy.deepcopy(self.store.report(self.store.state(),self.account)['totals'])
        self.act('category-create',name='Ăn uống',description='',parent='expense')
        self.assertEqual(self.store.report(self.store.state(),self.account)['totals'],r1)                    # báo cáo đợt đếm theo khóa gốc, không đổi
        events=self.store.backup()['events'];self.cats();self.store.category_history(dict(category='expense'));self.assertEqual(self.store.backup()['events'],events)
        restore=P01Store(self.tmp.name+'/restore');restore.restore(self.store.backup(),'restore');self.assertEqual(restore.view()['categories'],self.store.view()['categories'])

    def test_scale_two_thousand_transactions(self):
        n=2000;balance=10000000;rows=[]
        for i in range(n):
            balance-=1000;rows.append((f'{1+i*28//n:02d}/09/2026',f'Chi {i}',f'S-{i}','1000','',str(balance)))
        self.load(rows,10000000,balance);self.act('category-create',name='Số lượng lớn',description='',parent='expense');node=self.node('Số lượng lớn')['id']
        self.act('classify',ids=[t['id'] for t in self.store.state()['transactions']],parts=[dict(category='expense',node=node)],reason='QA')
        start=time.time();v=self.cats();h=self.store.category_history(dict(category='expense'));took=time.time()-start
        self.assertEqual((v['roots'][1]['totals']['transactions'],len(h['rows'])),(n,n));self.assertLess(took,3)
