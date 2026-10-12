# Contracts — 014 category-completion
Actions: `category-create {name,type,description?}` (không có `parent` → gốc tự tạo; `type` ∈ income|expense|investment, bắt buộc); các action danh mục khác giữ nguyên (`category-edit` không đổi cha/loại của gốc tự tạo).
`POST /api/category-view {start?,end?}` → như `view['categories']` có lọc kỳ + `period`.
`POST /api/category-history {category, start?, end?, account?}` → thêm `period`.
`POST /api/category-review {account}` → xem `data-model.md`.
Lỗi nghiệp vụ → `ValidationError` tiếng Việt (ngày không hợp lệ, `start>end`, tên trùng, thiếu loại…). UI: nút "+ Gốc mới", bộ lọc kỳ, khối "Theo danh mục" trong bước duyệt.
