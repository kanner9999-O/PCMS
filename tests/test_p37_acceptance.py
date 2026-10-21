import unittest
from decimal import Decimal
import test_p35_acceptance as base

TXT="05/06/2023\tA\tFT1\t30,000,000\t\t1\n"

class P37Acceptance(base.P35Acceptance):
    """Migrate lịch sử cũ: không ghi nhầm vào đối tượng có sẵn khi người dùng nhập tên đối tượng mới (spec 037)."""
    def test_selected_profile_with_different_name_is_rejected_new_name_creates(self):
        self.act('category-create',name='Property',type='investment');cat=self.nodes()['Property']['id']
        xm=self.make('Xuân Mai','PROPERTY',category=cat)
        self.err('legacy-import',category=cat,profile=xm,name='Đồng Cạn',text=TXT)                                         # chọn Xuân Mai nhưng gõ Đồng Cạn: chặn, không ghi nhầm
        with self.assertRaises(Exception):self.store.legacy_preview(dict(category=cat,profile=xm,name='Đồng Cạn',text=TXT))
        self.assertEqual(self.store.legacy_preview(dict(category=cat,profile=xm,name='xuân  mai',text=TXT))['object']['name'],'Xuân Mai')      # cùng tên: hợp lệ
        self.act('legacy-import',category=cat,name='Đồng Cạn',text=TXT)                                                    # chỉ nhập tên: tạo đối tượng mới
        self.assertIn('Đồng Cạn',self.objs());self.assertEqual(self.objs()['Đồng Cạn']['totals']['transactions'],1);self.assertEqual(self.objs()['Xuân Mai']['totals']['transactions'],0)
        self.assertIn(cat,[c['category'] for c in self.objs()['Đồng Cạn']['categories']])
if __name__=='__main__':unittest.main()
