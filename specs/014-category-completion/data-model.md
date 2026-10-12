# Data Model — 014 category-completion
**Nút danh mục (mở rộng)**: `parent` có thể `None` (gốc tự tạo); `root` = loại ∈ {income, expense, investment} với gốc tự tạo; mọi trường khác như spec 008. Bất biến: gốc tự tạo không đổi `parent`, không đổi `root`; tên gốc duy nhất trong gốc hệ thống + gốc tự tạo; độ sâu ≤4.
**Dẫn xuất**: `category_view(s, start, end)` → thêm `period:{start,end}|null`; `nodes[]` gồm cả gốc tự tạo (`depth=1`, `parent=None`).
`category_history(d)` → thêm `period`, hỗ trợ `account`.
`category_review({account})` → `{account, groups:[{key,name,type,system,status,transactions,objects,in,out,net_spend?,children:[…],}], checks:{transactions,money_in,money_out}, reconciled, draft}`.
