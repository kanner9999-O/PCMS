# ADR register

> **Cập nhật phạm vi 28/09/2026:** Thạch giao Codex tự quyết định và hoàn thành sản phẩm cơ bản dùng thử với dữ liệu giả lập. Đã triển khai ứng dụng local theo [quyết định bản thử](product-trial-decisions.md), [hướng dẫn sử dụng](runbooks/product-trial.md) và [nghiệm thu bản thử](product-trial-acceptance.md). Các ràng buộc Sheets-only/no-custom-UI và policy chưa chốt dưới đây thuộc baseline trước yêu cầu mới; chúng không chặn bản thử này. Những yêu cầu về dữ liệu thật/production chưa được coi là hoàn tất.


Cập nhật 2026-09-26. Yêu cầu của Thạch cho phép cập nhật tài liệu và chuẩn bị triển khai. Đây không phải blanket approval cho policy hoặc dữ liệu tài chính của owner. Các ADR là **PROPOSED**, dùng làm baseline cho thử nghiệm synthetic; production decisions cần approval tương ứng. Khi được duyệt, ghi decision ID, approved_by và approved_at; ADR bị thay thế vẫn giữ lại và liên kết superseding ADR.

| ADR | Decision đề xuất | Alternative / tradeoff | Approval |
|---|---|---|---|
| ADR-001 | Sheets provisional accepted ledger + independent evidence archive; PostgreSQL sau domain ổn | DB ngay kiểm soát tốt hơn nhưng tăng setup; Sheets thiếu strict immutability | O4 |
| ADR-002 | Append-only facts, master revisions, approval/publication events | Mutable current rows đơn giản nhưng làm mất as-reported history | O8 |
| ADR-003 | Balanced journal entries/lines + market valuation layer riêng | Flat transaction list ít tab hơn nhưng khó kiểm soát transfer/fees/debt | Architecture |
| ADR-004 | Personal perimeter với property/business equity; explicit debt treatment | Full look-through cần elimination rules và business books đầy đủ | O3 |
| ADR-005 | Native units/currency giữ nguyên; versioned base currency và FX | USD-only input làm mất reconciliation evidence | O1, O7 |
| ADR-006 | Frozen close inputs, immutable snapshots, restatement versions | Recompute history bằng latest data dễ dùng nhưng thay đổi báo cáo cũ | O2, O8 |
| ADR-007 | Tách holdings/value eligibility khỏi performance/basis eligibility | Chặn tất cả reporting chờ đủ lịch sử gây trì hoãn; cho tất cả analytics gây sai | Architecture |
| ADR-008 | Cash-flow basis v0.1, financing/investing và reserve routing tách riêng | Accrual có ích nhưng cần quy tắc receivables/payables đầy đủ hơn | O5 |
| ADR-009 | Liquid eligibility rõ; LNW DEFERRED_POLICY; direct obligation và embedded treatment là hai chiều có thể chồng nhau | Công thức LNW cũ dùng separately counted debt bị rút khỏi baseline; cần liability scope riêng | O6 |
| ADR-010 | Single writer, protected tabs, checksummed exports và manual approvals | Không chống admin tampering tuyệt đối; cần owner chấp nhận residual risk | O4 |
| ADR-011 | INVESTMENT/TRADING pools riêng; approved decision trước chuyển vốn | Chỉ phân loại theo asset class không kiểm soát rescue trading losses | O9 |
| ADR-012 | Migrate tab-to-table, giữ UUIDs và events; cutover một writer | Dual-write tăng drift và correction complexity | Architecture |

Không đưa risk limits, allocation targets, tax-lot methods hoặc return benchmarks giả định vào Config như policy đã được chấp thuận. Các mục chưa quyết định phải ở proposal state hoặc metric bị deferred.

## Các quyết định bổ sung sau trao đổi

| ADR | Đề xuất thiết kế | Tradeoff / gate |
|---|---|---|
| ADR-013 | Product core = tổng hợp và đối soát tài sản, nợ, dòng tiền; dashboard và AI sử dụng kết quả | v0.1 hoàn thành được mà không có AI hoặc custom frontend |
| ADR-014 | Deterministic calculations + approved policy checks + AI reasoning tách riêng | AI có thể đề xuất, không tự phê duyệt, sửa ledger hoặc tính số không kiểm chứng |
| ADR-015 | Build với synthetic data trong khi owner settings còn mở; production gates theo từng capability | Không biến defaults dùng test thành policy thật |

Thạch nên review kỹ ADR-004/007/008/009/006/011; ADR-001/010 cần hiểu giới hạn Sheets. Các ADR còn lại do implementation lead giải thích hệ quả và kiểm thử, không yêu cầu product reviewer biết kế toán. Tham khảo [product brief](product-brief.md) và [AI contract](ai-analysis-contract.md).
