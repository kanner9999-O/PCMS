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
    business_enabled=False      # spec 041: nghiệp vụ tạm dừng (chờ Thạch quyết định); mã và dữ liệu giữ nguyên, giao diện ẩn
    def biz_kind_error(self,s,profile,btype):
        """Why this profile cannot carry the business type, or None. Used by set, merge and migrate (chặn hẳn)."""
        spec=BUSINESS[btype];kind=profile['kind']
        if kind not in spec['kinds']:return f"Hồ sơ loại {KIND_NAMES.get(kind,kind)} không thể mang nghiệp vụ {spec['name']}."
        setup=profile.get('debt_setup')
        if kind=='LOAN' and setup and spec['direction'] and setup['direction']!=spec['direction']:
            return f"Khoản vay này thiết lập chiều {'Phải thu' if setup['direction']=='RECEIVABLE' else 'Phải trả'}; không thể gắn {spec['name']} ({spec['side']})."
        return None

    def loan_home(self,loan):
        """Category a loan record lives in (spec 016 group, else the Gốc vay root)."""
        return loan.get('group') or 'principal'

    def biz_pair_loans(self,s,entry):
        """Loan records of the person that live in this pair's category (spec 040)."""
        prof=item(s['profiles'],entry['profile'])
        if prof['kind']!='PERSON':return []
        return [x for x in s['profiles'] if x['kind']=='LOAN' and x.get('party')==prof['id'] and not x.get('merged_into') and self.loan_home(x)==entry['category']]

    def biz_ledger(self,items,setup,lent,effective):
        """Principal/interest movements of classified parts. Read-only."""
        inc=dec=int_in=int_out=Decimal(0);opening=D(setup['opening']) if setup else Decimal(0);tx=set();pre=False
        for t,p in items:
            kind=p.get('own_category') or p['category'];tx.add(t['id'])
            if effective and t['date']<effective:pre=True
            if kind=='interest':
                if D(t['signed_amount'])>0:int_in+=D(p['amount'])
                else:int_out+=D(p['amount'])
                continue
            if setup and t['date']<setup['effective_date']:pre=True;continue
            if (D(t['signed_amount'])<0)==lent:inc+=D(p['amount'])
            else:dec+=D(p['amount'])
        return dict(inc=inc,dec=dec,int_in=int_in,int_out=int_out,opening=opening,tx=tx,pre=pre)

    def biz_pair_parts(self,s):
        """{(category key, profile): [(transaction, part)]} using the effective (re-homed) parts."""
        out={}
        for t,p in self.cat_parts(s):
            if p.get('profile'):out.setdefault((self.cat_target(p),p['profile']),[]).append((t,p))
        return out

    def biz_items(self,s,entry,index):
        """Parts that belong to the pair. A LOAN record has a single ledger (as in the debt register); a person pair also owns the loans that live in its category."""
        prof=item(s['profiles'],entry['profile'])
        def loan_parts(pid):return [x for (cat,p),items in index.items() if p==pid for x in items if (x[1].get('own_category') or x[1]['category']) in {'principal','interest'}]
        if prof['kind']=='LOAN':return loan_parts(prof['id'])
        own=index.get((entry['category'],entry['profile']),[])
        return own+[x for l in self.biz_pair_loans(s,entry) for x in loan_parts(l['id'])]

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
        require(self.business_enabled,'Nghiệp vụ tạm dừng, chờ quyết định cách làm. Hiện chỉ lưu giao dịch dưới dạng thu và chi.')
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
        require(prof['kind']!='LOAN','Nghiệp vụ gắn cho người sở hữu khoản vay, không gắn cho hồ sơ khoản vay. Gắn cho người trong danh mục.')
        for l in self.biz_pair_loans(s,e):
            sd=(l.get('debt_setup') or {}).get('direction');require(not sd or sd==spec['direction'],f"Khoản {l['name']} thiết lập chiều {'Phải thu' if sd=='RECEIVABLE' else 'Phải trả'}; không thể gắn {spec['name']} ({spec['side']}).")
        params=self.biz_params(d);when=day(d.get('effective_date') or now()[:10])
        if current:
            require(reason,'Cần lý do khi đổi nghiệp vụ hoặc tham số.')
            if current['type']!=btype:require(not self.biz_activity(s,e,index),'Cặp này đã có giao dịch phân loại; không đổi loại nghiệp vụ (đổi chiều làm sai sổ cũ). Tạo đối tượng/danh mục khác cho nghiệp vụ mới.')
            require(current['type']!=btype or current['params']!=params,'Không có thay đổi nào.')
        new=dict(type=btype,effective_date=when,params=params)
        e.setdefault('business_history',[]).append(dict(at=now(),action='CHANGE' if current else 'SET',type=btype,effective_date=when,params=params,reason=reason,before=copy.deepcopy(current)));e['business']=new
        return f"Gắn nghiệp vụ {spec['name']} cho {prof['name']}"

    def business_migration_rows(self,s):
        """Preview of the structure change (spec 040): each person with loans becomes the member of the category the loans live in,
        carrying the business type; loan records stop being members. BĐS profiles become members of Đầu tư BĐS."""
        rows=[];by={p['id']:p for p in s['profiles']}
        groups={}
        for l in s['profiles']:
            if l['kind']=='LOAN' and not l.get('merged_into') and l.get('party') in by:groups.setdefault((l['party'],self.loan_home(l)),[]).append(l)
        for (pid,home),loans in groups.items():
            person=by[pid]
            try:self.cat_target_root(s,home)
            except Exception:rows.append(dict(profile=pid,name=person['name'],kind='PERSON',category=home,action='SKIP',message='Danh mục của khoản vay không còn hoạt động.',loans=[x['name'] for x in loans]));continue
            dirs=({(x.get('debt_setup') or {}).get('direction') for x in loans}-{None}) if self.business_enabled else set()
            retire=[e['id'] for e in s['category_objects'] if e['status']=='ACTIVE' and e['profile'] in {x['id'] for x in loans}]
            pair=active_pair(s,home,pid);has=self.business_enabled and pair is not None and bool(pair.get('business'))
            base=dict(profile=pid,name=person['name'],kind='PERSON',category=home,category_path=self.cat_path(s,home) if home not in ROLES else ROLES[home],loans=[x['name'] for x in loans],retire=retire)
            if len(dirs)>1:rows.append(dict(base,type=None,action='CONFLICT',message='Người này có khoản Phải thu lẫn Phải trả trong cùng một danh mục: chuyển một khoản sang danh mục khác (Công nợ → Chuyển danh mục) rồi hợp nhất lại.'));continue
            btype=None if not dirs else ('LOAN_LENT' if next(iter(dirs))=='RECEIVABLE' else 'LOAN_BORROWED')
            when=min(((x.get('debt_setup') or {}).get('effective_date') for x in loans if x.get('debt_setup')),default=None)
            if has and (btype is None or pair['business']['type']==btype):action,message=('RETIRE_ONLY' if retire else 'NOOP'),''
            elif has:rows.append(dict(base,type=btype,action='CONFLICT',message='Người này đã mang nghiệp vụ khác chiều trong danh mục này.'));continue
            elif btype is None:action,message=('ADD_ONLY' if pair is None else ('RETIRE_ONLY' if retire else 'NOOP')),'Khoản vay chưa thiết lập chiều (Phải thu / Phải trả): người được thêm vào danh mục nhưng chưa gắn loại; hệ thống không đoán chiều. Thiết lập ở màn Công nợ rồi hợp nhất lại.'
            else:action,message=('SET' if pair is not None else 'ADD_AND_SET'),''
            rows.append(dict(base,type=btype,type_name=BUSINESS[btype]['name'] if btype else None,effective_date=when,action=action,message=message))
        for p in (s['profiles'] if self.business_enabled else []):
            if p.get('merged_into') or p['kind']!='PROPERTY':continue
            category='investment';pair=active_pair(s,category,p['id']);has=pair is not None and bool(pair.get('business'))
            rows.append(dict(profile=p['id'],name=p['name'],kind='PROPERTY',category=category,category_path=ROLES[category],type='PROPERTY',type_name='Bất động sản',effective_date=None,retire=[],loans=[],
                action='NOOP' if has else ('SET' if pair is not None else 'ADD_AND_SET'),message='Đã có nghiệp vụ.' if has else ''))
        return rows

    def change_business_migrate(self,s,d):
        from .p01 import now
        require(d.get('confirm') is True,'Xác nhận hợp nhất sau khi xem trước.')
        rows=self.business_migration_rows(s);done=[]
        for r in rows:
            if r['action'] in {'NOOP','SKIP','CONFLICT'}:continue
            prof=item(s['profiles'],r['profile']);pair=active_pair(s,r['category'],prof['id'])
            if pair is None and r['action']!='RETIRE_ONLY':
                pair=dict(id=uid(),category=r['category'],profile=prof['id'],status='ACTIVE',created_at=now(),history=[dict(at=now(),action='ADD',to=r['category'],source='MIGRATION')]);s['category_objects'].append(pair)
            if r['type'] and pair is not None and not pair.get('business'):
                why=self.biz_kind_error(s,prof,r['type']);require(why is None,why or '')
                when=r.get('effective_date') or now()[:10]
                pair['business']=dict(type=r['type'],effective_date=when,params=dict(interest_note='',maturity='',note=''))
                pair.setdefault('business_history',[]).append(dict(at=now(),action='SET',type=r['type'],effective_date=when,params=copy.deepcopy(pair['business']['params']),reason='Hợp nhất hồ sơ nghiệp vụ',before=None))
            for e in s['category_objects']:                    # khoản vay thôi làm thành viên danh mục: người mới là đối tượng (giữ bản ghi, không xóa)
                if e['id'] in r.get('retire',[]):
                    if e.get('business') and self.business_enabled:e.setdefault('business_history',[]).append(dict(at=now(),action='CLEAR',type=None,effective_date=now()[:10],params=None,reason='Chuyển sang người sở hữu khoản vay',before=copy.deepcopy(e['business'])));e['business']=None
                    e.update(status='REMOVED',removed_at=now());e['history'].append(dict(at=now(),action='MIGRATED_TO_PERSON',to=prof['id'],reason='Người là đối tượng của danh mục, khoản vay là mục con'))
            done.append(dict(profile=prof['id'],category=r['category'],type=r['type'],action=r['action'],retired=len(r.get('retire',[]))))
        require(done,'Không có hồ sơ nào cần hợp nhất.')
        s.setdefault('business_migrations',[]).append(dict(id=uid(),at=now(),rows=done));return f'Hợp nhất {len(done)} hồ sơ: người là đối tượng của danh mục, khoản vay là mục con'

    # ---- guards used by category actions ------------------------------------
    def biz_guard_remove(self,s,e):
        require(not self.biz_pair_loans(s,e),'Người này còn khoản vay thuộc danh mục này; chuyển khoản vay sang danh mục khác (Công nợ → Chuyển danh mục) trước khi gỡ.')
        require(not (self.business_enabled and e.get('business')),'Đối tượng đang mang nghiệp vụ; gỡ nghiệp vụ (có lý do) trước khi gỡ khỏi danh mục.')

    def biz_guard_archive(self,s,node):
        if not self.business_enabled:return
        bad=[e for e in s.get('category_objects',[]) if e['status']=='ACTIVE' and e['category']==node['id'] and e.get('business')]
        require(not bad,'Còn đối tượng mang nghiệp vụ trong danh mục này; gỡ hoặc chuyển nghiệp vụ trước.')

    def biz_guard_merge(self,s,src,dst):
        if not self.business_enabled:return
        for e in s.get('category_objects',[]):
            if e['profile']!=src['id'] or e['status']!='ACTIVE' or not e.get('business'):continue
            why=self.biz_kind_error(s,dst,e['business']['type']);require(why is None,'Không gộp được: '+(why or ''))
            twin=active_pair(s,e['category'],dst['id'])
            require(twin is None or not twin.get('business') or twin['business']['type']==e['business']['type'],'Không gộp được: hai hồ sơ mang nghiệp vụ khác loại trong cùng danh mục.')

    # ---- read model -----------------------------------------------------------
    def business_view(self,s):
        if not self.business_enabled:
            s2=dict(s);s2.setdefault('category_objects',[]);return dict(enabled=False,migration=self.business_migration_rows(s2),migrations=s.get('business_migrations',[]))
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
                prof=by[e['profile']];b=e['business'];btype=b['type'];spec=BUSINESS[btype];issues=[]
                root=self.cat_target_root(s,e['category']);base=dict(entry=e['id'],warn=['IN_EXPENSE_REPORT'] if root=='expense' else (['IN_INCOME_REPORT'] if root=='income' else []),group='default',category=e['category'],category_path=self.cat_path(s,e['category']) if e['category'] not in ROLES else ROLES[e['category']],profile=prof['id'],name=prof['name'],kind=prof['kind'],type=btype,type_name=spec['name'],side=spec['side'],
                    effective_date=b['effective_date'],params=b['params'],history=e.get('business_history',[]))
                if btype=='PROPERTY':
                    items=self.biz_items(s,e,index)
                    tin=sum((D(p['amount']) for t,p in items if D(t['signed_amount'])>0),Decimal(0));tout=sum((D(p['amount']) for t,p in items if D(t['signed_amount'])<0),Decimal(0))
                    other.append(dict(base,totals={'in':S(tin),'out':S(tout),'transactions':len({t['id'] for t,p in items})},issues=issues));continue
                lent=btype=='LOAN_LENT';eff=b['effective_date']
                def parts_of(pid):return [x for (cat,p),items in index.items() if p==pid for x in items if (x[1].get('own_category') or x[1]['category']) in {'principal','interest'}]
                if prof['kind']=='LOAN':
                    sources=[(prof,parts_of(prof['id']))];own=[]
                else:
                    own_items=index.get((e['category'],e['profile']),[]);sources=[(l,parts_of(l['id'])) for l in self.biz_pair_loans(s,e)];own=own_items
                inc=dec=int_in=int_out=opening=Decimal(0);tx=set();pre=False;khoan=[];undirected=0
                def add(led):
                    nonlocal inc,dec,int_in,int_out,opening,pre
                    inc+=led['inc'];dec+=led['dec'];int_in+=led['int_in'];int_out+=led['int_out'];opening+=led['opening'];tx.update(led['tx']);pre=pre or led['pre']
                if own:add(self.biz_ledger(own,None,lent,eff))
                for l,items in sources:
                    setup=l.get('debt_setup');sd=(setup or {}).get('direction')
                    if sd and sd!=spec['direction']:issues.append('DIRECTION_MISMATCH');khoan.append(dict(id=l['id'],name=l['name'],direction=sd,excluded=True));continue
                    led=self.biz_ledger(items,setup,lent,eff);add(led);bal=led['opening']+led['inc']-led['dec'];reg=register.get(l['id'])
                    if not setup:issues.append('NO_DIRECTION')
                    if reg and reg['current_principal'] is not None and D(reg['current_principal'])!=bal:issues.append('REGISTER_MISMATCH')
                    khoan.append(dict(id=l['id'],name=l['name'],direction=sd,setup=bool(setup),balance=S(bal),increase=S(led['inc']),decrease=S(led['dec']),interest=S(led['int_in'] if lent else led['int_out']),transactions=len(led['tx']),register=reg['current_principal'] if reg else None))
                for t,p in ([] if prof['kind']=='LOAN' else interest_loose.get(prof['id'],[])):
                    if len(loan_pairs.get(prof['id'],[]))==1 and not sources:
                        if D(t['signed_amount'])>0:int_in+=D(p['amount'])
                        else:int_out+=D(p['amount'])
                        tx.add(t['id'])
                    elif not sources:undirected+=1
                balance=opening+inc-dec
                if prof['kind']=='LOAN' and len(loan_pairs.get(prof['id'],[]))>1:issues.append('DUPLICATE_PAIR')
                if balance<0:issues.append('NEGATIVE_BALANCE')
                if pre:issues.append('PRE_EFFECTIVE')
                if undirected:issues.append('UNDIRECTED_INTEREST')
                main_interest=int_in if lent else int_out
                reg=register.get(prof['id']) if prof['kind']=='LOAN' else None
                loans.append(dict(base,opening=S(opening),increase=S(inc),decrease=S(dec),balance=S(balance),interest=S(main_interest),interest_other=S(int_out if lent else int_in),transactions=len(tx),issues=list(dict.fromkeys(issues)),khoan=khoan,
                    register=dict(principal=reg['current_principal'],issues=reg['issues']) if reg else None,increase_label='Giải ngân' if lent else 'Nhận vay',decrease_label='Thu gốc' if lent else 'Trả gốc',interest_label='Lãi thu' if lent else 'Lãi trả'))
            unassigned=[]
            for e in s['category_objects']:
                if e['status']!='ACTIVE' or e.get('business') or e['profile'] not in by:continue
                prof=by[e['profile']]
                if prof['kind']=='LOAN' and not prof.get('merged_into'):unassigned.append(dict(entry=e['id'],category=e['category'],profile=prof['id'],name=prof['name'],reason='LOAN_AS_MEMBER'))
                elif prof['kind']=='PERSON' and self.biz_pair_loans(s,e):unassigned.append(dict(entry=e['id'],category=e['category'],profile=prof['id'],name=prof['name'],reason='NO_DIRECTION' if any(not l.get('debt_setup') for l in self.biz_pair_loans(s,e)) else 'NO_BUSINESS'))
            receivable=sum((D(x['balance']) for x in loans if x['type']=='LOAN_LENT'),Decimal(0));payable=sum((D(x['balance']) for x in loans if x['type']=='LOAN_BORROWED'),Decimal(0))
            return dict(enabled=True,roles=ROLES,types={k:dict(name=v['name'],side=v['side'],root=v['root'],kinds=sorted(v['kinds'])) for k,v in BUSINESS.items()},plain=sorted(PLAIN),loans=loans,properties=other,unassigned=unassigned,
                totals=dict(receivable=S(receivable),payable=S(payable)),migration=self.business_migration_rows(s),migrations=s.get('business_migrations',[]),basis='Tiền thực thu/chi; chưa dồn tích lãi, dự phòng, xóa nợ.',draft=True)
