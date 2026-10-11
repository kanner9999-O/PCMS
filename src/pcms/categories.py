"""Category tree: fixed system roots plus user-created child categories, totals and traceable history.

Totals come only from classified parts of source transactions; nothing here creates or edits money.
"""
import copy
import unicodedata
from decimal import Decimal, localcontext
from .core import require
from .product import D, S, uid

ROOTS={'income':'Thu nhập','expense':'Chi tiêu','principal':'Gốc vay','interest':'Lãi vay','investment':'Đầu tư BĐS','transfer':'Chuyển nội bộ','unknown':'Chưa phân loại'}
PARENTABLE={'income','expense','principal','interest','investment'}
MAX_DEPTH=4

def root_key(category):
    return 'transfer' if category=='transfer_pending' else category

def norm_name(value):
    return unicodedata.normalize('NFC',str(value or '').strip()).casefold()

def cat_state(s):
    s.setdefault('categories',[]);s.setdefault('category_roots',{})
    return s

class Categories:
    # ---- tree helpers -------------------------------------------------
    def cat_find(self,s,cid):
        found=next((n for n in cat_state(s)['categories'] if n['id']==cid),None)
        require(found is not None,'Không tìm thấy danh mục.')
        return found

    def cat_depth(self,s,node):
        depth=2;parent=node['parent']
        while parent not in ROOTS:
            parent=self.cat_find(s,parent)['parent'];depth+=1
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
        names.append(ROOTS.get(cid,cid));return ' › '.join(reversed(names))

    def cat_name_ok(self,s,name,parent,own=None):
        name=str(name or '').strip();require(1<=len(name)<=100,'Tên danh mục dài 1–100 ký tự.')
        require(not any(n['parent']==parent and n['id']!=own and norm_name(n['name'])==norm_name(name) for n in s['categories']),'Đã có danh mục cùng tên trong cùng danh mục cha (kể cả đã lưu trữ).')
        return name

    def cat_parent_ok(self,s,parent):
        if parent in ROOTS:
            require(parent in PARENTABLE,'Gốc này không có danh mục con.');return parent
        p=self.cat_find(s,parent);require(p['status']=='ACTIVE','Danh mục cha đang lưu trữ.');return p['root']

    # ---- actions ------------------------------------------------------
    def change_category(self,s,action,d):
        from .p01 import now
        cat_state(s)
        def log(node,kind,before,after,reason=''):
            node['history'].append(dict(at=now(),action=kind,before=before,after=after,reason=str(reason or '').strip()[:500]))
        if action=='category-root-describe':
            key=d.get('root');require(key in ROOTS,'Chọn một danh mục gốc.')
            text=str(d.get('description','')).strip();require(len(text)<=500,'Mô tả tối đa 500 ký tự.')
            s['category_roots'][key]=text;return 'Cập nhật mô tả '+ROOTS[key]
        if action=='category-create':
            parent=d.get('parent');root=self.cat_parent_ok(s,parent)
            name=self.cat_name_ok(s,d.get('name'),parent);desc=str(d.get('description','')).strip();require(len(desc)<=500,'Mô tả tối đa 500 ký tự.')
            depth=2 if parent in ROOTS else self.cat_depth(s,self.cat_find(s,parent))+1
            require(depth<=MAX_DEPTH,f'Tối đa {MAX_DEPTH} cấp kể cả danh mục gốc.')
            node=dict(id=uid(),name=name,description=desc,parent=parent,root=root,status='ACTIVE',created_at=now(),history=[])
            log(node,'CREATE',None,dict(name=name,parent=parent));s['categories'].append(node);return 'Tạo danh mục '+name
        node=self.cat_find(s,d.get('category'))
        if action=='category-edit':
            changed=False;reason=d.get('reason','')
            if 'parent' in d and d['parent']!=node['parent']:
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
            log(node,'ARCHIVE','ACTIVE','ARCHIVED',reason);node['status']='ARCHIVED';return 'Lưu trữ danh mục '+node['name']
        if action=='category-restore':
            require(node['status']=='ARCHIVED','Danh mục đang hoạt động.')
            require(node['parent'] in ROOTS or self.cat_find(s,node['parent'])['status']=='ACTIVE','Khôi phục danh mục cha trước.')
            log(node,'RESTORE','ARCHIVED','ACTIVE',d.get('reason',''));node['status']='ACTIVE';return 'Khôi phục danh mục '+node['name']
        require(False,'Hành động không hợp lệ.')

    # ---- quick object creation (one atomic step from the classify dialog) ----
    def change_quick_object(self,s,d):
        from .product import uid as new_id
        kind=d.get('kind');profiles=s['profiles']
        def unique(label,name,of_kind):
            require(not any(p['kind']==of_kind and norm_name(p['name'])==norm_name(name) for p in profiles),f'Đã có {label} cùng tên; hãy chọn cái có sẵn.')
        def clean(name,message):
            name=str(name or '').strip();require(1<=len(name)<=100,message);return name
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
                while any(p['kind']=='LOAN' and norm_name(p['name'])==norm_name(name) for p in profiles):name=f'{base} ({n})';n+=1;require(len(name)<=100,'Tên khoản vay tối đa 100 ký tự.')
            else:unique('khoản vay',name,'LOAN')
            if created:profiles.append(created)
            profiles.append({'id':new_id(),'kind':'LOAN','name':name,'party':person['id']})
            return 'Tạo nhanh khoản vay '+name+(' và người '+person['name'] if created else '')
        if kind=='CATEGORY':
            return self.change_category(s,'category-create',dict(parent=d.get('parent'),name=d.get('name'),description=''))
        require(False,'Loại đối tượng không hợp lệ.')

    def cat_descendants(self,s,node):
        out=[];stack=[node['id']]
        while stack:
            cid=stack.pop()
            for n in s['categories']:
                if n['parent']==cid:out.append(n);stack.append(n['id'])
        return out

    # ---- totals & history --------------------------------------------
    def cat_parts(self,s):
        """Yield (transaction, part) for every classified part; unclassified money goes to the 'unknown' root."""
        for t in s['transactions']:
            parts=t['allocations'] or [{'category':'unknown','amount':S(abs(D(t['signed_amount']))),'profile':None}]
            for p in parts:yield t,p

    def cat_keys(self,s,p):
        key=root_key(p['category']);node=p.get('node')
        return [key]+(self.cat_chain(s,node) if node else [])

    def category_view(self,s):
        with localcontext() as ctx:
            ctx.prec=60
            s=cat_state(copy.deepcopy(s));acc={}
            for t,p in self.cat_parts(s):
                incoming=D(t['signed_amount'])>0;amount=D(p['amount'])
                for key in self.cat_keys(s,p):
                    a=acc.setdefault(key,dict(in_=Decimal(0),out=Decimal(0),parts=0,tx=set()))
                    a['in_' if incoming else 'out']+=amount;a['parts']+=1;a['tx'].add(t['id'])
            def totals(key):
                a=acc.get(key);a=a or dict(in_=Decimal(0),out=Decimal(0),parts=0,tx=set())
                return dict(**{'in':S(a['in_']),'out':S(a['out']),'net':S(a['in_']-a['out']),'parts':a['parts'],'transactions':len(a['tx'])})
            roots=[dict(key=k,name=v,description=s['category_roots'].get(k,''),parentable=k in PARENTABLE,totals=totals(k)) for k,v in ROOTS.items()]
            nodes=[dict(id=n['id'],name=n['name'],description=n['description'],parent=n['parent'],root=n['root'],status=n['status'],depth=self.cat_depth(s,n),path=self.cat_path(s,n['id']),history=n['history'],totals=totals(n['id'])) for n in s['categories']]
            return dict(roots=roots,nodes=nodes,max_depth=MAX_DEPTH,draft=True)

    def category_history(self,d,s=None):
        from .p01 import display_day
        with localcontext() as ctx:
            ctx.prec=60
            s=cat_state(copy.deepcopy(s or self.state()));key=d.get('category')
            require(key in ROOTS or any(n['id']==key for n in s['categories']),'Chọn danh mục.')
            approved={t['id'] for snap in s['snapshots'] for t in snap['report']['transactions']}
            accounts={a['id']:a['name'] for a in s['accounts']};profiles={p['id']:p['name'] for p in s['profiles']}
            rows=[];tx=set();inc=out=Decimal(0)
            for t,p in self.cat_parts(s):
                if key not in self.cat_keys(s,p):continue
                incoming=D(t['signed_amount'])>0;amount=D(p['amount']);tx.add(t['id'])
                if incoming:inc+=amount
                else:out+=amount
                node=p.get('node');row_path=self.cat_path(s,node) if node else ROOTS[root_key(p['category'])]
                rows.append(dict(transaction=t['id'],date=t['date'],account=accounts.get(t['account'],''),reference=t['reference'],description=t['description'],amount=S(amount),direction='IN' if incoming else 'OUT',
                    category_path=row_path,object=profiles.get(p.get('profile')),status='APPROVED' if t['id'] in approved else 'DRAFT',node_status=next((n['status'] for n in s['categories'] if n['id']==node),None) if node else None,sources=copy.deepcopy(t.get('sources',[]))))
            rows.sort(key=lambda r:(r['date'],r['reference']))
            periods=[(b['period_start'],b['period_end']) for b in s['imports'] if b['status']=='PUBLISHED']
            evidence='HAS_DATA' if rows else ('EMPTY' if periods else 'EMPTY_NO_SOURCE')
            notice=('Kỳ nguồn đã ghi: '+'; '.join(display_day(a)+' → '+display_day(b) for a,b in sorted(set(periods)))+'. Ngoài các kỳ này chưa có bằng chứng.') if periods else 'Chưa có nguồn ngân hàng nào được ghi; không suy ra là không phát sinh.'
            return dict(category=key,path=self.cat_path(s,key),evidence=evidence,source_notice=notice,totals={'in':S(inc),'out':S(out),'net':S(inc-out),'parts':len(rows),'transactions':len(tx)},rows=rows)
