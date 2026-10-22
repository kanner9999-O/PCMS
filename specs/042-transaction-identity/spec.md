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

## Sửa sau PO review 22/10 (hai lỗi P1, `docs/po-review-042-2026-10-22.md`)
- **Gần trùng mọi thứ tự nhập**: `check_batch` (staging, kiểm lại, ghi) so cả lịch sử cũ đã có tài khoản và giao dịch đã ghi cùng tài khoản; `legacy_identity_status` gắn `NEAR_DUPLICATE` (không cộng, cần đối chiếu) cho dòng lịch sử gần trùng nguồn khác cùng tài khoản; `legacy_preview` so cả sao kê và lịch sử cùng tài khoản. Khác tài khoản không bị coi là gần trùng.
- **Quan hệ phân loại kiểm ngay khi ghi**: `classify` (mọi đường ghi phân loại, kể cả API và điều chỉnh) yêu cầu đối tượng sở hữu là thành viên danh mục hiệu lực (`cat_eff`: nhóm khoản vay, chuyển đối tượng, gộp hồ sơ). Bỏ các ngoại lệ native/legacy/kept; chỉ giữ phần y hệt đã có trên chính giao dịch (dữ liệu cũ xem được, sửa qua "Cần đối chiếu"). Giao diện phân loại chỉ liệt kê thành viên.
- Cờ nội bộ `require_membership` (mặc định bật) chỉ để fixture test dựng **dữ liệu kiểu cũ** trước 042 (P01–P17, bước dựng của P18), không có đường bật/tắt từ giao diện hay API.

## Sửa sau PO review vòng 2 (`docs/po-review-042-r2-2026-10-22.md`)
- **Cùng một file sao kê**: `check_batch` thêm từng dòng của file vào tập kiểm tra; mã lặp y hệt hoặc chỉ khác hậu tố với dòng trước trong cùng file ⇒ BLOCKED, ghi toàn đợt bị từ chối, không giao dịch nào được ghi. Không phụ thuộc thứ tự hai dòng; số dư hợp lệ cũng vẫn chặn (đây là cặp cần đối chiếu, không phải bằng chứng là một giao dịch).
- **Cùng một lần dán lịch sử**: trước đây dòng lặp y hệt trong cùng lần dán bị đánh "trùng" và **tự bỏ qua** (tức tự gộp) — nay là lỗi cần đối chiếu; mã chỉ khác hậu tố trong cùng lần dán cũng là lỗi. "Trùng lần migrate trước" vẫn chỉ áp cho dữ liệu đã ghi từ trước.
- Khác tài khoản: không gắn cờ.
