import copy
import unittest
import test_p18_acceptance as base
from pcms.core import ValidationError

class CategoryDeleteGuard(base.P18Acceptance):
    """Spec 044 (R201, A62): xóa hẳn danh mục chỉ khi chưa từng dùng ở bất kỳ đâu; nút "Xóa hẳn" và lệnh xóa cùng một quy tắc."""
    def node(self,name,parent='expense'):
        self.act('category-create',name=name,description='',parent=parent);return self.nodes()[name]['id']
    def mkp(self,name,cat):
        self.act('object-create',name=name,type='PERSON',category=cat);return next(p['id'] for p in self.store.state()['profiles'] if p['name']==name)
    def deletable(self,name):return next(n for n in self.store.view()['categories']['nodes'] if n['name']==name)['deletable']
    def blocked(self,name,cid,fragment):
        """Màn và lệnh đồng nhất (SC-003): không có nút thì lệnh cũng bị từ chối, với lý do có số lượng (SC-004)."""
        self.assertFalse(self.deletable(name))
        with self.assertRaises(ValidationError) as c:self.act('category-delete',category=cid,reason='thử')
        self.assertIn(fragment,str(c.exception));self.assertIn(cid,{n['id'] for n in self.store.state()['categories']});return str(c.exception)
    def legacy(self,cat,pid,ref='FT9'):
        self.act('legacy-import',category=cat,profile=pid,account=self.account,text=f"05/06/2023\tTiền mặt\t{ref}\t100,000\t\t1\n")
        return self.store.state()['legacy_batches'][-1],self.store.state()['legacy_entries'][-1]

    # ---- US1: lịch sử cũ ------------------------------------------------------------------
    def test_legacy_rows_block_delete_but_archive_still_works(self):
        c=self.node('Cũ');pid=self.mkp('Mỹ',c);self.legacy(c,pid);self.act('category-object-remove',category=c,profile=pid,reason='gỡ để thử riêng lịch sử cũ')
        totals=copy.deepcopy(self.nodes()['Cũ']['totals'])
        self.blocked('Cũ',c,'1 dòng lịch sử cũ')
        self.act('category-archive',category=c,reason='Không dùng nữa');self.assertEqual((self.nodes()['Cũ']['status'],self.nodes()['Cũ']['totals']),('ARCHIVED',totals))
        self.blocked('Cũ',c,'1 dòng lịch sử cũ')                                                      # đã lưu trữ: cùng quy tắc

    def test_void_batch_and_rows_moved_away_still_block(self):
        c=self.node('Đợt hủy');pid=self.mkp('Tươi',c);b,_=self.legacy(c,pid);self.act('legacy-void',batch=b['id'],reason='Dán nhầm')
        self.act('category-object-remove',category=c,profile=pid,reason='x');self.blocked('Đợt hủy',c,'dòng lịch sử cũ')
        c1=self.node('Nguồn');c2=self.node('Đích');p2=self.mkp('Lan',c1);self.act('category-object-add',category=c2,profile=p2);_,e=self.legacy(c1,p2,'FT8')
        p=self.store.reclassify_preview(dict(transaction=e['id'],part=0,category=c2,profile=p2));self.act('transaction-reclassify',transaction=e['id'],part=0,category=c2,profile=p2,review_token=p['review_token'],reason='Nhầm danh mục')
        self.act('category-object-remove',category=c1,profile=p2,reason='x');self.blocked('Nguồn',c1,'từng thuộc')   # dòng đã sửa đi vẫn giữ dấu vết danh mục cũ

    # ---- US2: đối tượng thành viên ---------------------------------------------------------------
    def test_active_members_then_member_history_block_delete(self):
        c=self.node('Hot');a=self.mkp('An',c);self.mkp('Bình',c)
        self.blocked('Hot',c,'2 đối tượng thành viên')
        for pid in (a,next(p['id'] for p in self.store.state()['profiles'] if p['name']=='Bình')):self.act('category-object-remove',category=c,profile=pid,reason='x')
        self.blocked('Hot',c,'từng có đối tượng thành viên')
        s1=self.node('Từ');s2=self.node('Tới');m=self.mkp('Minh',s1);self.act('category-object-move',profile=m,**{'from':s1,'to':s2},reason='chuyển')
        self.blocked('Từ',s1,'từng có đối tượng thành viên')

    # ---- US3: danh mục chưa dùng ---------------------------------------------------------------------
    def test_unused_category_still_deletable_active_or_archived(self):
        c=self.node('Trống');self.assertTrue(self.deletable('Trống'));self.act('category-delete',category=c,reason='Tạo nhầm')
        self.assertEqual(self.store.state()['category_deleted'][-1]['name'],'Trống')
        c=self.node('Trống 2');self.act('category-archive',category=c,reason='x');self.assertTrue(self.deletable('Trống 2'));self.act('category-delete',category=c,reason='Tạo nhầm')

    def test_screen_flag_matches_command_for_every_node(self):
        c=self.node('Cũ');pid=self.mkp('Mỹ',c);self.legacy(c,pid);self.node('Trống')
        for n in self.store.view()['categories']['nodes']:
            st=self.store.state()
            try:self.store.change(copy.deepcopy(st),'category-delete',dict(category=n['id'],reason='thử'));ok=True
            except ValidationError:ok=False
            self.assertEqual(n['deletable'],ok,n['path'])

if __name__=='__main__':unittest.main()
