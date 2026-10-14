import tempfile
import unittest
from decimal import Decimal
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError
from p01_fixtures import statement
import test_p24_acceptance as base

def D_(x):return Decimal(str(x))
b64=base.b64

class P25Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name)
        self.act('account',name='QA lịch sử',reference='000123',opening='1000000',effective_date='2026-07-09',opening_source='QA');self.a=self.store.state()['accounts'][0]['id']
    def tearDown(self):self.tmp.cleanup()
    def act(self,a,**d):return self.store.apply(a,d,str(uuid4()))
    def err(self,**d):
        with self.assertRaises(ValidationError):self.store.account_history(dict(account=self.a,**d))
    def pub(self,raw,name):
        self.act('import',account=self.a,filename=name,content=b64(raw));b=self.store.state()['imports'][-1];self.assertEqual(b['status'],'STAGED',b['issues']);self.act('publish',batch=b['id'])
    def hist(self,**d):return self.store.account_history(dict(account=self.a,**d))
    def many(self,count,start_balance=1000000,ref='M'):
        rows=[];bal=start_balance
        for i in range(count):
            bal-=1000;rows.append((f'{1+i%28:02d}/09/2026',f'Chi {i}',f'{ref}{i:03d}','1000','',str(bal)))
        return statement(rows,start_balance,bal,start='01/09/2026',end='28/09/2026'),bal

    def test_milestone_default_ten_last_and_since(self):
        raw,bal=self.many(25);self.pub(raw,'big.xlsx');self.act('approve',account=self.a,confirm_unknown=True,reason='')
        h=self.hist();self.assertEqual((h['reference']['kind'],h['reference']['reference'],h['reference']['balance'],h['total'],len(h['rows']),h['page']['has_more']),('MILESTONE','M024',str(bal),25,10,True))
        self.assertEqual([r['reference'] for r in h['rows']],[f'M{i:03d}' for i in range(24,14,-1)]);self.assertTrue(all(not r['after_milestone'] for r in h['rows']))
        self.assertEqual(h['rows'][0]['balance'],str(bal));self.assertEqual((h['rows'][0]['label'],h['rows'][0]['file']),('Chưa phân loại','big.xlsx'));self.assertEqual(h['since_milestone'],{'count':0,'unclassified':0})
        p2=self.hist(offset=10);self.assertEqual(([r['reference'] for r in p2['rows']][0],len(p2['rows'])),('M014',10));self.assertEqual(len(self.hist(offset=20)['rows']),5)
        self.assertEqual(len(self.hist(limit=200)['rows']),25)

    def test_no_milestone_uses_last_transaction(self):
        self.assertEqual((self.hist()['reference']['kind'],self.hist()['rows'],self.hist()['total']),('NONE',[],0))
        self.pub(base.F44,'44.xlsx');h=self.hist();self.assertEqual((h['reference']['kind'],h['reference']['reference'],h['milestone'],h['total']),('LAST_TRANSACTION','R4',None,4))

    def test_after_milestone_scope_and_files(self):
        self.pub(base.F44,'44.xlsx');self.act('approve',account=self.a,confirm_unknown=True,reason='');self.pub(base.F46,'46.xlsx')
        h=self.hist();self.assertEqual((h['total'],[r['reference'] for r in h['rows']],h['since_milestone']),(4,['R4','R3','R2','R1'],{'count':3,'unclassified':3}))
        al=self.hist(scope='all');self.assertEqual((al['total'],[r['reference'] for r in al['rows']][:4],[r['after_milestone'] for r in al['rows']][:4]),(7,['N3','N2','N1','R4'],[True,True,True,False]))
        f={x['filename']:x for x in h['files']};self.assertEqual((f['44.xlsx']['after_milestone'],f['46.xlsx']['after_milestone'],f['46.xlsx']['status'],f['44.xlsx']['rows']),(False,True,'PUBLISHED',4))
        self.assertEqual([x['filename'] for x in h['files']],['44.xlsx','46.xlsx'])                         # theo kỳ

    def test_filters_and_totals(self):
        self.pub(base.F44,'44.xlsx');self.pub(base.F46,'46.xlsx')
        r=self.hist(scope='all',direction='OUT',limit=200);self.assertEqual((r['total'],D_(r['totals']['out']),D_(r['totals']['in'])),(6,D_(100000+50000+39000+58000+100000+10000),0))
        r=self.hist(scope='all',direction='IN');self.assertEqual((r['total'],[x['reference'] for x in r['rows']],D_(r['totals']['in'])),(1,['R2'],200000))
        r=self.hist(scope='all',start='2026-09-28',end='2026-09-29',limit=200);self.assertEqual([x['reference'] for x in r['rows']],['N2','N1','R4','R3']);self.assertEqual(D_(r['totals']['out']),50000+39000+58000+100000)
        r=self.hist(scope='all',start='2026-09-29',direction='OUT',limit=200);self.assertEqual(r['total'],4)
        self.assertEqual(self.hist(scope='all',start='2027-01-01')['total'],0)
        self.assertEqual(self.hist(scope='all',limit=200)['total'],len(self.store.state()['transactions']))
        for bad in (dict(start='bad'),dict(end='2026-13-01'),dict(start='2026-09-30',end='2026-09-01'),dict(direction='X'),dict(scope='x'),dict(limit=0),dict(limit=201),dict(offset=-1),dict(limit='abc')):self.err(**bad)
        with self.assertRaises(ValidationError):self.store.account_history(dict(account='nope'))

    def test_continuity_of_incoming_files(self):
        self.pub(base.F44,'44.xlsx')
        self.act('import',account=self.a,filename='46.xlsx',content=b64(base.F46));c=self.hist()['continuity'];self.assertEqual(len(c),1)
        self.assertEqual((c[0]['link'],c[0]['ok'],c[0]['new_count'],c[0]['duplicate_count'],c[0]['closing_ok'],c[0]['expected_opening'],c[0]['issues']),('CONTAINS_TAIL',True,3,3,True,'1011000',[]))
        cont=statement([('30/09/2026','Chi tiep','C1','11000','','1000000')],1011000,1000000,start='30/09/2026',end='30/09/2026');self.act('import',account=self.a,filename='cont.xlsx',content=b64(cont))
        gap=statement([('30/09/2026','Hở','G1','1000','','799000')],800000,799000,start='30/09/2026',end='30/09/2026');self.act('import',account=self.a,filename='gap.xlsx',content=b64(gap))
        c={x['filename']:x for x in self.hist()['continuity']}
        self.assertEqual((c['cont.xlsx']['link'],c['cont.xlsx']['ok']),('OPENING_MATCH',True))
        g=c['gap.xlsx'];self.assertEqual((g['link'],g['ok'],g['status'],g['file_opening'],g['expected_opening']),('NONE',False,'BLOCKED','800000','1011000'));self.assertTrue(any('chưa nối tiếp' in i for i in g['issues']))
        self.act('publish',batch=next(x['batch'] for x in self.hist()['continuity'] if x['filename']=='46.xlsx'));self.assertEqual({x['filename'] for x in self.hist()['continuity']},{'cont.xlsx','gap.xlsx'})  # đã ghi thì không còn trong danh sách chờ

    def test_read_only(self):
        self.pub(base.F44,'44.xlsx');n=len(self.store.events());self.hist(scope='all');self.hist();self.assertEqual(len(self.store.events()),n)

if __name__=='__main__':unittest.main()
