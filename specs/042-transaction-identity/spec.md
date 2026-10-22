# Spec 042 — Phân loại và định danh nguồn
Trạng thái: đã làm rõ theo yêu cầu 22/10, chưa nghiệm thu. R191–R194; A58–A59.
## Quyết định
User yêu cầu cả hai nội dung; việc chọn phân loại tài chính thật vẫn do user xác nhận.
## Tư vấn kế toán
Một nguồn tiền ghi một lần trong tài khoản. Phân loại không tạo tiền. Sửa bằng dấu vết điều chỉnh; nguồn/snapshot bất biến. Không đưa kết luận thuế.
## Bản đồ tác động
- categories.py: tổng theo allocation, lịch sử đối tượng, legacy summary.
- p01.py: kiểm nguồn, publish, classify + adjustment.
- legacy_import.py: tài khoản, identity xuyên đối tượng, conflict, xử lý thiếu phạm vi.
- server.py + web/p01.js: xem trước sửa phân loại và xác định tài khoản lịch sử, cảnh báo.
- Objects/reports lấy cùng cat_parts; snapshot giữ nguyên. Debt/Realty đóng băng theo R190.
- Sàn: chưa có importer sao kê; không tuyên bố đã hỗ trợ.

## Bổ sung khi hoàn thiện (22/10/2026, Claude — không đổi quyết định nghiệp vụ)
- **Hai lối giải quyết sai lệch quan hệ** (người dùng chọn, hệ thống không tự chọn): thêm đối tượng vào danh mục phân bổ (không đổi tiền, không đổi phân loại) hoặc điều chỉnh nơi phân loại **trong cùng loại gốc**. Không bao giờ gợi ý chuyển Lãi vay sang Gốc vay.
- **Xem trước phải bằng kết quả thật**: điều chỉnh bị chặn khi khoản vay có nhóm riêng (nơi hiển thị do nhóm quyết định) hoặc giao dịch tách nhiều phần; xác định tài khoản bị chặn nếu làm đổi cách tính của lần migrate khác.
- **Chứng từ**: dòng lịch sử trùng hệt giao dịch sao kê cùng tài khoản vẫn được lưu để truy nguyên nhưng không cộng tiền. Dòng thiếu mã không nhập được. Mã chỉ khác hậu tố (`\BNK`, `\XMI`…) là gần trùng, phải đối chiếu.
- **Bản đồ tác động bổ sung**: server vận hành đọc `p01.js` từ đĩa mỗi lần tải trang, nên mã nháp đặt trong thư mục vận hành sẽ được phục vụ cho app thật ngay. Đợt này làm trong worktree riêng `../PCMS-042` (nhánh `042-transaction-identity-impl`); thư mục vận hành giữ mã P43.
