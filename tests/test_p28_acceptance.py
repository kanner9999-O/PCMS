import copy
import unittest
from decimal import Decimal
from uuid import uuid4
from pcms.core import ValidationError
import test_p18_acceptance as base

def D_(x):return Decimal(str(x))

class P28Acceptance(base.P18Acceptance):
    """Dùng lại dữ liệu P18 (6 giao dịch: K1 -5tr, K2 -10tr, K3 +3tr, K4 +200k lãi, S1 +20tr, X1 -10k)."""
    def node(self,name):return self.nodes()[name]
    def objs(self,key):
        c=self.store.view()['categories'];r=next((x for x in c['roots'] if x['key']==key),None) or next(n for n in c['nodes'] if n['id']==key)
        return {o['name']:o for o in r['objects']}
    def make_bds(self):
        self.act('category-create',name='Bất động sản',type='investment');root=self.node('Bất động sản')['id']
        self.act('category-create',name='Chung cư',description='',parent=root);self.act('category-create',name='Đất nền',description='',parent=root)
        self.cc,self.dn=self.node('Chung cư')['id'],self.node('Đất nền')['id']
        for n in ('Chung cư A','Chung cư B','Chung cư C'):self.act('category-object-add',category=self.cc,name=n)
        self.act('category-object-add',category=self.dn,name='Mảnh đất A')
        self.pid={p['name']:p['id'] for p in self.store.state()['profiles']}
        return root

    def test_tree_objects_and_totals(self):
        root=self.make_bds();self.assertEqual(set(self.objs(self.cc)),{'Chung cư A','Chung cư B','Chung cư C'});self.assertEqual(set(self.objs(self.dn)),{'Mảnh đất A'});self.assertEqual(self.objs(root),{})   # đối tượng của chính danh mục, không gộp con
        self.classify(['K1'],[dict(category='investment',node=self.cc,profile=self.pid['Chung cư A'])]);self.classify(['K2'],[dict(category='investment',node=self.cc,profile=self.pid['Chung cư A'])])
        self.classify(['K3'],[dict(category='investment',node=self.cc,profile=self.pid['Chung cư B'])])
        o=self.objs(self.cc);self.assertEqual((o['Chung cư A']['totals'],o['Chung cư B']['totals']),({'in':'0','out':'15000000','transactions':2},{'in':'3000000','out':'0','transactions':1}));self.assertEqual(o['Chung cư C']['totals']['transactions'],0)
        self.assertEqual(self.objs(self.dn)['Mảnh đất A']['totals']['transactions'],0);self.assertTrue(o['Chung cư C']['deletable']);self.assertFalse(o['Chung cư A']['deletable'])
        ch=[n for n in self.store.view()['categories']['nodes'] if n['parent']==root];self.assertEqual({n['name'] for n in ch},{'Chung cư','Đất nền'})

    def test_membership_rules_shared_profiles_and_classify_enforced(self):
        self.make_bds();ket=self.person;self.act('category-create',name='Dài hạn',description='',parent='principal');dh=self.node('Dài hạn')['id']
        self.act('category-object-add',category=dh,profile=ket);self.act('category-object-add',category=self.cc,profile=ket)                      # cùng hồ sơ ở hai danh mục
        self.assertIn('Kết',self.objs(dh));self.assertIn('Kết',self.objs(self.cc))
        self.err('category-object-add',category=dh,profile=ket);self.err('category-object-add',category=self.cc,name='chung cư a');self.err('category-object-add',category=self.cc,name='')
        self.err('category-object-add',category='unknown',name='X');self.err('category-object-add',category='transfer',name='X');self.err('category-object-add',category='nope',name='X')
        self.classify(['K4'],[dict(category='principal',node=dh,profile=ket)])                                                       # hồ sơ người là thành viên → lưu được
        self.err('classify',ids=[self.tx('K1')['id']],parts=[dict(category='principal',node=dh,profile=self.pid['Chung cư A'])])  # không thuộc danh mục
        self.classify(['K1'],[dict(category='investment',node=self.cc)])                                                              # đối tượng không bắt buộc
        self.act('category-object-remove',category=dh,profile=ket,reason='Dọn');self.assertNotIn('Kết',self.objs(dh));self.assertEqual(self.tx('K4')['allocations'][0]['profile'],ket)   # đã phân loại không đổi
        self.err('category-object-remove',category=dh,profile=ket,reason='lần hai')
        self.err('classify',ids=[self.tx('K2')['id']],parts=[dict(category='principal',node=dh,profile=ket)])
        self.classify(['K4'],[dict(category='principal',node=dh,profile=ket)])                                                      # giao dịch cũ giữ đối tượng cũ khi sửa

    def test_legacy_rules_without_members_old_data_unchanged(self):
        before=[(t['reference'],t['allocations']) for t in self.store.state()['transactions']]
        # spec 042 (PO review P1): bỏ ngoại lệ "danh mục chưa có thành viên"; mọi phân loại mới phải đúng quan hệ; dữ liệu cũ giữ nguyên, xem được
        self.err('classify',ids=[self.tx('K1')['id']],parts=[dict(category='principal',profile=self.l10)]);self.err('classify',ids=[self.tx('K2')['id']],parts=[dict(category='principal',profile=self.person)])
        self.err('classify',ids=[self.tx('S1')['id']],parts=[dict(category='income',profile=self.l5)]);self.err('classify',ids=[self.tx('X1')['id']],parts=[dict(category='expense',profile=self.l5)])
        self.act('category-object-add',category='expense',profile=self.person);self.classify(['X1'],[dict(category='expense',profile=self.l5)])
        self.assertTrue(self.store.category_history(dict(category='principal'))['rows'])                                        # dữ liệu cũ vẫn xem được
        for ref,alloc in before:
            if ref not in {'X1'}:self.assertEqual(next(t for t in self.store.state()['transactions'] if t['reference']==ref)['allocations'],alloc)

    def test_rename_delete_rules(self):
        self.make_bds();a=self.pid['Chung cư A'];self.classify(['K1'],[dict(category='investment',node=self.cc,profile=a)])
        self.act('category-object-rename',profile=a,name='Chung cư Alpha');self.assertIn('Chung cư Alpha',self.objs(self.cc));self.err('category-object-rename',profile=a,name='chung cư b');self.err('category-object-rename',profile=a,name='')
        self.err('category-object-delete',profile=a,reason='đã dùng');self.err('category-object-delete',profile=self.person,reason='hồ sơ người')
        c=self.pid['Chung cư C'];self.err('category-object-delete',profile=c,reason='');self.act('category-object-delete',profile=c,reason='Tạo nhầm')
        self.assertNotIn('Chung cư C',self.objs(self.cc));self.assertNotIn(c,[p['id'] for p in self.store.state()['profiles']]);self.assertEqual(self.store.state()['object_deleted'][-1]['name'],'Chung cư C')

    def test_move_object_between_categories_with_history(self):
        root=self.make_bds();a=self.pid['Chung cư A'];self.classify(['K1'],[dict(category='investment',node=self.cc,profile=a)]);self.classify(['K2'],[dict(category='investment',node=self.cc,profile=a)])
        self.act('category-object-move',profile=a,**{'from':self.cc,'to':self.dn},reason='Chuyển sang đất nền')
        self.assertEqual(set(self.objs(self.dn)),{'Mảnh đất A','Chung cư A'});self.assertNotIn('Chung cư A',self.objs(self.cc))
        self.assertEqual(self.objs(self.dn)['Chung cư A']['totals'],{'in':'0','out':'15000000','transactions':2})                       # giao dịch đi theo
        self.assertEqual((D_(self.node('Chung cư')['totals']['out']),D_(self.node('Đất nền')['totals']['out'])),(0,15000000))
        self.assertEqual(self.objs(self.dn)['Chung cư A']['history'][-1]['reason'],'Chuyển sang đất nền')
        self.assertEqual(self.tx('K1')['allocations'][0]['node'],self.cc)                                                                   # phân loại gốc không đổi
        h=self.store.category_history(dict(category=self.dn,object=a));self.assertEqual(({r['reference'] for r in h['rows']},D_(h['totals']['out'])),({'K1','K2'},15000000))
        self.assertEqual(self.store.category_history(dict(category=self.dn,object=self.pid['Mảnh đất A']))['rows'],[])
        for bad in (dict(profile=a,to='expense'),dict(profile=a,to=self.dn),dict(profile=a,to=self.cc,reason=''),dict(profile=self.pid['Mảnh đất A'],to=self.dn)):
            args={'profile':a,'from':self.dn,'to':'investment','reason':'x'};args.update({'from':args['from']});args.update(bad);self.err('category-object-move',**args)
        self.act('category-object-move',profile=a,**{'from':self.dn,'to':self.cc},reason='Trả lại');self.assertEqual(self.objs(self.cc)['Chung cư A']['totals']['transactions'],2)

    def test_read_only_and_backup(self):
        self.make_bds();n=len(self.store.events());self.store.view();self.assertEqual(len(self.store.events()),n)
        import tempfile
        from pcms.p01 import P01Store
        other=P01Store(tempfile.mkdtemp());other.restore(self.store.backup(),str(uuid4()));self.assertEqual(len(other.view()['categories']['nodes']),len(self.store.view()['categories']['nodes']))

for name in [n for n in dir(base.P18Acceptance) if n.startswith('test_')]:setattr(P28Acceptance,name,None)
if __name__=='__main__':unittest.main()
