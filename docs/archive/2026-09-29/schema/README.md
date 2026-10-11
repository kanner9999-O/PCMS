# Pilot schema contract

Version `0.1-pilot` is a deliberately narrower implementation than the target `0.1-draft` Sheets data dictionary. It is not a production database replacement. The local append-only event store is a test harness for the future Sheets adapter and calculation engine.

`pilot-entry.schema.json` describes the import object. Runtime validation in `pcms.core` additionally enforces decimal precision, UUIDs, foreign keys, supported account/class combinations, balanced postings, uniqueness, approval requirements and correction targets. Runtime is authoritative for cross-record rules; a JSON Schema pass alone does not authorize publication.

## Mapping to target model

| Target | Pilot representation | Deliberate restriction |
|---|---|---|
| Entities / Ownership | One synthetic owner and fully owned positions | No multi-entity, joint ownership or consolidation |
| Accounts / Assets | Config accounts, one instrument per investment account | Account and position are collapsed for the pilot; split before live adapter |
| Liabilities | DEBT account, treatment and secured property account | Personal separate debt or embedded property debt only |
| Journal Entries / Lines | ENTRY payload with complete lines in one published event | USD book currency only; no FX or settlement engine |
| Import Batches / Raw Transactions | IMPORT event and content-addressed exact raw JSON | One normalized entry per JSON file; no bank/exchange parser yet |
| Valuations | VALUATION event, explicit GROSS/EQUITY and source | Whole-account values at exact cutoff; no implicit carried-forward price |
| Raw Balances / Reconciliations | RECONCILIATION observations with source and actual/expected | Cash/debt book balance, investment quantity; private-asset book controls distinct from market valuation |
| Decisions / Events | DECISION and chronological event envelope | Synthetic actor string, no authentication or production authorization service |
| Corrections | CORRECTION decision + linked reversal/replacement ENTRY records | Replacement required; reversal-only voiding deferred |
| Close / Snapshots / Lines | SNAPSHOT event embedding frozen report and hash | Cutoff day, one month income/spending; no timezone-aware intraday close yet |
| Audit | Event sequence, previous hash, recorded_at, checksums | Single writer; admin can alter files, chain is not tamper-proof |
| Config | First CONFIG event | No config revisions or live-policy activation yet |

IDs are UUIDs; event sequence numbers are ordering metadata, not business IDs. Decimals stay text at persistence boundaries and use Decimal arithmetic. Raw inputs are never formulas. Business equity is already the owner's interest, not enterprise value.

Financial scope: reports compute gross property plus other assets minus each personal debt once, and separately show property equity as a presentation field. Never add `property_equity` to the gross contribution column. Negative equity is possible; the pilot does not produce allocation percentages.

The fixture configuration explicitly stands in for approved cash-flow basis, scope and zero reconciliation tolerance in a synthetic scenario only. LNW is always DEFERRED_POLICY. No real settings are inferred from fixtures.

Before production: complete entity/asset/ownership registries and FK mapping, multi-currency/FX, config versioning, typed decision scopes, actor authentication, issue-resolution workflow, operational Sheets adapter, exports/permissions and owner sign-offs. S0 is partial, not complete for the entire target model.
