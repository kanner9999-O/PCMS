# Contract — `/api/state` → `categories`, và các hành động liên quan

- `nodes[].deletable == (delete_block is None)`; `category-delete` thành công ⇔ `deletable`; `category-cleanup` chỉ đề xuất danh mục con có `deletable`.
- `delete_block` ví dụ:
  - `Đang có 2 đối tượng thành viên nên danh mục đã được dùng; không thể xóa hẳn. Lưu trữ để ẩn khỏi danh sách đang sử dụng.`
  - `Danh mục từng có đối tượng thành viên (đã gỡ, chuyển hoặc xóa đối tượng); không thể xóa hẳn. Lưu trữ để ẩn khỏi danh sách đang sử dụng.`
  - Danh mục đã lưu trữ: phần gợi ý là `Giữ lưu trữ hoặc khôi phục.`
- `restore_block`: `Danh mục cha «<đường dẫn>» đang lưu trữ; khôi phục cha trước.` hoặc null.
- `roots[].archived_share`, `nodes[].archived_share`: tổng (tiền, số phần, số giao dịch) của các phần thuộc danh mục lưu trữ nằm dưới mục đó; null nếu không có. Tổng của mục (`totals`) không đổi.
- `object-delete`, `category-object-delete`: đầu vào không đổi; bản ghi `object_deleted` thêm `memberships`.
