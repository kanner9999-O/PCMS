"""Real estate ledger: capital/cost from classified bank parts, plus manual valuations, mortgage links and contributions.

Nothing here edits money or infers ownership: values, contributions and mortgage links are entered by the user.
"""
import copy
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, localcontext
from .core import require
from .product import D, S, uid

GAP_LABEL='Chênh lệch chưa thực hiện: chưa trừ chi phí, nợ thế chấp hay thuế; không phải lãi/lỗ.'

def today_vn():
    return (datetime.now(timezone.utc)+timedelta(hours=7)).date().isoformat()

def realty_state(s):
    r=s.setdefault('realty',{})
    for key in ('valuations','mortgages','contributions','contracts','installments','pay_links'):r.setdefault(key,[])
    return r

def text(value,limit,message,required=True):
    value=str(value or '').strip()
    require(value or not required,message)
    return value[:limit]

class Realty:
    def realty_prop(self,s,pid):
        p=next((x for x in s['profiles'] if x['id']==pid),None)
        require(p is not None and p['kind']=='PROPERTY','Chọn một hồ sơ bất động sản.')
        return p

    def realty_pick(self,items,key,label):
        found=next((x for x in items if x['id']==key),None)
        require(found is not None,'Không tìm thấy '+label+'.')
        return found

    # ---- actions -------------------------------------------------------
    def change_realty(self,s,action,d):
        from .p01 import day,money,now
        r=realty_state(s)
        if action=='realty-valuation':
            p=self.realty_prop(s,d.get('property'));value=money(d.get('value'));require(value>0,'Giá trị hiện tại phải lớn hơn 0.')
            r['valuations'].append(dict(id=uid(),property=p['id'],value=S(value),date=day(d.get('date')),source=text(d.get('source'),500,'Cần ghi nguồn của giá trị (báo giá, thẩm định…).'),note=text(d.get('note'),500,'',False),status='ACTIVE',created_at=now()))
            return f"Ghi giá trị hiện tại {p['name']}"
        if action=='realty-valuation-void':
            v=self.realty_pick(r['valuations'],d.get('valuation'),'giá trị');require(v['status']=='ACTIVE','Giá trị đã hủy.')
            v.update(status='VOID',void_reason=text(d.get('reason'),500,'Cần lý do hủy.'),voided_at=now());return 'Hủy giá trị, giữ bản ghi'
        if action=='realty-mortgage':
            p=self.realty_prop(s,d.get('property'));loan=next((x for x in s['profiles'] if x['id']==d.get('loan')),None)
            require(loan is not None and loan['kind']=='LOAN','Chọn một khoản vay đã có trong Công nợ.')
            require(not any(m['status']=='ACTIVE' and m['loan']==loan['id'] for m in r['mortgages']),'Khoản vay này đang thế chấp một bất động sản; kết thúc liên kết cũ trước.')
            r['mortgages'].append(dict(id=uid(),property=p['id'],loan=loan['id'],purpose=text(d.get('purpose'),500,'Cần ghi mục đích dùng tiền vay.'),note=text(d.get('note'),500,'',False),status='ACTIVE',created_at=now()))
            return f"Liên kết thế chấp {p['name']} · {loan['name']}"
        if action=='realty-mortgage-end':
            m=self.realty_pick(r['mortgages'],d.get('mortgage'),'liên kết thế chấp');require(m['status']=='ACTIVE','Liên kết đã kết thúc.')
            m.update(status='ENDED',end_reason=text(d.get('reason'),500,'Cần lý do kết thúc.'),ended_at=now());return 'Kết thúc liên kết thế chấp, giữ bản ghi'
        if action=='realty-contribution':
            p=self.realty_prop(s,d.get('property'));party=next((x for x in s['profiles'] if x['id']==d.get('party')),None)
            require(party is not None and party['kind']=='PERSON','Chọn người từ hồ sơ người.')
            amount=money(d.get('amount'));require(amount>0,'Số tiền góp phải lớn hơn 0.')
            when=day(d['date']) if d.get('date') else None
            r['contributions'].append(dict(id=uid(),property=p['id'],party=party['id'],amount=S(amount),date=when,evidence=text(d.get('evidence'),500,'Cần ghi bằng chứng của khoản góp.'),note=text(d.get('note'),500,'',False),status='ACTIVE',created_at=now()))
            return f"Ghi góp vốn {party['name']} vào {p['name']}"
        if action=='realty-contribution-void':
            c=self.realty_pick(r['contributions'],d.get('contribution'),'khoản góp');require(c['status']=='ACTIVE','Khoản góp đã hủy.')
            c.update(status='VOID',void_reason=text(d.get('reason'),500,'Cần lý do hủy.'),voided_at=now());return 'Hủy khoản góp, giữ bản ghi'
        if action=='realty-contract':
            p=self.realty_prop(s,d.get('property'));price=money(d.get('price'));require(price>0,'Giá hợp đồng phải lớn hơn 0.')
            reason=text(d.get('reason'),500,'Cần lý do (ký hợp đồng, phụ lục, chiết khấu…).');handover=day(d['handover_date']) if d.get('handover_date') else None
            r['contracts'].append(dict(id=uid(),property=p['id'],price=S(price),date=day(d.get('date')),reason=reason,handover_date=handover,status='ACTIVE',created_at=now()))
            return f"Ghi giá hợp đồng {p['name']}"
        if action=='realty-contract-void':
            c=self.realty_pick(r['contracts'],d.get('contract'),'giá hợp đồng');require(c['status']=='ACTIVE','Bản ghi đã hủy.')
            c.update(status='VOID',void_reason=text(d.get('reason'),500,'Cần lý do hủy.'),voided_at=now());return 'Hủy giá hợp đồng, giữ bản ghi'
        if action=='realty-installment':
            p=self.realty_prop(s,d.get('property'));amount=money(d.get('amount'));require(amount>0,'Số tiền đợt phải lớn hơn 0.')
            r['installments'].append(dict(id=uid(),property=p['id'],label=text(d.get('label'),100,'Cần tên đợt (ví dụ Đợt 1).'),due_date=day(d.get('due_date')),amount=S(amount),note=text(d.get('note'),500,'',False),status='ACTIVE',created_at=now()))
            return f"Thêm đợt thanh toán {p['name']}"
        if action=='realty-installment-void':
            i=self.realty_pick(r['installments'],d.get('installment'),'đợt thanh toán');require(i['status']=='ACTIVE','Đợt đã hủy.')
            require(not any(l['status']=='ACTIVE' and l['installment']==i['id'] for l in r['pay_links']),'Đợt đang có giao dịch gắn; bỏ gắn các giao dịch trước.')
            i.update(status='VOID',void_reason=text(d.get('reason'),500,'Cần lý do hủy.'),voided_at=now());return 'Hủy đợt, giữ bản ghi'
        if action=='realty-pay-link':
            i=self.realty_pick(r['installments'],d.get('installment'),'đợt thanh toán');require(i['status']=='ACTIVE','Đợt đã hủy.')
            t=next((x for x in s['transactions'] if x['id']==d.get('transaction')),None);require(t is not None,'Chọn một giao dịch.')
            require(self.realty_link_amount(s,t,i['property'])>0,'Giao dịch phải là tiền ra đã phân loại Đầu tư BĐS gắn đúng BĐS của đợt này.')
            require(not any(l['status']=='ACTIVE' and l['transaction']==t['id'] for l in r['pay_links']),'Giao dịch đã gắn một đợt; bỏ gắn trước.')
            r['pay_links'].append(dict(id=uid(),installment=i['id'],transaction=t['id'],status='ACTIVE',created_at=now()));return f"Gắn giao dịch vào {i['label']}"
        if action=='realty-pay-unlink':
            l=self.realty_pick(r['pay_links'],d.get('link'),'liên kết');require(l['status']=='ACTIVE','Liên kết đã bỏ.')
            l.update(status='UNLINKED',unlink_reason=text(d.get('reason'),500,'Cần lý do bỏ gắn.'),unlinked_at=now());return 'Bỏ gắn giao dịch, giữ bản ghi'
        require(False,'Hành động không hợp lệ.')

    def realty_link_amount(self,s,t,pid):
        """Outgoing 'investment' parts of the transaction that belong to the property (what an installment payment can count)."""
        if D(t['signed_amount'])>=0:return Decimal(0)
        return sum((D(p['amount']) for p in t['allocations'] if p['category']=='investment' and p.get('profile')==pid),Decimal(0))

    def realty_progress(self,s,r,p):
        pid=p['id'];today=today_vn();tx={t['id']:t for t in s['transactions']}
        contracts=[c for c in r['contracts'] if c['property']==pid];active=[c for c in contracts if c['status']=='ACTIVE']
        cur=max(active,key=lambda c:(c['date'],c['created_at'])) if active else None
        insts=sorted([i for i in r['installments'] if i['property']==pid and i['status']=='ACTIVE'],key=lambda i:(i['due_date'],i['created_at']))
        linked={l['transaction'] for l in r['pay_links'] if l['status']=='ACTIVE'};rows=[];sched=paid_all=remaining_all=Decimal(0);overdue=0
        for i in insts:
            links=[];paid=Decimal(0)
            for l in (x for x in r['pay_links'] if x['installment']==i['id'] and x['status']=='ACTIVE'):
                t=tx.get(l['transaction']);live=self.realty_link_amount(s,t,pid) if t else Decimal(0);paid+=live
                links.append(dict(id=l['id'],transaction=l['transaction'],date=t['date'] if t else None,reference=t['reference'] if t else '',description=t['description'] if t else '',amount=S(live),broken=live==0))
            amount=D(i['amount']);status='PAID' if paid>=amount else ('PARTIAL' if paid>0 else 'UNPAID');late=status!='PAID' and i['due_date']<today
            days=(date.fromisoformat(today)-date.fromisoformat(i['due_date'])).days if late else 0
            rem=max(Decimal(0),amount-paid);sched+=amount;paid_all+=paid;remaining_all+=rem;overdue+=1 if late else 0
            rows.append(dict(id=i['id'],label=i['label'],due_date=i['due_date'],amount=i['amount'],note=i['note'],paid=S(paid),remaining=S(rem),status=status,over_paid=S(max(Decimal(0),paid-amount)),overdue=late,overdue_days=days,links=links))
        linkable=[dict(transaction=t['id'],date=t['date'],reference=t['reference'],description=t['description'],amount=S(self.realty_link_amount(s,t,pid))) for t in sorted(s['transactions'],key=lambda x:(x['date'],x['order']),reverse=True) if t['id'] not in linked and self.realty_link_amount(s,t,pid)>0]
        price=D(cur['price']) if cur else None
        return dict(contract=dict(current=cur,history=sorted(contracts,key=lambda c:(c['date'],c['created_at']),reverse=True)),handover_date=cur['handover_date'] if cur else None,installments=rows,
            summary=dict(price=S(price) if price is not None else None,scheduled=S(sched),paid=S(paid_all),remaining=S(remaining_all),difference=S(price-sched) if (price is not None and rows) else None,overdue=overdue),linkable=linkable,today=today,has_schedule=bool(cur or rows))

    # ---- derived views ---------------------------------------------------
    def realty_parts(self,s,pid):
        """(transaction, part) pairs attached to the property by classification."""
        for t in s['transactions']:
            for p in t['allocations']:
                if p.get('profile')==pid and p['category'] in {'investment','expense'}:yield t,p

    def realty_view(self,s):
        with localcontext() as ctx:
            ctx.prec=60
            s=copy.deepcopy(s);r=realty_state(s);periods=any(b['status']=='PUBLISHED' for b in s['imports'])
            loans={l['id']:l for l in self.debt_register(s)['loans']};people={p['id']:p['name'] for p in s['profiles']}
            props=[]
            for p in s['profiles']:
                if p['kind']!='PROPERTY':continue
                paid=received=spent=refunded=Decimal(0);tx=set()
                for t,part in self.realty_parts(s,p['id']):
                    amount=D(part['amount']);incoming=D(t['signed_amount'])>0;tx.add(t['id'])
                    if part['category']=='investment':
                        if incoming:received+=amount
                        else:paid+=amount
                    elif incoming:refunded+=amount
                    else:spent+=amount
                vals=[v for v in r['valuations'] if v['property']==p['id']]
                active=[v for v in vals if v['status']=='ACTIVE']
                current=max(active,key=lambda v:(v['date'],v['created_at'])) if active else None
                capital_net=paid-received
                gap=dict(amount=S(D(current['value'])-capital_net),label=GAP_LABEL) if current else None
                mortgages=[]
                for m in (x for x in r['mortgages'] if x['property']==p['id']):
                    loan=loans.get(m['loan']);mortgages.append(dict(m,loan_name=loan and next((x['name'] for x in s['profiles'] if x['id']==m['loan']),None),principal=(loan['current_principal'] if loan else None),issues=(loan['issues'] if loan else []),note_nodebt='Dư gốc chỉ để tham khảo; không trừ vào giá trị hay chênh lệch.'))
                items=[dict(c,party_name=people.get(c['party'],'')) for c in r['contributions'] if c['property']==p['id']]
                total=sum((D(c['amount']) for c in items if c['status']=='ACTIVE'),Decimal(0))
                props.append(dict(id=p['id'],name=p['name'],capital=dict(paid=S(paid),received=S(received),net=S(capital_net),transactions=len(tx)),costs=dict(spent=S(spent),refunded=S(refunded),net=S(spent-refunded)),
                    progress=self.realty_progress(s,r,p),                    valuation=dict(current=current,history=sorted(vals,key=lambda v:(v['date'],v['created_at']),reverse=True)),gap=gap,mortgages=mortgages,contributions=dict(items=items,total=S(total)),evidence='HAS_DATA' if tx else ('EMPTY' if periods else 'EMPTY_NO_SOURCE')))
            unclassified=sum(1 for t in s['transactions'] if not t['allocations'] or any(a['category']=='unknown' for a in t['allocations']))
            return dict(properties=props,unclassified=unclassified,gap_label=GAP_LABEL,draft=True)

    def realty_history(self,d,s=None):
        from .p01 import display_day
        with localcontext() as ctx:
            ctx.prec=60
            s=copy.deepcopy(s or self.state());p=self.realty_prop(s,d.get('property'))
            approved={t['id'] for snap in s['snapshots'] for t in snap['report']['transactions']};accounts={a['id']:a['name'] for a in s['accounts']}
            rows=[];tx=set();paid=received=spent=refunded=Decimal(0)
            for t,part in self.realty_parts(s,p['id']):
                amount=D(part['amount']);incoming=D(t['signed_amount'])>0;tx.add(t['id']);capital=part['category']=='investment'
                if capital:
                    if incoming:received+=amount
                    else:paid+=amount
                elif incoming:refunded+=amount
                else:spent+=amount
                rows.append(dict(transaction=t['id'],date=t['date'],account=accounts.get(t['account'],''),reference=t['reference'],description=t['description'],amount=S(amount),direction='IN' if incoming else 'OUT',kind='CAPITAL' if capital else 'COST',status='APPROVED' if t['id'] in approved else 'DRAFT',sources=copy.deepcopy(t.get('sources',[])),source_count=len(t.get('sources',[])),split=len(t['allocations'])>1,tx_amount=S(abs(D(t['signed_amount']))),
                    label=('Vốn nhận lại' if incoming else 'Vốn đã thanh toán') if capital else ('Hoàn chi phí' if incoming else 'Chi phí')))
            rows.sort(key=lambda r:(r['date'],r['reference']),reverse=True)
            periods=sorted({(b['period_start'],b['period_end']) for b in s['imports'] if b['status']=='PUBLISHED'})
            notice=('Kỳ nguồn đã ghi: '+'; '.join(display_day(a)+' → '+display_day(b) for a,b in periods)+'. Vốn chỉ tính giao dịch đã phân loại Đầu tư BĐS gắn BĐS này.') if periods else 'Chưa có nguồn ngân hàng nào được ghi; không suy ra là chưa thanh toán.'
            return dict(property=p['id'],name=p['name'],evidence='HAS_DATA' if rows else ('EMPTY' if periods else 'EMPTY_NO_SOURCE'),source_notice=notice,
                capital=dict(paid=S(paid),received=S(received),net=S(paid-received)),costs=dict(spent=S(spent),refunded=S(refunded),net=S(spent-refunded)),rows=rows)
