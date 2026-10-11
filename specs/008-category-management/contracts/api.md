# Contracts — 008 category-management
Actions qua `POST /api/action`: `category-create {name,description,parent}` · `category-edit {category,name?,description?,parent?,reason?}` · `category-archive {category,reason}` · `category-restore {category}` · `category-root-describe {root,description}`. Lỗi → `ValidationError` tiếng Việt.
`classify`: mỗi phần nhận thêm `node` tùy chọn (id nút ACTIVE cùng gốc với `category`).
`GET /api/state`: thêm `categories` và capability `category-tree`.
`POST /api/category-history {category}` (khóa gốc hoặc id nút) → `{category,path,evidence,source_notice,totals,rows[]}`.
UI: nút "Danh mục" ở sidebar; màn cây với tổng, nút Lịch sử/+ Con/Sửa/Lưu trữ/Khôi phục; hộp thoại phân loại có "Nhóm con"; lịch sử mở được dòng nguồn (`sourceDetail`).
Bất biến kiểm bằng test: tổng gốc = Σ phần phân loại của gốc; tổng cha = Σ cây, mỗi giao dịch một lần; không ghi sự kiện khi đọc; kết quả `report()` và snapshot cũ y hệt.
