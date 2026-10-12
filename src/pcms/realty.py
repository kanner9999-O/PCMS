"""Real estate ledger: capital/cost from classified bank parts, plus manual valuations, mortgage links and contributions.

Nothing here edits money or infers ownership: values, contributions and mortgage links are entered by the user.
"""
import copy
from decimal import Decimal, localcontext
from .core import require
from .product import D, S, uid

GAP_LABEL='Chênh lệch chưa thực hiện: chưa trừ chi phí, nợ thế chấp hay thuế; không phải lãi/lỗ.'

def realty_state(s):
    r=s.setdefault('realty',{})
    for key in ('valuations','mortgages','contributions'):r.setdefault(key,[])
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
        require(False,'Hành động không hợp lệ.')

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
                    valuation=dict(current=current,history=sorted(vals,key=lambda v:(v['date'],v['created_at']),reverse=True)),gap=gap,mortgages=mortgages,contributions=dict(items=items,total=S(total)),evidence='HAS_DATA' if tx else ('EMPTY' if periods else 'EMPTY_NO_SOURCE')))
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
