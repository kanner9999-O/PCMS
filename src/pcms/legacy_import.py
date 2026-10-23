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
ROLES={'date','description','reference','out','in','amount','balance','note','skip'}

def norm_ref(value):
    return str(value or '').strip().upper()

def base_ref(value):
    """Reference without the bank suffix after a backslash (FT…\\BNK → FT…); only used to flag near-duplicates and old unresolved rows."""
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
    def legacy_account(self,s,e):
        return next((b.get('account') for b in s.get('legacy_batches',[]) if b['id']==e['batch']),None)

    def legacy_identity_status(self,s):
        """Status of every active legacy row under the identity rule (account + full normalized reference, R192/R193).
        ACTIVE: counted; DUPLICATE / MATCHED_BANK: same identity and same content already recorded (not counted again);
        CONFLICT: same identity, different content; NEAR_DUPLICATE: same account, reference differs only by suffix (both not counted, need review); UNRESOLVED(_MATCH): no account yet (old data, provisional)."""
        active={b['id'] for b in s.get('legacy_batches',[]) if b['status']=='ACTIVE'}
        seen={};result={};near={(t['account'],base_ref(t['reference'])):norm_ref(t['reference']) for t in s['transactions'] if norm_ref(t['reference'])}
        for t in s['transactions']:
            seen[(t['account'],norm_ref(t['reference']))]=((t['date'],str(abs(Decimal(t['signed_amount']))),'IN' if Decimal(t['signed_amount'])>0 else 'OUT',t['description']),'MATCHED_BANK')
        for e in s.get('legacy_entries',[]):
            if e['batch'] not in active:continue
            account=self.legacy_account(s,e);ref=norm_ref(e['reference'])
            if not account or not ref:
                # Dữ liệu cũ chưa có tài khoản: giữ cách tính tạm như trước (ẩn nếu mã gốc trùng sao kê) cho tới khi người dùng xác định tài khoản.
                result[e['id']]='UNRESOLVED_MATCH' if base_ref(e['reference']) and any(base_ref(t['reference'])==base_ref(e['reference']) for t in s['transactions']) else 'UNRESOLVED'
                continue
            key=(account,ref);payload=(e['date'],e['amount'],e['direction'],e['description'])
            if key in seen:result[e['id']]=seen[key][1] if seen[key][0]==payload else 'CONFLICT'
            elif (account,base_ref(e['reference'])) in near and near[(account,base_ref(e['reference']))]!=ref:result[e['id']]='NEAR_DUPLICATE'     # gần trùng khác hậu tố với nguồn khác cùng tài khoản: không tự gộp, không cộng, cần đối chiếu
            else:seen[key]=(payload,'DUPLICATE');near.setdefault((account,base_ref(e['reference'])),ref);result[e['id']]='ACTIVE'
        return result

    def legacy_items(self,s):
        """Only resolved unique rows count; unresolved history is explicitly reported separately."""
        statuses=self.legacy_identity_status(s);nodes={n['id']:n for n in s.get('categories',[])}
        for e in s.get('legacy_entries',[]):
            if statuses.get(e['id']) not in {'ACTIVE','UNRESOLVED'}:continue
            key=e['category'];part={'category':key,'amount':e['amount'],'profile':e['profile']}
            if key not in ROOTS:
                node=nodes.get(key)
                if node is None:continue
                part['category']=node['root'];part['node']=key
            t=dict(id=e['id'],account=self.legacy_account(s,e),date=e['date'],reference=e['reference'],description=e['description'],signed_amount=e['amount'] if e['direction']=='IN' else '-'+e['amount'],
                allocations=[part],sources=[],legacy=True,order=0,classification_history=[],source_row=e['row'],bank_balance=e.get('bank_balance'),note=e.get('note',''),voucher=e.get('voucher',''))
            yield t,part

    def legacy_account_preview(self,d,s=None):
        """Exact simulation of assigning a source account to an old batch: before/after statuses come from the same rule used after the change."""
        s=copy.deepcopy(s or self.state());cat_state(s);s.setdefault('legacy_batches',[]);s.setdefault('legacy_entries',[])
        b=item(s['legacy_batches'],d.get('batch'));require(b['status']=='ACTIVE','Lần migrate không hoạt động.')
        require(not b.get('account'),'Lần migrate này đã có tài khoản nguồn.')
        account=d.get('account');require(account and any(a['id']==account for a in s['accounts']),'Chọn tài khoản nguồn.')
        before=self.legacy_identity_status(s);after_s=copy.deepcopy(s);item(after_s['legacy_batches'],b['id'])['account']=account;after=self.legacy_identity_status(after_s)
        mine=[e for e in s['legacy_entries'] if e['batch']==b['id']];counted={'ACTIVE','UNRESOLVED'}
        def total(st,es):return sum(((Decimal(e['amount']) if e['direction']=='IN' else -Decimal(e['amount'])) for e in es if st.get(e['id']) in counted),Decimal(0))
        issues=[]
        for e in mine:
            if after.get(e['id'])=='CONFLICT':issues.append(dict(row=e['row'],message=f"Dòng {e['row']}: mã {e['reference']} đã có trong tài khoản này với nội dung khác; cần đối chiếu."))
        for e in mine:
            if after.get(e['id'])=='NEAR_DUPLICATE':issues.append(dict(row=e['row'],message=f"Dòng {e['row']}: mã {e['reference']} gần trùng một mã đã có trong tài khoản này (khác hậu tố); cần đối chiếu, không tự gộp."))
        others=[e for e in s['legacy_entries'] if e['batch']!=b['id'] and before.get(e['id'])!=after.get(e['id'])]
        if others:issues.append(dict(row=None,message=f"Xác định tài khoản này làm đổi cách tính {len(others)} dòng của lần migrate khác; xử lý lần migrate trùng trước (hủy hoặc đối chiếu), không tự chuyển số giữa các đối tượng."))
        rows=[dict(row=e['row'],reference=e['reference'],date=e['date'],amount=e['amount'],direction=e['direction'],before=before.get(e['id']),after=after.get(e['id'])) for e in mine]
        return dict(batch=b['id'],account=account,rows=rows,issues=issues,before_total=str(total(before,mine)),after_total=str(total(after,mine)),
            matched_bank=sum(after.get(e['id'])=='MATCHED_BANK' for e in mine),duplicates=sum(after.get(e['id'])=='DUPLICATE' for e in mine),conflicts=sum(after.get(e['id']) in {'CONFLICT','NEAR_DUPLICATE'} for e in mine),draft=True)

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
            out_rows.append(dict(row=n,status='OK',note=cell(r,'note')[:1000],date=iso,description=desc[:500],reference=ref[:100],amount=str(amount),direction=direction,bank_balance=str(vals['balance']) if vals['balance'] is not None else None))
        return dict(columns=cols,mapping=mapping,rows=out_rows,issues=issues,declared=declared)

    def legacy_preview(self,d,s=None):
        with localcontext() as ctx:
            ctx.prec=60
            s=copy.deepcopy(s or self.state());cat_state(s);s.setdefault('legacy_batches',[]);s.setdefault('legacy_entries',[])
            key=d.get('category');self.cat_target_root(s,key)
            need_note=bool(self.cat_flag(s,key,'note_required'))
            text=str(d.get('text') or '');require(text.strip(),'Dán dữ liệu copy từ Google Sheets.');require(len(text)<=2_000_000,'Dữ liệu dán quá lớn.')
            parsed=self.legacy_parse(text,d.get('mapping'))
            pid=d.get('profile') or None;name=str(d.get('name') or '').strip()
            require(not d.get('type') or d['type'] in {'PERSON','PROPERTY','OBJECT'},'Loại đối tượng không hợp lệ.')
            if pid:
                prof=item(s['profiles'],pid)
                require(not name or norm_name(name)==norm_name(prof['name']),f"Bạn vừa chọn đối tượng có sẵn «{prof['name']}» vừa nhập tên «{name}». Dữ liệu sẽ ghi vào đối tượng đã chọn; bỏ chọn đối tượng nếu muốn tạo đối tượng mới, hoặc xóa ô tên.")
            else:
                require(1<=len(name)<=100,'Chọn đối tượng có sẵn hoặc nhập tên đối tượng mới (1–100 ký tự).')
                prof=self.profile_clash(s,name)
            active={b['id'] for b in s['legacy_batches'] if b['status']=='ACTIVE'}
            account=d.get('account') or None
            require(account and any(a['id']==account for a in s['accounts']),'Chọn tài khoản nguồn; không suy đoán tài khoản từ mã giao dịch.')
            seen={}
            for t in s['transactions']:
                if t['account']==account:seen[norm_ref(t['reference'])]=(t['date'],str(abs(Decimal(t['signed_amount']))),'IN' if Decimal(t['signed_amount'])>0 else 'OUT',t['description'],'MATCHED_BANK')
            near={base_ref(t['reference']):t['reference'] for t in s['transactions'] if t['account']==account}
            for e in s['legacy_entries']:
                if e['batch'] in active and self.legacy_account(s,e)==account and norm_ref(e['reference']):near.setdefault(base_ref(e['reference']),e['reference'])
            for e in s['legacy_entries']:
                if e['batch'] in active and self.legacy_account(s,e)==account:
                    seen.setdefault(norm_ref(e['reference']),(e['date'],e['amount'],e['direction'],e['description'],'DUPLICATE'))
            tin=tout=0;matched=dups=0;rows=parsed['rows'];paste_refs={};paste_bases={}
            for r in rows:
                if r['status']!='OK':continue
                amt=int(r['amount']);tin+=amt if r['direction']=='IN' else 0;tout+=amt if r['direction']=='OUT' else 0
                ref=norm_ref(r['reference']);payload=(r['date'],r['amount'],r['direction'],r['description'])
                if not ref:
                    r.update(status='ERROR',message='Thiếu mã giao dịch nguồn; chưa thể định danh.');parsed['issues'].append(dict(row=r['row'],message=r['message']));continue
                if ref in paste_refs:
                    r.update(status='ERROR',message=f"Mã lặp trong cùng lần dán (trùng dòng {paste_refs[ref]}); cần đối chiếu, không tự gộp.");parsed['issues'].append(dict(row=r['row'],message=r['message']));continue
                pb=base_ref(r['reference'])
                if pb in paste_bases and paste_bases[pb][0]!=ref:                                   # gần trùng trong cùng lần dán: cùng quy tắc như giữa các nguồn
                    r.update(status='ERROR',message=f"Mã gần trùng dòng {paste_bases[pb][1]} ({paste_bases[pb][2]}) trong cùng lần dán (khác hậu tố); cần đối chiếu, không tự gộp.");parsed['issues'].append(dict(row=r['row'],message=r['message']));continue
                paste_refs[ref]=r['row'];paste_bases.setdefault(pb,(ref,r['row'],r['reference']))
                if need_note and not r.get('note'):                                                # cùng quy tắc với phân loại và "Sửa phân loại" (spec 043, review vòng 2)
                    r.update(status='ERROR',message='Danh mục này yêu cầu ghi chú: chọn cột Ghi chú khi ánh xạ và điền mục đích cho dòng này.');parsed['issues'].append(dict(row=r['row'],message=r['message']));continue
                old=seen.get(ref)
                if not old and base_ref(r['reference']) in near and norm_ref(near[base_ref(r['reference'])])!=ref:
                    r.update(status='ERROR',message=f"Mã gần trùng {near[base_ref(r['reference'])]} đã có trong tài khoản này (khác hậu tố); cần đối chiếu, không tự gộp.");parsed['issues'].append(dict(row=r['row'],message=r['message']));continue
                if old:
                    if old[:4]!=payload:
                        r.update(status='ERROR',message='Cùng mã trong tài khoản nhưng nội dung khác; cần đối chiếu.');parsed['issues'].append(dict(row=r['row'],message=r['message']))
                    else:
                        r['status']=old[4]
                        if r['status']=='MATCHED_BANK':matched+=1
                        else:dups+=1
            declared=parsed['declared'];totals_ok=None if declared is None else (declared['in']==tin and declared['out']==tout)
            importable=sum(1 for r in rows if r['status'] in {'OK','MATCHED_BANK'})       # dòng trùng sao kê vẫn được lưu làm chứng từ truy nguyên, không cộng tiền lần hai
            return dict(columns=parsed['columns'],mapping=parsed['mapping'],rows=rows,issues=parsed['issues'],totals={'in':str(tin),'out':str(tout)},declared={k:str(v) for k,v in declared.items()} if declared else None,totals_ok=totals_ok,
                importable=importable,matched_bank=matched,duplicates=dups,object=dict(profile=prof['id'] if prof else None,name=prof['name'] if prof else name,exists=bool(prof),kind=prof['kind'] if prof else (d.get('type') or 'OBJECT')),can_import=not parsed['issues'] and importable>0 and totals_ok is not False,needs_confirm=totals_ok is False and not parsed['issues'],draft=True)

    def change_legacy(self,s,action,d):
        from .p01 import now
        cat_state(s);s.setdefault('legacy_batches',[]);s.setdefault('legacy_entries',[])
        if action=='legacy-resolve-account':
            reason=str(d.get('reason') or '').strip();require(reason,'Cần lý do xác định tài khoản.')
            p=self.legacy_account_preview(d,s);require(not p['issues'],'Có xung đột nguồn; chưa xác định tài khoản.')
            b=item(s['legacy_batches'],d.get('batch'));b.setdefault('account_history',[]).append(dict(at=now(),before=b.get('account'),after=d['account'],reason=reason))
            b['account']=d['account'];return 'Đã xác định tài khoản; bản dán gốc giữ nguyên'
        if action=='legacy-import':
            p=self.legacy_preview(d,s);require(not p['issues'],'Còn dòng lỗi: sửa dữ liệu dán rồi xem trước lại.');require(p['importable']>0,'Không có dòng mới để nhập.')
            require(p['totals_ok'] is not False or d.get('accept_total_mismatch') is True,'Tổng các dòng lệch dòng tổng; xác nhận rõ nếu vẫn muốn nhập.')
            key=d['category']
            if p['object']['exists']:prof=item(s['profiles'],p['object']['profile'])
            else:
                prof=self.create_profile(s,p['object']['name'],d.get('type') or 'OBJECT')
            if not any(e['category']==key and e['profile']==prof['id'] and e['status']=='ACTIVE' for e in s['category_objects']):
                s['category_objects'].append(dict(id=uid(),category=key,profile=prof['id'],status='ACTIVE',created_at=now(),history=[dict(at=now(),action='ADD',to=key)]))
            text=str(d['text']);bid=uid()
            s['legacy_batches'].append(dict(id=bid,at=now(),account=d['account'],source_text=text,sha256=hashlib.sha256(text.encode('utf-8')).hexdigest(),category=key,profile=prof['id'],mapping=p['mapping'],rows=p['importable'],
                totals=p['totals'],declared=p['declared'],accepted_mismatch=p['totals_ok'] is False,status='ACTIVE'))
            n=0
            for r in p['rows']:
                if r['status'] not in {'OK','MATCHED_BANK'}:continue
                s['legacy_entries'].append(dict(id=uid(),batch=bid,row=r['row'],date=r['date'],description=r['description'],reference=r['reference'],amount=r['amount'],direction=r['direction'],bank_balance=r['bank_balance'],category=key,profile=prof['id'],**({'note':r['note']} if r.get('note') else {})));n+=1
            return f"Migrate {n} dòng lịch sử cũ cho {prof['name']}"+(f"; bỏ qua {p['duplicates']} dòng trùng lần trước" if p['duplicates'] else '')
        if action=='legacy-void':
            b=item(s['legacy_batches'],d.get('batch'));require(b['status']=='ACTIVE','Lần migrate đã hủy.');reason=str(d.get('reason','')).strip();require(reason,'Cần lý do hủy.')
            b.update(status='VOID',void_reason=reason[:500],voided_at=now());return 'Hủy lần migrate, giữ bản ghi và bản dán gốc'
        require(False,'Hành động không hợp lệ.')
