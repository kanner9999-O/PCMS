# Quickstart — kiểm 011 realty
1. `PYTHONPATH=src:tests python3 -m unittest test_p13_acceptance test_p12_acceptance … test_p01_acceptance` · `node --check src/pcms/web/p01.js` · `for f in tests/js/*.test.cjs; do node $f; done`
2. Server QA bộ giả cổng 8801: `PYTHONPATH=src python3 -m pcms serve --p01 --data /tmp/pcms-realty-qa --port 8801`.
3. PO UI: tạo Đất A (nhanh) → phân loại ba khoản chi Đầu tư BĐS 200/150/250 triệu gắn Đất A → màn Bất động sản: vốn 600 triệu, ba dòng, mở dòng nguồn (≤2 thao tác) → thêm giá trị 900 triệu (ngày, nguồn): cạnh vốn, chênh lệch +300 triệu có nhãn → thêm giá trị mới rồi hủy → quay về bản trước → khoản vay + thế chấp (mục đích), thử thế chấp lần hai bị chặn → góp vốn người A 300 triệu, B 200 triệu (bằng chứng), không có % → chi phí gắn BĐS + hoàn chi → BĐS chưa có giao dịch hiện thiếu dữ liệu → 375px.
4. SHA256 `outputs/p01-user-trial` trước/sau; PR → merge; restart 8792; mở UI chính chỉ đọc.
