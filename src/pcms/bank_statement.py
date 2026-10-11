"""Read-only XLSX adapter for the supplied six-column Vietnamese statement.

No ledger publication or accounting classification. All workbook content is data.
Reads XML numeric text directly to avoid binary floating-point coercion.
"""
from __future__ import annotations

import hashlib
import io
import json
import posixpath
import re
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from pathlib import Path
from uuid import NAMESPACE_URL, uuid4, uuid5
from xml.etree import ElementTree as ET

from .core import ValidationError, canonical, create_file, require

ADAPTER = "vn-account-statement-v1"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
HEADERS = ["NGAY", "DIEN GIAI", "CHI TIET", "NO", "CO", "SO DU"]


def amount(value, blank_zero=False):
    if value in (None, "") and blank_zero:
        return Decimal(0)
    require(isinstance(value, str) and bool(re.fullmatch(r"-?(?:0|[1-9]\d*|[1-9]\d{0,2}(?:,\d{3})+)", value)),
            "Expected integer VND amount with optional comma thousands separators")
    require(len(value.replace(',', '').replace('-', '')) <= 38, "Amount exceeds supported precision")
    return Decimal(value.replace(",", ""))


def parse_date(value):
    require(isinstance(value, str) and bool(re.fullmatch(r"\d{2}/\d{2}/\d{4}", value)), "Expected DD/MM/YYYY date")
    return datetime.strptime(value, "%d/%m/%Y").date().isoformat()


def read_cells(raw):
    """Return every populated cell in each sheet without evaluating formulas."""
    require(len(raw) <= 25_000_000, "Workbook too large")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        infos = archive.infolist()
        require(len({i.filename for i in infos}) == len(infos), "Duplicate ZIP members")
        require(sum(i.file_size for i in infos) <= 100_000_000, "Expanded workbook too large")
        def xml(name):
            data = archive.read(name)
            require(b"<!DOCTYPE" not in data.upper() and b"<!ENTITY" not in data.upper(), "XML entities are unsupported")
            return ET.fromstring(data)
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared = ["".join(t.text or "" for t in si.findall(".//m:t", NS))
                      for si in xml("xl/sharedStrings.xml").findall("m:si", NS)]
        rels = {r.attrib["Id"]: r.attrib for r in xml("xl/_rels/workbook.xml.rels")}
        sheets = []
        for sheet in xml("xl/workbook.xml").findall("m:sheets/m:sheet", NS):
            rel = rels[sheet.attrib[f"{{{REL}}}id"]]
            require(rel.get("TargetMode") != "External", "External worksheet not supported")
            target = rel["Target"]
            name = posixpath.normpath(target.lstrip('/') if target.startswith('/') else 'xl/' + target)
            require(name.startswith("xl/worksheets/"), "Invalid worksheet path")
            cells = {}
            for cell in xml(name).findall("m:sheetData/m:row/m:c", NS):
                ref = cell.attrib["r"]
                require(re.fullmatch(r"[A-Z]+[1-9]\d*", ref), "Invalid cell coordinate")
                require(ref not in cells, "Duplicate cell coordinate")
                kind = cell.attrib.get("t", "n")
                v = cell.find("m:v", NS)
                value = v.text if v is not None else None
                if kind == "s":
                    index = int(value)
                    require(0 <= index < len(shared), "Invalid shared string index")
                    value = shared[index]
                elif kind == "inlineStr":
                    value = "".join(t.text or "" for t in cell.findall(".//m:t", NS))
                cells[ref] = {"value": value, "type": kind,
                              "formula": cell.find("m:f", NS) is not None}
            sheets.append((sheet.attrib["name"], cells))
        return sheets


def parse_statement(raw):
    with localcontext() as ctx:
        ctx.prec = 80
        return _parse_statement(raw)


def _parse_statement(raw):
    sha = hashlib.sha256(raw).hexdigest()
    matches = []
    for name, cells in read_cells(raw):
        if [cells.get(f"{col}8", {}).get("value") for col in "ABCDEF"] == HEADERS:
            matches.append((name, cells))
    require(len(matches) == 1, "Expected exactly one recognized statement sheet")
    sheet, cells = matches[0]
    def get(ref):
        item = cells.get(ref, {})
        require(not item.get("formula"), f"Formula in source cell {ref}; manual review required")
        require(item.get("type") not in {"e", "b"}, f"Unsupported cell type at {ref}")
        return item.get("value")
    for cell, label in {"A1": "Tu ngay", "C1": "Toi ngay", "A2": "So tai khoan", "A3": "Ten tai khoan",
                        "C3": "So du dau ky", "A4": "Loai tien", "C4": "So du cuoi ky"}.items():
        require(get(cell) == label, f"Unrecognized template label: {cell}")
    for col, label in zip("ABCDEF", HEADERS):
        require(get(f"{col}8") == label, "Header mismatch")
    account = get("B2")
    require(isinstance(account, str) and bool(re.fullmatch(r"\d+", account)), "Account identifier must be digit text")
    require(cells["B2"]["type"] in {"s", "inlineStr", "str"}, "Numeric account identifier may lose leading zeros")
    require(get("B4") == "VND", "This adapter currently supports VND only")
    start, end = parse_date(get("B1")), parse_date(get("D1"))
    require(start <= end, "Invalid statement period")
    opening, closing = amount(get("D3")), amount(get("D4"))
    issues, transactions = [], []
    def issue(code, row=None, **details):
        issues.append({"code": code, "source_row": row, "blocking": True, **details})
    rows = sorted({int(re.search(r"\d+$", ref).group()) for ref, c in cells.items()
                   if int(re.search(r"\d+$", ref).group()) > 8 and (c["value"] not in (None, "") or c["formula"])})
    previous = opening
    last_date = start
    for row in rows:
        try:
            values = {col: get(f"{col}{row}") for col in "ABCDEF"}
            # Do not silently ignore future formats with extra nonblank columns.
            require(not any(re.sub(r"\d", "", ref) not in set("ABCDEF") and re.search(r"\d+$", ref).group() == str(row)
                            and c["value"] not in (None, "") for ref, c in cells.items()), "Unexpected transaction columns")
            effective = parse_date(values["A"])
            debit, credit, balance = amount(values["D"], True), amount(values["E"], True), amount(values["F"])
            require(debit >= 0 and credit >= 0 and ((debit > 0) != (credit > 0)), "Exactly one positive debit or credit required")
            require(isinstance(values["B"], str) and values["B"], "Description missing")
            require(isinstance(values["C"], str) and values["C"], "Bank reference missing")
            if not start <= effective <= end:
                issue("DATE_OUTSIDE_PERIOD", row)
            if effective < last_date:
                issue("DATE_ORDER", row)
            last_date = effective
            signed = credit - debit
            expected = previous + signed if previous is not None else None
            if expected is not None and expected != balance:
                issue("RUNNING_BALANCE_MISMATCH", row, expected=str(expected), reported=str(balance), difference=str(balance - expected))
            previous = balance
            identity = {"account": account, "reference": values["C"], "date": effective,
                        "debit": str(debit), "credit": str(credit), "balance": str(balance), "description": values["B"]}
            transactions.append({"raw_record_id": str(uuid5(NAMESPACE_URL, f"{sha}:{sheet}:{row}")),
                                 "sheet": sheet, "source_row": row, "effective_date": effective,
                                 "time_precision": "DATE", "currency": "VND", "account_reference": account,
                                 "bank_reference": values["C"], "description": values["B"],
                                 "debit": str(debit), "credit": str(credit), "signed_amount": str(signed),
                                 "reported_balance": str(balance), "direction": "OUTFLOW" if debit else "INFLOW",
                                 "economic_category": None, "classification_status": "NEEDS_REVIEW",
                                 "fingerprint": hashlib.sha256(canonical(identity)).hexdigest(),
                                 "raw_cells": values})
        except (ValidationError, ValueError, TypeError) as exc:
            issue("INVALID_TRANSACTION_ROW", row, reason=str(exc))
            previous = None  # never bridge across an unparsed movement
    debits = sum((Decimal(t["debit"]) for t in transactions), Decimal(0))
    credits = sum((Decimal(t["credit"]) for t in transactions), Decimal(0))
    if opening + credits - debits != closing:
        issue("PERIOD_BALANCE_MISMATCH", expected=str(opening + credits - debits), reported=str(closing),
              difference=str(closing - (opening + credits - debits)))
    if transactions and Decimal(transactions[-1]["reported_balance"]) != closing:
        issue("CLOSING_BALANCE_MISMATCH", transactions[-1]["source_row"])
    refs = defaultdict(list)
    for t in transactions:
        refs[t["bank_reference"]].append(t)
    for group in refs.values():
        if len(group) > 1:
            issue("REPEATED_BANK_REFERENCE", rows=[t["source_row"] for t in group],
                  reason="Keep all rows; a reference can identify both debit and credit legs")
    opening_hint = None
    if transactions and transactions[0]["source_row"] == 9 and Decimal(transactions[0]["reported_balance"]) == opening:
        opening_hint = str(opening - Decimal(transactions[0]["signed_amount"]))
    return {"adapter": ADAPTER, "schema_version": "bank-staging-1", "file_sha256": sha, "sheet": sheet,
            "bank_identity": "UNCONFIRMED", "account_reference": account, "account_name": get("B3"),
            "currency": "VND", "period_start": start, "period_end": end,
            "reported_opening_balance": str(opening), "reported_closing_balance": str(closing),
            "opening_balance_hypothesis": opening_hint, "hypothesis_applied": False,
            "source_rows": len(rows), "parsed_rows": len(transactions), "debit_total": str(debits), "credit_total": str(credits),
            "transactions": transactions, "issues": issues,
            "status": "BLOCKED_RECONCILIATION" if issues else "AWAITING_CLASSIFICATION",
            "publication_status": "STAGING_ONLY"}


def stage_files(paths, destination):
    """Fresh batch per invocation, raw bytes saved before parsing. Never edits originals."""
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    batch = root / str(uuid4())
    batch.mkdir(mode=0o700)
    summaries = []
    for index, path in enumerate(paths, 1):
        raw = Path(path).read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        original = batch / f"{index:02d}-{sha}.xlsx"
        create_file(original, raw)
        try:
            result = parse_statement(raw)
        except (ValidationError, ValueError, KeyError, TypeError, zipfile.BadZipFile, ET.ParseError) as exc:
            result = {"adapter": ADAPTER, "file_sha256": sha, "status": "REJECTED_FORMAT",
                      "publication_status": "STAGING_ONLY", "issues": [{"code": "FORMAT_ERROR", "reason": str(exc)}]}
        result["source_filename"] = Path(path).name
        result["recorded_at"] = datetime.now(timezone.utc).isoformat()
        create_file(batch / f"{index:02d}-staging.json", canonical(result))
        summaries.append({"file": Path(path).name, "status": result["status"], "rows": result.get("parsed_rows", 0),
                          "issue_codes": [i["code"] for i in result["issues"]]})
    create_file(batch / "manifest.json", canonical({"adapter": ADAPTER, "created_at": datetime.now(timezone.utc).isoformat(),
                                                     "files": summaries, "publication_status": "STAGING_ONLY"}))
    return {"batch_directory": str(batch), "files": summaries, "publication_status": "STAGING_ONLY"}
