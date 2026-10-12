# Implementation Plan: Định dạng lịch sử giao dịch chuẩn (017)
**Spec**: [spec.md](spec.md) · Branch `017-history-format` · Python stdlib + JS thuần, không đổi tiền/snapshot, không đụng dữ liệu thật.
**Constitution**: chỉ thay hiển thị, đọc không ghi, số liệu không đổi. Đạt.

## Quyết định
- Một hàm JS `stmtRowHtml(row,{warn})` + CSS `.stmt-*` chuyển vào `p01.css` (hiện nằm inline trong màn Kiểm tra); màn Kiểm tra gọi hàm chung.
- Backend `category_history` và `realty_history` thêm `label`, `source_count`, `split`, `tx_amount` cho mỗi dòng; sắp mới nhất trước. Khoản vay dựng dòng phía giao diện từ `entries` (đã có đủ dữ liệu).
- Hàm thuần `historySummaryHtml` cho phần đầu; test node cho nhãn/sắp xếp.

## Tệp chạm tới
`src/pcms/categories.py`, `src/pcms/realty.py`, `src/pcms/p01.py` (build P19), `src/pcms/web/p01.js`, `p01.css`; test `tests/test_p19_acceptance.py`, `tests/js/history_format.test.cjs`.
