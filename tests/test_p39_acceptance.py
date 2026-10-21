import unittest
from decimal import Decimal
import test_p18_acceptance as base

def D_(x):return Decimal(str(x))

class P39Acceptance(base.P18Acceptance):
    """Người là đối tượng của danh mục, khoản vay là mục con (spec 040) trên dữ liệu P18: Kết có Kết 5tr, Kết 10tr (Phải thu)."""
    def setUp(self):
        super().setUp()
        self.act('object-quick-create',kind='LOAN',party=self.person,name='Kết vay ngược');self.l3=next(p['id'] for p in self.store.state()['profiles'] if p['name']=='Kết vay ngược')
        self.act('loan-setup',profile=self.l3,direction='PAYABLE',opening='1000000',effective_date='2026-09-01',source='QA',reason='QA')
    def pairs(self):return {(p['category'],p['type']) for p in self.store.view()['business']['loans'] if p['profile']==self.person}

    def test_conflicting_directions_in_one_category_block_then_regroup_resolves(self):
        row=next(r for r in self.store.view()['business']['migration'] if r['name']=='Kết');self.assertEqual(row['action'],'CONFLICT');self.assertIn('Phải thu lẫn Phải trả',row['message'])
        self.err('business-migrate',confirm=True)                                                                          # chỉ có dòng xung đột: không có gì để làm
        self.act('category-create',name='Vay ngược',description='',parent='principal');g=self.nodes()['Vay ngược']['id']
        self.act('loan-regroup',profile=self.l3,node=g,effective_date='2026-09-02',reason='Tách chiều')
        rows={(r['name'],r['category']):r['action'] for r in self.store.view()['business']['migration'] if r['kind']=='PERSON'};self.assertEqual(set(rows.values()),{'ADD_AND_SET'});self.assertEqual(len(rows),2)
        self.act('business-migrate',confirm=True);self.assertEqual(self.pairs(),{('principal','LOAN_LENT'),(g,'LOAN_BORROWED')})
        lent=next(p for p in self.store.view()['business']['loans'] if p['type']=='LOAN_LENT');borrowed=next(p for p in self.store.view()['business']['loans'] if p['type']=='LOAN_BORROWED')
        self.assertEqual((sorted(k['name'] for k in lent['khoan']),D_(borrowed['balance'])),(['Kết 10tr','Kết 5tr'],1000000))          # hai sổ riêng, không bù trừ
        self.assertEqual(D_(self.store.view()['business']['totals']['payable']),1000000)

    def test_person_pair_rejects_wrong_direction_and_object_screen_lists_category_via_loans(self):
        self.act('category-create',name='Vay ngược',description='',parent='principal');g=self.nodes()['Vay ngược']['id'];self.act('loan-regroup',profile=self.l3,node=g,effective_date='2026-09-02',reason='x')
        self.act('category-object-add',category=g,profile=self.person)
        self.err('business-set',category=g,profile=self.person,type='LOAN_LENT',effective_date='2026-09-01')                   # khoản vay trong danh mục thiết lập Phải trả
        k=next(o for o in self.store.view()['objects']['rows'] if o['id']==self.person);self.assertTrue(any(c.get('via_loan') for c in k['categories']))
        self.act('business-set',category=g,profile=self.person,type='LOAN_BORROWED',effective_date='2026-09-01')
        self.err('category-object-remove',category=g,profile=self.person,reason='x');self.err('category-archive',category=g,reason='x')
if __name__=='__main__':unittest.main()
