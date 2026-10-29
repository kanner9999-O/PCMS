"""Spec 046 (R203–R212, A64): nghiệp vụ Cho vay / Đi vay gắn vào danh mục. Dữ liệu giả theo bảng ví dụ trong spec."""
import base64
import copy
import tempfile
import unittest
from decimal import Decimal
from uuid import uuid4
from pcms.p01 import P01Store
from pcms.core import ValidationError
from pcms.loan_business import lb_accrue
from pcms.reclassify import RECLASS_GRANT
from p01_fixtures import statement

ROWS=[('20/10/2026','Giai ngan Ket','L1','100000000','','900000000'),('22/10/2026','Giai ngan Ket 2','L2','10000000','','890000000'),
      ('22/10/2026','Ket cho vay','L3','','50000000','940000000'),('25/10/2026','Ket tra goc lai','L4','','40150000','980150000'),
      ('26/10/2026','Chi tieu thuong','E1','1000000','','979150000'),('27/10/2026','Tra moi gioi','L5','120000','','979030000'),
      ('29/10/2026','Tuoi tra','L6','','5000000','984030000'),('31/10/2026','Ket tra het','L7','','70360000','1054390000')]

def D(x):return Decimal(str(x))

class Fixture(unittest.TestCase):
    today='2026-11-05'
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=P01Store(self.tmp.name);self.store.lb_today=lambda:self.today;self.build()
    def tearDown(self):self.tmp.cleanup()
    def act(self,a,**d):return self.store.apply(a,d,str(uuid4()))
    def err(self,a,**d):
        with self.assertRaises(ValidationError) as c:self.act(a,**d)
        return str(c.exception)
    def st(self):return self.store.state()
    def tx(self,ref):return next(t for t in self.st()['transactions'] if t['reference']==ref)
    def pid(self,name):return next(p['id'] for p in self.st()['profiles'] if p['name']==name and not p.get('merged_into'))
    def node(self,name):return next(n['id'] for n in self.st()['categories'] if n['name']==name)
    def build(self):
        self.act('account',name='QA',reference='000123',opening='1000000000',effective_date='2026-10-01',opening_source='QA');self.account=self.st()['accounts'][0]['id']
        self.act('import',account=self.account,filename='a.xlsx',content=base64.b64encode(statement(ROWS,1000000000,1054390000,start='01/10/2026',end='31/10/2026')).decode())
        self.act('publish',batch=self.st()['imports'][0]['id'])
        self.act('category-create',name='Hot Debt',type='expense',description='');self.hot=self.node('Hot Debt')
        self.act('category-create',name='Ngắn hạn',parent=self.hot,description='');self.short=self.node('Ngắn hạn')
        self.act('category-create',name='Vay bạn',type='expense',description='');self.borrow=self.node('Vay bạn')
        self.act('category-create',name='Cho vay',type='expense',description='');self.named=self.node('Cho vay')       # tên không mang nghiệp vụ
        self.act('category-object-add',category=self.hot,name='Kết',type='PERSON');self.ket=self.pid('Kết')
        self.act('category-object-add',category=self.hot,name='Tươi',type='PERSON');self.tuoi=self.pid('Tươi')
        self.act('category-object-add',category=self.hot,name='Nhà QA',type='PROPERTY');self.house=self.pid('Nhà QA')
        self.act('category-object-add',category=self.borrow,profile=self.ket)
        for ref in ('L1','L2','L4','L5','L7'):self.cls(ref,self.hot,self.ket)
        self.cls('L3',self.borrow,self.ket);self.cls('L6',self.hot,self.tuoi);self.act('classify',ids=[self.tx('E1')['id']],parts=[dict(category='expense')])
    def cls(self,ref,node,person):self.act('classify',ids=[self.tx(ref)['id']],parts=[dict(category='expense',node=node,profile=person)])
    def set_biz(self,node,typ,reason='QA'):
        p=self.store.lb_category_preview(dict(category=node,type=typ));self.assertEqual(p['blocks'],[],p['blocks'])
        self.act('lb-category-set',category=node,type=typ,reason=reason,review_token=p['review_token']);return p
    def loan(self,node,person,name,rate,code=None,**k):
        self.act('lb-loan-create',category=node,person=person,name=name,rate=rate,tracking_date=k.pop('tracking_date','2026-10-01'),code=code,**k)
        return next(l['id'] for l in self.st()['loans'] if l['name']==name)
    def post(self,ref,lines,reason=None):
        t=self.tx(ref);return self.act('lb-detail-post',source=t['id'],lines=lines,**({'reason':reason} if reason else {}))
    def line(self,loan,component,amount,node=None,person=None):
        l=next(x for x in self.st()['loans'] if x['id']==loan)
        return dict(category=node or l['category'],person=person or l['person'],loan=loan,component=component,amount=str(amount))
    def book(self,as_of=None,category=None):return self.store.loan_book(self.st(),as_of,category)
    def row(self,loan,as_of=None):return next(r for r in self.book(as_of)['loans'] if r['id']==loan)
    def example(self,upto=7):
        """Bảng ví dụ spec 046 bước 1..upto."""
        self.set_biz(self.hot,'RECEIVABLE');self.set_biz(self.borrow,'PAYABLE')
        self.cv1=self.loan(self.hot,self.ket,'Vay tháng 10',500,broker_name='Long',broker_rate=200);self.cv2=self.loan(self.hot,self.ket,'Vay thêm',600)
        self.dv1=self.loan(self.borrow,self.ket,'Kết cho mượn',0)
        steps=[lambda:self.post('L1',[self.line(self.cv1,'principal',100000000)]),lambda:self.post('L2',[self.line(self.cv2,'principal',10000000)]),
               lambda:self.post('L3',[self.line(self.dv1,'principal',50000000)]),lambda:self.post('L4',[self.line(self.cv1,'principal',40000000),self.line(self.cv1,'interest',150000)]),
               lambda:self.post('L5',[self.line(self.cv1,'broker',120000)]),
               lambda:self.post('L7',[self.line(self.cv1,'principal',60000000),self.line(self.cv1,'interest',300000),self.line(self.cv2,'principal',10000000),self.line(self.cv2,'interest',60000)]),
               lambda:self.act('lb-waiver-add',loan=self.cv1,date='2026-10-31',amount='30000',reason='Bớt lãi lẻ')]
        for f in steps[:upto]:f()


class InterestEngine(unittest.TestCase):
    def ev(self,*items):
        out={}
        for d,disb,rep in items:out.setdefault(d,dict(disb=D(0),repay=D(0)));out[d]['disb']+=D(disb);out[d]['repay']+=D(rep)
        return out
    def test_six_days_inclusive_both_ends(self):
        raw,_,closing,_=lb_accrue(self.ev(('2026-10-20',100000000,0),('2026-10-25',0,100000000)),'500','2026-11-30')
        self.assertEqual((raw,closing),(D(300000),D(0)))
    def test_partial_repayment_reduces_base_from_next_day(self):
        e=self.ev(('2026-10-20',100000000,0),('2026-10-25',0,40000000))
        self.assertEqual(lb_accrue(e,'500','2026-10-25')[0],D(300000));self.assertEqual(lb_accrue(e,'500','2026-10-26')[0]-D(300000),D(30000))
        self.assertEqual(lb_accrue(e,'500','2026-10-30')[0],D(450000))
    def test_rounding_once_on_cumulative_total_half_up(self):
        raw=lb_accrue(self.ev(('2026-10-01',1234567,0)),'500','2026-10-03')[0];self.assertEqual(raw,D('1851.8505'))
        self.assertEqual(raw.quantize(D(1),rounding='ROUND_HALF_UP'),D(1852))
    def test_zero_rate_same_day_and_view_before_start(self):
        e=self.ev(('2026-10-20',100000000,100000000))
        self.assertEqual(lb_accrue(e,'0','2026-12-01')[0],D(0));self.assertEqual(lb_accrue(e,'500','2026-12-01')[0],D(50000))   # cùng ngày: 1 ngày lãi
        self.assertEqual(lb_accrue(self.ev(('2026-10-20',1000000,0)),'500','2026-10-19')[0],D(0))
    def test_broker_uses_same_base(self):
        _,b,_,_=lb_accrue(self.ev(('2026-10-20',100000000,0),('2026-10-25',0,40000000)),'500','2026-10-25','200');self.assertEqual(b,D(120000))


class US1CategoryBusiness(Fixture):
    def test_inheritance_and_child_different_blocked(self):
        self.set_biz(self.hot,'RECEIVABLE');n=next(x for x in self.store.view()['categories']['nodes'] if x['id']==self.short)
        self.assertEqual((n['business']['type'],n['business']['own'],n['business']['from']),('RECEIVABLE',False,self.hot))
        p=self.store.lb_category_preview(dict(category=self.short,type='PAYABLE'));self.assertIn('PARENT_DIFFERENT',[b['code'] for b in p['blocks']])
        self.err('lb-category-set',category=self.short,type='PAYABLE',reason='x',review_token=p['review_token'])
        self.assertIn('INHERITED',[b['code'] for b in self.store.lb_category_preview(dict(category=self.short,type='RECEIVABLE'))['blocks']])

    def test_parent_blocked_when_child_has_other_business_and_names_branch(self):
        self.set_biz(self.short,'PAYABLE');p=self.store.lb_category_preview(dict(category=self.hot,type='RECEIVABLE'))
        b=next(x for x in p['blocks'] if x['code']=='CHILD_DIFFERENT');self.assertIn('Hot Debt › Ngắn hạn (Đi vay)',b['message'])
        self.err('lb-category-set',category=self.hot,type='RECEIVABLE',reason='x',review_token=p['review_token'])
        self.assertEqual(self.st()['categories'][[n['id'] for n in self.st()['categories']].index(self.short)]['business']['type'],'PAYABLE')   # không ghi đè

    def test_no_inference_from_name_and_no_system_root(self):
        self.assertIsNone(next(x for x in self.store.view()['categories']['nodes'] if x['id']==self.named)['business'])
        self.assertIsNone(self.store.lb_effective(self.st(),self.named))
        with self.assertRaises(ValidationError):self.store.lb_category_preview(dict(category='principal',type='RECEIVABLE'))

    def test_preview_counts_missing_and_conflicts_and_token(self):
        self.act('classify',ids=[self.tx('E1')['id']],parts=[dict(category='expense',node=self.hot,profile=self.house)],_reclass=RECLASS_GRANT)   # BĐS trong danh mục chưa có nghiệp vụ: hợp lệ
        p=self.store.lb_category_preview(dict(category=self.hot,type='RECEIVABLE'))
        self.assertEqual(p['missing']['count'],6);self.assertEqual(D(p['missing']['out']),D(110120000));self.assertEqual(D(p['missing']['in']),D(115510000))
        self.assertEqual([c['code'] for c in p['conflicts']],['NOT_PERSON']);self.assertEqual([x['name'] for x in p['non_person']],['Nhà QA'])
        self.err('lb-category-set',category=self.hot,type='RECEIVABLE',reason='x',review_token='sai')
        self.err('lb-category-set',category=self.hot,type='RECEIVABLE',review_token=p['review_token'])            # thiếu lý do
        self.act('lb-category-set',category=self.hot,type='RECEIVABLE',reason='Cho vay ngắn',review_token=p['review_token'])
        n=next(x for x in self.st()['categories'] if x['id']==self.hot);self.assertEqual((n['business']['type'],n['business_history'][-1]['reason']),('RECEIVABLE','Cho vay ngắn'))

    def test_clear_blocked_with_details_or_loans_and_move_blocked(self):
        self.set_biz(self.hot,'RECEIVABLE');self.act('lb-category-clear',category=self.hot,reason='thử');self.assertIsNone(self.store.lb_effective(self.st(),self.hot))
        self.set_biz(self.hot,'RECEIVABLE')
        self.act('category-object-add',category=self.short,profile=self.ket);cv=self.loan(self.short,self.ket,'Khoản ngắn',500)
        self.assertIn('khoản vay',self.err('lb-category-clear',category=self.hot,reason='x'))
        self.act('category-create',name='Khác',type='expense',description='');other=self.node('Khác');self.set_biz(other,'PAYABLE')
        self.assertIn('nghiệp vụ',self.err('category-edit',category=self.short,parent=other,reason='chuyển'))

    def test_clear_blocked_by_draft_and_delete_blocked_archive_keeps(self):
        self.example(1)
        self.act('lb-detail-draft',source=self.tx('L2')['id'],lines=[self.line(self.cv2,'principal',1)])
        self.assertIn('giao dịch đã ghi hoặc đang nháp',self.err('lb-category-clear',category=self.hot,reason='x'))
        self.act('category-create',name='Trống',type='expense',description='');empty=self.node('Trống');self.set_biz(empty,'PAYABLE')
        for c in (empty,self.borrow):
            n=next(x for x in self.store.view()['categories']['nodes'] if x['id']==c);self.assertFalse(n['deletable']);self.assertEqual(self.err('category-delete',category=c,reason='x'),n['delete_block'])
        self.assertIn('đã gắn nghiệp vụ vay',next(x for x in self.store.view()['categories']['nodes'] if x['id']==empty)['delete_block'])
        self.act('lb-category-clear',category=empty,reason='x');self.assertIn('kể cả đã gỡ',next(x for x in self.store.view()['categories']['nodes'] if x['id']==empty)['delete_block'])
        before=self.row(self.cv1)['principal'];self.act('category-archive',category=self.short,reason='Thừa')
        self.assertEqual(self.row(self.cv1)['principal'],before)

    def test_child_move_under_other_business_parent_blocked_without_details(self):
        self.act('category-create',name='A',type='expense',description='');a=self.node('A');self.act('category-create',name='A1',parent=a,description='');a1=self.node('A1')
        self.act('category-create',name='B',parent=self.hot,description='');b=self.node('B')
        self.set_biz(a1,'PAYABLE')
        p=self.store.lb_category_preview(dict(category=self.hot,type='RECEIVABLE'));self.act('lb-category-set',category=self.hot,type='RECEIVABLE',reason='x',review_token=p['review_token'])
        self.assertIn('không được khác',self.err('category-edit',category=a1,parent=self.hot,reason='chuyển'))


class US2Loans(Fixture):
    def setUp(self):
        super().setUp();self.set_biz(self.hot,'RECEIVABLE');self.set_biz(self.borrow,'PAYABLE')
    def test_codes_directions_broker(self):
        a=self.loan(self.hot,self.ket,'Một',500,broker_name='Long',broker_rate=200);b=self.loan(self.hot,self.ket,'Hai',600);c=self.loan(self.borrow,self.ket,'Ba',0)
        L={l['id']:l for l in self.st()['loans']}
        self.assertEqual([(L[x]['code'],L[x]['direction']) for x in (a,b,c)],[('CV-0001','RECEIVABLE'),('CV-0002','RECEIVABLE'),('ĐV-0001','PAYABLE')])
        self.assertEqual(L[a]['broker'],dict(name='Long',rate='200'))
        self.assertIn('đã có',self.err('lb-loan-create',category=self.hot,person=self.ket,name='Trùng',rate=0,tracking_date='2026-10-01',code='cv-0001'))
        self.assertIn('Môi giới chỉ',self.err('lb-loan-create',category=self.borrow,person=self.ket,name='X',rate=0,tracking_date='2026-10-01',broker_name='Long',broker_rate=1))
        self.err('lb-loan-create',category=self.hot,person=self.ket,name='X',rate=-1,tracking_date='2026-10-01')
        self.err('lb-loan-create',category=self.hot,person=self.ket,name='X',rate=0,tracking_date='2026-10-05',due_date='2026-10-01')

    def test_person_must_be_member_and_category_must_have_business(self):
        self.act('category-object-add',category=self.named,name='Lạ',type='PERSON')
        self.assertIn('chưa là thành viên',self.err('lb-loan-create',category=self.hot,person=self.pid('Lạ'),name='X',rate=0,tracking_date='2026-10-01'))
        self.assertIn('chưa mang nghiệp vụ',self.err('lb-loan-create',category=self.named,person=self.pid('Lạ'),name='X',rate=0,tracking_date='2026-10-01'))
        self.err('lb-loan-create',category=self.hot,person=self.house,name='X',rate=0,tracking_date='2026-10-01')

    def test_edit_needs_reason_history_rate_correctable_only_before_posting(self):
        # vòng sửa 29/10 (PO review P1): sửa mức lãi chỉ được khi chưa có phát sinh được ghi; sau khi ghi thì lãi lịch sử không đổi
        a=self.loan(self.hot,self.ket,'Một',500)
        self.err('lb-loan-edit',loan=a,rate=600);self.act('lb-loan-edit',loan=a,rate=600,reason='Nhập sai mức')
        self.assertEqual(self.st()['loans'][0]['history'][-1]['before'],{'rate':'500'})
        self.post('L1',[self.line(a,'principal',100000000)]);self.assertEqual(self.row(a,'2026-10-25')['interest_accrued'],'360000')
        self.err('lb-loan-edit',loan=a,rate=500,reason='Đổi lại');self.assertEqual(self.row(a,'2026-10-25')['interest_accrued'],'360000')
        self.assertIn('trước ngày theo dõi',self.err('lb-loan-edit',loan=a,tracking_date='2026-10-21',reason='x'))


class US3Details(Fixture):
    def test_split_two_loans_principal_and_interest_posts(self):
        self.example(6);t=self.tx('L7');src=self.book()['sources'][t['id']];self.assertEqual(src['status'],'POSTED')
        self.assertEqual((self.row(self.cv1)['principal'],self.row(self.cv2)['principal']),('0','0'))

    def test_incomplete_blocks_post_but_draft_saved_and_book_unchanged(self):
        self.example(5);before=copy.deepcopy(self.book());lines=[self.line(self.cv1,'principal',60000000),self.line(self.cv2,'principal',10000000)]
        self.assertIn('còn 360.000',self.err('lb-detail-post',source=self.tx('L7')['id'],lines=lines))
        self.act('lb-detail-draft',source=self.tx('L7')['id'],lines=lines);after=self.book()
        self.assertEqual([r['principal'] for r in after['loans']],[r['principal'] for r in before['loans']])
        self.assertEqual([r['interest_paid'] for r in after['loans']],[r['interest_paid'] for r in before['loans']])
        self.assertEqual(after['sources'][self.tx('L7')['id']]['status'],'PENDING');self.assertIn('DRAFT',after['sources'][self.tx('L7')['id']]['reasons'])

    def test_wrong_component_or_other_person_loan_blocked(self):
        self.example(0);self.cv_t=self.loan(self.hot,self.tuoi,'Tươi vay',500)
        self.assertIn('không thể là',self.err('lb-detail-post',source=self.tx('L1')['id'],lines=[self.line(self.cv1,'interest',100000000)]))
        self.err('lb-detail-post',source=self.tx('L1')['id'],lines=[dict(self.line(self.cv_t,'principal',100000000),person=self.ket)])
        self.err('lb-detail-post',source=self.tx('L1')['id'],lines=[self.line(self.cv2,'broker',100000000)])            # khoản không có môi giới
        self.err('lb-detail-post',source=self.tx('L3')['id'],lines=[dict(self.line(self.cv1,'principal',50000000),category=self.borrow)])  # khoản khác chiều

    def test_replacement_keeps_current_until_posted_and_void_needs_reason(self):
        self.example(4);sid=self.tx('L4')['id']
        self.act('lb-detail-draft',source=sid,lines=[self.line(self.cv1,'principal',40150000)])
        self.assertEqual(self.row(self.cv1,'2026-10-26')['interest_paid'],'150000');self.assertTrue(self.book()['sources'][sid]['editing'])
        self.assertEqual(self.book()['sources'][sid]['status'],'POSTED')
        self.err('lb-detail-post',source=sid,lines=[self.line(self.cv1,'principal',39150000),self.line(self.cv1,'interest',1000000)])  # thiếu lý do thay bản đã ghi
        self.act('lb-detail-post',source=sid,lines=[self.line(self.cv1,'principal',40050000),self.line(self.cv1,'interest',100000)],reason='Sửa tách')
        det=next(d for d in self.st()['loan_details'] if d['source']==sid);self.assertEqual([v['status'] for v in det['versions']],['POSTED','POSTED']);self.assertIsNone(det['draft'])
        self.assertEqual(self.row(self.cv1,'2026-10-26')['interest_paid'],'100000')
        self.err('lb-detail-void',source=sid);self.act('lb-detail-void',source=sid,reason='Ghi nhầm')
        self.assertEqual(self.book()['sources'][sid]['status'],'PENDING');self.assertEqual(self.row(self.cv1)['repaid'],'0')

    def test_pending_reasons(self):
        self.act('classify',ids=[self.tx('E1')['id']],parts=[dict(category='expense',node=self.hot)],_reclass=RECLASS_GRANT)   # phần cũ, phân loại trước khi gắn nghiệp vụ
        self.set_biz(self.hot,'RECEIVABLE');self.set_biz(self.borrow,'PAYABLE')
        b=self.book();r=lambda ref:b['sources'][self.tx(ref)['id']]['reasons']
        self.assertEqual(r('L6'),['NO_LOAN','NOT_DETAILED']);self.assertEqual(b['pending']['count'],8)
        self.assertEqual(r('E1'),['NO_PERSON'])

    def test_new_parts_only_person_in_business_category(self):
        self.set_biz(self.hot,'RECEIVABLE')
        self.assertIn('chỉ gắn đối tượng loại Người',self.err('classify',ids=[self.tx('E1')['id']],parts=[dict(category='expense',node=self.hot,profile=self.house)]))
        p=self.store.reclassify_preview(dict(transaction=self.tx('E1')['id'],part=0,category=self.hot,profile=self.house));self.assertFalse(p['can_commit'])

    def test_parallel_paths_blocked_after_post(self):
        self.example(4);sid=self.tx('L1')['id']
        self.assertIn('đã ghi nghiệp vụ vay',self.err('classify',ids=[sid],parts=[dict(category='expense')],_reclass=RECLASS_GRANT))
        p=self.store.reclassify_preview(dict(transaction=sid,part=0,category='expense'))
        self.assertTrue(any('đã ghi nghiệp vụ vay' in b['message'] for b in p['blocks']),p['blocks'])
        self.act('category-create',name='Hot 2',type='expense',description='');h2=self.node('Hot 2')
        self.assertIn('đã ghi nghiệp vụ vay',self.err('category-object-move',profile=self.ket,**{'from':self.hot,'to':h2},reason='x'))
        self.assertIn('không gỡ',self.err('category-object-remove',category=self.hot,profile=self.ket,reason='x'))
        self.act('category-object-add',category=h2,name='Kết trùng',type='OBJECT')
        before=copy.deepcopy(self.book()['loans']);self.act('category-object-merge',**{'from':self.pid('Kết trùng'),'into':self.ket},reason='trùng tên');self.assertEqual(self.book()['loans'],before)   # gộp hồ sơ khác vào Kết: không đổi chi tiết đã ghi nên được phép
        self.assertIn('nghiệp vụ',self.err('category-object-remove',category=self.borrow,profile=self.ket,reason='x'))   # Kết có ĐV-0001 tạo từ Vay bạn

    def test_legacy_link_valid_not_double_and_legacy_row_detail(self):
        self.store.require_membership=False
        self.act('profile',kind='LOAN',name='Khoản Kết',party=self.ket);old=self.pid('Khoản Kết')
        self.act('loan-setup',profile=old,direction='RECEIVABLE',opening='0',confirm_zero=True,effective_date='2026-10-01',source='QA',reason='QA')
        self.act('category-create',name='QA cũ',parent='principal',description='');oldcat=self.node('QA cũ')
        self.act('classify',ids=[self.tx('E1')['id']],parts=[dict(category='principal',node=oldcat,profile=old)],_reclass=RECLASS_GRANT)
        self.store.require_membership=True
        p=self.store.lb_category_preview(dict(category=oldcat,type='RECEIVABLE'));self.assertEqual(p['valid']['count'],1);self.assertEqual(D(p['valid']['out']),D(1000000))
        self.assertEqual(self.store.lb_category_preview(dict(category=oldcat,type='PAYABLE'))['conflicts'][0]['code'],'LEGACY_DIRECTION')
        self.act('lb-category-set',category=oldcat,type='RECEIVABLE',reason='x',review_token=p['review_token']);self.set_biz(self.hot,'RECEIVABLE')
        b=self.book();self.assertEqual(b['sources'][self.tx('E1')['id']]['status'],'LEGACY_LINK');self.assertEqual(b['summary']['legacy_loans'],1)
        self.assertEqual(D(b['summary']['legacy_receivable']),D(1000000));self.assertEqual(D(b['summary']['receivable']),D(0))
        # dòng lịch sử cũ trong danh mục nghiệp vụ: bóc tách như giao dịch, không ghi đôi
        cvt=self.loan(self.hot,self.tuoi,'Tươi cũ',0,tracking_date='2026-09-01')     # vòng sửa 29/10: migrate vào danh mục nghiệp vụ cần chọn khoản
        self.act('legacy-import',category=self.hot,profile=self.tuoi,loan=cvt,account=self.account,text="15/09/2026\tTuoi vay cu\tFT9\t2,000,000\t\t1\n")
        e=self.st()['legacy_entries'][-1];self.assertEqual(self.book()['sources'][e['id']]['status'],'PENDING')
        self.act('lb-detail-post',source=e['id'],lines=[self.line(cvt,'principal',2000000)])
        self.assertEqual((self.row(cvt)['principal'],self.book()['sources'][e['id']]['status']),('2000000','POSTED'))
        self.assertIn('đã ghi nghiệp vụ vay',self.err('legacy-void',batch=self.st()['legacy_batches'][-1]['id'],reason='x'))


class US4InterestSettlement(Fixture):
    def test_example_numbers(self):
        self.example(4);r=self.row(self.cv1,'2026-10-25')
        self.assertEqual((r['interest_accrued'],r['interest_paid'],r['interest_outstanding'],r['principal']),('300000','150000','150000','60000000'))
        r=self.row(self.cv1,'2026-10-30');self.assertEqual((r['interest_accrued'],r['interest_outstanding']),('450000','300000'))
        self.assertEqual(self.row(self.cv2,'2026-10-30')['interest_accrued'],'54000')

    def test_full_flow_completion_with_waiver(self):
        self.example(6);r=self.row(self.cv1)
        self.assertEqual((r['principal'],r['interest_accrued'],r['interest_paid'],r['interest_outstanding']),('0','480000','450000','30000'))
        self.assertFalse(r['can_complete']);self.assertIn('30.000',r['complete_blocker'])
        self.err('lb-loan-complete',loan=self.cv1,reason='x')
        self.assertTrue(self.row(self.cv2)['can_complete'],self.row(self.cv2)['complete_blocker'])
        self.act('lb-waiver-add',loan=self.cv1,date='2026-10-31',amount='30000',reason='Bớt lãi lẻ');r=self.row(self.cv1)
        self.assertEqual((r['waived'],r['interest_outstanding']),('30000','0'))
        # Tươi (bước 8) chờ không thuộc phạm vi của Kết: hoàn tất được
        self.assertTrue(self.row(self.cv1)['can_complete'],self.row(self.cv1)['complete_blocker'])
        self.act('lb-loan-complete',loan=self.cv1,reason='Xong');self.assertEqual(self.row(self.cv1)['status'],'COMPLETED')
        self.assertIn('đã hoàn tất',self.err('lb-waiver-add',loan=self.cv1,date='2026-10-31',amount='1',reason='x'))
        self.assertIn('đã hoàn tất',self.err('lb-detail-void',source=self.tx('L7')['id'],reason='x'))
        self.act('lb-loan-reopen',loan=self.cv1,reason='Kiểm lại');self.assertEqual(self.row(self.cv1)['status'],'ACTIVE')
        self.assertTrue(self.row(self.cv2)['can_complete'])

    def test_pending_in_same_person_direction_blocks_completion(self):
        self.example(7);self.act('classify',ids=[self.tx('L6')['id']],parts=[dict(category='expense',node=self.hot,profile=self.ket,loan=self.cv1)],_reclass=RECLASS_GRANT)   # vòng sửa 29/10: phần mới phải chọn khoản
        r=self.row(self.cv1);self.assertFalse(r['can_complete']);self.assertIn('chờ chi tiết',r['complete_blocker']);self.assertTrue(r['caution'])
        self.assertTrue(self.row(self.dv1)['caution'] is False)

    def test_over_principal_and_over_interest_blocked(self):
        self.example(3);sid=self.tx('L4')['id']
        p=self.store.lb_detail_preview(dict(source=sid,lines=[self.line(self.cv1,'principal',40150000)]));self.assertTrue(p['can_post'])
        self.assertEqual(p['impact'][0]['settlement'],'PARTIAL')
        self.assertIn('vượt lãi',self.err('lb-detail-post',source=sid,lines=[self.line(self.cv1,'principal',39000000),self.line(self.cv1,'interest',1150000)]))
        self.store.lb_today=lambda:'2026-11-05'
        # gốc vượt dư: thử với L7 chỉ cho CV-0002 (dư 10 triệu)
        self.assertIn('vượt dư gốc',self.err('lb-detail-post',source=self.tx('L7')['id'],lines=[self.line(self.cv2,'principal',70360000)]))
        self.assertIn('vượt',self.err('lb-waiver-add',loan=self.cv1,date='2026-10-21',amount='200000',reason='x'))

    def test_full_settlement_label_and_cancel_waiver(self):
        self.example(5);p=self.store.lb_detail_preview(dict(source=self.tx('L7')['id'],lines=[self.line(self.cv1,'principal',60000000),self.line(self.cv1,'interest',300000),self.line(self.cv2,'principal',10000000),self.line(self.cv2,'interest',60000)]))
        self.assertEqual({i['code']:i['settlement'] for i in p['impact']},{'CV-0001':'FULL','CV-0002':'FULL'})

    def test_void_that_breaks_obligation_blocked(self):
        self.example(4);self.assertIn('vượt dư gốc',self.err('lb-detail-void',source=self.tx('L1')['id'],reason='x'))
        self.act('lb-waiver-add',loan=self.cv1,date='2026-10-25',amount='150000',reason='x');w=self.st()['loan_waivers'][-1]['id']
        self.act('lb-waiver-cancel',waiver=w,reason='nhầm');self.assertEqual(self.row(self.cv1,'2026-10-25')['waived'],'0')


class US5Broker(Fixture):
    def test_terms_independent_of_cash(self):
        self.example(4);r=self.row(self.cv1,'2026-10-25')
        self.assertEqual((r['broker_terms'],r['spread_terms'],r['interest_paid'],r['interest_outstanding']),('120000','180000','150000','150000'))
        self.post('L5',[self.line(self.cv1,'broker',120000)]);r2=self.row(self.cv1,'2026-10-27')
        self.assertEqual((r2['broker_paid'],r2['principal'],r2['interest_paid']),('120000','60000000','150000'))
        r=self.row(self.cv1,'2026-10-31');self.assertEqual((r['broker_terms'],r['spread_terms']),('192000','288000'))
        self.assertIsNone(self.row(self.dv1)['broker_terms'])
    def test_over_paying_broker_warns_not_blocks(self):
        self.example(4);p=self.store.lb_detail_preview(dict(source=self.tx('L5')['id'],lines=[self.line(self.cv1,'broker',120000)]))
        self.assertTrue(p['can_post']);self.assertEqual(p['warnings'],[])
        # khoản mới mức môi giới thấp (điều khoản đặt trước khi ghi — vòng sửa 29/10 không cho sửa mức sau khi ghi)
        low=self.loan(self.hot,self.ket,'Môi giới thấp',500,broker_name='Long',broker_rate=10);self.post('L2',[self.line(low,'principal',10000000)],reason='Chuyển sang khoản thử')
        p=self.store.lb_detail_preview(dict(source=self.tx('L5')['id'],lines=[self.line(low,'broker',120000)]));self.assertTrue(p['can_post']);self.assertTrue(p['warnings'])


class US6OneBook(Fixture):
    def test_consistency_across_screens_and_counts(self):
        self.example(7);v=self.store.view();b=v['loan_book']
        self.assertEqual((D(b['summary']['receivable']),D(b['summary']['payable'])),(D(0),D(50000000)))
        self.assertEqual((b['summary']['people'],b['summary']['loans'],b['summary']['transactions']),(1,3,6))
        a=self.store.asset_core(self.st())['currencies']['VND']
        rec=next(x for x in a['assets']['groups'] if x['key']=='receivable');pay=next(x for x in a['liabilities']['groups'] if x['key']=='payable')
        self.assertEqual((D(rec['value']),D(pay['value'])),(D(0),D(50000000)))
        p=b['people'][0];self.assertEqual((p['receivable']['count'],p['payable']['count'],D(p['payable']['principal'])),(2,1,D(50000000)))
        n=next(x for x in v['categories']['nodes'] if x['id']==self.borrow);o=next(x for x in n['objects'] if x['profile']==self.ket)
        self.assertEqual([(l['code'],D(l['principal'])) for l in o['biz_loans']],[('ĐV-0001',D(50000000))])
        ob=next(x for x in v['objects']['rows'] if x['id']==self.ket);self.assertEqual(sorted((l['code'],D(l['principal'])) for l in ob['biz_loans']),[('CV-0001',D(0)),('CV-0002',D(0)),('ĐV-0001',D(50000000))])
        self.assertEqual({c['path']:c['loan_business'] for c in ob['categories']},{'Hot Debt':'RECEIVABLE','Vay bạn':'PAYABLE'})
        self.assertIsNotNone(ob['delete_reason'])
        hot=next(c for c in b['by_category'] if c['category']==self.hot);self.assertEqual((hot['transactions'],hot['loans'],hot['people'],D(hot['principal'])),(5,2,1,D(0)))

    def test_pending_banner_and_caution(self):
        self.example(4);b=self.book()
        self.assertEqual((b['pending']['count'],D(b['pending']['in']),D(b['pending']['out'])),(3,D(75360000),D(120000)))
        self.assertTrue(self.row(self.cv1)['caution'])
        self.assertEqual(D(b['by_account'][self.account]['out']),D(110120000))

    def test_approve_with_pending_and_snapshot_unchanged(self):
        self.set_biz(self.hot,'RECEIVABLE');rep0=copy.deepcopy(self.store.report(self.st(),self.account))
        self.act('approve',account=self.account,confirm_unknown=True);snap=copy.deepcopy(self.st()['snapshots'][-1])
        self.cv1=self.loan(self.hot,self.ket,'X',500);self.post('L1',[self.line(self.cv1,'principal',100000000)])
        self.assertEqual(self.st()['snapshots'][-1],snap);self.assertEqual(self.store.report(self.st(),self.account)['totals'],rep0['totals'])
        self.assertEqual(len(self.st()['snapshots']),1);self.assertFalse(self.st()['accounts'][0].get('adjustment_open'))

    def test_default_view_date_never_hides_recorded_events(self):
        self.example(6);self.store.lb_today=lambda:'2026-10-28';b=self.book()
        self.assertEqual((b['as_of'],b['future']),('2026-10-31',True));self.assertEqual(self.row(self.cv1)['principal'],'0')
        self.assertEqual(self.row(self.cv1,'2026-10-28')['principal'],'60000000')                          # chọn ngày xem thì tính tới đúng ngày đó

    def test_no_business_data_means_no_change(self):
        v=self.store.view();self.assertEqual(v['loan_book']['pending']['count'],0);self.assertEqual(v['loan_book']['loans'],[])
        self.assertIn('loan-business',v['capabilities'])


if __name__=='__main__':unittest.main()


class ReviewP1RetroactiveTerms(Fixture):
    """PO review 28/10 P1: không sửa điều khoản tài chính hồi tố khi khoản đã có phát sinh được ghi."""
    def test_rate_edit_blocked_after_posting_and_history_unchanged(self):
        self.example(4);before=self.row(self.cv1,'2026-10-25')
        self.assertEqual((before['interest_accrued'],before['interest_outstanding']),('300000','150000'))
        self.assertIn('đã có phát sinh được ghi',self.err('lb-loan-edit',loan=self.cv1,rate='700',reason='PO test'))
        after=self.row(self.cv1,'2026-10-25');self.assertEqual((after['interest_accrued'],after['interest_outstanding'],after['rate']),('300000','150000','500'))
        self.assertTrue(after['terms_locked']);self.assertIn('ngày hiệu lực',after['terms_lock_reason'])

    def test_broker_terms_locked_but_name_and_non_financial_fields_editable(self):
        self.example(4)
        self.err('lb-loan-edit',loan=self.cv1,broker_name='Long',broker_rate='300',reason='x')          # đổi mức môi giới
        self.err('lb-loan-edit',loan=self.cv1,broker_name='',broker_rate='',reason='x')                 # bỏ môi giới
        self.err('lb-loan-edit',loan=self.cv2,broker_name='Long',broker_rate='100',reason='x')          # thêm môi giới cho khoản đã ghi
        self.act('lb-loan-edit',loan=self.cv1,broker_name='Long (anh họ)',broker_rate='200',reason='đổi biệt danh')
        self.act('lb-loan-edit',loan=self.cv1,name='Vay tháng 10 (sửa tên)',code='CV-0101',due_date='2026-12-31',reason='sửa thông tin')
        r=self.row(self.cv1,'2026-10-25');self.assertEqual((r['code'],r['broker']['name'],r['broker_terms']),('CV-0101','Long (anh họ)','120000'))
        self.assertIn('trước ngày theo dõi',self.err('lb-loan-edit',loan=self.cv1,tracking_date='2026-10-21',reason='x'))   # quy tắc hiện hành giữ nguyên

    def test_edit_allowed_before_any_posting_drafts_do_not_lock(self):
        self.example(0);self.act('lb-detail-draft',source=self.tx('L1')['id'],lines=[self.line(self.cv1,'principal',100000000)])
        self.assertFalse(self.row(self.cv1)['terms_locked'])
        self.act('lb-loan-edit',loan=self.cv1,rate='600',broker_name='Long',broker_rate='250',reason='Nhập sai trước khi ghi')
        l=next(x for x in self.st()['loans'] if x['id']==self.cv1);self.assertEqual((l['rate'],l['broker']['rate']),('600','250'))
        self.assertEqual(l['history'][-1]['before'],{'rate':'500','broker':{'name':'Long','rate':'200'}})

    def test_void_and_reopen_do_not_unlock_terms(self):
        self.example(2);self.act('lb-detail-void',source=self.tx('L2')['id'],reason='Ghi nhầm')
        self.assertEqual(self.row(self.cv2)['sources'],0);self.assertTrue(self.row(self.cv2)['terms_locked'])
        self.assertIn('đã có phát sinh được ghi',self.err('lb-loan-edit',loan=self.cv2,rate='700',reason='x'))
        self.act('lb-detail-post',source=self.tx('L2')['id'],lines=[self.line(self.cv2,'principal',10000000)],reason='Ghi lại')
        self.post('L4',[self.line(self.cv1,'principal',40000000),self.line(self.cv1,'interest',150000)]);self.post('L5',[self.line(self.cv1,'broker',120000)])
        self.post('L7',[self.line(self.cv1,'principal',60000000),self.line(self.cv1,'interest',300000),self.line(self.cv2,'principal',10000000),self.line(self.cv2,'interest',60000)])
        self.act('lb-loan-complete',loan=self.cv2,reason='Xong');self.act('lb-loan-reopen',loan=self.cv2,reason='Kiểm lại')
        self.assertIn('đã có phát sinh được ghi',self.err('lb-loan-edit',loan=self.cv2,rate='700',reason='x'))


class ReviewP2PersonAndLoanRequired(Fixture):
    """PO review 28/10 P2: phân loại mới vào danh mục nghiệp vụ vay phải có Người và khoản vay có sẵn; chỉ để sau phần gốc/lãi/môi giới."""
    def setUp(self):
        super().setUp();self.example(0)
        self.e1=self.tx('E1')['id'];self.before=copy.deepcopy(self.tx('E1')['allocations'])
    def cls_e1(self,**part):return self.act('classify',ids=[self.e1],parts=[dict(category='expense',node=self.hot,**part)],_reclass=RECLASS_GRANT)
    def err_e1(self,parts,**k):
        m=self.err('classify',ids=[self.e1],parts=parts,_reclass=RECLASS_GRANT,**k);self.assertEqual(self.tx('E1')['allocations'],self.before);return m

    def test_no_person_or_no_loan_rejected_and_not_saved(self):
        self.assertIn('chọn Người và khoản vay',self.err_e1([dict(category='expense',node=self.hot)]))
        self.assertIn('chọn khoản vay của Kết',self.err_e1([dict(category='expense',node=self.hot,profile=self.ket)]))
        self.assertNotIn(self.e1,self.book()['sources'])

    def test_wrong_loan_rejected(self):
        cvt=self.loan(self.hot,self.tuoi,'Tươi vay',500)
        self.assertIn('không thuộc',self.err_e1([dict(category='expense',node=self.hot,profile=self.ket,loan=cvt)]))
        self.assertIn('không thuộc',self.err_e1([dict(category='expense',node=self.hot,profile=self.ket,loan=self.dv1)]))     # khác chiều
        self.err_e1([dict(category='expense',node=self.hot,profile=self.ket,loan='khong-co')])
        self.err_e1([dict(category='expense',profile=None,loan=self.cv1)])                                                   # danh mục không mang nghiệp vụ

    def test_person_and_loan_saves_pending_without_posting(self):
        before=copy.deepcopy(self.book()['loans']);self.cls_e1(profile=self.ket,loan=self.cv2)
        self.assertEqual(self.tx('E1')['allocations'][0]['loan'],self.cv2)
        src=self.book()['sources'][self.e1];self.assertEqual((src['status'],src['reasons']),('PENDING',['NOT_DETAILED']))
        self.assertEqual(self.book()['loans'],before)                                                                       # đóng/hủy hộp chi tiết: sổ không đổi
        p=self.store.lb_detail_preview(dict(source=self.e1));self.assertEqual([[l['id'] for l in g['loans']] for g in p['groups']],[[self.cv2]])

    def test_split_one_transaction_across_two_loans_of_one_person(self):
        self.act('classify',ids=[self.e1],parts=[dict(category='expense',node=self.hot,profile=self.ket,loan=self.cv1,amount='600000'),
            dict(category='expense',node=self.hot,profile=self.ket,loan=self.cv2,amount='400000')],_reclass=RECLASS_GRANT)
        p=self.store.lb_detail_preview(dict(source=self.e1));self.assertEqual(sorted(D(g['amount']) for g in p['groups']),[D(400000),D(600000)])
        swapped=[self.line(self.cv1,'principal',400000),self.line(self.cv2,'principal',600000)]
        self.err('lb-detail-post',source=self.e1,lines=swapped)                                                              # lệch khoản đã chọn khi phân loại
        self.err('lb-detail-post',source=self.e1,lines=[self.line(self.cv1,'principal',600000)])                             # chưa đủ: không ghi từng phần
        self.assertEqual(self.book()['sources'][self.e1]['status'],'PENDING')
        self.post('E1',[self.line(self.cv1,'principal',600000),self.line(self.cv2,'principal',400000)])
        self.assertEqual((self.row(self.cv1)['principal'],self.row(self.cv2)['principal']),('600000','400000'))

    def test_bulk_classification_same_rule(self):
        ids=[self.e1,self.tx('L6')['id']]
        self.assertIn('khoản vay',self.err('classify',ids=ids,parts=[dict(category='expense',node=self.hot,profile=self.ket)],_reclass=RECLASS_GRANT))
        self.act('classify',ids=ids,parts=[dict(category='expense',node=self.hot,profile=self.ket,loan=self.cv1)],_reclass=RECLASS_GRANT)
        self.assertEqual({self.tx(r)['allocations'][0]['loan'] for r in ('E1','L6')},{self.cv1})

    def test_reclassify_preview_and_commit_require_loan(self):
        p=self.store.reclassify_preview(dict(transaction=self.e1,part=0,category=self.hot,profile=self.ket));self.assertFalse(p['can_commit'])
        self.assertTrue(any('khoản vay' in b['message'] for b in p['blocks']),p['blocks'])
        p=self.store.reclassify_preview(dict(transaction=self.e1,part=0,category=self.hot,profile=self.ket,loan=self.cv1));self.assertTrue(p['can_commit'],p['blocks'])
        self.act('transaction-reclassify',transaction=self.e1,part=0,category=self.hot,profile=self.ket,loan=self.cv1,reason='Cho Kết vay thêm',review_token=p['review_token'],confirm_business=True)
        self.assertEqual(self.tx('E1')['allocations'][0]['loan'],self.cv1)

    def test_legacy_import_requires_loan_and_links_it(self):
        text="15/09/2026\tTuoi vay cu\tFT9\t2,000,000\t\t1\n"
        self.assertIn('khoản vay',self.err('legacy-import',category=self.hot,profile=self.tuoi,account=self.account,text=text))
        self.assertIn('khoản vay',self.err('legacy-import',category=self.hot,name='Người mới',type='PERSON',account=self.account,text=text))
        cvt=self.loan(self.hot,self.tuoi,'Tươi cũ',0,tracking_date='2026-09-01')
        self.act('legacy-import',category=self.hot,profile=self.tuoi,loan=cvt,account=self.account,text=text)
        e=self.st()['legacy_entries'][-1];self.assertEqual(e['loan'],cvt)
        p=self.store.lb_detail_preview(dict(source=e['id']));self.assertEqual([[l['id'] for l in g['loans']] for g in p['groups']],[[cvt]])

    def test_old_parts_without_loan_stay_visible_and_untouched(self):
        sid=self.tx('L6')['id'];old=copy.deepcopy(self.tx('L6')['allocations'])
        self.assertEqual(self.book()['sources'][sid]['reasons'],['NO_LOAN','NOT_DETAILED'])                                # ngoại lệ cũ: nằm trong danh sách chờ
        self.act('classify',ids=[sid],parts=copy.deepcopy(old),note='ghi chú mới');self.assertEqual(self.tx('L6')['allocations'],old)   # giữ nguyên phần cũ: được lưu
        self.assertIn(sid,[i['source'] for i in self.book()['pending']['items']])

    def test_moving_or_clearing_cannot_strand_loan_links(self):
        self.cls_e1(profile=self.ket,loan=self.cv1)
        self.act('category-create',name='Thường',type='expense',description='');plain=self.node('Thường')
        self.act('category-object-add',category=plain,profile=self.ket)
        self.act('category-object-add',category=self.short,profile=self.ket)
        self.act('classify',ids=[self.tx('L5')['id']],parts=[dict(category='expense',node=self.short,profile=self.ket,loan=self.cv1)],_reclass=RECLASS_GRANT)
        self.assertIn('khoản vay',self.err('category-edit',category=self.short,parent=plain,reason='chuyển'))              # nhánh mất nghiệp vụ khi còn phần gắn khoản
