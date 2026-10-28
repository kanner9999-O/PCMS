import copy
import unittest
from decimal import Decimal
import test_p18_acceptance as base
from pcms.core import ValidationError

class CategoryArchiveTabs(base.P18Acceptance):
    """Spec 045 (R202, A63; sửa R201 từ review spec 044): dấu vết khi xóa đối tượng, thông báo chặn xóa, phần tổng thuộc danh mục lưu trữ, dữ liệu cho tab Đã lưu trữ."""
    def node(self,name,parent='expense'):
        self.act('category-create',name=name,description='',parent=parent);return self.nodes()[name]['id']
    def view_node(self,cid,v=None):return next(n for n in (v or self.store.view()['categories'])['nodes'] if n['id']==cid)
    def obj(self,cat,name):
        self.act('category-object-add',category=cat,name=name);return next(p['id'] for p in self.store.state()['profiles'] if p['name']==name)
    def delete_result(self,cid):
        try:self.store.change(copy.deepcopy(self.store.state()),'category-delete',dict(category=cid,reason='thử'));return None
        except ValidationError as e:return str(e)
    def assert_used(self,cid):
        """Nút, lệnh xóa và dọn danh mục đồng nhất (SC-004)."""
        n=self.view_node(cid);why=self.delete_result(cid)
        self.assertFalse(n['deletable']);self.assertIsNotNone(why);self.assertEqual(n['delete_block'],why)
        if 'danh mục con' not in why:self.assertNotIn(cid,{x['id'] for x in self.store.view()['categories']['cleanup']})   # cha có con chưa dùng: dọn xóa con trước rồi cha (spec 034)
        return why
    def assert_unused(self,cid):
        n=self.view_node(cid);self.assertTrue(n['deletable']);self.assertIsNone(n['delete_block']);self.assertIsNone(self.delete_result(cid))
        self.assertIn(cid,{x['id'] for x in self.store.view()['categories']['cleanup']})
    def out_tx(self):return next(t for t in self.store.state()['transactions'] if Decimal(t['signed_amount'])<0 and not t['allocations'])

    # ---- US3: xóa đối tượng giữ dấu vết (sửa P2 review 044) ---------------------------------------
    def test_deleting_object_keeps_membership_trace_both_paths(self):
        for action in ('object-delete','category-object-delete'):
            c=self.node('Danh mục '+action);pid=self.obj(c,'Đối tượng '+action);self.assert_used(c)
            self.act(action,profile=pid,reason='Tạo nhầm')                                              # đối tượng chưa dùng vẫn xóa được
            rec=self.store.state()['object_deleted'][-1];self.assertEqual((rec['id'],[m['category'] for m in rec['memberships']]),(pid,[c]))
            self.assertIn('từng có đối tượng thành viên',self.assert_used(c))

    def test_remove_then_delete_object_still_blocks_category(self):
        c=self.node('Gỡ trước');pid=self.obj(c,'Tạm');self.act('category-object-remove',category=c,profile=pid,reason='gỡ')
        self.act('object-delete',profile=pid,reason='Tạo nhầm');self.assertEqual(self.store.state()['object_deleted'][-1]['memberships'][0]['status'],'REMOVED')
        self.assert_used(c)
        s1=self.node('Từ');s2=self.node('Tới');m=self.obj(s1,'Chuyển');self.act('category-object-move',profile=m,**{'from':s1,'to':s2},reason='chuyển')
        self.err('object-delete',profile=m,reason='x');self.assert_used(s1)                                  # đối tượng đã chuyển là đã dùng (quy tắc sẵn có)
        self.assert_unused(self.node('Chưa dùng'))

    # ---- US4: thông báo -------------------------------------------------------------------------------------
    def test_block_messages_point_to_archive_not_to_useless_steps(self):
        c=self.node('Có thành viên');self.obj(c,'A');self.obj(c,'B');why=self.assert_used(c)
        self.assertIn('2 đối tượng thành viên',why);self.assertIn('Lưu trữ để ẩn khỏi danh sách đang sử dụng',why);self.assertNotIn('gỡ hoặc chuyển',why.lower())
        self.act('category-archive',category=c,reason='Thừa');why=self.assert_used(c);self.assertIn('Giữ lưu trữ hoặc khôi phục',why);self.assertNotIn('Lưu trữ để ẩn',why)
        p=self.node('Cha');self.node('Con',parent=p);self.assertIn('danh mục con',self.assert_used(p))
        for n in self.store.view()['categories']['nodes']:self.assertNotIn('gỡ hoặc chuyển',(n['delete_block'] or '').lower())

    # ---- US1: phần tổng thuộc danh mục lưu trữ ---------------------------------------------------------------
    def test_archived_share_counts_transaction_once_and_totals_unchanged(self):
        a=self.node('Lưu A');b=self.node('Lưu B');t=self.out_tx();amt=abs(Decimal(t['signed_amount']));half=amt/2
        self.act('classify',ids=[t['id']],parts=[dict(category='expense',node=a,amount=str(half)),dict(category='expense',node=b,amount=str(amt-half))])
        root0=copy.deepcopy(next(r for r in self.store.view()['categories']['roots'] if r['key']=='expense'));self.assertIsNone(root0['archived_share'])
        self.act('category-archive',category=a,reason='Thừa');self.act('category-archive',category=b,reason='Thừa')
        root=next(r for r in self.store.view()['categories']['roots'] if r['key']=='expense')
        self.assertEqual(root['totals'],root0['totals']);sh=root['archived_share'];self.assertEqual((sh['transactions'],sh['parts'],Decimal(sh['out'])),(1,2,amt))
        d=t['date'];pv=self.store.category_view(self.store.state(),d,d);self.assertEqual(next(r for r in pv['roots'] if r['key']=='expense')['archived_share']['transactions'],1)   # theo kỳ
        far=self.store.category_view(self.store.state(),'1990-01-01','1990-01-02');self.assertIsNone(next(r for r in far['roots'] if r['key']=='expense')['archived_share'])
        self.act('category-restore',category=a);root2=next(r for r in self.store.view()['categories']['roots'] if r['key']=='expense')
        self.assertEqual((root2['totals'],root2['archived_share']['parts']),(root0['totals'],1))

    # ---- US2: dữ liệu tab Đã lưu trữ, không dây chuyền, không chọn được ----------------------------------------
    def test_archived_metadata_restore_block_and_no_cascade(self):
        p=self.node('Cha L');c=self.node('Con L',parent=p);self.assertIsNone(self.view_node(c)['archived_at'])
        self.err('category-archive',category=p,reason='x')                                                   # còn con hoạt động
        self.act('category-archive',category=c,reason='Không dùng');self.act('category-archive',category=p,reason='Gom lại')
        n=self.view_node(c);self.assertEqual(n['archive_reason'],'Không dùng');self.assertTrue(n['archived_at']);self.assertIn('Cha L',n['restore_block'])
        self.assertIsNone(self.view_node(p)['restore_block']);self.err('category-restore',category=c)
        self.err('category-create',name='Mới',description='',parent=p)
        q=self.node('Khác');self.err('category-edit',category=q,parent=p,reason='x')
        self.err('classify',ids=[self.out_tx()['id']],parts=[dict(category='expense',node=c)])
        self.err('category-object-add',category=c,name='Ai đó')
        self.err('legacy-import',category=c,name='Ai đó',account=self.account,text="05/06/2023\tX\tFT9\t1,000\t\t1\n")
        self.act('category-restore',category=p);self.assertEqual(self.view_node(p)['status'],'ACTIVE');self.assertEqual(self.view_node(c)['status'],'ARCHIVED')   # không khôi phục dây chuyền

if __name__=='__main__':unittest.main()
