# M0–M3 implementation plan

> **Cập nhật phạm vi 28/09/2026:** Thạch giao Codex tự quyết định và hoàn thành sản phẩm cơ bản dùng thử với dữ liệu giả lập. Đã triển khai ứng dụng local theo [quyết định bản thử](product-trial-decisions.md), [hướng dẫn sử dụng](runbooks/product-trial.md) và [nghiệm thu bản thử](product-trial-acceptance.md). Các ràng buộc Sheets-only/no-custom-UI và policy chưa chốt dưới đây thuộc baseline trước yêu cầu mới; chúng không chặn bản thử này. Những yêu cầu về dữ liệu thật/production chưa được coi là hoàn tất.


Người dùng nghiệm thu theo [Bảng milestone](milestone-board.md), không cần đọc phần kỹ thuật bên dưới. Ngày 28/09/2026 đã xác nhận Dũng duyệt và giữ đơn vị gốc từng tài khoản; tổng hợp sang USDT để sau khi có FX policy. M0 chưa hoàn thành toàn bộ.

Cập nhật 2026-09-26: tài liệu đã được cập nhật sau review với Thạch; sẵn sàng bước chuẩn bị triển khai. Đã có local synthetic code pilot và workbook review nhập liệu; chưa có workbook vận hành/close chính thức. [Implementation readiness](implementation-readiness.md) chia synthetic development và production gates; M0–M3 chưa được đánh dấu hoàn thành.

| Task | Deliverable | Responsible | Dependency / acceptance |
|---|---|---|---|
| M0.1 | System charter: scope, owner, currency, timezone, opening date | Owner + Codex | Owner duyệt O1–O3; không lấy handoff date làm opening mặc định. |
| M0.2 | Versioned policy: valuation, FX, liquidity, cash flow, close, materiality | Owner quyết định; Codex đặc tả | O5–O9 có quyết định hoặc đánh dấu metric bị deferred. |
| M0.3 | Workbook/schema template, permissions, private evidence/backup design | Codex + custodian | Baseline hiện tại dùng cho local synthetic development; policy thật/permissions được chốt trước activation. |
| M0.4 | Runbooks import/correction/close/restore | Codex; owner review | Demonstrate raw retention, reversal và preserved snapshot bằng synthetic data. |
| M1.1 | Entities/accounts inventory, trading/margin accounts riêng | Owner cung cấp; Codex chuẩn hóa | M0; mỗi account có entity, currency mode, custody, pool. |
| M1.2 | Financial assets/property/business interests/debt/guarantees inventory | Owner + Codex | Stable IDs, ownership evidence, debt treatment, không double-count. |
| M1.3 | Source coverage và evidence manifest | Custodian + owner | Statements đúng cutoff, valuation evidence, missing-data queue. |
| M1.4 | Wealth map sign-off | Owner | Tất cả asset classes được xác nhận có/không/unknown; unknown material chưa qua M1 gate. |
| M2.1 | Immutable raw imports + dedup review | Codex/custodian | M1 source manifest; repeated import không double-post. |
| M2.2 | Opening entries + accepted balances/valuations/FX | Codex; owner review | Quantity và native balances reconcile từng account; margin/debt đầy đủ. |
| M2.3 | Corrections và reconciliation issue resolution | Custodian + owner | USDT basis unknown giữ nguyên flag; XRP discrepancy có evidence giải thích; không bịa giá vốn. |
| M2.4 | Opening reconciliation sign-off và frozen baseline | Owner | Tất cả material gaps giải quyết; total khớp components, ownership/debt đúng; performance eligibility riêng. |
| M3.1 | Metrics views + cash-flow classification | Codex | M2; metric contract approved, unavailable inputs rõ ràng. |
| M3.2 | One-page Sheets CFO dashboard và 4 charts | Codex | TNW/LNW/debt/allocation/flows traceable; không xây custom UI. |
| M3.3 | First monthly close + export + restore verification | Custodian; owner approve | Snapshot bất biến, metric totals rebuild, source/FX selections frozen. |
| M3.4 | Operational handover | Owner + Codex | Owner trả lời được wealth/location/flows/liquidity/debt; close duration đo thực tế để làm baseline. |

## Definition of done

- **M0:** signed charter + ADR decisions + data dictionary + access/backup plan; không có implicit default ảnh hưởng metric đang dùng.
- **M1:** scope đầy đủ đã ký, tài khoản và economic positions có IDs/evidence; tài sản không tồn tại được owner xác nhận thay vì bỏ trống.
- **M2:** accepted opening balance được đối soát theo currency/quantity trước conversion; từng discrepancy có disposition. Market-value report có provenance; missing cost basis không làm lệch opening equity hoặc giả tạo lợi nhuận.
- **M3:** dashboard dùng accepted data; closed snapshots có input manifest, approval, version, backup; original và restated views không lẫn nhau. Không có đủ ba tháng spending thì runway N/A; không có tháng trước thì monthly change N/A.

## Acceptance scenarios cần kiểm tra khi triển khai

1. Import cùng CSV hai lần: giữ evidence/raw attempts nhưng accepted holdings không đổi.
2. Hai legitimate trades cùng thời điểm/amount: không auto-collapse khi source IDs khác nhau.
3. Transfer nội bộ và fee: consolidated transfer flow = 0, fee ghi đúng một lần.
4. Sai expense 1,000 thay vì 100: original + reversal + replacement ra 100; original record còn nguyên.
5. Closed month restated: report gốc unchanged, new version có delta −900 expense và approval, as-reported cutoff vẫn tái tạo đúng.
6. Property gross 500, debt 200, ownership 100%: TNW contribution 300; không tiếp tục trừ 200. Business equity 100 gồm cash 20: contribution vẫn 100.
7. FX thay đổi và late-arriving source: closed snapshot không đổi; current/restated report chọn cutoff đúng.
8. Unknown balance/FX/price: report incomplete, không coi là 0; material issue chặn close.
9. Partial entry append, dangling FK hoặc imbalance: chưa published, không lọt vào dashboard.
10. USDT thiếu basis: market value có thể hợp lệ sau reconcile, profit không bằng holdings; XRP unresolved thì affected report có flag/gate.
11. Investment → trading transfer thiếu approved Decision: reject publish; account thuộc pool không tự đổi để né rule.
12. Restore export giữ nguyên IDs, decimal quantities, events và frozen snapshot totals/checksums.

## Thứ tự và thời gian

M0 → M1 → M2 → M3. Dự kiến weeks 1–3 cho v0.1 khi sources sẵn sàng. Nếu historical statements thiếu, ưu tiên opening economic balance sheet và issue register; không lấp gap bằng estimate không gắn nhãn. M7 close dưới 30 phút là mục tiêu tương lai, không phải cam kết M3.

Owner cần cung cấp sau approval: aliases của entities/accounts, loại tài sản/nợ, quyền sở hữu, cutoff và statements/CSV/valuation evidence thích hợp. Không cần credentials hoặc thông tin bí mật truy cập tài khoản.

## Acceptance bổ sung sau product review

13. Chưa duyệt O6: LNW = null/DEFERRED_POLICY; không suy ra liability scope từ TNW treatment.
14. Mortgage vừa direct vừa embedded: debt breakdown không cộng hai lần.
15. AI nhận missing policy: không gọi concentration là policy breach; thiếu input phải nêu unavailable.
16. Report phân biệt synthetic/draft/closed/restated, chỉ rõ cutoff, source và approval state.
17. Owner không cần nhập debit/credit; biểu mẫu và issue queue dùng ngôn ngữ tài sản, thu/chi, chuyển tiền, vay/trả nợ.
