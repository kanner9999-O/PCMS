# Contracts 026
- `category-object-add` `{category: id danh mục hoặc khóa gốc, profile?: id hồ sơ có sẵn, name?: tên mới}`
- `category-object-rename` `{profile, name}` · `category-object-remove` `{category, profile, reason}` · `category-object-move` `{profile, from, to, reason}` · `category-object-delete` `{profile, reason}`
- `view.categories.roots[].objects` / `nodes[].objects`: `[{profile, name, kind, status:'ACTIVE', totals:{in,out,transactions}, deletable, history:[...]}]`
- `POST /api/category-history` thêm `object` (id hồ sơ) để lọc theo đối tượng.
- `classify`: `profile` tùy chọn; phải thuộc đối tượng của chính danh mục/danh mục con đã chọn (hoặc quy tắc cũ khi danh mục chưa có đối tượng).
