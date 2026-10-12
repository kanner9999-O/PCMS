import base64
import copy
import tempfile
import unittest
from decimal import Decimal
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError
from p01_fixtures import statement

ROWS=[('02/09/2026','Com trua','C1','450000','','999550000'),('03/09/2026','Ban A tra lai','C2','','300000','999850000'),('10/09/2026','Mua do chung','C3','100000','','999750000'),
      ('24/09/2026','NGUYEN BA DUNG ck ket','L1','500000000','','499750000'),('24/09/2026','ck','L2','','200000000','699750000'),('24/09/2026','ck','L3','','300000000','999750000'),
      ('28/09/2026','NGUYENN HUU TU CHUYEN TIEN','U1','','200000000','1199750000'),('29/09/2026','Chua phan loai chi','U2','20000','','1199730000')]

def D_(x):return Decimal(str(x))

class P17Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name);self.build()
    def tearDown(self):self.tmp.cleanup()
    def act(self,a,**d):return self.store.apply(a,d,str(uuid4()))
    def err(self,f,*a,**k):
        with self.assertRaises(ValidationError):f(*a,**k)
    def tx(self,ref):return next(t for t in self.store.state()['transactions'] if t['reference']==ref)
    def review(self,s=None,**d):return self.store.classification_review(dict(account=self.account,**d),s)
    def group(self,r,name):return next(g for g in r['groups'] if g['name']==name)
    def classify(self,refs,parts):self.act('classify',ids=[self.tx(r)['id'] for r in refs],parts=parts)
    def build(self):
        self.act('account',name='QA kiểm tra',reference='000123',opening='1000000000',effective_date='2026-09-01',opening_source='QA');self.account=self.store.state()['accounts'][0]['id']
        self.act('import',account=self.account,filename='k.xlsx',content=base64.b64encode(statement(ROWS,1000000000,1199730000,start='01/09/2026',end='30/09/2026')).decode());self.act('publish',batch=self.store.state()['imports'][-1]['id'])
        self.act('category-create',name='Ăn uống',description='',parent='expense');self.act('category-create',name='Đi lại',description='',parent='expense')
        nodes={n['name']:n['id'] for n in self.store.view()['categories']['nodes']};self.eat,self.go=nodes['Ăn uống'],nodes['Đi lại']
        self.classify(['C1'],[dict(category='expense',node=self.eat)]);self.classify(['C2'],[dict(category='expense',node=self.eat)])
        self.classify(['C3'],[dict(category='expense',node=self.eat,amount='60000'),dict(category='expense',node=self.go,amount='40000')])
        self.act('object-quick-create',kind='LOAN',party_name='Kết',name='Kết');self.loan=next(p['id'] for p in self.store.state()['profiles'] if p['name']=='Kết' and p['kind']=='LOAN')
        self.classify(['L1','L2','L3'],[dict(category='principal',profile=self.loan)])

    def test_groups_rows_totals_and_unclassified(self):
        r=self.review();self.assertEqual((r['summary']['transactions'],r['summary']['classified'],r['summary']['unclassified']),(8,6,2))
        k=self.group(r,'Gốc vay · Kết');self.assertEqual((k['transactions'],D_(k['in']),D_(k['out'])),(3,500000000,500000000));self.assertEqual([x['direction'] for x in k['rows']].count('IN'),2)
        self.assertEqual({x['reference'] for x in k['rows']},{'L1','L2','L3'});self.assertTrue(all(x['object']=='Kết' for x in k['rows']))
        eat=self.group(r,'Chi tiêu › Ăn uống');self.assertEqual((eat['transactions'],D_(eat['out']),D_(eat['in']),D_(eat['net_spend'])),(3,510000,300000,210000))
        self.assertEqual({x['reference']:x['label'] for x in eat['rows']},{'C1':'Chi tiêu › Ăn uống','C2':'Hoàn chi tiêu','C3':'Chi tiêu › Ăn uống'})
        go=self.group(r,'Chi tiêu › Đi lại');self.assertEqual((go['transactions'],D_(go['out'])),(1,40000))
        for g,ref,part in ((eat,'C3','60000'),(go,'C3','40000')):
            row=next(x for x in g['rows'] if x['reference']==ref);self.assertEqual((row['amount'],row['tx_amount'],row['split']),(part,'100000',True))
        un=r['groups'][-1];self.assertEqual((un['name'],un['unclassified'],un['transactions'],D_(un['in']),D_(un['out'])),('Chưa phân loại',True,2,200000000,20000));self.assertEqual({x['reference'] for x in un['rows']},{'U1','U2'})
        self.assertTrue(all(x['classified_at'] is None for x in un['rows']))
        self.assertEqual(sum(x['sources']>=1 for g in r['groups'] for x in g['rows']),len([x for g in r['groups'] for x in g['rows']]))
        self.assertEqual(sum(D_(g['in']) for g in r['groups']),D_(r['summary']['in']));self.assertEqual(sum(D_(g['out']) for g in r['groups']),D_(r['summary']['out']))

    def test_recent_first_ordering_and_recent_flag(self):
        r=self.review();names=[g['name'] for g in r['groups']];self.assertEqual(names[0],'Gốc vay · Kết');self.assertEqual(names[-1],'Chưa phân loại')               # vừa phân loại cuối cùng → trên đầu
        state=copy.deepcopy(self.store.state())
        for t in state['transactions']:
            ref=t['reference'];stamp={'C1':'2026-10-12T01:00:00+00:00','C2':'2026-10-12T02:00:00+00:00','C3':'2026-10-12T03:00:00+00:00','L1':'2026-10-12T04:00:00+00:00','L2':'2026-10-12T05:00:00+00:00','L3':'2026-10-12T04:30:00+00:00'}.get(ref)
            if stamp:t['classification_history'][-1]['at']=stamp
        r=self.review(state);self.assertEqual([g['name'] for g in r['groups']],['Gốc vay · Kết','Chi tiêu › Ăn uống','Chi tiêu › Đi lại','Chưa phân loại'])                    # nhóm theo lần phân loại mới nhất; C3 tách nên hai nhóm hòa 03:00 → theo tên
        self.assertEqual([x['reference'] for x in self.group(r,'Gốc vay · Kết')['rows']],['L2','L3','L1']);self.assertEqual([x['reference'] for x in self.group(r,'Chi tiêu › Ăn uống')['rows']],['C3','C2','C1'])
        old=copy.deepcopy(state)
        for t in old['transactions']:
            if t['reference']=='C1':t['classification_history'][-1]['at']='2026-01-01T00:00:00+00:00'
        r=self.review(old);flags={x['reference']:x['recent'] for g in r['groups'] for x in g['rows'] if g['name']!='Chưa phân loại'}
        self.assertTrue(flags['C1'] is False)                                                                                                       # đã quá 24 giờ

    def test_scopes_recent_and_range(self):
        state=copy.deepcopy(self.store.state())
        for t in state['transactions']:
            if t['reference'] in {'C1','C2'}:t['classification_history'][-1]['at']='2026-01-01T00:00:00+00:00'
        rec=self.review(state,scope='recent');refs={x['reference'] for g in rec['groups'] for x in g['rows']};self.assertEqual(refs,{'C3','L1','L2','L3'});self.assertFalse(any(g['unclassified'] for g in rec['groups']))
        self.assertEqual((rec['summary']['transactions'],rec['reconciled'],rec['scope']['mode']),(4,True,'recent'))
        day=self.review(scope='range',start='2026-09-24',end='2026-09-24');self.assertEqual(({x['reference'] for g in day['groups'] for x in g['rows']},day['summary']['transactions']),({'L1','L2','L3'},3))
        edge=self.review(scope='range',start='2026-09-03',end='2026-09-10');self.assertEqual({x['reference'] for g in edge['groups'] for x in g['rows']},{'C2','C3'})                  # hai đầu bao gồm
        open_end=self.review(scope='range',start='2026-09-28');self.assertEqual({x['reference'] for g in open_end['groups'] for x in g['rows']},{'U1','U2'})
        for bad in (dict(scope='range',start='2026-10-01',end='2026-09-01'),dict(scope='range',start='bad'),dict(scope='range'),dict(scope='lạ')):self.err(self.review,**bad)
        self.err(self.store.classification_review,dict(account='khong-co'))

    def test_checks_reconcile_and_tamper(self):
        r=self.review();self.assertTrue(r['reconciled']);self.assertEqual({k:v['ok'] for k,v in r['checks'].items()},{'transactions':True,'money_in':True,'money_out':True});self.assertEqual(r['checks']['transactions']['source'],8)
        bad=copy.deepcopy(self.store.state());next(t for t in bad['transactions'] if t['reference']=='L2')['allocations'][0]['amount']='199000000'
        r2=self.review(bad);self.assertFalse(r2['reconciled']);self.assertFalse(r2['checks']['money_in']['ok']);self.assertEqual(D_(r2['checks']['money_in']['difference']),-1000000);self.assertTrue(r2['checks']['money_out']['ok'])
        self.assertEqual(self.review()['reconciled'],True)

    def test_approved_status_custom_root_empty_and_read_only(self):
        self.act('approve',account=self.account,confirm_unknown=True,reason='Duyệt');r=self.review();self.assertEqual({x['status'] for g in r['groups'] for x in g['rows']},{'APPROVED'})
        self.act('category-create',name='Kinh doanh nhỏ',type='expense');biz=next(n['id'] for n in self.store.view()['categories']['nodes'] if n['name']=='Kinh doanh nhỏ')
        self.act('begin-adjustment',account=self.account);self.classify(['U2'],[dict(category='expense',node=biz)])
        r=self.review();g=self.group(r,'Kinh doanh nhỏ');self.assertEqual((g['type'],g['transactions'],D_(g['net_spend'])),('expense',1,20000));self.assertEqual(g['rows'][0]['status'],'APPROVED')                   # giao dịch đã nằm trong bản duyệt (phân loại lại đang chờ duyệt bản mới)
        self.assertEqual(r['groups'][0]['name'],'Kinh doanh nhỏ');self.assertEqual(r['summary']['unclassified'],1)
        self.act('account',name='Trống',reference='000999',opening='0',effective_date='2026-09-01',opening_source='QA');empty=self.store.state()['accounts'][1]['id']
        e=self.store.classification_review(dict(account=empty));self.assertTrue(e['empty']);self.assertEqual((e['groups'],e['summary']['transactions']),([],0));self.assertTrue(e['reconciled'])
        events=self.store.backup()['events'];self.review();self.review(scope='recent');self.assertEqual(self.store.backup()['events'],events)
