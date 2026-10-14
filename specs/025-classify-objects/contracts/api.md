# Contracts 025
- `category-object-kind` `{category: id danh mục hoặc khóa gốc hệ thống, kind: 'NONE'|'PERSON'|'LOAN'|'PROPERTY'|'INHERIT'(chỉ danh mục con), reason?}`
- `object-quick-create` thêm `kind:'PERSON'` `{name}`
- `view.categories.roots[].object_kind`, `nodes[].object_kind` (khai báo) và `nodes[].effective_object_kind`; `object_kinds` nhãn.
- `classify`: `profile` tùy chọn; nếu có phải đúng loại đối tượng hiệu lực của (danh mục, danh mục con), hoặc quy tắc cũ khi chưa khai.
