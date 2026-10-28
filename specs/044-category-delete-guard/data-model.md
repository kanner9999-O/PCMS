# Data model — Spec 044 (không thêm trường, chỉ đọc)

| Thực thể | Trường tham chiếu danh mục | Được xét khi xóa hẳn |
|---|---|---|
| `categories[]` | `parent` | Có (sẵn có) |
| `profiles[]` (LOAN) | `group`, `group_history[].from/to` | Có (sẵn có) |
| `transactions[]`, `snapshots[]` | `allocations[].node`, `classification_history[]` | Có (sẵn có) |
| `legacy_entries[]` | `category`, `classification_history[].before/after.category` | **Mới** |
| `legacy_batches[]` (ACTIVE/VOID) | `category` | **Mới** |
| `category_objects[]` (mọi trạng thái) | `category`, `history[].from/to` | **Mới** |
| `object_moves[]` | `from`, `to` | **Mới** |

Trạng thái danh mục không đổi: ACTIVE ↔ ARCHIVED; xóa hẳn chỉ khi không có tham chiếu nào.
