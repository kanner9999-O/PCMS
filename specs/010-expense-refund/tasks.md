---
description: "Task list — 010 expense-refund"
---

# Tasks: Hoàn chi tiêu
**Input**: `/specs/010-expense-refund/` · **Tests**: có · Ràng buộc: Decimal/BigInt, không đụng `outputs/p01-user-trial`, **chỉ `git add` đường dẫn cụ thể** (phiên khác có file chưa commit), quy trình PR.

## Phase 1: Setup
- [X] T001 Baseline hồi quy vào `specs/010-expense-refund/baseline.txt` (unittest P01–P11 + `node --check` + `node tests/js/*.test.cjs`)
- [X] T002 SHA256 `outputs/p01-user-trial/**` vào `/tmp/pcms-010-data-before.sha256`

## Phase 2: US1 — Phân loại tiền vào là hoàn chi (P1) 🎯 MVP
- [X] T003 [US1] `src/pcms/p01.py` `classify`: đổi điều kiện thành chỉ chặn `category=='income' and signed<0`; giữ thông báo; build `P12-…`
- [X] T004 [US1] Test `tests/test_p12_acceptance.py`: tiền vào gán `expense` lưu được (một dòng, hàng loạt, tách phần); `income` cho tiền ra vẫn bị chặn; `income` cho tiền vào vẫn được; `expense` có `node` (danh mục con) và có `profile` khoản vay hợp lệ; tổng phần bằng tiền nguồn; ví dụ cơm: ra 1.000.000, vào 300.000 ×2 → `report()` `expense_out=1000000`, `expense_in=600000`, `income_in` không có
- [X] T005 [US1] Cập nhật test cũ nếu đang khẳng định "expense cho tiền vào bị chặn" (tìm bằng `Loại thu/chi không khớp chiều tiền` trong `tests/`), ghi chú tham chiếu spec 010

## Phase 3: US2 — Chi / hoàn chi / chi ròng ở mọi nơi (P1)
- [X] T006 [US2] `src/pcms/categories.py`: `totals.net_spend = out − in` (Decimal, có thể âm) cho gốc `expense` và nút có `root=='expense'` trong `category_view`; `category_history` trả `root` và `totals.net_spend` khi root là `expense`
- [X] T007 [US2] Test: ví dụ cơm có danh mục con Ăn uống → gốc Chi tiêu `out=1000000`, `in=600000`, `net_spend=400000`, `transactions=3`; nút Ăn uống tương tự; `net_spend` âm khi hoàn > chi; gốc `income`/khác không có `net_spend`; `income` totals không đổi; đọc không ghi sự kiện
- [X] T008 [US2] `src/pcms/web/p01.js`: hàm `catLabel(category,incoming)` và `spendNet(out,inn)` (BigInt) một dòng mỗi hàm; dùng nhãn "Hoàn chi tiêu" ở bảng giao dịch (`renderTable`), `summary(r)` (đổi nhãn + thêm dòng "Chi ròng"), `showSnapshot`, hộp thoại phân loại (nhãn lựa chọn "Chi tiêu · hoàn chi" khi toàn bộ dòng chọn là tiền vào + ghi chú giải thích; không đổi mặc định)
- [X] T009 [US2] `p01.js` màn Danh mục (`catTotals`) và lịch sử (`catHistory`): nhánh expense hiện "Chi X · Hoàn chi Y · Chi ròng Z VND · N giao dịch" dùng `net_spend`; dòng tiền vào dưới Chi tiêu ghi "Hoàn chi" thay "Vào"; nhánh khác giữ "Vào/Ra/Chênh"
- [X] T010 [P] [US2] `tests/js/expense_refund.test.cjs`: trích `catLabel`, `spendNet` bằng regex một dòng; test nhãn (expense+vào → "Hoàn chi tiêu", expense+ra → "Chi tiêu", income → "Thu nhập"), `spendNet` âm/dương/số lớn > 2^53

## Phase 4: US3 — Thu nhập không tăng, dữ liệu cũ không đổi (P2)
- [X] T011 [US3] Test trong `test_p12_acceptance.py`: snapshot cũ cùng `hash`; `report()` của dữ liệu không dùng hoàn chi y hệt trước (so với bản sao dữ liệu cũ); tiền vào đã là Thu nhập giữ nguyên; phân loại lại sang hoàn chi qua `begin-adjustment` (lý do tùy chọn) rồi `approve` bản mới (lý do bắt buộc) — bản duyệt cũ nguyên vẹn; `loan_cash_report` có `expense_refunds` khi hoàn chi gắn khoản vay

## Phase 5: Polish & nghiệm thu
- [X] T012 `node --check`, `node tests/js/*.test.cjs`, toàn bộ unittest P01–P12; so với baseline
- [X] T013 PO dùng thử UI trên `/tmp/pcms-ref-qa` (8801) theo `quickstart.md` §3; desktop và 375px
- [X] T014 Đối chiếu SHA256 (T002) phải khớp
- [X] T015 Viết `outputs/p12-handoff.md` (file phải tồn tại trước khi tick); cập nhật `IMPLEMENTATION-STATUS.md`, `HANDOFF.md`, `ACCEPTANCE.md` (P12), `PRODUCT-SPEC.md` (R70), `specs/README.md` (hàng 010, dùng `git update-index --cacheinfo`)
- [ ] T016 Push nhánh, **mở PR** vào `main`, merge PR; cập nhật `main` cục bộ không checkout (`git fetch origin main:main`); restart 8792, kiểm chỉ đọc, đối chiếu checksum

## Dependencies
Phase 1 → US1 → US2 → US3 → Polish. Cùng sửa `p01.js`/`categories.py`/`test_p12_acceptance.py` nên tuần tự (T010 file riêng).
