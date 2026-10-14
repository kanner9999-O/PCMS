"""Loopback-only UI/API for the persistent synthetic product trial."""
import csv
import io
import json
import mimetypes
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

from .core import ValidationError, canonical
from .product import ProductStore


def serve(directory='private-data/product-demo', port=8787, p01=False):
    if p01:
        from .p01 import P01Store
        store = P01Store(directory)
    else:
        store = ProductStore(directory)
    assets = Path(__file__).parent / 'web'
    token = secrets.token_urlsafe(32)
    datasets = {'main':store}
    active_dataset = 'main'
    main_root = store.root.resolve()
    registry_path = main_root / '.runtime' / 'datasets.json'
    if p01 and registry_path.exists():
        registry=json.loads(registry_path.read_text())
        for key,name in registry.get('restored',{}).items():
            candidate=main_root.parent/name
            if not isinstance(name,str) or not name.startswith(main_root.name+'-restore-') or candidate.resolve().parent!=main_root.parent or not candidate.is_dir():
                raise ValidationError('Danh mục bộ khôi phục không hợp lệ; dữ liệu gốc vẫn giữ nguyên.')
            datasets[key]=P01Store(candidate)
        active_dataset=registry.get('active','main')
        if active_dataset not in datasets:raise ValidationError('Không tìm thấy bộ dữ liệu đã chọn trong danh mục khôi phục.')
        store=datasets[active_dataset]

    def save_registry():
        registry_path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        temporary=registry_path.with_suffix('.tmp')
        temporary.write_bytes(canonical({'active':active_dataset,'restored':{key:value.root.name for key,value in datasets.items() if key!='main'}}))
        temporary.replace(registry_path)

    if p01:
        import re
        changed=False
        pattern=re.compile(re.escape(main_root.name)+r'(?:-restore-[0-9a-f]{10})+')
        for candidate in main_root.parent.glob(main_root.name+'-restore-*'):
            if pattern.fullmatch(candidate.name) and candidate.is_dir() and candidate.resolve().parent==main_root.parent and candidate.resolve() not in {v.root.resolve() for v in datasets.values()}:
                key=secrets.token_hex(8);datasets[key]=P01Store(candidate);changed=True
        if changed:save_registry()

    class Handler(BaseHTTPRequestHandler):
        def headers_ok(self):
            allowed = {f'127.0.0.1:{port}', f'localhost:{port}'}
            if self.headers.get('Host') not in allowed:
                self.send_error(403); return False
            origin = self.headers.get('Origin')
            if origin and origin not in {f'http://{a}' for a in allowed}:
                self.send_error(403); return False
            return True

        def respond(self, payload, status=200, content_type='application/json; charset=utf-8', filename=None):
            raw = canonical(payload) if isinstance(payload,(dict,list)) else payload
            self.send_response(status)
            self.send_header('Content-Type',content_type)
            self.send_header('Content-Length',str(len(raw)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
            if filename:self.send_header('Content-Disposition',f'attachment; filename="{filename}"')
            self.end_headers();self.wfile.write(raw)

        def do_GET(self):
            if not self.headers_ok():return
            url=urlsplit(self.path).path
            try:
                if p01 and url=='/api/datasets':
                    return self.respond({'active':active_dataset,'datasets':[{'id':key,'name':'Bộ dùng thử chính' if key=='main' else 'Bản khôi phục '+key[:8]} for key in datasets]})
                if p01 and url=='/api/sample-p01':
                    q=parse_qs(urlsplit(self.path).query);name=q.get('file',[''])[0]
                    if name not in {'01-first.xlsx','02-overlap.xlsx'}:return self.send_error(404)
                    sample=Path(__file__).parent/'samples'/name
                    return self.respond(sample.read_bytes(),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',filename=name)
                if p01 and url=='/api/source':
                    import base64
                    from .product import item
                    q=parse_qs(urlsplit(self.path).query);b=item(store.state()['imports'],q.get('batch',[''])[0])
                    return self.respond(base64.b64decode(b['content']),content_type='application/octet-stream',filename='statement-source.xlsx')
                if url=='/api/account-history':
                    from .continuous import account_history
                    q=parse_qs(urlsplit(self.path).query);state=store.state()
                    return self.respond(account_history(state,q.get('account',[''])[0],q.get('from',[state['opening_date']])[0],q.get('to',[state['as_of']])[0]))
                if url=='/api/range-report':
                    from .product import projection,validate_date,D,S
                    from datetime import date,timedelta
                    q=parse_qs(urlsplit(self.path).query);state=store.state();start=q.get('from',[state['opening_date']])[0];end=q.get('to',[state['as_of']])[0]
                    validate_date(start,state);validate_date(end,state)
                    if start>end:raise ValidationError('Khoảng ngày không hợp lệ.')
                    after=projection(state,end);before=projection(state,(date.fromisoformat(start)-timedelta(days=1)).isoformat())
                    def total(report,key):return sum((D(f[key]) for f in report['flows']),D('0'))
                    return self.respond({'from':start,'to':end,'report':after,'income':S(total(after,'income')-total(before,'income')),
                        'expense':S(total(after,'expense')-total(before,'expense')),'principal_paid':S(total(after,'principal')-total(before,'principal'))})
                if url=='/api/state':return self.respond({**store.view(),'token':token})
                if url=='/api/backup':return self.respond(store.backup(),filename='pcms-backup-demo.json')
                if url=='/api/report.csv':
                    view=store.view(); report=view['report']; output=io.StringIO(); writer=csv.writer(output)
                    def safe(value):
                        text=str(value)
                        return "'"+text if text.startswith(('=','+','-','@')) else text
                    writer.writerow(['PCMS - BAO CAO GIA LAP',report['cutoff']])
                    writer.writerow(['Chỉ tiêu','Giá trị','Đơn vị'])
                    for key,label in [('net_worth','Tài sản ròng'),('gross_assets','Tổng tài sản'),('debt','Tổng nợ'),('cash','Tiền'),('income','Thu tháng'),('expense','Chi tháng'),('free_cash_flow','Thu trừ chi tháng')]:
                        writer.writerow([label,report[key],'USDT'])
                    writer.writerow([]);writer.writerow(['Tài sản / tài khoản / nợ','Loại','Giá trị nguyên tệ','Đơn vị','Quy đổi USDT'])
                    for a in report['accounts']:writer.writerow([safe(a['name']),'Tiền',a['balance'],a['currency'],a['base_value']])
                    for a in report['assets']:writer.writerow([safe(a['name']),a['class'],a['value'],a['currency'],a['base_value']])
                    for a in report['liabilities']:writer.writerow([safe(a['name']),'Nợ (trừ riêng)',a['balance'],a['currency'],a['base_value']])
                    writer.writerow([]);writer.writerow([view['state']['rate_note']])
                    return self.respond(output.getvalue().encode('utf-8-sig'),content_type='text/csv; charset=utf-8',filename='PCMS-bao-cao-gia-lap.csv')
                if url=='/api/report':
                    view=store.view()
                    return self.respond({'mode':'SYNTHETIC','report':view['report'],'policy':view['state']['policy'],
                                         'rates':view['state']['rates'],'rate_note':view['state']['rate_note']},filename='pcms-report-demo.json')
                if url=='/api/sample-csv':
                    return self.respond('date,account,kind,amount,description\n2026-09-25,bank-main,expense,350000,Chi sinh hoạt demo\n2026-09-26,bank-main,income,1200000,Thu nhập bổ sung demo\n'.encode(),content_type='text/csv; charset=utf-8',filename='pcms-sao-ke-demo.csv')
                paths={'/':'index.html','/app.js':'app.js','/style.css':'style.css','/favicon.svg':'favicon.svg','/continuous.js':'continuous.js'}
                if p01: paths={'/':'p01.html','/p01.js':'p01.js','/p01.css':'p01.css','/favicon.svg':'favicon.svg'}
                if url not in paths:return self.send_error(404)
                file=assets/paths[url]
                self.respond(file.read_bytes(),content_type=(mimetypes.guess_type(file.name)[0] or 'text/plain')+'; charset=utf-8')
            except (ValidationError,ValueError,KeyError) as exc:
                self.respond({'error':str(exc)},400)

        def do_POST(self):
            nonlocal store, active_dataset
            if not self.headers_ok():return
            if self.headers.get('X-PCMS-Token')!=token:return self.respond({'error':'Phiên làm việc hết hạn. Tải lại trang.'},403)
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=20_000_000:return self.respond({'error':'Nội dung yêu cầu quá lớn hoặc rỗng.'},400)
                data=json.loads(self.rfile.read(size))
                request=data.get('request_id')
                if self.path=='/api/action':result=store.apply(data.get('action'),data.get('data',{}),request)
                elif p01 and self.path=='/api/loan-completion':result=store.closure_preview(data)
                elif p01 and self.path=='/api/loan-cash-report':result=store.loan_cash_report(data)
                elif p01 and self.path=='/api/trx-report':result=store.trx_report(data)
                elif p01 and self.path=='/api/category-history':result=store.category_history(data)
                elif p01 and self.path=='/api/category-view':result=store.category_view(store.state(),*store.cat_period(data))
                elif p01 and self.path=='/api/category-review':result=store.category_review(data)
                elif p01 and self.path=='/api/source-preview':result=store.source_preview(data)
                elif p01 and self.path=='/api/account-history':result=store.account_history(data)
                elif p01 and self.path=='/api/classification-review':result=store.classification_review(data)
                elif p01 and self.path=='/api/realty-history':result=store.realty_history(data)
                elif p01 and self.path=='/api/interest-settlement':result=store.settlement_preview(data)
                elif p01 and self.path=='/api/interest-preview':result=store.interest_preview(data)
                elif p01 and self.path=='/api/select-dataset':
                    key=data.get('dataset')
                    if key not in datasets:raise ValidationError('Bộ dữ liệu không tồn tại trong phiên này.')
                    store=datasets[key];active_dataset=key;save_registry();result=store.view()
                elif self.path=='/api/restore':
                    if p01:
                        result=store.clone_restore(data.get('bundle',{}))
                        key=secrets.token_hex(8);datasets[key]=P01Store(result['directory']);result['dataset']=key;save_registry()
                    else:result=store.restore(data.get('bundle',{}),request)
                else:return self.send_error(404)
                self.respond({**result,'token':token})
            except (ValidationError,ValueError,KeyError,TypeError,ArithmeticError) as exc:
                self.respond({'error':str(exc) or 'Dữ liệu chưa hợp lệ.'},400)

        def log_message(self, fmt, *args):
            pass  # descriptions and bank data are not logged to terminal

    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    print(f'PCMS trial ready at http://127.0.0.1:{port}',flush=True)
    server.serve_forever()
