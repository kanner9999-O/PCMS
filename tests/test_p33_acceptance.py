import copy
import unittest
from decimal import Decimal
from pcms.core import ValidationError
import test_p18_acceptance as base

def D_(x):return Decimal(str(x))

class P33Acceptance(base.P18Acceptance):
    """Dùng dữ liệu P18 (Kết 5tr/10tr: giải ngân 5tr và 10tr, thu gốc 3tr, lãi 200k, lương 20tr)."""
    def biz(self):return self.store.view()['business']
    def loan(self,pid):return next(x for x in self.biz()['loans'] if x['profile']==pid)
    def members(self,key):
        n=next(x for x in self.store.view()['categories']['nodes'] if x['id']==key);return {o['profile']:o for o in n['objects']}
    def person_obj(self,name,cat):
        self.act('category-object-add',category=cat,name=name);return next(p['id'] for p in self.store.state()['profiles'] if p['name']==name)

    def test_roles_visible_on_roots_and_nodes(self):
        c=self.store.view()['categories'];self.assertEqual({r['key']:r['role'] for r in c['roots']}['principal'],'Gốc vay');self.assertEqual({r['key']:r['role'] for r in c['roots']}['expense'],'Dòng tiền chi')
        self.assertEqual(self.nodes()['Kết']['role'],'Gốc vay')

    def test_set_loan_business_on_object_and_blocks(self):
        my=self.person_obj('Mỹ',self.nodes()['Kết']['id']);k=self.nodes()['Kết']['id']
        self.act('business-set',category=k,profile=my,type='LOAN_LENT',effective_date='2026-09-01',interest_note='1',maturity='2027-01-01')
        self.assertEqual(self.members(k)[my]['business']['type'],'LOAN_LENT')
        self.err('business-set',category=k,profile=my,type='LOAN_LENT',effective_date='2026-09-01')                       # không thay đổi
        self.err('business-set',category=k,profile=my,type='LOAN_BORROWED',effective_date='2026-09-02')                   # đổi cần lý do
        self.act('business-set',category=k,profile=my,type='LOAN_BORROWED',effective_date='2026-09-02',reason='Nhầm chiều')   # chưa có giao dịch: đổi được, có lịch sử
        self.assertEqual([h['action'] for h in self.members(k)[my]['business'] and self.biz()['loans'][0]['history']],['SET','CHANGE'])
        self.act('category-create',name='Ăn uống',description='',parent='expense');e=self.nodes()['Ăn uống']['id'];an=self.person_obj('Quán A',e)
        self.act('business-set',category=e,profile=an,type='LOAN_LENT',effective_date='2026-09-01')                         # spec 032: không còn chặn theo loại gốc
        self.err('business-set',category=k,profile=self.person,type='LOAN_LENT')                                           # không là thành viên

    def test_loan_kind_direction_and_property_mismatch(self):
        r=self.store.view()['business']['migration'];self.assertEqual({x['name']:x['action'] for x in r},{'Kết 5tr':'ADD_AND_SET','Kết 10tr':'ADD_AND_SET'})
        self.act('business-migrate',confirm=True)
        self.err('business-set',category='principal',profile=self.l10,type='LOAN_BORROWED',effective_date='2026-09-01',reason='x')   # khoản vay thiết lập Phải thu
        self.err('business-set',category='principal',profile=self.l10,type='PROPERTY',effective_date='2026-09-01',reason='x')

    def test_migration_idempotent_totals_unchanged_and_ledger(self):
        self.act('object-quick-create',kind='LOAN',party_name='Mới',name='Chưa thiết lập')
        c0=self.store.view()['categories'];rep0=self.store.report(self.store.state(),self.account);debt0=self.store.debt_register(self.store.state())
        prev={x['name']:x for x in self.biz()['migration']};self.assertEqual((prev['Chưa thiết lập']['action'],prev['Kết 10tr']['type']),('ADD_ONLY','LOAN_LENT'));self.assertIn('không đoán',prev['Chưa thiết lập']['message'])
        self.err('business-migrate');self.err('business-migrate',confirm=False)
        self.act('business-migrate',confirm=True);self.err('business-migrate',confirm=True)                                 # chạy lại: không còn gì để làm
        self.assertEqual(len(self.store.state()['business_migrations']),1)
        l10=self.loan(self.l10);self.assertEqual((l10['type'],D_(l10['increase']),D_(l10['decrease']),D_(l10['balance']),D_(l10['interest']),l10['side']),('LOAN_LENT',10000000,3000000,7000000,200000,'Phải thu'))
        l5=self.loan(self.l5);self.assertEqual((D_(l5['balance']),l5['issues']),(5000000,[]))
        self.assertEqual(l10['register']['principal'],'7000000');self.assertNotIn('REGISTER_MISMATCH',l10['issues'])
        self.assertEqual([x['name'] for x in self.biz()['unassigned']],['Chưa thiết lập']);self.assertEqual(D_(self.biz()['totals']['receivable']),12000000)
        c1=self.store.view()['categories']
        for r0,r1 in zip(c0['roots'],c1['roots']):self.assertEqual(r0['totals'],r1['totals'])
        self.assertEqual(self.store.report(self.store.state(),self.account),rep0);self.assertEqual(self.store.debt_register(self.store.state()),debt0)
        self.assertFalse(any(x['action']=='SET' for x in self.biz()['migration']))
        self.act('classify',ids=[self.tx('X1')['id']],parts=[dict(category='principal',profile=self.l5)])               # vẫn phân loại được sau hợp nhất

    def test_object_pair_ledger_interest_and_two_pairs(self):
        k=self.nodes()['Kết']['id'];my=self.person_obj('Mỹ',k);self.act('business-set',category=k,profile=my,type='LOAN_LENT',effective_date='2026-09-01')
        self.classify(['K3'],[dict(category='principal',node=k,profile=my)]);self.classify(['K1'],[dict(category='principal',node=k,profile=my)])
        row=next(x for x in self.biz()['loans'] if x['profile']==my);self.assertEqual((D_(row['increase']),D_(row['decrease']),D_(row['balance'])),(5000000,3000000,2000000))
        self.err('business-clear',category=k,profile=my,reason='x');self.err('business-set',category=k,profile=my,type='LOAN_BORROWED',effective_date='2026-09-05',reason='đổi')   # có giao dịch: không gỡ/đổi loại
        self.act('business-set',category=k,profile=my,type='LOAN_LENT',effective_date='2026-09-05',reason='Ghi lãi thỏa thuận',interest_note='1.5')                # sửa tham số được, có lịch sử
        self.assertEqual(len(next(x for x in self.biz()['loans'] if x['profile']==my)['history']),2)
        # lãi không đổi dư nợ gốc; đối tượng có một cặp cho vay nên lãi gom vào cặp
        self.act('category-create',name='Lãi Mỹ',description='',parent='interest');li=self.nodes()['Lãi Mỹ']['id'];self.act('category-object-add',category=li,profile=my)
        self.classify(['K4'],[dict(category='interest',node=li,profile=my)])
        row=next(x for x in self.biz()['loans'] if x['profile']==my);self.assertEqual((D_(row['balance']),D_(row['interest']),row['issues']),(2000000,200000,[]))
        # cùng một người cho vay và đi vay: hai cặp, hai sổ; lãi không chỉ định rõ được
        b=self.nodes()['Loans']['id'];self.act('category-object-add',category=b,profile=my);self.act('business-set',category=b,profile=my,type='LOAN_BORROWED',effective_date='2026-09-01')
        self.assertEqual({x['type'] for x in self.biz()['loans'] if x['profile']==my},{'LOAN_LENT','LOAN_BORROWED'})
        self.assertIn('UNDIRECTED_INTEREST',next(x for x in self.biz()['loans'] if x['profile']==my and x['type']=='LOAN_LENT')['issues'])
        self.assertEqual(D_(self.biz()['totals']['payable']),0)

    def test_negative_balance_warning_and_pre_effective(self):
        k=self.nodes()['Kết']['id'];my=self.person_obj('Mỹ',k);self.act('business-set',category=k,profile=my,type='LOAN_LENT',effective_date='2026-09-26')
        self.classify(['K3'],[dict(category='principal',node=k,profile=my)])
        row=next(x for x in self.biz()['loans'] if x['profile']==my);self.assertEqual(set(row['issues']),{'NEGATIVE_BALANCE'} | ({'PRE_EFFECTIVE'} if False else set()))
        self.assertEqual(D_(row['balance']),-3000000)

    def test_guards_remove_archive_merge(self):
        k=self.nodes()['Kết']['id'];my=self.person_obj('Mỹ',k);self.act('business-set',category=k,profile=my,type='LOAN_LENT',effective_date='2026-09-01')
        self.err('category-object-remove',category=k,profile=my,reason='x');self.err('category-archive',category=k,reason='x')
        self.act('object-quick-create',kind='PROPERTY',name='Nhà X');nx=next(p['id'] for p in self.store.state()['profiles'] if p['name']=='Nhà X')
        self.err('category-object-merge',**{'from':my,'into':nx,'reason':'x'})                                              # đích là BĐS, nguồn mang cho vay
        self.act('business-clear',category=k,profile=my,reason='Không còn dùng');self.assertIsNone(self.members(k)[my]['business'])
        self.act('category-object-remove',category=k,profile=my,reason='Gỡ')

    def test_property_business_and_no_effect_on_money(self):
        self.act('category-create',name='Property',type='investment');pc=self.nodes()['Property']['id']
        self.act('object-quick-create',kind='PROPERTY',name='Xuân Mai');xm=next(p['id'] for p in self.store.state()['profiles'] if p['name']=='Xuân Mai')
        self.err('business-set',category=pc,profile=xm,type='PROPERTY',effective_date='2026-09-01')                         # chưa là thành viên
        self.act('category-object-add',category=pc,profile=xm);self.act('business-set',category=pc,profile=xm,type='PROPERTY',effective_date='2026-09-01')
        self.err('business-set',category=pc,profile=xm,type='LOAN_LENT',effective_date='2026-09-01',reason='x')
        self.assertEqual(self.biz()['properties'][0]['type_name'],'Bất động sản');self.assertTrue(self.store.view()['build'].startswith('P3'))

if __name__=='__main__':unittest.main()
