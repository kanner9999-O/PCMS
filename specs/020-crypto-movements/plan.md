# Plan 020
**Mã**: `src/pcms/crypto_ledger.py` (hành động `crypto-trade`, `crypto-transfer`, `crypto-movement-void`; hàm `crypto_deltas`; `crypto_view` tính số lượng sổ cái, cảnh báo và đối chiếu), `src/pcms/p01.py` (dispatch đã theo tiền tố `crypto-`; build P22), `src/pcms/web/p01.js` (nút Mua/Bán, Chuyển; mục Giao dịch; dòng số dư ghi "mốc + n giao dịch"; cảnh báo; đối chiếu), test `tests/test_p22_acceptance.py`. Không đổi giá, vốn, tổng tài sản ngoài số lượng.
**Constitution**: Decimal, không float, không quy đổi, đọc không ghi, bản ghi hủy giữ lại.
