import base64
import copy
import tempfile
import unittest
from uuid import uuid4
from pcms.product import ProductStore, D, projection
from pcms.continuous import account_history, active_transactions
from pcms.core import ValidationError

class ContinuousTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=ProductStore(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def act(self,action,**d):return self.store.apply(action,d,str(uuid4()))
    def tx(self,**kw):
        d=dict(kind='unclassified_in',account='bank-main',amount='1000000',date='2026-09-28',description='Transfer source');d.update(kw)
        return self.act('transaction',**d)
    def party(self,name='Person A'):
        self.act('party',name=name);return self.store.state()['parties'][-1]['id']
    def loan(self,party=None,direction='BORROWED',opening='0',**kw):
        d=dict(name='A01',party=party or self.party(),loan_direction=direction,currency='VND',effective_date='2026-09-01',due='2026-12-31',opening=opening,annual_rate='8',source='confirmed demo')
        d.update(kw);self.act('loan',**d);return self.store.state()['liabilities'][-1]['id']
    def test_account_opening_and_unbounded_dates(self):
        v=self.act('account',name='Bank new',owner='Thach demo',type='BANK',currency='VND',pool='OPERATING',opening='1000',effective_date='2024-01-01',opening_source='demo')
        a=v['state']['accounts'][-1]['id']
        self.tx(account=a,date='2024-01-02',amount='100')
        self.tx(account=a,date='2027-02-01',amount='200')
        self.assertEqual(self.store.state()['as_of'],'2027-02-01')
        h=account_history(self.store.state(),a,'2024-01-01','2027-03-01')
        self.assertEqual(D(h['closing']),D('1300'))
        with self.assertRaises(ValidationError):self.tx(account=a,date='2023-12-31')
    def test_unknown_changes_balance_not_income_then_classifies_once(self):
        before=self.store.view()['report'];v=self.tx();tid=v['state']['transactions'][-1]['id']
        self.assertEqual(v['report']['income'],before['income']);self.assertEqual(v['report']['unclassified'],1)
        amount=v['report']['cash']
        v=self.act('classify',id=tid,parts=[dict(kind='income',amount='1000000')],reason='confirmed income')
        self.assertEqual(v['report']['cash'],amount);self.assertEqual(v['report']['unclassified'],0)
        self.assertEqual(D(v['report']['income'])-D(before['income']),D('40'))
        with self.assertRaises(ValidationError):self.act('classify',id=tid,parts=[dict(kind='income',amount='1000000')],reason='again')
    def test_four_people_multiple_loans_split_payment(self):
        people=[self.party('Person '+str(i)) for i in range(4)]
        loans=[self.loan(p,opening='100000000') for p in people]
        other=self.loan(people[0],opening='50000000',name='A02')
        self.act('interest-record',loan=loans[0],date='2026-09-28',amount='5000000',source='interest agreed')
        v=self.act('loan-payment',loan=loans[0],account='bank-main',date='2026-09-28',principal='50000000',interest='5000000',total='55000000',fee='0',description='pay A')
        group=next(g for g in v['report']['loan_totals'] if g['party']==people[0])
        self.assertEqual(D(group['borrowed']),D('100000000'));self.assertEqual(D(group['interest_payable']),0)
        l=next(l for l in v['report']['loans'] if l['id']==other);self.assertEqual(D(l['balance']),D('50000000'))
    def test_classify_imported_payment_does_not_double_post(self):
        loan=self.loan(opening='100000000')
        v=self.tx(kind='unclassified_out',amount='55000000');tid=v['state']['transactions'][-1]['id'];cash=v['report']['cash']
        v=self.act('classify',id=tid,reason='principal and interest',parts=[dict(kind='repay',amount='50000000',liability=loan),dict(kind='expense',amount='5000000',liability=loan,component='interest')])
        self.assertEqual(v['report']['cash'],cash)
        self.assertEqual(D(next(l for l in v['report']['loans'] if l['id']==loan)['balance']),D('50000000'))
    def test_reclassify_known_income_as_loan_preserves_cash(self):
        loan=self.loan();v=self.tx(kind='income');tid=v['state']['transactions'][-1]['id'];cash=v['report']['cash']
        v=self.act('classify',id=tid,reason='Actually borrowed',parts=[dict(kind='borrow',amount='1000000',liability=loan)])
        self.assertEqual(v['report']['cash'],cash)
        self.assertEqual(D(next(l['balance'] for l in v['report']['loans'] if l['id']==loan)),D('1000000'))
        self.assertEqual(len(active_transactions(v['state'])),25)

    def test_wrong_split_atomic(self):
        v=self.tx();tid=v['state']['transactions'][-1]['id'];n=len(self.store.events())
        with self.assertRaises(ValidationError):self.act('classify',id=tid,reason='bad',parts=[dict(kind='income',amount='1')])
        self.assertEqual(len(self.store.events()),n)
    def test_receivable_no_false_expense_or_debt_netting(self):
        loan=self.loan(direction='LENT');before=self.store.view()['report']
        v=self.tx(kind='lend',liability=loan,amount='10000000')
        self.assertEqual(D(v['report']['net_worth']),D(before['net_worth']));self.assertEqual(v['report']['expense'],before['expense'])
        self.assertEqual(D(v['report']['receivable_total']),D('400'))
        with self.assertRaises(ValidationError):self.tx(kind='collect',liability=loan,amount='20000000')
    def test_transfer_matching_preserves_dates_cash_and_no_income(self):
        v=self.tx(kind='unclassified_out',amount='1000000',date='2026-09-27');out=v['state']['transactions'][-1]['id']
        v=self.tx(account='bank-reserve',amount='1000000');inc=v['state']['transactions'][-1]['id']
        before=[account_history(self.store.state(),a,'2026-09-26','2026-09-27')['closing'] for a in ('bank-main','bank-reserve')]
        cash=v['report']['cash'];income=v['report']['income']
        v=self.act('match-transfer',outgoing=out,incoming=inc,reason='same transfer')
        self.assertEqual(v['report']['cash'],cash);self.assertEqual(v['report']['income'],income)
        self.assertEqual(before,[account_history(self.store.state(),a,'2026-09-26','2026-09-27')['closing'] for a in ('bank-main','bank-reserve')])
        with self.assertRaises(ValidationError):self.act('match-transfer',outgoing=out,incoming=inc,reason='again')
    def test_actual_cross_currency_amount(self):
        self.party();before=self.store.view()['report']
        with self.assertRaises(ValidationError):self.tx(kind='transfer',to_account='crypto-cash')
        v=self.tx(kind='transfer',to_account='crypto-cash',received_amount='39')
        cash=next(a for a in v['report']['accounts'] if a['id']=='crypto-cash')
        self.assertEqual(D(cash['balance']),D('65039'))
        self.assertEqual(D(v['report']['net_worth']),D(before['net_worth'])-1)
    def test_overlapping_import_review_keeps_distinct_rows(self):
        raw='date,account,direction,amount,description,reference\n2026-09-28,bank-main,IN,1000000,Deposit,ABC\n'
        def load(raw,name):
            v=self.act('continuous-import',filename=name,content=base64.b64encode(raw.encode()).decode());return v['state']['imports'][-1]
        b=load(raw,'first.csv');v=self.act('import-row',batch=b['id'],row=b['rows'][0]['id'],kind='unclassified_in');tx=v['state']['transactions'][-1]['id'];cash=v['report']['cash']
        b=load(raw+'\n','second.csv');self.assertEqual(b['rows'][0]['duplicate_candidates'],[tx])
        with self.assertRaises(ValidationError):self.act('import-row',batch=b['id'],row=b['rows'][0]['id'],kind='unclassified_in')
        self.act('import-duplicate',batch=b['id'],row=b['rows'][0]['id'],transaction=tx,reason='same transaction')
        self.assertEqual(self.store.view()['report']['cash'],cash)
        b=load(raw+'\n\n','third.csv');self.act('import-row',batch=b['id'],row=b['rows'][0]['id'],kind='unclassified_in',distinct_reason='different payment verified')
        self.assertEqual(D(self.store.view()['report']['cash']),D(cash)+40)
    def test_holdings_account_specific_and_transfer_no_wealth_change(self):
        before=self.store.view()['report']['net_worth']
        self.act('custody-move',asset='btc',from_account='UNASSIGNED',to_account='crypto-cash',date='2026-07-01',quantity='1.2',source='confirmed custody')
        self.act('custody-move',asset='btc',from_account='crypto-cash',to_account='trading',date='2026-09-28',quantity='0.2',source='wallet transfer')
        v=self.store.view();self.assertEqual(v['report']['net_worth'],before)
        self.assertEqual(D(next(h['quantity'] for h in v['report']['holdings'] if h['asset']=='btc' and h['account']=='trading')),D('.2'))
        with self.assertRaises(ValidationError):self.tx(kind='sell',account='trading',asset='btc',quantity='.3',amount='18600')
    def test_history_counts_economic_movements_not_reversal_noise(self):
        v=self.tx();tid=v['state']['transactions'][-1]['id']
        before=account_history(self.store.state(),'bank-main','2026-09-28','2026-09-28')
        self.act('classify',id=tid,reason='classified',parts=[dict(kind='income',amount='1000000')])
        after=account_history(self.store.state(),'bank-main','2026-09-28','2026-09-28')
        for key in ('incoming','outgoing','closing'):self.assertEqual(before[key],after[key])
        self.assertEqual(len(after['rows']),1)
    def test_source_balance_mismatch_blocks_import(self):
        raw='date,account,direction,amount,description,balance,opening_balance\n2026-09-28,bank-main,IN,100,First,100,0\n2026-09-28,bank-main,OUT,50,Second,60,\n'
        v=self.act('continuous-import',filename='bad-balance.csv',content=base64.b64encode(raw.encode()).decode());b=v['state']['imports'][-1]
        self.assertTrue(b['issues'])
        with self.assertRaises(ValidationError):self.act('import-row',batch=b['id'],row=b['rows'][0]['id'],kind='unclassified_in')
    def test_matched_cross_day_transfer_in_transit(self):
        self.tx(kind='unclassified_out',amount='1000000',date='2026-09-26');out=self.store.state()['transactions'][-1]['id']
        self.tx(account='bank-reserve',amount='1000000',date='2026-09-28');inc=self.store.state()['transactions'][-1]['id']
        self.act('match-transfer',outgoing=out,incoming=inc,reason='two days settlement')
        middle=projection(self.store.state(),'2026-09-27');end=projection(self.store.state(),'2026-09-28')
        self.assertEqual(D(middle['in_transit_total']),D('40'));self.assertEqual(D(end['in_transit_total']),0)
        self.assertEqual(D(middle['net_worth']),D(end['net_worth']))

    def test_frozen_snapshots_survive_new_workflows_and_restore(self):
        before=copy.deepcopy(self.store.state()['snapshots']);self.party();self.loan();self.tx()
        self.assertEqual(before,self.store.state()['snapshots']);bundle=self.store.backup();self.store.restore(bundle,str(uuid4()))
        self.assertEqual(before,self.store.state()['snapshots'])
    def test_backdated_classification_after_report_cutoff_validates_future(self):
        loan=self.loan(opening='1000000');self.tx(kind='repay',liability=loan,amount='1000000',date='2026-10-01')
        self.act('report-date',date='2026-09-28')
        with self.assertRaises(ValidationError):self.tx(kind='repay',liability=loan,amount='1',date='2026-09-28')

if __name__=='__main__':unittest.main()
