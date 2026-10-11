# Contracts — 009 classification-ux
`POST /api/action` `{action:'classify', data:{ids, parts, reason?}}` — `reason` tùy chọn. `begin-adjustment {account, reason?}` — `reason` tùy chọn. `approve` không đổi (lý do bắt buộc khi có bản duyệt trước).
`object-quick-create`:
- `{kind:'LOAN', party:<id người>|party_name:<tên mới>, name?:<tên khoản>}`
- `{kind:'PROPERTY', name}`
- `{kind:'CATEGORY', parent:<khóa gốc|id danh mục>, name}`
Lỗi nghiệp vụ → `ValidationError` tiếng Việt (tên trùng, tên rỗng/quá dài, người không tồn tại, gốc/danh mục cha không hợp lệ). Thành công trả `view` mới; UI tìm đối tượng mới (profile cuối cùng / nút danh mục theo tên và cha).
`GET /api/state`: `capabilities` thêm `quick-object`.
UI: sắp xếp (`Ngày`, `Số tiền nhỏ → lớn`, `Số tiền lớn → nhỏ`) cạnh ô tìm kiếm; ô lý do không còn bắt buộc; mỗi dòng phần phân loại có nút "+ Tạo nhanh …" theo danh mục.
