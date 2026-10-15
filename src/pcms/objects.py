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

    def obj_in_use(self,s,prof):
        """Why the object cannot be deleted for good (it is referenced somewhere), or None."""
        if prof['kind']=='LOAN':return 'Khoản vay quản lý ở Công nợ.'
        if self.obj_party_loans(s,prof):return 'Người này đang là bên của khoản vay.'
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
        for row in self.business_view(s)['loans']:
            if row['profile']==prof['id'] and D(row['balance'])!=0:return 'Còn dư nợ gốc theo nghiệp vụ; hoàn tất trước khi lưu trữ.'
        return None

    def change_object(self,s,action,d):
        from .p01 import now
        if action=='object-create':
            typ=d.get('type');require(typ in EDITABLE_TYPES,'Chọn loại đối tượng: Người, Bất động sản hoặc Khác.')
            name=str(d.get('name') or '').strip();require(1<=len(name)<=100,'Tên đối tượng dài 1–100 ký tự.');self.require_free_name(s,name)
            prof={'id':uid(),'kind':typ,'name':name,'party':None};s['profiles'].append(prof)
            if d.get('category'):
                self.cat_target_root(s,d['category'])
                s['category_objects'].append(dict(id=uid(),category=d['category'],profile=prof['id'],status='ACTIVE',created_at=now(),history=[dict(at=now(),action='ADD',to=d['category'])]))
            return f"Tạo đối tượng {name} ({TYPES[typ]})"
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
            s['category_objects']=[e for e in s['category_objects'] if e['profile']!=prof['id']];s['profiles']=[x for x in s['profiles'] if x['id']!=prof['id']]
            s.setdefault('object_deleted',[]).append(dict(id=prof['id'],name=prof['name'],kind=prof['kind'],reason=reason,at=now()));return f"Xóa hẳn đối tượng {prof['name']}"
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
            for p in s['profiles']:
                if p['kind']=='LOAN' or p.get('merged_into'):continue
                fam=self.obj_family(s,p);tin=sum((acc.get(i,{}).get('in_',Decimal(0)) for i in fam),Decimal(0));tout=sum((acc.get(i,{}).get('out',Decimal(0)) for i in fam),Decimal(0));tx=set().union(*[acc.get(i,{}).get('tx',set()) for i in fam])
                cats=[dict(category=e['category'],path=self.cat_path(s,e['category']) if e['category'] not in self.ROLES_ else self.ROLES_[e['category']],business=(e.get('business') or {}).get('type')) for e in s['category_objects'] if e['status']=='ACTIVE' and e['profile']==p['id']]
                mine=[dict(id=x['id'],name=x['name'],direction=(x.get('debt_setup') or {}).get('direction'),current=loans[x['id']]['current_principal'],status=loans[x['id']]['completion_status'],setup=bool(x.get('debt_setup')),
                    category=(self.cat_path(s,x['group']) if x.get('group') else self.ROLES_['principal'])) for x in self.obj_party_loans(s,p)]
                rows.append(dict(id=p['id'],name=p['name'],kind=p['kind'],type_name=TYPES[p['kind']],status=p.get('status','ACTIVE'),categories=cats,loans=mine,totals={'in':S(tin),'out':S(tout),'transactions':len(tx)},
                    type_reason=self.obj_type_reason(s,p),delete_reason=self.obj_in_use(s,p),renames=len(p.get('rename_history',[])),archive_history=p.get('archive_history',[]),type_history=p.get('type_history',[])))
            rows.sort(key=lambda r:(r['status']=='ARCHIVED',r['name'].casefold()))
            return dict(rows=rows,types={k:v for k,v in TYPES.items() if k in EDITABLE_TYPES},deleted=s.get('object_deleted',[]),counts={k:sum(1 for r in rows if r['kind']==k and r['status']=='ACTIVE') for k in EDITABLE_TYPES},archived=sum(1 for r in rows if r['status']=='ARCHIVED'))
