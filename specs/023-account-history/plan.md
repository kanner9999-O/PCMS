# Plan 023
**Mã**: `src/pcms/account_history.py` (mixin `AccountHistory.account_history`), `p01.py` (thêm vào `P01Store`, build P25), `server.py` (route `/api/account-history`), `web/p01.js` (khối "Lịch sử sao kê" ở bước Nhập nguồn: mốc, 10 giao dịch cuối, tình trạng file nối tiếp; nút "Xem toàn bộ lịch sử" mở hộp rộng có bộ lọc, phân trang, danh sách file; dùng `stmtRowHtml`), test `tests/test_p25_acceptance.py`.
**Constitution**: Decimal, chỉ đọc, dùng dữ liệu sẵn có (không thêm trường lưu), không đổi mốc/snapshot.
