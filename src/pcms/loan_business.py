"""Spec 046 (R203–R212): Cho vay / Đi vay gắn vào danh mục.

Nghiệp vụ là lớp song song trên cây danh mục (Constitution VII): danh mục mang nghiệp vụ, nhánh con kế thừa; khoản vay thuộc
một người; chi tiết nghiệp vụ bóc phần tiền đã phân loại của từng nguồn (giao dịch ngân hàng hoặc dòng lịch sử cũ) thành
gốc / lãi / phí môi giới của từng khoản. Chi tiết nằm ngoài giao dịch nên tiền nguồn, sao kê và snapshot không đổi (R212).
Sổ khoản vay (`loan_book`) là phép tính duy nhất cho mọi màn (R210). Không có gì ở đây tạo hay sửa tiền nguồn.
"""
import copy
import re
from datetime import date, timedelta
from decimal import Decimal, localcontext, ROUND_HALF_UP, InvalidOperation
from .core import require, digest, ValidationError
from .product import D, S, uid, item
from .categories import ROOTS

DIRS={'RECEIVABLE':dict(name='Cho vay',side='Phải thu',prefix='CV'),'PAYABLE':dict(name='Đi vay',side='Phải trả',prefix='ĐV')}
# thành phần hợp lệ theo (chiều khoản, chiều tiền) — R205: người dùng chọn, hệ thống không tự suy
COMPONENTS={('RECEIVABLE','OUT'):{'principal':'Giải ngân','broker':'Trả phí môi giới'},('RECEIVABLE','IN'):{'principal':'Thu gốc','interest':'Thu lãi'},
            ('PAYABLE','IN'):{'principal':'Nhận tiền vay'},('PAYABLE','OUT'):{'principal':'Trả gốc','interest':'Trả lãi'}}
MILLION=Decimal(1000000)
MAX_RATE=Decimal(100000)
PENDING_TEXT={'NO_PERSON':'chưa chọn người','NOT_PERSON':'đối tượng không phải Người','NO_LOAN':'người chưa có khoản vay cùng chiều',
    'NOT_DETAILED':'chưa ghi chi tiết nghiệp vụ','DRAFT':'có nháp chưa ghi','MISMATCH':'chi tiết đã ghi không còn khớp phân loại',
    'LEGACY_DIRECTION':'khoản vay cũ khác chiều nghiệp vụ','LEGACY_NO_SETUP':'khoản vay cũ chưa thiết lập chiều','LEGACY_NOT_COUNTED':'khoản vay cũ gắn ngoài Gốc vay/Lãi vay nên sổ cũ không tính; sửa phân loại sang Người',
    'LOAN_MISMATCH':'khoản vay đã chọn khi phân loại không thuộc người hoặc khác chiều nghiệp vụ; sửa phân loại'}

def lb_state(s):
    for k in ('loans','loan_details','loan_waivers'):s.setdefault(k,[])
    return s

def rnd(x):return x.quantize(Decimal(1),rounding=ROUND_HALF_UP)
def _d(x):return date.fromisoformat(x)
def _gap(a,b):return (_d(b)-_d(a)).days

def lb_rate(value,label):
    text=str(value if value is not None else '').strip().replace(',','.')
    require(text!='',f'Nhập {label} (đồng/triệu/ngày; 0 là không lãi).')
    try:r=Decimal(text)
    except InvalidOperation:raise ValidationError(f'{label.capitalize()} phải là số.')
    require(r.is_finite() and Decimal(0)<=r<=MAX_RATE,f'{label.capitalize()} từ 0 đến 100.000 đồng/triệu/ngày.')
    require(-r.as_tuple().exponent<=4 if r.as_tuple().exponent<0 else True,f'{label.capitalize()} tối đa 4 chữ số thập phân.')
    return format(r.normalize(),'f') if r!=0 else '0'

def lb_accrue(events,rate,as_of,broker_rate=None):
    """Lãi theo đoạn sự kiện (R206). events={ngày:{'disb':D,'repay':D}}. Cơ sở ngày D = dư cuối D−1 + giải ngân D;
    gốc trả ngày D chỉ giảm cơ sở từ D+1. Trả (lãi thô, môi giới thô, dư cuối tới ngày xem, các đoạn)."""
    with localcontext() as ctx:
        ctx.prec=80
        closing=Decimal(0);prev=None;segs=[]
        def add(start,end,days,base):
            if days<=0 or base<=0:return
            if segs and segs[-1]['base']==base and _gap(segs[-1]['end'],start)==1:segs[-1].update(end=end,days=segs[-1]['days']+days)
            else:segs.append(dict(start=start,end=end,days=days,base=base))
        for d in sorted(x for x in events if x<=as_of):
            if prev is not None and _gap(prev,d)>1:add((_d(prev)+timedelta(days=1)).isoformat(),(_d(d)-timedelta(days=1)).isoformat(),_gap(prev,d)-1,closing)
            e=events[d];add(d,d,1,closing+e['disb']);closing=closing+e['disb']-e['repay'];prev=d
        if prev is not None and prev<as_of:add((_d(prev)+timedelta(days=1)).isoformat(),as_of,_gap(prev,as_of),closing)
        r=D(rate);b=D(broker_rate) if broker_rate is not None else None
        raw=sum((g['base']*g['days'] for g in segs),Decimal(0))
        for g in segs:g.update(base=S(g['base']),interest=S(g['base']*g['days']*r/MILLION),broker=S(g['base']*g['days']*b/MILLION) if b is not None else None)
        return raw*r/MILLION,(raw*b/MILLION if b is not None else None),closing,segs


class LoanBusiness:
    # ---- nghiệp vụ danh mục (R203) ----------------------------------------------------------
    def lb_biz_map(self,s):
        """{node id: (loại, nút gắn)} nghiệp vụ hiệu lực của mọi danh mục người dùng tạo; gốc hệ thống không mang nghiệp vụ."""
        by={n['id']:n for n in s.get('categories',[])};out={}
        def eff(cid):
            if cid in out:return out[cid]
            n=by[cid];own=(n.get('business') or {}).get('type')
            r=(own,cid) if own else (eff(n['parent']) if n['parent'] in by else None)
            out[cid]=r;return r
        for cid in by:eff(cid)
        return {k:v for k,v in out.items() if v}

    def lb_effective(self,s,key):
        return self.lb_biz_map(s).get(key)

    def lb_scope(self,s,node_id):
        return [node_id]+[n['id'] for n in self.cat_descendants(s,self.cat_find(s,node_id))]

    def lb_tree_conflicts(self,s):
        """Nút mang nghiệp vụ riêng khác nghiệp vụ hiệu lực của cha (con không được khác cha)."""
        by={n['id']:n for n in s.get('categories',[])};biz=self.lb_biz_map(s);bad=[]
        for n in by.values():
            own=(n.get('business') or {}).get('type')
            if own and n['parent'] in by and biz.get(n['parent']) and biz[n['parent']][0]!=own:bad.append(n['id'])
        return bad

    # ---- nguồn và phạm vi (R205) ------------------------------------------------------------
    def lb_sources(self,s):
        """Nguồn nhận được chi tiết: giao dịch ngân hàng và dòng lịch sử cũ đang hiệu lực."""
        out={t['id']:t for t in s['transactions']}
        for t,_ in self.legacy_items(s):out[t['id']]=t
        return out

    def lb_groups(self,s,biz=None):
        """{nguồn: dict(t, groups {(danh mục, người): số}, issues [...], legacy [...])} cho mọi nguồn có tiền trong danh mục nghiệp vụ."""
        biz=self.lb_biz_map(s) if biz is None else biz;profiles={p['id']:p for p in s['profiles']};out={};loans={l['id']:l for l in s.get('loans',[])}
        if not biz:return out
        for t,p in self.cat_parts(s):
            key=self.cat_target(p);b=biz.get(key)
            if not b:continue
            rec=out.setdefault(t['id'],dict(t=t,groups={},issues=[],legacy=[],amount=Decimal(0),legacy_amount=Decimal(0)))
            amount=D(p['amount']);prof=profiles.get(p.get('profile'))
            if prof is None:rec['issues'].append(dict(code='NO_PERSON',category=key,amount=amount));rec['amount']+=amount
            elif prof['kind']=='PERSON':
                lo=p.get('loan') or None;ln=loans.get(lo) if lo else None
                if lo and not (ln and ln['person']==prof['id'] and ln['direction']==b[0]):rec['issues'].append(dict(code='LOAN_MISMATCH',category=key,profile=prof['id'],amount=amount));rec['amount']+=amount
                else:g=(key,prof['id'],lo);rec['groups'][g]=rec['groups'].get(g,Decimal(0))+amount;rec['amount']+=amount
            elif prof['kind']=='LOAN':
                sd=(prof.get('debt_setup') or {}).get('direction')
                if p['category'] not in {'principal','interest'}:rec['issues'].append(dict(code='LEGACY_NOT_COUNTED',category=key,profile=prof['id'],amount=amount));rec['amount']+=amount
                elif sd==b[0]:rec['legacy'].append(dict(category=key,loan=prof['id'],amount=amount));rec['legacy_amount']+=amount
                else:rec['issues'].append(dict(code='LEGACY_DIRECTION' if sd else 'LEGACY_NO_SETUP',category=key,profile=prof['id'],amount=amount));rec['amount']+=amount
            else:rec['issues'].append(dict(code='NOT_PERSON',category=key,profile=prof['id'],amount=amount));rec['amount']+=amount
        return out

    def lb_detail(self,s,source):
        return next((x for x in lb_state(s)['loan_details'] if x['source']==source),None)

    def lb_current(self,det):
        v=(det or {}).get('versions') or []
        return v[-1] if v and v[-1]['status']=='POSTED' else None

    def lb_line_group(self,groups,l):
        """Nhóm (danh mục, người, khoản) của một dòng chi tiết; phần tiền cũ không chọn khoản là nhóm (danh mục, người, None)."""
        k=(l.get('category'),l.get('person'),l.get('loan'))
        return k if k in groups else (k[0],k[1],None) if (k[0],k[1],None) in groups else k

    def lb_status(self,s,rec,det,loans_of):
        """Trạng thái một nguồn: POSTED / PENDING (kèm lý do) / LEGACY_LINK."""
        cur=self.lb_current(det);reasons=[i['code'] for i in rec['issues']]
        if rec['groups']:
            if cur:
                sums={}
                for l in cur['lines']:g=self.lb_line_group(rec['groups'],l);sums[g]=sums.get(g,Decimal(0))+D(l['amount'])
                if sums!=rec['groups']:reasons.append('MISMATCH')
            else:
                for (key,person,lo),_ in rec['groups'].items():
                    if not lo and not loans_of.get(person):reasons.append('NO_LOAN')
                reasons.append('NOT_DETAILED')
        if det and det.get('draft'):reasons.append('DRAFT')
        reasons=list(dict.fromkeys(reasons))
        blocking=[r for r in reasons if r!='DRAFT' or not cur]
        status='PENDING' if blocking else ('POSTED' if cur else 'LEGACY_LINK')
        return status,reasons

    # ---- sổ từng khoản (R206–R209) ---------------------------------------------------------
    def lb_principal_sign(self,loan,direction):
        """+1 giải ngân / nhận tiền vay, −1 thu gốc / trả gốc."""
        return 1 if (loan['direction']=='RECEIVABLE')==(direction=='OUT') else -1

    def lb_loan_lines(self,s,details=None):
        """{khoản: [(nguồn, ngày, chiều tiền, dòng)]} của các bản đã ghi."""
        srcs=self.lb_sources(s);out={}
        for det in (lb_state(s)['loan_details'] if details is None else details):
            cur=self.lb_current(det);t=srcs.get(det['source'])
            if not cur or t is None:continue
            direction='IN' if D(t['signed_amount'])>0 else 'OUT'
            for l in cur['lines']:out.setdefault(l['loan'],[]).append((t,t['date'],direction,l))
        return out

    def lb_ledger(self,loan,lines,waivers,as_of):
        """Một khoản: dư gốc, lãi theo điều khoản, thực thu/trả, miễn giảm, còn thiếu, môi giới — tới ngày xem."""
        with localcontext() as ctx:
            ctx.prec=80
            events={};paid=Decimal(0);broker_paid=Decimal(0);disb=Decimal(0);repay=Decimal(0);entries=[];txs=set()
            for t,when,direction,l in sorted(lines,key=lambda x:(x[1],x[0].get('order',0))):
                amount=D(l['amount'])
                if when>as_of:continue
                txs.add(t['id']);e=events.setdefault(when,dict(disb=Decimal(0),repay=Decimal(0)))
                if l['component']=='principal':
                    if self.lb_principal_sign(loan,direction)>0:e['disb']+=amount;disb+=amount
                    else:e['repay']+=amount;repay+=amount
                elif l['component']=='interest':paid+=amount
                else:broker_paid+=amount
                entries.append(dict(source=t['id'],date=when,reference=t.get('reference'),legacy=bool(t.get('legacy')),direction=direction,component=l['component'],
                    label=COMPONENTS[(loan['direction'],direction)].get(l['component']),amount=S(amount)))
            act=[w for w in waivers if w['status']=='ACTIVE' and w['date']<=as_of];waived=sum((D(w['amount']) for w in act),Decimal(0))
            broker=loan.get('broker');raw,braw,closing,segs=lb_accrue(events,loan['rate'],as_of,broker['rate'] if broker else None)
            accrued=rnd(raw);bterms=rnd(braw) if braw is not None else None
            out=dict(principal=S(closing),disbursed=S(disb),repaid=S(repay),interest_accrued=S(accrued),interest_paid=S(paid),waived=S(waived),
                interest_outstanding=S(accrued-paid-waived),broker_terms=S(bterms) if bterms is not None else None,spread_terms=S(accrued-bterms) if bterms is not None else None,
                broker_paid=S(broker_paid),broker_over=bool(broker and bterms is not None and broker_paid>bterms),segments=segs,entries=entries,sources=len(txs),
                last_event=max(events) if events else None)
            return out

    def lb_check(self,s,loan,lines,waivers):
        """Chặn vượt nghĩa vụ tại mọi ngày có phát sinh (R208) và nguồn trước ngày theo dõi."""
        with localcontext() as ctx:
            ctx.prec=80
            for t,when,_,l in lines:
                require(when>=loan['tracking_date'],f"Khoản {loan['code']} theo dõi từ {self.lb_day(loan['tracking_date'])}; nguồn {t.get('reference') or ''} ngày {self.lb_day(when)} trước ngày theo dõi. Sửa ngày theo dõi của khoản hoặc chọn khoản khác.")
            dates=sorted({x[1] for x in lines}|{w['date'] for w in waivers if w['status']=='ACTIVE'})
            closing=Decimal(0);cum=Decimal(0)
            for when in dates:
                day_lines=[x for x in lines if x[1]==when]
                disb=sum((D(l['amount']) for _,_,dr,l in day_lines if l['component']=='principal' and self.lb_principal_sign(loan,dr)>0),Decimal(0))
                rep=sum((D(l['amount']) for _,_,dr,l in day_lines if l['component']=='principal' and self.lb_principal_sign(loan,dr)<0),Decimal(0))
                require(rep<=closing+disb,f"{COMPONENTS[(loan['direction'],'IN' if loan['direction']=='RECEIVABLE' else 'OUT')]['principal']} {self.lb_money(rep)} ngày {self.lb_day(when)} vượt dư gốc {self.lb_money(closing+disb)} của khoản {loan['code']}. Không tạo dư âm hay tiền trả trước: phân loại phần thừa sang danh mục khác rồi ghi lại.")
                closing=closing+disb-rep
                cum+=sum((D(l['amount']) for _,_,_,l in day_lines if l['component']=='interest'),Decimal(0))+sum((D(w['amount']) for w in waivers if w['status']=='ACTIVE' and w['date']==when),Decimal(0))
                accrued=self.lb_ledger(loan,lines,[],when)['interest_accrued']
                require(cum<=D(accrued),f"Lãi đã {'thu' if loan['direction']=='RECEIVABLE' else 'trả'} cộng miễn giảm tới {self.lb_day(when)} là {self.lb_money(cum)}, vượt lãi tính theo điều khoản {self.lb_money(accrued)} của khoản {loan['code']}. Chưa hỗ trợ trả lãi trước: giảm số lãi hoặc phân loại phần thừa sang danh mục khác.")

    def lb_day(self,x):return _d(x).strftime('%d/%m/%Y')
    def lb_money(self,x):return f"{int(D(x)):,}".replace(',','.')

    def lb_today(self):return date.today().isoformat()

    # ---- sổ khoản vay (R210, R211) -----------------------------------------------------------
    def loan_book(self,s,as_of=None,category=None):
        from .p01 import day
        with localcontext() as ctx:
            ctx.prec=80
            s=lb_state(s);today=self.lb_today();lines=self.lb_loan_lines(s)
            # ngày xem mặc định: hôm nay, nhưng không trước phát sinh cuối đã ghi (không giấu số đã ghi)
            as_of=day(as_of) if as_of else max([today]+[x[1] for ls in lines.values() for x in ls]+[w['date'] for w in s['loan_waivers'] if w['status']=='ACTIVE'])
            biz=self.lb_biz_map(s);groups=self.lb_groups(s,biz);profiles={p['id']:p for p in s['profiles']}
            loans_of={}
            for l in s['loans']:loans_of.setdefault(l['person'],[]).append(l)
            details={d['source']:d for d in s['loan_details']}
            sources={};pending=[];p_in=p_out=Decimal(0);scope_pending=set()
            for sid,rec in groups.items():
                t=rec['t'];det=details.get(sid);status,reasons=self.lb_status(s,rec,det,loans_of);direction='IN' if D(t['signed_amount'])>0 else 'OUT'
                persons=sorted({p for (_,p,_) in rec['groups']});cats=sorted({k for (k,_,_) in rec['groups']}|{i['category'] for i in rec['issues']}|{x['category'] for x in rec['legacy']})
                info=dict(status=status,reasons=reasons,reason_text=[PENDING_TEXT[r] for r in reasons],direction=direction,date=t['date'],reference=t.get('reference'),
                    description=t.get('description'),account=t.get('account'),legacy=bool(t.get('legacy')),amount=S(rec['amount']),legacy_amount=S(rec['legacy_amount']),persons=persons,
                    person_names=[profiles[p]['name'] for p in persons if p in profiles],categories=cats,paths=[self.cat_path(s,c) for c in cats],
                    business=sorted({biz[c][0] for c in cats if c in biz}),has_draft=bool(det and det.get('draft')),editing=bool(det and det.get('draft') and self.lb_current(det)),
                    version=len((det or {}).get('versions') or []))
                sources[sid]=info
                if status=='PENDING':
                    pending.append(dict(source=sid,**info))
                    if direction=='IN':p_in+=rec['amount']
                    else:p_out+=rec['amount']
                    for p in persons:
                        for k in cats:
                            if k in biz:scope_pending.add((p,biz[k][0]))
            waivers={}
            for w in s['loan_waivers']:waivers.setdefault(w['loan'],[]).append(w)
            drafts_of={}
            for det in s['loan_details']:
                for l in (det.get('draft') or {}).get('lines',[]):drafts_of.setdefault(l.get('loan'),set()).add(det['source'])
            rows=[]
            for loan in s['loans']:
                led=self.lb_ledger(loan,lines.get(loan['id'],[]),waivers.get(loan['id'],[]),as_of)
                final=self.lb_ledger(loan,lines.get(loan['id'],[]),waivers.get(loan['id'],[]),max(today,as_of,*(x[1] for x in lines.get(loan['id'],[]))) if lines.get(loan['id']) else max(today,as_of))
                caution=(loan['person'],loan['direction']) in scope_pending
                blocker=None
                if loan['status']=='COMPLETED':blocker='Khoản đã hoàn tất.'
                elif not final['last_event']:blocker='Khoản chưa có phát sinh.'
                elif D(final['principal'])!=0:blocker=f"Dư gốc còn {self.lb_money(final['principal'])}."
                elif D(final['interest_outstanding'])!=0:blocker=f"Lãi còn thiếu {self.lb_money(final['interest_outstanding'])}; thu đủ hoặc miễn giảm trước khi hoàn tất."
                elif caution:blocker=f"Còn giao dịch chờ chi tiết nghiệp vụ của {profiles[loan['person']]['name']} cùng chiều {DIRS[loan['direction']]['name']}; xử lý danh sách chờ trước."
                elif drafts_of.get(loan['id']):blocker='Còn nháp chi tiết nghiệp vụ gắn khoản này; ghi hoặc bỏ nháp trước.'
                node=next((n for n in s['categories'] if n['id']==loan['category']),None)
                rows.append(dict(id=loan['id'],code=loan['code'],name=loan['name'],person=loan['person'],person_name=profiles.get(loan['person'],{}).get('name'),direction=loan['direction'],
                    direction_name=DIRS[loan['direction']]['name'],side=DIRS[loan['direction']]['side'],category=loan['category'],category_path=self.cat_path(s,loan['category']) if node else None,
                    rate=loan['rate'],broker=copy.deepcopy(loan.get('broker')),tracking_date=loan['tracking_date'],due_date=loan.get('due_date'),status=loan['status'],
                    overdue=bool(loan.get('due_date') and as_of>loan['due_date'] and (D(led['principal'])>0 or D(led['interest_outstanding'])>0) and loan['status']!='COMPLETED'),
                    settled=bool(final['last_event'] and D(final['principal'])==0 and D(final['interest_outstanding'])==0),can_complete=blocker is None,complete_blocker=blocker,caution=caution,
                    terms_locked=bool(self.lb_terms_locked(s,loan)),terms_lock_reason=self.lb_terms_locked(s,loan),
                    waivers=copy.deepcopy(waivers.get(loan['id'],[])),history=copy.deepcopy(loan.get('history',[])),completion=copy.deepcopy(loan.get('completion')),**led))
            # theo danh mục: dòng đã ghi cộng vào danh mục và mọi danh mục cha tới nút gắn nghiệp vụ, giao dịch đếm một lần mỗi danh mục
            by_cat={};srcs=self.lb_sources(s);loan_by={l['id']:l for l in s['loans']}
            for det in s['loan_details']:
                cur=self.lb_current(det);t=srcs.get(det['source'])
                if not cur or t is None or t['date']>as_of:continue
                direction='IN' if D(t['signed_amount'])>0 else 'OUT'
                for l in cur['lines']:
                    loan=loan_by.get(l['loan'])
                    if loan is None:continue
                    chain=self.cat_chain(s,l['category']) if any(n['id']==l['category'] for n in s['categories']) else [l['category']]
                    origin=(biz.get(l['category']) or (None,None))[1]
                    keys=chain[:chain.index(origin)+1] if origin in chain else chain[:1]
                    for k in keys:
                        c=by_cat.setdefault(k,dict(category=k,path=self.cat_path(s,k),direction=loan['direction'],disbursed=Decimal(0),repaid=Decimal(0),interest_cash=Decimal(0),broker_paid=Decimal(0),tx=set(),loans=set(),people=set()))
                        a=D(l['amount']);c['tx'].add(t['id']);c['loans'].add(loan['id']);c['people'].add(loan['person'])
                        if l['component']=='principal':
                            if self.lb_principal_sign(loan,direction)>0:c['disbursed']+=a
                            else:c['repaid']+=a
                        elif l['component']=='interest':c['interest_cash']+=a
                        else:c['broker_paid']+=a
            by_category=[dict(category=c['category'],path=c['path'],direction=c['direction'],disbursed=S(c['disbursed']),repaid=S(c['repaid']),principal=S(c['disbursed']-c['repaid']),
                interest_cash=S(c['interest_cash']),broker_paid=S(c['broker_paid']),transactions=len(c['tx']),loans=len(c['loans']),people=len(c['people'])) for c in by_cat.values()]
            by_account={}
            for sid,rec in groups.items():
                t=rec['t']
                if t.get('legacy'):continue
                total=rec['amount']+sum((x['amount'] for x in rec['legacy']),Decimal(0));a=by_account.setdefault(t['account'],dict(in_=Decimal(0),out=Decimal(0)))
                a['in_' if D(t['signed_amount'])>0 else 'out']+=total
            legacy=self.debt_register(s)
            people=[]
            for pid in sorted({l['person'] for l in s['loans']},key=lambda x:profiles.get(x,{}).get('name','')):
                own=[r for r in rows if r['person']==pid];blk={}
                for dname in DIRS:
                    rs=[r for r in own if r['direction']==dname]
                    blk[dname]=dict(loans=[r['id'] for r in rs],count=len(rs),principal=S(sum((D(r['principal']) for r in rs),Decimal(0))),
                        interest_outstanding=S(sum((D(r['interest_outstanding']) for r in rs),Decimal(0))),sources=len({e['source'] for r in rs for e in r['entries']})) if rs else None
                people.append(dict(person=pid,name=profiles.get(pid,{}).get('name'),receivable=blk['RECEIVABLE'],payable=blk['PAYABLE'],legacy_loans=[x['name'] for x in legacy['loans'] if x['party']==pid]))
            if category:
                scope=set(self.lb_scope(s,category))
                rows=[r for r in rows if r['category'] in scope or any(e['source'] in {sid for sid,i in sources.items() if set(i['categories'])&scope} for e in r['entries'])]
                pending=[p for p in pending if set(p['categories'])&scope]
            posted_tx={e['source'] for r in rows for e in r['entries']}
            summary=dict(receivable=S(sum((D(r['principal']) for r in rows if r['direction']=='RECEIVABLE'),Decimal(0))),payable=S(sum((D(r['principal']) for r in rows if r['direction']=='PAYABLE'),Decimal(0))),
                interest_outstanding_receivable=S(sum((D(r['interest_outstanding']) for r in rows if r['direction']=='RECEIVABLE'),Decimal(0))),
                interest_outstanding_payable=S(sum((D(r['interest_outstanding']) for r in rows if r['direction']=='PAYABLE'),Decimal(0))),
                people=len({r['person'] for r in rows}),loans=len(rows),transactions=len(posted_tx),
                legacy_receivable=S(sum((D(p['receivable']) for p in legacy['people']),Decimal(0))),legacy_payable=S(sum((D(p['payable']) for p in legacy['people']),Decimal(0))),legacy_loans=len(legacy['loans']))
            return dict(as_of=as_of,today=today,future=as_of>today,loans=rows,people=people,by_category=by_category,
                by_account={k:{'in':S(v['in_']),'out':S(v['out'])} for k,v in by_account.items()},summary=summary,
                pending=dict(count=len(pending),**{'in':S(p_in),'out':S(p_out)},items=sorted(pending,key=lambda x:(x['date'],x['reference'] or ''))),sources=sources,
                categories=[dict(id=k,path=self.cat_path(s,k),type=v[0],own=v[1]==k) for k,v in biz.items() if self.cat_find(s,k)['status']=='ACTIVE'],
                components={f'{a}_{b}':v for (a,b),v in COMPONENTS.items()},directions=DIRS)

    # ---- dấu vân tay & bất biến (FR-005, research D6) ----------------------------------------
    def lb_fingerprint(self,s):
        biz=self.lb_biz_map(s)
        if not (s.get('loan_details') or s.get('loans') or biz):return None
        groups=self.lb_groups(s,biz);posted={};drafts={};pairs=set()
        t=lambda k:(biz.get(k) or (None,))[0]
        for det in s['loan_details']:
            cur=self.lb_current(det);rec=groups.get(det['source'])
            if cur:
                posted[det['source']]=sorted((k,p,lo or '',str(a),t(k)) for (k,p,lo),a in rec['groups'].items()) if rec else None
                pairs|={(l['category'],l['person']) for l in cur['lines']}
            dl=(det.get('draft') or {}).get('lines',[])
            pairs|={(l.get('category'),l.get('person')) for l in dl if l.get('category') and l.get('person')}
            drafts[det['source']]=sorted({(c,t(c)) for c in {l['category'] for l in (cur or {}).get('lines',[])}|{l.get('category') for l in dl if l.get('category')}})
        loans=sorted((l['id'],t(l['category'])) for l in s['loans']);pairs|={(l['category'],l['person']) for l in s['loans']}
        raw,bad=self.lb_part_audit(s,biz)
        return dict(posted=posted,drafts=drafts,loans=loans,members=sorted((c,p,self.is_member(s,c,p)) for c,p in pairs),tree=self.lb_tree_conflicts(s),raw=raw,bad=bad)

    # ---- người + khoản khi phân loại (PO review P2) -----------------------------------------
    def lb_part_check(self,s,part,biz=None,completed=True):
        """(mã, thông báo) nếu phần tiền (thô hoặc hiệu lực) vi phạm quy tắc người + khoản của danh mục nghiệp vụ, ngược lại None."""
        biz=self.lb_biz_map(s) if biz is None else biz;eff=self.cat_eff(s,part) if 'own_profile' not in part and 'own_node' not in part else part
        key=self.cat_target(eff);b=biz.get(key);lo=eff.get('loan') or None
        path=lambda:self.cat_path(s,key) if any(n['id']==key for n in s.get('categories',[])) else key
        if not b:return ('LOAN_NO_BUSINESS',f"Danh mục {path()} không mang nghiệp vụ Cho vay/Đi vay; bỏ chọn khoản vay cho phần tiền này.") if lo else None
        name=DIRS[b[0]]['name'];prof=next((x for x in s['profiles'] if x['id']==eff.get('profile')),None) if eff.get('profile') else None
        if prof is None:return ('NO_PERSON',f"Danh mục {path()} mang nghiệp vụ {name}: chọn Người và khoản vay có sẵn cho phần tiền này. Chỉ phần gốc / lãi / phí môi giới được để sau.")
        if prof['kind']!='PERSON':return ('NOT_PERSON',f"Danh mục {path()} mang nghiệp vụ vay: chỉ gắn đối tượng loại Người, kèm khoản vay của người đó.")
        if not lo:return ('NO_LOAN_LINK',f"Danh mục {path()} mang nghiệp vụ {name}: chọn khoản vay của {prof['name']} (một người nhiều khoản thì tách phần theo từng khoản). Chưa có khoản: tạo ở Công nợ → + Khoản vay mới. Chi tiết gốc / lãi để sau được.")
        ln=next((x for x in s.get('loans',[]) if x['id']==lo),None)
        if not ln or ln['person']!=prof['id'] or ln['direction']!=b[0]:return ('LOAN_MISMATCH',f"Khoản vay đã chọn không thuộc {prof['name']} hoặc khác chiều {name} của danh mục {path()}.")
        if completed and ln['status']=='COMPLETED':return ('LOAN_COMPLETED',f"Khoản {ln['code']} đã hoàn tất; mở lại khoản trước khi phân loại thêm tiền vào khoản này.")
        return None

    def lb_part_audit(self,s,biz):
        """Tập phần tiền thô và tập phần vi phạm (thô, mã, thông báo) — để bất biến chặn phần vi phạm mới ở mọi đường ghi."""
        raw=set();bad={}
        for t,p in self.cat_parts(s):
            k=(t['id'],p.get('own_category',p['category']),p.get('own_node',p.get('node')) or None,p.get('own_profile',p.get('profile')) or None,p.get('loan') or None,str(p['amount']))
            raw.add(k)
            if not p.get('loan') and not biz.get(self.cat_target(p)):continue
            r=self.lb_part_check(s,p,biz,completed=False)
            if r:bad[(k,r[0])]=(t.get('reference') or '',r[1])
        return raw,bad

    def lb_guard(self,s,before):
        after=self.lb_fingerprint(s)
        if after is None and before is None:
            require(not self.lb_tree_conflicts(s),'Danh mục con không được khác nghiệp vụ của danh mục cha; gỡ nghiệp vụ riêng của nhánh trước.')
            return
        if before is not None and after is not None:
            for (k,code),(ref_,msg) in after['bad'].items():
                if (k,code) in before['bad']:continue
                # phần y nguyên có từ trước (ngoại lệ lịch sử) được giữ và vào danh sách chờ; phần mới/đổi, hay khoản đã chọn bị lệch, thì chặn
                require(k in before['raw'] and code not in {'LOAN_MISMATCH','LOAN_NO_BUSINESS'},f"Phần tiền {ref_}: {msg}")
        empty=dict(posted={},drafts={},loans=[],members=[],tree=[],raw=set(),bad={})
        before=before or empty;after=after or empty;srcs=self.lb_sources(s)
        ref=lambda sid:(srcs.get(sid) or {}).get('reference') or sid[:8]
        for sid,g in before['posted'].items():
            require(after['posted'].get(sid)==g,f"Giao dịch {ref(sid)} đã ghi nghiệp vụ vay; thao tác này làm đổi phần tiền, đối tượng hoặc nghiệp vụ của nó. Mở «Chi tiết nghiệp vụ» của giao dịch (ở lịch sử tài khoản hoặc Công nợ → Sổ chi tiết), hủy có lý do rồi làm lại.")
        for sid,g in before['drafts'].items():
            require(after['drafts'].get(sid)==g,f"Nháp chi tiết nghiệp vụ của {ref(sid)} dùng danh mục bị đổi nghiệp vụ; bỏ nháp trước.")
        lb={l['id']:l for l in s['loans']};now_loans=dict(after['loans'])
        for lid,typ in before['loans']:
            require(now_loans.get(lid)==typ,f"Khoản vay {lb[lid]['code'] if lid in lb else ''} được tạo từ danh mục này; thao tác làm đổi nghiệp vụ của danh mục nơi tạo khoản.")
        names={p['id']:p['name'] for p in s['profiles']}
        for (c,p,m) in before['members']:
            if m:require(self.is_member(s,c,p),f"{names.get(p,'Đối tượng')} còn khoản vay hoặc chi tiết nghiệp vụ ở danh mục {self.cat_path(s,c)}; không gỡ, chuyển hay gộp khỏi danh mục này. Hủy chi tiết nghiệp vụ trước nếu thật sự cần.")
        require(not (set(after['tree'])-set(before['tree'])),'Danh mục con không được khác nghiệp vụ của danh mục cha; gỡ nghiệp vụ riêng của nhánh trước.')

    # ---- xem trước gắn nghiệp vụ -----------------------------------------------------------
    def lb_category_preview(self,d,s=None):
        with localcontext() as ctx:
            ctx.prec=80
            s=lb_state(copy.deepcopy(s or self.state()));key=d.get('category');typ=d.get('type')
            require(key not in ROOTS,'Chỉ gắn nghiệp vụ vào danh mục bạn tạo; không gắn vào danh mục gốc hệ thống.')
            node=self.cat_find(s,key);require(typ in DIRS,'Chọn Cho vay hoặc Đi vay.')
            biz=self.lb_biz_map(s);blocks=[];own=(node.get('business') or {}).get('type')
            if node['status']!='ACTIVE':blocks.append(dict(code='ARCHIVED',message='Danh mục đang lưu trữ; khôi phục trước khi gắn nghiệp vụ.'))
            parent=biz.get(node['parent']) if node['parent'] else None
            if parent:
                blocks.append(dict(code='INHERITED' if parent[0]==typ else 'PARENT_DIFFERENT',message=(f"Danh mục đã kế thừa {DIRS[parent[0]]['name']} từ {self.cat_path(s,parent[1])}." if parent[0]==typ else f"Danh mục cha {self.cat_path(s,parent[1])} mang {DIRS[parent[0]]['name']}; danh mục con không được khác nghiệp vụ của cha.")))
            if own==typ:blocks.append(dict(code='SAME',message='Danh mục đã gắn nghiệp vụ này.'))
            elif own:blocks.append(dict(code='CHANGE',message=f"Danh mục đang gắn {DIRS[own]['name']}; gỡ nghiệp vụ trước (chỉ được khi chưa có chi tiết hay khoản vay)."))
            scope=self.lb_scope(s,key)
            clash=[n for n in s['categories'] if n['id'] in scope[1:] and (n.get('business') or {}).get('type') not in (None,typ)]
            if clash:blocks.append(dict(code='CHILD_DIFFERENT',message='Nhánh con đang mang nghiệp vụ khác: '+'; '.join(f"{self.cat_path(s,n['id'])} ({DIRS[n['business']['type']]['name']})" for n in clash)+'. Không ghi đè; gỡ hoặc tách nhánh trước.'))
            sim=copy.deepcopy(s);self.cat_find(sim,key)['business']=dict(type=typ)
            book=self.loan_book(sim) if not clash else None
            valid=dict(count=0,in_=Decimal(0),out=Decimal(0));missing=dict(count=0,in_=Decimal(0),out=Decimal(0));conflicts=[]
            if book:
                sset=set(scope)
                for sid,i in book['sources'].items():
                    if not set(i['categories'])&sset:continue
                    bad=[r for r in i['reasons'] if r in {'NOT_PERSON','LEGACY_DIRECTION','LEGACY_NO_SETUP','LEGACY_NOT_COUNTED'}]
                    if bad:conflicts.append(dict(source=sid,reference=i['reference'],date=i['date'],amount=i['amount'],code=bad[0],message=PENDING_TEXT[bad[0]],paths=i['paths']))
                    elif i['status']=='PENDING':missing['count']+=1;missing['in_' if i['direction']=='IN' else 'out']+=D(i['amount'])
                    else:valid['count']+=1;valid['in_' if i['direction']=='IN' else 'out']+=D(i['amount'])+D(i['legacy_amount'])
            profiles={p['id']:p for p in s['profiles']}
            non_person=[dict(profile=e['profile'],name=profiles[e['profile']]['name'],kind=profiles[e['profile']]['kind'],path=self.cat_path(s,e['category'])) for e in s['category_objects'] if e['status']=='ACTIVE' and e['category'] in scope and e['profile'] in profiles and profiles[e['profile']]['kind']!='PERSON']
            out=dict(category=key,path=self.cat_path(s,key),type=typ,type_name=DIRS[typ]['name'],scope=[dict(id=c,path=self.cat_path(s,c)) for c in scope],
                valid={'count':valid['count'],'in':S(valid['in_']),'out':S(valid['out'])} if book else None,missing={'count':missing['count'],'in':S(missing['in_']),'out':S(missing['out'])} if book else None,
                conflicts=conflicts,non_person=non_person,blocks=blocks,can_commit=not blocks)
            out['review_token']=digest({k:out[k] for k in ('category','type','scope','valid','missing','conflicts','non_person','blocks')})
            return out

    # ---- xem trước chi tiết nghiệp vụ --------------------------------------------------------
    def lb_parse_lines(self,s,lines,strict=True):
        from .p01 import money
        require(isinstance(lines,list) and len(lines)<=50,'Tối đa 50 dòng chi tiết.')
        out=[];loans={l['id']:l for l in s['loans']}
        for l in lines:
            require(isinstance(l,dict),'Dòng chi tiết không hợp lệ.')
            row=dict(category=l.get('category'),person=l.get('person'),loan=l.get('loan') or None,component=l.get('component') or None,amount=None)
            if l.get('amount') not in (None,''):
                a=money(l['amount']);require(a>0,'Số tiền mỗi dòng phải dương.');row['amount']=S(a)
            if strict:
                require(row['loan'] in loans,'Mỗi dòng cần chọn khoản vay.');require(row['component'] in {'principal','interest','broker'},'Mỗi dòng cần chọn thành phần.');require(row['amount'],'Mỗi dòng cần số tiền.')
            out.append(row)
        return out

    def lb_detail_preview(self,d,s=None):
        with localcontext() as ctx:
            ctx.prec=80
            s=lb_state(copy.deepcopy(s or self.state()));sid=d.get('source');srcs=self.lb_sources(s);t=srcs.get(sid)
            require(t is not None,'Không tìm thấy giao dịch hoặc dòng lịch sử cũ đang hiệu lực.')
            biz=self.lb_biz_map(s);rec=self.lb_groups(s,biz).get(sid)
            require(rec is not None,'Giao dịch này không có tiền trong danh mục mang nghiệp vụ vay. Phân loại vào danh mục có nghiệp vụ trước.')
            det=self.lb_detail(s,sid);cur=self.lb_current(det);direction='IN' if D(t['signed_amount'])>0 else 'OUT'
            profiles={p['id']:p for p in s['profiles']};blocks=[];warnings=[]
            if d.get('lines') is not None:lines=self.lb_parse_lines(s,d['lines'],strict=False)
            else:lines=copy.deepcopy((det or {}).get('draft',{}) and det['draft']['lines'] or (cur or {}).get('lines',[]))
            for i in rec['issues']:blocks.append(dict(code=i['code'],message=f"Phần {self.lb_money(i['amount'])} ở {self.cat_path(s,i['category'])}: {PENDING_TEXT[i['code']]}. Sửa phân loại (chọn Người là thành viên) trước."))
            loans={l['id']:l for l in s['loans']};groups=[]
            for (key,pid,lo),amount in sorted(rec['groups'].items(),key=lambda kv:(self.cat_path(s,kv[0][0]),profiles[kv[0][1]]['name'],loans[kv[0][2]]['code'] if kv[0][2] else '')):
                typ=biz[key][0];opts=[loans[lo]] if lo else [l for l in s['loans'] if l['person']==pid and l['direction']==typ]
                got=sum((D(l['amount']) for l in lines if self.lb_line_group(rec['groups'],l)==(key,pid,lo) and l.get('amount')),Decimal(0))
                groups.append(dict(category=key,path=self.cat_path(s,key),person=pid,person_name=profiles[pid]['name'],loan=lo,loan_code=loans[lo]['code'] if lo else None,amount=S(amount),business=typ,business_name=DIRS[typ]['name'],
                    allocated=S(got),remaining=S(amount-got),components=COMPONENTS[(typ,direction)],
                    loans=[dict(id=l['id'],code=l['code'],name=l['name'],status=l['status'],broker=bool(l.get('broker')),tracking_date=l['tracking_date']) for l in opts]))
                if not opts:blocks.append(dict(code='NO_LOAN',message=f"{profiles[pid]['name']} chưa có khoản {DIRS[typ]['name']}; tạo khoản vay trước khi liên kết."))
                if got!=amount:blocks.append(dict(code='INCOMPLETE',message=f"{profiles[pid]['name']}{' · '+loans[lo]['code'] if lo else ''} · {self.cat_path(s,key)}: đã phân bổ {self.lb_money(got)} / {self.lb_money(amount)}, còn {self.lb_money(amount-got)}."))
            keys={(g['category'],g['person'],g['loan']) for g in groups}
            for l in lines:
                if self.lb_line_group(rec['groups'],l) not in keys:
                    fixed=[g for g in groups if g['category']==l['category'] and g['person']==l['person']]
                    blocks.append(dict(code='LINE_GROUP',message=f"Dòng dùng khoản khác khoản đã chọn khi phân loại ({', '.join(g['loan_code'] for g in fixed)}); chọn đúng khoản hoặc Sửa phân loại." if fixed else 'Có dòng không thuộc phần tiền nào của giao dịch; xóa dòng đó.'));continue
                loan=loans.get(l['loan'])
                if not loan or not l['component'] or not l['amount']:blocks.append(dict(code='LINE_EMPTY',message='Mỗi dòng cần khoản vay, thành phần và số tiền.'));continue
                typ=biz[l['category']][0]
                if loan['person']!=l['person'] or loan['direction']!=typ:blocks.append(dict(code='LINE_LOAN',message=f"Khoản {loan['code']} không thuộc {profiles[l['person']]['name']} hoặc khác chiều {DIRS[typ]['name']}."));continue
                if l['component'] not in COMPONENTS[(typ,direction)]:blocks.append(dict(code='LINE_COMPONENT',message=f"Tiền {'vào' if direction=='IN' else 'ra'} của khoản {DIRS[typ]['name']} không thể là \"{ {'principal':'gốc','interest':'lãi','broker':'phí môi giới'}[l['component']] }\"; chọn: {', '.join(COMPONENTS[(typ,direction)].values())}."));continue
                if l['component']=='broker' and not loan.get('broker'):blocks.append(dict(code='LINE_BROKER',message=f"Khoản {loan['code']} không có môi giới."));continue
                if loan['status']=='COMPLETED':blocks.append(dict(code='COMPLETED',message=f"Khoản {loan['code']} đã hoàn tất; mở lại khoản trước khi ghi thêm."))
            impact=[]
            if not blocks or all(b['code'] in {'INCOMPLETE'} for b in blocks):
                sim=copy.deepcopy(s);sdet=self.lb_detail(sim,sid)
                if sdet is None:sdet=dict(source=sid,kind='LEGACY' if t.get('legacy') else 'BANK',versions=[],draft=None);sim['loan_details'].append(sdet)
                sdet['versions'].append(dict(n=len(sdet['versions'])+1,status='POSTED',lines=[l for l in lines if l.get('loan') in loans and l.get('amount')],at='',reason=''))
                before_lines=self.lb_loan_lines(s);after_lines=self.lb_loan_lines(sim);wv={}
                for w in s['loan_waivers']:wv.setdefault(w['loan'],[]).append(w)
                touched=sorted({l['loan'] for l in lines if l.get('loan') in loans}|{l['loan'] for l in (cur or {}).get('lines',[])},key=lambda x:loans[x]['code'])
                for lid in touched:
                    loan=loans[lid];b=self.lb_ledger(loan,before_lines.get(lid,[]),wv.get(lid,[]),t['date']);a=self.lb_ledger(loan,after_lines.get(lid,[]),wv.get(lid,[]),t['date'])
                    pick=lambda x:{k:x[k] for k in ('principal','interest_accrued','interest_paid','waived','interest_outstanding','broker_terms','spread_terms','broker_paid')}
                    repaying=any(l['loan']==lid and l['component']=='principal' and self.lb_principal_sign(loan,direction)<0 for l in lines if l.get('loan'))
                    err=None
                    try:self.lb_check(sim,loan,after_lines.get(lid,[]),wv.get(lid,[]))
                    except ValidationError as e:err=str(e);blocks.append(dict(code='OBLIGATION',message=err))
                    w=[]
                    if a['broker_over']:w.append(f"Đã trả môi giới {self.lb_money(a['broker_paid'])} vượt phần theo điều khoản tới ngày này {self.lb_money(a['broker_terms'])} (chỉ cảnh báo).")
                    if loan.get('due_date') and t['date']>loan['due_date']:w.append(f"Giao dịch sau hạn {self.lb_day(loan['due_date'])}.")
                    warnings+=w
                    impact.append(dict(loan=lid,code=loan['code'],name=loan['name'],direction=loan['direction'],before=pick(b),after=pick(a),
                        settlement=('FULL' if D(a['principal'])==0 else 'PARTIAL') if repaying and not err else None,warnings=w,error=err))
            out=dict(source=dict(id=sid,kind='LEGACY' if t.get('legacy') else 'BANK',date=t['date'],reference=t.get('reference'),description=t.get('description'),account=t.get('account'),
                amount=S(abs(D(t['signed_amount']))),direction=direction,in_scope=S(rec['amount'])),groups=groups,legacy_links=[dict(loan=x['loan'],name=profiles[x['loan']]['name'],amount=S(x['amount'])) for x in rec['legacy']],
                current=copy.deepcopy(cur),versions=copy.deepcopy((det or {}).get('versions',[])),draft=copy.deepcopy((det or {}).get('draft')),lines=lines,impact=impact,warnings=warnings,
                allocated=S(sum((D(l['amount']) for l in lines if l.get('amount')),Decimal(0))),remaining=S(rec['amount']-sum((D(l['amount']) for l in lines if l.get('amount')),Decimal(0))),
                blocks=blocks,can_post=not blocks and bool(lines),pending_codes=[i['code'] for i in rec['issues']])
            return out

    # ---- hành động ---------------------------------------------------------------------------
    def lb_suggest_code(self,s,direction):
        pre=DIRS[direction]['prefix'];nums=[int(m.group(1)) for l in s['loans'] for m in [re.fullmatch(re.escape(pre)+r'-(\d+)',l['code'])] if m]
        return f"{pre}-{max(nums,default=0)+1:04d}"

    def lb_loan_fields(self,s,d,loan=None):
        from .p01 import day
        out={}
        if loan is None or 'code' in d:
            code=str(d.get('code') or '').strip() or self.lb_suggest_code(s,loan['direction'] if loan else d['_direction'])
            require(1<=len(code)<=20,'Mã khoản dài 1–20 ký tự.')
            require(not any(x['code'].casefold()==code.casefold() and (loan is None or x['id']!=loan['id']) for x in s['loans']),f'Mã khoản {code} đã có; chọn mã khác.')
            out['code']=code
        if loan is None or 'name' in d:
            name=str(d.get('name') or '').strip();require(1<=len(name)<=100,'Tên khoản dài 1–100 ký tự.');out['name']=name
        if loan is None or 'tracking_date' in d:out['tracking_date']=day(d.get('tracking_date'))
        if loan is None or 'due_date' in d:out['due_date']=day(d['due_date']) if d.get('due_date') else None
        if loan is None or 'rate' in d:out['rate']=lb_rate(d.get('rate'),'mức lãi')
        direction=loan['direction'] if loan else d['_direction']
        if loan is None or 'broker_name' in d or 'broker_rate' in d:
            bn=str(d.get('broker_name') or '').strip();br=d.get('broker_rate')
            if bn or str(br or '').strip():
                require(direction=='RECEIVABLE','Môi giới chỉ áp dụng cho khoản Cho vay.')
                require(1<=len(bn)<=100,'Nhập tên/biệt danh môi giới (1–100 ký tự).');out['broker']=dict(name=bn,rate=lb_rate(br,'mức môi giới'))
            else:out['broker']=None
        td=out.get('tracking_date',(loan or {}).get('tracking_date'));dd=out.get('due_date',(loan or {}).get('due_date'))
        require(not dd or dd>=td,'Hạn trả không được trước ngày theo dõi.')
        return out

    def lb_terms_locked(self,s,loan):
        """PO review P1: khoản đã từng có phát sinh được ghi (mọi phiên bản chi tiết, kể cả đã thay/hủy, hoặc miễn giảm) thì khóa điều khoản tài chính."""
        srcs={det['source'] for det in s.get('loan_details',[]) for v in det.get('versions',[]) if any(l.get('loan')==loan['id'] for l in v.get('lines',[]))}
        waived=any(w['loan']==loan['id'] for w in s.get('loan_waivers',[]))
        if not srcs and not waived:return None
        return (f"Khoản {loan['code']} đã có phát sinh được ghi ({len(srcs)} nguồn{', có miễn giảm' if waived else ''}); không sửa mức lãi hay điều khoản môi giới vì sẽ đổi lãi của những ngày đã qua. "
                "Bản này chưa hỗ trợ đổi lãi suất theo ngày hiệu lực. Nếu nhập sai từ đầu: hủy chi tiết các nguồn, tạo khoản mới đúng điều khoản rồi ghi lại vào khoản mới.")

    def change_loan_business(self,s,action,d):
        from .p01 import now
        lb_state(s);reason=str(d.get('reason') or '').strip()[:500]
        if action in {'lb-category-set','lb-category-clear'}:
            before=self.lb_fingerprint(s);msg=self.lb_change_category(s,action,d,reason);self.lb_guard(s,before);return msg
        if action=='lb-loan-create':
            key=d.get('category');require(key not in ROOTS,'Chọn danh mục mang nghiệp vụ vay.')
            node=self.cat_find(s,key);require(node['status']=='ACTIVE','Danh mục đang lưu trữ.')
            b=self.lb_effective(s,key);require(b,'Danh mục này chưa mang nghiệp vụ Cho vay/Đi vay; gắn nghiệp vụ ở màn Danh mục trước.')
            prof=item(s['profiles'],d.get('person'));require(prof['kind']=='PERSON' and not prof.get('merged_into'),'Khoản vay chỉ thuộc về đối tượng loại Người.')
            require(prof.get('status')!='ARCHIVED','Người đang lưu trữ; khôi phục ở màn Đối tượng trước.')
            require(self.is_member(s,key,prof['id']),f"{prof['name']} chưa là thành viên danh mục {self.cat_path(s,key)}; thêm người vào danh mục trước khi tạo khoản.")
            f=self.lb_loan_fields(s,dict(d,_direction=b[0]))
            loan=dict(id=uid(),person=prof['id'],direction=b[0],category=key,status='ACTIVE',created_at=now(),completion=None,history=[],**f)
            loan['history'].append(dict(at=now(),action='CREATE',before=None,after={k:copy.deepcopy(loan[k]) for k in f},reason=reason))
            s['loans'].append(loan);return f"Tạo khoản {DIRS[b[0]]['name']} {loan['code']} · {loan['name']} cho {prof['name']}"
        if action=='lb-loan-edit':
            loan=item(s['loans'],d.get('loan'));require(reason,'Cần lý do sửa thông tin khoản vay.')
            f=self.lb_loan_fields(s,{k:v for k,v in d.items() if k in {'code','name','tracking_date','due_date','rate','broker_name','broker_rate'}},loan)
            changed={k:v for k,v in f.items() if loan.get(k)!=v};require(changed,'Không có thay đổi nào.')
            if loan['status']=='COMPLETED':require(set(changed)<={'name','code'},'Khoản đã hoàn tất: chỉ đổi tên/mã. Mở lại khoản trước khi sửa lãi, ngày hay môi giới.')
            old_b=loan.get('broker');new_b=changed.get('broker',old_b)
            financial='rate' in changed or bool(old_b)!=bool(new_b) or (old_b and new_b and old_b['rate']!=new_b['rate'])
            lock=self.lb_terms_locked(s,loan) if financial else None;require(not lock,lock or '')
            before={k:copy.deepcopy(loan.get(k)) for k in changed};loan.update(changed)
            self.lb_check(s,loan,self.lb_loan_lines(s).get(loan['id'],[]),[w for w in s['loan_waivers'] if w['loan']==loan['id']])
            loan['history'].append(dict(at=now(),action='EDIT',before=before,after=copy.deepcopy(changed),reason=reason))
            return f"Sửa khoản {loan['code']}: {reason}"
        if action in {'lb-detail-draft','lb-detail-post','lb-detail-void','lb-detail-discard'}:return self.lb_change_detail(s,action,d,reason)
        if action in {'lb-waiver-add','lb-waiver-cancel'}:
            from .p01 import day,money
            if action=='lb-waiver-add':
                loan=item(s['loans'],d.get('loan'));require(loan['status']!='COMPLETED',f"Khoản {loan['code']} đã hoàn tất; mở lại trước.")
                require(reason,'Cần lý do miễn giảm.');when=day(d.get('date'));amount=money(d.get('amount'));require(amount>0,'Số miễn giảm phải dương.')
                require(when>=loan['tracking_date'],'Ngày miễn giảm không được trước ngày theo dõi.')
                w=dict(id=uid(),loan=loan['id'],date=when,amount=S(amount),reason=reason,status='ACTIVE',at=now(),history=[dict(at=now(),action='ADD',reason=reason)])
                waivers=[x for x in s['loan_waivers'] if x['loan']==loan['id']]+[w]
                self.lb_check(s,loan,self.lb_loan_lines(s).get(loan['id'],[]),waivers)
                s['loan_waivers'].append(w);return f"Miễn giảm lãi {self.lb_money(amount)} cho khoản {loan['code']}: {reason}"
            w=item(s['loan_waivers'],d.get('waiver'));loan=item(s['loans'],w['loan']);require(w['status']=='ACTIVE','Miễn giảm đã hủy.')
            require(loan['status']!='COMPLETED',f"Khoản {loan['code']} đã hoàn tất; mở lại trước khi hủy miễn giảm.");require(reason,'Cần lý do hủy miễn giảm.')
            w['status']='CANCELLED';w['history'].append(dict(at=now(),action='CANCEL',reason=reason));return f"Hủy miễn giảm của khoản {loan['code']}"
        if action=='lb-loan-complete':
            loan=item(s['loans'],d.get('loan'));require(reason,'Cần lý do / ghi chú hoàn tất.')
            row=next(r for r in self.loan_book(s)['loans'] if r['id']==loan['id']);require(row['can_complete'],'Chưa hoàn tất được: '+(row['complete_blocker'] or ''))
            loan.update(status='COMPLETED',completion=dict(at=now(),reason=reason,as_of=row['last_event']));loan['history'].append(dict(at=now(),action='COMPLETE',before='ACTIVE',after='COMPLETED',reason=reason))
            return f"Hoàn tất khoản {loan['code']}"
        if action=='lb-loan-reopen':
            loan=item(s['loans'],d.get('loan'));require(loan['status']=='COMPLETED','Khoản chưa hoàn tất.');require(reason,'Cần lý do mở lại.')
            loan.update(status='ACTIVE');loan['history'].append(dict(at=now(),action='REOPEN',before='COMPLETED',after='ACTIVE',reason=reason));return f"Mở lại khoản {loan['code']}"
        require(False,'Thao tác nghiệp vụ vay không hợp lệ.')

    def lb_change_category(self,s,action,d,reason):
        from .p01 import now
        key=d.get('category');require(key not in ROOTS,'Chỉ gắn nghiệp vụ vào danh mục bạn tạo.');node=self.cat_find(s,key)
        require(reason,'Cần lý do.')
        if action=='lb-category-set':
            p=self.lb_category_preview(d,s);require(not p['blocks'],p['blocks'][0]['message'] if p['blocks'] else '')
            require(d.get('review_token')==p['review_token'],'Dữ liệu đã thay đổi sau khi xem trước; xem trước lại rồi xác nhận.')
            node['business']=dict(type=d['type'],at=now(),reason=reason)
            node.setdefault('business_history',[]).append(dict(at=now(),action='SET',type=d['type'],reason=reason,before=None))
            return f"Gắn nghiệp vụ {DIRS[d['type']]['name']} cho {self.cat_path(s,key)}"
        own=node.get('business');require(own,'Danh mục không mang nghiệp vụ riêng (có thể đang kế thừa từ danh mục cha).')
        scope=set(self.lb_scope(s,key))
        lines=[l for det in s['loan_details'] for v in ([self.lb_current(det)] if self.lb_current(det) else [])+([det['draft']] if det.get('draft') else []) for l in v['lines'] if l.get('category') in scope]
        nsrc=len({det['source'] for det in s['loan_details'] for v in ([self.lb_current(det)] if self.lb_current(det) else [])+([det['draft']] if det.get('draft') else []) if any(l.get('category') in scope for l in v['lines'])})
        loans=[l for l in s['loans'] if l['category'] in scope]
        require(not lines,f"Nhánh có {nsrc} giao dịch đã ghi hoặc đang nháp chi tiết nghiệp vụ; không gỡ nghiệp vụ để tránh đổi lịch sử đã ghi. Hủy các chi tiết đó trước.")
        require(not loans,f"Nhánh có {len(loans)} khoản vay được tạo từ đây ({', '.join(l['code'] for l in loans)}); không gỡ nghiệp vụ.")
        node.setdefault('business_history',[]).append(dict(at=now(),action='CLEAR',type=None,reason=reason,before=copy.deepcopy(own)));node['business']=None
        return f"Gỡ nghiệp vụ của {self.cat_path(s,key)}"

    def lb_change_detail(self,s,action,d,reason):
        from .p01 import now
        sid=d.get('source');srcs=self.lb_sources(s);t=srcs.get(sid);require(t is not None,'Không tìm thấy giao dịch hoặc dòng lịch sử cũ đang hiệu lực.')
        det=self.lb_detail(s,sid)
        if action=='lb-detail-discard':
            require(det and det.get('draft'),'Không có nháp.');det['draft']=None;return 'Bỏ nháp chi tiết nghiệp vụ'
        if det is None:
            det=dict(source=sid,kind='LEGACY' if t.get('legacy') else 'BANK',versions=[],draft=None);s['loan_details'].append(det)
        loans={l['id']:l for l in s['loans']}
        if action=='lb-detail-draft':
            require(self.lb_groups(s).get(sid) is not None,'Giao dịch không có tiền trong danh mục mang nghiệp vụ vay.')
            lines=self.lb_parse_lines(s,d.get('lines',[]),strict=False);require(lines,'Nháp cần ít nhất một dòng.')
            det['draft']=dict(at=now(),lines=lines);return 'Lưu nháp chi tiết nghiệp vụ (chưa ghi sổ)'
        cur=self.lb_current(det)
        if action=='lb-detail-post':
            lines=self.lb_parse_lines(s,d.get('lines',[]),strict=True);require(lines,'Cần ít nhất một dòng chi tiết.')
            p=self.lb_detail_preview(dict(source=sid,lines=lines),s);require(not p['blocks'],p['blocks'][0]['message'] if p['blocks'] else '')
            if cur:
                require(reason,'Cần lý do khi thay bản chi tiết đã ghi.')
                key=lambda ls:sorted((l['category'],l['person'],l['loan'],l['component'],l['amount']) for l in ls)
                require(key(cur['lines'])!=key(lines),'Chi tiết giống bản đã ghi; không tạo phiên bản mới.')
                for lid in {l['loan'] for l in cur['lines']}:require(loans[lid]['status']!='COMPLETED',f"Khoản {loans[lid]['code']} đã hoàn tất; mở lại trước khi sửa chi tiết.")
            det['versions'].append(dict(n=len(det['versions'])+1,status='POSTED',lines=lines,at=now(),reason=reason or 'Ghi nghiệp vụ'));det['draft']=None
            return f"Ghi nghiệp vụ cho {t.get('reference') or 'dòng lịch sử cũ'}"
        require(cur,'Chưa có chi tiết đã ghi để hủy.');require(reason,'Cần lý do hủy chi tiết nghiệp vụ.')
        affected={l['loan'] for l in cur['lines']}
        for lid in affected:require(loans[lid]['status']!='COMPLETED',f"Khoản {loans[lid]['code']} đã hoàn tất; mở lại trước khi hủy chi tiết.")
        det['versions'].append(dict(n=len(det['versions'])+1,status='VOID',lines=[],at=now(),reason=reason))
        allines=self.lb_loan_lines(s)
        for lid in affected:self.lb_check(s,loans[lid],allines.get(lid,[]),[w for w in s['loan_waivers'] if w['loan']==lid])
        return f"Hủy chi tiết nghiệp vụ của {t.get('reference') or 'dòng lịch sử cũ'}: {reason}"
