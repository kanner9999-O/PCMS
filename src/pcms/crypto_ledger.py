"""Manual crypto ledger: holding places, dated balance confirmations, hand-entered prices and capital.

Nothing here derives quantities from transactions, fetches prices or touches keys; every figure is typed in by the user.
"""
import copy
import re
from decimal import Decimal, localcontext, ROUND_HALF_UP
from .core import require
from .product import S, uid

BUCKETS={'HOLDING':'Đang giữ','EARN_LOCKED':'Đang Earn / khóa','MARGIN_COLLATERAL':'Ký quỹ','OPEN_POSITION':'Vị thế đang mở','MARGIN_DEBT':'Nợ margin'}
ASSET_BUCKETS=('HOLDING','EARN_LOCKED','MARGIN_COLLATERAL')
WALLET_BUCKETS=('HOLDING',)
GAP_LABEL='Chênh lệch chưa thực hiện: giá nhập tay, chưa trừ phí/thuế; không phải lãi/lỗ.'
COMPONENTS_NOTE='Tổng nơi giữ chỉ gồm các thành phần tài sản (đang giữ, Earn/khóa, ký quỹ) có giá; bạn bảo đảm các thành phần không chồng nhau.'
Q6=Decimal('0.000001');Q2=Decimal('0.01')

def crypto_state(s):
    c=s.setdefault('crypto',{})
    for key in ('places','balances','prices','capitals'):c.setdefault(key,[])
    return c

def text(value,limit,message,required=True):
    value=str(value or '').strip()
    require(value or not required,message)
    return value[:limit]

def norm_ticker(value):
    ticker=str(value or '').strip().upper()
    require(re.fullmatch(r'[A-Z0-9]{1,20}',ticker),'Ticker gồm chữ/số, 1–20 ký tự (ví dụ BTC, USDT).')
    return ticker

def norm_network(value):
    network=str(value or '').strip().upper()
    require(len(network)<=30,'Tên mạng tối đa 30 ký tự.')
    return network

def coin_key(ticker,network):return f'{ticker}|{network}'

def D(value):
    """Decimal parser for crypto quantities/prices: strings only, finite, up to 40 digits (the money helper caps at 12 decimals)."""
    require(not isinstance(value,(float,bool)) and value is not None,'Số cần được nhập dưới dạng chuỗi thập phân.')
    try:result=Decimal(str(value).strip())
    except Exception:raise_invalid()
    require(result.is_finite() and len(result.as_tuple().digits)<=40,'Số nằm ngoài phạm vi hỗ trợ.')
    return result

def raise_invalid():require(False,'Số không hợp lệ.')

def decimals(value,places,message):
    result=D(value);require(-result.as_tuple().exponent<=places,message);return result

def latest(items):return max(items,key=lambda x:(x['date'],x['created_at'])) if items else None

class CryptoLedger:
    def crypto_place(self,s,pid,active=True):
        p=next((x for x in crypto_state(s)['places'] if x['id']==pid),None)
        require(p is not None,'Chọn một nơi giữ.')
        require(not active or p['status']=='ACTIVE','Nơi giữ đã lưu trữ.')
        return p

    def crypto_pick(self,items,key,label):
        found=next((x for x in items if x['id']==key),None)
        require(found is not None,'Không tìm thấy '+label+'.')
        return found

    # ---- actions -------------------------------------------------------
    def change_crypto(self,s,action,d):
        from .p01 import day,now
        c=crypto_state(s)
        if action=='crypto-place':
            name=text(d.get('name'),100,'Cần tên nơi giữ.')
            require(not any(p['name'].casefold()==name.casefold() for p in c['places']),'Đã có nơi giữ cùng tên.')
            kind=d.get('kind');require(kind in {'WALLET','EXCHANGE'},'Chọn ví riêng hoặc sàn.')
            c['places'].append(dict(id=uid(),name=name,kind=kind,start_date=day(d['start_date']) if d.get('start_date') else None,note=text(d.get('note'),500,'',False),status='ACTIVE',created_at=now()))
            return 'Thêm nơi giữ '+name
        if action=='crypto-place-archive':
            p=self.crypto_place(s,d.get('place'));p.update(status='ARCHIVED',archive_reason=text(d.get('reason'),500,'Cần lý do lưu trữ.'),archived_at=now());return 'Lưu trữ nơi giữ '+p['name']
        if action=='crypto-balance':
            p=self.crypto_place(s,d.get('place'));bucket=d.get('bucket')
            require(bucket in (WALLET_BUCKETS if p['kind']=='WALLET' else tuple(BUCKETS)),'Trạng thái không hợp lệ với loại nơi giữ (ví riêng chỉ có "đang giữ").')
            qty=decimals(d.get('quantity'),18,'Số lượng tối đa 18 chữ số thập phân.');require(qty>=0,'Số lượng không âm.')
            when=day(d.get('date'));require(not p['start_date'] or when>=p['start_date'],'Ngày xác nhận không được trước mốc bắt đầu theo dõi của nơi giữ.')
            c['balances'].append(dict(id=uid(),place=p['id'],ticker=norm_ticker(d.get('ticker')),network=norm_network(d.get('network')),bucket=bucket,quantity=S(qty),date=when,source=text(d.get('source'),500,'Cần ghi nguồn xác nhận (ảnh chụp, mã giao dịch, ghi chú).'),status='ACTIVE',created_at=now()))
            return f"Xác nhận số dư {norm_ticker(d.get('ticker'))} tại {p['name']}"
        if action=='crypto-balance-void':
            b=self.crypto_pick(c['balances'],d.get('balance'),'lần xác nhận');require(b['status']=='ACTIVE','Lần xác nhận đã hủy.')
            b.update(status='VOID',void_reason=text(d.get('reason'),500,'Cần lý do hủy.'),voided_at=now());return 'Hủy lần xác nhận, giữ bản ghi'
        if action in {'crypto-price','crypto-capital'}:
            kind='prices' if action=='crypto-price' else 'capitals';field='price' if kind=='prices' else 'amount'
            value=decimals(d.get(field),12,'Tối đa 12 chữ số thập phân.');require(value>0,'Giá trị phải lớn hơn 0.')
            ticker=norm_ticker(d.get('ticker'))
            c[kind].append(dict(id=uid(),ticker=ticker,network=norm_network(d.get('network')),**{field:S(value)},date=day(d.get('date')),source=text(d.get('source'),500,'Cần ghi nguồn.'),status='ACTIVE',created_at=now()))
            return ('Nhập giá ' if kind=='prices' else 'Ghi vốn ')+ticker
        if action in {'crypto-price-void','crypto-capital-void'}:
            kind='prices' if action=='crypto-price-void' else 'capitals';key='price' if kind=='prices' else 'capital'
            row=self.crypto_pick(c[kind],d.get(key),'bản ghi');require(row['status']=='ACTIVE','Bản ghi đã hủy.')
            row.update(status='VOID',void_reason=text(d.get('reason'),500,'Cần lý do hủy.'),voided_at=now());return 'Hủy bản ghi, giữ lịch sử'
        require(False,'Hành động không hợp lệ.')

    # ---- derived view --------------------------------------------------------
    def crypto_view(self,s):
        with localcontext() as ctx:
            ctx.prec=60
            s=copy.deepcopy(s);c=crypto_state(s)
            def current(items,key):
                groups={}
                for x in items:
                    if x['status']=='ACTIVE':groups.setdefault(key(x),[]).append(x)
                return {k:latest(v) for k,v in groups.items()}
            prices=current(c['prices'],lambda x:coin_key(x['ticker'],x['network']))
            capitals=current(c['capitals'],lambda x:coin_key(x['ticker'],x['network']))
            places=[];coin_qty={};coin_places={};total=Decimal(0)
            for p in c['places']:
                mine=[b for b in c['balances'] if b['place']==p['id']]
                cur=current(mine,lambda b:(coin_key(b['ticker'],b['network']),b['bucket']))
                components=[];positions=[];debts=[];value=Decimal(0)
                for (key,bucket),b in sorted(cur.items()):
                    row=dict(balance=b['id'],coin=key,ticker=b['ticker'],network=b['network'],bucket=bucket,bucket_label=BUCKETS[bucket],quantity=b['quantity'],date=b['date'],source=b['source'])
                    if bucket=='OPEN_POSITION':positions.append(row);continue
                    if bucket=='MARGIN_DEBT':debts.append(row);continue
                    pr=prices.get(key)
                    if pr:row['value']=S((D(b['quantity'])*D(pr['price'])).quantize(Q6,rounding=ROUND_HALF_UP));row['price']=pr['price']
                    else:row['value']=None
                    components.append(row)
                    if p['status']=='ACTIVE':
                        coin_qty[key]=coin_qty.get(key,Decimal(0))+D(b['quantity']);coin_places.setdefault(key,set()).add(p['name'])
                        if pr:value+=D(row['value'])
                if p['status']=='ACTIVE':total+=value
                places.append(dict(p,components=components,positions=positions,debts=debts,asset_value=S(value),history=sorted(mine,key=lambda b:(b['date'],b['created_at']),reverse=True)))
            for pl in places:
                pl['weight']=S((D(pl['asset_value'])/total*100).quantize(Q2,rounding=ROUND_HALF_UP)) if total>0 and pl['status']=='ACTIVE' and D(pl['asset_value'])>0 else (S(Decimal('0.00')) if pl['status']=='ACTIVE' and total>0 else None)
            coins=[];unpriced=[]
            for key,qty in sorted(coin_qty.items()):
                ticker,network=key.split('|');pr=prices.get(key);cap=capitals.get(key)
                value=(qty*D(pr['price'])).quantize(Q6,rounding=ROUND_HALF_UP) if pr else None
                gap=dict(amount=S(value-D(cap['amount'])),label=GAP_LABEL) if (pr and cap) else None
                coins.append(dict(key=key,ticker=ticker,network=network,quantity=S(qty),places=sorted(coin_places[key]),price=pr,value=S(value) if value is not None else None,
                    weight=S((value/total*100).quantize(Q2,rounding=ROUND_HALF_UP)) if (value is not None and total>0) else None,capital=cap,gap=gap))
                if not pr:unpriced.append(key)
            return dict(places=places,coins=coins,totals=dict(value=S(total),unit='USDT',unpriced=unpriced,denominator='Tổng giá trị các coin có giá ở các nơi giữ đang hoạt động (USDT).'),
                prices=sorted(c['prices'],key=lambda x:(x['date'],x['created_at']),reverse=True),capitals=sorted(c['capitals'],key=lambda x:(x['date'],x['created_at']),reverse=True),
                buckets=BUCKETS,gap_label=GAP_LABEL,components_note=COMPONENTS_NOTE,draft=True)
