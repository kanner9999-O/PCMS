# Research — Spec 044

## R1. Một quy tắc cho màn và lệnh
- **Decision**: giữ một hàm `cat_in_use_fast(s,node,blob)`; `category_view` dùng nó cho `deletable`, `category-delete` dùng qua `cat_in_use`.
- **Rationale**: SC-003 (đồng nhất màn–lệnh) đạt theo cấu trúc, không cần đồng bộ hai nơi.
- **Alternatives**: kiểm riêng ở giao diện — loại (lệch giữa màn và API, đúng loại lỗi P1 của 043).

## R2. Phạm vi "đã từng dùng"
- **Decision**: thêm dòng lịch sử cũ (`category` hiện tại, `classification_history[].before/after.category`), mọi `legacy_batches[].category` (kể cả VOID), `category_objects` (mọi trạng thái), `object_moves` (`from`/`to`).
- **Rationale**: R93 "chưa từng dùng (kể cả lịch sử)"; Thạch chốt lịch sử cũ và thành viên hoạt động; lịch sử thành viên/chuyển là lịch sử dùng theo R93.
- **Đối chiếu dữ liệu thật (bản sao chỉ đọc)**: Property chặn (36 dòng, 7 lần migrate, 5 thành viên); Hot Debt chặn (2 thành viên); Bianance, Long Debt không có tham chiếu → vẫn xóa được.

## R3. Thứ tự và nội dung lý do
- **Decision**: danh mục con → khoản vay → giao dịch ngân hàng → dòng lịch sử cũ (đếm) → lần migrate (đếm) → thành viên hoạt động (đếm) → lịch sử thành viên/chuyển. Mỗi lý do kết thúc bằng "chỉ có thể lưu trữ" hoặc hướng xử lý.

## R4. Hiệu năng
- **Decision**: quét tuyến tính theo danh mục (số danh mục nhỏ). Đo `category_view` trên bản sao dữ liệu thật trước/sau.
