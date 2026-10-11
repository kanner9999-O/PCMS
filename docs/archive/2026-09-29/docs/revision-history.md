# Revision history

## 2026-09-26 — Product clarification và implementation preparation

Yêu cầu: cập nhật tài liệu sau trao đổi với Thạch và chuẩn bị triển khai. Không có lựa chọn cụ thể mới về base currency, cutoff, ownership hoặc policy tài chính; không tự ghi approved_by cho Thạch/Dũng.

- Thêm product brief: core, input/output, bốn khu vực người dùng, sáu feature workflows, acceptance và vai trò.
- Thêm AI contract: deterministic calculations, approved policy checks và AI reasoning; nguồn, versions, uncertainty, review và giới hạn quyền.
- Thêm readiness plan: synthetic development, backlog S0–S5, first slice và production gates theo O1–O9.
- Sửa ER optional relationships của journal lines/valuations, source links nhiều–nhiều, close chưa có snapshot và generic record links; nêu rõ giới hạn joint accounts/cross-collateral.
- Sửa debt explanation: direct obligation và embedded treatment có thể chồng nhau; không cộng hai lần.
- Rút công thức LNW cũ khỏi baseline; DEFERRED_POLICY cho đến khi chốt eligibility/horizon/liability scope.
- Làm rõ mẫu số allocation dùng economic components (property/business equity), không gọi nhầm gross assets.
- Thêm metric eligibility/reason và synthetic label; cập nhật milestones/ADR/README nhất quán.
- Không thay đổi dữ liệu tài chính, tạo workbook, triển khai code hoặc đánh dấu M0–M3 hoàn thành.

Tài liệu hiện tại là bản sửa đổi của thiết kế, không phải overwrite lịch sử tài chính. Snapshot/ledger immutability áp dụng khi có dữ liệu nghiệp vụ, không ngăn chỉnh tài liệu thiết kế.

## 2026-09-26 — Bắt đầu implementation theo yêu cầu tiếp theo

- Thêm Python standard-library local pilot: append-only publication, Decimal, validation, raw evidence, dedup, reconciliation, frozen reports, corrections, restatement và backup/restore.
- Thêm pilot entry JSON Schema, checked-in synthetic fixtures, automated tests, CLI và runbook.
- Demo kiểm chứng 29 events, TNW giả lập 414.390 → 415.290 sau correction; báo cáo gốc không đổi.
- Chưa triển khai workbook/CSV/FX/live permissions; chưa có production approval hoặc owner settings thật. Không chuyển source of truth dài hạn sang local event files.

## 2026-09-28 — Sample bank XLSX adapter

- Thêm `bank-stage` CLI và read-only adapter cho mẫu sáu cột được cung cấp; source files không thay đổi.
- Map tiền ra/vào thành movements VND, giữ ngày, mô tả, reference, running balance và source row; chưa infer income/expense hoặc ghi ledger.
- Lưu raw bytes/SHA-256 và normalized staging trong private-data, ngoài Git; fixtures chỉ synthetic.
- Đối soát đầu/cuối kỳ và từng dòng; giữ repeated references, không dedup một cách mất dữ liệu.
- Thêm 14 tests; tổng 40 tests đạt. M2 vẫn chưa nghiệm thu vì source discrepancies cần review.

## 2026-09-28 — Owner review workbook và xác nhận vận hành

- User yêu cầu bám milestone, tránh báo cáo chi tiết kỹ thuật. Thêm milestone-board là trang nghiệm thu chính.
- Xác nhận Dũng duyệt số liệu; giữ VND/USDT theo tài khoản; tổng hợp USDT để sau. Scope và FX rules còn mở, không coi là approved.
- Bàn giao workbook review sáu tab với 76 movements, formulas đối soát, dropdown phân loại và câu hỏi bằng chứng; chưa là official financial report.
- Thêm verified review package và nhận câu trả lời pending-review, không tự ghi sổ; phát hiện source edits và duplicate source IDs.
- Bộ test 49 cases đạt; kiểm tra formulas, render tất cả sheets và XLSX round-trip.

## 2026-09-28 — Sản phẩm dùng thử cơ bản

Thạch thay phạm vi từ hỗ trợ milestone/workbook sang hoàn thành sản phẩm dùng thử, giao Codex tự chọn thiết kế và policy, dùng dữ liệu giả lập. Đã bổ sung web local tiếng Việt, inventory bốn nhóm tài sản, cashflow, transaction/correction, nhập CSV, policy/risk/scenario, phân bổ có duyệt, chốt/restatement, kế hoạch vốn và backup/restore. Ghi riêng các quyết định và giới hạn trong product-trial-decisions.md; không thay đổi owner-settings thật hay đưa sao kê thật vào demo. Cập nhật banner trong tài liệu baseline để phân biệt quyết định cũ với phạm vi mới.

## 2026-09-28 — Nhập liệu liên tục, tài khoản và công nợ theo người

Thạch làm rõ không bắt buộc chọn tháng: nhập dữ liệu và phân loại bất cứ lúc nào, hệ thống kiểm tra tính đúng đắn và theo dõi lịch sử tài khoản. Đã triển khai khai báo ngân hàng/sàn, số dư đầu theo ngày, lịch sử số dư, tài sản theo nơi giữ, giao dịch chưa phân loại, chia gốc/lãi, phân loại lại, ghép chuyển nội bộ, CSV chồng kỳ, mapping XLSX mẫu, bên liên quan, nhiều khoản vay/cho vay và báo cáo theo ngày. Giữ dữ liệu/snapshot cũ; backup trước cập nhật. Lãi theo ngày, đa ví thanh toán, margin/futures và dữ liệu thật chưa được coi là hoàn thành.


## 2026-09-29 — Domain model hiện tại

Theo yêu cầu của Thạch, bổ sung domain-model.md đối chiếu với mã nguồn bản thử. Phân biệt mô hình nghiệp vụ, cấu trúc đang triển khai và thiết kế ledger dài hạn; làm rõ Entity chưa có danh mục riêng, Position là kết quả tính, Loan hai chiều lưu trong liabilities, Account.pool đang là nhóm vốn có ảnh hưởng kiểm soát. Ghi đề xuất tài khoản dùng chung/quỹ riêng là hướng chưa triển khai. Không thay đổi dữ liệu hoặc hành vi ứng dụng trong lần cập nhật tài liệu này.


## 2026-09-29 — Tài liệu use case

Theo yêu cầu của Thạch, bổ sung use-cases.md với 21 tình huống sử dụng, tác nhân, sơ đồ tổng quan, điều kiện, luồng chính/ngoại lệ, kết quả và tiêu chí nghiệm thu. Bám bản thử hiện tại, nhập liên tục không bắt buộc tháng; phân biệt vai trò duyệt giả lập, hành vi đã có và backlog. Liên kết README/domain model; không thay đổi mã chạy hay dữ liệu.


## 2026-09-29 — Use case v1.1: hồ sơ tài khoản và import lịch sử

Theo điều chỉnh trực tiếp của Thạch: UC-01 bỏ Mục đích; gộp UC-03 vào UC-02, xử lý trùng ngay trong import dựa vào toàn bộ lịch sử đã có của tài khoản. Khai báo và import nằm trong cùng hồ sơ tài khoản, mục Import lịch sử giao dịch. UC-07 bổ sung lịch sử sao kê từ ngày tracking đến hôm nay, giữ dòng nguồn khác các phần phân loại và hiển thị độ bao phủ. Giữ mã UC-03 đã gộp để truy vết, không đánh lại mã. Cập nhật sơ đồ, danh mục, luồng, ngoại lệ, kịch bản, tiêu chí U11-01–10, domain model và README. Đây là cập nhật đặc tả đã chốt; chưa thay mã hay dữ liệu ứng dụng.
