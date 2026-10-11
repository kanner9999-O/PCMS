# Data dictionary — Sheets v0.1 → PostgreSQL

Cập nhật: 2026-09-26. Status: IMPLEMENTATION BASELINE; policy chưa chốt được gate riêng. Schema version: 0.1-draft. Đây là thiết kế, chưa phải workbook hoặc DDL đã triển khai.

## 1. Quy ước chung

- ID: UUID dạng text, được cấp một lần bởi writer; không dùng ticker, số dòng hoặc công thức volatile. Business keys và IDs tách riêng.
- Mỗi persisted row: `id, recorded_at, effective_at, source, source_record_id?, created_by, schema_version, notes?`. Dấu `?` là nullable; field không có dấu là bắt buộc trừ khi có conditional rule. `recorded_at` là created timestamp bất biến; không cần thêm created_at trùng nghĩa. `source_record_id` null cho manual fact nhưng phải có evidence/decision link phù hợp.
- Entity/account/asset/currency là FK theo ngữ cảnh, không ép vào record không có ý nghĩa như Config hoặc Audit_Log. Tránh FK giả để lấp ô trống.
- Timestamps: ISO 8601 UTC với offset/Z; ngày nghiệp vụ `YYYY-MM-DD`; reporting timezone là config được version. Nếu chỉ biết ngày thì lưu date và `time_precision=DATE`, không bịa giờ giao dịch.
- Currency codes dùng registry, fiat tách khỏi crypto asset IDs. USDT không phải USD; symbol không unique xuyên chain/contract.
- Quantity và tiền lưu text decimal canonical trong raw/accepted Sheets, ví dụ `1234.56000000`, không dấu phân cách nghìn hoặc scientific notation. Reporting có thể dùng số/formulas nhưng không dùng làm authoritative precision. PostgreSQL dùng NUMERIC với precision/scale được validate theo instrument (đề xuất 38,18 cho quantity; 38,12 cho value/FX nếu phù hợp; asset vượt giới hạn phải mở rộng trước import).
- Unknown = null kèm issue; zero = đã xác nhận bằng 0. Required value không được null để publish. Không ghi `N/A` vào numeric fields. Currency conversion lưu original và selected FX; rounding chỉ ở presentation/final reconciliation theo policy.
- Master revisions: `logical_id, revision_no, supersedes_id?, valid_from, valid_to?`. PK `id` là revision ID; logical ID ổn định. Validity có thể được kết thúc bằng revision mới; không update row cũ. Report chọn một revision theo effective và recorded cutoffs.
- Status được tính từ Record_Events; không sửa status cell của original. Financial row immutable sau append; lỗi ở staging cũng được giữ và reject bằng event.
- FK đến logical master IDs phải resolve đúng revision tại cutoff; snapshot pin revision IDs. FK đến financial fact dùng exact row ID.

## 2. Persisted tabs

Các trường dưới đây cộng với common envelope. `id` được đặt tên nghiệp vụ khi hiển thị (`transaction_id`, `valuation_id`, ...), nhưng chỉ một PK.

| Tab / future table | Grain | Các cột nghiệp vụ |
|---|---|---|
| Entities / entity_revisions | Một revision của owner/legal entity | logical_id, revision_no, supersedes_id?, valid_from, valid_to?, name_alias, entity_type, consolidation_scope |
| Accounts / account_revisions | Một revision account | logical_id, revision_no, supersedes_id?, valid_from, valid_to?, entity_id, institution_alias, account_type, currency_mode, default_currency?, liquidity_class, capital_pool, lifecycle_status |
| Assets / asset_revisions | Một revision instrument/property/business interest | logical_id, revision_no, supersedes_id?, valid_from, valid_to?, asset_type, asset_class, subclass?, symbol?, name, denomination_currency, liquidity_class, chain?, contract_identifier? |
| Ownership / ownership_revisions | Một quyền sở hữu theo thời gian | logical_id, revision_no, supersedes_id?, valid_from, valid_to?, entity_id, asset_id, ownership_fraction, ownership_basis, evidence_id |
| Liabilities / liability_revisions | Một revision nghĩa vụ | logical_id, revision_no, supersedes_id?, valid_from, valid_to?, borrower_entity_id, creditor_alias, account_id?, secured_asset_id?, currency, liability_type, debt_treatment, maturity_date?, rate_type?, annual_rate?, contingent_flag |
| Import_Batches / import_batches | Một file/import attempt | source_system, source_account_ref?, evidence_uri, sha256, retrieved_at, period_start?, period_end?, row_count, file_format |
| Raw_Transactions / raw_transactions | Một source row nguyên trạng | import_batch_id, row_locator, external_event_id?, event_fingerprint?, raw_payload_text, payload_sha256, time_precision |
| Raw_Balances / raw_balances | Một balance observation | import_batch_id?, account_id, entity_id, asset_id?, liability_id?, as_of, quantity?, amount?, currency, balance_kind, evidence_uri?, raw_payload_text?, time_precision |
| Journal_Entries / journal_entries | Một economic entry | entity_id, effective_date, transaction_type, transfer_group_id?, correction_id?, reverses_entry_id?, replaces_entry_id?, primary_source_record_id?, description |
| Journal_Lines / journal_lines | Một posting trong entry | entry_id, line_no, posting_class, account_id?, asset_id?, liability_id?, capital_pool?, quantity_delta?, debit_base, credit_base, native_amount?, native_currency?, book_currency, fx_rate_id?, category?, cash_flow_class?, lot_ref? |
| Valuations / valuations | Một observation position/asset/liability | entity_id, account_id?, asset_id?, liability_id?, as_of, valuation_scope, valuation_method, quantity?, price?, market_value, currency, value_basis, ownership_revision_id?, evidence_id, confidence, supersedes_valuation_id? |
| FX_Rates / fx_rates | Một source rate tại timestamp | from_currency, to_currency, rate, rate_as_of, rate_type, evidence_id, supersedes_rate_id? |
| Real_Estate / property_revisions | Một revision property metadata | logical_id, revision_no, supersedes_id?, valid_from, valid_to?, asset_id, location_alias, purchase_date?, purchase_price?, purchase_currency?, valuation_frequency |
| Business / business_revisions | Một revision business metadata | logical_id, revision_no, supersedes_id?, valid_from, valid_to?, asset_id, operating_entity_id?, valuation_basis, valuation_frequency |
| Reconciliations / reconciliations | Một check và kết quả tại cutoff | scope_entity_id, account_id?, asset_id?, liability_id?, cutoff, observed_balance_id?, ledger_manifest_id, expected_quantity?, actual_quantity?, expected_amount?, actual_amount?, currency?, difference, tolerance_config_id, issue_code?, severity, evidence_id? |
| Close_Runs / close_runs | Một close/restatement attempt | period_start, period_end_exclusive, reporting_timezone, scope_config_id, base_currency, policy_version_id, recorded_cutoff, input_manifest_uri, input_manifest_sha256, restates_snapshot_id?, reason? |
| Monthly_Snapshots / snapshots | Một frozen report version | close_run_id, version_no, previous_version_id?, total_net_worth, liquid_net_worth?, cash, crypto, stocks, real_estate_equity, business_equity, other_assets, separate_debt, embedded_debt, monthly_income?, monthly_spending?, free_cash_flow?, coverage_status, report_sha256 |
| Snapshot_Lines / snapshot_lines | Một component được đóng băng | snapshot_id, entity_id, account_id?, asset_id?, liability_id?, master_revision_id, quantity?, native_value, native_currency, fx_rate_id, fx_rate_value, base_value, debt_treatment?, net_worth_contribution, liquid_contribution?, capital_pool?, valuation_id?, source_manifest_id |
| Decision_Log / decisions | Một proposal/quyết định | category, subject_type, subject_id?, decision_text, before_state, after_state, reason, expected_effect, risk, requested_by, policy_version_id? |
| Corrections / corrections | Một correction request | correction_kind, target_record_type, target_record_id, reason, proposed_effect, requested_by, replacement_group_id? |
| Config / config_revisions | Một policy/config version | logical_id, revision_no, supersedes_id?, valid_from, valid_to?, config_key, typed_value_json, unit?, owner_decision_id? |
| Record_Events / record_events | Một transition/publication/approval | target_type, target_id, event_type, actor_id, reason?, decision_id?, manifest_uri?, manifest_sha256? |
| Record_Links / record_links | Một typed link giữa records | from_type, from_id, relationship, to_type, to_id |
| Audit_Log / audit_log | Một thao tác hoặc verification | actor_id, action, target_type, target_id, correlation_id, reason?, evidence_uri?, payload_sha256? |

Real estate rent, operating costs, maintenance, taxes và debt service đến từ ledger, không copy thành authoritative monthly columns. NOI, cash-on-cash, yield, LTV là derived sau khi đủ dữ liệu. Business revenue, expense, cash, debt, CapEx, working capital và distributions có thể lấy từ business ledger/statement linked; v0.1 chỉ bắt buộc equity valuation và personal transfers. Không tuyên bố module operating-business hoàn chỉnh ở M3.

## 3. Derived tabs / views

| Tab | Grain / nội dung | Rebuild source |
|---|---|---|
| Cash_Flow | Tháng/entity/category; income, spend, capital movements, reserve allocations | Published journal lines + versioned categorization |
| Investments | Account/asset/pool; quantity, value, custody, basis quality | Ledger + selected valuations + FX |
| Dashboard | Current accepted report hoặc selected closed snapshot | Snapshot + metric definitions; hiển thị as-of/coverage/restatement |
| Reconciliation_Queue | Open issues và review state | Reconciliations + events |
| Current_Registry | Revision hiện hành của masters | Master revisions + accepted events |

Các view không phải nguồn dữ liệu nhập và có thể xóa/rebuild theo quy trình. Financial facts và closed snapshots không áp dụng quyền xóa này.

## 4. Constraints và publish rules

1. Mọi IDs unique, envelope đầy đủ, FK tồn tại, currency/type/enum hợp lệ trước publish. Registry lifecycle INACTIVE không xóa history; historical FK vẫn resolve.
2. Một entry chỉ thuộc một entity; lines có account thì account owner phải khớp. `line_no` unique trong entry. Entry phải có ít nhất hai postings; tổng debit_base = tổng credit_base trong cùng book_currency. Số debit/credit không âm, đúng một bên dương; quantity-only adjustment cần valuation/reconciliation rule rõ trước publish.
3. Purchase opening carrying value có thể dùng cho quản trị balance sheet nhưng không gọi là tax cost basis. Market valuation là lớp riêng; không cộng carrying balance với market value. Market value thay thế carrying amount trong projection vị thế.
4. Trade/swap có legs cho cả hai instruments, fee riêng, native quantities và quote evidence. Transfer group kiểm tra in/out theo instrument; external income không bị matched nhầm thành transfer. In-transit được nêu rõ, không xóa gap.
5. Observation có đúng một asset_id hoặc liability_id, trừ bank cash account được map explicit sang cash asset. Quantity/amount requirements tùy balance_kind. Locked, collateral, available balances không được cộng nếu là subsets của total.
6. Valuation khai báo `valuation_scope=WHOLE_ASSET|OWNED_INTEREST|ACCOUNT_POSITION` và `value_basis=GROSS_ASSET|ENTERPRISE|EQUITY`. Tránh nhân ownership lần hai. Mỗi position trong snapshot có đúng một selected valuation; price*quantity hoặc direct appraisal, không cùng lúc cộng hai cách.
7. FX positive; quy ước 1 from_currency = rate to_currency. Identity rate 1 cần record/policy rõ. Conversion path và rate IDs được pin; không lấy latest FX để rebuild closed period.
8. Source external event unique theo `(source_system, external_account, external_event_id, event_component)` ở **accepted mapping**, không ở raw archive: raw duplicate vẫn giữ. Fingerprint không đủ để tự reject legitimate repeats; cần reviewer nếu ambiguous.
9. Publish event chỉ sau manifest liệt kê đầy đủ line IDs/checksums. Manifest mismatch chặn report. Approval lưu actor/time/action ở Record_Events; Decision/Correction views expose approved_by và approved_at từ đó. Không coi proposal là approved.
10. Version uniqueness theo logical ID + revision number; supersession chains không cycle. Published reversal không được lặp đối với cùng original. Snapshot version unique theo scope/period/version, phải có approved close run.

PostgreSQL: PK/FK/UNIQUE/CHECK cho row-local constraints; transactional validation cho cross-row balance, publish, manifest và reversal uniqueness; typed link tables hoặc validated registry để tránh polymorphic links mất integrity. Reporting views chỉ đọc published accepted records. App role không có UPDATE/DELETE tài chính; backups và schema migration/admin role được kiểm soát riêng. Đây là hướng thiết kế, DDL và enforcement tests sau approval.

## 5. Metrics contract cho M3

Mọi metric trả `value, currency/unit, effective_as_of, recorded_cutoff, coverage_status, input_manifest, policy_version, eligibility_status, unavailable_reason`. Eligibility gồm AVAILABLE, INCOMPLETE_DATA, DEFERRED_POLICY, UNSUPPORTED. Khi unavailable, value = null. Demo output phải gắn SYNTHETIC — NOT OWNER DATA. Thiếu input → unavailable/incomplete; không hiện zero hoặc aggregate hoàn chỉnh.

| Metric | Định nghĩa đề xuất / điều kiện |
|---|---|
| Total net worth | Công thức equity trong architecture; separate debt chỉ trừ một lần. |
| Liquid net worth | DEFERRED_POLICY đến khi O6 duyệt liquidity horizon, eligible assets và liability scope. Debt treatment của TNW không được tự quyết định nợ bị trừ ở đây. |
| Investable assets | Assets thuộc INVESTMENT pool và đủ điều kiện; loại reserves/trading/operating theo policy. |
| Monthly income | External cash income: salary/rent/distributions/interest; loại transfers, loan proceeds, sale proceeds và opening equity. |
| Monthly spending | Living/operating cash expenses + paid interest/tax/fees theo scope; loại đầu tư và debt principal. Credit-card cash basis: expense khi thanh toán, card purchase tăng payable và clearing; không ghi expense hai lần. Accrual view là quyết định riêng. |
| Free cash flow | Monthly income − monthly spending; không đồng nghĩa cash balance change. |
| Investable cash flow | FCF − mandatory principal payments − planned tax reserve additions − liquidity reserve additions; không trừ paid tax lần hai. Reserve moves là allocations, không expense. Giá trị có thể âm. |
| Investment rate | Net strategic investment contributions / monthly income; không gồm market gains. Income ≤ 0 → N/A. Savings rate = FCF/income là metric riêng. |
| Cash % / Crypto % / Stocks % | Từng class value / positive economic component base (cash + financial investments + property equity + business equity + other assets, trước separately deducted debt; không gọi là gross assets); mẫu số ghi rõ, không dùng TNW ngầm. |
| Real estate % / Business % | Owned equity / cùng economic asset base. Nếu component equity âm, allocation chart N/A và hiển thị signed table. |
| Direct debt | Tổng nghĩa vụ trực tiếp theo unique liability ID; mortgage có thể đồng thời embedded trong property equity. Breakdown embedded không được cộng thêm vào direct total. |
| Leverage | Direct debt / owned gross personal assets trước property debt; business interest dùng equity, không full business assets. Cần gross-to-equity bridge; thiếu bridge → N/A. |
| Largest asset exposure | Max consolidated exposure theo asset/issuer / eligible positive exposure base; cùng asset across accounts gộp lại. |
| Largest position | Max account+asset position / financial investment NAV; chỉ báo financial portfolio. |
| Liquidity runway | Unrestricted reserve cash / trailing 3 full months essential spending bình quân; chưa đủ lịch sử hoặc denominator ≤ 0 → N/A. |
| Monthly net worth change | Current closed TNW − previous closed TNW (và % nếu previous > 0); không gọi là investment return. |

19 metric cards nếu tách 5 allocation percentages; các card chưa đủ điều kiện hiển thị N/A có lý do. Net worth history chỉ dùng comparable scope/base currency và chọn original/restated rõ ràng. Cash-flow bridge: opening cash + income − spending + financing + net asset-sale/purchase flows + other external capital + FX effect = closing cash; internal transfers net zero trong scope. Mọi khoản còn lại cần classification/issue, không dùng balancing plug âm thầm.

Performance gate riêng: holdings, fees, external cashflows, cost basis/lot history và pricing phải đạt chất lượng phù hợp cho từng metric. TWR/MWR không tự yêu cầu tax lots nhưng cần valuation/cashflow history đúng; realized/unrealized P&L cần cost basis đáng tin. VaR/volatility/correlation chưa trong M3.

## 6. Protection, export và portability

Writer nhập identifiers/text bằng literal values; chặn spreadsheet formula injection từ imported strings. Không để imported text bắt đầu bằng formula trở thành executable cell. Raw file bytes vẫn giữ nguyên trong archive; cell representation được encode an toàn, có format/version để decode.

Proposed access: owner approve, custodian append, analyst read derived/redacted views. Protected raw/ledger/closed ranges không mở cho general editors. Evidence URI là private identifier, không public sharing link. Backup theo mỗi import batch và close, có schema/enums/config/events, headers, UTF-8 CSV/text decimals và checksum manifest; export không phụ thuộc formulas hoặc row positions. Retention/backup destination/restore cadence cần M0 chốt.

Backups cần kiểm tra restore bằng synthetic và sau đó dataset được owner cho phép. Không lưu bank passwords, OTP, private keys hoặc full card credentials; integrations tương lai chỉ read-only khi khả dụng.

## 7. Readiness và proposal boundary

Config cần phân biệt proposal và approved revision bằng Record_Events; thiếu approval không được dùng cho official metrics/close. Raw extraction hoặc AI-suggested classification là proposal, không tự publish. Identity approval dùng actor ID được owner chỉ định, không tự gán tên Thạch/Dũng. AI report contract nằm ở tài liệu riêng và chưa đòi hỏi thêm module AI vào v0.1. Currency registry, evidence manifest, enum definitions và typed-link targets phải được resolve đầy đủ trong machine-readable schema trước khi viết importer; không để evidence_id/config_id là dangling references.

## 8. Bank staging adapter v1

Schema `bank-staging-1` là boundary riêng, chưa là accepted Journal_Entries. Raw XLSX được giữ theo file hash; each transaction có raw_record_id, sheet/source_row, account_reference, bank_reference, effective_date, time_precision, currency, debit, credit, signed_amount, reported_balance, description, raw_cells, fingerprint và classification_status. Account reference chưa phải approved account_id; bank_reference không có unique constraint vì có thể xuất hiện ở cả debit và credit legs. Economic category mặc định null; classification cần owner/custodian review.

Metadata gồm reported opening/closing, period, totals và issues. Opening balance hypothesis không được dùng thay reported value. Batch/raw/normalized history nằm ở private staging và không đổi synthetic ledger source of truth. Native VND không được ép vào USD pilot. Xem [runbook](runbooks/bank-statement-v1.md) cho mappings và status gates.
