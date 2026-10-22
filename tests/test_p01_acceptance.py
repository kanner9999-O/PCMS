"""Independent P01 release checks against persistent application, not prototype."""
import base64
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4
from p01_fixtures import fixtures
from pcms.p01 import P01Store


class P01Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=P01Store(Path(self.tmp.name)/'original');self.store.require_membership=False
        self.files=fixtures()
        self.act('account',name='QA A',reference='000123',opening='100000000',effective_date='2026-10-01',opening_source='Synthetic test opening')
        self.a=self.store.state()['accounts'][-1]['id']
        self.act('account',name='QA B',reference='000456',opening='20000000',effective_date='2026-10-01',opening_source='Synthetic test opening')
        self.b=self.store.state()['accounts'][-1]['id']
    def tearDown(self):self.tmp.cleanup()
    def act(self,action,**data):return self.store.apply(action,data,str(uuid4()))
    def stage(self,name,account=None):
        self.act('import',account=account or self.a,filename=name,content=base64.b64encode(self.files[name]).decode())
        return next(b['id'] for b in self.store.state()['imports'] if b['account']==(account or self.a) and b['sha256']==hashlib.sha256(self.files[name]).hexdigest())
    def publish(self,name,account=None):
        batch=self.stage(name,account);self.act('publish',batch=batch);return batch
    def tx(self,ref):return next(t for t in self.store.state()['transactions'] if t.get('bank_reference',t.get('reference'))==ref)
    def balance(self,a):
        s=self.store.state();acc=next(x for x in s['accounts'] if x['id']==a)
        return int(acc['opening'])+sum(int(t['signed_amount']) for t in s['transactions'] if t['account']==a)
    def first_two(self):self.publish('01-first.xlsx');self.publish('02-overlap.xlsx')
    def rejected(self,action,**data):
        old=copy.deepcopy(self.store.state())
        with self.assertRaises(Exception):self.act(action,**data)
        self.assertEqual(self.store.state(),old)

    def test_P01_01_overlap_reimport_and_restart(self):
        self.publish('01-first.xlsx');self.assertEqual(self.balance(self.a),115000000)
        self.publish('02-overlap.xlsx');self.assertEqual(self.balance(self.a),112000000)
        self.assertEqual(len(self.tx('OUT-01')['sources']),2)
        self.assertEqual(next(r for r in self.store.view()['reports'] if r['account']==self.a)['source_end'],'2026-10-03')
        self.stage('01-first.xlsx');self.assertEqual(len(self.store.state()['transactions']),3)
        self.store=P01Store(Path(self.tmp.name)/'original');self.store.require_membership=False
        self.assertEqual(self.balance(self.a),112000000)
        self.assertEqual(len(self.store.state()['transactions']),3)

    def test_P01_01_stale_staged_duplicate_cannot_double_post(self):
        first=self.stage('01-first.xlsx')
        self.files['stale.xlsx']=self.files['01-first.xlsx']+b'QA independent duplicate payload'
        second=self.stage('stale.xlsx')
        self.act('publish',batch=first)
        try:self.act('publish',batch=second)
        except Exception:pass  # Rejection or safe dedup is acceptable; double-posting is not.
        try:self.act('publish',batch=first)
        except Exception:pass
        self.assertEqual(self.balance(self.a),115000000)
        self.assertEqual(len(self.store.state()['transactions']),2)

    def test_P01_03_recheck_after_missing_earlier_source(self):
        late=self.stage('02-overlap.xlsx')
        batch=next(b for b in self.store.state()['imports'] if b['id']==late)
        self.assertEqual(batch['status'],'BLOCKED')
        original_payload=batch['content']; original_sha=batch['sha256']
        self.rejected('publish',batch=late)
        self.publish('01-first.xlsx')
        self.act('recheck-import',batch=late)
        batch=next(b for b in self.store.state()['imports'] if b['id']==late)
        self.assertEqual(batch['status'],'STAGED')
        self.assertEqual(batch['issues'],[])
        self.assertEqual(batch['content'],original_payload)
        self.assertEqual(batch['sha256'],original_sha)
        self.act('publish',batch=late)
        self.assertEqual(self.balance(self.a),112000000)
        self.assertEqual(len(self.store.state()['transactions']),3)
        self.assertEqual(len(self.tx('OUT-01')['sources']),2)

    def test_P01_02_distinct_and_conflict_atomicity(self):
        self.first_two();self.publish('03-distinct.xlsx')
        self.assertEqual(len(self.store.state()['transactions']),5)
        self.assertEqual(self.balance(self.a),110000000)
        batch=self.stage('04-conflict.xlsx');self.rejected('publish',batch=batch)
        self.assertEqual(len(self.store.state()['transactions']),5)

    def test_P01_03_invalid_sources_never_post(self):
        batch=self.stage('05-mismatch.xlsx');self.rejected('publish',batch=batch)
        self.assertEqual(len(self.store.state()['transactions']),0)
        batch=self.stage('09-unsupported.xlsx');self.rejected('publish',batch=batch)
        self.assertEqual(len(self.store.state()['transactions']),0)

    def test_P01_03_invalid_staged_source_blocks_approval(self):
        self.first_two()
        self.stage('05-mismatch.xlsx')
        self.rejected('approve',account=self.a,confirm_unknown=True)

    def test_P01_04_split_bulk_scope_and_wrong_profile(self):
        self.first_two();self.publish('06-split.xlsx')
        self.act('profile',kind='PERSON',name='QA borrower')
        person=self.store.state()['profiles'][-1]['id']
        self.act('profile',kind='LOAN',name='QA loan',party=person)
        loan=self.store.state()['profiles'][-1]['id']
        tx=self.tx('SPLIT-01');before=self.balance(self.a)
        self.rejected('classify',ids=[tx['id']],parts=[dict(category='principal',amount='20000000',profile=loan)],reason='invalid total')
        self.rejected('classify',ids=[tx['id']],parts=[dict(category='principal',amount='22000000',profile='missing')],reason='invalid target')
        self.act('classify',ids=[tx['id']],parts=[dict(category='principal',amount='20000000',profile=loan),dict(category='interest',amount='2000000',profile=loan)],reason='Confirmed synthetic split')
        self.assertEqual(self.balance(self.a),before)
        self.assertEqual(len(self.store.state()['transactions']),4)
        ids=[self.tx('OUT-01')['id'],self.tx('OUT-02')['id']]
        unchanged=copy.deepcopy(self.tx('IN-01'))
        self.act('classify',ids=ids,parts=[dict(category='expense')],reason='Bulk selected expenses')
        self.assertEqual(self.tx('IN-01'),unchanged)
        self.assertEqual(self.tx('SPLIT-01')['allocations'][0]['amount'],'20000000')

    def test_P01_04_partial_unknown_retained_and_requires_confirmation(self):
        self.first_two();self.publish('06-split.xlsx')
        self.act('profile',kind='PERSON',name='Partial QA person')
        person=self.store.state()['profiles'][-1]['id']
        self.act('profile',kind='LOAN',name='Partial QA loan',party=person)
        loan=self.store.state()['profiles'][-1]['id']
        self.act('classify',ids=[self.tx('IN-01')['id']],parts=[dict(category='income')],reason='Known receipt')
        self.act('classify',ids=[self.tx('OUT-01')['id'],self.tx('OUT-02')['id']],parts=[dict(category='expense')],reason='Known expense')
        self.act('classify',ids=[self.tx('SPLIT-01')['id']],parts=[dict(category='principal',amount='20000000',profile=loan),dict(category='unknown',amount='2000000')],reason='Principal known; remainder pending evidence')
        report=next(r for r in self.store.view()['reports'] if r['account']==self.a)
        self.assertEqual(report['unknown_count'],1)
        self.assertEqual(report['totals']['unknown_out'],'2000000')
        self.rejected('approve',account=self.a,confirm_unknown=False)
        self.act('approve',account=self.a,confirm_unknown=True)
        snapshot=self.store.state()['snapshots'][0]
        self.assertEqual(snapshot['report']['totals']['unknown_out'],'2000000')

    def test_P01_05_approval_unknown_restatement_frozen(self):
        self.first_two();self.rejected('approve',account=self.a,confirm_unknown=False)
        self.act('approve',account=self.a,confirm_unknown=True)
        snapshot=copy.deepcopy(self.store.state()['snapshots'][0])
        tx=self.tx('OUT-01')
        self.rejected('classify',ids=[tx['id']],parts=[dict(category='expense',amount='5000000')],reason='')
        self.rejected('classify',ids=[tx['id']],parts=[dict(category='expense',amount='5000000')],reason='Must open adjustment first')
        self.act('begin-adjustment',account=self.a,reason='')   # spec 009: lý do mở phiên điều chỉnh là tùy chọn (lý do khi duyệt bản mới vẫn bắt buộc)
        self.act('begin-adjustment',account=self.a,reason='Identify missing expense classification')
        self.act('classify',ids=[tx['id']],parts=[dict(category='expense',amount='5000000')],reason='Identified expense after approval')
        self.act('approve',account=self.a,confirm_unknown=True,reason='Correction of previous classification')
        self.assertEqual(self.store.state()['snapshots'][0],snapshot)
        self.assertEqual(len(self.store.state()['snapshots']),2)
        self.store=P01Store(Path(self.tmp.name)/'original');self.store.require_membership=False
        self.assertEqual(self.store.state()['snapshots'][0],snapshot)

    def test_P01_06_account_isolation_and_transfer(self):
        self.first_two();self.publish('06-split.xlsx')
        self.assertEqual(self.balance(self.b),20000000)
        self.publish('07-transfer-out.xlsx')
        outgoing=self.tx('TRANSFER-OUT')['id']
        self.act('classify',ids=[outgoing],parts=[dict(category='transfer_pending',amount='10000000')],reason='Awaiting recipient statement')
        report=next(r for r in self.store.view()['reports'] if r['account']==self.a)
        self.assertEqual(report['totals']['transfer_pending_out'],'10000000')
        self.assertNotIn('expense_out',report['totals'])
        self.publish('08-transfer-in.xlsx',self.b)
        incoming=self.tx('TRANSFER-IN')['id']
        self.act('match-transfer',outgoing=outgoing,incoming=incoming,reason='Own transfer confirmed')
        self.assertEqual(self.balance(self.a),80000000);self.assertEqual(self.balance(self.b),30000000)
        self.rejected('match-transfer',outgoing=outgoing,incoming=incoming,reason='Repeated match forbidden')
        self.assertEqual(self.tx('TRANSFER-OUT')['date'],'2026-10-05')
        self.assertEqual(self.tx('TRANSFER-IN')['date'],'2026-10-06')
        for report in self.store.view()['reports']:
            self.assertNotIn('income_in',report['totals'])
            self.assertNotIn('expense_out',report['totals'])

    def test_P01_07_restore_separate_and_preserve_source(self):
        self.first_two()
        self.act('profile',kind='PERSON',name='Restore QA person')
        self.act('classify',ids=[self.tx('OUT-01')['id']],parts=[dict(category='expense',amount='5000000')],reason='Classification included in backup')
        self.act('approve',account=self.a,confirm_unknown=True)
        original=copy.deepcopy(self.store.state());bundle=self.store.backup()
        restored=P01Store(Path(self.tmp.name)/'restored')
        restored.restore(bundle,str(uuid4()))
        self.assertEqual(restored.state(),original)
        self.assertEqual(self.store.state(),original)
        self.assertIn(base64.b64encode(self.files['01-first.xlsx']).decode(),str(bundle))
        with self.assertRaises(Exception):self.store.restore(bundle,str(uuid4()))
        self.assertEqual(self.store.state(),original)

if __name__=='__main__':unittest.main()
