# Implementation readiness — v0.1

> **Cập nhật phạm vi 28/09/2026:** Thạch giao Codex tự quyết định và hoàn thành sản phẩm cơ bản dùng thử với dữ liệu giả lập. Đã triển khai ứng dụng local theo [quyết định bản thử](product-trial-decisions.md), [hướng dẫn sử dụng](runbooks/product-trial.md) và [nghiệm thu bản thử](product-trial-acceptance.md). Các ràng buộc Sheets-only/no-custom-UI và policy chưa chốt dưới đây thuộc baseline trước yêu cầu mới; chúng không chặn bản thử này. Những yêu cầu về dữ liệu thật/production chưa được coi là hoàn tất.


Cập nhật 2026-09-26. Thạch yêu cầu cập nhật tài liệu và chuẩn bị bắt đầu triển khai. Theo yêu cầu tiếp theo “bắt đầu triển khai”, đã có local synthetic ledger pilot, fixtures, validators và luồng demo. Chưa có workbook, database sản xuất hay kết nối tài khoản.

## Phạm vi có thể bắt đầu

Local development với synthetic fixtures, schema, validation, quy trình và workbook template rỗng. Không cần chờ các lựa chọn tiền tệ hay policy thực để kiểm thử core. USD/VND, thời điểm, tên và policy trong fixtures phải ghi rõ là synthetic, không ghi thành owner configuration.

Production activation cần chốt những dữ liệu và quyền áp dụng cho capability đó. Không suy ra cuộc trao đổi với Thạch là approval của asset owner hoặc toàn bộ ADR. Không tạo thêm confirmation gate cho việc chuẩn bị kỹ thuật đã được yêu cầu.

## Các quyết định mở và ảnh hưởng

| ID | Cần ai/cái gì xác nhận | Nếu chưa có | Vẫn làm được |
|---|---|---|---|
| O1 | Owner: base currency/timezone | Chưa có official consolidated report | Multi-currency synthetic tests |
| O2 | Owner: opening cutoff/period | Chưa publish opening thật | Date/cutoff fixtures |
| O3 | Owner: scope, ownership, debt responsibility | Inventory thật chưa signed-off | Registry/ownership schema |
| O4 | Owner: người duyệt, writer, nơi lưu evidence/backup và access | Chưa tạo live shared workbook hoặc nhập dữ liệu nhạy cảm | Local template và permission plan |
| O5 | Owner: cash-flow basis và categories | Cash-flow official metrics deferred | Test cash/financing/investing separation |
| O6 | Owner: liquidity eligibility/horizon/liability scope | LNW/runway/leverage liên quan policy unavailable | TNW/coverage và metric gating tests |
| O7 | Owner: sources, valuation age, FX và tolerances | Official valuation/reconciliation gate chưa đạt | Synthetic rates/prices và validation |
| O8 | Owner: close authority/materiality/late-data rules | Không close thật | Close/reversal/restatement simulation |
| O9 | Owner: pools, approval authority và limits nếu có | Không publish transfer cần approval; không gắn policy breach nếu thiếu rule | Decision linkage và transfer validation |

Owner chỉ cần trả lời business choices. Người triển khai phải đưa phương án cụ thể và ví dụ khi cần quyết định, không yêu cầu owner tự thiết kế accounting schema.

## Backlog bắt đầu triển khai

| Thứ tự | Gói việc | Output | Gate hoàn thành |
|---|---|---|---|
| S0 | Schema contract | Machine-readable schema/enums, currency/evidence registries, FK map, document-to-schema mapping | Không dangling references; decimal/date/ID/policy status rõ |
| S1 | Synthetic fixtures + validators | Opening, income, expense, transfer, trade/fee, loan, property/business, correction cases | Reject duplicates/imbalanced/partial records đúng rule |
| S2 | Template & import staging | Workbook rỗng, raw staging, issue queue; manual normalized CSV đầu tiên | Round-trip IDs/precision; không execute imported formulas |
| S3 | Reconciliation + core metrics | Quantity/native balance checks, TNW, flows, allocation và eligibility | Không double-count; missing input/policy không thành 0 |
| S4 | Close, corrections, restore | Frozen snapshot manifest, reversal/replacement, restatement, exports | Original unchanged; rebuilt values khớp; restore đủ history |
| S5 | Owner pilot readiness | One-page report, runbook, config questionnaire và acceptance evidence | Production O-gates liên quan được chốt trước dùng dữ liệu thật |

Mỗi bước là vertical slice kiểm chứng được; không xây toàn bộ tương lai cùng lúc. S0–S4 có thể chạy với synthetic data. Không cần PostgreSQL, custom frontend hoặc AI để hoàn thành slice đầu.

## First demonstrable slice

Một owner giả lập, hai bank accounts, một investment account, một property và một khoản vay. Chạy opening → income/expense → internal transfer → investment purchase → reconcile → report → approve demo close → correction/restatement → export/restore. Bổ sung business equity fixture để chứng minh không cộng cash doanh nghiệp lần hai. Demo luôn có nhãn SYNTHETIC và approval actor giả lập, không thay thế production approval.

Nguồn kiểm thử dự kiến: synthetic normalized CSV + manifest riêng. Source-specific bank/exchange parsers chọn sau khi xem sample được phép sử dụng; không hứa hỗ trợ mọi file ngay từ đầu.

## Release gates

1. Synthetic acceptance scenarios trong [milestones](milestones.md) đạt; unsupported instruments được báo rõ.
2. Permissions, backup destination và restore được kiểm chứng trong môi trường thực trước live use.
3. Scope/opening được owner xác nhận; ledger balances và valuation coverage reconcile.
4. Metric nào thiếu approved definition phải disabled/unavailable; không block mọi chức năng độc lập.
5. Snapshot có owner approval, frozen inputs và history; report/AI không tự tạo quyết định tài chính.

## Chưa triển khai trong đợt đầu

Live APIs, trading execution, custom frontend, full business consolidation, tax engine, advanced performance/risk, Monte Carlo và AI automation. Manual Decision Log và property/business equity vẫn thuộc v0.1.

## Tiến độ triển khai đầu tiên — 2026-09-26

- S0: partial — JSON entry schema và pilot-to-target mapping; registry chuẩn hóa đầy đủ còn lại.
- S1: triển khai synthetic fixtures và bộ test cho phạm vi pilot.
- S2: có raw JSON import/evidence retention; CSV và workbook template chưa triển khai.
- S3: có USD single-owner TNW/flows/debt và reconciliation; chưa FX, full policy versioning hay dashboard.
- S4: có synthetic snapshot/restatement/export/restore; production approvals/permissions chưa có.
- S5: chưa đủ điều kiện dùng dữ liệu thật.

[Runbook](runbooks/local-pilot.md) nêu cách chạy, số kỳ vọng và giới hạn. Không đánh dấu S0–S4 hoặc M0–M3 hoàn thành chỉ vì demo đạt.

## Cập nhật S2 — 2026-09-28

Đã đọc hai sample bank XLSX bằng adapter riêng, giữ nguyên evidence và 76 dòng vào private staging; native currency VND, không đẩy sang demo USD. Source balances có mismatch và reference lặp nên chưa qua M2. Đã đối chiếu từng cell A:F với reader độc lập, bổ sung 14 synthetic tests cho format, amounts, dates, source safety và reconciliation. CSV/workbook UI, financial classification, bank identity confirmation và approved journal publication còn lại. Xem [bank runbook](runbooks/bank-statement-v1.md).

## Bàn giao review theo milestone — 28/09/2026

Đã tạo workbook 6 tab cho owner: tiến độ, thiết lập, tài khoản, đối soát, cần xác nhận và 76 giao dịch. Có dropdown phân loại, ô trả lời, công thức đối soát và đếm giao dịch chưa rõ. Đã nhận Dũng là người duyệt; tài khoản giữ đơn vị gốc, consolidated USDT là bước sau. User-facing status ở [milestone board](milestone-board.md).

Có luồng nhận workbook trả lời thành proposals, kiểm tra nguồn không bị sửa và không tự tạo approval/ledger. Đây là tiến độ nhập liệu/review; full operational workbook, issue resolution/approval và M2 publication còn lại. Chưa tuyên bố M0–M3 hoàn thành. Workbook editable không phải source of truth; XLSX gốc và evidence archive giữ riêng.
