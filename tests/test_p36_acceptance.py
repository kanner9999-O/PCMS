import unittest
import test_p35_acceptance as base

class P36Acceptance(base.P35Acceptance):
    """Dọn danh mục con chưa dùng (spec 034) trên dữ liệu P18."""
    def cands(self):return {c['path'] for c in self.store.view()['categories']['cleanup']}
    def test_cleanup_lists_only_unused_children_leaf_first_and_deletes(self):
        for name,parent in (('Rỗng 1','expense'),('Rỗng 2','expense'),('Dùng','expense')):self.act('category-create',name=name,description='',parent=parent)
        self.act('category-create',name='Cha rỗng',description='',parent='expense');cr=self.nodes()['Cha rỗng']['id'];self.act('category-create',name='Con rỗng',description='',parent=cr)
        self.act('category-create',name='Có đối tượng',description='',parent='expense');co=self.nodes()['Có đối tượng']['id'];self.make('Đối tượng X','OBJECT',category=co)
        self.act('category-create',name='Gốc tự tạo',type='expense');self.classify(['X1'],[dict(category='expense',node=self.nodes()['Dùng']['id'])])
        c=self.cands();self.assertEqual({'Chi tiêu › Rỗng 1','Chi tiêu › Rỗng 2','Chi tiêu › Cha rỗng','Chi tiêu › Cha rỗng › Con rỗng'},{x for x in c if 'Rỗng' in x or 'rỗng' in x})
        self.assertNotIn('Chi tiêu › Dùng',c);self.assertNotIn('Chi tiêu › Có đối tượng',c);self.assertFalse(any('Gốc tự tạo' in x for x in c))                  # gốc tự tạo không bị xóa
        rep0=self.store.report(self.store.state(),self.account);roots0=[r['totals'] for r in self.store.view()['categories']['roots']]
        ids=[x['id'] for x in self.store.view()['categories']['cleanup']]
        self.err('category-cleanup',ids=ids);self.err('category-cleanup',confirm=True,ids=ids[:-1]);self.err('category-cleanup',confirm=True,ids=[])
        self.act('category-cleanup',confirm=True,ids=ids)
        left={n['name'] for n in self.store.state()['categories']};self.assertTrue({'Dùng','Có đối tượng','Gốc tự tạo'}<=left);self.assertFalse(left&{'Rỗng 1','Rỗng 2','Cha rỗng','Con rỗng'})
        self.assertEqual(len(self.store.state()['category_deleted']),len(ids));self.assertEqual(self.store.report(self.store.state(),self.account),rep0)
        self.assertEqual([r['totals'] for r in self.store.view()['categories']['roots']],roots0);self.assertEqual(self.store.view()['categories']['cleanup'],[]);self.err('category-cleanup',confirm=True,ids=ids)

    def test_used_loan_group_and_legacy_categories_are_kept(self):
        c=self.cands();self.assertNotIn('Gốc vay › Kết',c);self.assertEqual({x for x in c if 'Loans' in x},{'Gốc vay › Loans','Gốc vay › Loans › Long debt'})   # đã có phân loại → giữ; chưa dùng → dọn (cha sau con)
        self.act('category-create',name='Lịch sử',description='',parent='investment');h=self.nodes()['Lịch sử']['id']
        self.act('legacy-import',account=self.account,category=h,name='Xuân Mai X',text="05/06/2023\tA\tFT1\t30,000,000\t\t1\n");self.assertNotIn('Đầu tư BĐS › Lịch sử',self.cands())   # có nhập lịch sử cũ → giữ
        self.act('object-create',name='Người vay',type='PERSON',category=self.nodes()['Long debt']['id']);self.assertFalse({x for x in self.cands() if 'Loans' in x})   # có đối tượng → giữ cả cha

if __name__=='__main__':unittest.main()
