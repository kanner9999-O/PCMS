"""P05 interest preview assumptions, source checks and audited rate terms."""
import copy
import tempfile
import unittest
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError
from test_p04_acceptance import seed as seed_p04


def seed(store):
    account,ids=seed_p04(store)
    for loan in ids[:3]:
        store.apply('interest-terms',dict(profile=loan,unit='VND_MILLION_DAY',value='500',effective_date='2026-10-01',source='Synthetic rate agreement',reason='QA first rate',acknowledge=True),str(uuid4()))
    return account,ids

class P05Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name);self.account,self.ids=seed(self.store)
    def tearDown(self):self.tmp.cleanup()
    def act(self,action,**data):return self.store.apply(action,data,str(uuid4()))
    def terms(self,**kw):
        return self.act('interest-terms',**(dict(profile=self.ids[0],unit='VND_MILLION_DAY',value='500',effective_date='2026-10-01',source='Agreement',reason='Rate revision',acknowledge=True)|kw))
    def preview(self,**kw):return self.store.interest_preview(dict(profile=self.ids[0],start='2026-10-01',end='2026-10-11',acknowledge=True)|kw)
    def fixture(self,opening,changes=()):
        s=self.store.state();p=next(p for p in s['profiles'] if p['id']==self.ids[0]);p['debt_setup']['opening']=opening
        template=copy.deepcopy(s['transactions'][0]);s['transactions']=[]
        for i,(when,delta,category) in enumerate(changes):
            t=copy.deepcopy(template);t.update(id=str(i),date=when,order=i,signed_amount=str(-int(delta)))
            t['allocations']=[dict(profile=p['id'],category=category,amount=str(abs(int(delta))))];s['transactions'].append(t)
        original=self.store.state;self.store.state=lambda:s
        self.addCleanup(setattr,self.store,'state',original)
        return s
    def test_a38_a39_equivalence_and_fractional_principal(self):
        for opening,end,expected in [('100000000','2026-10-11','500000'),('1500000','2026-10-11','7500'),('100000000','2026-11-01','1550000')]:
            with self.subTest(opening=opening,end=end):
                s=self.fixture(opening);self.assertEqual(self.preview(end=end)['total'],expected)
                p=next(p for p in s['profiles'] if p['id']==self.ids[0]);p['interest_terms'][0].update(unit='PERCENT_30_DAY',value='1.5')
                self.assertEqual(self.preview(end=end)['total'],expected)
                self.doCleanups()
        self.fixture('300000000',[('2026-10-11','-100000000','principal')]);r=self.preview(end='2026-10-16')
        self.assertEqual(r['total'],'2000000');self.assertEqual([x['days'] for x in r['segments']],[10,5])
    def test_same_day_rate_change_interval_cash_and_rounding(self):
        s=self.fixture('100000000',[('2026-10-01','20000000','principal'),('2026-10-01','-30000000','principal'),('2026-10-03','-10000000','principal'),('2026-10-03','-9000','interest')])
        p=next(p for p in s['profiles'] if p['id']==self.ids[0]);p['interest_terms'].append(dict(p['interest_terms'][0],effective_date='2026-10-03',value='1000'))
        r=self.preview(start='2026-10-02',end='2026-10-04');self.assertEqual(r['total'],'125000');self.assertEqual(r['interest_received'],'9000');self.assertEqual([x['principal'] for x in r['segments']],['90000000','80000000'])
        p['debt_setup']['opening']='1000';s['transactions']=[];p['interest_terms']=p['interest_terms'][:1]
        self.assertEqual(self.preview(end='2026-10-02')['total'],'1')
        self.assertEqual(self.preview(end='2026-10-03')['total'],'1')
    def test_missing_invalid_and_read_only(self):
        before=self.store.backup();self.preview();self.assertEqual(self.store.backup(),before)
        for kw in [dict(acknowledge=False),dict(profile=self.ids[3]),dict(start='2026-09-30'),dict(end='2026-10-01')]:
            with self.assertRaises(ValidationError):self.preview(**kw)
        for kw in [dict(value='NaN'),dict(value='Infinity'),dict(value='-1'),dict(source=' '),dict(unit=''),dict(acknowledge=False),dict(effective_date='2026-09-01')]:
            with self.assertRaises(ValidationError):self.terms(**kw)
        s=self.fixture('1',[('2026-10-02','-2','principal')])
        with self.assertRaises(ValidationError):self.preview()
        s['transactions'][0]['date']='2026-09-30'
        with self.assertRaises(ValidationError):self.preview()
        s['transactions'][0]['date']='2026-10-02';s['transactions'][0]['sources']=[]
        with self.assertRaises(ValidationError):self.preview()
        s['transactions']=[];p=next(p for p in s['profiles'] if p['id']==self.ids[0]);p['interest_terms']=[]
        with self.assertRaises(ValidationError):self.preview()
    def test_audit_snapshot_and_backup(self):
        self.act('approve',account=self.account);old=copy.deepcopy(self.store.state()['snapshots'])
        self.terms(value='600');p=next(p for p in self.store.state()['profiles'] if p['id']==self.ids[0])
        self.assertEqual(p['interest_history'][-1]['before']['value'],'500');self.assertEqual(len(p['interest_terms']),1)
        self.assertEqual(self.store.state()['snapshots'],old);self.assertTrue(self.store.view()['readiness'][0]['financial_changed'])
        self.terms(value='700',effective_date='2026-10-05');self.assertEqual(len(self.preview()['segments']),3)
        other=P01Store(self.tmp.name+'/restore');other.restore(self.store.backup(),'restore');self.assertEqual(other.interest_preview(dict(profile=self.ids[0],start='2026-10-01',end='2026-10-11',acknowledge=True)),self.preview())
