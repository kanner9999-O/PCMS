import unittest
from decimal import Decimal
import test_p18_acceptance as base

def D_(x):return Decimal(str(x))

class P35Acceptance(base.P18Acceptance):
    """Quản lý đối tượng (spec 033) trên dữ liệu P18: người Kết có hai khoản vay 5tr/10tr."""
    def objs(self):return {o['name']:o for o in self.store.view()['objects']['rows']}
    def prof(self,pid):return next(p for p in self.store.state()['profiles'] if p['id']==pid)
    def make(self,name,typ='OBJECT',**k):
        self.act('object-create',name=name,type=typ,**k);return next(p['id'] for p in self.store.state()['profiles'] if p['name']==name)

    def test_list_types_and_loans_nested_in_person(self):
        O=self.store.view()['objects'];self.assertEqual(O['types'],{'PERSON':'Người','PROPERTY':'Bất động sản','OBJECT':'Khác'})
        rows={o['name']:o for o in O['rows']};self.assertNotIn('Kết 5tr',rows);self.assertTrue(all(o['kind']!='LOAN' for o in O['rows']))
        k=rows['Kết'];self.assertEqual((k['type_name'],sorted(l['name'] for l in k['loans'])),('Người',['Kết 10tr','Kết 5tr']))
        self.assertEqual((k['totals']['transactions'],D_(k['totals']['out'])),(4,15000000));self.assertEqual({l['direction'] for l in k['loans']},{'RECEIVABLE'})
        self.assertIsNotNone(k['delete_reason']);self.assertIn('khoản vay',k['type_reason'])

    def test_create_unique_types_and_attach(self):
        self.act('category-create',name='Tươi Cat',description='',parent='principal');cat=self.nodes()['Tươi Cat']['id']
        pid=self.make('Tươi','PERSON',category=cat);self.assertEqual([c['path'] for c in self.objs()['Tươi']['categories']],['Gốc vay › Tươi Cat'])
        for bad in (dict(name='tươi',type='PERSON'),dict(name='  TƯƠI ',type='OBJECT'),dict(name='X',type='LOAN'),dict(name='X',type='nope'),dict(name='',type='PERSON'),dict(name='a'*101,type='PERSON'),dict(name='Y',type='PERSON',category='nope')):self.err('object-create',**bad)
        self.act('object-archive',profile=pid,reason='không dùng');self.err('object-create',name='tươi',type='PERSON')                 # tên đã lưu trữ vẫn chiếm
        self.act('object-create',name='Chi tiêu chung',type='OBJECT');self.assertEqual(self.objs()['Chi tiêu chung']['categories'],[])    # đối tượng có thể chưa thuộc danh mục nào

    def test_rename_and_type_change_rules(self):
        a=self.make('Hòa Sơn');self.act('object-edit',profile=a,name='Hòa Sơn 2');self.assertEqual(self.prof(a)['rename_history'][0]['before'],'Hòa Sơn')
        self.err('object-edit',profile=a,name='kết');self.err('object-edit',profile=a,name='Hòa Sơn 2');self.err('object-edit',profile=a)
        self.err('object-edit',profile=a,type='PERSON')                                                                          # đổi loại cần lý do
        self.act('object-edit',profile=a,type='PERSON',reason='Là một người');self.assertEqual((self.prof(a)['kind'],self.prof(a)['type_history'][0]['after']),('PERSON','PERSON'))
        self.err('object-edit',profile=a,type='LOAN',reason='x');self.err('object-edit',profile=self.l5,type='PERSON',reason='x');self.err('object-edit',profile=self.person,type='PROPERTY',reason='x')   # khoản vay / người có khoản vay
        self.act('object-edit',profile=a,type='PROPERTY',reason='Đổi');self.act('object-edit',profile=a,type='OBJECT',reason='Đổi lại')

    def test_property_with_investment_data_and_business_cannot_change(self):
        self.act('category-create',name='Nhà',type='investment');cat=self.nodes()['Nhà']['id']
        p=self.make('Xuân Mai','PROPERTY',category=cat);self.act('business-set',category=cat,profile=p,type='PROPERTY',effective_date='2026-09-01')
        self.err('object-edit',profile=p,type='OBJECT',reason='x');self.assertIn('nghiệp vụ',self.objs()['Xuân Mai']['type_reason'])
        self.act('business-clear',category=cat,profile=p,reason='gỡ');self.classify(['X1'],[dict(category='investment',node=cat,profile=p)])
        self.assertIn('Bất động sản',self.objs()['Xuân Mai']['type_reason']);self.err('object-edit',profile=p,type='OBJECT',reason='x')

    def test_archive_restore_and_picker_guards(self):
        a=self.make('Cũ','PERSON');self.act('category-create',name='Nhóm A',description='',parent='expense');ca=self.nodes()['Nhóm A']['id']
        self.err('object-archive',profile=a);self.act('object-archive',profile=a,reason='Không dùng nữa');self.assertEqual(self.objs()['Cũ']['status'],'ARCHIVED');self.err('object-archive',profile=a,reason='lần hai')
        self.err('category-object-add',category=ca,profile=a)                                                                      # không thêm vào danh mục mới
        self.err('classify',ids=[self.tx('X1')['id']],parts=[dict(category='expense',node=ca,profile=a)])
        self.err('object-restore',profile=self.person)
        self.act('object-restore',profile=a);self.assertEqual(self.objs()['Cũ']['status'],'ACTIVE');self.act('category-object-add',category=ca,profile=a)
        self.assertEqual(self.prof(a)['archive_history'][0]['action'],'ARCHIVE')
        self.err('object-archive',profile=self.person,reason='x')                                                                   # còn dư nợ gốc
        self.err('object-archive',profile=self.l5,reason='x')

    def test_delete_only_when_unused(self):
        a=self.make('Tạm','PERSON');self.err('object-delete',profile=a);self.act('object-delete',profile=a,reason='Tạo nhầm')
        self.assertNotIn('Tạm',self.objs());self.assertEqual(self.store.state()['object_deleted'][0]['name'],'Tạm');self.act('object-create',name='Tạm',type='PERSON')      # tên được giải phóng
        self.act('category-create',name='Mục',description='',parent='expense');cat=self.nodes()['Mục']['id'];u=self.make('Đã dùng','OBJECT',category=cat)
        self.classify(['X1'],[dict(category='expense',node=cat,profile=u)]);self.assertIsNotNone(self.objs()['Đã dùng']['delete_reason']);self.err('object-delete',profile=u,reason='x')
        self.err('object-delete',profile=self.person,reason='x');self.err('object-delete',profile=self.l5,reason='x')
        self.act('object-archive',profile=u,reason='Đã dùng, lưu trữ');self.assertEqual(self.objs()['Đã dùng']['status'],'ARCHIVED')
        self.act('category-create',name='NV',description='',parent='principal');nv=self.nodes()['NV']['id'];b=self.make('Có NV','OBJECT',category=nv)
        self.act('business-set',category=nv,profile=b,type='LOAN_LENT',effective_date='2026-09-01');self.err('object-delete',profile=b,reason='x')

    def test_history_across_categories_includes_loans_and_totals_unchanged(self):
        c0=self.store.view()['categories']['roots'];rep0=self.store.report(self.store.state(),self.account)
        h=self.store.category_history(dict(category='*',object=self.person));self.assertEqual(({r['reference'] for r in h['rows']},h['path']),({'K1','K2','K3','K4'},'Tất cả danh mục'))
        with self.assertRaises(Exception):self.store.category_history(dict(category='*'))                                          # '*' cần đối tượng
        a=self.make('Rỗng','PERSON');self.assertEqual(self.store.category_history(dict(category='*',object=a))['rows'],[])
        self.assertEqual([r['totals'] for r in self.store.view()['categories']['roots']],[r['totals'] for r in c0]);self.assertEqual(self.store.report(self.store.state(),self.account),rep0)

    def test_category_with_zero_or_many_objects(self):
        self.act('category-create',name='Cho vay NV',description='',parent='principal');cat=self.nodes()['Cho vay NV']['id']
        for n in ('Mỹ','Kết2','Tươi'):self.make(n,'PERSON',category=cat)
        node=next(n for n in self.store.view()['categories']['nodes'] if n['id']==cat);self.assertEqual(sorted(o['name'] for o in node['objects']),['Kết2','Mỹ','Tươi'])
        self.classify(['X1'],[dict(category='expense')])                                                                          # chi tiêu không có đối tượng: phân loại thẳng

if __name__=='__main__':unittest.main()
