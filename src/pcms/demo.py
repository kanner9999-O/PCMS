"""Reproducible synthetic business cases; no owner data or approved real policy."""
import copy
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from .core import Ledger, canonical, create_file, money


def uid(name):
    return str(uuid5(NAMESPACE_URL, "pcms:synthetic:" + name))


def config():
    accounts = [
        ("bank-a", "Bank A", "CASH", "RESERVE"),
        ("bank-b", "Bank B", "CASH", "RESERVE"),
        ("broker", "Investment position", "INVESTMENT", "INVESTMENT"),
        ("house", "Property — 100% synthetic ownership", "PROPERTY", "INVESTMENT"),
        ("business", "Owned business equity", "BUSINESS", "INVESTMENT"),
        ("mortgage", "Personal mortgage", "DEBT", "RESERVE"),
        ("loan", "Personal loan", "DEBT", "RESERVE"),
    ]
    result = {"schema_version": "0.1-pilot", "mode": "SYNTHETIC", "base_currency": "USD",
              "owner_actor": "synthetic-owner", "opening_date": "2026-09-01", "accounts": []}
    for key, name, kind, pool in accounts:
        account = {"id": uid(key), "name": name, "kind": kind, "pool": pool}
        if kind == "DEBT":
            account["treatment"] = "EMBEDDED_IN_PROPERTY_EQUITY" if key == "mortgage" else "DEDUCT_SEPARATELY"
        if key == "mortgage":
            account["secured_account"] = uid("house")
        result["accounts"].append(account)
    return result


def entry(key, kind, lines, effective="2026-09-10"):
    """lines: (account alias or None, posting class, debit, credit, quantity?)."""
    postings = []
    for index, line in enumerate(lines):
        account, posting, debit, credit, *quantity = line
        p = {"id": uid(f"{key}:line:{index}"), "class": posting, "debit": debit, "credit": credit}
        if account:
            p["account_id"] = uid(account)
        if quantity:
            p["quantity"] = quantity[0]
        postings.append(p)
    return {"id": uid(key), "type": kind, "effective_date": effective, "currency": "USD",
            "source": "synthetic-statement", "source_record_id": key, "lines": postings}


def cases():
    return [
        entry("opening", "OPENING", [
            ("bank-a", "ASSET", "10000", "0"), ("house", "ASSET", "500000", "0"),
            ("business", "ASSET", "100000", "0"), ("mortgage", "LIABILITY", "0", "200000"),
            (None, "EQUITY", "0", "410000")], "2026-09-01"),
        entry("salary", "INCOME", [("bank-a", "ASSET", "5000", "0"), (None, "INCOME", "0", "5000")]),
        entry("expense", "EXPENSE", [(None, "EXPENSE", "1000", "0"), ("bank-a", "ASSET", "0", "1000")]),
        entry("transfer", "TRANSFER", [("bank-a", "ASSET", "0", "2000"), ("bank-b", "ASSET", "2000", "0")]),
        entry("trade", "TRADE", [("broker", "ASSET", "3000", "0", "1"), (None, "EXPENSE", "10", "0"),
                                   ("bank-a", "ASSET", "0", "3010")]),
        entry("loan-draw", "LOAN", [("bank-a", "ASSET", "10000", "0"), ("loan", "LIABILITY", "0", "10000")]),
        entry("loan-repay", "LOAN", [("loan", "LIABILITY", "1000", "0"), (None, "EXPENSE", "100", "0"),
                                      ("bank-a", "ASSET", "0", "1100")]),
    ]


def valuations(ledger):
    for alias, value, basis in [("broker", "3500", "GROSS"), ("house", "500000", "GROSS"), ("business", "100000", "EQUITY")]:
        ledger.value({"id": uid("valuation-" + alias), "account_id": uid(alias), "value": value,
                      "basis": basis, "as_of": "2026-09-30", "currency": "USD", "source": "synthetic valuation evidence"})


def observations(corrected=False):
    # Independent fixture expectations, deliberately not computed from ledger.
    return {uid(key): {"value": value, "source": "synthetic closing statement: " + key}
            for key, value in [("bank-a", "18790" if corrected else "17890"), ("bank-b", "2000"),
                               ("broker", "1"), ("house", "500000"), ("business", "100000"),
                               ("mortgage", "200000"), ("loan", "9000")]}


def correct_expense(ledger):
    decision = uid("correction-approval")
    ledger.decide(decision, "CORRECTION", "synthetic-owner", "expense=1000", "expense=100", "Synthetic transcription error")
    original = next(e for e in ledger.entries() if e["id"] == uid("expense"))
    reverse = copy.deepcopy(original)
    reverse.update(id=uid("expense-reversal"), source_record_id="expense-reversal", type="CORRECTION",
                   reverses=original["id"], correction_decision_id=decision)
    for index, line in enumerate(reverse["lines"]):
        line["id"] = uid(f"reverse-line-{index}")
        line["debit"], line["credit"] = line["credit"], line["debit"]
        if "quantity" in line:
            line["quantity"] = str(-money(line["quantity"]))
    ledger.post(reverse)
    replacement = entry("expense-replacement", "CORRECTION", [(None, "EXPENSE", "100", "0"), ("bank-a", "ASSET", "0", "100")])
    replacement.update(replaces=original["id"], correction_decision_id=decision)
    ledger.post(replacement)


def approve_close(ledger, label, restates=None):
    decision = uid(label)
    ledger.decide(decision, "CLOSE", "synthetic-owner", "reconciled draft", "closed synthetic snapshot", "Synthetic test approval only")
    return ledger.close("2026-09-30", decision, restates)


def run_demo(destination):
    root = Path(destination)
    if root.exists():
        raise ValueError("Demo destination must be new; history will not be overwritten")
    ledger = Ledger(root / "ledger")
    ledger.initialize(config())
    for item in cases():
        path = root / "input" / (item["source_record_id"] + ".json")
        create_file(path, canonical(item))
        if not ledger.import_json(path):
            raise ValueError("Demo import failed: " + str(path))
    ledger.import_json(root / "input" / "salary.json")  # repeated raw attempt, no double posting
    valuations(ledger)
    ledger.reconcile("2026-09-30", observations(), "synthetic-owner")
    original = approve_close(ledger, "close-original")
    correct_expense(ledger)
    ledger.reconcile("2026-09-30", observations(True), "synthetic-owner")
    restated = approve_close(ledger, "close-restated", original["id"])
    ledger.export(root / "backup.json")
    restored = Ledger.restore(root / "backup.json", root / "restored")
    assert restored.report("2026-09-30") == ledger.report("2026-09-30")
    report = ledger.report("2026-09-30")
    create_file(root / "report.json", canonical(report))
    text = f"""# PCMS — báo cáo chạy thử

**SYNTHETIC — toàn bộ dữ liệu giả lập, không phải tài sản của owner.**

Ngày báo cáo: 2026-09-30. Đơn vị: USD. Đây là prototype local, không phải workbook vận hành.

| Chỉ tiêu | Bản gốc | Restated |
|---|---:|---:|
| Tài sản ròng | {original['report']['total_net_worth']} | {restated['report']['total_net_worth']} |
| Thu nhập | {original['report']['income']} | {restated['report']['income']} |
| Chi phí | {original['report']['spending']} | {restated['report']['spending']} |
| Dòng tiền dư | {original['report']['free_cash_flow']} | {restated['report']['free_cash_flow']} |
| Nợ trực tiếp | {original['report']['direct_debt']} | {restated['report']['direct_debt']} |

Liquid Net Worth chưa tính vì policy O6 chưa được duyệt. Performance chưa triển khai.

Một expense được sửa từ 1.000 xuống 100 bằng reversal + replacement. Báo cáo gốc vẫn được lưu nguyên vẹn.
Khoản mortgage 200.000 đã trừ đúng một lần; business được đưa vào bằng equity 100.000.
Nhập lại salary tạo issue duplicate nhưng không tăng thu nhập. Backup đã restore và đối chiếu cùng báo cáo.

Snapshot gốc: {original['id']}. Restated: {restated['id']}.
"""
    create_file(root / "report.md", text.encode())
    return {"report": str(root / "report.md"), "events_verified": ledger.verify(),
            "original_net_worth": original["report"]["total_net_worth"],
            "restated_net_worth": restated["report"]["total_net_worth"]}
