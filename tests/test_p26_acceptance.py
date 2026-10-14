import tempfile
import unittest
from decimal import Decimal
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError
from p01_fixtures import statement
import test_p24_acceptance as base

D_=lambda x:Decimal(str(x))
b64=base.b64

class P26Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name)
        self.act('account',name='QA preview',reference='000123',opening='1000000',effective_date='2026-07-09',opening_source='QA');self.a=self.store.state()['accounts'][0]['id']
    def tearDown(self):self.tmp.cleanup()
    def act(self,a,**d):return self.store.apply(a,d,str(uuid4()))
    def stage(self,raw,name):
        self.act('import',account=self.a,filename=name,content=b64(raw));return self.store.state()['imports'][-1]
    def prev(self,b):return self.store.source_preview(dict(batch=b['id']))

    def test_46_preview_lists_only_new_rows_after_anchor(self):
        b=self.stage(base.F44,'44.xlsx');self.act('publish',batch=b['id']);b=self.stage(base.F46,'46.xlsx');p=self.prev(b)
        self.assertEqual((p['anchor']['kind'],p['anchor']['reference'],p['anchor']['balance'],p['new_count'],p['duplicate_count']),('LAST_TRANSACTION','R4','1011000',3,3))
        self.assertEqual([(r['reference'],r['computed_balance'],r['reported_balance'],r['ok'],r['direction']) for r in p['rows']],[('N1','953000','953000',True,'OUT'),('N2','853000','853000',True,'OUT'),('N3','843000','843000',True,'OUT')])
        self.assertEqual((D_(p['totals']['out']),D_(p['totals']['in']),p['expected_closing'],p['file_closing'],p['closing_ok'],p['all_ok']),(168000,0,'843000','843000',True,True))
        before=len(self.store.state()['transactions']);self.act('publish',batch=b['id']);self.assertEqual(len(self.store.state()['transactions'])-before,p['new_count'])      # số dòng preview = số dòng được ghi

    def test_first_file_anchor_is_opening_and_duplicates_only(self):
        b=self.stage(base.F44,'44.xlsx');p=self.prev(b);self.assertEqual((p['anchor']['kind'],p['anchor']['balance'],p['new_count'],p['expected_closing'],p['all_ok']),('OPENING','1000000',4,'1011000',True))
        self.act('publish',batch=b['id']);only=statement([base.R2,base.R3,base.R4],900000,1011000,start='15/08/2026',end='29/09/2026');b2=self.stage(only,'only.xlsx');p2=self.prev(b2)
        self.assertEqual((p2['rows'],p2['new_count'],p2['duplicate_count'],p2['closing_ok']),([],0,3,True))

    def test_mismatch_row_flagged_and_closing(self):
        b=self.stage(base.F44,'44.xlsx');self.act('publish',batch=b['id'])
        b=self.stage(base.F46,'46.xlsx')
        st=self.store.state();batch=next(x for x in st['imports'] if x['id']==b['id'])        # giả lập số dư file lệch ở một dòng để kiểm cờ ✘ (không đi qua nhập thật)
        s=self.store.state();next(x for x in s['imports'] if x['id']==b['id'])['rows'][4]['reported_balance']='852999'
        p=self.store.source_preview(dict(batch=b['id']),s);self.assertEqual([r['ok'] for r in p['rows']],[True,False,True]);self.assertFalse(p['all_ok'])

    def test_blocked_published_dismissed_rejected(self):
        b=self.stage(base.F44,'44.xlsx');self.act('publish',batch=b['id'])
        with self.assertRaises(ValidationError):self.prev(b)                                    # đã ghi
        gap=statement([('30/09/2026','Hở','G1','1000','','799000')],800000,799000,start='30/09/2026',end='30/09/2026');g=self.stage(gap,'gap.xlsx');self.assertEqual(g['status'],'BLOCKED')
        with self.assertRaises(ValidationError):self.prev(g)
        self.act('dismiss-import',batch=g['id'],reason='x')
        with self.assertRaises(ValidationError):self.prev(g)
        with self.assertRaises(ValidationError):self.store.source_preview(dict(batch='nope'))

    def test_read_only(self):
        b=self.stage(base.F44,'44.xlsx');n=len(self.store.events());self.prev(b);self.assertEqual(len(self.store.events()),n)

if __name__=='__main__':unittest.main()
