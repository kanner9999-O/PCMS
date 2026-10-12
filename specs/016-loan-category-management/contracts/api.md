# Contracts: 016

**Hành động mới** (qua `POST /api/action`, lưu sự kiện):
- `loan-regroup` `{profile, node, effective_date, reason}`: `node` rỗng/`"principal"` = về Gốc vay; ngược lại id danh mục đang hoạt động có `root=='principal'`. Lỗi: không phải khoản vay; danh mục khác loại/lưu trữ; trùng nhóm hiện tại; thiếu ngày/lý do; ngày sai.
- `category-delete` `{category, reason}`: lỗi nếu đã dùng, có con, là gốc hệ thống hoặc thiếu lý do.

**Thay đổi hành vi**: `classify` chặn `profile` ở Thu nhập/Chuyển nội bộ/Chưa phân loại và mọi hồ sơ người (Chi tiêu gắn khoản vay/BĐS vẫn được); `category-archive` chặn khi còn khoản vay đang gắn.

**`GET` view**: thêm `loan_options`; `categories.nodes[].deletable|loans`; `categories.deleted`.

**`POST /api/classification-review`**: nhóm theo quy tắc mới (R92); thêm `loan` vào dòng khi có đối tượng; không đổi các khóa còn lại.

**`POST /api/category-history`/`category-view`/`category-review`**: số liệu theo danh mục hiệu lực; không đổi khóa.
