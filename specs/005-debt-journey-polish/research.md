# Research — 005 debt-journey-polish

Không có mục NEEDS CLARIFICATION. Các quyết định dưới đây dựa trên đọc mã hiện hành (11/10/2026).

## R1 — Kỳ mặc định của báo cáo dòng tiền
- **Hiện trạng**: `loanCashReport()` trong `p01.js` mặc định ngày = hôm nay (múi giờ Việt Nam), kỳ = tháng. Backend `loan_cash_report` không biết kỳ nguồn.
- **Quyết định**: tính ở client từ `view.reports[].source_end` (đã có trong state: `source_end`, `source_periods`). Nếu hôm nay không thuộc kỳ nguồn nào của bất kỳ tài khoản nào thì mặc định ngày = `source_end` lớn nhất, và hiện dòng "Đang chọn ngày nguồn mới nhất: …". Lựa chọn của người dùng (đổi ngày/kỳ) giữ nguyên trong phiên mở hộp thoại.
- **Cảnh báo "chưa có nguồn"**: sau khi có kết quả, nếu khoảng `[start,end)` của báo cáo không giao với bất kỳ `source_periods` nào, hiện cảnh báo kèm các khoảng nguồn đã ghi; nếu giao một phần, nêu "chỉ có nguồn cho một phần kỳ".
- **Phương án loại**: sửa backend nhận kỳ mặc định — không cần, đổi API không cần thiết.

## R2 — Tổng quan công nợ
- **Hiện trạng**: `debt_register` trả `people[]` và `loans[]` với `receivable/payable` theo người, `completion_status` theo khoản và người; UI chỉ liệt kê.
- **Quyết định**: thêm `summary` vào kết quả `debt_register`, tính bằng `Decimal`: `receivable_total`, `payable_total`, `people` (đếm), `loans_by_status` (ACTIVE/COMPLETED/NEEDS_REVIEW), `needs_setup` (khoản chưa có `debt_setup`), `excluded` (khoản bị loại khỏi tổng do lỗi). Cộng đúng tập mà các dòng từng người đang cộng (khoản có lỗi/chưa thiết lập đã bị loại khỏi `receivable/payable` người — giữ nguyên, chỉ tổng hợp).
- **Lý do**: giữ Decimal precision của backend (constitution III), UI không cộng tiền bằng `Number`.
- **Phương án loại**: cộng ở client bằng `Number` (vi phạm constitution III).

## R3 — Gợi ý việc kế tiếp cho khoản hết gốc
- **Hiện trạng**: `closure_preview` ném `ValidationError` với thông điệp tiếng Việt cho từng điều kiện thiếu (bảng kê chưa phủ, còn lãi, nháp, thiếu xác nhận…).
- **Quyết định**: thêm `LoanCompletion.completion_blocker(s, profile)`: nếu khoản `LOAN`, đã có `debt_setup`, gốc hiện tại bằng 0 và trạng thái `ACTIVE`, gọi `closure_preview` với `closing_date` = ngày nguồn mới nhất ghi nhận cho khoản; bắt `ValidationError` và trả thông điệp, ngược lại `None`. Hàm chỉ đọc, không đổi trạng thái. Với khoản chưa thiết lập thì trả mã `NEEDS_SETUP` (UI hiện "Cần thiết lập").
- **Lý do**: tái dùng đúng điều kiện tất toán, tránh hai nơi lệch nhau.
- **Phương án loại**: viết lại điều kiện ở UI (rủi ro lệch với backend).
- **Ghi chú**: ngày thử dùng ngày giao dịch gần nhất của khoản; nếu khoản chưa có giao dịch thì dùng ngày hiệu lực thiết lập. Thông điệp là gợi ý, không phải kết luận tất toán.

## R4 — Nhãn trạng thái lặp
- **Hiện trạng**: tiêu đề người ghi `· Đã hoàn tất`, nút khoản ghi `Đã hoàn tất · Hoàn tất / lịch sử`.
- **Quyết định**: tiêu đề người giữ nhãn trạng thái; trên khoản thay nút bằng nhãn trạng thái dạng chip + nút "Hoàn tất / lịch sử" (không lặp chữ trạng thái trong nút).

## R5 — Liên kết tài khoản ↔ công nợ
- **Hiện trạng**: có `#debts` ở thanh bên (`debtMode`), `loanDetail` truy tới giao dịch nguồn, `sourceDetail`.
- **Quyết định**: (a) trên tổng quan tài khoản thêm dòng "Khoản vay liên quan: N khoản · Mở Công nợ" khi có giao dịch gắn khoản (đếm từ phân bổ `profile` của giao dịch); (b) trong chi tiết khoản thêm nút "Mở tài khoản" chọn đúng tài khoản chứa giao dịch và quay lại được bằng nút Công nợ sẵn có. Không thêm màn mới.

## R6 — Gate phiên bản
- UI mới dùng tổng quan/gợi ý chỉ khi `view.debts.summary` tồn tại (backend mới); backend cũ → UI cũ chạy như hiện tại (HANDOFF §6, tránh UI gọi API chưa có).
