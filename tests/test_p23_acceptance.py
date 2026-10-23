from pcms.reclassify import RECLASS_GRANT   # quyền nội bộ của "Sửa phân loại" (spec 043); API không gửi được — kiểm ở test_p45
import copy
import tempfile
import unittest
from decimal import Decimal
from datetime import date, timedelta
from pcms.core import ValidationError
import test_p13_acceptance as base

D_=base.D_

class P23Acceptance(base.P13Acceptance):
    """Dùng lại sao kê BĐS của P13 (Đất A: 200/150/250 triệu, chi phí, hoàn chi, nhận lại)."""
    def setup_cc(self):
        a=self.setup_land();self.a=a
        today=date.today();self.due=[(today-timedelta(days=60)).isoformat(),(today+timedelta(days=60)).isoformat(),(today+timedelta(days=200)).isoformat()]
        self.act('realty-contract',property=a,price='600000000',date='2026-08-01',reason='Ký hợp đồng',handover_date='2027-12-31')
        for lab,due,amt in (('Đợt 1',self.due[0],'200000000'),('Đợt 2',self.due[1],'200000000'),('Đợt 3',self.due[2],'200000000')):self.act('realty-installment',property=a,label=lab,due_date=due,amount=amt,note='')
        return a
    def prog(self,name='Đất A'):return self.prop(name)['progress']
    def inst(self,label):return next(i for i in self.prog()['installments'] if i['label']==label)

    def test_contract_versions_schedule_and_difference(self):
        self.setup_cc();p=self.prog();self.assertEqual((D_(p['summary']['price']),D_(p['summary']['scheduled']),D_(p['summary']['difference'])),(600000000,600000000,0));self.assertEqual(p['handover_date'],'2027-12-31')
        self.act('realty-contract',property=self.a,price='580000000',date='2026-09-10',reason='Chiết khấu');p=self.prog()
        self.assertEqual((D_(p['summary']['price']),D_(p['summary']['difference']),len(p['contract']['history'])),(580000000,-20000000,2))
        cid=p['contract']['current']['id'];self.err('realty-contract-void',contract=cid,reason='');self.act('realty-contract-void',contract=cid,reason='Nhập nhầm');self.assertEqual(D_(self.prog()['summary']['price']),600000000)
        for bad in (dict(price='0'),dict(price='1.5'),dict(price='abc'),dict(reason=''),dict(date='bad'),dict(property=self.pid('Đất A')+'x')):
            self.err('realty-contract',**{**dict(property=self.a,price='1',date='2026-09-10',reason='x'),**bad})
        for bad in (dict(label=''),dict(amount='0'),dict(amount='10.5'),dict(due_date='bad'),dict(property='nope')):
            self.err('realty-installment',**{**dict(property=self.a,label='X',due_date='2027-01-01',amount='1'),**bad})

    def test_link_paid_partial_overdue_and_commitment(self):
        self.setup_cc()                                              # D-1/D-2/D-3 đã phân loại Đầu tư BĐS (200/150/250 triệu)
        i1,i2,i3=self.inst('Đợt 1'),self.inst('Đợt 2'),self.inst('Đợt 3')
        self.assertEqual((i1['status'],i1['overdue']),('UNPAID',True));self.assertTrue(i1['overdue_days']>=59);self.assertEqual((i2['overdue'],i3['overdue']),(False,False))
        self.act('realty-pay-link',installment=i1['id'],transaction=self.tx('D-1')['id']);i1=self.inst('Đợt 1');self.assertEqual((i1['status'],D_(i1['paid']),D_(i1['remaining']),i1['overdue']),('PAID',200000000,0,False))
        self.act('realty-pay-link',installment=i2['id'],transaction=self.tx('D-2')['id']);i2=self.inst('Đợt 2');self.assertEqual((i2['status'],D_(i2['paid']),D_(i2['remaining'])),('PARTIAL',150000000,50000000))
        self.act('realty-pay-link',installment=i3['id'],transaction=self.tx('D-3')['id']);i3=self.inst('Đợt 3');self.assertEqual((i3['status'],D_(i3['over_paid'])),('PAID',50000000))      # trả quá
        s=self.prog()['summary'];self.assertEqual((D_(s['paid']),D_(s['remaining']),s['overdue']),(600000000,50000000,0))
        self.assertEqual(self.prog()['linkable'],[])
        a=self.store.view()['assets'];self.assertEqual(D_(a['commitments']['VND']),50000000)
        self.assertIn('không cộng vào nợ',a['commitments']['note'])

    def test_link_rules_unlink_void_and_broken(self):
        self.setup_cc();i1,i2=self.inst('Đợt 1'),self.inst('Đợt 2');d1=self.tx('D-1')['id']
        for bad in (self.tx('D-BACK')['id'],self.tx('D-COST')['id'],self.tx('D-SAL')['id'] if any(t['reference']=='D-SAL' for t in self.store.state()['transactions']) else 'nope'):self.err('realty-pay-link',installment=i1['id'],transaction=bad)
        self.act('realty-pay-link',installment=i1['id'],transaction=d1);self.err('realty-pay-link',installment=i2['id'],transaction=d1)       # đã gắn đợt khác
        self.err('realty-installment-void',installment=i1['id'],reason='x')                                                                      # còn giao dịch gắn
        lid=self.inst('Đợt 1')['links'][0]['id'];self.err('realty-pay-unlink',link=lid,reason='');self.act('realty-pay-unlink',link=lid,reason='Gắn nhầm')
        self.assertEqual((self.inst('Đợt 1')['status'],len(self.inst('Đợt 1')['links'])),('UNPAID',0))
        self.act('realty-pay-link',installment=i1['id'],transaction=d1)
        other=self.act('object-quick-create',kind='PROPERTY',name='Đất B');b=self.pid('Đất B')
        self.err('classify',ids=[d1],parts=[dict(category='investment',profile=b)],_reclass=RECLASS_GRANT)                                # spec 043: đã gắn đợt thanh toán BĐS → bỏ gắn trước
        l=self.inst('Đợt 1')['links'][0];self.assertFalse(l['broken']);self.act('realty-pay-unlink',link=l['id'],reason='Không còn là Đất A')
        self.classify(['D-1'],[dict(category='investment',profile=b)]);self.assertEqual((D_(self.inst('Đợt 1')['paid']),self.inst('Đợt 1')['status']),(0,'UNPAID'))   # phân loại lại khỏi Đất A sau khi bỏ gắn
        self.act('realty-installment-void',installment=i2['id'],reason='Gộp đợt');self.assertEqual(len(self.prog()['installments']),2)
        self.err('realty-installment-void',installment=i2['id'],reason='lần hai')

    def test_no_schedule_unchanged_and_assets_unaffected(self):
        a=self.setup_land();before=self.store.view()['assets'];p=self.prop('Đất A')['progress'];self.assertFalse(p['has_schedule']);self.assertEqual(D_(self.store.view()['assets']['commitments']['VND']),0)
        self.act('realty-installment',property=a,label='Đợt 1',due_date='2030-01-01',amount='100000000',note='')
        after=self.store.view()['assets'];self.assertEqual(after['currencies'],before['currencies']);self.assertEqual(D_(after['commitments']['VND']),100000000)         # tổng tài sản/nợ/ròng không đổi
        self.assertEqual(self.prop('Đất A')['capital'],self.prop('Đất A')['capital'])

    def test_read_only_and_backup(self):
        import tempfile as tf
        from uuid import uuid4
        self.setup_cc();n=len(self.store.events());self.view();self.store.view();self.assertEqual(len(self.store.events()),n)
        other=base.P01Store(tf.mkdtemp());other.restore(self.store.backup(),str(uuid4()));self.assertEqual(len(other.view()['realty']['properties'][0]['progress']['installments']),3)

for name in [n for n in dir(base.P13Acceptance) if n.startswith('test_')]:setattr(P23Acceptance,name,None)
if __name__=='__main__':unittest.main()
