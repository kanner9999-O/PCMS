# Quickstart / nghiệm thu 016 (dữ liệu giả, cổng 8801, không 8792)

1. `PYTHONPATH=src:tests python3 -m unittest test_p18_acceptance` và toàn bộ test cũ; `node --check`; `node tests/js/*.test.cjs`.
2. Tạo bộ giả: tài khoản có giao dịch cho Kết (5tr 20/09, 10tr 25/09, thêm 3 giao dịch cũ); hai khoản vay của Kết.
3. UI: phân loại giao dịch → chọn Gốc vay → chọn người Kết → thấy đúng hai khoản "Kết · 20/09/2026 · gốc … · dư …"; tạo khoản thứ ba trong ô chọn; chọn Chi tiêu → ô đối tượng biến mất.
4. Màn Kiểm tra: một nhóm "Gốc vay · Khoản Kết" dù có danh mục con.
5. Công nợ → khoản vay → "Chuyển danh mục" sang Long debt (con của Gốc vay): Danh mục tổng đổi, phải thu không đổi, lịch sử có dòng chuyển.
6. Danh mục: tạo "Thử" → Xóa được; danh mục đã dùng → không có nút Xóa, chỉ Lưu trữ.
7. SHA256 `outputs/p01-user-trial` trước/sau trùng nhau.
