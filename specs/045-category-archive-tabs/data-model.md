# Data model — Spec 045

| Thực thể | Thay đổi |
|---|---|
| `object_deleted[]` | Bản ghi mới thêm `memberships: [{category, status, history}]` (dấu vết quan hệ trước khi xóa). Bản ghi cũ không đổi. |
| `categories.roots[]`, `categories.nodes[]` (view, chỉ đọc) | Thêm `archived_share` (`{in,out,net,parts,transactions[,net_spend]}` hoặc null) |
| `categories.nodes[]` (view) | Thêm `delete_block` (chuỗi/null, cùng nguồn với `deletable`), `restore_block` (chuỗi/null), `archived_at`, `archive_reason` (từ lần ARCHIVE gần nhất, null nếu không có) |

Trạng thái danh mục: ACTIVE ↔ ARCHIVED (không đổi). Xóa hẳn khi `delete_block` null.
