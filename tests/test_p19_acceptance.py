import copy
import unittest
from decimal import Decimal
import test_p18_acceptance as base

def D_(x):return Decimal(str(x))

class P19Acceptance(base.P18Acceptance):
    """Dùng lại dữ liệu P18 (hai khoản vay của Kết); kiểm định dạng lịch sử chuẩn."""
    def test_category_history_rows_standard_and_totals(self):
        self.act('category-create',name='Ăn',description='',parent='expense');eat=self.nodes()['Ăn']['id']
        self.classify(['X1'],[dict(category='expense',node=eat)])
        h=self.store.category_history(dict(category='principal'))
        self.assertEqual([r['reference'] for r in h['rows']],['K3','K2','K1'])                       # mới nhất trước
        for r in h['rows']:
            self.assertTrue(r['label'] and isinstance(r['source_count'],int) and r['source_count']>=1);self.assertFalse(r['split'])
            self.assertEqual(D_(r['tx_amount']),D_(r['amount']))
        self.assertEqual(h['rows'][0]['label'],'Gốc vay · Kết 10tr')
        inc=sum(D_(r['amount']) for r in h['rows'] if r['direction']=='IN');out=sum(D_(r['amount']) for r in h['rows'] if r['direction']=='OUT')
        self.assertEqual((inc,out,len(h['rows'])),(D_(h['totals']['in']),D_(h['totals']['out']),h['totals']['parts']))
        e=self.store.category_history(dict(category='expense'));self.assertEqual((e['rows'][0]['label'],len(e['rows'])),('Chi tiêu › Ăn',1))

    def test_split_and_refund_labels(self):
        self.classify(['S1'],[dict(category='expense',amount='5000000'),dict(category='income',amount='15000000')])
        h=self.store.category_history(dict(category='income'));r=h['rows'][0];self.assertEqual((r['split'],D_(r['amount']),D_(r['tx_amount'])),(True,15000000,20000000))
        e=self.store.category_history(dict(category='expense'));self.assertEqual(e['rows'][0]['label'],'Hoàn chi tiêu')

    def test_realty_history_labels_and_order(self):
        self.act('object-quick-create',kind='PROPERTY',name='Đất A');a=next(p['id'] for p in self.store.state()['profiles'] if p['name']=='Đất A')
        self.classify(['K1'],[dict(category='investment',profile=a)]);self.classify(['K2'],[dict(category='expense',profile=a)]);self.classify(['S1'],[dict(category='investment',profile=a)])
        h=self.store.realty_history(dict(property=a));self.assertEqual([r['reference'] for r in h['rows']],['S1','K2','K1'])
        self.assertEqual([r['label'] for r in h['rows']],['Vốn nhận lại','Chi phí','Vốn đã thanh toán']);self.assertTrue(all(r['source_count']>=1 for r in h['rows']))
        self.assertEqual((D_(h['capital']['paid']),D_(h['capital']['received']),D_(h['costs']['spent'])),(5000000,20000000,10000000))

    def test_interest_follows_loan_but_type_report_unchanged(self):
        v0=self.store.view();by0={r['key']:r['totals'] for r in v0['categories']['roots']};rep0=self.store.report(self.store.state(),self.account)['totals']
        self.act('loan-regroup',profile=self.l10,node=self.nodes()['Long debt']['id'],effective_date='2026-10-01',reason='x')
        v=self.store.view();by={r['key']:r['totals'] for r in v['categories']['roots']}
        self.assertEqual((D_(by['interest']['in']),by['interest']['transactions']),(0,0));self.assertEqual(D_(by0['interest']['in']),200000)
        self.assertEqual(D_(by['principal']['in'])+D_(by['interest']['in']),D_(by0['principal']['in'])+D_(by0['interest']['in']))      # tiền không mất, chỉ đổi chỗ
        self.assertEqual(self.store.report(self.store.state(),self.account)['totals'],rep0)                                            # báo cáo theo loại không đổi
        h=self.store.category_history(dict(category=self.nodes()['Long debt']['id']));self.assertEqual({r['reference']:r['label'] for r in h['rows']}['K4'],'Lãi vay · Kết 10tr')
        self.assertEqual(v['debts'],v0['debts'])

    def test_read_only(self):
        n=len(self.store.events());self.store.category_history(dict(category='principal'));self.assertEqual(len(self.store.events()),n)

for name in [n for n in dir(base.P18Acceptance) if n.startswith('test_')]:setattr(P19Acceptance,name,None)
if __name__=='__main__':unittest.main()
