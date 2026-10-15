import unittest
from decimal import Decimal
import test_p33_acceptance as base

def D_(x):return Decimal(str(x))

class P34Acceptance(base.P33Acceptance):
    """Nhóm mặc định (spec 032): chỉ nhãn tổ chức; không đổi phân loại, tổng, báo cáo."""
    def cat(self):return self.store.view()['categories']

    def test_every_category_is_default_group_and_totals_unchanged(self):
        c0=self.cat();rep0=self.store.report(self.store.state(),self.account)
        self.assertTrue(all(r['group']=='default' for r in c0['roots']) and all(n['group']=='default' for n in c0['nodes']))
        self.assertEqual(c0['groups'],{'default':'Nhóm mặc định'});self.assertIn('tổng hợp',c0['group_note'])
        for n in self.store.state()['categories']:n.pop('group',None)                                                       # dữ liệu cũ không có trường: vẫn là mặc định
        self.act('category-create',name='Mới',description='',parent='expense');self.act('category-create',name='GốcMới',type='expense')
        nodes={n['name']:n for n in self.cat()['nodes']};self.assertEqual((nodes['Mới']['group'],nodes['GốcMới']['group'],nodes['Kết']['group']),('default',)*3)
        self.assertTrue(all(n.get('group')=='default' for n in self.store.state()['categories'] if n['name'] in {'Mới','GốcMới'}))
        c1=self.cat()
        for a,b in zip(c0['roots'],c1['roots']):self.assertEqual(a['totals'],b['totals'])
        self.assertEqual(self.store.report(self.store.state(),self.account),rep0)

    def test_business_in_expense_category_allowed_with_warning(self):
        self.act('category-create',name='Long Debt X',type='expense');ld=self.nodes()['Long Debt X']['id']
        my=self.person_obj('Mỹ',ld);self.act('business-set',category=ld,profile=my,type='LOAN_LENT',effective_date='2026-09-01')
        self.classify(['K1'],[dict(category='expense',node=ld,profile=my)])
        row=next(x for x in self.biz()['loans'] if x['profile']==my);self.assertEqual((row['warn'],D_(row['increase']),D_(row['balance'])),(['IN_EXPENSE_REPORT'],5000000,5000000))
        self.assertEqual(row['group'],'default')
        self.act('category-create',name='Thu X',type='income');ti=self.nodes()['Thu X']['id'];o2=self.person_obj('B',ti)
        self.act('business-set',category=ti,profile=o2,type='LOAN_BORROWED',effective_date='2026-09-01')
        self.assertEqual(next(x for x in self.biz()['loans'] if x['profile']==o2)['warn'],['IN_INCOME_REPORT'])
        self.assertEqual(self.biz()['loans'][0]['warn'] if self.biz()['loans'][0]['category']=='principal' else [],[])
        # chặn mâu thuẫn thật vẫn giữ
        self.act('business-migrate',confirm=True);self.err('business-set',category='principal',profile=self.l10,type='LOAN_BORROWED',effective_date='2026-09-01',reason='x')
        self.err('business-set',category=ld,profile=my,type='LOAN_BORROWED',effective_date='2026-09-05',reason='đổi')           # đã có giao dịch

if __name__=='__main__':unittest.main()
