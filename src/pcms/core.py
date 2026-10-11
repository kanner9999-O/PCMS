"""Small append-only event ledger. No external services or live-data activation.

Atomic create-only event files implement single-writer publication. Each published
entry contains all its lines. Hash chains detect accidental edits, not privileged
tampering. Monetary inputs are decimal strings; floats are rejected.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from collections import defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal, localcontext
from pathlib import Path
from uuid import UUID, uuid4


class ValidationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def money(value):
    require(isinstance(value, str) and re.fullmatch(r"-?(0|[1-9]\d*)(\.\d+)?", value),
            "Decimal must be a plain decimal string")
    require(len(value.replace('-', '').replace('.', '')) <= 38, "Decimal precision exceeds 38 digits")
    return Decimal(value)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def decimal_text(value):
    return format(value, "f")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def identifier(value):
    try:
        require(str(UUID(value)) == value, "ID must be canonical UUID")
    except (ValueError, TypeError, AttributeError) as exc:
        raise ValidationError("ID must be canonical UUID") from exc


def day(value):
    require(isinstance(value, str) and date.fromisoformat(value).isoformat() == value, "Invalid ISO date")
    return value


def create_file(path, payload):
    """Publish a fully written file via exclusive hard link; never replace history."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.parent / (".pending-" + str(uuid4()))
    try:
        with temp.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temp, path)  # destination must not already exist
    finally:
        temp.unlink(missing_ok=True)


class Ledger:
    def __init__(self, path):
        self.path = Path(path)

    def events(self):
        previous = None
        result = []
        for index, path in enumerate(sorted((self.path / "events").glob("*.json")), 1):
            event = json.loads(path.read_text())
            checksum = event.pop("sha256")
            require(path.name == f"{index:08d}.json", "Event sequence gap")
            require(event["sequence"] == index and event["previous"] == previous, "Broken event chain")
            require(digest(event) == checksum, "Event checksum mismatch")
            event["sha256"] = checksum
            result.append(event)
            previous = checksum
        return result

    def _append(self, kind, payload):
        events = self.events()
        event = {"sequence": len(events) + 1, "id": str(uuid4()), "kind": kind,
                 "recorded_at": datetime.now(timezone.utc).isoformat(),
                 "previous": events[-1]["sha256"] if events else None, "payload": payload}
        event["sha256"] = digest(event)
        create_file(self.path / "events" / f"{event['sequence']:08d}.json", canonical(event))
        return event

    def initialize(self, config):
        require(not self.events(), "Ledger already initialized")
        require(config["mode"] == "SYNTHETIC", "Live data activation is not supported")
        require(config["schema_version"] == "0.1-pilot", "Unsupported schema version")
        require(config["base_currency"] == "USD", "Pilot supports USD only; no implicit FX")
        require(bool(config["owner_actor"]), "Owner actor required")
        day(config["opening_date"])
        accounts = config["accounts"]
        require(accounts and len({a["id"] for a in accounts}) == len(accounts), "Duplicate/empty accounts")
        for account in accounts:
            identifier(account["id"])
            require(account["kind"] in {"CASH", "INVESTMENT", "PROPERTY", "BUSINESS", "DEBT"}, "Account kind")
            require(account["pool"] in {"RESERVE", "INVESTMENT", "TRADING", "OPERATING"}, "Capital pool")
            if account["kind"] == "DEBT":
                require(account["treatment"] in {"DEDUCT_SEPARATELY", "EMBEDDED_IN_PROPERTY_EQUITY"}, "Unsupported debt treatment")
                if account["treatment"] == "EMBEDDED_IN_PROPERTY_EQUITY":
                    require(any(a["id"] == account.get("secured_account") and a["kind"] == "PROPERTY" for a in accounts), "Missing property debt target")
        self._append("CONFIG", config)

    @property
    def config(self):
        events = self.events()
        require(events and events[0]["kind"] == "CONFIG", "Ledger not initialized")
        return events[0]["payload"]

    def decide(self, decision_id, purpose, actor, before, after, reason):
        identifier(decision_id)
        require(actor == self.config["owner_actor"], "Owner approval required")
        require(purpose in {"CAPITAL_TRANSFER", "CORRECTION", "CLOSE"}, "Decision purpose")
        require(before and after and reason, "Decision context required")
        require(not any(e["kind"] == "DECISION" and e["payload"]["id"] == decision_id for e in self.events()), "Decision ID exists")
        self._append("DECISION", {"id": decision_id, "purpose": purpose, "actor": actor,
                                  "before": before, "after": after, "reason": reason})

    def _approval(self, decision_id, purpose):
        require(any(e["kind"] == "DECISION" and e["payload"]["id"] == decision_id
                    and e["payload"]["purpose"] == purpose for e in self.events()), "Missing approved decision")

    def entries(self):
        return [e["payload"] for e in self.events() if e["kind"] == "ENTRY"]

    def _validate_entry(self, entry):
        require(isinstance(entry, dict), "Entry must be an object")
        required = {"id", "effective_date", "currency", "type", "source", "source_record_id", "lines"}
        optional = {"import_batch_id", "decision_id", "reverses", "replaces", "correction_decision_id"}
        require(required <= entry.keys() and entry.keys() <= required | optional, "Entry fields do not match pilot contract")
        identifier(entry["id"])
        day(entry["effective_date"])
        require(entry["effective_date"] >= self.config["opening_date"], "Entry before opening date")
        require(entry["currency"] == self.config["base_currency"], "Unsupported currency; FX is not implemented")
        require(entry["type"] in {"OPENING", "INCOME", "EXPENSE", "TRANSFER", "TRADE", "LOAN", "CORRECTION"}, "Entry type")
        if entry["type"] == "OPENING":
            require(entry["effective_date"] == self.config["opening_date"], "Opening entry must use opening date")
        if entry["type"] == "CORRECTION":
            require(bool(entry.get("reverses")) != bool(entry.get("replaces")), "Correction needs exactly one target")
        else:
            require(not entry.get("reverses") and not entry.get("replaces"), "Correction target requires CORRECTION type")
        require(entry["source"] and entry["source_record_id"], "Source provenance required")
        accounts = {a["id"]: a for a in self.config["accounts"]}
        debit = credit = Decimal(0)
        lines = entry["lines"]
        allowed = {"OPENING": {"ASSET", "LIABILITY", "EQUITY"}, "INCOME": {"ASSET", "INCOME"},
                   "EXPENSE": {"ASSET", "EXPENSE"}, "TRANSFER": {"ASSET"},
                   "TRADE": {"ASSET", "EXPENSE"}, "LOAN": {"ASSET", "LIABILITY", "EXPENSE"},
                   "CORRECTION": {"ASSET", "LIABILITY", "EQUITY", "INCOME", "EXPENSE"}}
        require(len(lines) >= 2, "At least two postings required")
        require(len({line["id"] for line in lines}) == len(lines), "Duplicate line IDs")
        for line in lines:
            require({"id", "class", "debit", "credit"} <= line.keys() and
                    line.keys() <= {"id", "class", "debit", "credit", "account_id", "quantity"}, "Posting fields do not match pilot contract")
            identifier(line["id"])
            d, c = money(line["debit"]), money(line["credit"])
            require(d >= 0 and c >= 0 and ((d > 0) != (c > 0)), "Posting must have one positive side")
            debit += d
            credit += c
            posting = line["class"]
            require(posting in allowed[entry["type"]], "Posting class incompatible with entry type")
            account = accounts.get(line.get("account_id"))
            if posting in {"ASSET", "LIABILITY"}:
                require(account is not None, "Missing account FK")
                require((account["kind"] == "DEBT") == (posting == "LIABILITY"), "Posting/account mismatch")
                if account["kind"] == "INVESTMENT":
                    q = money(line.get("quantity"))
                    require(q != 0 and (q > 0) == (d > c), "Quantity direction must match asset movement")
            else:
                require(line.get("account_id") is None, "Nominal posting cannot hold an account")
                require("quantity" not in line, "Nominal posting cannot hold quantity")
        require(debit == credit, "Entry is not balanced")
        if any(l["class"] in {"INCOME", "EXPENSE"} for l in lines):
            require(any(accounts.get(l.get("account_id"), {}).get("kind") == "CASH" for l in lines), "Pilot supports cash-based income/expense only")
        pools = {accounts[line["account_id"]]["pool"] for line in lines if line.get("account_id")}
        if {"INVESTMENT", "TRADING"} <= pools:
            self._approval(entry.get("decision_id"), "CAPITAL_TRANSFER")

    def post(self, entry):
        with localcontext() as ctx:
            ctx.prec = 80
            self._validate_entry(entry)
        entries = self.entries()
        require(not any(e["id"] == entry["id"] for e in entries), "Entry ID exists")
        source_key = (entry["source"], entry["source_record_id"])
        require(not any((e["source"], e["source_record_id"]) == source_key for e in entries), "Duplicate source event")
        all_line_ids = {line["id"] for e in entries for line in e["lines"]}
        require(not any(line["id"] in all_line_ids for line in entry["lines"]), "Line ID already exists")
        if entry.get("reverses"):
            self._approval(entry.get("correction_decision_id"), "CORRECTION")
            originals = [e for e in entries if e["id"] == entry["reverses"]]
            require(len(originals) == 1, "Reversal target missing")
            require(not any(e.get("reverses") == entry["reverses"] for e in entries), "Already reversed")
            original = originals[0]
            require(entry["effective_date"] == original["effective_date"], "Reversal effective date mismatch")
            def signature(line, reverse=False):
                return (line["class"], line.get("account_id"),
                        money(line["credit"] if reverse else line["debit"]),
                        money(line["debit"] if reverse else line["credit"]),
                        -money(line.get("quantity", "0")) if reverse else money(line.get("quantity", "0")))
            from collections import Counter
            require(Counter(signature(l, True) for l in original["lines"]) ==
                    Counter(signature(l) for l in entry["lines"]), "Reversal must exactly offset original")
        if entry.get("replaces"):
            self._approval(entry.get("correction_decision_id"), "CORRECTION")
            require(any(e.get("reverses") == entry["replaces"] for e in entries), "Replacement needs reversal first")
            require(not any(e.get("replaces") == entry["replaces"] for e in entries), "Replacement already exists")
            original = next(e for e in entries if e["id"] == entry["replaces"])
            require(entry["effective_date"] == original["effective_date"], "Replacement effective date mismatch")
            reversal = next(e for e in entries if e.get("reverses") == entry["replaces"])
            require(entry["correction_decision_id"] == reversal["correction_decision_id"], "Correction decision mismatch")
        self._append("ENTRY", entry)

    def import_json(self, path):
        """Preserve raw bytes before validation. One JSON object is one atomic entry."""
        raw = Path(path).read_bytes()
        checksum = hashlib.sha256(raw).hexdigest()
        evidence = self.path / "evidence" / f"{checksum}.json"
        if not evidence.exists():
            create_file(evidence, raw)
        batch_id = str(uuid4())
        self._append("IMPORT", {"id": batch_id, "sha256": checksum, "evidence": evidence.name})
        entry = None
        try:
            entry = json.loads(raw)
            entry["import_batch_id"] = batch_id
            self.post(entry)
        except (ValueError, KeyError, TypeError) as exc:
            def without_batch(value):
                return {k: v for k, v in value.items() if k != "import_batch_id"}
            exact_duplicate = isinstance(entry, dict) and any(without_batch(e) == without_batch(entry) for e in self.entries())
            self._append("ISSUE", {"batch_id": batch_id, "reason": str(exc),
                                    "blocking": not exact_duplicate,
                                    "classification": "EXACT_DUPLICATE" if exact_duplicate else "REQUIRES_REVIEW"})
            return False
        return True

    def value(self, valuation):
        identifier(valuation["id"])
        account = next((a for a in self.config["accounts"] if a["id"] == valuation["account_id"]), None)
        require(account and account["kind"] in {"INVESTMENT", "PROPERTY", "BUSINESS"}, "Valuation target")
        require(valuation["currency"] == self.config["base_currency"], "Unsupported valuation currency")
        require(valuation["source"], "Valuation source required")
        day(valuation["as_of"])
        require(not any(e["kind"] == "VALUATION" and e["payload"]["id"] == valuation["id"] for e in self.events()), "Valuation ID exists")
        require(money(valuation["value"]) >= 0, "Negative valuations unsupported in pilot")
        require(valuation["basis"] == ("EQUITY" if account["kind"] == "BUSINESS" else "GROSS"), "Valuation basis mismatch")
        self._append("VALUATION", valuation)

    def balances(self, cutoff, through=None):
        day(cutoff)
        balances = defaultdict(Decimal)
        quantities = defaultdict(Decimal)
        income = expense = Decimal(0)
        with localcontext() as ctx:
            ctx.prec = 80
            for event in self.events()[:through]:
                if event["kind"] != "ENTRY" or event["payload"]["effective_date"] > cutoff:
                    continue
                for line in event["payload"]["lines"]:
                    amount = money(line["debit"]) - money(line["credit"])
                    if line.get("account_id"):
                        balances[line["account_id"]] += -amount if line["class"] == "LIABILITY" else amount
                        quantities[line["account_id"]] += money(line.get("quantity", "0"))
                    if event["payload"]["effective_date"][:7] == cutoff[:7]:
                        if line["class"] == "INCOME":
                            income -= amount
                        elif line["class"] == "EXPENSE":
                            expense += amount
        return balances, quantities, income, expense

    def reconcile(self, cutoff, observed, actor):
        require(actor == self.config["owner_actor"], "Reviewer required")
        balances, quantities, _, _ = self.balances(cutoff)
        accounts = self.config["accounts"]
        require(set(observed) == {a["id"] for a in accounts}, "Observation coverage must include every account")
        results = []
        for account in accounts:
            item = observed[account["id"]]
            require(item["source"], "Balance evidence required")
            actual = quantities[account["id"]] if account["kind"] == "INVESTMENT" else balances[account["id"]]
            expected = money(item["value"])
            results.append({"account_id": account["id"], "source": item["source"],
                            "actual": decimal_text(actual), "expected": decimal_text(expected), "matches": actual == expected})
        events = self.events()
        payload = {"cutoff": cutoff, "through": len(events), "input_sha256": events[-1]["sha256"],
                   "actor": actor, "results": results, "passed": all(r["matches"] for r in results)}
        self._append("RECONCILIATION", payload)
        return payload

    def report(self, cutoff, through=None):
        with localcontext() as ctx:
            ctx.prec = 80
            return self._report(cutoff, through)

    def _report(self, cutoff, through):
        events = self.events()[:through]
        balances, quantities, income, expense = self.balances(cutoff, through)
        lines, issues = [], []
        values = {}
        for event in events:
            if event["kind"] == "VALUATION" and event["payload"]["as_of"] <= cutoff:
                v = event["payload"]
                old = values.get(v["account_id"])
                if old is None or old["as_of"] <= v["as_of"]:
                    values[v["account_id"]] = v
        for account in self.config["accounts"]:
            aid = account["id"]
            if account["kind"] in {"CASH", "DEBT"}:
                value = balances[aid]
            else:
                valuation = values.get(aid)
                if not valuation or valuation["as_of"] != cutoff:
                    issues.append(f"Missing exact-cutoff valuation: {account['name']}")
                    value = None
                else:
                    value = money(valuation["value"])
            contribution = -value if account["kind"] == "DEBT" and value is not None else value
            lines.append({"account_id": aid, "name": account["name"], "kind": account["kind"],
                          "book_balance": decimal_text(balances[aid]), "quantity": decimal_text(quantities[aid]),
                          "value": decimal_text(value) if value is not None else None,
                          "contribution": decimal_text(contribution) if contribution is not None else None,
                          "valuation_id": values.get(aid, {}).get("id")})
        # Computation uses gross property assets minus all debt exactly once.
        # Equity presentation subtracts embedded debt from property, never a second deduction.
        for account in self.config["accounts"]:
            if account["kind"] == "DEBT" and account["treatment"] == "EMBEDDED_IN_PROPERTY_EQUITY":
                target = next(line for line in lines if line["account_id"] == account["secured_account"])
                target["property_equity"] = (decimal_text(money(target.get("property_equity", target["value"])) - balances[account["id"]])
                                             if target["value"] is not None else None)
        last_input = max((e["sequence"] for e in events if e["kind"] in {"ENTRY", "VALUATION"}), default=0)
        checks = [e["payload"] for e in events if e["kind"] == "RECONCILIATION" and e["payload"]["cutoff"] == cutoff]
        reconciled = bool(checks and checks[-1]["passed"] and checks[-1]["through"] >= last_input)
        for event in events:
            if event["kind"] == "ISSUE" and event["payload"].get("blocking", True):
                issues.append("Unresolved import issue: " + event["payload"]["batch_id"])
        entries = [e["payload"] for e in events if e["kind"] == "ENTRY"]
        replaced = {e.get("replaces") for e in entries}
        for e in entries:
            if e.get("reverses") and e["reverses"] not in replaced:
                issues.append("Correction awaiting replacement: " + e["reverses"])
        if not reconciled:
            issues.append("Current inputs have not been fully reconciled")
        return {"mode": "SYNTHETIC — NOT OWNER DATA", "schema_version": "0.1-pilot", "formula_version": "pilot-1",
                "cutoff": cutoff, "currency": self.config["base_currency"], "through": len(events),
                "input_sha256": events[-1]["sha256"], "status": "INCOMPLETE_DATA" if issues else "AVAILABLE",
                "issues": issues, "lines": lines,
                "total_net_worth": None if issues else decimal_text(sum(money(l["contribution"]) for l in lines)),
                "income": decimal_text(income), "spending": decimal_text(expense), "free_cash_flow": decimal_text(income - expense),
                "cash_flow_status": "AVAILABLE" if reconciled else "INCOMPLETE_DATA",
                "direct_debt": decimal_text(sum(balances[a["id"]] for a in self.config["accounts"] if a["kind"] == "DEBT")),
                "liquid_net_worth": {"value": None, "status": "DEFERRED_POLICY", "reason": "O6 is not approved"},
                "performance": {"value": None, "status": "UNSUPPORTED", "reason": "Historical cost basis and performance engine not implemented"}}

    def close(self, cutoff, decision_id, restates=None):
        self._approval(decision_id, "CLOSE")
        report = self.report(cutoff)
        require(report["status"] == "AVAILABLE", "Close blocked: " + "; ".join(report["issues"]))
        snapshots = [e["payload"] for e in self.events() if e["kind"] == "SNAPSHOT"]
        previous = [s for s in snapshots if s["report"]["cutoff"] == cutoff]
        require(not previous or restates == previous[-1]["id"], "Existing period requires latest snapshot restatement")
        require(not restates or any(s["id"] == restates and s["report"]["cutoff"] == cutoff for s in snapshots), "Restatement target missing")
        require(not any(s["decision_id"] == decision_id for s in snapshots), "Close approval already used")
        snapshot = {"id": str(uuid4()), "version": len(previous) + 1, "restates": restates,
                    "decision_id": decision_id, "report": report, "report_sha256": digest(report)}
        self._append("SNAPSHOT", snapshot)
        return snapshot

    def verify(self):
        events = self.events()
        require(events and events[0]["kind"] == "CONFIG", "Missing configuration")
        require(events[0]["payload"]["mode"] == "SYNTHETIC", "Live mode not supported")
        for event in events:
            p = event["payload"]
            if event["kind"] == "IMPORT":
                raw = (self.path / "evidence" / p["evidence"]).read_bytes()
                require(hashlib.sha256(raw).hexdigest() == p["sha256"], "Evidence checksum mismatch")
            if event["kind"] == "SNAPSHOT":
                require(digest(p["report"]) == p["report_sha256"], "Snapshot checksum mismatch")
                require(self.report(p["report"]["cutoff"], p["report"]["through"]) == p["report"], "Snapshot rebuild mismatch")
        return len(events)

    def export(self, destination):
        self.verify()
        require(not Path(destination).exists(), "Export destination exists")
        files = {str(p.relative_to(self.path)): p.read_text() for folder in ("events", "evidence")
                 for p in (self.path / folder).glob("*.json")}
        bundle = {"files": files, "checksums": {name: hashlib.sha256(content.encode()).hexdigest() for name, content in files.items()}}
        create_file(Path(destination), canonical(bundle))

    @classmethod
    def restore(cls, bundle_path, destination):
        bundle = json.loads(Path(bundle_path).read_text())
        require(not Path(destination).exists(), "Restore destination must be new")
        require(set(bundle["files"]) == set(bundle["checksums"]), "Manifest file set mismatch")
        for name, content in bundle["files"].items():
            require(re.fullmatch(r"(events/\d{8}|evidence/[a-f0-9]{64})\.json", name), "Unsafe bundle path")
            require(hashlib.sha256(content.encode()).hexdigest() == bundle["checksums"][name], "Bundle checksum mismatch")
        for name, content in bundle["files"].items():
            create_file(Path(destination) / name, content.encode())
        ledger = cls(destination)
        ledger.verify()
        return ledger
