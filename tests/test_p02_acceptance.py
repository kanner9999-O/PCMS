"""Independent lifecycle QA. Synthetic sources; never operational data."""
import base64
import copy
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4
from pcms.p01 import P01Store
from p01_fixtures import fixtures, statement

class P02Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'store';self.store=P01Store(self.path)
        self.files=fixtures()
        self.a=self.account('QA A','000123','100000000')
        self.b=self.account('QA B','000456','20000000')
    def tearDown(self):self.tmp.cleanup()
    def act(self,action,**data):return self.store.apply(action,data,str(uuid4()))
    def account(self,name,reference,opening):
        self.act('account',name=name,reference=reference,opening=opening,effective_date='2026-10-01',opening_source='Synthetic opening')
        return self.store.state()['accounts'][-1]['id']
    def get(self,id):return next(a for a in self.store.state()['accounts'] if a['id']==id)
    def stage(self,name,account=None):
        self.act('import',account=account or self.a,filename=name,content=base64.b64encode(self.files[name]).decode())
        return self.store.state()['imports'][-1]['id']
    def publish(self,name,account=None):
        batch=self.stage(name,account);self.act('publish',batch=batch);return batch
    def reject(self,action,**data):
        before=copy.deepcopy(self.store.state())
        with self.assertRaises(Exception):self.act(action,**data)
        self.assertEqual(self.store.state(),before)
    def finance(self):
        s=self.store.state()
        return {k:copy.deepcopy(s[k]) for k in ('transactions','imports','snapshots','profiles')}
    def balance(self,a):return next(r['balance'] for r in self.store.view()['reports'] if r['account']==a)

    def test_01_edit_wrong_opening_before_source_and_audit(self):
        self.act('account-edit',account=self.a,name='QA A corrected',opening='90000000',opening_source='Wrong source entered for QA')
        self.act('account-edit',account=self.a,name='QA A corrected',opening='100000000',opening_source='Correct synthetic source')
        self.assertEqual(self.get(self.a)['opening'],'100000000')
        self.publish('01-first.xlsx')
        self.assertEqual(self.balance(self.a),'115000000')
        self.assertTrue(any(x['action']=='account-edit' for x in self.store.state()['audit']))
        self.assertEqual(self.get(self.b)['opening'],'20000000')

    def test_02_staged_source_revalidation_preserves_bytes(self):
        self.act('account-edit',account=self.a,name='QA A',opening='90000000')
        batch=self.stage('01-first.xlsx');before=copy.deepcopy(self.store.state()['imports'][-1])
        self.assertEqual(before['status'],'BLOCKED')
        self.act('account-edit',account=self.a,name='QA A',opening='100000000')
        after=next(b for b in self.store.state()['imports'] if b['id']==batch)
        self.assertEqual(after['status'],'STAGED');self.assertEqual(after['issues'],[])
        for key in ('id','sha256','content','rows'):self.assertEqual(before[key],after[key])
        self.act('publish',batch=batch);self.assertEqual(self.balance(self.a),'115000000')

    def test_03_rename_used_account_preserves_money_source_snapshots(self):
        self.publish('01-first.xlsx');self.act('approve',account=self.a,confirm_unknown=True)
        before=self.finance();other=copy.deepcopy(self.get(self.b))
        self.act('account-edit',account=self.a,name='Renamed by QA')
        self.assertEqual(self.finance(),before);self.assertEqual(self.get(self.b),other)
        self.assertEqual(self.store.state()['snapshots'][0]['account_details']['name'],'QA A')
        self.assertEqual(self.balance(self.a),'115000000')
        self.store=P01Store(self.path)
        self.assertEqual(self.get(self.a)['name'],'Renamed by QA');self.assertEqual(self.finance(),before)
        for patch in ({'opening':'99999999'},{'reference':'999888'},{'effective_date':'2026-09-30'},{'opening_source':'Different basis'}):
            self.reject('account-edit',account=self.a,name='Renamed by QA',**patch)
        self.reject('account-delete',account=self.a,confirm=True,reason='Cannot delete published history')

    def test_04_soft_delete_requires_confirmation_and_restores(self):
        self.reject('account-delete',account=self.a,confirm=False,reason='QA deletion')
        original=copy.deepcopy(self.get(self.a))
        self.act('account-delete',account=self.a,confirm=True,reason='')
        self.assertEqual(self.get(self.a)['history'][-1]['reason'],'Tạo nhầm')
        self.assertEqual(self.get(self.a)['status'],'DELETED')
        self.assertEqual(self.get(self.b).get('status','ACTIVE'),'ACTIVE')
        self.reject('account-edit',account=self.a,name='Should not edit deleted')
        self.reject('import',account=self.a,filename='01-first.xlsx',content=base64.b64encode(self.files['01-first.xlsx']).decode())
        self.store=P01Store(self.path);self.assertEqual(self.get(self.a)['status'],'DELETED')
        self.act('account-restore',account=self.a,reason='Restore mistakenly hidden account')
        self.assertEqual(self.get(self.a)['status'],'ACTIVE')
        for key in ('id','reference','opening','effective_date','opening_source','name'):self.assertEqual(self.get(self.a)[key],original[key])
        self.publish('01-first.xlsx');self.assertEqual(self.balance(self.a),'115000000')

    def test_05_staged_evidence_cannot_be_deleted(self):
        batch=self.stage('01-first.xlsx');before=self.finance()
        self.reject('account-delete',account=self.a,confirm=True,reason='No published movement yet but source exists')
        self.act('account-archive',account=self.a,confirm=True,reason='Retain staged evidence')
        self.assertEqual(self.finance(),before)
        self.reject('publish',batch=batch)
        self.reject('recheck-import',batch=batch)
        self.reject('dismiss-import',batch=batch,reason='Not while archived')
        self.act('account-restore',account=self.a,reason='Continue import')
        self.act('publish',batch=batch);self.assertEqual(self.balance(self.a),'115000000')

    def test_06_archive_used_is_readonly_and_restart_restorable(self):
        self.publish('01-first.xlsx');self.act('approve',account=self.a,confirm_unknown=True)
        before=self.finance();tx=self.store.state()['transactions'][0]['id']
        self.reject('account-archive',account=self.a,confirm=False,reason='QA archive')
        self.act('account-archive',account=self.a,confirm=True,reason='Stop using account')
        self.assertEqual(self.get(self.a)['status'],'ARCHIVED');self.assertEqual(self.finance(),before)
        self.reject('classify',ids=[tx],parts=[dict(category='income')],reason='Archived read only')
        self.reject('approve',account=self.a,confirm_unknown=True,reason='Archived read only')
        self.reject('begin-adjustment',account=self.a,reason='Archived read only')
        self.reject('account-edit',account=self.a,name='Archived read only')
        self.reject('import',account=self.a,filename='02-overlap.xlsx',content=base64.b64encode(self.files['02-overlap.xlsx']).decode())
        self.store=P01Store(self.path);self.assertEqual(self.finance(),before)
        self.act('account-restore',account=self.a,reason='Resume account')
        self.assertEqual(self.finance(),before)
        self.publish('02-overlap.xlsx');self.assertEqual(self.balance(self.a),'112000000')

    def test_07_archive_blocks_transfer_on_either_side(self):
        self.files['out.xlsx']=statement([('01/10/2026','Own transfer out','QA-OUT','10000000','','90000000')],100000000,90000000,end='01/10/2026')
        self.files['in.xlsx']=statement([('01/10/2026','Own transfer in','QA-IN','','10000000','30000000')],20000000,30000000,end='01/10/2026',account='000456')
        self.publish('out.xlsx');self.publish('in.xlsx',self.b)
        out,inc=[t['id'] for t in self.store.state()['transactions']]
        self.act('account-archive',account=self.a,confirm=True,reason='Archive outgoing')
        self.reject('match-transfer',outgoing=out,incoming=inc,reason='Must reject archived outgoing')
        self.act('account-restore',account=self.a,reason='Resume')
        self.act('account-archive',account=self.b,confirm=True,reason='Archive incoming')
        self.reject('match-transfer',outgoing=out,incoming=inc,reason='Must reject archived incoming')
        self.act('account-restore',account=self.b,reason='Resume')
        self.act('match-transfer',outgoing=out,incoming=inc,reason='Both active, match source')
        self.assertEqual(self.balance(self.a),'90000000');self.assertEqual(self.balance(self.b),'30000000')

    def test_10_tracking_fields_revalidate_staging_in_both_directions(self):
        batch=self.stage('01-first.xlsx')
        original=copy.deepcopy(self.store.state()['imports'][-1])
        self.act('account-edit',account=self.a,name='QA A',reference='000999',effective_date='2026-10-02',opening_source='Updated synthetic basis')
        staged=next(b for b in self.store.state()['imports'] if b['id']==batch)
        self.assertEqual(staged['status'],'BLOCKED')
        self.reject('publish',batch=batch)
        self.act('account-edit',account=self.a,name='QA A',reference='000123',effective_date='2026-10-01')
        staged=next(b for b in self.store.state()['imports'] if b['id']==batch)
        self.assertEqual(staged['status'],'STAGED')
        self.assertEqual(staged['content'],original['content'])
        self.act('publish',batch=batch)
        self.assertEqual(self.balance(self.a),'115000000')

    def test_11_bulk_with_archived_account_is_atomic(self):
        self.publish('01-first.xlsx')
        self.files['b.xlsx']=statement([('01/10/2026','QA B debit','QA-B-OUT','1000000','','19000000')],20000000,19000000,end='01/10/2026',account='000456')
        self.publish('b.xlsx',self.b)
        ids=[t['id'] for t in self.store.state()['transactions'] if int(t['signed_amount'])<0]
        self.act('account-archive',account=self.b,confirm=True,reason='Archived target in bulk')
        self.reject('classify',ids=ids,parts=[dict(category='expense')],reason='Must not partly classify A then fail B')
        self.assertTrue(all(not t['allocations'] for t in self.store.state()['transactions']))

    def test_09_deleted_reference_cannot_create_restore_collision(self):
        self.act('account-delete',account=self.a,confirm=True,reason='QA collision setup')
        before=copy.deepcopy(self.store.state())
        try:self.account('Potential duplicate','000123','100000000')
        except Exception:
            self.assertEqual(self.store.state(),before)
            self.act('account-restore',account=self.a,reason='Original reference reserved')
        else:
            self.reject('account-restore',account=self.a,reason='Must not create duplicate active reference')
        active=[a for a in self.store.state()['accounts'] if a.get('status','ACTIVE')=='ACTIVE']
        self.assertEqual(len({a['reference'] for a in active}),len(active))

    def test_08_invalid_edits_are_atomic_and_references_unique(self):
        for patch in ({'name':''},{'reference':'000456'},{'opening':'-1'},{'effective_date':'not-a-day'},{'opening_source':''}):
            data=dict(account=self.a,name='QA A');data.update(patch);self.reject('account-edit',**data)

    def august_source(self):
        self.files['august.xlsx']=statement([('01/08/2026','QA August receipt','AUG-IN','','20000000','120000000'),('02/08/2026','QA August expense','AUG-OUT','5000000','','115000000')],100000000,115000000,start='01/08/2026',end='02/08/2026')
        self.act('account-edit',account=self.a,name='QA A',effective_date='2026-10-09')
        batch=self.stage('august.xlsx')
        self.assertEqual(self.store.state()['imports'][-1]['status'],'BLOCKED')
        self.act('dismiss-import',batch=batch,reason='Wrong tracking date, temporarily exclude')
        self.act('account-edit',account=self.a,name='QA A',effective_date='2026-07-09')
        return batch

    def test_12_reopen_dismissed_source_revalidates_without_autopublish(self):
        batch=self.august_source()
        dismissed=copy.deepcopy(next(b for b in self.store.state()['imports'] if b['id']==batch))
        self.assertEqual(dismissed['status'],'DISMISSED')
        self.assertTrue(dismissed['issues'])
        current=next(b for b in self.store.view()['state']['imports'] if b['id']==batch)
        self.assertEqual(current['current_issues'],[])
        self.assertEqual(current['issues'],dismissed['issues'])
        self.assertEqual(len(self.store.state()['transactions']),0)
        self.act('reopen-import',batch=batch,reason='Tracking corrected; review same source again')
        reopened=next(b for b in self.store.state()['imports'] if b['id']==batch)
        self.assertEqual(reopened['status'],'STAGED');self.assertEqual(reopened['issues'],[])
        self.assertEqual(reopened['review_history'][-1]['previous_issues'],dismissed['issues'])
        for key in ('id','content','sha256','rows'):self.assertEqual(reopened[key],dismissed[key])
        self.assertEqual(len(self.store.state()['transactions']),0)
        self.act('publish',batch=batch)
        self.assertEqual(self.balance(self.a),'115000000')
        report=next(r for r in self.store.view()['reports'] if r['account']==self.a)
        self.assertEqual([(p['start'],p['end']) for p in report['source_periods']],[('2026-08-01','2026-08-02')])
        self.assertIn('Chỉ xác nhận các kỳ nguồn',report['coverage_note'])
        self.assertEqual(report['coverage_gaps'],[{'start':'2026-07-09','end':'2026-07-31'}])
        self.assertEqual(len(self.store.state()['imports']),1)

    def test_14_same_file_reimport_gives_actionable_reopen_error(self):
        batch=self.august_source();before=copy.deepcopy(self.store.state())
        with self.assertRaisesRegex(Exception,'Đưa lại vào kiểm tra'):
            self.act('import',account=self.a,filename='august.xlsx',content=base64.b64encode(self.files['august.xlsx']).decode())
        self.assertEqual(self.store.state(),before)
        self.assertEqual(len(self.store.state()['imports']),1)
        self.assertEqual(self.store.state()['imports'][0]['id'],batch)

    def test_13_archived_account_rejects_reopening_dismissed_source(self):
        batch=self.august_source()
        self.act('account-archive',account=self.a,confirm=True,reason='Readonly account')
        self.reject('reopen-import',batch=batch,reason='Must remain read only')
        self.assertEqual(len(self.store.state()['transactions']),0)

if __name__=='__main__':unittest.main()
