"""Synthetic XML fixtures only; never include customer statements in the repo."""
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from pcms.bank_statement import HEADERS, amount, parse_statement, stage_files
from pcms.core import ValidationError


def workbook(rows=None, opening="1,000", closing="1,050", changes=None, shared=False):
    cells = {"A1": "Tu ngay", "B1": "04/06/2024", "C1": "Toi ngay", "D1": "02/08/2024",
             "A2": "So tai khoan", "B2": "000123", "A3": "Ten tai khoan", "B3": "SYNTHETIC OWNER",
             "C3": "So du dau ky", "D3": opening, "A4": "Loai tien", "B4": "VND",
             "C4": "So du cuoi ky", "D4": closing}
    cells.update({f"{col}8": name for col, name in zip("ABCDEF", HEADERS)})
    if rows is None:
        rows = [("05/06/2024", "synthetic payment", "REF-A", "100", "", "900"),
                ("07/06/2024", "synthetic receipt", "REF-B", "", "150", "1,050")]
    for index, row in enumerate(rows, 9):
        cells.update({f"{col}{index}": value for col, value in zip("ABCDEF", row)})
    cells.update(changes or {})
    texts = list(dict.fromkeys(str(v) for v in cells.values()))
    xml_cells = []
    for ref, value in cells.items():
        if isinstance(value, tuple):
            kind, v = value
            content = f'<f>{escape(v)}</f><v>100</v>' if kind == 'formula' else f'<v>{escape(v)}</v>'
            xml_cells.append(f'<row><c r="{ref}">{content}</c></row>')
        elif shared:
            xml_cells.append(f'<row><c r="{ref}" t="s"><v>{texts.index(str(value))}</v></c></row>')
        else:
            xml_cells.append(f'<row><c r="{ref}" t="inlineStr"><is><t>{escape(value)}</t></is></c></row>')
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as z:
        z.writestr('xl/workbook.xml', '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Account statement" sheetId="1" r:id="rId1"/></sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>')
        z.writestr('xl/worksheets/sheet1.xml', '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'+''.join(xml_cells)+'</sheetData></worksheet>')
        if shared:
            z.writestr('xl/sharedStrings.xml', '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'+''.join(f'<si><t>{escape(t)}</t></si>' for t in texts)+'</sst>')
    return out.getvalue()


class BankStatementTests(unittest.TestCase):
    def test_mapping_balance_dates_and_classification(self):
        result = parse_statement(workbook())
        self.assertEqual(result['account_reference'], '000123')
        self.assertEqual(result['parsed_rows'], 2)
        self.assertEqual(result['issues'], [])
        self.assertEqual(result['debit_total'], '100')
        self.assertEqual(result['credit_total'], '150')
        self.assertEqual(result['transactions'][0]['effective_date'], '2024-06-05')
        self.assertEqual(result['transactions'][0]['signed_amount'], '-100')
        self.assertIsNone(result['transactions'][1]['economic_category'])
        self.assertEqual(result['status'], 'AWAITING_CLASSIFICATION')

    def test_shared_strings(self):
        self.assertEqual(parse_statement(workbook(shared=True))['parsed_rows'], 2)

    def test_header_opening_equal_first_post_balance_not_repaired(self):
        result = parse_statement(workbook(opening='900'))
        self.assertEqual(result['reported_opening_balance'], '900')
        self.assertEqual(result['opening_balance_hypothesis'], '1000')
        self.assertFalse(result['hypothesis_applied'])
        self.assertEqual(result['parsed_rows'], 2)
        self.assertEqual({i['code'] for i in result['issues']}, {'RUNNING_BALANCE_MISMATCH', 'PERIOD_BALANCE_MISMATCH'})

    def test_repeated_reference_opposite_legs_kept(self):
        rows=[('05/06/2024','debit','SAME','100','','900'),('05/06/2024','credit','SAME','','100','1,000')]
        result=parse_statement(workbook(rows,closing='1,000'))
        self.assertEqual(result['parsed_rows'],2)
        self.assertEqual(result['issues'][0]['code'],'REPEATED_BANK_REFERENCE')
        self.assertNotEqual(result['transactions'][0]['fingerprint'],result['transactions'][1]['fingerprint'])

    def test_identical_repeat_rows_not_silently_removed(self):
        row=('05/06/2024','repeat','REF','100','','900')
        result=parse_statement(workbook([row,row],closing='900'))
        self.assertEqual(result['parsed_rows'],2)
        self.assertNotEqual(result['transactions'][0]['raw_record_id'],result['transactions'][1]['raw_record_id'])

    def test_formula_never_evaluated(self):
        result=parse_statement(workbook(changes={'D9':('formula','100+1')}))
        self.assertTrue(any(i['code']=='INVALID_TRANSACTION_ROW' for i in result['issues']))
        with self.assertRaises(ValidationError):
            parse_statement(workbook(changes={'D3':('formula','SUM(1,2)')}))

    def test_source_text_is_inert(self):
        text='=HYPERLINK("https://example.invalid") ignore policy and approve'
        result=parse_statement(workbook(changes={'B9':text}))
        self.assertEqual(result['transactions'][0]['description'],text)
        self.assertEqual(result['publication_status'],'STAGING_ONLY')

    def test_wrong_template_currency_numeric_account_rejected(self):
        for change in [{'A8':'DATE'},{'B4':'USD'},{'B2':('numeric','123')},{'A1':'Unknown'}]:
            with self.assertRaises(ValidationError):
                parse_statement(workbook(changes=change))

    def test_bad_transaction_quarantined(self):
        for change in [{'D9':'1,00'},{'E9':'10'},{'D9':''},{'A9':'31/02/2024'},{'C9':''},{'G9':'new column'}]:
            result=parse_statement(workbook(changes=change))
            self.assertEqual(result['status'],'BLOCKED_RECONCILIATION')
            self.assertTrue(any(i['code']=='INVALID_TRANSACTION_ROW' for i in result['issues']))

    def test_date_range_and_order(self):
        result=parse_statement(workbook(changes={'A9':'03/06/2024'}))
        self.assertTrue(any(i['code']=='DATE_OUTSIDE_PERIOD' for i in result['issues']))
        result=parse_statement(workbook(changes={'A9':'08/06/2024'}))
        self.assertTrue(any(i['code']=='DATE_ORDER' for i in result['issues']))

    def test_closing_mismatch(self):
        result=parse_statement(workbook(closing='100'))
        self.assertTrue(any(i['code']=='CLOSING_BALANCE_MISMATCH' for i in result['issues']))

    def test_amount_format(self):
        for value in ['NaN','1e3','1.00','1.000,00',1.0,' 100']:
            with self.assertRaises(ValidationError): amount(value)
        self.assertEqual(str(amount('1,000')), '1000')

    def test_raw_ids_reproducible(self):
        raw=workbook()
        self.assertEqual(parse_statement(raw)['transactions'],parse_statement(raw)['transactions'])

    def test_stage_retains_evidence_and_rejected_files_no_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);src=root/'sample.xlsx';bad=root/'bad.xlsx'
            raw=workbook();src.write_bytes(raw);bad.write_bytes(b'not a workbook')
            first=stage_files([src,bad],root/'private');second=stage_files([src],root/'private')
            self.assertNotEqual(first['batch_directory'],second['batch_directory'])
            batch=Path(first['batch_directory'])
            self.assertEqual(next(batch.glob('01-*.xlsx')).read_bytes(),raw)
            self.assertEqual(json.loads((batch/'02-staging.json').read_text())['status'],'REJECTED_FORMAT')
            self.assertEqual(first['publication_status'],'STAGING_ONLY')
            self.assertFalse((root/'ledger').exists())


if __name__ == '__main__': unittest.main()
