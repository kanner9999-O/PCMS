"""Category tree: fixed system roots plus user-created child categories, totals and traceable history.

Totals come only from classified parts of source transactions; nothing here creates or edits money.
"""
import copy
import json
import unicodedata
from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext
from .core import require
from .product import D, S, uid, item

ROOTS={'income':'Thu nhập','expense':'Chi tiêu','principal':'Gốc vay','interest':'Lãi vay','investment':'Đầu tư BĐS','transfer':'Chuyển nội bộ','unknown':'Chưa phân loại'}
PARENTABLE={'income','expense','principal','interest','investment'}
MAX_DEPTH=4
TEMPLATES={'realty-acquisition':dict(name='Chi phí mua BĐS (vốn hóa)',type='expense',flags={'capitalize':True},children=['Công chứng','Thuế trước bạ','Môi giới','Khác'],
    description='Chi phí trực tiếp liên quan việc mua BĐS: cộng vào giá gốc BĐS khi gắn hồ sơ BĐS.'),
  'no-voucher':dict(name='Chi khác không chứng từ',type='expense',flags={'note_required':True},children=[],
    description='Khoản chi không có chứng từ hợp lệ: hiển thị riêng, không vốn hóa, bắt buộc ghi chú.')}
ROLE_LABELS={'income':'Dòng tiền thu','expense':'Dòng tiền chi','principal':'Gốc vay','interest':'Lãi vay','investment':'Đầu tư BĐS','transfer':'Chuyển nội bộ','unknown':'Chưa phân loại'}
GROUPS={'default':'Nhóm mặc định'}
GROUP_NOTE='Chỉ tổng hợp tiền vào/ra, đưa vào báo cáo; chưa gắn nghiệp vụ.'
ROOT_TYPES={'income':'Nhóm thu','expense':'Nhóm chi','investment':'Nhóm đầu tư'}

def root_key(category):
    return 'transfer' if category=='transfer_pending' else category

def norm_name(value):
    return ' '.join(unicodedata.normalize('NFC',str(value or '')).split()).casefold()

def norm_ref_c(value):
    return str(value or '').split('\\')[0].strip().upper()

def cat_state(s):
    s.setdefault('categories',[]);s.setdefault('category_roots',{});s.setdefault('category_objects',[]);s.setdefault('object_moves',[])
    return s

class Categories:
    # ---- tree helpers -------------------------------------------------
    def cat_find(self,s,cid):
        found=next((n for n in cat_state(s)['categories'] if n['id']==cid),None)
        require(found is not None,'Không tìm thấy danh mục.')
        return found

    def cat_depth(self,s,node):
        """Levels counted from the top: a user-created root is 1, a child of any root is 2, and so on."""
        depth=1;cur=node
        while cur['parent'] is not None:
            depth+=1
            if cur['parent'] in ROOTS:break
            cur=self.cat_find(s,cur['parent'])
        return depth

    def cat_chain(self,s,cid):
        """Node ids from the given node up to (excluding) its root."""
        chain=[];by={n['id']:n for n in cat_state(s)['categories']}
        while cid in by:chain.append(cid);cid=by[cid]['parent']
        return chain

    def cat_height(self,s,node):
        kids=[n for n in s['categories'] if n['parent']==node['id']]
        return 1+max((self.cat_height(s,k) for k in kids),default=0)

    def cat_path(self,s,cid):
        names=[];by={n['id']:n for n in cat_state(s)['categories']}
        while cid in by:names.append(by[cid]['name']);cid=by[cid]['parent']
        if cid is not None:names.append(ROOTS.get(cid,cid))
        return ' › '.join(reversed(names))

    def cat_name_ok(self,s,name,parent,own=None):
        name=str(name or '').strip();require(1<=len(name)<=100,'Tên danh mục dài 1–100 ký tự.')
        if parent is None:require(not any(norm_name(v)==norm_name(name) for v in ROOTS.values()),'Tên trùng một danh mục gốc hệ thống.')
        require(not any(n['parent']==parent and n['id']!=own and norm_name(n['name'])==norm_name(name) for n in s['categories']),'Đã có danh mục cùng tên trong cùng danh mục cha (kể cả đã lưu trữ).')
        return name

    def cat_parent_ok(self,s,parent):
        if parent in ROOTS:
            require(parent in PARENTABLE,'Gốc này không có danh mục con.');return parent
        p=self.cat_find(s,parent);require(p['status']=='ACTIVE','Danh mục cha đang lưu trữ.');return p['root']

    def profile_clash(self,s,name,exclude=None):
        """The existing (not merged) profile of any kind that already uses this name, or None (R138)."""
        key=norm_name(name)
        return next((x for x in s['profiles'] if x['id']!=exclude and not x.get('merged_into') and norm_name(x['name'])==key),None)

    def require_free_name(self,s,name,exclude=None):
        other=self.profile_clash(s,name,exclude);kinds={'PERSON':'người','LOAN':'khoản vay','PROPERTY':'BĐS','OBJECT':'đối tượng'}
        require(other is None,f"Đã có hồ sơ tên \"{other['name']}\" (loại {kinds.get(other['kind'],other['kind'])}); hãy chọn hồ sơ có sẵn thay vì tạo trùng." if other else '')

    def cat_flag(self,s,node_id,flag):
        """Whether a category (or any ancestor) carries a business flag such as 'capitalize' or 'note_required'."""
        by={n['id']:n for n in s.get('categories',[])};cid=node_id
        while cid in by:
            if by[cid].get('flags',{}).get(flag):return True
            cid=by[cid]['parent']
        return False

    def apply_note(self,t,note,voucher):
        from .p01 import now
        before=dict(note=t.get('note',''),voucher=t.get('voucher',''));new=dict(before)
        if note is not None:new['note']=str(note).strip()[:1000]
        if voucher is not None:new['voucher']=str(voucher).strip()[:100]
        if new!=before:t.setdefault('note_history',[]).append(dict(at=now(),before=before,after=new));t.update(new)

    def change_note(self,s,d):
        note=d.get('note');voucher=d.get('voucher');key=d.get('transaction')
        t=next((x for x in s['transactions'] if x['id']==key),None);nodes=None
        if t is not None:nodes=[p.get('node') for p in t['allocations']]
        else:
            t=next((e for e in s.get('legacy_entries',[]) if e['id']==key),None);require(t is not None,'Không tìm thấy giao dịch.');nodes=[t['category']]       # dòng lịch sử cũ: ghi chú trên chính dòng, không đổi bản dán gốc
        require(note is not None or voucher is not None,'Nhập ghi chú hoặc số chứng từ.')
        final=str(note).strip() if note is not None else t.get('note','')
        require(final or not any(self.cat_flag(s,n,'note_required') for n in nodes),'Danh mục này yêu cầu ghi chú; không được để trống.')
        self.apply_note(t,note,voucher);return 'Cập nhật ghi chú giao dịch'

    def cat_target(self,p):
        return p.get('node') or root_key(p['category'])

    def cat_target_root(self,s,key):
        """Root type of a category key (system root key or active node id); objects may attach to any category except 'unknown'."""
        if key in ROOTS:
            require(key in PARENTABLE,'Danh mục này không có đối tượng.');return key
        node=self.cat_find(s,key);require(node['status']=='ACTIVE','Danh mục đang lưu trữ.');return node['root']

    # ---- actions ------------------------------------------------------
    def change_category(self,s,action,d):
        from .p01 import now
        cat_state(s)
        def log(node,kind,before,after,reason=''):
            node['history'].append(dict(at=now(),action=kind,before=before,after=after,reason=str(reason or '').strip()[:500]))
        if action=='category-template':
            tpl=TEMPLATES.get(d.get('template'));require(tpl is not None,'Chọn danh mục mẫu.')
            require(not any(n['parent'] is None and norm_name(n['name'])==norm_name(tpl['name']) for n in s['categories']),'Danh mục mẫu này đã có.')
            self.change_category(s,'category-create',dict(name=tpl['name'],type=tpl['type'],description=tpl['description']))
            root=next(n for n in s['categories'] if n['parent'] is None and n['name']==tpl['name']);root['flags']=dict(tpl['flags'])
            for child in tpl['children']:self.change_category(s,'category-create',dict(name=child,description='',parent=root['id']))
            return 'Tạo danh mục mẫu '+tpl['name']
        if action=='category-object-add':
            key=d.get('category');self.cat_target_root(s,key);pid=d.get('profile');name=str(d.get('name') or '').strip()
            if pid:
                prof=item(s['profiles'],pid);require(prof.get('status')!='ARCHIVED' and not prof.get('merged_into'),'Đối tượng đã lưu trữ hoặc đã gộp; khôi phục ở màn Đối tượng trước.')
            else:
                require(1<=len(name)<=100,'Tên đối tượng dài 1–100 ký tự.')
                self.require_free_name(s,name)
                prof={'id':uid(),'kind':'OBJECT','name':name,'party':None};s['profiles'].append(prof)
            require(not any(e['category']==key and e['profile']==prof['id'] and e['status']=='ACTIVE' for e in s['category_objects']),'Đối tượng đã có trong danh mục này.')
            s['category_objects'].append(dict(id=uid(),category=key,profile=prof['id'],status='ACTIVE',created_at=now(),history=[dict(at=now(),action='ADD',to=key)]));return 'Thêm đối tượng '+prof['name']+' vào danh mục'
        if action=='category-object-rename':
            prof=item(s['profiles'],d.get('profile'));name=str(d.get('name') or '').strip();require(1<=len(name)<=100,'Tên đối tượng dài 1–100 ký tự.')
            self.require_free_name(s,name,exclude=prof['id'])
            prof.setdefault('rename_history',[]).append(dict(at=now(),before=prof['name'],after=name));prof['name']=name;return 'Đổi tên đối tượng thành '+name
        if action=='category-object-remove':
            e=next((x for x in s['category_objects'] if x['category']==d.get('category') and x['profile']==d.get('profile') and x['status']=='ACTIVE'),None);require(e is not None,'Đối tượng không có trong danh mục này.')
            reason=str(d.get('reason','')).strip();require(reason,'Cần lý do gỡ.');self.biz_guard_remove(s,e);e.update(status='REMOVED',removed_at=now());e['history'].append(dict(at=now(),action='REMOVE',from_=e['category'],reason=reason[:500]));return 'Gỡ đối tượng khỏi danh mục'
        if action=='category-object-move':
            src,dst=d.get('from'),d.get('to');e=next((x for x in s['category_objects'] if x['category']==src and x['profile']==d.get('profile') and x['status']=='ACTIVE'),None);require(e is not None,'Đối tượng không có trong danh mục nguồn.')
            require(src!=dst,'Chọn danh mục đích khác.');reason=str(d.get('reason','')).strip();require(reason,'Cần lý do chuyển.')
            require(self.cat_target_root(s,dst)==self.cat_target_root(s,src) if src in ROOTS or any(n['id']==src for n in s['categories']) else False,'Chỉ chuyển giữa các danh mục cùng loại gốc.')
            require(not any(x['category']==dst and x['profile']==e['profile'] and x['status']=='ACTIVE' for x in s['category_objects']),'Đối tượng đã có ở danh mục đích.')
            e['history'].append(dict(at=now(),action='MOVE',from_=src,to=dst,reason=reason[:500]));e['category']=dst
            s['object_moves'].append(dict(profile=e['profile'],**{'from':src,'to':dst},at=now(),reason=reason[:500]));return 'Chuyển đối tượng sang danh mục khác'
        if action=='category-object-merge':
            src=item(s['profiles'],d.get('from'));dst=item(s['profiles'],d.get('into'));reason=str(d.get('reason','')).strip()
            require(src['kind']=='OBJECT','Chỉ gộp được hồ sơ loại "đối tượng"; hồ sơ người/khoản vay/BĐS giữ làm hồ sơ đích.');require(src['id']!=dst['id'],'Chọn hồ sơ đích khác.')
            require(not src.get('merged_into') and not dst.get('merged_into'),'Hồ sơ đã bị gộp.');require(reason,'Cần lý do gộp.')
            self.biz_guard_merge(s,src,dst)
            for e in s['category_objects']:
                if e['profile']!=src['id'] or e['status']!='ACTIVE':continue
                if any(x['category']==e['category'] and x['profile']==dst['id'] and x['status']=='ACTIVE' for x in s['category_objects']):
                    e.update(status='REMOVED',removed_at=now());e['history'].append(dict(at=now(),action='MERGE_REMOVED',into=dst['id'],reason=reason[:500]))
                else:
                    e['profile']=dst['id'];e['history'].append(dict(at=now(),action='MERGE',from_=src['id'],reason=reason[:500]))
            for coll in ('legacy_entries','legacy_batches','object_moves'):
                for x in s.get(coll,[]):
                    if x.get('profile')==src['id']:x['profile']=dst['id']
            src['merged_into']=dst['id'];s.setdefault('profile_merges',[]).append(dict(**{'from':src['id'],'to':dst['id']},from_name=src['name'],to_name=dst['name'],at=now(),reason=reason[:500]));return f"Gộp đối tượng {src['name']} vào {dst['name']}"
        if action=='category-object-delete':
            prof=item(s['profiles'],d.get('profile'));require(prof['kind']=='OBJECT','Chỉ xóa hẳn được đối tượng tạo trong danh mục; hồ sơ người/khoản vay/BĐS chỉ gỡ khỏi danh mục.')
            reason=str(d.get('reason','')).strip();require(reason,'Cần lý do xóa.');require(prof['id'] not in self.cat_usage_blob(s),'Đối tượng đã từng được dùng để phân loại; chỉ có thể gỡ khỏi danh mục.')
            s['category_objects']=[e for e in s['category_objects'] if e['profile']!=prof['id']];s['profiles']=[x for x in s['profiles'] if x['id']!=prof['id']]
            s.setdefault('object_deleted',[]).append(dict(id=prof['id'],name=prof['name'],reason=reason[:500],at=now()));return 'Xóa hẳn đối tượng '+prof['name']
        if action=='category-cleanup':
            require(d.get('confirm') is True,'Xác nhận sau khi xem danh sách.');ids=d.get('ids');require(isinstance(ids,list) and ids,'Không có danh mục nào để dọn.')
            cands=self.cat_cleanup_candidates(s);require(set(ids)=={n['id'] for n in cands},'Danh sách đã thay đổi; xem trước lại rồi xác nhận.')
            reason=str(d.get('reason') or 'Dọn danh mục chưa dùng').strip()[:500]
            for n in cands:s.setdefault('category_deleted',[]).append(dict(id=n['id'],name=n['name'],path=self.cat_path(s,n['id']),root=n['root'],reason=reason,at=now()))
            gone={n['id'] for n in cands};s['categories']=[n for n in s['categories'] if n['id'] not in gone];return f'Dọn {len(gone)} danh mục chưa dùng'
        if action=='category-root-describe':
            key=d.get('root');require(key in ROOTS,'Chọn một danh mục gốc.')
            text=str(d.get('description','')).strip();require(len(text)<=500,'Mô tả tối đa 500 ký tự.')
            s['category_roots'][key]=text;return 'Cập nhật mô tả '+ROOTS[key]
        if action=='category-create' and not d.get('parent'):
            typ=d.get('type') or 'default'
            if typ=='default':typ='expense'                      # nhóm mặc định: nhận cả tiền vào và ra, ghi nhận báo cáo như Chi tiêu (phương án A, không đổi lịch sử)
            require(typ in ROOT_TYPES,'Chọn loại cho danh mục gốc: nhóm thu, nhóm chi hoặc nhóm đầu tư.')
            name=self.cat_name_ok(s,d.get('name'),None);desc=str(d.get('description','')).strip();require(len(desc)<=500,'Mô tả tối đa 500 ký tự.')
            node=dict(id=uid(),name=name,description=desc,parent=None,root=typ,group='default',status='ACTIVE',created_at=now(),history=[])
            log(node,'CREATE',None,dict(name=name,type=typ));s['categories'].append(node);return 'Tạo danh mục gốc '+name
        if action=='category-create':
            parent=d.get('parent');root=self.cat_parent_ok(s,parent)
            name=self.cat_name_ok(s,d.get('name'),parent);desc=str(d.get('description','')).strip();require(len(desc)<=500,'Mô tả tối đa 500 ký tự.')
            depth=2 if parent in ROOTS else self.cat_depth(s,self.cat_find(s,parent))+1
            require(depth<=MAX_DEPTH,f'Tối đa {MAX_DEPTH} cấp kể cả danh mục gốc.')
            node=dict(id=uid(),name=name,description=desc,parent=parent,root=root,group='default',status='ACTIVE',created_at=now(),history=[])
            log(node,'CREATE',None,dict(name=name,parent=parent));s['categories'].append(node);return 'Tạo danh mục '+name
        if action=='loan-regroup':return self.change_loan_group(s,d)
        node=self.cat_find(s,d.get('category'))
        if action=='category-delete':
            reason=str(d.get('reason','')).strip();require(reason,'Cần lý do xóa.')
            why=self.cat_in_use(s,node);require(why is None,why or '')
            s.setdefault('category_deleted',[]).append(dict(id=node['id'],name=node['name'],path=self.cat_path(s,node['id']),root=node['root'],reason=reason[:500],at=now()))
            s['categories']=[n for n in s['categories'] if n['id']!=node['id']];return 'Xóa hẳn danh mục '+node['name']
        if action=='category-edit':
            changed=False;reason=d.get('reason','')
            if 'parent' in d and d['parent']!=node['parent'] and not (node['parent'] is None and not d['parent']):
                require(node['parent'] is not None,'Danh mục gốc tự tạo không đổi cấp cha.')
                parent=d['parent'];root=self.cat_parent_ok(s,parent);require(root==node['root'],'Chỉ đổi cha trong cùng một danh mục gốc.')
                require(parent!=node['id'] and parent not in {n['id'] for n in self.cat_descendants(s,node)},'Không thể đặt danh mục làm con của chính nó hoặc của danh mục con của nó.')
                new_depth=2 if parent in ROOTS else self.cat_depth(s,self.cat_find(s,parent))+1
                require(new_depth+self.cat_height(s,node)-1<=MAX_DEPTH,f'Vượt {MAX_DEPTH} cấp sau khi chuyển.')
                require(not any(n['parent']==parent and n['id']!=node['id'] and norm_name(n['name'])==norm_name(node['name']) for n in s['categories']),'Đã có danh mục cùng tên ở danh mục cha mới.')
                log(node,'MOVE',node['parent'],parent,reason);node['parent']=parent;changed=True
            if 'name' in d and str(d['name']).strip()!=node['name']:
                name=self.cat_name_ok(s,d['name'],node['parent'],node['id']);log(node,'RENAME',node['name'],name,reason);node['name']=name;changed=True
            if 'description' in d and str(d['description']).strip()!=node['description']:
                desc=str(d['description']).strip();require(len(desc)<=500,'Mô tả tối đa 500 ký tự.');log(node,'DESCRIBE',node['description'],desc,reason);node['description']=desc;changed=True
            require(changed,'Không có thay đổi nào.');return 'Sửa danh mục '+node['name']
        if action=='category-archive':
            require(node['status']=='ACTIVE','Danh mục đã lưu trữ.');reason=str(d.get('reason','')).strip();require(reason,'Cần lý do lưu trữ.')
            require(not any(n['parent']==node['id'] and n['status']=='ACTIVE' for n in s['categories']),'Còn danh mục con đang hoạt động; lưu trữ các danh mục con trước.')
            require(not any(p['kind']=='LOAN' and p.get('group')==node['id'] for p in s['profiles']),'Còn khoản vay đang gắn danh mục này; chuyển các khoản vay sang danh mục khác trước.')
            self.biz_guard_archive(s,node)
            log(node,'ARCHIVE','ACTIVE','ARCHIVED',reason);node['status']='ARCHIVED';return 'Lưu trữ danh mục '+node['name']
        if action=='category-restore':
            require(node['status']=='ARCHIVED','Danh mục đang hoạt động.')
            require(node['parent'] is None or node['parent'] in ROOTS or self.cat_find(s,node['parent'])['status']=='ACTIVE','Khôi phục danh mục cha trước.')
            log(node,'RESTORE','ARCHIVED','ACTIVE',d.get('reason',''));node['status']='ACTIVE';return 'Khôi phục danh mục '+node['name']
        require(False,'Hành động không hợp lệ.')

    # ---- quick object creation (one atomic step from the classify dialog) ----
    def change_quick_object(self,s,d):
        from .product import uid as new_id
        kind=d.get('kind');profiles=s['profiles']
        def unique(label,name,of_kind):
            self.require_free_name(s,name)
        def clean(name,message):
            name=str(name or '').strip();require(1<=len(name)<=100,message);return name
        if kind=='PERSON':
            name=clean(d.get('name'),'Tên người dài 1–100 ký tự.');unique('người / tổ chức',name,'PERSON')
            profiles.append({'id':new_id(),'kind':'PERSON','name':name,'party':None});return 'Tạo nhanh người '+name
        if kind=='PROPERTY':
            name=clean(d.get('name'),'Tên BĐS dài 1–100 ký tự.');unique('BĐS',name,'PROPERTY')
            profiles.append({'id':new_id(),'kind':'PROPERTY','name':name,'party':None});return 'Tạo nhanh BĐS '+name
        if kind=='LOAN':
            if d.get('party'):
                person=next((p for p in profiles if p['id']==d['party']),None);require(person is not None and person['kind']=='PERSON','Chọn người có sẵn hoặc nhập tên người mới.')
                created=None
            else:
                pname=clean(d.get('party_name'),'Tên người dài 1–100 ký tự.');unique('người / tổ chức',pname,'PERSON')
                person={'id':new_id(),'kind':'PERSON','name':pname,'party':None};created=person
            raw=str(d.get('name') or '').strip();base=raw or 'Khoản '+person['name']
            require(len(base)<=100,'Tên khoản vay tối đa 100 ký tự.')
            name=base
            if not raw:
                n=2
                while self.profile_clash(s,name):name=f'{base} ({n})';n+=1;require(len(name)<=100,'Tên khoản vay tối đa 100 ký tự.')
            else:unique('khoản vay',name,'LOAN')
            if created:profiles.append(created)
            profiles.append({'id':new_id(),'kind':'LOAN','name':name,'party':person['id']})
            return 'Tạo nhanh khoản vay '+name+(' và người '+person['name'] if created else '')
        if kind=='CATEGORY':
            return self.change_category(s,'category-create',dict(parent=d.get('parent'),name=d.get('name'),description=''))
        require(False,'Loại đối tượng không hợp lệ.')

    def cat_cleanup_candidates(self,s):
        """Child categories never used anywhere, found leaf-first so empty parents follow their children (spec 034)."""
        cat_state(s);blob=self.cat_usage_blob(s);work=list(s['categories']);removed=[]
        def blocked(n):
            nid=n['id']
            return (any(e['status']=='ACTIVE' and e['category']==nid for e in s['category_objects']) or any(b.get('category')==nid for b in s.get('legacy_batches',[]))
                or any(nid in (m['from'],m['to']) for m in s.get('object_moves',[])))
        changed=True
        while changed:
            changed=False;view=dict(s,categories=work)
            for n in list(work):
                if n['parent'] is None or blocked(n) or self.cat_in_use_fast(view,n,blob) is not None:continue
                work.remove(n);removed.append(n);changed=True;break
        return removed

    def cat_descendants(self,s,node):
        out=[];stack=[node['id']]
        while stack:
            cid=stack.pop()
            for n in s['categories']:
                if n['parent']==cid:out.append(n);stack.append(n['id'])
        return out

    def legacy_summary(self,s):
        """Batches migrated from spreadsheets with totals of the rows that count (not hidden by a bank-statement match)."""
        profiles={p['id']:p['name'] for p in s['profiles']};refs=self.legacy_bank_refs(s);out=[]
        for b in s.get('legacy_batches',[]):
            es=[e for e in s.get('legacy_entries',[]) if e['batch']==b['id']];counted=[e for e in es if not (norm_ref_c(e['reference']) and norm_ref_c(e['reference']) in refs)]
            tin=sum(int(e['amount']) for e in counted if e['direction']=='IN');tout=sum(int(e['amount']) for e in counted if e['direction']=='OUT')
            out.append(dict(id=b['id'],at=b['at'],category=b['category'],category_path=self.cat_path(s,b['category']) if b['category'] not in ROOTS else ROOTS[b['category']],profile=b['profile'],profile_name=profiles.get(b['profile'],''),rows=len(es),active=len(counted) if b['status']=='ACTIVE' else 0,matched_bank=len(es)-len(counted),
                totals={'in':str(tin),'out':str(tout)},declared=b.get('declared'),status=b['status'],void_reason=b.get('void_reason'),source_text=b['source_text']))
        return sorted(out,key=lambda x:x['at'],reverse=True)

    def cat_in_use(self,s,node):
        """Why the category cannot be deleted for good, or None when it was never used anywhere."""
        return self.cat_in_use_fast(s,node,self.cat_usage_blob(s))

    def cat_in_use_fast(self,s,node,blob):
        nid=node['id']
        if any(n['parent']==nid for n in s['categories']):return 'Còn danh mục con; xóa hoặc chuyển các danh mục con trước.'
        if any(p['kind']=='LOAN' and (p.get('group')==nid or any(nid in (h.get('from'),h.get('to')) for h in p.get('group_history',[]))) for p in s['profiles']):return 'Đã có khoản vay gắn danh mục này; chỉ có thể lưu trữ.'
        if nid in blob:return 'Danh mục đã từng được dùng để phân loại; chỉ có thể lưu trữ.'
        return None

    def cat_usage_blob(self,s):
        return json.dumps([[t['allocations'],t.get('classification_history') or []] for t in s['transactions']],ensure_ascii=False)+json.dumps([[t['allocations'] for t in sn['report']['transactions']] for sn in s['snapshots']],ensure_ascii=False)

    def change_loan_group(self,s,d):
        from .p01 import day,now
        loan=next((p for p in s['profiles'] if p['id']==d.get('profile')),None);require(loan is not None and loan['kind']=='LOAN','Chọn một khoản vay.')
        target=d.get('node') or None
        if target=='principal':target=None
        if target is not None:
            node=self.cat_find(s,target);require(node['root']=='principal' and node['status']=='ACTIVE','Chỉ chuyển sang danh mục Gốc vay đang hoạt động.')
        require((loan.get('group') or None)!=target,'Khoản vay đã ở danh mục này.')
        when=day(d.get('effective_date'));reason=str(d.get('reason','')).strip();require(reason,'Cần lý do chuyển danh mục.')
        loan.setdefault('group_history',[]).append(dict(at=now(),effective_date=when,**{'from':loan.get('group') or None,'to':target},reason=reason[:500]));loan['group']=target
        return 'Chuyển khoản vay '+loan['name']+' sang '+(self.cat_path(s,target) if target else ROOTS['principal'])

    def cat_eff(self,s,p):
        """The part as the category screens see it: loan group (spec 016/019) and object moves (spec 026) re-home it."""
        for m in s.get('profile_merges',[]):
            if p.get('profile')==m['from']:p=dict(p,profile=m['to'],own_profile=p['profile'])
        if p.get('category') in {'principal','interest'} and p.get('profile'):
            loan=next((x for x in s['profiles'] if x['id']==p['profile']),None)
            if loan and loan['kind']=='LOAN' and loan.get('group'):p=dict(p,category='principal',node=loan['group'],own_node=p.get('node'),own_category=p['category'])
        if p.get('profile'):
            for mv in s.get('object_moves',[]):
                if mv['profile']==p['profile'] and self.cat_target(p)==mv['from']:p=dict(p,node=None if mv['to'] in ROOTS else mv['to'],own_node=p.get('own_node',p.get('node')))
        return p

    def loan_options(self,s):
        with localcontext() as ctx:
            ctx.prec=60
            people={p['id']:p['name'] for p in s['profiles']};by={p['id']:p for p in s['profiles']};rows=[]
            for l in self.debt_register(s)['loans']:
                setup=l['setup'];first=min((e['date'] for e in l['entries']),default=None);gross=None
                if setup:
                    gross=D(setup['opening']);receivable=setup['direction']=='RECEIVABLE'
                    for e in l['entries']:
                        if e['pre_opening']:continue
                        for part in e['parts']:
                            if part['category']=='principal' and (D(e['signed_amount'])<0)==receivable:gross+=D(part['amount'])
                prof=by[l['id']];group=prof.get('group')
                rows.append(dict(id=l['id'],party=l['party'],party_name=people.get(l['party'],''),name=l['name'],date=setup['effective_date'] if setup else first,gross=S(gross) if gross is not None else None,
                    current=l['current_principal'],direction=setup['direction'] if setup else None,setup=bool(setup),group=group,group_path=self.cat_path(s,group) if group else ROOTS['principal'],history=prof.get('group_history',[])))
        return rows

    # ---- totals & history --------------------------------------------
    def cat_period(self,d):
        from .p01 import day
        start=d.get('start') or None;end=d.get('end') or None
        if start:day(start)
        if end:day(end)
        require(not(start and end) or start<=end,'Ngày kết thúc không được trước ngày bắt đầu.')
        return start,end

    def cat_parts(self,s,start=None,end=None,account=None):
        """Yield (transaction, part) for every classified part; unclassified money goes to the 'unknown' root."""
        for t in s['transactions']:
            if (start and t['date']<start) or (end and t['date']>end) or (account and t['account']!=account):continue
            parts=t['allocations'] or [{'category':'unknown','amount':S(abs(D(t['signed_amount']))),'profile':None}]
            for p in parts:yield t,self.cat_eff(s,p)
        if account is None:
            for t,p in self.legacy_items(s):
                if (start and t['date']<start) or (end and t['date']>end):continue
                yield t,self.cat_eff(s,p)

    def cat_keys(self,s,p):
        key=root_key(p['category']);node=p.get('node')
        if not node:return [key]
        chain=self.cat_chain(s,node)
        return chain if self.cat_find(s,chain[-1])['parent'] is None else [key]+chain      # user-created root: own totals, not the system root's

    def cat_top(self,s,p):
        keys=self.cat_keys(s,p);return keys[-1] if p.get('node') and keys[0]!=root_key(p['category']) else keys[0]

    def category_view(self,s,start=None,end=None):
        with localcontext() as ctx:
            ctx.prec=60
            s=cat_state(copy.deepcopy(s));acc={};oacc={}
            for t,p in self.cat_parts(s,start,end):
                incoming=D(t['signed_amount'])>0;amount=D(p['amount'])
                if p.get('profile'):
                    o=oacc.setdefault((self.cat_target(p),p['profile']),dict(in_=Decimal(0),out=Decimal(0),tx=set()));o['in_' if incoming else 'out']+=amount;o['tx'].add(t['id'])
                for key in self.cat_keys(s,p):
                    a=acc.setdefault(key,dict(in_=Decimal(0),out=Decimal(0),parts=0,tx=set()))
                    a['in_' if incoming else 'out']+=amount;a['parts']+=1;a['tx'].add(t['id'])
            def totals(key,spend=False):
                a=acc.get(key);a=a or dict(in_=Decimal(0),out=Decimal(0),parts=0,tx=set())
                out=dict(**{'in':S(a['in_']),'out':S(a['out']),'net':S(a['in_']-a['out']),'parts':a['parts'],'transactions':len(a['tx'])})
                if spend:out['net_spend']=S(a['out']-a['in_'])
                return out
            blob=self.cat_usage_blob(s);attached={};by_profile={x['id']:x for x in s['profiles']};objs={}
            for e in s['category_objects']:
                if e['status']!='ACTIVE' or e['profile'] not in by_profile:continue
                pr=by_profile[e['profile']]
                if pr.get('merged_into'):continue
                dup=[dict(profile=x['id'],name=x['name'],kind=x['kind']) for x in s['profiles'] if x['id']!=pr['id'] and not x.get('merged_into') and norm_name(x['name'])==norm_name(pr['name'])];o=oacc.get((e['category'],e['profile']),dict(in_=Decimal(0),out=Decimal(0),tx=set()))
                objs.setdefault(e['category'],[]).append(dict(business=e.get('business'),entry=e['id'],profile=pr['id'],name=pr['name'],kind=pr['kind'],totals={'in':S(o['in_']),'out':S(o['out']),'transactions':len(o['tx'])},deletable=pr['kind']=='OBJECT' and pr['id'] not in blob,history=e['history'],duplicate_of=dup))
            for pr in s['profiles']:
                if pr['kind']=='LOAN' and pr.get('group'):attached[pr['group']]=attached.get(pr['group'],0)+1
            roots=[dict(key=k,name=v,description=s['category_roots'].get(k,''),role=ROLE_LABELS[k],group='default',group_name=GROUPS['default'],objects=objs.get(k,[]),parentable=k in PARENTABLE,totals=totals(k,k=='expense')) for k,v in ROOTS.items()]
            nodes=[dict(group=n.get('group','default'),group_name=GROUPS[n.get('group','default')],role=ROLE_LABELS[n['root']],capitalize=self.cat_flag(s,n['id'],'capitalize'),note_required=self.cat_flag(s,n['id'],'note_required'),objects=objs.get(n['id'],[]),deletable=self.cat_in_use_fast(s,n,blob) is None,loans=attached.get(n['id'],0),id=n['id'],name=n['name'],description=n['description'],parent=n['parent'],root=n['root'],status=n['status'],depth=self.cat_depth(s,n),path=self.cat_path(s,n['id']),history=n['history'],totals=totals(n['id'],n['root']=='expense')) for n in s['categories']]
            return dict(roots=roots,nodes=nodes,templates={k:dict(name=v['name'],children=v['children'],description=v['description'],exists=any(n['parent'] is None and norm_name(n['name'])==norm_name(v['name']) for n in s['categories'])) for k,v in TEMPLATES.items()},deleted=s.get('category_deleted',[]),merges=s.get('profile_merges',[]),cleanup=[dict(id=n['id'],path=self.cat_path(s,n['id']),root=n['root'],status=n['status']) for n in self.cat_cleanup_candidates(s)],legacy=self.legacy_summary(s),groups=GROUPS,group_note=GROUP_NOTE,max_depth=MAX_DEPTH,root_types=ROOT_TYPES,period=dict(start=start,end=end) if (start or end) else None,draft=True)

    def category_history(self,d,s=None):
        from .p01 import display_day
        with localcontext() as ctx:
            ctx.prec=60
            s=cat_state(copy.deepcopy(s or self.state()));key=d.get('category');start,end=self.cat_period(d);account=d.get('account') or None
            everything=key=='*' and bool(d.get('object'))
            require(everything or key in ROOTS or any(n['id']==key for n in s['categories']),'Chọn danh mục.')
            approved={t['id'] for snap in s['snapshots'] for t in snap['report']['transactions']}
            accounts={a['id']:a['name'] for a in s['accounts']};profiles={p['id']:p['name'] for p in s['profiles']}
            rows=[];tx=set();inc=out=Decimal(0);family=set()
            if d.get('object'):
                owner=next((x for x in s['profiles'] if x['id']==d['object']),None);family={d['object']}|({x['id'] for x in self.obj_party_loans(s,owner)} if everything and owner and owner['kind']=='PERSON' else set())
            for t,p in self.cat_parts(s,start,end,account):
                if not everything and key not in self.cat_keys(s,p):continue
                if d.get('object') and p.get('profile') not in family:continue
                incoming=D(t['signed_amount'])>0;amount=D(p['amount']);tx.add(t['id'])
                if incoming:inc+=amount
                else:out+=amount
                node=p.get('node');row_path=self.cat_path(s,node) if node else ROOTS[root_key(p['category'])]
                rows.append(dict(transaction=t['id'],date=t['date'],account=accounts.get(t['account'],''),reference=t['reference'],description=t['description'],amount=S(amount),direction='IN' if incoming else 'OUT',
                    label=('Hoàn chi tiêu' if (p['category']=='expense' and incoming) else ('Lãi vay' if p.get('own_category')=='interest' else row_path))+(' · '+profiles[p['profile']] if p.get('profile') in profiles else ''),source_count=len(t.get('sources',[])),split=len(t['allocations'])>1,tx_amount=S(abs(D(t['signed_amount']))),
                    note=t.get('note',''),voucher=t.get('voucher',''),legacy=bool(t.get('legacy')),source_row=t.get('source_row'),bank_balance=t.get('bank_balance'),category_path=row_path,object=profiles.get(p.get('profile')),status='LEGACY' if t.get('legacy') else ('APPROVED' if t['id'] in approved else 'DRAFT'),node_status=next((n['status'] for n in s['categories'] if n['id']==node),None) if node else None,sources=copy.deepcopy(t.get('sources',[]))))
            rows.sort(key=lambda r:(r['date'],r['reference']),reverse=True)
            periods=[(b['period_start'],b['period_end']) for b in s['imports'] if b['status']=='PUBLISHED']
            evidence='HAS_DATA' if rows else ('EMPTY' if periods else 'EMPTY_NO_SOURCE')
            notice=('Kỳ nguồn đã ghi: '+'; '.join(display_day(a)+' → '+display_day(b) for a,b in sorted(set(periods)))+'. Ngoài các kỳ này chưa có bằng chứng.') if periods else 'Chưa có nguồn ngân hàng nào được ghi; không suy ra là không phát sinh.'
            root='all' if everything else (key if key in ROOTS else next(n['root'] for n in s['categories'] if n['id']==key))
            totals={'in':S(inc),'out':S(out),'net':S(inc-out),'parts':len(rows),'transactions':len(tx)}
            if root=='expense':totals['net_spend']=S(out-inc)
            return dict(category=key,root=root,path='Tất cả danh mục' if everything else self.cat_path(s,key),evidence=evidence,source_notice=notice,totals=totals,rows=rows,period=dict(start=start,end=end) if (start or end) else None)

    def category_review(self,d,s=None):
        """Approval-step breakdown by category for one account, with a reconciliation against the source rows."""
        with localcontext() as ctx:
            ctx.prec=60
            s=cat_state(copy.deepcopy(s or self.state()));account=d.get('account')
            require(any(a['id']==account for a in s['accounts']),'Chọn tài khoản.')
            txs=[t for t in s['transactions'] if t['account']==account];acc={};top={}
            def bucket(table,key):return table.setdefault(key,dict(in_=Decimal(0),out=Decimal(0),tx=set(),objs=set()))
            src_in=src_out=Decimal(0)
            for t in txs:
                incoming=D(t['signed_amount'])>0
                if incoming:src_in+=abs(D(t['signed_amount']))
                else:src_out+=abs(D(t['signed_amount']))
            for t,p in self.cat_parts(s,account=account):
                incoming=D(t['signed_amount'])>0;amount=D(p['amount'])
                for key in self.cat_keys(s,p)+['@'+self.cat_top(s,p)]:
                    b=bucket(top if key.startswith('@') else acc,key[1:] if key.startswith('@') else key)
                    b['in_' if incoming else 'out']+=amount;b['tx'].add(t['id'])
                    if p.get('profile'):b['objs'].add(p['profile'])
            def stats(key,typ):
                b=acc.get(key) or dict(in_=Decimal(0),out=Decimal(0),tx=set(),objs=set())
                row=dict(transactions=len(b['tx']),objects=len(b['objs']),**{'in':S(b['in_']),'out':S(b['out'])})
                if typ=='expense':row['net_spend']=S(b['out']-b['in_'])
                return row
            def children(parent):
                out=[]
                for n in s['categories']:
                    if n['parent']!=parent:continue
                    row=dict(key=n['id'],name=n['name'],type=n['root'],system=False,status=n['status'],**stats(n['id'],n['root']));row['children']=children(n['id'])
                    if row['transactions'] or row['children'] or n['status']=='ACTIVE':out.append(row)
                return out
            groups=[]
            for k,v in ROOTS.items():
                row=dict(key=k,name=v,type=k,system=True,status='ACTIVE',**stats(k,k));row['children']=children(k);groups.append(row)
            for n in s['categories']:
                if n['parent'] is None:
                    row=dict(key=n['id'],name=n['name'],type=n['root'],system=False,status=n['status'],**stats(n['id'],n['root']));row['children']=children(n['id'])
                    if row['transactions'] or row['children'] or n['status']=='ACTIVE':groups.append(row)
            grouped_tx=set().union(*[b['tx'] for b in top.values()]) if top else set()
            g_in=sum((b['in_'] for b in top.values()),Decimal(0));g_out=sum((b['out'] for b in top.values()),Decimal(0))
            def check(source,grouped):return dict(source=S(source) if isinstance(source,Decimal) else source,grouped=S(grouped) if isinstance(grouped,Decimal) else grouped,ok=source==grouped,difference=S(grouped-source) if isinstance(source,Decimal) else grouped-source)
            checks=dict(transactions=check(len(txs),len(grouped_tx)),money_in=check(src_in,g_in),money_out=check(src_out,g_out))
            return dict(account=account,groups=groups,checks=checks,reconciled=all(c['ok'] for c in checks.values()),empty=not txs,draft=True)

    def classification_review(self,d,s=None):
        """Read-only statement-style listing of every transaction grouped by category / category · object."""
        from .p01 import now
        with localcontext() as ctx:
            ctx.prec=60
            s=cat_state(copy.deepcopy(s or self.state()));account=d.get('account')
            require(any(a['id']==account for a in s['accounts']),'Chọn tài khoản.')
            mode=d.get('scope') or 'all';require(mode in {'all','recent','range'},'Phạm vi không hợp lệ.')
            start=end=None
            if mode=='range':
                start,end=self.cat_period(d);require(start or end,'Chọn ngày bắt đầu hoặc kết thúc.')
            moment=now();cutoff=(datetime.fromisoformat(moment)-timedelta(hours=24)).isoformat()
            approved={t['id'] for snap in s['snapshots'] for t in snap['report']['transactions']};profiles={p['id']:p['name'] for p in s['profiles']}
            def when(t):
                h=t.get('classification_history') or []
                return h[-1]['at'] if h and t['allocations'] else None
            txs=[]
            for t in s['transactions']:
                if t['account']!=account:continue
                at=when(t)
                if mode=='recent' and not(at and at>=cutoff):continue
                if mode=='range' and ((start and t['date']<start) or (end and t['date']>end)):continue
                txs.append(t)
            groups={};src_in=src_out=g_in=g_out=Decimal(0);seen=set();classified=0
            for t in txs:
                signed=D(t['signed_amount']);incoming=signed>0;at=when(t)
                if incoming:src_in+=abs(signed)
                else:src_out+=abs(signed)
                parts=t['allocations'] or [{'category':'unknown','amount':S(abs(signed)),'profile':None}]
                if t['allocations'] and not any(p['category']=='unknown' for p in t['allocations']):classified+=1
                for p in parts:
                    unknown=p['category']=='unknown';own=p.get('node');eff=self.cat_eff(s,p);node=eff.get('node')
                    own_path=self.cat_path(s,own) if own else ROOTS[root_key(p['category'])]
                    obj=profiles.get(p.get('profile')) if p.get('profile') else None
                    if unknown:base='Chưa phân loại'
                    elif obj and eff is p:
                        top=self.cat_top(s,p);base=ROOTS[top] if top in ROOTS else self.cat_find(s,top)['name']
                    else:base=self.cat_path(s,node) if node else ROOTS[root_key(p['category'])]
                    name=base if unknown or not obj else f'{base} · {obj}'
                    typ=root_key(p['category']) if not node else self.cat_find(s,node)['root']
                    amount=D(p['amount']);g=groups.setdefault(name,dict(key=name,name=name,type=typ,unclassified=unknown,tx=set(),in_=Decimal(0),out=Decimal(0),latest=None,rows=[]))
                    g['in_' if incoming else 'out']+=amount;g['tx'].add(t['id']);seen.add(t['id'])
                    if incoming:g_in+=amount
                    else:g_out+=amount
                    if at and (g['latest'] is None or at>g['latest']):g['latest']=at
                    label='Hoàn chi tiêu' if (p['category']=='expense' and incoming) else own_path
                    g['rows'].append(dict(transaction=t['id'],date=t['date'],reference=t['reference'],description=t['description'],amount=S(amount),tx_amount=S(abs(signed)),direction='IN' if incoming else 'OUT',
                        label=label,object=obj,note=t.get('note',''),voucher=t.get('voucher',''),split=len(parts)>1,classified_at=at,recent=bool(at and at>=cutoff),status='APPROVED' if t['id'] in approved else 'DRAFT',sources=len(t.get('sources',[])),_order=t.get('order',0)))
            out=[]
            for g in groups.values():
                g['rows'].sort(key=lambda r:(r['classified_at'] or '',r['date'],r['_order']),reverse=True)
                for r in g['rows']:r.pop('_order')
                row=dict(key=g['key'],name=g['name'],type=g['type'],unclassified=g['unclassified'],transactions=len(g['tx']),latest=g['latest'],rows=g['rows'],**{'in':S(g['in_']),'out':S(g['out'])})
                if g['type']=='expense':row['net_spend']=S(g['out']-g['in_'])
                out.append(row)
            out.sort(key=lambda g:(g['unclassified'],_neg(g['latest']),g['name']))
            def check(source,grouped):return dict(source=source if isinstance(source,int) else S(source),grouped=grouped if isinstance(grouped,int) else S(grouped),ok=source==grouped,difference=(grouped-source) if isinstance(source,int) else S(grouped-source))
            checks=dict(transactions=check(len(txs),len(seen)),money_in=check(src_in,g_in),money_out=check(src_out,g_out))
            return dict(account=account,scope=dict(mode=mode,start=start,end=end,cutoff=cutoff if mode=='recent' else None),now=moment,
                summary=dict(transactions=len(txs),classified=classified,unclassified=len(txs)-classified,**{'in':S(src_in),'out':S(src_out),'net':S(src_in-src_out)}),
                checks=checks,reconciled=all(c['ok'] for c in checks.values()),groups=out,empty=not txs,draft=True)

def _neg(value):
    """Sort key making later ISO timestamps come first; groups without a timestamp go last."""
    return tuple(-ord(c) for c in value) if value else (1,)
