"""Asset overview: read-only consolidation of existing modules into separate VND and USDT blocks, plus immutable snapshots.

Never converts currencies, never accrues interest and never nets a mortgage against a property: it only restates numbers
that other modules already hold, with the basis and the reliability warnings made explicit.
"""
import copy
from decimal import Decimal, localcontext, ROUND_HALF_UP
from .core import require, digest
from .product import D, S, uid

Q2=Decimal('0.01')
NEGATIVE_LABEL='Nợ lớn hơn tài sản'
NOTES=['Không quy đổi giữa VND và USDT; mỗi đồng tiền là một khối riêng.','Phải thu/phải trả chỉ gồm gốc theo dữ liệu Công nợ (nháp); lãi ghi theo tiền thực thu, không dồn tích.','Khoản vay thế chấp chỉ nằm ở nợ, không trừ vào giá trị bất động sản; nợ margin và vị thế sàn không cộng hay trừ.','Số dư ngân hàng theo dữ liệu nguồn đã ghi, chưa phải số dư đã đối soát.']

def asset_state(s):
    s.setdefault('asset_snapshots',[]);return s

def N(value):
    value=D(value) if not isinstance(value,Decimal) else value
    return '0' if value==0 else S(value.normalize())

class AssetOverview:
    def asset_group(self,key,label,target,value=None,has_data=False,basis='',as_of=None,detail=None):
        return dict(key=key,label=label,target=target,has_data=has_data,value=N(value) if (value is not None and has_data) else None,basis=basis,as_of=as_of,detail=detail or [],weight=None)

    def asset_core(self,s):
        """Current consolidated numbers (no snapshots/deltas)."""
        with localcontext() as ctx:
            ctx.prec=60
            active=[a for a in s['accounts'] if a.get('status','ACTIVE')=='ACTIVE']
            # ---- VND ----------------------------------------------------
            bank_rows=[];bank_total=Decimal(0);unclassified=gaps=0;as_of=None
            for a in active:
                r=self.report(s,a['id']);bank_total+=D(r['balance']);unclassified+=r['unknown_count'];gaps+=len(r['coverage_gaps'])
                if r['source_end']:as_of=max(as_of or '',r['source_end'])
                bank_rows.append(dict(account=a['id'],name=a['name'],balance=r['balance'],source_end=r['source_end'],unclassified=r['unknown_count']))
            debts=self.debt_register(s);people=debts['people']
            loans=[l for l in debts['loans']];setup_loans=[l for l in loans if l['setup']]
            receivable=sum((D(p['receivable']) for p in people),Decimal(0));payable=sum((D(p['payable']) for p in people),Decimal(0))
            loan_issues=sum(p['excluded_count'] for p in people)
            realty=self.realty_view(s);realty_rows=[];by_basis={'VALUE':Decimal(0),'COST':Decimal(0)};none=[];realty_total=Decimal(0)
            for p in realty['properties']:
                cur=p['valuation']['current'];net=D(p['capital']['basis'])
                if cur:basis,value='VALUE',D(cur['value'])
                elif net>0:basis,value='COST',net
                else:basis,value='NONE',None
                if value is None:none.append(dict(id=p['id'],name=p['name']))
                else:by_basis[basis]+=value;realty_total+=value
                realty_rows.append(dict(id=p['id'],name=p['name'],basis=basis,value=N(value) if value is not None else None,date=cur['date'] if cur else None,capital_net=p['capital']['basis']))
            vnd_assets=[self.asset_group('bank','Tiền ngân hàng','account',bank_total,bool(active),'Theo dữ liệu nguồn đã ghi'+(f' đến ngày {as_of}' if as_of else ''),as_of,bank_rows),
                self.asset_group('receivable','Phải thu (gốc cho vay)','debts',receivable,bool(setup_loans),'Gốc theo dữ liệu Công nợ, không gồm lãi'),
                self.asset_group('realty','Bất động sản','realty',realty_total if realty['properties'] else None,bool(realty['properties']),'Giá trị hiện tại nếu đã nhập; chưa có thì giá gốc (vốn đã thanh toán ròng + chi phí mua vốn hóa ròng), chưa định giá',None,realty_rows)]
            vnd_assets[2]['by_basis']={k:N(v) for k,v in by_basis.items()}
            vnd_liab=[self.asset_group('payable','Phải trả (gốc đi vay)','debts',payable,bool(setup_loans),'Gốc theo dữ liệu Công nợ, gồm khoản vay thế chấp')]
            # ---- USDT ---------------------------------------------------
            crypto=self.crypto_view(s);trx=self.trx_view(s)
            places=[p for p in crypto['places'] if p['status']=='ACTIVE' and p['components']]
            usdt_assets=[self.asset_group('crypto','Crypto (coin có giá)','crypto',D(crypto['totals']['value']),bool(places),'Giá USDT nhập tay; vị thế đang mở và nợ margin không tính',None,[dict(key=c['key'],value=c['value']) for c in crypto['coins'] if c['value'] is not None]),
                self.asset_group('trx_receivable','Phải thu khách TRX / Energy','trx',D(trx['totals']['outstanding']),bool(trx['customers']),'Còn nợ theo đơn còn hiệu lực (USDT)')]
            usdt_liab=[self.asset_group('trx_advance','Tiền khách nhận trước (chờ phân bổ)','trx',D(trx['totals']['unallocated']),bool(trx['customers']),'Tiền đã nhận chưa phân bổ vào đơn; chưa là doanh thu')]
            def block(assets,liab):
                total=sum((D(g['value']) for g in assets if g['value'] is not None),Decimal(0));debt=sum((D(g['value']) for g in liab if g['value'] is not None),Decimal(0))
                for g in assets:
                    if g['value'] is not None and total>0:g['weight']=S((D(g['value'])/total*100).quantize(Q2,rounding=ROUND_HALF_UP))
                net=total-debt
                return dict(assets=dict(total=N(total),groups=assets),liabilities=dict(total=N(debt),groups=liab),net=dict(value=N(net),label=NEGATIVE_LABEL if net<0 else None),has_data=any(g['has_data'] for g in assets+liab))
            unpriced=len(crypto['totals']['unpriced'])
            warnings=[]
            def warn(code,label,count,target):
                if count:warnings.append(dict(code=code,label=label,count=count,target=target))
            warn('UNCLASSIFIED','Giao dịch ngân hàng chưa phân loại (có thể ảnh hưởng vốn BĐS và công nợ)',unclassified,'account');warn('COVERAGE_GAPS','Khoảng chưa có nguồn ngân hàng',gaps,'account')
            warn('LOAN_ISSUES','Khoản vay lỗi hoặc chưa thiết lập (không vào phải thu/phải trả)',loan_issues,'debts');warn('UNPRICED_COIN','Coin chưa có giá (không vào giá trị crypto)',unpriced,'crypto')
            warn('REALTY_COST_BASIS','Bất động sản tính theo giá gốc, chưa định giá',sum(1 for r in realty_rows if r['basis']=='COST'),'realty');warn('REALTY_NO_VALUE','Bất động sản chưa có giá trị (ngoài tổng)',len(none),'realty')
            return dict(currencies=dict(VND=block(vnd_assets,vnd_liab),USDT=block(usdt_assets,usdt_liab)),warnings=warnings,realty_basis=dict(rows=realty_rows,none=none),notes=NOTES,as_of=as_of)

    def asset_delta(self,now,before):
        out={}
        for cur in ('VND','USDT'):
            n,b=now['currencies'][cur],before['currencies'][cur]
            out[cur]=dict(assets=N(D(n['assets']['total'])-D(b['assets']['total'])),liabilities=N(D(n['liabilities']['total'])-D(b['liabilities']['total'])),net=N(D(n['net']['value'])-D(b['net']['value'])))
        return out

    def asset_view(self,s):
        with localcontext() as ctx:
            ctx.prec=60
            s=asset_state(copy.deepcopy(s));core=self.asset_core(s);snaps=sorted(s['asset_snapshots'],key=lambda x:x['at'])
            listed=[]
            for i,sn in enumerate(snaps):
                prev=snaps[i-1] if i else None
                listed.append(dict(sn,delta_vs_previous=self.asset_delta(sn['data'],prev['data']) if prev else None))
            latest=snaps[-1] if snaps else None
            commit=[(x['name'],D(x['progress']['summary']['remaining'])) for x in self.realty_view(s)['properties'] if x['progress']['summary']['remaining'] not in ('0',0)]
            commitments=dict(VND=N(sum((v for _,v in commit),Decimal(0))),properties=[dict(name=n,remaining=N(v)) for n,v in commit if v>0],note='Cam kết chưa thanh toán theo hợp đồng BĐS; không cộng vào nợ và không trừ giá trị BĐS.')
            return dict(core,commitments=commitments,snapshots=list(reversed(listed)),delta=dict(vs=latest['id'],vs_at=latest['at'],**self.asset_delta(core,latest['data'])) if latest else None,draft=True)

    def change_assets(self,s,action,d):
        from .p01 import now
        asset_state(s)
        if action=='assets-snapshot':
            note=str(d.get('note') or '').strip()[:500]
            snap=dict(id=uid(),at=now(),note=note,actor='Thạch',data=self.asset_core(s))
            snap['hash']=digest(snap);s['asset_snapshots'].append(snap)
            return 'Lưu bản chụp tổng tài sản'+(': '+note if note else '')
        require(False,'Hành động không hợp lệ.')
