"""Category tree: fixed system roots plus user-created child categories, totals and traceable history.

Totals come only from classified parts of source transactions; nothing here creates or edits money.
"""
import copy
import unicodedata
from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext
from .core import require
from .product import D, S, uid

ROOTS={'income':'Thu nhập','expense':'Chi tiêu','principal':'Gốc vay','interest':'Lãi vay','investment':'Đầu tư BĐS','transfer':'Chuyển nội bộ','unknown':'Chưa phân loại'}
PARENTABLE={'income','expense','principal','interest','investment'}
MAX_DEPTH=4
ROOT_TYPES={'income':'Nhóm thu','expense':'Nhóm chi','investment':'Nhóm đầu tư'}

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
        if action=='category-create' and not d.get('parent'):
            typ=d.get('type');require(typ in ROOT_TYPES,'Chọn loại cho danh mục gốc: nhóm thu, nhóm chi hoặc nhóm đầu tư.')
            name=self.cat_name_ok(s,d.get('name'),None);desc=str(d.get('description','')).strip();require(len(desc)<=500,'Mô tả tối đa 500 ký tự.')
            node=dict(id=uid(),name=name,description=desc,parent=None,root=typ,status='ACTIVE',created_at=now(),history=[])
            log(node,'CREATE',None,dict(name=name,type=typ));s['categories'].append(node);return 'Tạo danh mục gốc '+name
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
            for p in parts:yield t,p

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
            s=cat_state(copy.deepcopy(s));acc={}
            for t,p in self.cat_parts(s,start,end):
                incoming=D(t['signed_amount'])>0;amount=D(p['amount'])
                for key in self.cat_keys(s,p):
                    a=acc.setdefault(key,dict(in_=Decimal(0),out=Decimal(0),parts=0,tx=set()))
                    a['in_' if incoming else 'out']+=amount;a['parts']+=1;a['tx'].add(t['id'])
            def totals(key,spend=False):
                a=acc.get(key);a=a or dict(in_=Decimal(0),out=Decimal(0),parts=0,tx=set())
                out=dict(**{'in':S(a['in_']),'out':S(a['out']),'net':S(a['in_']-a['out']),'parts':a['parts'],'transactions':len(a['tx'])})
                if spend:out['net_spend']=S(a['out']-a['in_'])
                return out
            roots=[dict(key=k,name=v,description=s['category_roots'].get(k,''),parentable=k in PARENTABLE,totals=totals(k,k=='expense')) for k,v in ROOTS.items()]
            nodes=[dict(id=n['id'],name=n['name'],description=n['description'],parent=n['parent'],root=n['root'],status=n['status'],depth=self.cat_depth(s,n),path=self.cat_path(s,n['id']),history=n['history'],totals=totals(n['id'],n['root']=='expense')) for n in s['categories']]
            return dict(roots=roots,nodes=nodes,max_depth=MAX_DEPTH,root_types=ROOT_TYPES,period=dict(start=start,end=end) if (start or end) else None,draft=True)

    def category_history(self,d,s=None):
        from .p01 import display_day
        with localcontext() as ctx:
            ctx.prec=60
            s=cat_state(copy.deepcopy(s or self.state()));key=d.get('category');start,end=self.cat_period(d);account=d.get('account') or None
            require(key in ROOTS or any(n['id']==key for n in s['categories']),'Chọn danh mục.')
            approved={t['id'] for snap in s['snapshots'] for t in snap['report']['transactions']}
            accounts={a['id']:a['name'] for a in s['accounts']};profiles={p['id']:p['name'] for p in s['profiles']}
            rows=[];tx=set();inc=out=Decimal(0)
            for t,p in self.cat_parts(s,start,end,account):
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
            root=key if key in ROOTS else next(n['root'] for n in s['categories'] if n['id']==key)
            totals={'in':S(inc),'out':S(out),'net':S(inc-out),'parts':len(rows),'transactions':len(tx)}
            if root=='expense':totals['net_spend']=S(out-inc)
            return dict(category=key,root=root,path=self.cat_path(s,key),evidence=evidence,source_notice=notice,totals=totals,rows=rows,period=dict(start=start,end=end) if (start or end) else None)

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
                    unknown=p['category']=='unknown';node=p.get('node')
                    base='Chưa phân loại' if unknown else (self.cat_path(s,node) if node else ROOTS[root_key(p['category'])])
                    obj=profiles.get(p.get('profile')) if p.get('profile') else None
                    name=base if unknown or not obj else f'{base} · {obj}'
                    typ=root_key(p['category']) if not node else self.cat_find(s,node)['root']
                    amount=D(p['amount']);g=groups.setdefault(name,dict(key=name,name=name,type=typ,unclassified=unknown,tx=set(),in_=Decimal(0),out=Decimal(0),latest=None,rows=[]))
                    g['in_' if incoming else 'out']+=amount;g['tx'].add(t['id']);seen.add(t['id'])
                    if incoming:g_in+=amount
                    else:g_out+=amount
                    if at and (g['latest'] is None or at>g['latest']):g['latest']=at
                    label='Hoàn chi tiêu' if (p['category']=='expense' and incoming) else base
                    g['rows'].append(dict(transaction=t['id'],date=t['date'],reference=t['reference'],description=t['description'],amount=S(amount),tx_amount=S(abs(signed)),direction='IN' if incoming else 'OUT',
                        label=label,object=obj,split=len(parts)>1,classified_at=at,recent=bool(at and at>=cutoff),status='APPROVED' if t['id'] in approved else 'DRAFT',sources=len(t.get('sources',[])),_order=t.get('order',0)))
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
