# Contract — xóa hẳn danh mục

**Hành động** `category-delete` `{category, reason}` (không đổi đầu vào).
- Thành công chỉ khi `deletable=true` cho danh mục đó trong `categories.nodes[]` của `/api/state`.
- Bị chặn → lỗi kiểm tra với một thông báo, ví dụ:
  - `Còn 36 dòng lịch sử cũ (kể cả lần migrate đã hủy) thuộc hoặc từng thuộc danh mục này; chỉ có thể lưu trữ.`
  - `Danh mục được ghi trong 7 lần migrate lịch sử cũ; chỉ có thể lưu trữ.`
  - `Còn 5 đối tượng thành viên; gỡ hoặc chuyển đối tượng, hoặc lưu trữ danh mục.`
  - `Danh mục từng có đối tượng thành viên (đã gỡ/chuyển); chỉ có thể lưu trữ.`
- Không đổi: thông báo sẵn có (danh mục con, khoản vay, đã phân loại).
