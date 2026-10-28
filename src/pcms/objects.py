"""Object management (spec 033): standalone list of objects with create / edit / archive / restore / delete.

An object has a unique name and a type (Người, Bất động sản, Khác). A loan record belongs to a person and is shown inside it.
Nothing here creates or edits money; archived objects only disappear from pickers and keep their history.
"""
import copy
import json
from decimal import Decimal, localcontext
from .core import require
from .product import D, S, uid, item
from .business import active_pair

TYPES={'PERSON':'Người','PROPERTY':'Bất động sản','OBJECT':'Khác','LOAN':'Khoản vay'}
EDITABLE_TYPES={'PERSON','PROPERTY','OBJECT'}

class Objects:
    def obj_party_loans(self,s,prof):
        return [x for x in s['profiles'] if x['kind']=='LOAN' and x.get('party')==prof['id'] and not x.get('merged_into')]

    def obj_family(self,s,prof):
        """The object plus, for a person, the loan records that belong to it."""
        return [prof['id']]+([x['id'] for x in self.obj_party_loans(s,prof)] if prof['kind']=='PERSON' else [])

    def obj_type_reason(self,s,prof):
        """Why the type cannot change, or None."""
        if prof['kind']=='LOAN':return 'Khoản vay thuộc về một người và quản lý ở Công nợ; không đổi loại.'
        if self.obj_party_loans(s,prof):return 'Người này đang là bên của khoản vay; xử lý các khoản vay trước.'
        if any(e['status']=='ACTIVE' and e['profile']==prof['id'] and e.get('business') for e in s.get('category_objects',[])):return 'Đối tượng đang mang nghiệp vụ; gỡ nghiệp vụ (nếu chưa có giao dịch) trước.'
        if prof['kind']=='PROPERTY':
            blob=json.dumps(s.get('realty',{}),ensure_ascii=False)
            if prof['id'] in blob or any(a.get('profile')==prof['id'] and a['category']=='investment' for t in s['transactions'] for a in t['allocations']):return 'Bất động sản đã có hợp đồng, thanh toán hoặc phân loại đầu tư; không đổi loại.'
        return None

    def obj_delete_trace(self,s,prof):
        """Dấu vết quan hệ đối tượng–danh mục giữ lại khi xóa hẳn đối tượng (spec 045, sửa R201): danh mục từng có thành viên vẫn là "đã dùng"."""
        return [dict(category=e['category'],status=e['status'],history=copy.deepcopy(e.get('history',[]))) for e in s.get('category_objects',[]) if e['profile']==prof['id']]

    def obj_in_use(self,s,prof):
        """Why the object cannot be deleted for good (it is referenced somewhere), or None."""
        if prof['kind']=='LOAN':return 'Khoản vay quản lý ở Công nợ.'
        if self.obj_party_loans(s,prof):return 'Người này đang là bên của khoản vay.'
        if any(l['person']==prof['id'] for l in s.get('loans',[])):return 'Người này có khoản vay (nghiệp vụ Cho vay/Đi vay); chỉ có thể lưu trữ.'
        rest={k:v for k,v in s.items() if k not in {'profiles','category_objects','snapshots','object_deleted'}}
        rest['snapshots']=[dict(report=sn['report'],imports=sn.get('imports')) for sn in s['snapshots']]
        rest['profiles']=[{k:v for k,v in x.items() if k not in {'rename_history','archive_history','type_history'}} for x in s['profiles'] if x['id']!=prof['id']]
        rest['category_objects']=[{k:v for k,v in e.items() if k not in {'history','business_history'}} for e in s['category_objects'] if e['profile']!=prof['id']]
        if prof['id'] in json.dumps(rest,ensure_ascii=False):return 'Đối tượng đã được dùng (phân loại, lịch sử, nghiệp vụ hoặc dữ liệu liên quan); chỉ có thể lưu trữ.'
        if any(e['profile']==prof['id'] and e.get('business') for e in s['category_objects']):return 'Đối tượng đang mang nghiệp vụ; gỡ nghiệp vụ trước.'
        return None

    def obj_archive_reason(self,s,prof):
        if prof.get('status')=='ARCHIVED':return 'Đã lưu trữ.'
        if prof['kind']=='LOAN':return 'Khoản vay quản lý ở Công nợ.'
        for loan in self.debt_register(s)['loans']:
            if loan['party']==prof['id'] and loan['current_principal'] is not None and D(loan['current_principal'])!=0:return 'Còn khoản vay có dư nợ gốc; hoàn tất khoản vay trước.'
        for row in (self.loan_book(s)['loans'] if s.get('loans') else []):
            if row['person']==prof['id'] and (D(row['principal'])!=0 or D(row['interest_outstanding'])!=0):return f"Còn khoản {row['code']} chưa hết gốc/lãi; hoàn tất khoản vay trước."
        for row in self.business_view(s).get('loans',[]):
            if row['profile']==prof['id'] and D(row['balance'])!=0:return 'Còn dư nợ gốc theo nghiệp vụ; hoàn tất trước khi lưu trữ.'
        return None

    def create_profile(self,s,name,kind,category=None):
        """The single way to create an object: unique name over the whole system (archived included) and a type (spec 041)."""
        from .p01 import now
        require(kind in EDITABLE_TYPES,'Chọn loại đối tượng: Người, Bất động sản hoặc Khác.')
        name=str(name or '').strip();require(1<=len(name)<=100,'Tên đối tượng dài 1–100 ký tự.');self.require_free_name(s,name)
        prof={'id':uid(),'kind':kind,'name':name,'party':None};s['profiles'].append(prof)
        if category:
            self.cat_target_root(s,category)
            s['category_objects'].append(dict(id=uid(),category=category,profile=prof['id'],status='ACTIVE',created_at=now(),history=[dict(at=now(),action='ADD',to=category)]))
        return prof

    def disp_name(self,s,pid):
        """Name shown to the user: a loan record is shown as the person who owns it."""
        p=next((x for x in s['profiles'] if x['id']==pid),None)
        if p is None:return ''
        if p['kind']=='LOAN' and p.get('party'):
            owner=next((x for x in s['profiles'] if x['id']==p['party']),None)
            return owner['name'] if owner else p['name']
        return p['name']

    def change_object(self,s,action,d):
        from .p01 import now
        if action=='object-create':
            prof=self.create_profile(s,d.get('name'),d.get('type'),d.get('category') or None)
            return f"Tạo đối tượng {prof['name']} ({TYPES[prof['kind']]})"
        prof=item(s['profiles'],d.get('profile'));require(not prof.get('merged_into'),'Hồ sơ đã bị gộp.')
        reason=str(d.get('reason') or '').strip()[:500]
        if action=='object-edit':
            changed=[]
            if 'name' in d and str(d['name']).strip()!=prof['name']:
                name=str(d['name']).strip();require(1<=len(name)<=100,'Tên đối tượng dài 1–100 ký tự.');require(prof['kind']!='LOAN','Tên khoản vay đổi ở Công nợ.');self.require_free_name(s,name,exclude=prof['id'])
                prof.setdefault('rename_history',[]).append(dict(at=now(),before=prof['name'],after=name,reason=reason));prof['name']=name;changed.append('tên')
            if 'type' in d and d['type']!=prof['kind']:
                require(d['type'] in EDITABLE_TYPES,'Loại đối tượng không hợp lệ.');why=self.obj_type_reason(s,prof);require(why is None,why or '');require(reason,'Cần lý do đổi loại.')
                prof.setdefault('type_history',[]).append(dict(at=now(),before=prof['kind'],after=d['type'],reason=reason));prof['kind']=d['type'];changed.append('loại')
            require(changed,'Không có thay đổi nào.');return f"Sửa {' và '.join(changed)} của đối tượng {prof['name']}"
        if action=='object-archive':
            require(reason,'Cần lý do lưu trữ.');why=self.obj_archive_reason(s,prof);require(why is None,why or '')
            prof['status']='ARCHIVED';prof.setdefault('archive_history',[]).append(dict(at=now(),action='ARCHIVE',reason=reason));return f"Lưu trữ đối tượng {prof['name']}"
        if action=='object-restore':
            require(prof.get('status')=='ARCHIVED','Đối tượng đang hoạt động.');prof['status']='ACTIVE';prof.setdefault('archive_history',[]).append(dict(at=now(),action='RESTORE',reason=reason));return f"Khôi phục đối tượng {prof['name']}"
        if action=='object-delete':
            require(reason,'Cần lý do xóa.');why=self.obj_in_use(s,prof);require(why is None,why or '')
            trace=self.obj_delete_trace(s,prof)
            s['category_objects']=[e for e in s['category_objects'] if e['profile']!=prof['id']];s['profiles']=[x for x in s['profiles'] if x['id']!=prof['id']]
            s.setdefault('object_deleted',[]).append(dict(id=prof['id'],name=prof['name'],kind=prof['kind'],reason=reason,at=now(),memberships=trace));return f"Xóa hẳn đối tượng {prof['name']}"
        require(False,'Hành động không hợp lệ.')

    def object_view(self,s):
        with localcontext() as ctx:
            ctx.prec=60
            s=copy.deepcopy(s);s.setdefault('category_objects',[]);by={p['id']:p for p in s['profiles']}
            acc={}
            for t,p in self.cat_parts(s):
                if not p.get('profile'):continue
                a=acc.setdefault(p['profile'],dict(in_=Decimal(0),out=Decimal(0),tx=set()));a['in_' if D(t['signed_amount'])>0 else 'out']+=D(p['amount']);a['tx'].add(t['id'])
            loans={l['id']:l for l in self.debt_register(s)['loans']};rows=[]
            book=self.loan_book(s) if s.get('loans') else None;biz=self.lb_biz_map(s)        # spec 046: khoản vay theo hai chiều, cùng sổ với Công nợ
            for p in s['profiles']:
                if p['kind']=='LOAN' or p.get('merged_into'):continue
                fam=self.obj_family(s,p);tin=sum((acc.get(i,{}).get('in_',Decimal(0)) for i in fam),Decimal(0));tout=sum((acc.get(i,{}).get('out',Decimal(0)) for i in fam),Decimal(0));tx=set().union(*[acc.get(i,{}).get('tx',set()) for i in fam])
                cats=[dict(category=e['category'],path=self.cat_path(s,e['category']) if e['category'] not in self.ROLES_ else self.ROLES_[e['category']],business=((e.get('business') or {}).get('type') if self.business_enabled else None)) for e in s['category_objects'] if e['status']=='ACTIVE' and e['profile']==p['id']]
                have={c['category'] for c in cats}
                for l in self.obj_party_loans(s,p):
                    home=self.loan_home(l)
                    if home not in have:have.add(home);cats.append(dict(category=home,path=self.cat_path(s,home) if home not in self.ROLES_ else self.ROLES_[home],business=None,via_loan=True))
                mine=[] if not self.business_enabled else [dict(id=x['id'],name=x['name'],direction=(x.get('debt_setup') or {}).get('direction'),current=loans[x['id']]['current_principal'],status=loans[x['id']]['completion_status'],setup=bool(x.get('debt_setup')),
                    category=(self.cat_path(s,x['group']) if x.get('group') else self.ROLES_['principal'])) for x in self.obj_party_loans(s,p)]
                for c in cats:c['loan_business']=(biz.get(c['category']) or (None,))[0]
                biz_loans=[dict(id=r['id'],code=r['code'],name=r['name'],direction=r['direction'],direction_name=r['direction_name'],principal=r['principal'],interest_outstanding=r['interest_outstanding'],status=r['status'],category_path=r['category_path']) for r in (book or {}).get('loans',[]) if r['person']==p['id']]
                rows.append(dict(id=p['id'],name=p['name'],kind=p['kind'],type_name=TYPES[p['kind']],status=p.get('status','ACTIVE'),categories=cats,loans=mine,biz_loans=biz_loans,totals={'in':S(tin),'out':S(tout),'transactions':len(tx)},
                    type_reason=self.obj_type_reason(s,p),delete_reason=self.obj_in_use(s,p),renames=len(p.get('rename_history',[])),archive_history=p.get('archive_history',[]),type_history=p.get('type_history',[])))
            issues=[]
            for e in s['category_objects']:
                if e['status']!='ACTIVE' or e['profile'] not in by:continue
                p=by[e['profile']]
                if p['kind']=='LOAN' and not p.get('merged_into'):issues.append(dict(code='LOAN_AS_MEMBER',profile=p['id'],name=p['name'],party=(by.get(p.get('party')) or {}).get('name'),message='Khoản vay đang là thành viên danh mục; người sở hữu mới là đối tượng của danh mục. Dùng "Hợp nhất hồ sơ nghiệp vụ".'))
            for p in s['profiles']:
                if p['kind']!='PERSON' or p.get('merged_into'):continue
                homes={self.loan_home(l) for l in self.obj_party_loans(s,p)}
                if homes and not any(e['status']=='ACTIVE' and e['profile']==p['id'] and e['category'] in homes for e in s['category_objects']):issues.append(dict(code='PERSON_NOT_MEMBER',profile=p['id'],name=p['name'],message='Người có khoản vay nhưng chưa là thành viên của danh mục chứa khoản vay. Dùng "Hợp nhất hồ sơ nghiệp vụ".'))
            rows.sort(key=lambda r:(r['status']=='ARCHIVED',r['name'].casefold()))
            return dict(issues=issues,rows=rows,types={k:v for k,v in TYPES.items() if k in EDITABLE_TYPES},deleted=s.get('object_deleted',[]),counts={k:sum(1 for r in rows if r['kind']==k and r['status']=='ACTIVE') for k in EDITABLE_TYPES},archived=sum(1 for r in rows if r['status']=='ARCHIVED'))
