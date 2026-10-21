import unittest
import test_p37_acceptance as base

TXT="05/06/2023\tNGUYEN BA DUNG chuyen tien a tuan uong ruou\tFT1\t10,000,000\t\t1\tTiền môi giới\n07/06/2023\tB\tFT2\t\t4,000,000\t1\t\n"
MAP=['date','description','reference','out','in','balance','note']

class P38Acceptance(base.P37Acceptance):
    """Ghi chú giao dịch: nhập từ cột migrate, sửa trên dòng lịch sử cũ và ngân hàng (spec 038)."""
    def setUp(self):
        super().setUp();self.act('category-create',name='Property N',type='investment');self.cat=self.nodes()['Property N']['id']
    def rows(self,key=None,obj=None):
        return self.store.category_history(dict(category=key or self.cat))['rows']

    def test_note_column_is_imported_and_previewed(self):
        p=self.store.legacy_preview(dict(category=self.cat,name='Đồng Cạn',text=TXT,mapping=MAP));self.assertEqual([r['note'] for r in p['rows']],['Tiền môi giới',''])
        self.act('legacy-import',category=self.cat,name='Đồng Cạn',text=TXT,mapping=MAP)
        rows={r['reference']:r for r in self.rows()};self.assertEqual((rows['FT1']['note'],rows['FT2']['note']),('Tiền môi giới',''));self.assertTrue(rows['FT1']['legacy'])
        d=self.store.legacy_preview(dict(category=self.cat,name='X',text=TXT));self.assertTrue(all(r['note']=='' for r in d['rows']))        # mặc định cột G bỏ qua
        self.err('legacy-import',category=self.cat,name='Y',text=TXT,mapping=['date','description','reference','out','in','balance','note','note'])   # hai cột note

    def test_edit_note_on_legacy_row_keeps_source_and_money(self):
        self.act('legacy-import',category=self.cat,name='Đồng Cạn',text=TXT,mapping=MAP)
        e=next(x for x in self.store.state()['legacy_entries'] if x['reference']=='FT2');tot0=self.rows()
        self.act('transaction-note',transaction=e['id'],note='Hoàn môi giới',voucher='BL-9')
        r=next(x for x in self.rows() if x['reference']=='FT2');self.assertEqual((r['note'],r['voucher'],r['description']),('Hoàn môi giới','BL-9','B'))
        e=next(x for x in self.store.state()['legacy_entries'] if x['reference']=='FT2');self.assertEqual(len(e['note_history']),1)
        self.assertEqual([(x['amount'],x['direction']) for x in self.rows()],[(x['amount'],x['direction']) for x in tot0])
        h=self.store.category_history(dict(category='*',object=next(p['id'] for p in self.store.state()['profiles'] if p['name']=='Đồng Cạn')));self.assertEqual({x['note'] for x in h['rows']},{'Tiền môi giới','Hoàn môi giới'})
        self.err('transaction-note',transaction='nope',note='x')

    def test_note_on_bank_row_after_approval_and_required_category(self):
        t=self.tx('S1');self.act('transaction-note',transaction=t['id'],note='Lương tháng 9');self.assertEqual(self.tx('S1')['note'],'Lương tháng 9')
        self.act('category-template',template='no-voucher');nv=self.nodes()['Chi khác không chứng từ']['id']
        self.act('classify',ids=[self.tx('X1')['id']],parts=[dict(category='expense',node=nv)],note='Chi giấy tờ')
        self.err('transaction-note',transaction=self.tx('X1')['id'],note='')                                              # danh mục yêu cầu ghi chú
        self.act('legacy-import',category=nv,name='Cũ NV',text=TXT,mapping=MAP)
        e=next(x for x in self.store.state()['legacy_entries'] if x['reference']=='FT2');self.err('transaction-note',transaction=e['id'],note='')   # dòng lịch sử cũ cũng bị ràng buộc
if __name__=='__main__':unittest.main()
