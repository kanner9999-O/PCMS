"""Business types attached to (object, category) pairs; ledgers are read-only views over classified parts (spec 031).

A category carries a neutral cash-flow role (derived from its system root). An object inside a category may carry a
business type with parameters. Nothing here creates or edits money.
"""
import copy
from decimal import Decimal, localcontext
from .core import require
from .product import D, S, uid, item

ROLES={'income':'Dòng tiền thu','expense':'Dòng tiền chi','principal':'Gốc vay','interest':'Lãi vay','investment':'Đầu tư BĐS','transfer':'Chuyển nội bộ','unknown':'Chưa phân loại'}
PLAIN={'income','expense'}
BUSINESS={'LOAN_LENT':dict(name='Cho vay',side='Phải thu',root='principal',kinds={'LOAN','PERSON','OBJECT'},direction='RECEIVABLE'),
          'LOAN_BORROWED':dict(name='Đi vay',side='Phải trả',root='principal',kinds={'LOAN','PERSON','OBJECT'},direction='PAYABLE'),
          'PROPERTY':dict(name='Bất động sản',side='Tài sản',root='investment',kinds={'PROPERTY','OBJECT'},direction=None)}
KIND_NAMES={'PERSON':'người','LOAN':'khoản vay','PROPERTY':'BĐS','OBJECT':'đối tượng'}

def active_pair(s,category,profile):
    return next((e for e in s.get('category_objects',[]) if e['status']=='ACTIVE' and e['category']==category and e['profile']==profile),None)

class Business:
    ROLES_=ROLES
    def biz_kind_error(self,s,profile,btype):
        """Why this profile cannot carry the business type, or None. Used by set, merge and migrate (chặn hẳn)."""
        spec=BUSINESS[btype];kind=profile['kind']
        if kind not in spec['kinds']:return f"Hồ sơ loại {KIND_NAMES.get(kind,kind)} không thể mang nghiệp vụ {spec['name']}."
        setup=profile.get('debt_setup')
        if kind=='LOAN' and setup and spec['direction'] and setup['direction']!=spec['direction']:
            return f"Khoản vay này thiết lập chiều {'Phải thu' if setup['direction']=='RECEIVABLE' else 'Phải trả'}; không thể gắn {spec['name']} ({spec['side']})."
        return None

    def biz_pair_parts(self,s):
        """{(category key, profile): [(transaction, part)]} using the effective (re-homed) parts."""
        out={}
        for t,p in self.cat_parts(s):
            if p.get('profile'):out.setdefault((self.cat_target(p),p['profile']),[]).append((t,p))
        return out

    def biz_items(self,s,entry,index):
        """Parts that belong to the pair. A LOAN profile has a single ledger (as in the debt register) wherever its parts were classified."""
        prof=item(s['profiles'],entry['profile'])
        if prof['kind']=='LOAN':return [x for (cat,pid),items in index.items() if pid==prof['id'] for x in items if (x[1].get('own_category') or x[1]['category']) in {'principal','interest'}]
        return index.get((entry['category'],entry['profile']),[])

    def biz_activity(self,s,entry,index=None):
        return bool(self.biz_items(s,entry,index if index is not None else self.biz_pair_parts(s)))

    def biz_params(self,d):
        rate=str(d.get('interest_note') or '').strip().replace(',','.')
        if rate:
            try:value=Decimal(rate)
            except Exception:require(False,'Lãi suất thỏa thuận phải là số.')
            require(Decimal(0)<=value<=Decimal(1000),'Lãi suất thỏa thuận từ 0 đến 1000.')
        from .p01 import day
        maturity=str(d.get('maturity') or '').strip()
        if maturity:day(maturity)
        note=str(d.get('note') or '').strip();require(len(note)<=500,'Ghi chú nghiệp vụ tối đa 500 ký tự.')
        return dict(interest_note=rate,maturity=maturity,note=note)

    # ---- actions ---------------------------------------------------------
    def change_business(self,s,action,d):
        from .p01 import day,now
        if action=='business-migrate':return self.change_business_migrate(s,d)
        e=active_pair(s,d.get('category'),d.get('profile'));require(e is not None,'Đối tượng không có trong danh mục này.')
        prof=item(s['profiles'],e['profile']);root=self.cat_target_root(s,e['category']);current=e.get('business');reason=str(d.get('reason') or '').strip()[:500]
        index=self.biz_pair_parts(s)
        if action=='business-clear':
            require(current,'Đối tượng chưa mang nghiệp vụ.');require(reason,'Cần lý do gỡ nghiệp vụ.')
            require(not self.biz_activity(s,e,index),'Cặp này đã có giao dịch phân loại; không gỡ nghiệp vụ để tránh làm mất sổ phải thu/phải trả. Giữ nghiệp vụ và chỉ chỉnh tham số.')
            when=day(d.get('effective_date') or now()[:10])
            e.setdefault('business_history',[]).append(dict(at=now(),action='CLEAR',type=None,effective_date=when,params=None,reason=reason,before=copy.deepcopy(current)));e['business']=None
            return f"Gỡ nghiệp vụ của {prof['name']}"
        if action!='business-set':require(False,'Hành động không hợp lệ.')
        btype=d.get('type');require(btype in BUSINESS,'Chọn loại nghiệp vụ.');spec=BUSINESS[btype]
        why=self.biz_kind_error(s,prof,btype);require(why is None,why or '')
        params=self.biz_params(d);when=day(d.get('effective_date') or now()[:10])
        if current:
            require(reason,'Cần lý do khi đổi nghiệp vụ hoặc tham số.')
            if current['type']!=btype:require(not self.biz_activity(s,e,index),'Cặp này đã có giao dịch phân loại; không đổi loại nghiệp vụ (đổi chiều làm sai sổ cũ). Tạo đối tượng/danh mục khác cho nghiệp vụ mới.')
            require(current['type']!=btype or current['params']!=params,'Không có thay đổi nào.')
        new=dict(type=btype,effective_date=when,params=params)
        e.setdefault('business_history',[]).append(dict(at=now(),action='CHANGE' if current else 'SET',type=btype,effective_date=when,params=params,reason=reason,before=copy.deepcopy(current)));e['business']=new
        return f"Gắn nghiệp vụ {spec['name']} cho {prof['name']}"

    def business_migration_rows(self,s):
        rows=[]
        for p in s['profiles']:
            if p.get('merged_into') or p['kind'] not in {'LOAN','PROPERTY'}:continue
            if p['kind']=='LOAN':
                category=p.get('group') or 'principal';setup=p.get('debt_setup');btype=None
                if setup:btype='LOAN_LENT' if setup['direction']=='RECEIVABLE' else 'LOAN_BORROWED'
                when=setup['effective_date'] if setup else None
            else:category='investment';btype='PROPERTY';when=None
            try:self.cat_target_root(s,category)
            except Exception:rows.append(dict(profile=p['id'],name=p['name'],kind=p['kind'],category=category,type=btype,action='SKIP',message='Danh mục của hồ sơ không còn hoạt động.'));continue
            pair=active_pair(s,category,p['id']);has=pair is not None and bool(pair.get('business'))
            if has:action,message='NOOP','Đã có nghiệp vụ.'
            elif btype is None:action,message=('ADD_ONLY' if pair is None else 'NOOP'),'Khoản vay chưa thiết lập chiều (Phải thu / Phải trả): đưa vào danh mục nhưng chưa gắn loại; hệ thống không đoán chiều. Thiết lập ở màn Công nợ rồi hợp nhất lại.'
            else:action,message=('SET' if pair is not None else 'ADD_AND_SET'),''
            rows.append(dict(profile=p['id'],name=p['name'],kind=p['kind'],category=category,category_path=self.cat_path(s,category) if category not in ROLES else ROLES[category],type=btype,type_name=BUSINESS[btype]['name'] if btype else None,effective_date=when,action=action,message=message))
        return rows

    def change_business_migrate(self,s,d):
        from .p01 import now
        require(d.get('confirm') is True,'Xác nhận hợp nhất sau khi xem trước.')
        rows=self.business_migration_rows(s);done=[]
        for r in rows:
            if r['action'] in {'NOOP','SKIP'}:continue
            prof=item(s['profiles'],r['profile']);pair=active_pair(s,r['category'],prof['id'])
            if pair is None:
                pair=dict(id=uid(),category=r['category'],profile=prof['id'],status='ACTIVE',created_at=now(),history=[dict(at=now(),action='ADD',to=r['category'],source='MIGRATION')]);s['category_objects'].append(pair)
            if r['type'] and not pair.get('business'):
                why=self.biz_kind_error(s,prof,r['type']);require(why is None,why or '')
                when=r['effective_date'] or now()[:10]
                pair['business']=dict(type=r['type'],effective_date=when,params=dict(interest_note='',maturity='',note=''))
                pair.setdefault('business_history',[]).append(dict(at=now(),action='SET',type=r['type'],effective_date=when,params=copy.deepcopy(pair['business']['params']),reason='Hợp nhất hồ sơ nghiệp vụ',before=None))
            done.append(dict(profile=prof['id'],category=r['category'],type=r['type'],action=r['action']))
        require(done,'Không có hồ sơ nào cần hợp nhất.')
        s.setdefault('business_migrations',[]).append(dict(id=uid(),at=now(),rows=done));return f'Hợp nhất {len(done)} hồ sơ vào đối tượng có nghiệp vụ'

    # ---- guards used by category actions ------------------------------------
    def biz_guard_remove(self,s,e):
        require(not e.get('business'),'Đối tượng đang mang nghiệp vụ; gỡ nghiệp vụ (có lý do) trước khi gỡ khỏi danh mục.')

    def biz_guard_archive(self,s,node):
        bad=[e for e in s.get('category_objects',[]) if e['status']=='ACTIVE' and e['category']==node['id'] and e.get('business')]
        require(not bad,'Còn đối tượng mang nghiệp vụ trong danh mục này; gỡ hoặc chuyển nghiệp vụ trước.')

    def biz_guard_merge(self,s,src,dst):
        for e in s.get('category_objects',[]):
            if e['profile']!=src['id'] or e['status']!='ACTIVE' or not e.get('business'):continue
            why=self.biz_kind_error(s,dst,e['business']['type']);require(why is None,'Không gộp được: '+(why or ''))
            twin=active_pair(s,e['category'],dst['id'])
            require(twin is None or not twin.get('business') or twin['business']['type']==e['business']['type'],'Không gộp được: hai hồ sơ mang nghiệp vụ khác loại trong cùng danh mục.')

    # ---- read model -----------------------------------------------------------
    def business_view(self,s):
        with localcontext() as ctx:
            ctx.prec=60
            s=copy.deepcopy(s);s.setdefault('category_objects',[]);by={p['id']:p for p in s['profiles']};index=self.biz_pair_parts(s)
            register={x['id']:x for x in self.debt_register(s)['loans']}
            pairs=[e for e in s['category_objects'] if e['status']=='ACTIVE' and e.get('business') and e['profile'] in by]
            loan_pairs={}
            for e in pairs:
                if e['business']['type'].startswith('LOAN_'):loan_pairs.setdefault(e['profile'],[]).append(e)
            interest_loose={}
            for key,items in index.items():
                for t,p in items:
                    if (p.get('own_category') or p['category'])=='interest' and p['category']=='interest':interest_loose.setdefault(p['profile'],[]).append((t,p))
            loans=[];other=[]
            for e in pairs:
                prof=by[e['profile']];b=e['business'];btype=b['type'];spec=BUSINESS[btype];items=self.biz_items(s,e,index);issues=[]
                root=self.cat_target_root(s,e['category']);base=dict(entry=e['id'],warn=['IN_EXPENSE_REPORT'] if root=='expense' else (['IN_INCOME_REPORT'] if root=='income' else []),group='default',category=e['category'],category_path=self.cat_path(s,e['category']) if e['category'] not in ROLES else ROLES[e['category']],profile=prof['id'],name=prof['name'],kind=prof['kind'],type=btype,type_name=spec['name'],side=spec['side'],
                    effective_date=b['effective_date'],params=b['params'],history=e.get('business_history',[]))
                if btype=='PROPERTY':
                    tin=sum((D(p['amount']) for t,p in items if D(t['signed_amount'])>0),Decimal(0));tout=sum((D(p['amount']) for t,p in items if D(t['signed_amount'])<0),Decimal(0))
                    other.append(dict(base,totals={'in':S(tin),'out':S(tout),'transactions':len({t['id'] for t,p in items})},issues=issues));continue
                setup=prof.get('debt_setup') if prof['kind']=='LOAN' else None
                lent=btype=='LOAN_LENT';inc=dec=int_in=int_out=Decimal(0);opening=D(setup['opening']) if setup else Decimal(0);tx=set();pre=False;undirected=0
                def add_interest(t,p):
                    nonlocal int_in,int_out
                    if D(t['signed_amount'])>0:int_in+=D(p['amount'])
                    else:int_out+=D(p['amount'])
                for t,p in items:
                    kind=p.get('own_category') or p['category'];tx.add(t['id'])
                    if b['effective_date'] and t['date']<b['effective_date']:pre=True
                    if kind=='interest':add_interest(t,p);continue
                    if setup and t['date']<setup['effective_date']:pre=True;continue
                    out_=D(t['signed_amount'])<0
                    if out_==lent:inc+=D(p['amount'])
                    else:dec+=D(p['amount'])
                for t,p in ([] if prof['kind']=='LOAN' else interest_loose.get(prof['id'],[])):
                    if len(loan_pairs.get(prof['id'],[]))==1:add_interest(t,p);tx.add(t['id'])
                    else:undirected+=1
                balance=opening+inc-dec
                reg=register.get(prof['id'])
                if prof['kind']=='LOAN' and len(loan_pairs.get(prof['id'],[]))>1:issues.append('DUPLICATE_PAIR')
                if balance<0:issues.append('NEGATIVE_BALANCE')
                if pre:issues.append('PRE_EFFECTIVE')
                if undirected:issues.append('UNDIRECTED_INTEREST')
                if prof['kind']=='LOAN' and not setup:issues.append('NO_DIRECTION')
                if reg and reg['current_principal'] is not None and D(reg['current_principal'])!=balance:issues.append('REGISTER_MISMATCH')
                main_interest=int_in if lent else int_out
                loans.append(dict(base,opening=S(opening),increase=S(inc),decrease=S(dec),balance=S(balance),interest=S(main_interest),interest_other=S(int_out if lent else int_in),transactions=len(tx),issues=issues,
                    register=dict(principal=reg['current_principal'],issues=reg['issues']) if reg else None,increase_label='Giải ngân' if lent else 'Nhận vay',decrease_label='Thu gốc' if lent else 'Trả gốc',interest_label='Lãi thu' if lent else 'Lãi trả'))
            unassigned=[]
            for e in s['category_objects']:
                if e['status']!='ACTIVE' or e.get('business') or e['profile'] not in by:continue
                prof=by[e['profile']]
                if prof['kind']=='LOAN' and not prof.get('merged_into'):unassigned.append(dict(entry=e['id'],category=e['category'],profile=prof['id'],name=prof['name'],reason='NO_DIRECTION' if not prof.get('debt_setup') else 'NO_BUSINESS'))
            receivable=sum((D(x['balance']) for x in loans if x['type']=='LOAN_LENT'),Decimal(0));payable=sum((D(x['balance']) for x in loans if x['type']=='LOAN_BORROWED'),Decimal(0))
            return dict(roles=ROLES,types={k:dict(name=v['name'],side=v['side'],root=v['root'],kinds=sorted(v['kinds'])) for k,v in BUSINESS.items()},plain=sorted(PLAIN),loans=loans,properties=other,unassigned=unassigned,
                totals=dict(receivable=S(receivable),payable=S(payable)),migration=self.business_migration_rows(s),migrations=s.get('business_migrations',[]),basis='Tiền thực thu/chi; chưa dồn tích lãi, dự phòng, xóa nợ.',draft=True)
