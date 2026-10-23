import copy
import json
from uuid import uuid4
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

    # ---- review PO vòng 2 (23/10/2026) -------------------------------------------------------------
    def test_old_classify_api_cannot_make_business_change_with_any_flag(self):
        """P1: đổi thu gốc → thu lãi qua API phân loại cũ bị từ chối dù gửi cờ gì (business_ack, _reclass, confirm_business); công nợ không đổi."""
        self.act('category-object-add',category='interest',profile=self.person);debt0=self.store.debt_register(self.store.state());k3=copy.deepcopy(self.tx('K3'))
        for extra in (dict(business_ack=True),dict(_reclass=True),dict(_reclass='RECLASS_GRANT'),dict(confirm_business=True,reason='x'),dict(business_ack=True,reason='Thu lãi')):
            data=json.loads(json.dumps(dict(ids=[k3['id']],parts=[dict(category='interest',profile=self.l10)],**extra)))   # đúng như qua HTTP/JSON
            with self.assertRaises(ValidationError) as c:self.store.apply('classify',data,str(uuid4()))
            self.assertIn('Sửa phân loại',str(c.exception))
        self.assertEqual(self.tx('K3')['allocations'],k3['allocations']);self.assertEqual(self.store.debt_register(self.store.state()),debt0)
        self.act('classify',ids=[k3['id']],parts=k3['allocations'],reason='Không đổi nghiệp vụ')   # mức A vẫn qua đường cũ

    def note_setup(self):
        self.act('category-template',template='no-voucher');nv=self.nodes()['Chi khác không chứng từ']['id'];an,=self.nodes_make('Ăn uống')
        pid=self.mk_person('Mỹ',an,nv);return nv,an,pid

    def test_legacy_row_into_note_required_category_needs_note(self):
        """P2: dòng lịch sử cũ chuyển vào danh mục bắt buộc ghi chú: thiếu ghi chú thì chặn ở xem trước và khi ghi; có ghi chú thì ghi và giữ dấu vết."""
        nv,an,pid=self.note_setup()
        self.act('legacy-import',category=an,profile=pid,account=self.account,text="05/06/2023\tTiền mặt\tFT9\t\t200,000\t1\n");e=self.store.state()['legacy_entries'][-1]
        p=self.store.reclassify_preview(dict(transaction=e['id'],part=0,category=nv,profile=pid));self.assertEqual([b['code'] for b in p['blocks']],['NOTE_REQUIRED']);self.assertFalse(p['can_commit'])
        self.err('transaction-reclassify',transaction=e['id'],part=0,category=nv,profile=pid,review_token=p['review_token'],reason='Không chứng từ')
        self.err('transaction-reclassify',transaction=e['id'],part=0,category=nv,profile=pid,review_token=p['review_token'],reason='Không chứng từ',note='   ')
        p=self.store.reclassify_preview(dict(transaction=e['id'],part=0,category=nv,profile=pid,note='Trả công phụ việc'));self.assertEqual(p['blocks'],[])
        self.err('transaction-reclassify',transaction=e['id'],part=0,category=nv,profile=pid,review_token=p['review_token'],reason='Không chứng từ')      # đổi (bỏ) ghi chú sau xem trước
        self.act('transaction-reclassify',transaction=e['id'],part=0,category=nv,profile=pid,review_token=p['review_token'],reason='Không chứng từ',note='Trả công phụ việc')
        e2=next(x for x in self.store.state()['legacy_entries'] if x['id']==e['id']);self.assertEqual((e2['category'],e2['note'],e2['classification_history'][-1]['after']['note']),(nv,'Trả công phụ việc','Trả công phụ việc'))

    def test_legacy_note_rule_inherited_from_parent_and_paste_kept(self):
        """P2 (PO): cờ ghi chú kế thừa từ danh mục cha; bản dán gốc không đổi khi sửa dòng."""
        nv,an,pid=self.note_setup();self.act('category-create',name='Phụ việc',description='',parent=nv);child=self.nodes()['Phụ việc']['id'];self.act('category-object-add',category=child,profile=pid)
        self.act('legacy-import',category=an,profile=pid,account=self.account,text="08/06/2023\tTiền mặt\tFT5\t70,000\t\t1\n");b=copy.deepcopy(self.store.state()['legacy_batches'][-1]);e=self.store.state()['legacy_entries'][-1]
        p=self.store.reclassify_preview(dict(transaction=e['id'],part=0,category=child,profile=pid));self.assertEqual(([x['code'] for x in p['blocks']],p['note']['required']),(['NOTE_REQUIRED'],True))
        p=self.store.reclassify_preview(dict(transaction=e['id'],part=0,category=child,profile=pid,note='Công phụ hồ'))
        self.act('transaction-reclassify',transaction=e['id'],part=0,category=child,profile=pid,review_token=p['review_token'],reason='Không chứng từ',note='Công phụ hồ')
        b2=next(x for x in self.store.state()['legacy_batches'] if x['id']==b['id']);self.assertEqual((b2['source_text'],b2['sha256'],b2['rows']),(b['source_text'],b['sha256'],b['rows']))

    def test_reclassify_business_change_rejects_bad_token_missing_reason_even_with_business_ack(self):
        """P1 (PO): ở đường hợp lệ, cờ business_ack không thay được mã xem trước, lý do hay xác nhận."""
        self.act('category-object-add',category='interest',profile=self.person);self.act('approve',account=self.account,reason='QA',confirm_unknown=True);snap=copy.deepcopy(self.store.state()['snapshots'][-1])
        self.act('begin-adjustment',account=self.account,reason='Sửa');p=self.prev('K3',category='interest',profile=self.l10);base=dict(transaction=p['transaction'],part=0,category='interest',profile=self.l10,business_ack=True)
        self.err('transaction-reclassify',**base,review_token='sai',reason='x',confirm_business=True)                     # mã sai
        self.err('transaction-reclassify',**base,reason='x',confirm_business=True)                                         # thiếu mã
        self.err('transaction-reclassify',**base,review_token=p['review_token'],confirm_business=True)                    # thiếu lý do
        self.err('transaction-reclassify',**base,review_token=p['review_token'],reason='x')                                # thiếu xác nhận
        self.assertEqual(self.tx('K3')['allocations'][0]['category'],'principal')
        self.act('transaction-reclassify',**base,review_token=p['review_token'],reason='Thu lãi',confirm_business=True)   # đường hợp lệ vẫn ghi
        self.assertEqual((self.tx('K3')['allocations'][0]['category'],self.store.state()['snapshots'][-1]),('interest',snap))

    def test_legacy_import_into_note_required_category_needs_note_per_row(self):
        nv,an,pid=self.note_setup();m=['date','description','reference','out','in','balance','note']
        txt="05/06/2023\tTiền mặt\tFT7\t100,000\t\t1\tCông thợ\n06/06/2023\tTiền mặt\tFT8\t50,000\t\t1\t\n"
        p=self.store.legacy_preview(dict(account=self.account,category=nv,profile=pid,text=txt,mapping=m));self.assertEqual([r['status'] for r in p['rows']],['OK','ERROR']);self.assertFalse(p['can_import'])
        self.err('legacy-import',account=self.account,category=nv,profile=pid,text=txt,mapping=m)
        self.act('legacy-import',account=self.account,category=nv,profile=pid,text=txt.replace('1\t\n','1\tGửi xe\n'),mapping=m)
        self.assertEqual([e.get('note') for e in self.store.state()['legacy_entries'][-2:]],['Công thợ','Gửi xe'])
        self.act('legacy-import',account=self.account,category=an,profile=pid,text="07/06/2023\tĂn trưa\tFT6\t30,000\t\t1\n")   # danh mục thường không cần ghi chú

    def test_bank_transaction_into_note_required_category_needs_note(self):
        nv,an,pid=self.note_setup();k=next(t for t in self.store.state()['transactions'] if D_(t['signed_amount'])<0 and not t.get('note') and not t['allocations'])
        self.act('classify',ids=[k['id']],parts=[dict(category='expense',node=an,profile=pid)])
        p=self.store.reclassify_preview(dict(transaction=k['id'],part=0,category=nv,profile=pid));self.assertEqual([b['code'] for b in p['blocks']],['NOTE_REQUIRED'])
        p=self.store.reclassify_preview(dict(transaction=k['id'],part=0,category=nv,profile=pid,note='Mua vật tư lẻ'));self.assertEqual(p['blocks'],[])
        self.act('transaction-reclassify',transaction=k['id'],part=0,category=nv,profile=pid,review_token=p['review_token'],reason='Không chứng từ',note='Mua vật tư lẻ')
        self.assertEqual((self.tx_by_id(k['id'])['allocations'][0]['node'],self.tx_by_id(k['id'])['note']),(nv,'Mua vật tư lẻ'))
    def tx_by_id(self,i):return next(t for t in self.store.state()['transactions'] if t['id']==i)

    def test_review_token_survives_server_envelope(self):
        """server.py chèn mã phiên `token` vào mọi phản hồi; mã xem trước phải mang tên khác và vẫn dùng được (lỗi phát hiện khi dùng thử UI)."""
        self.act('category-object-add',category='principal',profile=self.person)
        response={**{k:v for k,v in self.prev('K1',category='principal',profile=self.l5).items() if k!='parts_raw'},'token':'session-csrf-token'}
        self.assertNotEqual(response['review_token'],'session-csrf-token')
        self.act('transaction-reclassify',transaction=response['transaction'],part=0,category='principal',profile=self.l5,review_token=response['review_token'],reason='Qua giao diện')
        self.assertNotIn('node',self.tx('K1')['allocations'][0])

if __name__=='__main__':unittest.main()
