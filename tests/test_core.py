import copy
import json
import tempfile
import unittest
from pathlib import Path

from pcms.core import Ledger, ValidationError, canonical, money
from pcms.demo import (approve_close, cases, config, correct_expense, entry,
                       observations, run_demo, uid, valuations)


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ledger = Ledger(self.root / "ledger")
        self.ledger.initialize(config())

    def populated(self):
        for item in cases():
            self.ledger.post(item)
        valuations(self.ledger)

    def reconciled(self):
        self.populated()
        self.ledger.reconcile("2026-09-30", observations(), "synthetic-owner")

    def test_live_activation_rejected(self):
        c = config()
        c["mode"] = "LIVE"
        with self.assertRaises(ValidationError):
            Ledger(self.root / "live").initialize(c)

    def test_no_overwrite(self):
        with self.assertRaises(ValidationError):
            self.ledger.initialize(config())

    def test_decimal_rejects_float_scientific_nan(self):
        for value in [0.1, "1e9", "NaN", "Infinity", "1,000", " 2"]:
            with self.assertRaises(ValidationError):
                money(value)
        self.assertEqual(str(money("0.000000000000000001")), "1E-18")

    def test_unbalanced_missing_fk_currency_and_partial_rejected(self):
        for change in ["unbalanced", "fk", "currency", "partial"]:
            item = copy.deepcopy(cases()[1])
            if change == "unbalanced":
                item["lines"][0]["debit"] = "4999"
            elif change == "fk":
                item["lines"][0]["account_id"] = uid("missing")
            elif change == "currency":
                item["currency"] = "VND"
            else:
                item["lines"] = item["lines"][:1]
            before = len(self.ledger.events())
            with self.assertRaises(ValidationError):
                self.ledger.post(item)
            self.assertEqual(len(self.ledger.events()), before)

    def test_duplicate_raw_retained_but_not_posted_twice(self):
        p = self.root / "source.json"
        p.write_bytes(canonical(cases()[1]))
        self.assertTrue(self.ledger.import_json(p))
        self.assertFalse(self.ledger.import_json(p))
        self.assertEqual(len(self.ledger.entries()), 1)
        self.assertEqual(sum(e["kind"] == "IMPORT" for e in self.ledger.events()), 2)
        self.assertTrue(any(e["kind"] == "ISSUE" for e in self.ledger.events()))

    def test_same_amount_distinct_events_preserved(self):
        self.ledger.post(cases()[1])
        other = entry("second-salary", "INCOME", [("bank-a", "ASSET", "5000", "0"), (None, "INCOME", "0", "5000")])
        self.ledger.post(other)
        self.assertEqual(len(self.ledger.entries()), 2)

    def test_source_collision_with_changed_content_is_blocking(self):
        p = self.root / "source.json"
        item = cases()[1]
        p.write_bytes(canonical(item))
        self.assertTrue(self.ledger.import_json(p))
        item["lines"][0]["debit"] = "6000"
        item["lines"][1]["credit"] = "6000"
        p.write_bytes(canonical(item))
        self.assertFalse(self.ledger.import_json(p))
        issue = self.ledger.events()[-1]["payload"]
        self.assertTrue(issue["blocking"])
        self.assertEqual(issue["classification"], "REQUIRES_REVIEW")
        self.assertEqual(len(self.ledger.entries()), 1)

    def test_transfer_loan_principal_not_income_spending(self):
        self.reconciled()
        report = self.ledger.report("2026-09-30")
        self.assertEqual(report["income"], "5000")
        self.assertEqual(report["spending"], "1110")
        self.assertEqual(report["free_cash_flow"], "3890")

    def test_property_business_and_debt_not_double_counted(self):
        self.reconciled()
        report = self.ledger.report("2026-09-30")
        self.assertEqual(report["total_net_worth"], "414390")
        self.assertEqual(report["direct_debt"], "209000")
        house = next(l for l in report["lines"] if l["account_id"] == uid("house"))
        self.assertEqual(house["property_equity"], "300000")

    def test_policy_and_performance_unavailable(self):
        self.reconciled()
        report = self.ledger.report("2026-09-30")
        self.assertIsNone(report["liquid_net_worth"]["value"])
        self.assertEqual(report["liquid_net_worth"]["status"], "DEFERRED_POLICY")
        self.assertIsNone(report["performance"]["value"])

    def test_missing_valuation_not_zero(self):
        for item in cases():
            self.ledger.post(item)
        self.ledger.reconcile("2026-09-30", observations(), "synthetic-owner")
        report = self.ledger.report("2026-09-30")
        self.assertIsNone(report["total_net_worth"])
        with self.assertRaises(ValidationError):
            approve_close(self.ledger, "missing-price")

    def test_reconciliation_coverage_mismatch_blocks_close(self):
        self.populated()
        data = observations()
        data[uid("broker")]["value"] = "2"
        self.assertFalse(self.ledger.reconcile("2026-09-30", data, "synthetic-owner")["passed"])
        with self.assertRaises(ValidationError):
            approve_close(self.ledger, "bad-reconcile")
        del data[uid("house")]
        with self.assertRaises(ValidationError):
            self.ledger.reconcile("2026-09-30", data, "synthetic-owner")

    def test_new_records_require_new_reconciliation(self):
        self.reconciled()
        correct_expense(self.ledger)
        self.assertEqual(self.ledger.report("2026-09-30")["status"], "INCOMPLETE_DATA")

    def test_close_requires_owner_approval(self):
        self.reconciled()
        with self.assertRaises(ValidationError):
            self.ledger.close("2026-09-30", uid("none"))
        with self.assertRaises(ValidationError):
            self.ledger.decide(uid("fake"), "CLOSE", "AI", "a", "b", "c")

    def test_correction_restatement_original_unchanged(self):
        self.reconciled()
        original = approve_close(self.ledger, "close-original")
        frozen = canonical(original)
        correct_expense(self.ledger)
        self.ledger.reconcile("2026-09-30", observations(True), "synthetic-owner")
        updated = approve_close(self.ledger, "close-restated", original["id"])
        self.assertEqual(updated["report"]["total_net_worth"], "415290")
        self.assertEqual(updated["report"]["spending"], "210")
        old = next(e["payload"] for e in self.ledger.events() if e["kind"] == "SNAPSHOT")
        self.assertEqual(canonical(old), frozen)
        self.ledger.verify()

    def test_wrong_reversal_rejected(self):
        self.reconciled()
        self.ledger.decide(uid("correct"), "CORRECTION", "synthetic-owner", "a", "b", "test")
        reversal = entry("wrong-reversal", "CORRECTION", [(None, "EXPENSE", "0", "10"), ("bank-a", "ASSET", "10", "0")])
        reversal.update(reverses=uid("expense"), correction_decision_id=uid("correct"))
        with self.assertRaises(ValidationError):
            self.ledger.post(reversal)

    def test_investment_trading_transfer_requires_decision(self):
        cfg = config()
        cfg["accounts"][0]["pool"] = "INVESTMENT"
        cfg["accounts"][1]["pool"] = "TRADING"
        ledger = Ledger(self.root / "pools")
        ledger.initialize(cfg)
        item = cases()[3]
        with self.assertRaises(ValidationError):
            ledger.post(item)
        ledger.decide(uid("capital"), "CAPITAL_TRANSFER", "synthetic-owner", "before", "after", "demo")
        item["decision_id"] = uid("capital")
        ledger.post(item)

    def test_event_tampering_detected(self):
        path = self.root / "ledger/events/00000001.json"
        text = path.read_text().replace("Bank A", "Bank X")
        path.write_text(text)
        with self.assertRaises(ValidationError):
            self.ledger.verify()

    def test_full_demo_backup_and_restore(self):
        result = run_demo(self.root / "demo")
        self.assertEqual(result["restated_net_worth"], "415290")
        with self.assertRaises(ValueError):
            run_demo(self.root / "demo")

    def test_restore_manifest_corruption_and_path_traversal(self):
        self.ledger.export(self.root / "backup.json")
        bundle = json.loads((self.root / "backup.json").read_text())
        bundle["files"]["../evil"] = "x"
        bundle["checksums"]["../evil"] = "x"
        (self.root / "bad.json").write_text(json.dumps(bundle))
        with self.assertRaises(ValidationError):
            Ledger.restore(self.root / "bad.json", self.root / "restored")
        self.assertFalse((self.root / "restored").exists())

    def test_latest_failed_reconciliation_supersedes_previous_pass(self):
        self.reconciled()
        bad = observations()
        bad[uid("bank-a")]["value"] = "1"
        self.ledger.reconcile("2026-09-30", bad, "synthetic-owner")
        self.assertIsNone(self.ledger.report("2026-09-30")["total_net_worth"])

    def test_reversal_without_replacement_blocks_report(self):
        self.reconciled()
        self.ledger.decide(uid("partial-correction"), "CORRECTION", "synthetic-owner", "a", "b", "test")
        item = entry("partial-reversal", "CORRECTION", [(None, "EXPENSE", "0", "1000.00"), ("bank-a", "ASSET", "1000.00", "0")])
        item.update(reverses=uid("expense"), correction_decision_id=uid("partial-correction"))
        self.ledger.post(item)
        observed = observations()
        observed[uid("bank-a")]["value"] = "18890"
        self.ledger.reconcile("2026-09-30", observed, "synthetic-owner")
        report = self.ledger.report("2026-09-30")
        self.assertTrue(any("awaiting replacement" in i for i in report["issues"]))

    def test_malformed_import_preserved_and_blocks_close(self):
        self.reconciled()
        p = self.root / "broken.json"
        p.write_text('{bad input')
        self.assertFalse(self.ledger.import_json(p))
        with self.assertRaises(ValidationError):
            approve_close(self.ledger, "unresolved-import")

    def test_opening_not_income_and_correction_requires_target(self):
        bad = copy.deepcopy(cases()[1])
        bad["type"] = "OPENING"
        bad["effective_date"] = "2026-09-01"
        with self.assertRaises(ValidationError):
            self.ledger.post(bad)
        bad["type"] = "CORRECTION"
        with self.assertRaises(ValidationError):
            self.ledger.post(bad)

    def test_decimal_quantity_roundtrip(self):
        self.ledger.post(entry("tiny-trade", "TRADE", [("broker", "ASSET", "1", "0", "0.000000000000000001"),
                                                      ("bank-a", "ASSET", "0", "1")]))
        report = self.ledger.report("2026-09-30")
        position = next(l for l in report["lines"] if l["account_id"] == uid("broker"))
        self.assertEqual(position["quantity"], "0.000000000000000001")

    def test_checked_in_fixtures_match_generators(self):
        root = Path(__file__).parent / "fixtures/synthetic"
        self.assertEqual(json.loads((root / "config.json").read_text()), config())
        for item in cases():
            self.assertEqual(json.loads((root / (item["source_record_id"] + ".json")).read_text()), item)


if __name__ == "__main__":
    unittest.main()
