# Data Model — 008 category-management

**State mới**: `categories`: danh sách nút; `category_roots`: `{rootKey: description}`.

| Thực thể | Trường (ràng buộc) |
|---|---|
| root (hằng số) | key ∈ {income, expense, principal, interest, investment, transfer, unknown}; tên hiển thị cố định; chỉ `description` sửa được (≤500) |
| node | `id`, `name` (1–100 sau trim; duy nhất giữa các nút cùng cha, casefold + NFC, tính cả ARCHIVED), `description` (≤500), `parent` (rootKey hoặc id nút), `root` (dẫn xuất), `status` ACTIVE\|ARCHIVED, `created_at`, `history[]` |
| history item | `{at, action: CREATE\|RENAME\|MOVE\|DESCRIBE\|ARCHIVE\|RESTORE, before, after, reason}`; `reason` bắt buộc khi ARCHIVE |
| allocation (mở rộng) | `{category, amount, profile}` + `node` tùy chọn: nút ACTIVE có `root == category` (chỉ khi gán) |

Ràng buộc: độ sâu ≤ 4 (gốc = 1); không vòng lặp; không xóa nút; lưu trữ nút chặn nếu còn con ACTIVE; khôi phục cần cha ACTIVE (hoặc gốc).

**Dẫn xuất `view['categories']`**: `roots[{key,name,description,totals}]`, `nodes[{id,name,description,parent,root,status,depth,totals}]`, `totals = {in,out,net,parts,transactions}` (chuỗi Decimal, VND). **`category_history(d)`** → `{category, path, evidence, source_notice, totals, rows[]}`.
