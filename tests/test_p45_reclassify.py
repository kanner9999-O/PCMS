import copy
import unittest
from decimal import Decimal
import test_p18_acceptance as base
from pcms.core import ValidationError

def D_(x):return Decimal(str(x))

class ReclassifyTests(base.P18Acceptance):
    """Spec 043 — "Sửa phân loại" (R195–R200) trên dữ liệu giả P18: Kết có Kết 5tr (K1 ở Gốc vay › Kết) và Kết 10tr (K2, K3 Gốc vay; K4 Lãi vay)."""
    def prev(self,ref,part=0,**k):return self.store.reclassify_preview(dict(transaction=self.tx(ref)['id'],part=part,**k))
    def commit(self,p,**k):return self.act('transaction-reclassify',transaction=p['transaction'],part=p['part'],category=k.pop('category'),profile=k.pop('profile',None),review_token=p['review_token'],**k)
    def cat_totals(self):
        c=self.store.view()['categories'];return {**{r['name']:r['totals'] for r in c['roots']},**{n['path']:n['totals'] for n in c['nodes']}}
    def obj_totals(self,key,pid):
        c=self.store.view()['categories'];h=next(x for x in c['roots']+c['nodes'] if (x.get('key') or x['id'])==key);return next((o['totals'] for o in h['objects'] if o['profile']==pid),None)
    def assert_preview_matches(self,p):
        """Xem trước = kết quả: mọi tổng danh mục mà xem trước báo sẽ đổi đều bằng đúng giá trị 'sau' trong xem trước."""
        now=self.cat_totals()
        for e in p['effects']['categories']:self.assertEqual(now.get(e['path']),e['after'],e['path'])
    def nodes_make(self,*names,parent='expense'):
        for n in names:self.act('category-create',name=n,description='',parent=parent)
        return [self.nodes()[n]['id'] for n in names]
    def mk_person(self,name,*cats):
        self.act('object-create',name=name,type='PERSON',category=cats[0]);pid=next(p['id'] for p in self.store.state()['profiles'] if p['name']==name)
        for c in cats[1:]:self.act('category-object-add',category=c,profile=pid)
        return pid

    # ---- A58 / ca Kết ---------------------------------------------------------------
    def test_ket_case_keeps_loan_link_moves_part_and_changes_no_money(self):
        self.act('category-object-add',category='principal',profile=self.person);t0=copy.deepcopy(self.tx('K1'));rep0=self.store.report(self.store.state(),self.account);root0=self.cat_totals()['Gốc vay']
        p=self.prev('K1',category='principal',profile=self.l5)
        self.assertEqual((p['level'],p['blocks'],p['moved'],p['parts_before'][0]['path'],p['parts_after'][0]['path'],p['parts_after'][0]['link']),('A',[],'5000000','Gốc vay › Kết','Gốc vay','Khoản vay: Kết 5tr'))
        eff={e['path']:(e['before'],e['after']) for e in p['effects']['categories']};self.assertEqual((D_(eff['Gốc vay › Kết'][0]['out']),D_(eff['Gốc vay › Kết'][1]['out'])),(5000000,0))
        self.assertNotIn('Gốc vay',eff);self.assertTrue(p['invariants']['source_unchanged'])                                        # tổng Gốc vay không đổi
        obj={(e['path'],e['object']):e for e in p['effects']['objects']};self.assertEqual(D_(obj[('Gốc vay','Kết')]['after']['out'])-D_(obj[('Gốc vay','Kết')]['before']['out']),5000000)
        self.err('transaction-reclassify',transaction=p['transaction'],part=0,category='principal',profile=self.l5,review_token=p['review_token'])   # thiếu lý do
        self.commit(p,category='principal',profile=self.l5,reason='Thạch chọn Gốc vay')
        t=self.tx('K1');self.assertEqual({k:t[k] for k in ('id','account','date','reference','signed_amount','description','sources')},{k:t0[k] for k in ('id','account','date','reference','signed_amount','description','sources')})
        self.assertEqual(t['allocations'],[dict(category='principal',amount='5000000',profile=self.l5)]);self.assertEqual(t['classification_history'][-1]['reason'],'Thạch chọn Gốc vay')
        self.assertIn('Kết',self.nodes());self.assertEqual(self.cat_totals()['Gốc vay'],root0);self.assertEqual(self.store.report(self.store.state(),self.account)['balance'],rep0['balance'])
        self.assertIn(t['id'],{r['transaction'] for r in self.store.category_history(dict(category='principal',object=self.person))['rows']})
        self.assert_preview_matches(p)

    # ---- đổi danh mục / đối tượng / cả hai ---------------------------------------------------
    def test_move_between_same_nature_categories_change_object_and_both(self):
        a,b=self.nodes_make('A','B');my=self.mk_person('Mỹ',a,b);tuoi=self.mk_person('Tươi',b)
        self.act('classify',ids=[self.tx('X1')['id']],parts=[dict(category='expense',node=a,profile=my)])
        p=self.prev('X1',category=b,profile=my);self.assertEqual(p['level'],'A');self.commit(p,category=b,profile=my,reason='Cùng bản chất');self.assert_preview_matches(p)
        self.assertEqual((self.obj_totals(a,my)['transactions'],self.obj_totals(b,my)['transactions']),(0,1))
        p=self.prev('X1',category=b,profile=tuoi);self.commit(p,category=b,profile=tuoi,reason='Đổi đối tượng');self.assertEqual((self.obj_totals(b,my)['transactions'],self.obj_totals(b,tuoi)['transactions']),(0,1))
        p=self.prev('X1',category=a,profile=my);self.commit(p,category=a,profile=my,reason='Đổi cả hai');self.assertEqual(self.tx('X1')['allocations'][0]['node'],a);self.assert_preview_matches(p)

    def test_split_transaction_edits_only_the_chosen_part_and_counts_transaction_once(self):
        a,b=self.nodes_make('A','B');my=self.mk_person('Mỹ',a,b);tuoi=self.mk_person('Tươi',a,b)
        self.act('classify',ids=[self.tx('X1')['id']],parts=[dict(category='expense',node=a,profile=my,amount='4000'),dict(category='expense',node=b,profile=tuoi,amount='6000')])
        p=self.prev('X1',part=1,category=a,profile=tuoi);self.assertEqual((p['moved'],[x['path'] for x in p['parts_after']]),('6000',['Chi tiêu › A','Chi tiêu › A']))
        self.commit(p,category=a,profile=tuoi,reason='Một phần');al=self.tx('X1')['allocations']
        self.assertEqual((al[0],[x['amount'] for x in al]),(dict(category='expense',node=a,profile=my,amount='4000'),['4000','6000']));self.assertEqual(sum(D_(x['amount']) for x in al),10000)
        t=self.cat_totals();self.assertEqual((t['Chi tiêu › A']['transactions'],t['Chi tiêu › A']['parts'],t['Chi tiêu']['transactions'],t['Chi tiêu']['parts']),(1,2,1,2))   # giao dịch đếm một lần, phần phân bổ tách riêng
        self.assertEqual(t['Chi tiêu › B']['transactions'],0)
        with self.assertRaises(ValidationError):self.prev('X1',part=5,category=a,profile=tuoi)

    # ---- đích không hợp lệ ----------------------------------------------------------------
    def test_invalid_targets_are_blocked_in_preview_and_commit(self):
        a,b=self.nodes_make('A','B');my=self.mk_person('Mỹ',a)
        self.act('classify',ids=[self.tx('X1')['id']],parts=[dict(category='expense',node=a,profile=my)])
        p=self.prev('X1',category=b,profile=my);self.assertEqual([x['code'] for x in p['blocks']],['NOT_MEMBER']);self.assertEqual(p['needs_membership']['profile'],my)
        self.err('transaction-reclassify',transaction=p['transaction'],part=0,category=b,profile=my,review_token=p['review_token'],reason='x')
        self.act('category-object-add',category=b,profile=my);self.assertEqual(self.prev('X1',category=b,profile=my)['blocks'],[])   # thêm thành viên (xác nhận riêng) rồi xem trước lại
        c,=self.nodes_make('C');self.act('category-archive',category=c,reason='QA');self.assertIn('ARCHIVED',[x['code'] for x in self.prev('X1',category=c,profile=None)['blocks']])
        self.assertIn('NO_CHANGE',[x['code'] for x in self.prev('X1',category=a,profile=my)['blocks']])
        ld=self.nodes()['Long debt']['id'];self.act('category-object-add',category='principal',profile=self.person);self.act('category-object-add',category=ld,profile=self.person)
        self.act('loan-regroup',profile=self.l5,node=ld,effective_date='2026-09-21',reason='QA')
        self.assertIn('LOAN_GROUP',[x['code'] for x in self.prev('K1',category='principal',profile=self.l5)['blocks']])            # nhóm khoản vay quyết định nơi hiển thị
        self.err('classify',ids=[self.tx('X1')['id']],parts=[dict(category='expense',node=b,profile=self.person)])                    # API phân loại cũ: người chưa thuộc B → chặn như UI

    # ---- mức B ------------------------------------------------------------------------------
    def test_business_change_shows_impact_and_needs_separate_confirmation(self):
        self.act('category-object-add',category='interest',profile=self.person);loan0=next(l for l in self.store.debt_register(self.store.state())['loans'] if l['id']==self.l10)
        p=self.prev('K3',category='interest',profile=self.l10);self.assertEqual((p['level'],p['blocks']),('B',[]))
        imp=p['business']['loans'][0];self.assertEqual((imp['before']['principal'],imp['after']['principal']),(loan0['current_principal'],str(D_(loan0['current_principal'])+3000000)))
        self.assertEqual(D_(imp['after']['interest_received'])-D_(imp['before']['interest_received']),3000000)
        self.err('transaction-reclassify',transaction=p['transaction'],part=0,category='interest',profile=self.l10,review_token=p['review_token'],reason='Thu lãi chứ không phải gốc')   # thiếu xác nhận tác động
        self.err('classify',ids=[self.tx('K3')['id']],parts=[dict(category='interest',profile=self.l10)])                              # đường phân loại cũ không lách được
        self.commit(p,category='interest',profile=self.l10,reason='Thu lãi chứ không phải gốc',confirm_business=True)
        l=next(l for l in self.store.debt_register(self.store.state())['loans'] if l['id']==self.l10);self.assertEqual(l['current_principal'],imp['after']['principal'])
        self.assertEqual(self.tx('K3')['classification_history'][-1]['reclassify']['level'],'B')

    def test_business_references_block_with_guidance(self):
        self.act('category-object-add',category='interest',profile=self.person);self.act('category-object-add',category='principal',profile=self.person)
        s=self.store.state();t=self.tx('K3');s['interest_statements']=[dict(id='st',profile=self.l10,versions=[dict(draft=dict(payments=[dict(transaction=t['id'],amount='1')]))])]
        p=self.store.reclassify_preview(dict(transaction=t['id'],part=0,category='interest',profile=self.l10),s);self.assertEqual([x['code'] for x in p['blocks']],['INTEREST_STATEMENT']);self.assertIn('mở lại bảng kê',p['blocks'][0]['message'])
        s=self.store.state();next(x for x in s['profiles'] if x['id']==self.l5)['completion_history']=[dict(action='COMPLETE')]
        p=self.store.reclassify_preview(dict(transaction=self.tx('K1')['id'],part=0,category='principal',profile=self.l5),s);self.assertEqual([x['code'] for x in p['blocks']],['LOAN_COMPLETED'])   # kể cả mức A
        s=self.store.state();s.setdefault('realty',{})['pay_links']=[dict(id='l',transaction=t['id'],status='ACTIVE')]
        self.assertIn('REALTY_LINK',[x['code'] for x in self.store.reclassify_preview(dict(transaction=t['id'],part=0,category='interest',profile=self.l10),s)['blocks']])
        s=self.store.state();self.tx('K3');next(x for x in s['transactions'] if x['id']==t['id'])['transfer_match']='m'
        self.assertIn('TRANSFER',[x['code'] for x in self.store.reclassify_preview(dict(transaction=t['id'],part=0,category='principal',profile=self.l10,),s)['blocks']])

    # ---- đã duyệt, xem trước hết hạn, hoàn tác ---------------------------------------------------
    def test_approved_needs_adjustment_and_snapshot_is_kept(self):
        self.act('category-object-add',category='principal',profile=self.person);self.act('approve',account=self.account,reason='QA',confirm_unknown=True);snap=copy.deepcopy(self.store.state()['snapshots'][-1])
        p=self.prev('K1',category='principal',profile=self.l5);self.assertEqual((p['approved'],p['needs_adjustment']),(True,True))
        self.err('transaction-reclassify',transaction=p['transaction'],part=0,category='principal',profile=self.l5,review_token=p['review_token'],reason='x')
        self.act('begin-adjustment',account=self.account,reason='Sửa phân loại');self.commit(p,category='principal',profile=self.l5,reason='x')   # mở phiên không làm hỏng mã xem trước
        self.assertEqual(self.store.state()['snapshots'][-1],snap)

    def test_stale_preview_or_changed_choice_is_rejected(self):
        self.act('category-object-add',category='principal',profile=self.person);self.act('category-object-add',category=self.nodes()['Kết']['id'],profile=self.person)
        p=self.prev('K1',category='principal',profile=self.l5)
        self.err('transaction-reclassify',transaction=p['transaction'],part=0,category='principal',profile=self.l10,review_token=p['review_token'],reason='x')   # đổi lựa chọn sau xem trước
        self.act('classify',ids=[self.tx('K2')['id']],parts=[dict(category='principal',node=self.nodes()['Kết']['id'],profile=self.l10)])   # dữ liệu đổi sau xem trước
        self.err('transaction-reclassify',transaction=p['transaction'],part=0,category='principal',profile=self.l5,review_token=p['review_token'],reason='x')
        p=self.prev('K1',category='principal',profile=self.l5);self.commit(p,category='principal',profile=self.l5,reason='Xem trước lại')
        q=self.prev('K1',category=self.nodes()['Kết']['id'],profile=self.l5);self.commit(q,category=self.nodes()['Kết']['id'],profile=self.l5,reason='Hoàn tác bằng điều chỉnh mới')
        self.assertEqual([h['reason'] for h in self.tx('K1')['classification_history']][-2:],['Xem trước lại','Hoàn tác bằng điều chỉnh mới'])

    # ---- lịch sử cũ -----------------------------------------------------------------------------
    def test_legacy_row_reclassified_within_root_and_source_kept(self):
        nha,=self.nodes_make('Nhà',parent='investment');self.act('object-create',name='Đất A',type='PROPERTY',category=nha);self.act('object-create',name='Đất B',type='PROPERTY',category=nha)
        pa,pb=(next(p['id'] for p in self.store.state()['profiles'] if p['name']==n) for n in ('Đất A','Đất B'))
        self.act('legacy-import',category=nha,profile=pa,account=self.account,text="05/06/2023\tCọc\tFT1\t30,000,000\t\t1\n");e=self.store.state()['legacy_entries'][-1];src=self.store.state()['legacy_batches'][-1]['source_text']
        p=self.store.reclassify_preview(dict(transaction=e['id'],part=0,category=nha,profile=pb));self.assertEqual((p['legacy'],p['level']),(True,'B'))      # đổi BĐS là mức B
        self.err('transaction-reclassify',transaction=e['id'],part=0,category=nha,profile=pb,review_token=p['review_token'],reason='Nhầm BĐS')
        self.act('transaction-reclassify',transaction=e['id'],part=0,category=nha,profile=pb,review_token=p['review_token'],reason='Nhầm BĐS',confirm_business=True)
        e2=next(x for x in self.store.state()['legacy_entries'] if x['id']==e['id']);self.assertEqual((e2['profile'],e2['classification_history'][-1]['before']['profile']),(pb,pa))
        self.assertEqual(self.store.state()['legacy_batches'][-1]['source_text'],src)
        self.assertIn('LEGACY_ROOT',[x['code'] for x in self.store.reclassify_preview(dict(transaction=e['id'],part=0,category='expense',profile=None))['blocks']])

    def test_review_token_survives_server_envelope(self):
        """server.py chèn mã phiên `token` vào mọi phản hồi; mã xem trước phải mang tên khác và vẫn dùng được (lỗi phát hiện khi dùng thử UI)."""
        self.act('category-object-add',category='principal',profile=self.person)
        response={**{k:v for k,v in self.prev('K1',category='principal',profile=self.l5).items() if k!='parts_raw'},'token':'session-csrf-token'}
        self.assertNotEqual(response['review_token'],'session-csrf-token')
        self.act('transaction-reclassify',transaction=response['transaction'],part=0,category='principal',profile=self.l5,review_token=response['review_token'],reason='Qua giao diện')
        self.assertNotIn('node',self.tx('K1')['allocations'][0])

if __name__=='__main__':unittest.main()
