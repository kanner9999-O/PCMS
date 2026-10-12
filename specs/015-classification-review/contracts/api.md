# Contracts — 015 classification-review
`POST /api/classification-review {account, scope?: all|recent|range, start?, end?}` → xem `data-model.md`. Lỗi: tài khoản không tồn tại, `scope` lạ, ngày không hợp lệ hoặc kết thúc trước bắt đầu → `ValidationError` tiếng Việt. Chỉ đọc (không tăng số sự kiện).
UI: nút "Kiểm tra phân loại" ở bước Phân loại; màn có "← Quay lại phân loại"; chọn phạm vi (Cả tài khoản mặc định, 24 giờ qua, Khoảng ngày); "Thu gọn tất cả / Mở tất cả"; "Xem nguồn" dùng `sourceDetail`.
