# Research — Spec 045

## R1. Tổ chức spec
- **Decision**: spec mới 045 gộp yêu cầu R202 và hai sửa lỗi của spec 044 (bảng truy nguyên); `specs/044.../review.md` chỉ thêm liên kết "sửa ở 045".
- **Rationale**: 044 đã phát hành; không viết lại lịch sử. Nguyên tắc IX: một lần phát hành cho cùng khái niệm "danh mục đã dùng / lưu trữ".

## R2. Tổng phần thuộc danh mục lưu trữ
- **Decision**: tính ở backend trong cùng vòng tính tổng: với mỗi phần phân loại, mọi tổ tiên (gồm gốc) của một danh mục lưu trữ trên chuỗi của phần đó nhận phần này vào `archived_share` (giao dịch đếm một lần).
- **Alternatives**: cộng ở giao diện tổng các danh mục lưu trữ con — loại vì đếm trùng giao dịch tách hai phần vào hai danh mục lưu trữ.

## R3. Dấu vết thành viên khi xóa đối tượng
- **Decision**: trước khi bỏ quan hệ, lưu `memberships=[{category,status,history}]` vào bản ghi `object_deleted`; `cat_in_use_fast` coi danh mục xuất hiện trong `memberships` (cả `category` và `history[].from/from_/to`) là "từng có đối tượng thành viên".
- **Alternatives**: giữ `category_objects` trạng thái DELETED — loại vì nhiều chỗ đọc `category_objects` và tra hồ sơ theo `profile` (hồ sơ đã bị xóa) → dễ lỗi; cấm xóa đối tượng chưa dùng — trái yêu cầu.

## R4. Thông báo
- **Decision**: nguyên nhân + gợi ý theo trạng thái: danh mục hoạt động → "Lưu trữ để ẩn khỏi danh sách đang sử dụng"; đã lưu trữ → "giữ lưu trữ hoặc khôi phục"; khoản vay đang gắn → phải chuyển khoản vay trước khi lưu trữ (vì lưu trữ cũng bị chặn); danh mục con → nêu rõ con cũng phải xóa được hoặc chuyển đi.

## R5. Cha lưu trữ – con hoạt động
- **Decision**: không tạo được qua giao diện/hệ thống (đã kiểm: lưu trữ cha cần con đã lưu trữ; khôi phục con cần cha hoạt động; tạo/đổi cha vào danh mục lưu trữ bị chặn). Dữ liệu thật: 0 trường hợp. Phòng thủ: tab hoạt động vẽ cha lưu trữ dạng ngữ cảnh khi còn con hoạt động; bộ chọn theo cấp cho đi qua cha đó. Có test khẳng định các đường chặn.

## R6. Đo hiệu năng
- Đo `view()` trên bản sao dữ liệu thật trước/sau.
