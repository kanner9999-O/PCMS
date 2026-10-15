# Plan 029
**Constitution**: VII (đối tượng thuộc danh mục) và VIII (một đối tượng một hồ sơ trong sổ chi tiết; gộp có dấu vết).
**Mã**: `categories.py` (khóa tên chuẩn hóa dùng chung, kiểm duy nhất ở tạo nhanh/thêm đối tượng/đổi tên, `category-object-merge`, `cat_eff` đọc `profile_merges`, view `duplicate_of`), `p01.py` (kiểm duy nhất ở action `profile`; build P31), `legacy_import.py` (migrate theo tên dùng lại hồ sơ bất kỳ loại), `web/p01.js` (cảnh báo, nút Gộp, ẩn hồ sơ bị gộp ở danh sách chọn), test `tests/test_p31_acceptance.py`.
