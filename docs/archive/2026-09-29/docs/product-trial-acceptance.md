# Nghiệm thu bản sản phẩm cơ bản

Ngày 28/09/2026. **Bàn giao để Thạch dùng thử**, không thay thế nghiệm thu dữ liệu tài chính thật của Dũng. Các lựa chọn của owner được Codex mô phỏng theo quyền được giao; không yêu cầu người dùng tiếp tục điền workbook để bắt đầu.

| Mốc gốc | Kết quả có thể dùng thử | Điều kiện kiểm chứng ngay | Phần chưa được khẳng định |
|---|---|---|---|
| M0 — Cách vận hành | Kỳ mẫu, nguyên tệ, USDT báo cáo, vai trò Dũng mô phỏng, policy và sao lưu đã chọn | Mở Thiết lập, đọc tỷ giá/ngưỡng; chỉnh policy và thấy cảnh báo tính lại | Policy thật, phân quyền nhiều người |
| M1 — Biết có gì | Tài khoản, 4 nhóm tài sản, tỷ lệ sở hữu, khoản nợ | Thấy 5 tài khoản, 8 tài sản, 2 khoản nợ; thêm tài sản/nợ | Inventory thực của gia đình, chứng từ sở hữu thật |
| M2 — Số liệu khớp | Thu/chi/chuyển/mua/bán/vay/trả gốc, CSV review, sửa sai và đối soát | Chuyển nội bộ không làm tăng tài sản; nhập trùng bị chặn; lệch số dư chặn close | Tự ghi sổ mẫu XLSX bank thật chưa có |
| M3 — Báo cáo & đóng kỳ | Tổng quan, dòng tiền, chốt kỳ, restatement, báo cáo CSV, backup/restore | Chốt rồi sửa: snapshot cũ không đổi, chốt lại có v2; tải lại trang vẫn giữ số liệu | Báo cáo tài chính chính thức, chứng cứ số dư thật |
| M4 — Review rủi ro | Ngưỡng tập trung, crypto, dự phòng; stress giá từng nhóm | Đổi ngưỡng hoặc sốc giá thấy kết quả thay đổi; sổ không tự phát sinh lệnh | AI ngôn ngữ, dự báo xác suất, kiểm định rủi ro thị trường |
| M5 — Phân bổ vốn | Đề xuất → duyệt thử → thực hiện → lưu quyết định | Chuyển Đầu tư → Trading cần quyết định đúng số tiền; không thực hiện hai lần | Kết nối chuyển tiền thật |
| M6 — BĐS & doanh nghiệp | Giá phần sở hữu, nợ thế chấp, doanh nghiệp equity, ghi thu/chi gắn tài sản | Đất sở hữu 50% chỉ tính một nửa; tiền/nợ nội bộ doanh nghiệp không cộng/trừ trùng | Sổ kế toán doanh nghiệp, hợp đồng thuê, thuế đầy đủ |
| M7 — Vận hành close | Một màn hình đối soát/chốt kỳ và hướng dẫn một vòng thao tác | Người dùng đi trọn một vòng với nguồn giả lập | Chưa chứng minh close thật dưới 30 phút |
| M8 — Review định kỳ | Ghi quyết định review, xem lịch sử, giữ báo cáo theo kỳ | Tạo quyết định có lý do, duyệt thử và xem lại | Chưa có nhắc lịch hay bằng chứng vận hành nhiều chu kỳ |
| M9 — Kế hoạch 1/3/5 năm | Mô hình vốn đầu, góp hàng tháng, tăng trưởng giả định và mục tiêu | Thay giả định, xem 3 thời hạn, lưu giả định thành quyết định | Không phải dự báo; chưa thuế/phí/lạm phát/lịch trả nợ tương lai |

## Bằng chứng kiểm tra

- 61 bài kiểm tra Python đã qua: 49 kiểm tra pilot/adapter/review cũ và 12 kiểm tra sản phẩm mới.
- Kiểm tra trình duyệt trên dữ liệu tách riêng: các màn hình desktop/mobile không tràn ngang toàn trang; không lỗi JavaScript.
- Vòng thao tác giao diện đã thử: tạo chi → sửa số tiền → định giá BĐS → đề xuất/duyệt/thực hiện phân bổ → nạp CSV/ghi một dòng/bỏ một dòng → đối soát/chốt → tạo bản điều chỉnh → tải lại → tải backup/khôi phục.
- Tài sản ròng mẫu ban đầu 745.960 USDT. Chi 1 triệu VND giảm 40 USDT theo tỷ giá giả lập. Chuyển vốn giữa hai tài khoản giữ nguyên tổng tài sản và thu/chi.
- Dữ liệu bàn giao ở cổng 8787 giữ bộ mẫu ban đầu; dữ liệu kiểm thử thay đổi nằm riêng tại cổng 8788 và thư mục tạm.

Không tự ghi “Dũng đã nghiệm thu” hay “production-ready”. Thạch có thể nghiệm thu bản cơ bản bằng cách thực hiện các bước ở [hướng dẫn dùng thử](runbooks/product-trial.md).
