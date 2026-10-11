import json
import tempfile
import unittest
from pathlib import Path
from pcms.bank_statement import stage_files
from pcms.core import ValidationError
from pcms.review import review_package, collect_answers
from datetime import date
from test_bank_statement import workbook


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root/'source.xlsx'
        self.source.write_bytes(workbook())

    def test_review_does_not_publish_or_infer_approval(self):
        batch = stage_files([self.source], self.root/'staging')['batch_directory']
        package = review_package(batch)
        self.assertIsNone(package['owner_approval'])
        self.assertEqual(package['sources'][0]['parsed_rows'], 2)
        self.assertEqual(package['publication_status'], 'REVIEW_ONLY')

    def test_exact_same_file_not_counted_twice(self):
        batch = stage_files([self.source,self.source], self.root/'staging')['batch_directory']
        package = review_package(batch)
        self.assertEqual(len(package['sources']), 1)
        self.assertEqual(len(package['duplicate_files_excluded']), 1)

    def test_edited_staging_rejected(self):
        batch = Path(stage_files([self.source], self.root/'staging')['batch_directory'])
        p = batch/'01-staging.json'
        data = json.loads(p.read_text());data['reported_opening_balance']='1'
        p.write_text(json.dumps(data))
        with self.assertRaises(ValidationError): review_package(batch)

    def test_edited_evidence_rejected(self):
        batch = Path(stage_files([self.source], self.root/'staging')['batch_directory'])
        next(batch.glob('*.xlsx')).write_bytes(b'changed')
        with self.assertRaises(ValidationError): review_package(batch)

    def response_fixture(self):
        batch = stage_files([self.source], self.root/'staging')['batch_directory']
        package = review_package(batch)
        cells={}
        for row,t in enumerate(package['sources'][0]['transactions'],5):
            values={'B':'****'+t['account_reference'][-4:],
                    'C':str((date.fromisoformat(t['effective_date'])-date(1899,12,30)).days),
                    'D':t['description'],'E':t['debit'],'F':t['credit'],'G':t['reported_balance'],
                    'I':'Chưa rõ','L':t['bank_reference'],'M':t['raw_record_id']}
            cells.update({f'{col}{row}':{'value':v,'formula':False} for col,v in values.items()})
        return package, {'Giao_dich':cells,'Thiet_lap':{},'Tai_khoan':{},'Can_xac_nhan':{}}

    def test_return_proposal_is_not_approval(self):
        package,sheets=self.response_fixture()
        sheets['Giao_dich']['I5']['value']='Chi sinh hoạt'
        sheets['Giao_dich']['K5']={'value':'Dũng','formula':False}
        result=collect_answers(package,sheets)
        self.assertEqual(len(result['transaction_proposals']),1)
        self.assertEqual(result['approvals_created'],0)
        self.assertEqual(result['ledger_entries_created'],0)

    def test_changed_source_money_rejected(self):
        package,sheets=self.response_fixture()
        sheets['Giao_dich']['E5']['value']='1'
        with self.assertRaises(ValidationError): collect_answers(package,sheets)

    def test_deleted_transaction_rejected(self):
        package,sheets=self.response_fixture()
        del sheets['Giao_dich']['M5']
        with self.assertRaises(ValidationError): collect_answers(package,sheets)

    def test_formula_response_rejected(self):
        package,sheets=self.response_fixture()
        sheets['Giao_dich']['I5']['formula']=True
        with self.assertRaises(ValidationError): collect_answers(package,sheets)

    def test_sorted_rows_preserve_identity(self):
        package,sheets=self.response_fixture()
        cells=sheets['Giao_dich']
        for col in 'BCDEFGILM':
            cells[f'{col}5'],cells[f'{col}6']=cells[f'{col}6'],cells[f'{col}5']
        self.assertEqual(collect_answers(package,sheets)['transaction_proposals'],[])
