import unittest
from decimal import Decimal
from unittest import mock
from pcms.core import ValidationError
from pcms.p01 import P01Store
import test_p18_acceptance as base

def D_(x):return Decimal(str(x))

class P31Acceptance(base.P18Acceptance):
    """Dùng lại dữ liệu P18; mô phỏng hai hồ sơ trùng tên đã có từ trước bằng cách tạm tắt kiểm tra."""
    def setUp(self):
        super().setUp()
        self.act('category-create',name='Property',type='investment');self.prop_cat=self.nodes()['Property']['id']
    def pid(self,kind,name=None):
        return next(p['id'] for p in self.store.state()['profiles'] if p['kind']==kind and (name is None or p['name']==name))
    def members(self,key=None):
        c=self.store.view()['categories'];n=next(x for x in c['nodes'] if x['id']==(key or self.prop_cat));return {o['profile']:o for o in n['objects']}
    def make_dup(self):
        self.act('object-quick-create',kind='PROPERTY',name='Xuân Mai');self.xm=self.pid('PROPERTY','Xuân Mai');self.act('category-object-add',category=self.prop_cat,profile=self.xm)
        with mock.patch.object(P01Store,'require_free_name',lambda *a,**k:None):self.act('category-object-add',category=self.prop_cat,name='Xuân Mai')       # mô phỏng trùng đã tồn tại từ trước
        self.xo=self.pid('OBJECT','Xuân Mai')

    def test_every_path_rejects_duplicate_names_across_kinds(self):
        self.act('object-quick-create',kind='PROPERTY',name='Xuân Mai');n=len(self.store.state()['profiles'])
        for name in ('xuân mai','  XUÂN   Mai  ','Xuân Mai'):
            self.err('category-object-add',category=self.prop_cat,name=name);self.err('profile',kind='PERSON',name=name);self.err('object-quick-create',kind='PERSON',name=name);self.err('object-quick-create',kind='PROPERTY',name=name)
        self.err('object-quick-create',kind='LOAN',party_name='Xuân Mai',name='Khoản mới')                                                         # người mới trùng BĐS
        self.act('category-object-add',category=self.prop_cat,name='Hòa Sơn');hs=self.pid('OBJECT','Hòa Sơn');self.err('category-object-rename',profile=hs,name='xuân mai')   # đổi tên cũng kiểm
        self.act('category-object-rename',profile=hs,name='Hòa Sơn 2');self.act('category-object-rename',profile=hs,name='Hòa Sơn 2')             # tự đổi về chính mình: không coi là trùng
        self.assertEqual(len(self.store.state()['profiles']),n+1);self.act('category-object-add',category=self.prop_cat,name='Xuân Mai 2')            # tên khác hợp lệ

    def test_legacy_import_by_name_reuses_existing_profile_of_any_kind(self):
        self.act('object-quick-create',kind='PROPERTY',name='Xuân Mai');xm=self.pid('PROPERTY','Xuân Mai');n=len(self.store.state()['profiles'])
        txt="05/06/2023\tA\tFT1\t30,000,000\t\t1\n"
        p=self.store.legacy_preview(dict(category=self.prop_cat,name='XUÂN MAI',text=txt));self.assertEqual((p['object']['exists'],p['object']['kind'],p['object']['profile']),(True,'PROPERTY',xm))
        self.act('legacy-import',category=self.prop_cat,name='XUÂN MAI',text=txt);self.assertEqual(len(self.store.state()['profiles']),n)                 # không tạo hồ sơ mới
        self.assertIn(xm,self.members());self.assertEqual(self.members()[xm]['totals']['transactions'],1)

    def test_duplicate_warning_and_merge_object_into_property(self):
        self.make_dup();m=self.members();self.assertEqual((set(m),[d['kind'] for d in m[self.xo]['duplicate_of']],[d['kind'] for d in m[self.xm]['duplicate_of']]),({self.xm,self.xo},['PROPERTY'],['OBJECT']))
        self.act('legacy-import',category=self.prop_cat,profile=self.xo,text="05/06/2023\tA\tFT1\t30,000,000\t\t1\n07/06/2023\tB\tFT2\t\t10,000,000\t1\n")
        self.classify(['K1'],[dict(category='investment',node=self.prop_cat,profile=self.xo)])                                                          # giao dịch ngân hàng gắn bản trùng
        before=self.members()[self.xo]['totals'];self.assertEqual(before,{'in':'10000000','out':'35000000','transactions':3})
        alloc_before=self.tx('K1')['allocations'];rep0=self.store.report(self.store.state(),self.store.state()['accounts'][0]['id'])
        self.err('category-object-merge',**{'from':self.xo,'into':self.xo,'reason':'x'});self.err('category-object-merge',**{'from':self.xo,'into':self.xm,'reason':''})
        self.err('category-object-merge',**{'from':self.xm,'into':self.xo,'reason':'x'})                                                                 # nguồn phải là loại "đối tượng"
        self.act('category-object-merge',**{'from':self.xo,'into':self.xm,'reason':'Trùng với BĐS Xuân Mai'})
        m=self.members();self.assertEqual(set(m),{self.xm});self.assertEqual((m[self.xm]['totals'],m[self.xm]['duplicate_of']),(before,[]))             # tổng gộp đủ, không còn cảnh báo
        profile=next(p for p in self.store.state()['profiles'] if p['id']==self.xo);self.assertEqual(profile['merged_into'],self.xm)
        self.assertEqual(self.tx('K1')['allocations'],alloc_before);self.assertEqual(self.store.report(self.store.state(),self.store.state()['accounts'][0]['id']),rep0)  # phân loại gốc và báo cáo không đổi
        h=self.store.category_history(dict(category=self.prop_cat,object=self.xm));self.assertEqual(({r['reference'] for r in h['rows']},len(h['rows'])),({'K1','FT1','FT2'},3))
        rec=self.store.view()['categories']['merges'][0];self.assertEqual((rec['from_name'],rec['to_name'],rec['reason']),('Xuân Mai','Xuân Mai','Trùng với BĐS Xuân Mai'))
        self.err('classify',ids=[self.tx('K2')['id']],parts=[dict(category='investment',node=self.prop_cat,profile=self.xo)])                           # không dùng được bản đã gộp
        self.err('category-object-merge',**{'from':self.xo,'into':self.xm,'reason':'lần hai'});self.act('category-object-add',category=self.prop_cat,name='Xuân Mai 3')

    def test_merge_where_target_not_member_moves_membership_and_read_only(self):
        self.act('category-object-add',category=self.prop_cat,name='Mảnh A');a=self.pid('OBJECT','Mảnh A')
        self.act('object-quick-create',kind='PROPERTY',name='Mảnh A bản chính');b=self.pid('PROPERTY','Mảnh A bản chính')
        self.act('category-object-merge',**{'from':a,'into':b,'reason':'Gộp'});self.assertEqual(set(self.members()),{b})                                   # đích chưa là thành viên: thành viên chuyển sang đích
        n=len(self.store.events());self.store.view();self.assertEqual(len(self.store.events()),n)

for name in [n for n in dir(base.P18Acceptance) if n.startswith('test_')]:setattr(P31Acceptance,name,None)
if __name__=='__main__':unittest.main()
