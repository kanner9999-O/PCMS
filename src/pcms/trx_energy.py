"""Manual TRX/Energy ledger: customers, orders, receipts, allocations and cash-basis reports.

Never infers profit, overdue status or exchange rates; every figure is entered by the user.
"""
import copy
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, localcontext, ROUND_HALF_UP
from .core import require
from .product import D, S, uid

LINE_TYPES={'ENERGY_ONCE','ENERGY_MONTHLY','TRX_SALE'}
Q6=Decimal('0.000001')

def usdt(value):
    return D(value).quantize(Q6,rounding=ROUND_HALF_UP)

def text(value,limit,message,required=True):
    value=str(value or '').strip()
    require(value or not required,message)
    return value[:limit]

def pick(items,key,label):
    found=next((x for x in items if x['id']==key),None)
    require(found is not None,'Không tìm thấy '+label+'.')
    return found

def vn_today():
    return datetime.now(timezone(timedelta(hours=7))).date().isoformat()

def trx_state(s):
    t=s.setdefault('trx',{})
    for key in ('customers','orders','receipts','rewards'):t.setdefault(key,[])
    return t

class TrxEnergy:
    def line_paid(self,t):
        paid={}
        for r in t['receipts']:
            if r['status']!='ACTIVE':continue
            for a in r['allocations']:paid[a['line']]=paid.get(a['line'],Decimal(0))+D(a['amount_usdt'])
        return paid

    def receipt_allocated(self,r):
        return sum((D(a['amount_usdt']) for a in r['allocations']),Decimal(0))

    def _allocate(self,t,receipt,items):
        from .p01 import now
        require(isinstance(items,list) and items,'Cần ít nhất một dòng phân bổ.')
        order_of={ln['id']:(o,ln) for o in t['orders'] if o['status']=='ACTIVE' and o['customer']==receipt['customer'] for ln in o['lines']}
        add={}
        for a in items:
            require(a.get('line') in order_of,'Dòng phân bổ phải thuộc đơn còn hiệu lực của đúng khách này.')
            amount=usdt(a.get('amount_usdt'));require(amount>0,'Số tiền phân bổ phải lớn hơn 0.')
            add[a['line']]=add.get(a['line'],Decimal(0))+amount
        require(self.receipt_allocated(receipt)+sum(add.values())<=D(receipt['usdt_equivalent']),'Tổng phân bổ vượt số USDT của khoản thu; phần thừa để chờ phân bổ.')
        paid=self.line_paid(t)
        for line,amount in add.items():
            require(paid.get(line,Decimal(0))+amount<=D(order_of[line][1]['amount_usdt']),'Phân bổ vượt số còn phải thu của dòng đơn.')
        stamp=now()
        for line,amount in add.items():receipt['allocations'].append(dict(line=line,amount_usdt=S(amount),at=stamp))

    def change_trx(self,s,action,d):
        from .p01 import day,money,now
        t=trx_state(s)
        if action=='trx-customer':
            name=text(d.get('name'),100,'Cần tên khách.')
            require(not any(c['name'].lower()==name.lower() for c in t['customers']),'Khách này đã có.')
            t['customers'].append(dict(id=uid(),name=name,note=text(d.get('note'),500,'',False),created_at=now(),status='ACTIVE'))
            return 'Thêm khách '+name
        if action=='trx-order':
            customer=pick(t['customers'],d.get('customer'),'khách')
            terms=d.get('terms') or {};mode=terms.get('mode');require(mode in {'PREPAID','POSTPAID'},'Chọn thu trước hoặc thu sau.')
            due=terms.get('due_date') or None
            if due:day(due)
            evidence=text(d.get('evidence'),500,'Cần ghi căn cứ/bằng chứng của đơn.')
            lines=[];raw=d.get('lines')
            require(isinstance(raw,list) and raw,'Đơn cần ít nhất một dòng.')
            for ln in raw:
                kind=ln.get('type');require(kind in LINE_TYPES,'Loại dòng không hợp lệ.')
                amount=usdt(ln.get('amount_usdt'));quantity=D(ln.get('quantity'))
                require(amount>0,'Số tiền USDT của dòng phải lớn hơn 0.');require(quantity>0,'Số lượng phải lớn hơn 0.')
                row=dict(id=uid(),type=kind,amount_usdt=S(amount),quantity=S(quantity),note=text(ln.get('note'),300,'',False))
                if kind=='ENERGY_MONTHLY':
                    row['plan']=text(ln.get('plan'),100,'Gói tháng cần tên gói.')
                    row['service_start']=day(ln.get('service_start'));row['service_end']=day(ln.get('service_end'))
                    require(row['service_end']>=row['service_start'],'Ngày kết thúc dịch vụ không trước ngày bắt đầu.')
                lines.append(row)
            t['orders'].append(dict(id=uid(),customer=customer['id'],date=day(d.get('date')),terms=dict(mode=mode,due_date=due),evidence=evidence,lines=lines,status='ACTIVE',created_at=now()))
            return f"Thêm đơn cho {customer['name']} ({len(lines)} dòng)"
        if action=='trx-order-void':
            order=pick(t['orders'],d.get('order'),'đơn');require(order['status']=='ACTIVE','Đơn đã hủy.')
            reason=text(d.get('reason'),500,'Cần lý do hủy.')
            ids={ln['id'] for ln in order['lines']}
            require(not any(a['line'] in ids for r in t['receipts'] if r['status']=='ACTIVE' for a in r['allocations']),'Đơn còn phân bổ tiền thu; hủy khoản thu liên quan trước.')
            order.update(status='VOID',void_reason=reason,voided_at=now());return 'Hủy đơn, giữ bản ghi'
        if action=='trx-receipt':
            customer=pick(t['customers'],d.get('customer'),'khách');currency=d.get('currency');require(currency in {'USDT','VND'},'Chọn USDT hoặc VND.')
            received=D(d.get('received'));require(received>0,'Số tiền nhận phải lớn hơn 0.')
            evidence=text(d.get('evidence'),500,'Cần ghi căn cứ/bằng chứng của khoản thu.');rate=None;bank=d.get('bank_transaction') or None
            if currency=='VND':
                money(d.get('received'));rate=D(d.get('rate'));require(rate>0,'Cần tỷ giá VND/USDT của lần thu này.')
                equivalent=(received/rate).quantize(Q6,rounding=ROUND_HALF_UP);require(equivalent>0,'Số USDT cấn quá nhỏ.')
            else:
                require(not bank,'Chỉ khoản thu VND mới gắn giao dịch ngân hàng.');equivalent=usdt(received);received=equivalent
            if bank:
                tx=pick(s['transactions'],bank,'giao dịch ngân hàng');require(D(tx['signed_amount'])>0,'Chỉ gắn giao dịch tiền vào.')
                require(not any(a.get('profile') for a in tx.get('allocations',[])),'Giao dịch này đã phân bổ vào khoản vay/hồ sơ khác; không gắn vào khoản thu TRX để tránh tính tiền hai lần.')
                used=sum((D(r['received']) for r in t['receipts'] if r['status']=='ACTIVE' and r.get('bank_transaction')==bank),Decimal(0))
                require(used+received<=D(tx['signed_amount']),'Giao dịch ngân hàng này không còn đủ tiền chưa gắn (tránh ghi tiền hai lần).')
            receipt=dict(id=uid(),customer=customer['id'],date=day(d.get('date')),currency=currency,received=S(received),rate=S(rate) if rate else None,usdt_equivalent=S(equivalent),bank_transaction=bank,evidence=evidence,allocations=[],status='ACTIVE',created_at=now())
            t['receipts'].append(receipt)
            if d.get('allocations'):self._allocate(t,receipt,d['allocations'])
            return f"Ghi khoản thu {S(received)} {currency} của {customer['name']}"
        if action=='trx-allocate':
            receipt=pick(t['receipts'],d.get('receipt'),'khoản thu');require(receipt['status']=='ACTIVE','Khoản thu đã hủy.')
            self._allocate(t,receipt,d.get('allocations'));return 'Phân bổ thêm khoản thu'
        if action=='trx-receipt-void':
            receipt=pick(t['receipts'],d.get('receipt'),'khoản thu');require(receipt['status']=='ACTIVE','Khoản thu đã hủy.')
            receipt.update(status='VOID',void_reason=text(d.get('reason'),500,'Cần lý do hủy.'),voided_at=now());return 'Hủy khoản thu, giữ bản ghi'
        if action=='trx-reward':
            amount=D(d.get('trx_amount'));require(amount>0,'Số TRX thưởng phải lớn hơn 0.')
            t['rewards'].append(dict(id=uid(),date=day(d.get('date')),trx_amount=S(amount),note=text(d.get('note'),300,'',False),status='ACTIVE',created_at=now()));return 'Ghi thưởng staking '+S(amount)+' TRX'
        require(False,'Hành động không hợp lệ.')

    def trx_view(self,s,today=None):
        with localcontext() as ctx:
            ctx.prec=60
            t=copy.deepcopy(trx_state(s));today=today or vn_today();paid=self.line_paid(t)
            customers=[];totals={k:Decimal(0) for k in ('billed','allocated','outstanding','unallocated')}
            for c in t['customers']:
                orders=[o for o in t['orders'] if o['customer']==c['id']];billed=allocated=Decimal(0);overdue=False
                for o in orders:
                    total=sum((D(ln['amount_usdt']) for ln in o['lines']),Decimal(0));got=Decimal(0)
                    for ln in o['lines']:
                        p=paid.get(ln['id'],Decimal(0)) if o['status']=='ACTIVE' else Decimal(0);got+=p
                        ln['paid']=S(p);ln['outstanding']=S(D(ln['amount_usdt'])-p if o['status']=='ACTIVE' else Decimal(0))
                        ln['status']='VOID' if o['status']!='ACTIVE' else ('PAID' if p>=D(ln['amount_usdt']) else ('PARTIAL' if p>0 else 'UNPAID'))
                    o['billed']=S(total if o['status']=='ACTIVE' else Decimal(0));o['paid']=S(got);o['outstanding']=S(total-got if o['status']=='ACTIVE' else Decimal(0))
                    o['overdue']=bool(o['status']=='ACTIVE' and o['terms'].get('due_date') and today>o['terms']['due_date'] and total-got>0)
                    if o['status']=='ACTIVE':billed+=total;allocated+=got;overdue=overdue or o['overdue']
                receipts=[r for r in t['receipts'] if r['customer']==c['id']];unalloc=Decimal(0)
                for r in receipts:
                    left=D(r['usdt_equivalent'])-self.receipt_allocated(r);r['allocated']=S(self.receipt_allocated(r));r['unallocated']=S(left if r['status']=='ACTIVE' else Decimal(0))
                    if r['status']=='ACTIVE':unalloc+=left
                customers.append(dict(id=c['id'],name=c['name'],note=c['note'],billed=S(billed),allocated=S(allocated),outstanding=S(billed-allocated),unallocated=S(unalloc),overdue=overdue,orders=orders,receipts=receipts))
                for k,v in (('billed',billed),('allocated',allocated),('outstanding',billed-allocated),('unallocated',unalloc)):totals[k]+=v
            sold=sum((D(ln['quantity']) for o in t['orders'] if o['status']=='ACTIVE' for ln in o['lines'] if ln['type']=='TRX_SALE'),Decimal(0))
            rewards=sum((D(r['trx_amount']) for r in t['rewards'] if r['status']=='ACTIVE'),Decimal(0))
            return dict(customers=customers,rewards=t['rewards'],totals={k:S(v) for k,v in totals.items()},trx_sold_quantity=S(sold),reward_quantity=S(rewards),today=today,draft=True)

    def trx_report(self,d,s=None):
        from .p01 import day
        with localcontext() as ctx:
            ctx.prec=60
            s=s or self.state();t=trx_state(copy.deepcopy(s));chosen=date.fromisoformat(day(d.get('date')));period=d.get('period')
            require(period in {'week','month','quarter'},'Chọn tuần, tháng hoặc quý.')
            if period=='week':start=chosen-timedelta(days=chosen.weekday());end=start+timedelta(days=7)
            else:
                month=chosen.month if period=='month' else ((chosen.month-1)//3)*3+1
                start=date(chosen.year,month,1);nxt=month+(1 if period=='month' else 3);end=date(chosen.year+(nxt-1)//12,(nxt-1)%12+1,1)
            kinds={ln['id']:ln['type'] for o in t['orders'] for ln in o['lines']}
            by={k:Decimal(0) for k in ('ENERGY_ONCE','ENERGY_MONTHLY','TRX_SALE','UNALLOCATED')};usdt_total=vnd=direct=Decimal(0);entries=[]
            for r in t['receipts']:
                if r['status']!='ACTIVE' or not start.isoformat()<=r['date']<end.isoformat():continue
                eq=D(r['usdt_equivalent']);usdt_total+=eq
                if r['currency']=='VND':vnd+=D(r['received'])
                else:direct+=eq
                for a in r['allocations']:by[kinds[a['line']]]+=D(a['amount_usdt'])
                by['UNALLOCATED']+=eq-self.receipt_allocated(r)
                entries.append(dict(receipt=r['id'],date=r['date'],customer=r['customer'],currency=r['currency'],received=r['received'],rate=r['rate'],usdt_equivalent=r['usdt_equivalent'],bank_transaction=r['bank_transaction']))
            sold=sum((D(ln['quantity']) for o in t['orders'] if o['status']=='ACTIVE' and start.isoformat()<=o['date']<end.isoformat() for ln in o['lines'] if ln['type']=='TRX_SALE'),Decimal(0))
            rewards=sum((D(r['trx_amount']) for r in t['rewards'] if r['status']=='ACTIVE' and start.isoformat()<=r['date']<end.isoformat()),Decimal(0))
            return dict(start=start.isoformat(),end=end.isoformat(),period=period,received_usdt=S(usdt_total),received_usdt_direct=S(direct),received_vnd=S(vnd),by_type={k:S(v) for k,v in by.items()},trx_sold=S(sold),trx_rewards=S(rewards),entries=entries)
