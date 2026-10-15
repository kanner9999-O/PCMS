"""Migrate legacy transaction history pasted from a spreadsheet into a category object (R129-R134).

The rows live outside the bank-statement chain: they feed the category/object totals and history only, never account balances,
milestones or reconciliation. Rows whose reference already exists in a bank statement are left out of the totals automatically.
"""
import copy
import hashlib
import re
from datetime import date as _date
from decimal import Decimal, localcontext
from .core import require
from .product import S, uid, item
from .categories import ROOTS, cat_state, norm_name

DEFAULT_MAPPING=['date','description','reference','out','in','balance']
ROLES={'date','description','reference','out','in','amount','balance','skip'}

def norm_ref(value):
    return str(value or '').split('\\')[0].strip().upper()

def parse_date(cell):
    c=cell.strip()
    m=re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})',c)
    if m:d,mo,y=int(m.group(1)),int(m.group(2)),int(m.group(3))
    else:
        m=re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})',c)
        require(m is not None,'Ngày không đúng dạng dd/mm/yyyy.');y,mo,d=int(m.group(1)),int(m.group(2)),int(m.group(3))
    try:return _date(y,mo,d).isoformat()
    except ValueError:raise ValueError('Ngày không hợp lệ.')

def parse_num(cell,signed=False):
    c=cell.replace(' ','').replace(' ','')
    if not c:return None
    if re.fullmatch(r'-?\d{1,3}(\.\d{3})+',c):c=c.replace('.','')
    c=c.replace(',','')
    try:value=Decimal(c)
    except Exception:raise ValueError(f'Số không hợp lệ: {cell}')
    if not value.is_finite() or value!=value.to_integral_value():raise ValueError(f'Chỉ nhận số nguyên VND: {cell}')
    if value<0 and not signed:raise ValueError(f'Số tiền không âm: {cell}')
    return int(value)

class LegacyImport:
    def legacy_bank_refs(self,s):
        return {norm_ref(t['reference']) for t in s['transactions'] if norm_ref(t['reference'])}

    def legacy_items(self,s):
        """Pseudo transactions (and their single part) for active, not-in-statement legacy rows."""
        batches={b['id'] for b in s.get('legacy_batches',[]) if b['status']=='ACTIVE'}
        if not batches:return
        refs=self.legacy_bank_refs(s);nodes={n['id']:n for n in s.get('categories',[])}
        for e in s.get('legacy_entries',[]):
            if e['batch'] not in batches:continue
            ref=norm_ref(e['reference'])
            if ref and ref in refs:continue
            key=e['category'];part={'category':key,'amount':e['amount'],'profile':e['profile']}
            if key not in ROOTS:
                node=nodes.get(key)
                if node is None:continue
                part['category']=node['root'];part['node']=key
            t=dict(id=e['id'],account=None,date=e['date'],reference=e['reference'] or '—',description=e['description'],signed_amount=e['amount'] if e['direction']=='IN' else '-'+e['amount'],
                allocations=[part],sources=[],legacy=True,order=0,classification_history=[],source_row=e['row'],bank_balance=e.get('bank_balance'))
            yield t,part

    def legacy_parse(self,text,mapping=None):
        lines=text.replace('\r\n','\n').replace('\r','\n').split('\n')
        rows=[(i+1,[c.strip() for c in line.split('\t')]) for i,line in enumerate(lines)];rows=[(n,r) for n,r in rows if any(r)]
        require(rows,'Không có dòng dữ liệu nào.')
        cols=max(len(r) for _,r in rows)
        if mapping is None:mapping=DEFAULT_MAPPING[:cols]+['skip']*max(0,cols-len(DEFAULT_MAPPING))
        require(isinstance(mapping,list) and mapping and all(m in ROLES for m in mapping),'Ánh xạ cột không hợp lệ.')
        for role in ROLES-{'skip'}:require(mapping.count(role)<=1,'Mỗi vai trò cột chỉ chọn một lần.')
        require('date' in mapping and ('amount' in mapping or 'out' in mapping or 'in' in mapping),'Cần cột ngày và cột tiền (ra/vào hoặc số tiền có dấu).')
        out_rows=[];issues=[];declared=None
        def cell(r,role):
            i=mapping.index(role) if role in mapping else None
            return r[i] if i is not None and i<len(r) else ''
        for n,r in rows:
            d=cell(r,'date');desc=cell(r,'description');ref=cell(r,'reference')
            try:
                vals={k:parse_num(cell(r,k),signed=(k=='amount')) for k in ('out','in','amount','balance')}
            except ValueError as exc:
                issues.append(dict(row=n,message=str(exc)));out_rows.append(dict(row=n,status='ERROR',message=str(exc),date=d,description=desc,reference=ref,amount=None,direction=None,bank_balance=None));continue
            if not d:
                if not desc and not ref and any(v is not None for k,v in vals.items() if k!='balance'):
                    if declared is None:declared={'out':vals['out'] or 0,'in':vals['in'] or 0}
                    continue
                msg='Thiếu ngày.';issues.append(dict(row=n,message=msg));out_rows.append(dict(row=n,status='ERROR',message=msg,date=d,description=desc,reference=ref,amount=None,direction=None,bank_balance=vals['balance']));continue
            try:iso=parse_date(d)
            except Exception as exc:
                msg=str(exc).replace('Ngày không hợp lệ.','Ngày không hợp lệ.');issues.append(dict(row=n,message=msg));out_rows.append(dict(row=n,status='ERROR',message=msg,date=d,description=desc,reference=ref,amount=None,direction=None,bank_balance=vals['balance']));continue
            if 'amount' in mapping and vals['amount'] is not None:
                amount=abs(vals['amount']);direction='IN' if vals['amount']>0 else 'OUT';bad=amount==0
            else:
                o,i_=vals['out'] or 0,vals['in'] or 0;bad=(o>0)==(i_>0)       # cả hai hoặc không có số nào
                amount=o or i_;direction='OUT' if o>0 else 'IN'
            if bad:
                msg='Dòng cần đúng một trong tiền ra hoặc tiền vào (lớn hơn 0).';issues.append(dict(row=n,message=msg));out_rows.append(dict(row=n,status='ERROR',message=msg,date=iso,description=desc,reference=ref,amount=None,direction=None,bank_balance=vals['balance']));continue
            out_rows.append(dict(row=n,status='OK',date=iso,description=desc[:500],reference=ref[:100],amount=str(amount),direction=direction,bank_balance=str(vals['balance']) if vals['balance'] is not None else None))
        return dict(columns=cols,mapping=mapping,rows=out_rows,issues=issues,declared=declared)

    def legacy_preview(self,d,s=None):
        with localcontext() as ctx:
            ctx.prec=60
            s=copy.deepcopy(s or self.state());cat_state(s);s.setdefault('legacy_batches',[]);s.setdefault('legacy_entries',[])
            key=d.get('category');self.cat_target_root(s,key)
            text=str(d.get('text') or '');require(text.strip(),'Dán dữ liệu copy từ Google Sheets.');require(len(text)<=2_000_000,'Dữ liệu dán quá lớn.')
            parsed=self.legacy_parse(text,d.get('mapping'))
            pid=d.get('profile') or None;name=str(d.get('name') or '').strip()
            if pid:prof=item(s['profiles'],pid)
            else:
                require(1<=len(name)<=100,'Chọn đối tượng có sẵn hoặc nhập tên đối tượng mới (1–100 ký tự).')
                prof=next((x for x in s['profiles'] if x['kind']=='OBJECT' and norm_name(x['name'])==norm_name(name)),None)
            active={b['id'] for b in s['legacy_batches'] if b['status']=='ACTIVE'}
            seen={(norm_ref(e['reference']),e['date'],e['amount'],e['direction']) for e in s['legacy_entries'] if e['batch'] in active and prof and e['profile']==prof['id'] and norm_ref(e['reference'])}
            bank=self.legacy_bank_refs(s);tin=tout=0;matched=dups=0;rows=parsed['rows']
            for r in rows:
                if r['status']!='OK':continue
                amt=int(r['amount']);tin+=amt if r['direction']=='IN' else 0;tout+=amt if r['direction']=='OUT' else 0
                ref=norm_ref(r['reference']);k=(ref,r['date'],r['amount'],r['direction'])
                if ref and k in seen:r['status']='DUPLICATE';dups+=1;continue
                if ref:seen.add(k)
                if ref and ref in bank:r['status']='MATCHED_BANK';matched+=1
            declared=parsed['declared'];totals_ok=None if declared is None else (declared['in']==tin and declared['out']==tout)
            importable=sum(1 for r in rows if r['status'] in {'OK','MATCHED_BANK'})
            return dict(columns=parsed['columns'],mapping=parsed['mapping'],rows=rows,issues=parsed['issues'],totals={'in':str(tin),'out':str(tout)},declared={k:str(v) for k,v in declared.items()} if declared else None,totals_ok=totals_ok,
                importable=importable,matched_bank=matched,duplicates=dups,object=dict(profile=prof['id'] if prof else None,name=prof['name'] if prof else name,exists=bool(prof)),can_import=not parsed['issues'] and importable>0 and totals_ok is not False,needs_confirm=totals_ok is False and not parsed['issues'],draft=True)

    def change_legacy(self,s,action,d):
        from .p01 import now
        cat_state(s);s.setdefault('legacy_batches',[]);s.setdefault('legacy_entries',[])
        if action=='legacy-import':
            p=self.legacy_preview(d,s);require(not p['issues'],'Còn dòng lỗi: sửa dữ liệu dán rồi xem trước lại.');require(p['importable']>0,'Không có dòng mới để nhập.')
            require(p['totals_ok'] is not False or d.get('accept_total_mismatch') is True,'Tổng các dòng lệch dòng tổng; xác nhận rõ nếu vẫn muốn nhập.')
            key=d['category']
            if p['object']['exists']:prof=item(s['profiles'],p['object']['profile'])
            else:
                prof={'id':uid(),'kind':'OBJECT','name':p['object']['name'],'party':None};s['profiles'].append(prof)
            if not any(e['category']==key and e['profile']==prof['id'] and e['status']=='ACTIVE' for e in s['category_objects']):
                s['category_objects'].append(dict(id=uid(),category=key,profile=prof['id'],status='ACTIVE',created_at=now(),history=[dict(at=now(),action='ADD',to=key)]))
            text=str(d['text']);bid=uid()
            s['legacy_batches'].append(dict(id=bid,at=now(),source_text=text,sha256=hashlib.sha256(text.encode('utf-8')).hexdigest(),category=key,profile=prof['id'],mapping=p['mapping'],rows=p['importable'],
                totals=p['totals'],declared=p['declared'],accepted_mismatch=p['totals_ok'] is False,status='ACTIVE'))
            n=0
            for r in p['rows']:
                if r['status'] not in {'OK','MATCHED_BANK'}:continue
                s['legacy_entries'].append(dict(id=uid(),batch=bid,row=r['row'],date=r['date'],description=r['description'],reference=r['reference'],amount=r['amount'],direction=r['direction'],bank_balance=r['bank_balance'],category=key,profile=prof['id']));n+=1
            return f"Migrate {n} dòng lịch sử cũ cho {prof['name']}"+(f"; bỏ qua {p['duplicates']} dòng trùng lần trước" if p['duplicates'] else '')
        if action=='legacy-void':
            b=item(s['legacy_batches'],d.get('batch'));require(b['status']=='ACTIVE','Lần migrate đã hủy.');reason=str(d.get('reason','')).strip();require(reason,'Cần lý do hủy.')
            b.update(status='VOID',void_reason=reason[:500],voided_at=now());return 'Hủy lần migrate, giữ bản ghi và bản dán gốc'
        require(False,'Hành động không hợp lệ.')
