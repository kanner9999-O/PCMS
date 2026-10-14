import tempfile
import unittest
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError
import test_p18_acceptance as base

class P27Acceptance(base.P18Acceptance):
    """Dùng lại dữ liệu P18 (Kết có hai khoản vay, danh mục Loans › Long debt)."""
    def kind(self,key):
        c=self.store.view()['categories'];r=next((x for x in c['roots'] if x['key']==key),None)
        return r['object_kind'] if r else next((n for n in c['nodes'] if n['id']==key),None)
    def eff(self,name):return self.nodes()[name]['effective_object_kind']
    def pid_of(self,name):return next(p['id'] for p in self.store.state()['profiles'] if p['kind']=='PERSON' and p['name']==name)

    def test_declare_inherit_override_and_history(self):
        self.assertIsNone(self.kind('principal'));self.assertIsNone(self.eff('Loans'))                                   # mặc định không có đối tượng
        self.act('category-object-kind',category='principal',kind='PERSON');self.assertEqual((self.kind('principal'),self.eff('Loans'),self.eff('Long debt'),self.eff('Kết')),('PERSON',)*4)
        self.act('category-object-kind',category=self.nodes()['Long debt']['id'],kind='LOAN',reason='Khoản vay dài hạn');self.assertEqual((self.eff('Long debt'),self.eff('Loans')),('LOAN','PERSON'))
        self.act('category-object-kind',category=self.nodes()['Loans']['id'],kind='PROPERTY');self.assertEqual((self.eff('Loans'),self.eff('Long debt')),('PROPERTY','LOAN'))   # con tự đặt giữ nguyên
        self.act('category-object-kind',category=self.nodes()['Long debt']['id'],kind='INHERIT');self.assertEqual(self.eff('Long debt'),'PROPERTY')
        self.act('category-object-kind',category=self.nodes()['Loans']['id'],kind='NONE');self.assertIsNone(self.eff('Loans'));self.assertIsNone(self.eff('Long debt'))
        self.assertIsNone(self.eff('Loans'));self.act('category-object-kind',category='principal',kind='NONE');self.assertIsNone(self.kind('principal'))
        h=self.nodes()['Long debt']['history'];self.assertEqual([x['action'] for x in h][-2:],['OBJECT_KIND','OBJECT_KIND']);self.assertEqual(h[-2]['reason'],'Khoản vay dài hạn')
        self.assertEqual(self.store.view()['categories']['object_kinds']['PERSON'],'Người')
        for bad in (dict(category='principal',kind='X'),dict(category='unknown',kind='PERSON'),dict(category='principal',kind='INHERIT'),dict(category='nope',kind='PERSON')):self.err('category-object-kind',**bad)

    def test_user_root_default_and_children(self):
        self.act('category-create',name='Gốc riêng',type='expense');root=self.nodes()['Gốc riêng']['id'];self.act('category-create',name='Con riêng',description='',parent=root)
        self.assertEqual((self.eff('Gốc riêng'),self.eff('Con riêng')),(None,None));self.act('category-object-kind',category=root,kind='PERSON');self.assertEqual((self.eff('Gốc riêng'),self.eff('Con riêng')),('PERSON','PERSON'))

    def test_classify_person_object_not_required_and_kind_enforced(self):
        self.act('object-quick-create',kind='PERSON',name='Tươi');tuoi=self.pid_of('Tươi');kết=self.pid_of('Kết')
        self.act('category-object-kind',category='principal',kind='PERSON')
        self.classify(['X1'],[dict(category='principal',profile=tuoi)])                                                 # người trong danh mục cho vay, không cần khoản vay
        t=self.tx('X1');self.assertEqual((t['allocations'][0]['category'],t['allocations'][0]['profile']),('principal',tuoi))
        self.err('classify',ids=[self.tx('K1')['id']],parts=[dict(category='principal',profile=self.l5)])            # khoản vay sai loại (danh mục khai Người)
        self.classify(['K1'],[dict(category='principal')])                                                                   # đối tượng không bắt buộc
        self.act('category-object-kind',category='principal',kind='LOAN');self.classify(['K1'],[dict(category='principal',profile=self.l5)]);self.err('classify',ids=[self.tx('K1')['id']],parts=[dict(category='principal',profile=kết)])
        self.err('classify',ids=[self.tx('S1')['id']],parts=[dict(category='income',profile=kết)])                           # danh mục chưa khai: thu nhập không đối tượng
        self.act('category-object-kind',category='income',kind='PERSON');self.classify(['S1'],[dict(category='income',profile=kết)])

    def test_undeclared_keeps_legacy_rules_and_old_data_unchanged(self):
        before=[(t['reference'],t['allocations']) for t in self.store.state()['transactions']]
        self.classify(['K1'],[dict(category='principal',profile=self.l10)])                                              # chưa khai: quy tắc cũ (gốc ↔ khoản vay)
        self.err('classify',ids=[self.tx('K2')['id']],parts=[dict(category='principal',profile=self.person)])
        self.err('classify',ids=[self.tx('K2')['id']],parts=[dict(category='interest',profile=self.person)])
        self.classify(['X1'],[dict(category='expense',profile=self.l5)])                                                   # chi hộ khoản vay vẫn được
        for ref,alloc in before:
            if ref not in {'K1','X1'}:self.assertEqual(next(t for t in self.store.state()['transactions'] if t['reference']==ref)['allocations'],alloc)
        self.assertTrue(self.store.view()['debts']['loans'])

    def test_quick_person_unique(self):
        self.act('object-quick-create',kind='PERSON',name='Thái');self.err('object-quick-create',kind='PERSON',name='thái');self.err('object-quick-create',kind='PERSON',name='')

    def test_read_only(self):
        n=len(self.store.events());self.store.view();self.assertEqual(len(self.store.events()),n)

for name in [n for n in dir(base.P18Acceptance) if n.startswith('test_')]:setattr(P27Acceptance,name,None)
if __name__=='__main__':unittest.main()
