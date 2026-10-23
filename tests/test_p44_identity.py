from pcms.reclassify import RECLASS_GRANT   # quyền nội bộ của "Sửa phân loại" (spec 043); API không gửi được — kiểm ở test_p45
import base64
import copy
import unittest
from decimal import Decimal
import test_p18_acceptance as base
from p01_fixtures import statement
from pcms.core import ValidationError

def D_(x):return Decimal(str(x))

class IdentityTests(base.P18Acceptance):
    """Spec 042 (R191–R194, A58–A59) trên dữ liệu giả P18: người Kết có Kết 5tr, Kết 10tr; K1 phân loại ở danh mục con Gốc vay › Kết."""
    def view(self):return self.store.view()
    def root(self,key):return next(r for r in self.view()['categories']['roots'] if r['key']==key)
    def node(self,name):return self.nodes()[name]
    def obj_in(self,holder,pid):return next((o for o in holder['objects'] if o['profile']==pid),None)
    def issues(self,ref=None):return [i for i in self.view()['categories']['classification_issues'] if ref is None or i['reference']==ref]
    def ket_case(self):
        """Tái hiện FT26267843740784: một giao dịch nguồn 5tr phân loại ở Gốc vay › Kết (khoản vay của Kết), còn người Kết là thành viên Gốc vay."""
        self.act('category-object-add',category='principal',profile=self.person)
        return self.tx('K1')

    def assert_screens_consistent(self):
        """Tổng của mỗi đối tượng ở mỗi danh mục (màn Danh mục) bằng tổng lịch sử của chính đối tượng đó tại danh mục đó."""
        c=self.view()['categories']
        for holder in c['roots']+c['nodes']:
            key=holder.get('key') or holder['id']
            for o in holder['objects']:
                h=self.store.category_history(dict(category=key,object=o['profile']))
                self.assertEqual((o['totals']['in'],o['totals']['out'],o['totals']['transactions']),(h['totals']['in'],h['totals']['out'],h['totals']['transactions']),(holder.get('path') or holder.get('name'),o['name']))

    # ---- R191 / A58 -----------------------------------------------------
    def test_ket_case_reproduced_object_total_follows_allocation_category(self):
        t=self.ket_case();rootK=self.obj_in(self.root('principal'),self.person)
        self.assertNotIn(t['id'],{r['transaction'] for r in self.store.category_history(dict(category='principal',object=self.person))['rows']})
        self.assertEqual(D_(rootK['totals']['out']),10000000)                                               # chỉ K2 (Gốc vay); K1 ở danh mục con không cộng vào Kết ở cha
        i=self.issues('K1')[0];self.assertEqual((i['path'],i['object'],i['amount'],i['can_add']),('Gốc vay › Kết','Kết','5000000',True));self.assertEqual([x['category'] for x in i['choices']],['principal'])
        self.assertEqual(D_(self.node('Kết')['totals']['out']),5000000);self.assertEqual(D_(self.root('principal')['totals']['out']),15000000)   # tổng danh mục không đổi, một giao dịch nguồn
        self.assertEqual(sum(1 for x in self.store.state()['transactions'] if x['reference']=='K1'),1)
        self.assert_screens_consistent()

    def test_resolution_add_membership_changes_no_money(self):
        t=self.ket_case();before=copy.deepcopy(t);rep0=self.store.report(self.store.state(),self.account);roots0=[r['totals'] for r in self.view()['categories']['roots']]
        self.act('category-object-add',category=self.node('Kết')['id'],profile=self.person)
        self.assertEqual(self.issues('K1'),[]);self.assertEqual(self.obj_in(self.node('Kết'),self.person)['totals']['transactions'],1)
        self.assertEqual(self.tx('K1'),before);self.assertEqual(self.store.report(self.store.state(),self.account),rep0);self.assertEqual([r['totals'] for r in self.view()['categories']['roots']],roots0)
        self.assert_screens_consistent()

    def test_resolution_reclassify_preview_equals_result_and_keeps_source(self):
        t=self.ket_case();before=copy.deepcopy(t);roots0=[r['totals'] for r in self.view()['categories']['roots']]
        p=self.store.classification_preview(dict(transaction=t['id'],category='principal'));self.assertEqual((p['before'],p['after'],p['amount'],p['approved']),('Gốc vay › Kết','Gốc vay','5000000',False))
        self.err('category-correct-classification',transaction=t['id'],category='principal')                                 # cần lý do
        self.act('category-correct-classification',transaction=t['id'],category='principal',reason='Thạch chọn Gốc vay')
        t=self.tx('K1');self.assertEqual(t['allocations'],p['parts']);self.assertEqual((t['sources'],t['signed_amount'],t['reference']),(before['sources'],before['signed_amount'],before['reference']))
        self.assertEqual(t['classification_history'][-1]['reason'],'Thạch chọn Gốc vay');self.assertEqual(self.issues('K1'),[])
        self.assertEqual(D_(self.obj_in(self.root('principal'),self.person)['totals']['out']),15000000);self.assertEqual([r['totals'] for r in self.view()['categories']['roots']],roots0)
        self.assert_screens_consistent()

    def test_correction_guards_root_type_membership_loan_group_split(self):
        self.ket_case()
        k4=self.tx('K4');self.assertEqual(self.issues('K4')[0]['choices'],[])                                              # lãi không được gợi ý chuyển sang Gốc vay
        with self.assertRaises(ValidationError):self.store.classification_preview(dict(transaction=k4['id'],category='principal'))
        with self.assertRaises(ValidationError):self.store.classification_preview(dict(transaction=self.tx('K1')['id'],category=self.node('Loans')['id']))   # Kết không thuộc Loans
        self.act('category-object-add',category=self.node('Loans')['id'],profile=self.person);self.act('loan-regroup',profile=self.l5,node=self.node('Long debt')['id'],effective_date='2026-09-21',reason='QA')
        with self.assertRaises(ValidationError):self.store.classification_preview(dict(transaction=self.tx('K1')['id'],category=self.node('Loans')['id']))   # khoản vay có nhóm riêng: xem trước sẽ khác kết quả → chặn
        self.act('classify',ids=[self.tx('X1')['id']],parts=[dict(category='principal',profile=self.l10,amount='5000'),dict(category='principal',profile=self.l10,amount='5000')])
        with self.assertRaises(ValidationError):self.store.classification_preview(dict(transaction=self.tx('X1')['id'],category='principal'))

    def test_approved_row_needs_adjustment_and_snapshot_is_immutable(self):
        t=self.ket_case();self.act('approve',account=self.account,reason='QA duyệt',confirm_unknown=True);snap=copy.deepcopy(self.store.state()['snapshots'][-1])
        self.assertTrue(self.store.classification_preview(dict(transaction=t['id'],category='principal'))['approved'])
        self.err('category-correct-classification',transaction=t['id'],category='principal',reason='x')                       # chưa mở phiên điều chỉnh
        self.act('begin-adjustment',account=self.account,reason='Sửa nơi phân loại');self.act('category-correct-classification',transaction=t['id'],category='principal',reason='x')
        self.assertEqual(self.store.state()['snapshots'][-1],snap);self.assertNotIn('node',self.tx('K1')['allocations'][0])

    # ---- R192 / A59: bank -------------------------------------------------
    def test_bank_reimport_same_file_adds_nothing_and_duplicate_ref_in_file_blocks(self):
        n=len(self.store.state()['transactions']);imp=self.store.state()['imports'][0]
        content=base64.b64encode(statement(base.ROWS,1000000000,1008190000,start='01/09/2026',end='30/09/2026')).decode()
        self.act('import',account=self.account,filename='lai.xlsx',content=content);s=self.store.state();b=s['imports'][-1];issues,new,dups=self.store.check_batch(s,b)
        self.assertEqual((issues,len(new),len(dups)),([],0,len(base.ROWS)));self.assertEqual(len(self.store.state()['transactions']),n)          # nhập lặp không thêm giao dịch nào
        s=self.store.state();bb=copy.deepcopy(imp);r=bb['rows'][0];s['transactions']=[];bb['rows']=[r,dict(r,source_row=r['source_row']+1)]
        self.assertTrue(any('lặp trong cùng file' in x for x in self.store.check_batch(s,bb)[0]))
        s=self.store.state();bb=copy.deepcopy(imp);bb['rows'][0]=dict(bb['rows'][0],signed_amount='-4000000')
        self.assertTrue(any('xung đột' in x for x in self.store.check_batch(s,bb)[0]))                                       # cùng mã khác nội dung

    def test_same_reference_in_another_account_is_kept_separate(self):
        self.act('account',name='QA khác',reference='000456',opening='1000000000',effective_date='2026-09-01',opening_source='QA');other=self.store.state()['accounts'][-1]['id']
        content=base64.b64encode(statement(base.ROWS,1000000000,1008190000,start='01/09/2026',end='30/09/2026',account='000456')).decode()
        self.act('import',account=other,filename='k2.xlsx',content=content);s=self.store.state();b=s['imports'][-1];issues,new,dups=self.store.check_batch(s,b);self.assertEqual((issues,len(new),len(dups)),([],len(base.ROWS),0))
        self.act('publish',batch=b['id']);self.assertEqual(sum(1 for t in self.store.state()['transactions'] if t['reference']=='K1'),2)

    # ---- R193: lịch sử cũ ---------------------------------------------------
    def test_legacy_scoped_duplicates_across_objects_and_accounts(self):
        text='05/06/2023\tA\tFT1\t30000000\t\t1'
        d=dict(category='principal',name='Alpha',type='PERSON',text=text,account=self.account)
        with self.assertRaises(ValidationError):self.store.legacy_preview({**d,'account':None})
        self.act('legacy-import',**d)
        p=self.store.legacy_preview({**d,'name':'Beta'});self.assertEqual((p['duplicates'],p['can_import']),(1,False))         # cùng tài khoản, khác đối tượng: không cộng lần hai
        self.assertTrue(self.store.legacy_preview({**d,'text':text.replace('30000000','40000000')})['issues'])                   # cùng mã khác nội dung
        self.act('account',name='Other',reference='222',opening='0',effective_date='2023-01-01',opening_source='QA');other=self.store.state()['accounts'][-1]['id']
        self.assertTrue(self.store.legacy_preview({**d,'name':'Beta','account':other})['can_import'])
        self.assertTrue(self.store.legacy_preview({**d,'text':"05/06/2023\tA\t\t30000000\t\t1"})['issues'])                    # thiếu mã: không định danh được

    def test_old_batch_without_account_is_provisional_and_resolution_preview_equals_result(self):
        d=dict(category='principal',name='Alpha',type='PERSON',text='05/06/2023\tA\tFT1\t30000000\t\t1\n06/06/2023\tB\tFT2\t1000000\t\t1',account=self.account)
        self.act('legacy-import',**d);s=self.store.state();b=s['legacy_batches'][-1];b.pop('account')                         # mô phỏng dữ liệu cũ thiếu tài khoản
        self.assertEqual(self.store.legacy_summary(s)[0]['unresolved'],2);self.assertEqual(len(list(self.store.legacy_items(s))),2)
        rows=self.store.category_history(dict(category='principal'),s)['rows'];self.assertTrue(all(r['provisional'] for r in rows if r['legacy']))
        p=self.store.legacy_account_preview(dict(batch=b['id'],account=self.account),s);self.assertEqual((p['before_total'],p['after_total'],p['issues']),('-31000000','-31000000',[]))
        self.assertNotIn('account',b)                                                                                           # xem trước không đổi dữ liệu
        text0=b['source_text'];self.store.change_legacy(s,'legacy-resolve-account',dict(batch=b['id'],account=self.account,reason='Thạch xác nhận'))
        after=sum((Decimal(t['signed_amount']) for t,_ in self.store.legacy_items(s)),Decimal(0));self.assertEqual(str(after),p['after_total'])
        self.assertEqual((b['account'],b['source_text'],b['account_history'][0]['reason']),(self.account,text0,'Thạch xác nhận'))

    def test_resolution_blocked_when_it_would_move_money_between_batches(self):
        text='05/06/2023\tA\tFT1\t30000000\t\t1'
        self.act('legacy-import',category='principal',name='Alpha',type='PERSON',text=text,account=self.account)
        s=self.store.state();a=s['legacy_batches'][-1];a.pop('account')                                                         # A: cũ, chưa có tài khoản
        self.store.change_legacy(s,'legacy-import',dict(category='principal',name='Beta',type='PERSON',text=text,account=self.account))   # B: nhập sau, đã có tài khoản
        counted=lambda:sorted(e['profile'] for t,_ in self.store.legacy_items(s) for e in s['legacy_entries'] if e['id']==t['id'])
        before=counted()
        p=self.store.legacy_account_preview(dict(batch=a['id'],account=self.account),s);self.assertTrue(any('lần migrate khác' in x['message'] for x in p['issues']))
        with self.assertRaises(ValidationError):self.store.change_legacy(s,'legacy-resolve-account',dict(batch=a['id'],account=self.account,reason='x'))
        self.assertNotIn('account',a);self.assertEqual(counted(),before)

    def test_bank_import_conflicting_with_scoped_legacy_is_blocked(self):
        self.act('legacy-import',category='principal',name='Alpha',account=self.account,text='05/06/2023\tA\tFT1\t30000000\t\t1')
        s=self.store.state();b=copy.deepcopy(s['imports'][0]);b['rows'][0].update(reference='FT1')
        self.assertTrue(any('lịch sử cũ' in x for x in self.store.check_batch(s,b)[0]))

    # ---- PO review P1 (22/10): gần trùng khác hậu tố, mọi thứ tự nhập -------------------------
    def other_account(self):
        self.act('account',name='QA B',reference='000456',opening='1000000000',effective_date='2026-09-01',opening_source='QA');return self.store.state()['accounts'][-1]['id']
    def stage_b(self,acc):
        content=base64.b64encode(statement(base.ROWS,1000000000,1008190000,start='01/09/2026',end='30/09/2026',account='000456')).decode()
        self.act('import',account=acc,filename='b.xlsx',content=content);return self.store.state()['imports'][-1]
    K1_SAME="20/09/2026\tCho Ket vay 5tr\tK1\\BNK\t5,000,000\t\t1\n"                                                  # cùng ngày/nội dung/tiền với K1 sao kê, chỉ khác hậu tố

    def test_near_duplicate_legacy_first_then_bank_is_blocked_in_check_and_publish(self):
        acc=self.other_account();self.act('legacy-import',category='principal',name='Alpha',account=acc,text=self.K1_SAME)
        b=self.stage_b(acc);s=self.store.state();issues=self.store.check_batch(s,b)[0];self.assertTrue(any('gần trùng' in x for x in issues))
        self.err('publish',batch=b['id']);self.assertFalse(any(t['account']==acc for t in self.store.state()['transactions']))   # không ghi, không cộng hai lần

    def test_near_duplicate_bank_first_then_legacy_is_blocked(self):
        p=self.store.legacy_preview(dict(category='principal',name='Alpha',account=self.account,text=self.K1_SAME));self.assertTrue(any('gần trùng' in x['message'] for x in p['issues']))
        self.err('legacy-import',category='principal',name='Alpha',account=self.account,text=self.K1_SAME)

    def test_near_duplicate_in_other_account_is_not_flagged(self):
        acc=self.other_account();self.act('legacy-import',category='principal',name='Alpha',account=acc,text=self.K1_SAME)          # tài khoản B; sao kê K1 ở tài khoản A
        st=self.store.legacy_identity_status(self.store.state());self.assertEqual(set(st.values()),{'ACTIVE'})
        b=self.stage_b(acc);issues=self.store.check_batch(self.store.state(),b)[0];self.assertTrue(any('gần trùng' in x for x in issues))   # cùng tài khoản B thì vẫn chặn
        self.assertFalse(any('gần trùng' in x for x in self.store.check_batch(self.store.state(),self.store.state()['imports'][0])[0]))   # file của tài khoản A không bị ảnh hưởng

    def test_near_duplicate_between_two_legacy_pastes_and_resolution(self):
        self.act('legacy-import',category='principal',name='Alpha',account=self.account,text="05/06/2023\tA\tFT9\t1,000,000\t\t1\n")
        self.assertTrue(self.store.legacy_preview(dict(category='principal',name='Beta',account=self.account,text="05/06/2023\tA\tFT9\\X\t1,000,000\t\t1\n"))['issues'])
        self.act('legacy-import',category='principal',name='Gamma',account=self.account,text="07/06/2023\tC\tFT7\t2,000,000\t\t1\n")
        s=self.store.state();g=s['legacy_batches'][-1];g.pop('account');g_entry=next(e for e in s['legacy_entries'] if e['batch']==g['id']);g_entry['reference']='K1\\BNK'   # lịch sử cũ thiếu tài khoản, gần trùng K1 sao kê
        p=self.store.legacy_account_preview(dict(batch=g['id'],account=self.account),s);self.assertTrue(any('gần trùng' in x['message'] for x in p['issues']))
        with self.assertRaises(ValidationError):self.store.change_legacy(s,'legacy-resolve-account',dict(batch=g['id'],account=self.account,reason='x'))
        g['account']=self.account;st=self.store.legacy_identity_status(s);self.assertEqual(st[g_entry['id']],'NEAR_DUPLICATE')            # kể cả khi dữ liệu đã lỡ có: không cộng, cần đối chiếu
        self.assertNotIn(g_entry['id'],{t['id'] for t,_ in self.store.legacy_items(s)})

    # ---- PO review P1 (22/10): mọi phân loại mới phải đúng quan hệ đối tượng–danh mục hiệu lực ----------
    def test_new_classification_blocked_when_owner_not_member_of_effective_category(self):
        self.ket_case();x1=self.tx('X1')['id'];kn=self.node('Kết')['id']
        self.err('classify',ids=[x1],parts=[dict(category='principal',node=kn,profile=self.l5)])                                       # ca PO tái hiện: Kết thuộc Gốc vay, không thuộc Gốc vay › Kết
        self.assertNotIn('X1',[i['reference'] for i in self.issues()]);self.assertEqual(self.tx('X1')['allocations'],[])
        self.act('classify',ids=[x1],parts=[dict(category='principal',profile=self.l5)])                                                # đúng quan hệ: được
        self.act('object-quick-create',kind='PROPERTY',name='Đất QA');prop=next(p['id'] for p in self.store.state()['profiles'] if p['name']=='Đất QA')
        self.err('classify',ids=[self.tx('S1')['id']],parts=[dict(category='investment',profile=prop)])                                # BĐS chưa thuộc Đầu tư BĐS
        self.act('category-object-add',category='investment',profile=prop);self.act('classify',ids=[self.tx('S1')['id']],parts=[dict(category='investment',profile=prop)],_reclass=RECLASS_GRANT)   # đổi thu nhập → BĐS là mức B (spec 043)
        self.assertEqual(self.issues('X1')+self.issues('S1'),[])

    def test_loan_group_and_object_move_use_effective_category(self):
        self.ket_case();ld=self.node('Long debt')['id']
        self.act('loan-regroup',profile=self.l5,node=ld,effective_date='2026-09-21',reason='QA')
        self.err('classify',ids=[self.tx('X1')['id']],parts=[dict(category='principal',profile=self.l5)])                              # nhóm khoản vay đưa tiền về Long debt, Kết chưa thuộc Long debt
        self.act('category-object-add',category=ld,profile=self.person);self.act('classify',ids=[self.tx('X1')['id']],parts=[dict(category='principal',profile=self.l5)])
        self.act('category-create',name='A',description='',parent='expense');self.act('category-create',name='B',description='',parent='expense');self.act('category-create',name='C',description='',parent='expense')
        a,b,c=(self.node(n)['id'] for n in 'ABC');self.act('object-create',name='Mỹ',type='PERSON',category=a);my=next(p['id'] for p in self.store.state()['profiles'] if p['name']=='Mỹ')
        self.act('category-object-move',profile=my,reason='QA',**{'from':a,'to':b})
        self.act('classify',ids=[self.tx('S1')['id']],parts=[dict(category='expense',node=a,profile=my)])                              # chuyển đối tượng A→B: danh mục hiệu lực là B, Mỹ thuộc B
        self.err('classify',ids=[self.tx('K3')['id']],parts=[dict(category='expense',node=c,profile=my)])
        self.assertEqual(self.issues('S1'),[])

    def test_unchanged_old_part_can_be_resaved_but_not_moved_to_another_invalid_place(self):
        self.ket_case();k1=self.tx('K1');parts=copy.deepcopy(k1['allocations'])
        self.act('classify',ids=[k1['id']],parts=parts,note='Ghi chú thêm')                                                            # dữ liệu cũ giữ nguyên được (kèm ghi chú)
        self.assertEqual(self.tx('K1')['allocations'],parts);self.assertEqual(len(self.issues('K1')),1)                               # vẫn hiện ở mục Cần đối chiếu
        self.err('classify',ids=[k1['id']],parts=[dict(category='principal',node=self.node('Loans')['id'],profile=self.l5)])

    def test_void_batch_keeps_reference_totals_but_counts_nothing(self):
        self.act('legacy-import',category='principal',name='Alpha',account=self.account,text="05/06/2023\tA\tFT1\t30,000,000\t\t1\n")
        b=self.store.state()['legacy_batches'][-1];self.act('legacy-void',batch=b['id'],reason='QA')
        row=next(x for x in self.store.view()['categories']['legacy'] if x['id']==b['id']);self.assertEqual((row['status'],row['active'],row['totals']['out']),('VOID',0,'30000000'))
        self.assertEqual(list(self.store.legacy_items(self.store.state())),[])                                                  # đã hủy: không tính vào đâu

    # ---- PO review vòng 2 (22/10): gần trùng / lặp trong cùng file sao kê và cùng lần dán lịch sử -----------------
    def fresh_account(self,ref):
        self.act('account',name='QA '+ref,reference=ref,opening='1000000000',effective_date='2026-09-01',opening_source='QA');return self.store.state()['accounts'][-1]['id']
    def stage_rows(self,acc,ref,refs,name):
        bal=1000000000;rows=[]
        for r in refs:bal-=5000000;rows.append(('20/09/2026','QA transfer',r,'5000000','',str(bal)))       # số dư từng dòng hoàn toàn hợp lệ
        content=base64.b64encode(statement(rows,1000000000,bal,start='01/09/2026',end='30/09/2026',account=ref)).decode()
        self.act('import',account=acc,filename=name,content=content);return self.store.state()['imports'][-1]
    def tx_count(self,acc):return sum(1 for t in self.store.state()['transactions'] if t['account']==acc)

    def test_same_file_near_duplicate_blocks_import_and_publish_in_both_orders(self):
        for i,refs in enumerate((['FTQA','FTQA\\BNK'],['FTQA\\BNK','FTQA'])):
            acc=self.fresh_account('00077'+str(i));b=self.stage_rows(acc,'00077'+str(i),refs,f'gan-trung-{i}.xlsx')
            self.assertEqual(b['status'],'BLOCKED');self.assertTrue(any('gần trùng' in x and 'cùng file' in x for x in b['issues']),b['issues'])
            issues,new,_=self.store.check_batch(self.store.state(),b);self.assertTrue(any('cùng file' in x for x in issues))
            self.err('publish',batch=b['id']);self.assertEqual(self.tx_count(acc),0)                                         # bị chặn: không ghi giao dịch nào, không tự gộp

    def test_same_file_exact_duplicate_blocks_import_and_publish(self):
        acc=self.fresh_account('000775');b=self.stage_rows(acc,'000775',['FTQA','FTQA'],'lap.xlsx')
        self.assertEqual(b['status'],'BLOCKED');self.assertTrue(any('lặp trong cùng file' in x for x in b['issues']))
        self.err('publish',batch=b['id']);self.assertEqual(self.tx_count(acc),0)

    def test_suffix_variants_in_different_accounts_are_kept_separate(self):
        a=self.fresh_account('000776');b=self.fresh_account('000778')
        ba=self.stage_rows(a,'000776',['FTQA'],'a.xlsx');bb=self.stage_rows(b,'000778',['FTQA\\BNK'],'b.xlsx')
        self.assertEqual((ba['status'],ba['issues'],bb['status'],bb['issues']),('STAGED',[],'STAGED',[]))
        self.act('publish',batch=ba['id']);self.act('publish',batch=bb['id']);self.assertEqual((self.tx_count(a),self.tx_count(b)),(1,1))

    def test_same_paste_exact_and_near_duplicates_block_preview_and_import(self):
        n0=len(self.store.state().get('legacy_entries',[]))
        row=lambda ref:f"05/06/2023\tQA\t{ref}\t1,000,000\t\t1\n"
        for text,word in ((row('FT8')+row('FT8'),'lặp trong cùng lần dán'),(row('FT8')+row('FT8\\X'),'gần trùng'),(row('FT8\\X')+row('FT8'),'gần trùng')):
            p=self.store.legacy_preview(dict(category='principal',name='Alpha',type='PERSON',account=self.account,text=text))
            self.assertTrue(any(word in x['message'] for x in p['issues']),p['issues']);self.assertFalse(p['can_import']);self.assertEqual(p['duplicates'],0)   # không coi là "trùng lần trước" để tự bỏ qua
            self.err('legacy-import',category='principal',name='Alpha',type='PERSON',account=self.account,text=text)
        self.assertEqual(len(self.store.state().get('legacy_entries',[])),n0)
        other=self.fresh_account('000779')
        self.act('legacy-import',category='principal',name='Alpha',type='PERSON',account=self.account,text=row('FT8'));self.act('legacy-import',category='principal',name='Alpha',account=other,text=row('FT8\\X'))   # khác tài khoản: giữ riêng
        self.assertEqual(len(self.store.state()['legacy_entries']),n0+2)

if __name__=='__main__':unittest.main()
