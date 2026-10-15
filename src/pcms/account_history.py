"""Read-only statement history of one account, anchored on the latest snapshot milestone (R111-R114).

Nothing here changes data: it restates recorded transactions in chain order, lists the source files and says how
staged files relate to the last recorded transaction (continuity by running balance, spec 022).
"""
import copy
from decimal import Decimal, localcontext
from .core import require
from .product import D, S, item
from .categories import ROOTS, root_key

def label_of(self,s,t,profiles):
    if not t['allocations'] or any(p['category']=='unknown' for p in t['allocations']):return 'Chưa phân loại'
    names=[]
    for p in t['allocations']:
        node=p.get('node');base=self.cat_path(s,node) if node else ROOTS[root_key(p['category'])]
        obj=profiles.get(p.get('profile'));name=base+(' · '+obj if obj else '')
        if name not in names:names.append(name)
    return ' + '.join(names)

class AccountHistory:
    def account_history(self,d,s=None):
        from .p01 import day,display_day
        with localcontext() as ctx:
            ctx.prec=60
            s=copy.deepcopy(s or self.state());account=d.get('account');a=next((x for x in s['accounts'] if x['id']==account),None);require(a is not None,'Chọn tài khoản.')
            scope=d.get('scope') or 'milestone';require(scope in {'milestone','all'},'Phạm vi không hợp lệ.')
            try:limit=10 if d.get('limit') in (None,'') else int(d['limit']);offset=0 if d.get('offset') in (None,'') else int(d['offset'])
            except (TypeError,ValueError):raise_(' Số dòng/trang không hợp lệ.')
            require(1<=limit<=200 and offset>=0,'Số dòng mỗi trang từ 1 đến 200.')
            start=d.get('start') or None;end=d.get('end') or None
            if start:day(start)
            if end:day(end)
            require(not(start and end) or start<=end,'Ngày kết thúc không được trước ngày bắt đầu.')
            direction=d.get('direction') or '';require(direction in {'','IN','OUT'},'Chiều tiền không hợp lệ.')
            txs=sorted([t for t in s['transactions'] if t['account']==a['id']],key=lambda t:t['order']);profiles={p['id']:p['name'] for p in s['profiles']}
            snaps=[x for x in s['snapshots'] if x['account']==a['id']];latest=snaps[-1] if snaps else None;ms=latest.get('milestone') if latest else None
            tail=txs[-1] if txs else None;balance=D(a['opening'])+sum((D(t['signed_amount']) for t in txs),Decimal(0))
            anchor_order=ms['anchor']['order'] if ms and ms.get('anchor') else None
            if ms and ms.get('anchor'):reference=dict(kind='MILESTONE',reference=ms['anchor']['reference'],date=ms['anchor']['date'],balance=ms['balance'])
            elif tail:reference=dict(kind='LAST_TRANSACTION',reference=tail['reference'],date=tail['date'],balance=S(balance))
            else:reference=dict(kind='NONE',reference=None,date=None,balance=S(balance))
            since=None
            if anchor_order is not None:
                later=[t for t in txs if t['order']>anchor_order];since=dict(count=len(later),unclassified=sum(1 for t in later if not t['allocations'] or any(p['category']=='unknown' for p in t['allocations'])))
            files_by={b['id']:b for b in s['imports'] if b['account']==a['id']}
            running=D(a['opening']);rows=[]
            for t in txs:
                running+=D(t['signed_amount']);after=anchor_order is not None and t['order']>anchor_order
                if scope=='milestone' and after:continue
                if (start and t['date']<start) or (end and t['date']>end):continue
                incoming=D(t['signed_amount'])>0
                if direction=='IN' and not incoming or direction=='OUT' and incoming:continue
                src=t.get('sources',[]);first=files_by.get(src[0]['batch']) if src else None
                rows.append(dict(transaction=t['id'],date=t['date'],reference=t['reference'],description=t['description'],amount=S(abs(D(t['signed_amount']))),direction='IN' if incoming else 'OUT',
                    balance=t.get('reported_balance') or S(running),label=label_of(self,s,t,profiles),status='APPROVED' if any(any(x['id']==t['id'] for x in sn['report']['transactions']) for sn in snaps) else 'DRAFT',
                    sources=len(src),file=first['filename'] if first else None,note=t.get('note',''),voucher=t.get('voucher',''),after_milestone=after,_order=t['order']))
            total=len(rows);tin=sum((D(r['amount']) for r in rows if r['direction']=='IN'),Decimal(0));tout=sum((D(r['amount']) for r in rows if r['direction']=='OUT'),Decimal(0))
            rows.sort(key=lambda r:r['_order'],reverse=True);page=rows[offset:offset+limit]
            for r in page:r.pop('_order')
            files=[]
            published_orders={}
            for t in txs:
                for x in t.get('sources',[])[:1]:published_orders.setdefault(x['batch'],[]).append(t['order'])
            for b in sorted(files_by.values(),key=lambda b:(b.get('period_start') or '',b['imported_at'])):
                orders=published_orders.get(b['id'],[])
                files.append(dict(id=b['id'],filename=b['filename'],period_start=b.get('period_start'),period_end=b.get('period_end'),rows=len(b['rows']),status=b['status'],new_count=b.get('new_count'),duplicate_count=b.get('duplicate_count'),
                    source_opening=b.get('source_opening'),source_closing=b.get('source_closing'),after_milestone=(b['status']!='PUBLISHED') or (anchor_order is not None and any(o>anchor_order for o in orders))))
            continuity=[]
            for b in files_by.values():
                if b['status'] not in {'STAGED','BLOCKED'}:continue
                issues,new,dups=self.check_batch(s,b);link='NONE'
                if tail and any(r['reference']==tail['reference'] for r,_ in dups):link='CONTAINS_TAIL'
                elif D(b['source_opening'])==balance if b.get('source_opening') is not None else False:link='OPENING_MATCH'
                after=balance+sum((D(r['signed_amount']) for r in new),Decimal(0))
                continuity.append(dict(batch=b['id'],filename=b['filename'],status=b['status'],link=link,ok=not issues,issues=issues,new_count=len(new),duplicate_count=len(dups),expected_opening=S(balance),
                    file_opening=b.get('source_opening'),file_closing=b.get('source_closing'),closing_ok=bool(b.get('source_closing') is not None and after==D(b['source_closing']))))
            return dict(account=dict(id=a['id'],name=a['name'],reference=a['reference'],opening=a['opening'],tracking_date=a['effective_date']),milestone=ms,reference=reference,
                tail=dict(reference=tail['reference'],date=tail['date'],balance=S(balance)) if tail else None,since_milestone=since,files=files,rows=page,total=total,totals={'in':S(tin),'out':S(tout)},
                page=dict(limit=limit,offset=offset,has_more=offset+limit<total),scope=scope,filters=dict(start=start,end=end,direction=direction),continuity=continuity,draft=True)

    def source_preview(self,d,s=None):
        """Preview, read-only, of the rows a staged file would append to the balance chain (R115-R117)."""
        from .p01 import display_day
        with localcontext() as ctx:
            ctx.prec=60
            s=copy.deepcopy(s or self.state());b=item(s['imports'],d.get('batch'));a=item(s['accounts'],b['account'])
            require(b['status']=='STAGED','Chỉ xem trước được file hợp lệ đang chờ ghi.')
            issues,new,dups=self.check_batch(s,b);require(not issues,'File còn lỗi, không có xem trước: '+'; '.join(issues))
            existing=sorted([t for t in s['transactions'] if t['account']==a['id']],key=lambda t:t['order']);tail=existing[-1] if existing else None
            balance=D(a['opening'])+sum((D(t['signed_amount']) for t in existing),Decimal(0))
            anchor=dict(kind='LAST_TRANSACTION',reference=tail['reference'],date=tail['date'],description=tail['description'],balance=S(balance)) if tail else dict(kind='OPENING',reference=None,date=a['effective_date'],description='Số dư đầu tài khoản',balance=S(balance))
            new_ids={id(r) for r in new};rows=[];running=balance;tin=tout=Decimal(0)
            for r in b['rows']:
                if id(r) not in new_ids:continue
                amount=D(r['signed_amount']);running+=amount
                if amount>0:tin+=amount
                else:tout+=-amount
                rows.append(dict(source_row=r['source_row'],date=r['date'],reference=r['reference'],description=r['description'],amount=S(abs(amount)),direction='IN' if amount>0 else 'OUT',
                    reported_balance=r['reported_balance'],computed_balance=S(running),ok=r['reported_balance'] is not None and D(r['reported_balance'])==running))
            closing_ok=b.get('source_closing') is not None and (running==D(b['source_closing']) if rows else True)
            return dict(batch=b['id'],filename=b['filename'],account=a['id'],anchor=anchor,rows=rows,new_count=len(rows),duplicate_count=len(dups),totals={'in':S(tin),'out':S(tout)},
                expected_closing=S(running),file_closing=b.get('source_closing'),closing_ok=closing_ok,all_ok=closing_ok and all(r['ok'] for r in rows),draft=True)

def raise_(message):require(False,message)
