# Quickstart — kiểm 014 category-completion
1. `PYTHONPATH=src:tests python3 -m unittest test_p16_acceptance test_p15_acceptance … test_p01_acceptance` · `node --check src/pcms/web/p01.js` · `for f in tests/js/*.test.cjs; do node $f; done`
2. Server QA bộ giả cổng 8801 (`/tmp/pcms-cat2-qa`): tài khoản 7 giao dịch trải tháng 9–10, có giao dịch tách, đối tượng (khoản vay, BĐS).
3. PO UI: Danh mục → "+ Gốc mới" "Kinh doanh nhỏ" loại nhóm chi → con "Nhập hàng" → phân loại giao dịch chi vào "Nhập hàng" (≤4 thao tác); Chi tiêu hệ thống không tăng; thử tên "chi tiêu" bị chặn; lọc tháng 9 → tổng chỉ tháng 9, lịch sử cùng kỳ; kỳ trống hiện "chưa có giao dịch trong kỳ này"; ngày kết thúc < bắt đầu bị chặn; bước xem toàn đợt: khối "Theo danh mục" khớp số giao dịch gốc và tiền vào/ra, mở chi tiết → mở dòng nguồn; 375px.
4. SHA256 `outputs/p01-user-trial` trước/sau; PR → merge; restart 8792; mở UI chính chỉ đọc.
