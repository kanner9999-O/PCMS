# Quickstart — kiểm chứng spec 044

1. Test: `cd tests && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../src python3 -m unittest test_p47_category_delete` — mỗi loại tham chiếu chặn xóa, `deletable` khớp lệnh, danh mục trống vẫn xóa được.
2. Toàn bộ: `python3 -m unittest discover -s . -p "test_*.py"`; `node --test tests/js/`.
3. Bản sao chỉ đọc dữ liệu thật: `deletable` — Property, Hot Debt = false; Bianance, Long Debt = true; tổng danh mục/đối tượng/công nợ/báo cáo giống trước.
4. UI dữ liệu giả: danh mục có lịch sử cũ không có nút "Xóa hẳn"; danh mục trống có và xóa được.
