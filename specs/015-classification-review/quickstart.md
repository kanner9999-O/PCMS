# Quickstart — kiểm 015 classification-review
1. `PYTHONPATH=src:tests python3 -m unittest test_p17_acceptance test_p16_acceptance … test_p01_acceptance` · `node --check src/pcms/web/p01.js` · `for f in tests/js/*.test.cjs; do node $f; done`
2. Server QA bộ giả cổng 8801 (`/tmp/pcms-check-qa`): 8–10 giao dịch gồm 3 giao dịch cho vay "Kết" (-500tr, +200tr, +300tr cùng ngày), chi tiêu có danh mục con, một giao dịch tách, hoàn chi, vài giao dịch chưa phân loại.
3. PO UI: phân loại các giao dịch ở các thời điểm khác nhau → Kiểm tra phân loại: nhóm vừa phân loại ở trên cùng, nhóm "Gốc vay · Kết" đủ 3 giao dịch vào 500tr/ra 500tr/ròng 0; mọi nhóm mở sẵn; thu gọn/mở tất cả; 24 giờ qua; khoảng ngày (sai bị chặn); Chưa phân loại cuối và nổi bật ở thanh tóm tắt; kiểm khớp ✔; Xem nguồn mở được; quay lại; 375px.
4. SHA256 `outputs/p01-user-trial` trước/sau; PR → merge; restart 8792; mở UI chính chỉ đọc.
