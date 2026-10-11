"""Prepare user-facing review from verified archived bank originals, not edited staging."""
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from decimal import Decimal
from uuid import uuid4

from .bank_statement import parse_statement, read_cells
from .core import require, canonical, create_file


def review_package(batch_directory):
    batch = Path(batch_directory)
    manifest = json.loads((batch / 'manifest.json').read_text())
    sources, seen = [], set()
    duplicates = []
    for index, item in enumerate(manifest['files'], 1):
        staged = json.loads((batch / f'{index:02d}-staging.json').read_text())
        sha = staged['file_sha256']
        require(len(sha) == 64 and all(c in '0123456789abcdef' for c in sha), 'Invalid evidence hash')
        raw = (batch / f'{index:02d}-{sha}.xlsx').read_bytes()
        require(hashlib.sha256(raw).hexdigest() == sha, 'Archived statement changed')
        if sha in seen:
            duplicates.append(item['file'])
            continue
        seen.add(sha)
        parsed = parse_statement(raw)
        # Detect edits to parsed monetary fields before presenting them for review.
        require(all(staged.get(k) == v for k, v in parsed.items()), 'Staging differs from archived source')
        parsed['source_filename'] = item['file']
        parsed['source_id'] = f'S{len(sources)+1:02d}'
        sources.append(parsed)
    require(sources, 'No readable statements')
    return {'version': 'owner-review-1', 'publication_status': 'REVIEW_ONLY',
            'sources': sources, 'duplicate_files_excluded': duplicates,
            'scope': 'Provided statement samples only; not a complete wealth inventory',
            'owner_approval': None}


def export_review_package(batch, destination):
    payload = review_package(batch)
    create_file(destination, canonical(payload))
    return {'sources': len(payload['sources']), 'rows': sum(s['parsed_rows'] for s in payload['sources']),
            'destination': str(destination), 'publication_status': 'REVIEW_ONLY'}


CATEGORIES = {'Chưa rõ', 'Lương / thu nhập', 'Chi sinh hoạt', 'Lãi nhận', 'Lãi / phí trả',
              'Chuyển nội bộ', 'Đầu tư', 'Vay / trả nợ', 'Góp / rút vốn',
              'Gốc và lãi cần tách', 'Hoàn / đảo giao dịch'}


def collect_answers(package, sheets):
    """Read suggestions only. The workbook cannot authorize a financial action."""
    def value(sheet, cell):
        item = sheets[sheet].get(cell, {})
        require(not item.get('formula'), f'Formula in response cell {sheet}!{cell}')
        return item.get('value') or ''
    require({'Giao_dich','Can_xac_nhan','Thiet_lap','Tai_khoan'} <= sheets.keys(), 'Review sheets missing')
    originals = {t['raw_record_id']: t for s in package['sources'] for t in s['transactions']}
    proposals, seen = [], set()
    # Source IDs, rather than row order, retain correct mappings after Excel sorting.
    rows = sorted({int(k[1:]) for k in sheets['Giao_dich'] if k.startswith('M') and k[1:].isdigit() and int(k[1:]) >= 5})
    for row in rows:
        rid = value('Giao_dich', f'M{row}')
        if not rid:
            continue
        require(rid in originals and rid not in seen, 'Unknown or repeated source record in review')
        seen.add(rid)
        original = originals[rid]
        for col, key in [('E','debit'),('F','credit'),('G','reported_balance')]:
            require(Decimal(value('Giao_dich',f'{col}{row}')) == Decimal(original[key]), 'Source money was edited; return to original workbook')
        for col,key in [('D','description'),('L','bank_reference')]:
            literal = value('Giao_dich',f'{col}{row}')
            expected = original[key]
            require(literal == expected or literal == "'" + expected, 'Source text was edited')
        require(value('Giao_dich', f'B{row}') == '****' + original['account_reference'][-4:], 'Source account was edited')
        date_cell = value('Giao_dich', f'C{row}')
        expected_serial = (date.fromisoformat(original['effective_date']) - date(1899,12,30)).days
        require(date_cell == original['effective_date'] or Decimal(date_cell) == expected_serial, 'Source date was edited')
        category = value('Giao_dich', f'I{row}') or 'Chưa rõ'
        require(category in CATEGORIES, 'Unknown review category')
        note = value('Giao_dich', f'J{row}')
        reviewer = value('Giao_dich', f'K{row}')
        if category != 'Chưa rõ' or note or reviewer:
            proposals.append({'raw_record_id':rid,'proposed_category':category,'explanation':note,
                              'reviewer_text':reviewer,'status':'PENDING_REVIEW'})
    require(seen == set(originals), 'Review missing original transactions')
    responses = {}
    for sheet, columns in [('Thiet_lap','C'),('Tai_khoan','DEFG'),('Can_xac_nhan','EFG')]:
        responses[sheet] = {cell:value(sheet,cell) for cell in sheets[sheet]
                            if cell[0] in columns and cell[1:].isdigit() and int(cell[1:]) >= 5 and value(sheet,cell)}
    return {'version':'review-response-1','publication_status':'PENDING_REVIEW',
            'transaction_proposals':proposals,'form_responses':responses,
            'approvals_created':0,'ledger_entries_created':0}


def receive_review(batch, workbook_path, destination):
    package = review_package(batch)
    raw = Path(workbook_path).read_bytes()
    response = collect_answers(package, dict(read_cells(raw)))
    response['workbook_sha256'] = hashlib.sha256(raw).hexdigest()
    response['source_hashes'] = [s['file_sha256'] for s in package['sources']]
    response['recorded_at'] = datetime.now(timezone.utc).isoformat()
    folder = Path(destination) / str(uuid4())
    folder.mkdir(parents=True, mode=0o700)
    create_file(folder/'review.xlsx',raw)
    create_file(folder/'response.json',canonical(response))
    return {'directory':str(folder),'proposals':len(response['transaction_proposals']),
            'publication_status':'PENDING_REVIEW','ledger_entries_created':0}
