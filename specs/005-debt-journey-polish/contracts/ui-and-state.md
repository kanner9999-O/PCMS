# Contracts — 005 debt-journey-polish

## 1. State payload (`GET /api/state`, khóa `debts`)
Thêm `debts.summary` và `debts.loans[].completion_blocker` như [data-model.md](../data-model.md). Các khóa cũ giữ nguyên tên và nghĩa. Backend cũ không có hai khóa này → UI phải chạy chế độ cũ (gate theo sự tồn tại của `debts.summary`).

## 2. API
Không thêm endpoint. `/api/loan-cash-report` giữ nguyên tham số `{date, period}` và kết quả `{start,end,period,totals,cash_difference,entries}`; không đổi số.

## 3. UI (hành vi người dùng thấy)

| Màn / phần | Hợp đồng |
|---|---|
| Đầu màn Công nợ | Khối "Tổng quan": phải thu, phải trả (hai số riêng), số người, số khoản đang hoạt động/đã hoàn tất/cần kiểm tra lại, số khoản cần thiết lập; nhãn "NHÁP · theo dữ liệu hiện có"; ghi rõ phạm vi = toàn bộ khoản, không theo bộ lọc |
| Dòng từng người | giữ nguyên |
| Khoản có `completion_blocker.code=='BLOCKED'` | hiện dòng "Chưa thể hoàn tất: {message}" + nút đi tới "Bảng kê lãi" (đã có `settlementList`) |
| Khoản `READY` | hiện "Đủ điều kiện kiểm tra hoàn tất" + nút mở `completionCheck`; không tự hoàn tất |
| Khoản `NEEDS_SETUP` | hiện "Cần thiết lập" thay vì gợi ý tất toán |
| Nhãn trạng thái khoản | một chip trạng thái; nút còn lại là "Hoàn tất / lịch sử" |
| Hộp thoại báo cáo dòng tiền | ngày mặc định = hôm nay nếu thuộc kỳ nguồn, ngược lại = ngày nguồn mới nhất kèm dòng giải thích; cảnh báo khi kỳ không giao kỳ nguồn |
| Tổng quan tài khoản | dòng "Khoản vay liên quan: N · Mở Công nợ" khi N>0 |
| Chi tiết khoản | nút "Mở tài khoản" |

## 4. Bất biến phải giữ (kiểm bằng test)
- Cộng các dòng người = `summary.receivable_total` / `payable_total`.
- `loans_by_status` cộng lại = tổng số khoản đã thiết lập hoặc không (mỗi khoản đúng một trạng thái).
- Gọi `/api/state` hai lần cho cùng dữ liệu không ghi sự kiện; `events` không tăng.
- Báo cáo dòng tiền cho cùng `{date, period}` trả y hệt trước/sau thay đổi.
