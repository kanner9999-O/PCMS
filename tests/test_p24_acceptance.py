import base64
import copy
import tempfile
import unittest
from decimal import Decimal
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError
from p01_fixtures import statement

def D_(x):return Decimal(str(x))
b64=lambda raw:base64.b64encode(raw).decode()

# Mô phỏng file (44) → (46): (44) dừng giữa ngày 29/09; (46) chồng lên rồi thêm giao dịch cùng ngày và các ngày sau.
R1=('01/08/2026','Chi A','R1','100000','','900000');R2=('15/08/2026','Thu B','R2','','200000','1100000')
R3=('28/09/2026','Chi C','R3','50000','','1050000');R4=('29/09/2026','Chi D','R4','39000','','1011000')
N1=('29/09/2026','Chi cuoi ngay 1','N1','58000','','953000');N2=('29/09/2026','Chi cuoi ngay 2','N2','100000','','853000');N3=('30/09/2026','Chi ngay sau','N3','10000','','843000')
F44=statement([R1,R2,R3,R4],1000000,1011000,start='01/08/2026',end='29/09/2026')
F46=statement([R2,R3,R4,N1,N2,N3],900000,843000,start='15/08/2026',end='30/09/2026')

class P24Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name)
        self.act('account',name='QA nối tiếp',reference='000123',opening='1000000',effective_date='2026-07-09',opening_source='QA');self.a=self.store.state()['accounts'][0]['id']
    def tearDown(self):self.tmp.cleanup()
    def act(self,a,**d):return self.store.apply(a,d,str(uuid4()))
    def err(self,a,*patterns,**d):
        with self.assertRaises(ValidationError) as cm:self.act(a,**d)
        for p in patterns:self.assertIn(p,str(cm.exception))
    def stage(self,raw,name='f.xlsx'):
        self.act('import',account=self.a,filename=name,content=b64(raw));return self.store.state()['imports'][-1]
    def publish(self,raw,name='f.xlsx'):
        b=self.stage(raw,name);self.assertEqual(b['status'],'STAGED',b['issues']);self.act('publish',batch=b['id']);return b
    def txs(self):return [t for t in self.store.state()['transactions'] if t['account']==self.a]
    def ready(self):return next(r for r in self.store.view()['readiness'] if r['account']==self.a)

    def test_44_then_46_overlap_adds_same_day_rows(self):
        self.publish(F44,'44.xlsx');self.assertEqual(len(self.txs()),4)
        b=self.stage(F46,'46.xlsx');self.assertEqual((b['status'],b['issues']),('STAGED',[]));self.assertEqual((b['pending_new_count'] if 'pending_new_count' in b else None),None)
        self.act('publish',batch=b['id']);t=self.txs();self.assertEqual([x['reference'] for x in t],['R1','R2','R3','R4','N1','N2','N3'])
        self.assertEqual(self.store.report(self.store.state(),self.a)['balance'],'843000')
        for ref in ('R2','R3','R4'):self.assertEqual(len(next(x for x in t if x['reference']==ref)['sources']),2)         # dòng trùng liên kết nguồn
        self.assertEqual(len(next(x for x in t if x['reference']=='N1')['sources']),1);self.assertEqual(self.store.view()['reports'][0]['coverage_gaps'],[])

    def test_continues_without_repeating_anchor_and_duplicates_only(self):
        self.publish(F44,'44.xlsx')
        cont=statement([('30/09/2026','Chi tiep','C1','11000','','1000000')],1011000,1000000,start='30/09/2026',end='30/09/2026');self.publish(cont,'cont.xlsx');self.assertEqual(len(self.txs()),5)
        only=statement([R2,R3,R4],900000,1011000,start='15/08/2026',end='29/09/2026');b=self.stage(only,'only.xlsx');self.assertEqual((b['status'],b['issues']),('STAGED',[]))
        self.act('publish',batch=b['id']);self.assertEqual(len(self.txs()),5)

    def test_blocked_when_not_continuous(self):
        self.publish(F44,'44.xlsx')
        gap=statement([('30/09/2026','Hở','G1','1000','','799000')],800000,799000,start='30/09/2026',end='30/09/2026');b=self.stage(gap,'gap.xlsx')
        self.assertEqual(b['status'],'BLOCKED');self.assertIn('chưa nối tiếp',' '.join(b['issues']));self.assertIn('R4',' '.join(b['issues']))
        wrong_tail=statement([R2,R3,('29/09/2026','Khác','X9','10000','','1040000')],900000,1040000,start='15/08/2026',end='29/09/2026');b=self.stage(wrong_tail,'wrong.xlsx')
        self.assertEqual(b['status'],'BLOCKED')
        newfirst=statement([('10/08/2026','Cũ hơn','O1','1000','','1000000'),R2],1001000,1100000,start='10/08/2026',end='15/08/2026');b=self.stage(newfirst,'old.xlsx');self.assertEqual(b['status'],'BLOCKED')
        conflict=statement([R2,('28/09/2026','Chi C','R3','50001','','1049999')],900000,1049999,start='15/08/2026',end='28/09/2026');b=self.stage(conflict,'conf.xlsx');self.assertEqual(b['status'],'BLOCKED');self.assertIn('xung đột',' '.join(b['issues']))
        self.assertEqual(len(self.txs()),4)                                                         # không ghi gì khi bị chặn

    def test_first_file_must_match_opening_for_manual_account(self):
        b=self.stage(statement([('01/08/2026','Chi A','Q1','100000','','899999')],999999,899999,start='01/08/2026',end='01/08/2026'),'bad.xlsx');self.assertEqual(b['status'],'BLOCKED');self.assertIn('số dư đầu tài khoản',' '.join(b['issues']))
        self.assertEqual(self.stage(F44,'44.xlsx')['status'],'STAGED')

    def test_milestone_and_since_milestone(self):
        self.publish(F44,'44.xlsx');self.act('approve',account=self.a,confirm_unknown=True,reason='')
        ms=self.store.state()['snapshots'][0]['milestone'];self.assertEqual((ms['anchor']['reference'],ms['anchor']['date'],ms['balance'],ms['transactions'],ms['unclassified']),('R4','2026-09-29','1011000',4,4))
        r=self.ready();self.assertEqual((r['milestone']['anchor']['reference'],r['since_milestone']),('R4',{'count':0,'unclassified':0}))
        self.publish(F46,'46.xlsx');r=self.ready();self.assertEqual(r['since_milestone'],{'count':3,'unclassified':3})            # N1, N2, N3 nối tiếp sau mốc
        t=next(x for x in self.txs() if x['reference']=='N1');self.act('classify',ids=[t['id']],parts=[{'category':'expense','amount':'58000'}]);self.assertEqual(self.ready()['since_milestone'],{'count':3,'unclassified':2})
        self.act('approve',account=self.a,confirm_unknown=True,reason='Mốc 2');snaps=self.store.state()['snapshots'];self.assertEqual((snaps[1]['milestone']['anchor']['reference'],snaps[1]['milestone']['balance']),('N3','843000'));self.assertEqual(snaps[0]['milestone']['anchor']['reference'],'R4')

    def test_account_from_first_file(self):
        before=len(self.store.state()['accounts'])
        raw=statement([R1,R2],1000000,1100000,start='01/08/2026',end='15/08/2026',account='777888')
        self.act('account-from-file',filename='first.xlsx',content=b64(raw),name='Từ file')
        s=self.store.state();acc=next(a for a in s['accounts'] if a['reference']=='777888')
        self.assertEqual((acc['name'],acc['opening'],acc['effective_date'],len(s['accounts'])),('Từ file','1000000','2026-08-01',before+1));self.assertIn('first.xlsx',acc['opening_source'])
        b=s['imports'][-1];self.assertEqual((b['account'],b['status'],b['issues']),(acc['id'],'STAGED',[]))
        self.err('account-from-file','đã tồn tại',filename='again.xlsx',content=b64(raw),name='Trùng')
        n=len(self.store.state()['accounts']);imports=len(self.store.state()['imports'])
        self.err('account-from-file',filename='bad.xlsx',content=b64(b'not excel'),name='Hỏng');self.err('account-from-file',filename='x.csv',content=b64(raw))
        self.assertEqual((len(self.store.state()['accounts']),len(self.store.state()['imports'])),(n,imports))                       # nguyên tử: không tạo dở dang
        self.act('publish',batch=b['id']);self.assertEqual(self.store.report(self.store.state(),acc['id'])['balance'],'1100000')
        default=statement([R3],1100000,1050000,start='28/09/2026',end='28/09/2026',account='555444');self.act('account-from-file',filename='d.xlsx',content=b64(default))
        self.assertEqual(next(a for a in self.store.state()['accounts'] if a['reference']=='555444')['name'],'Tài khoản 555444')

    def test_read_only(self):
        self.publish(F44,'44.xlsx');n=len(self.store.events());self.store.view();self.store.report(self.store.state(),self.a);self.assertEqual(len(self.store.events()),n)

if __name__=='__main__':unittest.main()
