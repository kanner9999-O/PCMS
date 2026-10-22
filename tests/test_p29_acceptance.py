import copy
import tempfile
import unittest
from decimal import Decimal
from uuid import uuid4
from pcms.core import ValidationError
from pcms.p01 import P01Store
import test_p18_acceptance as base

def D_(x):return Decimal(str(x))

MY=("\t\t\t176,000,000.00\t130,000,000.00\t46,000,000.00\n\n\n"
    "05/06/2023\tNbd ck duc vay\tFT23156186980\t30,000,000.00\t\t878,010,890.00\n\n"
    "10/03/2023\tNbd ck duc vay\tFT230695470692\t25,000,000.00\t\t1,661,132,066.00\n\n\n"
    "08/07/2023\tDuc chuyen\tFT23189278758578\\BNK\t\t30,000,000.00\t823,048,426.00\n\n"
    "07/09/2023\tNGUYEN BA DUNG ck\tFT23250564617\t15,000,000.00\t\t1,515,004,709.00\n\n"
    "26/09/2023\tNGUYEN BA DUNG ck\tFT23270210656\t66,000,000.00\t\t619,767,707.00\n"
    "27/09/2023\tDuc chuyen\tFT23271717053072\\BNK\t\t60,000,000.00\t379,767,707.00\n"
    "07/10/2023\tNGUYEN BA DUNG ck\tFT23280542696\t40,000,000.00\t\t12,149,980.00\n\n"
    "08/10/2023\tPHAM VAN DUC\tFT23282650944236\\BNK\t\t40,000,000.00\t152,149,980.00\n")

class P29Acceptance(base.P18Acceptance):
    """Dùng lại dữ liệu P18 (Long debt nằm trong Loans)."""
    def setUp(self):
        super().setUp();self.ld=self.nodes()['Long debt']['id']
    def prev(self,text=MY,**k):return self.store.legacy_preview(dict(account=self.account,category=self.ld,name='Mỹ',text=text,**k))
    def imp(self,text=MY,**k):self.act('legacy-import',account=self.account,category=self.ld,name='Mỹ',text=text,**k)
    def objs(self,key):
        c=self.store.view()['categories'];return {o['name']:o for o in next(n for n in c['nodes'] if n['id']==key)['objects']}
    def err(self,a,**d):
        n=len(self.store.events())
        with self.assertRaises(ValidationError):self.act(a,**d)
        self.assertEqual(len(self.store.events()),n)

    def test_preview_my_tab_matches_total_row(self):
        p=self.prev();self.assertEqual((len(p['rows']),p['issues'],p['totals'],p['declared'],p['totals_ok'],p['can_import'],p['importable'],p['object']['exists']),(8,[],{'in':'130000000','out':'176000000'},{'in':'130000000','out':'176000000'},True,True,8,False))
        r={x['reference']:x for x in p['rows']};self.assertEqual((r['FT23156186980']['date'],r['FT23156186980']['amount'],r['FT23156186980']['direction'],r['FT23156186980']['bank_balance']),('2023-06-05','30000000','OUT','878010890'))
        self.assertEqual((r['FT23189278758578\\BNK']['direction'],r['FT23189278758578\\BNK']['amount']),('IN','30000000'));self.assertEqual(p['rows'][0]['row'],4)    # số dòng nguồn trong bản dán
        n=len(self.store.events());self.prev();self.assertEqual(len(self.store.events()),n)                                                   # xem trước chỉ đọc

    def test_import_creates_object_totals_history_and_leaves_bank_untouched(self):
        rep0=self.store.report(self.store.state(),self.store.state()['accounts'][0]['id']);assets0=self.store.view()['assets']['currencies'];aid0=self.store.state()['accounts'][0]['id'];cr=lambda:{k:v for k,v in self.store.classification_review(dict(account=aid0)).items() if k not in ('now','scope')};cr0=cr()
        ld0=self.nodes()['Long debt']['totals']
        self.imp();o=self.objs(self.ld)['Mỹ'];self.assertEqual((o['totals'],o['kind']),({'in':'130000000','out':'176000000','transactions':8},'OBJECT'))
        t=self.nodes()['Long debt']['totals'];self.assertEqual((D_(t['in'])-D_(ld0['in']),D_(t['out'])-D_(ld0['out'])),(130000000,176000000))                    # tổng danh mục tăng đúng
        h=self.store.category_history(dict(category=self.ld,object=o['profile']));self.assertEqual((len(h['rows']),h['rows'][0]['reference'],h['rows'][0]['legacy'],h['rows'][0]['status']),(8,'FT23282650944236\\BNK',True,'LEGACY'))
        self.assertEqual(h['rows'][0]['date'],'2023-10-08');self.assertEqual((D_(h['totals']['in']),D_(h['totals']['out'])),(130000000,176000000));self.assertEqual(h['rows'][-1]['source_row'],6)
        aid=self.store.state()['accounts'][0]['id'];self.assertEqual(self.store.report(self.store.state(),aid),rep0);self.assertEqual(self.store.view()['assets']['currencies'],assets0)
        self.assertEqual(cr(),cr0)                                                                                   # không đụng kiểm khớp sao kê
        r=self.store.category_review(dict(account=aid));self.assertTrue(r['reconciled'])
        b=self.store.view()['categories']['legacy'][0];self.assertEqual((b['rows'],b['active'],b['profile_name'],b['status'],b['declared']['out'],'Nbd ck duc vay' in b['source_text']),(8,8,'Mỹ','ACTIVE','176000000',True))

    def test_validation_blocks_bad_rows_and_changes_nothing(self):
        good="05/06/2023\tA\tFT1\t30,000,000.00\t\t1\n"
        bads={'ngày sai':"31/02/2023\tA\tFT1\t1000\t\t1\n",'cả ra và vào':"05/06/2023\tA\tFT1\t1000\t2000\t1\n",'không có tiền':"05/06/2023\tA\tFT1\t\t\t1\n",'số sai':"05/06/2023\tA\tFT1\tabc\t\t1\n",'số lẻ':"05/06/2023\tA\tFT1\t1000.5\t\t1\n",'thiếu ngày':"\tA\tFT1\t1000\t\t1\n",'số âm':"05/06/2023\tA\tFT1\t-1000\t\t1\n"}
        for k,text in bads.items():
            p=self.prev(good+text);self.assertTrue(p['issues'] and not p['can_import'],k);self.err('legacy-import',account=self.account,category=self.ld,name='Mỹ',text=good+text)
        self.assertEqual(self.prev(good)['can_import'],True)
        for bad in (dict(text='   '),dict(text=good,name=''),dict(text=good,category='unknown'),dict(text=good,category='nope'),dict(text=good,mapping=['date']),dict(text=good,mapping=['date','date','out']),dict(text=good,mapping=['date','x','out'])):
            args=dict(category=self.ld,name='Mỹ');args.update(bad);self.err('legacy-import',account=self.account,**args)

    def test_total_mismatch_needs_confirmation(self):
        bad=MY.replace('176,000,000.00\t130,000,000.00\t46,000,000.00','175,000,000.00\t130,000,000.00\t45,000,000.00',1)
        p=self.prev(bad);self.assertEqual((p['totals_ok'],p['can_import'],p['needs_confirm'],p['issues']),(False,False,True,[]))
        self.err('legacy-import',account=self.account,category=self.ld,name='Mỹ',text=bad);self.imp(bad,accept_total_mismatch=True)
        self.assertTrue(self.store.state()['legacy_batches'][0]['accepted_mismatch']);self.assertEqual(len(self.store.state()['legacy_entries']),8)
        nototals="05/06/2023\tA\tFT1\t1000\t\t1\n";self.assertIsNone(self.prev(nototals)['totals_ok']);self.assertTrue(self.prev(nototals)['can_import'])

    def test_bank_duplicates_and_repeat_paste_and_late_statement(self):
        # R192/A59 (spec 042): định danh = tài khoản + mã đầy đủ; cùng định danh cùng nội dung thì không cộng hai lần; khác nội dung hoặc khác hậu tố là xung đột cần đối chiếu.
        same="20/09/2026\tCho Ket vay 5tr\tK1\t5,000,000\t\t1\n06/06/2023\tY\tZZ9\t7,000,000\t\t1\n"                      # K1 trùng hệt giao dịch sao kê trong tài khoản QA
        p=self.prev(same);self.assertEqual(([r['status'] for r in p['rows']],p['matched_bank'],p['importable']),(['MATCHED_BANK','OK'],1,2))
        self.imp(same);o=self.objs(self.ld)['Mỹ'];self.assertEqual(o['totals'],{'in':'0','out':'7000000','transactions':1})                  # dòng trùng sao kê lưu làm chứng từ, không tính hai lần
        b=self.store.view()['categories']['legacy'][0];self.assertEqual((b['rows'],b['active'],b['matched_bank']),(2,1,1))
        p2=self.prev(same);self.assertEqual(([r['status'] for r in p2['rows']],p2['duplicates'],p2['matched_bank']),(['MATCHED_BANK','DUPLICATE'],1,1))   # dán lại
        self.err('legacy-import',account=self.account,category=self.ld,name='Mỹ',text="06/06/2023\tY\tZZ9\t7,000,000\t\t1\n")                 # không còn dòng mới
        self.assertTrue(self.prev("06/06/2023\tY\tZZ9\t8,000,000\t\t1\n")['issues'])                                                      # cùng mã khác nội dung: xung đột
        self.assertTrue(self.prev("20/09/2026\tCho Ket vay 5tr\tK1\\BNK\t5,000,000\t\t1\n")['issues'])                                    # khác hậu tố: gần trùng, cần đối chiếu (không tự gộp, không cộng hai lần)
        s=self.store.state();t0=s['transactions'][0];s['transactions'].append(dict(copy.deepcopy(t0),id='late',reference='ZZ9',date='2023-06-06',description='Y',signed_amount='-7000000'))   # sao kê nhập sau, cùng định danh cùng nội dung
        late=self.store.legacy_summary(s);self.assertEqual((late[0]['active'],late[0]['matched_bank']),(0,2))
        s['transactions'][-1]['signed_amount']='-7500000';self.assertEqual(self.store.legacy_summary(s)[0]['conflicts'],1)                      # cùng định danh khác nội dung: xung đột, không tính

    def test_reuse_object_auto_membership_mapping_and_void(self):
        self.act('category-object-add',category=self.nodes()['Loans']['id'],name='Khiêm');kh=next(p['id'] for p in self.store.state()['profiles'] if p['name']=='Khiêm')
        signed="08/07/2023\tA\tFTA\t30,000,000\t1\n09/07/2023\tB\tFTB\t-12,000,000\t2\n"
        p=self.store.legacy_preview(dict(account=self.account,category=self.ld,profile=kh,text=signed,mapping=['date','description','reference','amount','balance']));self.assertEqual(([(r['direction'],r['amount']) for r in p['rows']],p['object']['exists']),([('IN','30000000'),('OUT','12000000')],True))
        self.act('legacy-import',account=self.account,category=self.ld,profile=kh,text=signed,mapping=['date','description','reference','amount','balance'])
        self.assertIn('Khiêm',self.objs(self.ld));self.assertEqual(self.objs(self.ld)['Khiêm']['totals'],{'in':'30000000','out':'12000000','transactions':2})        # tự gán vào danh mục
        bid=self.store.state()['legacy_batches'][0]['id'];self.err('legacy-void',batch=bid,reason='');self.act('legacy-void',batch=bid,reason='Dán nhầm')
        self.assertEqual(self.objs(self.ld)['Khiêm']['totals']['transactions'],0);v=self.store.view()['categories']['legacy'][0];self.assertEqual((v['status'],v['void_reason'],bool(v['source_text'])),('VOID','Dán nhầm',True));self.err('legacy-void',batch=bid,reason='lần hai')

    def test_backup_restore_and_move_follows(self):
        self.imp();my=self.objs(self.ld)['Mỹ']['profile'];other=self.nodes()['Loans']['id']
        self.act('category-object-move',profile=my,**{'from':self.ld,'to':other},reason='Chuyển');self.assertEqual(self.objs(other)['Mỹ']['totals']['transactions'],8)
        from pcms.p01 import P01Store
        o=P01Store(tempfile.mkdtemp());o.restore(self.store.backup(),str(uuid4()));self.assertEqual(len(o.view()['categories']['legacy']),1)

for name in [n for n in dir(base.P18Acceptance) if n.startswith('test_')]:setattr(P29Acceptance,name,None)
if __name__=='__main__':unittest.main()
