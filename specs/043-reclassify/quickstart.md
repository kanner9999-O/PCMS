# Quickstart kiểm chứng — 043 (dữ liệu giả)
1. Ca Kết (A): `transaction-reclassify` K1 phần 0 → `principal` + khoản vay của Kết; tổng Gốc vay, số dư không đổi; lịch sử Kết tại Gốc vay có 5tr; Gốc vay › Kết mất phần; danh mục con còn.
2. Cùng bản chất: Chi tiêu › A → Chi tiêu › B; đổi đối tượng; đổi cả hai.
3. Nhiều phần: sửa phần 1 của giao dịch 2 phần; phần 0 giữ nguyên; tổng = |giao dịch|.
4. Đích sai: chưa là thành viên / danh mục lưu trữ / nhóm khoản vay ⇒ chặn qua API.
5. B: Gốc vay → Lãi vay cùng khoản vay ⇒ xem trước hiện dư nợ gốc và lãi trước→sau; thiếu xác nhận ⇒ từ chối; có xác nhận ⇒ ghi. `classify` cũ không có xác nhận ⇒ từ chối.
6. Tham chiếu: bảng kê lãi / khoản vay đã hoàn tất / gắn đợt BĐS / chuyển nội bộ đã ghép ⇒ chặn kèm hướng xử lý.
7. Đã duyệt: tự mở phiên điều chỉnh; snapshot giữ nguyên.
8. Xem trước hết hạn: đổi dữ liệu hoặc lựa chọn sau xem trước ⇒ ghi bị từ chối.
9. Lịch sử cũ: đổi danh mục/đối tượng cùng gốc; bản dán gốc giữ nguyên.
10. UI trên `/tmp/pcms-043-qa`: các bước trên qua hộp "Sửa phân loại".
