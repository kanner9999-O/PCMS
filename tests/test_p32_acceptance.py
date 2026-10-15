import copy
import unittest
from decimal import Decimal
from pcms.core import ValidationError
import test_p13_acceptance as base

D_=base.D_

class P32Acceptance(base.P13Acceptance):
    """Dùng sao kê BĐS của P13 (Đất A: 200/150/250 triệu; công chứng 5 triệu; hoàn 1 triệu; nhận lại cọc 10 triệu; lương 20 triệu)."""
    def nodes(self):return {n['name']:n for n in self.store.view()['categories']['nodes']}
    def mk(self):
        self.act('category-template',template='realty-acquisition');self.act('category-template',template='no-voucher')
        a=self.setup_land();self.cc=self.nodes()['Công chứng']['id'];self.nv=self.nodes()['Chi khác không chứng từ']['id'];return a

    def test_templates_flags_and_inheritance(self):
        self.act('category-template',template='realty-acquisition');n=self.nodes()
        self.assertEqual({k for k in n if n[k]['parent']==n['Chi phí mua BĐS (vốn hóa)']['id']},{'Công chứng','Thuế trước bạ','Môi giới','Khác'})
        self.assertTrue(all(n[k]['capitalize'] for k in ('Chi phí mua BĐS (vốn hóa)','Công chứng','Khác')));self.assertFalse(n['Công chứng']['note_required'])
        self.assertEqual(n['Chi phí mua BĐS (vốn hóa)']['root'],'expense');self.err('category-template',template='realty-acquisition');self.err('category-template',template='nope')
        self.act('category-template',template='no-voucher');n=self.nodes();self.assertEqual((n['Chi khác không chứng từ']['note_required'],n['Chi khác không chứng từ']['capitalize']),(True,False))
        t=self.store.view()['categories']['templates'];self.assertTrue(all(x['exists'] for x in t.values()))

    def test_capitalized_cost_basis_gap_and_assets(self):
        a=self.mk();self.classify(['D-BACK'],[dict(category='investment',profile=a)])
        self.classify(['D-COST'],[dict(category='expense',node=self.cc,profile=a)]);self.classify(['D-REF'],[dict(category='expense',profile=a)])                 # hoàn chi thường (chi phí vận hành)
        p=self.prop('Đất A');c=p['capital'];self.assertEqual((D_(c['net']),D_(c['acquisition']['paid']),D_(c['acquisition']['net']),D_(c['basis'])),(590000000,5000000,5000000,595000000))
        self.assertEqual((D_(p['costs']['spent']),D_(p['costs']['refunded']),D_(p['costs']['net'])),(0,1000000,-1000000))                                         # không đếm kép chi phí vốn hóa
        self.act('realty-valuation',property=a,value='900000000',date='2026-10-01',source='Báo giá');self.assertEqual(D_(self.prop('Đất A')['gap']['amount']),305000000)
        self.classify(['D-REF'],[dict(category='expense',node=self.cc,profile=a)]);p=self.prop('Đất A');self.assertEqual((D_(p['capital']['acquisition']['net']),D_(p['capital']['basis']),D_(p['costs']['spent'])),(4000000,594000000,0))   # hoàn chi phí mua vốn hóa trừ
        self.assertEqual(D_(self.prop('Đất A')['gap']['amount']),306000000)
        h=self.store.realty_history(dict(property=a));self.assertEqual(sorted(r['kind'] for r in h['rows'] if r['kind']=='ACQUISITION'),['ACQUISITION','ACQUISITION']);self.assertEqual(D_(h['capital']['basis']),594000000)
        self.assertIn('vốn hóa',[r['label'] for r in h['rows'] if r['kind']=='ACQUISITION'][0])

    def test_assets_use_cost_basis_with_capitalized_costs(self):
        a=self.mk();self.classify(['D-COST'],[dict(category='expense',node=self.cc,profile=a)])
        g=next(x for x in self.store.view()['assets']['currencies']['VND']['assets']['groups'] if x['key']=='realty');self.assertEqual(D_(g['value']),605000000);self.assertIn('vốn hóa',g['basis'])  # 600 + 5 triệu

    def test_unmarked_expense_unchanged_and_not_capitalized(self):
        a=self.setup_land();self.classify(['D-COST'],[dict(category='expense',profile=a)]);p=self.prop('Đất A')
        self.assertEqual((D_(p['capital']['basis']),D_(p['capital']['acquisition']['net']),D_(p['costs']['spent'])),(600000000,0,5000000))                          # dữ liệu cũ: chi phí thường, giá gốc không đổi

    def test_no_voucher_requires_note_and_notes_everywhere(self):
        a=self.mk();ids=[self.tx('D-COST')['id']]
        self.err('classify',ids=ids,parts=[dict(category='expense',node=self.nv)])                                                                                       # thiếu ghi chú
        self.err('classify',ids=ids,parts=[dict(category='expense',node=self.nv)],note='   ')
        self.act('classify',ids=ids,parts=[dict(category='expense',node=self.nv)],note='Chi giấy tờ không hóa đơn',voucher='')
        t=self.tx('D-COST');self.assertEqual((t['note'],t['voucher'],len(t['note_history'])),('Chi giấy tờ không hóa đơn','',1))
        self.assertEqual(D_(self.prop('Đất A')['capital']['basis']),600000000)                                                                                          # không vốn hóa
        self.err('transaction-note',transaction=t['id'],note='');self.act('transaction-note',transaction=t['id'],note='Chi giấy tờ đợt 2',voucher='BL-01');t=self.tx('D-COST');self.assertEqual((t['note'],t['voucher'],len(t['note_history'])),('Chi giấy tờ đợt 2','BL-01',2))
        self.err('transaction-note',transaction='nope',note='x');self.err('transaction-note',transaction=t['id'])
        h=self.store.category_history(dict(category=self.nv));self.assertEqual((h['rows'][0]['note'],h['rows'][0]['voucher']),('Chi giấy tờ đợt 2','BL-01'))
        # ghi chú thường (không bắt buộc), áp cho nhiều dòng, bỏ trống thì không đổi
        self.act('classify',ids=[self.tx('D-1')['id'],self.tx('D-2')['id']],parts=[dict(category='investment',profile=a)],note='Đợt thanh toán đầu');self.assertEqual((self.tx('D-1')['note'],self.tx('D-2')['note']),('Đợt thanh toán đầu',)*2)
        self.act('classify',ids=[self.tx('D-1')['id']],parts=[dict(category='investment',profile=a)]);self.assertEqual(self.tx('D-1')['note'],'Đợt thanh toán đầu')
        rows=self.store.realty_history(dict(property=a))['rows'];self.assertEqual({r['reference']:r['note'] for r in rows}['D-1'],'Đợt thanh toán đầu')
        aid=self.store.state()['accounts'][0]['id'];ah=self.store.account_history(dict(account=aid,scope='all',limit=200));self.assertEqual(next(r for r in ah['rows'] if r['reference']=='D-COST')['voucher'],'BL-01')
        cr=self.store.classification_review(dict(account=aid));self.assertTrue(any(r['note']=='Chi giấy tờ đợt 2' for g in cr['groups'] for r in g['rows']))

    def test_note_edit_after_approval_needs_no_adjustment_and_snapshot_untouched(self):
        a=self.mk();self.classify(['D-1'],[dict(category='investment',profile=a)])
        aid=self.store.state()['accounts'][0]['id'];self.act('approve',account=aid,confirm_unknown=True,reason='')
        snaps=copy.deepcopy(self.store.state()['snapshots']);t=self.tx('D-1')
        self.err('classify',ids=[t['id']],parts=[dict(category='investment',profile=a)],note='cần phiên điều chỉnh')                                                   # sửa phân loại sau duyệt vẫn cần phiên điều chỉnh
        self.act('transaction-note',transaction=t['id'],note='Ghi chú sau chốt',voucher='HĐ-9');self.assertEqual(self.tx('D-1')['note'],'Ghi chú sau chốt');self.assertEqual(self.store.state()['snapshots'],snaps)

    def test_read_only(self):
        self.mk();n=len(self.store.events());self.store.view();self.assertEqual(len(self.store.events()),n)

for name in [n for n in dir(base.P13Acceptance) if n.startswith('test_')]:setattr(P32Acceptance,name,None)
if __name__=='__main__':unittest.main()
