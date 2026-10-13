# Plan 021
**Mã**: `src/pcms/realty.py` (6 hành động; `realty_view` thêm `progress`), `src/pcms/assets.py` (`asset_view` thêm `commitments`, không vào `asset_core`/snapshot), `src/pcms/p01.py` (build P23), `src/pcms/web/p01.js` (panel "Hợp đồng và tiến độ" trong từng BĐS; hộp thoại giá HĐ, đợt, gắn giao dịch; dòng cam kết ở Tổng tài sản), test `tests/test_p23_acceptance.py`.
**Constitution**: Decimal/VND nguyên, không bù trừ, không đổi vốn/giá trị/nợ, bản ghi hủy giữ lại, đọc không ghi.
