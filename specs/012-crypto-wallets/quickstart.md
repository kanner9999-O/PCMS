# Quickstart — kiểm 012 crypto-wallets
1. `PYTHONPATH=src:tests python3 -m unittest test_p14_acceptance test_p13_acceptance … test_p01_acceptance` · `node --check src/pcms/web/p01.js` · `for f in tests/js/*.test.cjs; do node $f; done`
2. Server QA bộ giả cổng 8801: `PYTHONPATH=src python3 -m pcms serve --p01 --data /tmp/pcms-crypto-qa --port 8801`.
3. PO UI: tạo Ví lạnh 1 (ví riêng), Binance, BingX (sàn) → xác nhận BTC 0,5 → 0,6 → hủy bản mới (quay về 0,5) → BingX BTC giữ 0,2, ký quỹ 0,1, vị thế 5, nợ margin 0,05 (vị thế/nợ ở khu riêng) → USDT TRC20 và ERC20 tách riêng → giá BTC 60.000, ETH 2.500, XYZ chưa giá → tổng 55.000, tỷ trọng 54,55%/45,45%, XYZ ở "chưa có giá" → vốn BTC 25.000 → chênh lệch +5.000 có nhãn, ETH chưa vốn → "chưa xác định" → 375px.
4. SHA256 `outputs/p01-user-trial` trước/sau; PR → merge; restart 8792; mở UI chính chỉ đọc.
