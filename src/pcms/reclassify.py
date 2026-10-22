"""Sửa phân loại giao dịch (spec 043, R195–R200).

Một chức năng chung để đổi danh mục và/hoặc đối tượng của **một phần** phân loại. Nguồn bất biến; ghi đi qua đúng
`classify` (giao dịch ngân hàng) hoặc thao tác dòng lịch sử cũ. Xem trước = mô phỏng chính thao tác ghi trên bản sao,
nên những gì xem trước hiển thị là những gì sẽ được ghi. Mức B (ảnh hưởng công nợ, lãi, tài sản) cần xác nhận riêng;
khi giao dịch đã bị nghiệp vụ tham chiếu thì chặn kèm đường xử lý.
"""
import copy
from decimal import Decimal, localcontext
from .core import require, digest, ValidationError
from .product import D, S, item

BIZ_ROOTS={'principal','interest','investment'}
ROOT_NAMES={'income','expense','principal','interest','investment','transfer','transfer_pending','unknown'}
ROOT_OF={'transfer_pending':'transfer'}

def _root(category):
    return ROOT_OF.get(category,category)

class Reclassify:
    # ---- mức A / B ---------------------------------------------------------------
    def reclass_signature(self,s,part):
        """Business signature of a part: what the debt register, interest and realty read from it. None for plain parts."""
        prof=next((p for p in s['profiles'] if p['id']==part.get('profile')),None) if part.get('profile') else None
        root=_root(part['category']);biz_root=root if root in BIZ_ROOTS else None
        biz_prof=prof['id'] if prof and prof['kind'] in {'LOAN','PROPERTY'} else None
        cap=bool(self.cat_flag(s,part.get('node'),'capitalize')) if prof and prof['kind']=='PROPERTY' else None
        return (biz_root,biz_prof,cap) if (biz_root or biz_prof) else None

    def reclass_level(self,s,before,after):
        """'B' when the change alters what business ledgers read (debts, interest, assets); first classification is never B."""
        if not before or all(p['category']=='unknown' for p in before):return 'A'
        sig=lambda parts:sorted((repr(self.reclass_signature(s,p)),str(D(p['amount']))) for p in parts if self.reclass_signature(s,p))
        return 'B' if sig(before)!=sig(after) else 'A'

    def reclass_reference_blocks(self,s,t,before,after,level):
        """Business records that already rely on this transaction: always block, with the way out."""
        blocks=[];key=lambda p:(p['category'],p.get('node') or None,p.get('profile') or None,str(D(p['amount'])))
        changed=[p for p in before if key(p) not in {key(x) for x in after}]+[p for p in after if key(p) not in {key(x) for x in before}]
        if t.get('transfer_match'):blocks.append(dict(code='TRANSFER',message='Giao dịch chuyển nội bộ đã ghép hai đầu; không sửa phân loại.'))
        if t.get('legacy'):
            b=next((x for x in s.get('legacy_batches',[]) if any(e['id']==t['id'] and e['batch']==x['id'] for e in s.get('legacy_entries',[]))),None)
            if b and b['status']!='ACTIVE':blocks.append(dict(code='VOID',message='Dòng thuộc lần migrate đã hủy; không sửa.'))
        for pid in {p.get('profile') for p in changed if p.get('profile')}:
            prof=next((x for x in s['profiles'] if x['id']==pid),None)
            if prof and prof['kind']=='LOAN' and prof.get('completion_history') and prof['completion_history'][-1]['action']!='REOPEN':
                blocks.append(dict(code='LOAN_COMPLETED',message=f"Khoản vay {prof['name']} đã hoàn tất; mở lại ở màn Công nợ trước khi sửa phân loại."))
        if level=='B':
            if any(x.get('transaction')==t['id'] for st in s.get('interest_statements',[]) if st.get('versions') for x in st['versions'][-1]['draft'].get('payments',[])):
                blocks.append(dict(code='INTEREST_STATEMENT',message='Giao dịch đang được dùng trong bảng kê lãi; mở lại bảng kê ở màn Công nợ trước khi đổi nghiệp vụ.'))
            if any(l['status']=='ACTIVE' and l['transaction']==t['id'] for l in (s.get('realty') or {}).get('pay_links',[])):
                blocks.append(dict(code='REALTY_LINK',message='Giao dịch đã gắn một đợt thanh toán BĐS; bỏ gắn ở màn Bất động sản trước khi đổi nghiệp vụ.'))
        return blocks

    # ---- xem trước ------------------------------------------------------------------
    def reclass_source(self,s,tid):
        t=next((x for x in s['transactions'] if x['id']==tid),None)
        if t is not None:return t,None
        e=next((x for x in s.get('legacy_entries',[]) if x['id']==tid),None);require(e is not None,'Không tìm thấy giao dịch.')
        node=next((n for n in s.get('categories',[]) if n['id']==e['category']),None)
        part={'category':node['root'] if node else e['category'],'amount':e['amount'],'profile':e.get('profile')}
        if node:part['node']=node['id']
        pseudo=dict(id=e['id'],account=self.legacy_account(s,e),date=e['date'],reference=e['reference'],description=e['description'],signed_amount=e['amount'] if e['direction']=='IN' else '-'+e['amount'],allocations=[part],legacy=True)
        return pseudo,e

    def reclass_snapshot(self,s):
        """Totals the user sees, used to show (and prove) what changes."""
        c=self.category_view(s);out={}
        for r in c['roots']:out[('cat',r['key'])]=dict(path=r['name'],totals=r['totals'])
        for n in c['nodes']:out[('cat',n['id'])]=dict(path=n['path'],totals=n['totals'])
        for h in c['roots']+c['nodes']:
            hk=h.get('key') or h['id'];hp=h.get('path') or h['name']
            for o in h['objects']:out[('obj',hk,o['profile'])]=dict(path=hp,object=o['name'],totals=o['totals'])
        loans={l['id']:dict(name=self.disp_name(s,l['id'])+' · '+l['name'],principal=l['current_principal'],principal_in=l['principal_in'],principal_out=l['principal_out'],interest_received=l['interest_received'],interest_paid=l['interest_paid'],issues=l['issues']) for l in self.debt_register(s)['loans']}
        props={p['id']:dict(name=p['name'],basis=p['capital'].get('basis'),acquisition=p['capital'].get('acquisition'),costs=p.get('costs')) for p in self.realty_view(s)['properties']}
        source={a['id']:(r['balance'],r['transaction_count']) for a,r in ((a,self.report(s,a['id'])) for a in s['accounts'])}
        return out,loans,props,source

    def reclassify_preview(self,d,s=None):
        with localcontext() as ctx:
            ctx.prec=60
            base=copy.deepcopy(s or self.state());base.setdefault('category_objects',[])
            tid=d.get('transaction');t,entry=self.reclass_source(base,tid)
            try:idx=int(d.get('part') or 0)
            except (TypeError,ValueError):idx=-1
            before=copy.deepcopy(t['allocations']) or [{'category':'unknown','amount':S(abs(D(t['signed_amount']))),'profile':None}]
            require(0<=idx<len(before),'Chọn phần phân loại cần sửa.')
            key=d.get('category');require(key,'Chọn danh mục đích.');profile=d.get('profile') or None
            node=next((n for n in base.get('categories',[]) if n['id']==key),None)
            require(node is not None or key in {'income','expense','principal','interest','investment','transfer_pending','unknown'},'Danh mục đích không tồn tại.')
            new={'category':node['root'] if node else key,'amount':before[idx]['amount'],'profile':profile}
            if node:new['node']=node['id']
            after=copy.deepcopy(before);after[idx]=new
            blocks=[];needs_membership=None
            same=lambda a,b:(a['category'],a.get('node') or None,a.get('profile') or None)==(b['category'],b.get('node') or None,b.get('profile') or None)
            if same(before[idx],new):blocks.append(dict(code='NO_CHANGE',message='Phần này đã ở đúng danh mục và đối tượng đã chọn.'))
            if node and node['status']!='ACTIVE':blocks.append(dict(code='ARCHIVED',message='Danh mục đích đang lưu trữ; khôi phục trước hoặc chọn danh mục khác.'))
            prof=None
            if profile:
                prof=next((p for p in base['profiles'] if p['id']==profile),None)
                if prof is None or prof.get('merged_into'):blocks.append(dict(code='PROFILE',message='Đối tượng không tồn tại hoặc đã được gộp vào hồ sơ khác.'));prof=None
                elif prof.get('status')=='ARCHIVED':blocks.append(dict(code='ARCHIVED',message='Đối tượng đang lưu trữ; khôi phục ở màn Đối tượng trước.'))
            if prof:
                owner=self.part_owner(base,prof);eff=self.cat_target(self.cat_eff(base,new))
                if eff!=(node['id'] if node else key):blocks.append(dict(code='LOAN_GROUP',message='Khoản vay này thuộc một nhóm riêng nên tiền của nó luôn hiện ở nhóm đó; muốn đổi nơi hiển thị, dùng Công nợ → Chuyển danh mục khoản vay.'))
                elif not self.is_member(base,eff,owner):
                    needs_membership=dict(category=eff,path=self.reclass_label(base,dict(category=new['category'],node=None if eff in ROOT_NAMES else eff,profile=None,amount='0'))['path'],profile=owner,name=self.disp_name(base,owner))
                    blocks.append(dict(code='NOT_MEMBER',message=f"{needs_membership['name']} chưa là thành viên danh mục đích. Thêm vào danh mục (có xác nhận riêng) rồi xem trước lại."))
            level=self.reclass_level(base,before,after)
            if entry is not None and _root(before[idx]['category'])!=_root(new['category']):blocks.append(dict(code='LEGACY_ROOT',message='Dòng lịch sử cũ chỉ đổi danh mục/đối tượng trong cùng loại gốc; muốn đổi loại, hủy lần migrate và migrate lại.'))
            blocks+=self.reclass_reference_blocks(base,t,before,after,level)
            approved=entry is None and any(any(x['id']==t['id'] for x in sn['report']['transactions']) for sn in base['snapshots'] if sn['account']==t['account'])
            acc=next((a for a in base['accounts'] if a['id']==t['account']),None)
            result=dict(transaction=t['id'],legacy=entry is not None,source=dict(date=t['date'],account=acc['name'] if acc else None,reference=t['reference'],description=t['description'],amount=S(abs(D(t['signed_amount']))),direction='IN' if D(t['signed_amount'])>0 else 'OUT'),
                part=idx,moved=S(D(before[idx]['amount'])),parts_before=[self.reclass_label(base,p) for p in before],parts_after=[self.reclass_label(base,p) for p in after],
                level=level,approved=approved,needs_adjustment=bool(approved and not (acc or {}).get('adjustment_open')),needs_membership=needs_membership,blocks=blocks,effects=None,business=None,invariants=None,draft=True)
            if not blocks:
                sim=copy.deepcopy(base)
                try:self.reclass_apply(sim,t['id'],idx,after,'Xem trước',simulate=True)
                except ValidationError as exc:blocks.append(dict(code='RULE',message=str(exc)))
            if not blocks:
                b_cat,b_loan,b_prop,b_src=self.reclass_snapshot(base);a_cat,a_loan,a_prop,a_src=self.reclass_snapshot(sim)
                cats=[dict(path=v['path'],object=v.get('object'),kind=k[0],before=(b_cat.get(k) or {}).get('totals'),after=(a_cat.get(k) or {}).get('totals')) for k,v in sorted({**b_cat,**a_cat}.items(),key=lambda kv:repr(kv[0])) if (b_cat.get(k) or {}).get('totals')!=(a_cat.get(k) or {}).get('totals')]
                loans=[dict(name=b_loan[i]['name'],before=b_loan[i],after=a_loan[i]) for i in b_loan if b_loan[i]!=a_loan.get(i)]
                props=[dict(name=b_prop[i]['name'],before=b_prop[i],after=a_prop[i]) for i in b_prop if b_prop[i]!=a_prop.get(i)]
                result.update(effects=dict(categories=[c for c in cats if c['kind']=='cat'],objects=[c for c in cats if c['kind']=='obj']),business=dict(loans=loans,properties=props),
                    invariants=dict(source_unchanged=b_src==a_src,transactions_same=len(base['transactions'])==len(sim['transactions'])))
                if not (b_src==a_src):blocks.append(dict(code='INTERNAL',message='Mô phỏng làm đổi số dư nguồn; không ghi.'))
                if level=='B' and not (loans or props):result['business']['note']='Không có số dư khoản vay hoặc giá gốc BĐS nào thay đổi.'
            result['blocks']=blocks;result['can_commit']=not blocks
            result['review_token']=digest({k:result[k] for k in ('transaction','part','parts_before','parts_after','level','approved','effects','business','invariants','blocks')})
            result['parts_raw']=after
            return result

    def reclass_label(self,s,p):
        node=p.get('node');path=self.cat_path(s,node) if node else {'income':'Thu nhập','expense':'Chi tiêu','principal':'Gốc vay','interest':'Lãi vay','investment':'Đầu tư BĐS','transfer_pending':'Chuyển nội bộ · chờ đối ứng','transfer':'Chuyển nội bộ','unknown':'Chưa phân loại'}.get(p['category'],p['category'])
        prof=next((x for x in s['profiles'] if x['id']==p.get('profile')),None) if p.get('profile') else None
        link=None
        if prof and prof['kind']=='LOAN':link='Khoản vay: '+prof['name']
        elif prof and prof['kind']=='PROPERTY':link='BĐS: '+prof['name']+(' (vốn hóa)' if self.cat_flag(s,node,'capitalize') else '')
        return dict(category=p['category'],node=node,path=path,profile=p.get('profile'),object=self.disp_name(s,p['profile']) if p.get('profile') else None,link=link,amount=S(D(p['amount'])))

    # ---- ghi -------------------------------------------------------------------------
    def reclass_apply(self,s,tid,idx,after,reason,simulate=False,business_ack=False):
        """The one write path: classify for bank transactions, the row itself for legacy rows."""
        from .p01 import now
        t=next((x for x in s['transactions'] if x['id']==tid),None)
        if t is not None:
            if simulate:
                acc=next((a for a in s['accounts'] if a['id']==t['account']),None)
                if acc is not None:acc['adjustment_open']=True                     # mô phỏng phiên điều chỉnh mà bước ghi sẽ yêu cầu
            payload=[{k:v for k,v in p.items() if k in {'category','amount','profile','node'}} for p in after]
            return self.change(s,'classify',dict(ids=[tid],parts=payload,reason=reason,business_ack=True if simulate else business_ack))
        e=item(s['legacy_entries'],tid);p=after[0];key=p.get('node') or p['category']
        b=next((x for x in s.get('legacy_batches',[]) if x['id']==e['batch']),None);require(b and b['status']=='ACTIVE','Dòng thuộc lần migrate đã hủy; không sửa.')
        require(p.get('profile'),'Dòng lịch sử cũ cần một đối tượng.')
        prof=item(s['profiles'],p['profile']);require(self.is_member(s,self.cat_target(self.cat_eff(s,p)),self.part_owner(s,prof)),'Đối tượng chưa là thành viên danh mục đích.')
        before=dict(category=e['category'],profile=e.get('profile'));e['category']=key;e['profile']=p['profile']
        e.setdefault('classification_history',[]).append(dict(at=now(),before=before,after=dict(category=key,profile=p['profile']),reason=reason))
        return 'Sửa phân loại dòng lịch sử cũ'

    def change_reclassify(self,s,d):
        reason=str(d.get('reason') or '').strip()[:500];require(reason,'Cần lý do thay đổi.')
        p=self.reclassify_preview(d,s)
        require(not p['blocks'],p['blocks'][0]['message'] if p['blocks'] else '')
        require(d.get('review_token')==p['review_token'],'Dữ liệu hoặc lựa chọn đã thay đổi sau khi xem trước; hãy xem trước lại.')
        if p['level']=='B':require(d.get('confirm_business') is True,'Thay đổi này ảnh hưởng công nợ, lãi hoặc tài sản: xác nhận đã xem tác động trước khi ghi.')
        self.reclass_apply(s,p['transaction'],p['part'],p['parts_raw'],reason,business_ack=p['level']=='B')
        t=next((x for x in s['transactions'] if x['id']==p['transaction']),None)
        if t is not None and t.get('classification_history'):t['classification_history'][-1]['reclassify']=dict(part=p['part'],level=p['level'],review_token=p['review_token'])
        return f"Sửa phân loại {p['source']['reference']}: {p['parts_before'][p['part']]['path']} → {p['parts_after'][p['part']]['path']}"
