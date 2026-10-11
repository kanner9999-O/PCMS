import base64
import copy
import tempfile
import unittest
from uuid import uuid4
from pcms.product import ProductStore, projection, D
from pcms.core import ValidationError

class ProductTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=ProductStore(self.tmp.name)
    def tearDown(self): self.tmp.cleanup()
    def action(self,action,**data):return self.store.apply(action,data,str(uuid4()))
    def tx(self,**values):
        d=dict(kind='expense',account='bank-main',amount='1000000',date='2026-09-28',description='Test expense')
        d.update(values)
        return self.action('transaction',**d)
    def test_ownership_and_no_double_count(self):
        r=self.store.view()['report']
        a={x['id']:x for x in r['assets']}
        self.assertEqual(D(a['land']['value']),D('1600000000'))
        self.assertEqual(D(a['business']['value']),D('3600000000'))
        self.assertEqual(D(r['net_worth']),D(r['gross_assets'])-D(r['debt']))
        self.assertEqual(D(a['apt']['equity']),D('3200000000'))
    def test_transfer_preserves_wealth_and_income(self):
        before=self.store.view()['report']
        after=self.tx(kind='transfer',account='bank-main',to_account='crypto-cash')['report']
        for key in ('net_worth','income','expense','cash'):
            self.assertEqual(D(before[key]),D(after[key]))
        self.assertFalse(after['can_close'])
    def test_buy_and_sell_and_insufficient(self):
        before=self.store.view()['report']
        after=self.tx(kind='buy',account='crypto-cash',asset='btc',quantity='0.1',amount='6200')['report']
        self.assertEqual(D(before['net_worth']),D(after['net_worth']))
        self.assertEqual(D(next(a for a in after['assets'] if a['id']=='btc')['quantity']),D('1.3'))
        with self.assertRaises(ValidationError):self.tx(kind='sell',account='crypto-cash',asset='btc',quantity='10',amount='620000')
        with self.assertRaises(ValidationError):self.tx(amount='999999999999')
        self.assertEqual(len(self.store.events()),2)
    def test_approval_required_and_once(self):
        with self.assertRaises(ValidationError):self.tx(kind='transfer',account='crypto-cash',to_account='trading',amount='1000')
        self.action('decision',category='CAPITAL',title='Budget',reason='Trial',from_account='crypto-cash',to_account='trading',amount='1000')
        key=self.store.state()['decisions'][-1]['id']
        with self.assertRaises(ValidationError):self.action('execute',id=key)
        self.action('approve',id=key);self.action('execute',id=key)
        with self.assertRaises(ValidationError):self.action('execute',id=key)
    def test_correction_restates_and_keeps_original_close(self):
        self.action('close',note='First')
        old=copy.deepcopy(self.store.state()['snapshots'][-1])
        original=self.store.state()['transactions'][0]
        self.action('correct',id=original['id'],amount='86000000',reason='Example')
        with self.assertRaises(ValidationError):self.action('close',note='Blocked')
        self.action('reconcile-demo')
        self.action('close',note='Restated',restates=old['id'])
        state=self.store.state()
        self.assertEqual(old,state['snapshots'][-2])
        self.assertNotEqual(old['hash'],state['snapshots'][-1]['hash'])
        self.assertEqual(state['snapshots'][-1]['version'],2)
    def test_import_gate_duplicate_review(self):
        raw=b'date,account,kind,amount,description\n2026-09-25,bank-main,expense,350000,Example\n'
        data={'filename':'demo.csv','content':base64.b64encode(raw).decode()}
        self.action('import',**data)
        with self.assertRaises(ValidationError):self.action('import',**data)
        self.assertFalse(self.store.view()['report']['can_close'])
        b=self.store.state()['imports'][-1]
        self.action('import-row',batch=b['id'],row=b['rows'][0]['id'],kind='expense')
        with self.assertRaises(ValidationError):self.action('import-row',batch=b['id'],row=b['rows'][0]['id'],kind='expense')
        self.action('reconcile-demo');self.action('close',note='CSV accepted')
    def test_invalid_import_cannot_close_until_archived(self):
        raw=b'date,account,amount,description\n2026-09-25,missing,350000,Invalid\n'
        self.action('import',filename='invalid.csv',content=base64.b64encode(raw).decode())
        self.assertFalse(self.store.view()['report']['can_close'])
        b=self.store.state()['imports'][-1]
        self.action('archive-import',id=b['id'],reason='Invalid demo')
        self.assertTrue(self.store.view()['report']['can_close'])
    def test_backup_restore_tamper_and_idempotency(self):
        bundle=self.store.backup();before=self.store.view()['report']
        self.tx();self.store.restore(bundle,str(uuid4()))
        self.assertEqual(before,self.store.view()['report'])
        bad=copy.deepcopy(bundle);bad['events'][0]['state']['rates']['USDT']='9'
        with self.assertRaises(ValidationError):self.store.restore(bad,str(uuid4()))
        rid=str(uuid4());self.store.apply('policy',dict(single_asset_limit='40',crypto_limit='40',cash_floor='20000'),rid)
        n=len(self.store.events());self.store.apply('policy',{},rid);self.assertEqual(n,len(self.store.events()))
    def test_new_asset_does_not_change_historical_projection(self):
        before=projection(self.store.state(),'2026-08-31')
        self.action('asset',name='New',currency='VND',quantity='1',price='1000000',ownership='0.5',reason='scope',**{'class':'PROPERTY'})
        self.assertEqual(before,projection(self.store.state(),'2026-08-31'))
    def test_liability_effective_date(self):
        before=projection(self.store.state(),'2026-08-31')
        self.action('liability',name='New debt',currency='VND',opening='1000000',interest='8',next_payment='100000',due='2026-10-10',reason='scope')
        self.assertEqual(before,projection(self.store.state(),'2026-08-31'))
    def test_backdated_overdraft_rejected_even_when_current_cash_enough(self):
        with self.assertRaises(ValidationError):
            self.tx(amount='300000000',date='2026-07-01')
        self.assertEqual(len(self.store.events()),1)

    def test_reconciliation_mismatch_blocks_close(self):
        self.action('reconcile',account='bank-main',observed='0',source='Demo mismatch')
        with self.assertRaises(ValidationError):self.action('close',note='No')

if __name__=='__main__':unittest.main()
