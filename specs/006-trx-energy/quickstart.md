# Quickstart — kiểm 006 trx-energy
1. `PYTHONPATH=src:tests python3 -m unittest test_p09_acceptance test_p08_acceptance test_p07_acceptance test_p06_acceptance test_p05_acceptance test_p04_acceptance` · `node --check src/pcms/web/p01.js`
2. Server QA mới (bộ giả riêng, cổng 8801): `PYTHONPATH=src python3 -m pcms serve --p01 --data /tmp/pcms-trx-qa --port 8801`.
3. PO UI: TRX/Energy → thêm khách → đơn 3 dòng gói tháng 100 USDT (hạn thu cụ thể) → thu 200 USDT phân bổ 2 dòng → còn nợ 100 → thu VND (tỷ giá nhập tay) gắn giao dịch ngân hàng giả → thử gắn lại cùng giao dịch quá số tiền (bị chặn) → báo cáo tháng → void khoản thu → số liệu hoàn lại.
4. Đối chiếu SHA256 `outputs/p01-user-trial` trước/sau; restart 8792; mở UI chính chỉ đọc.
