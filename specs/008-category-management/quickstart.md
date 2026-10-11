# Quickstart — kiểm 008 category-management
1. `PYTHONPATH=src:tests python3 -m unittest test_p10_acceptance test_p09_acceptance test_p08_acceptance test_p07_acceptance test_p06_acceptance test_p05_acceptance test_p04_acceptance test_p03_acceptance test_p02_acceptance test_p01_acceptance` · `node --check src/pcms/web/p01.js`
2. Server QA bộ giả (cổng 8801): `PYTHONPATH=src python3 -m pcms serve --p01 --data /tmp/pcms-cat-qa --port 8801`.
3. PO UI: Danh mục → thêm "Ăn uống" và "Đi lại" dưới Chi tiêu → phân loại giao dịch chi vào "Ăn uống", tách một giao dịch vào hai nhóm → xem Chi tiêu (cha) tổng khớp, mỗi giao dịch một lần → Lịch sử mở dòng nguồn → đổi tên, thử trùng tên/vòng lặp → lưu trữ (cần lý do) → duyệt bản mới rồi đổi tên: snapshot cũ giữ tên cũ → danh mục rỗng hiện thiếu dữ liệu → điện thoại 375px.
4. Đối chiếu SHA256 `outputs/p01-user-trial` trước/sau; restart 8792; mở UI chính chỉ đọc.
