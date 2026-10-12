---
description: "Task list — 017 history-format"
---
# Tasks: Định dạng lịch sử giao dịch chuẩn
**Ràng buộc**: chỉ hiển thị, không đổi số liệu, không đụng `outputs/p01-user-trial`, chỉ `git add` đường dẫn cụ thể.

## Phase 1: Setup
- [x] T001 Baseline `specs/017-history-format/baseline.txt` (unittest + node) và SHA256 `/tmp/pcms-017-data-before.sha256`

## Phase 2: Backend (US1, US2)
- [x] T002 [US1] `src/pcms/categories.py` `category_history`: thêm `label`, `source_count`, `split`, `tx_amount`; sắp mới nhất trước (FR-002/003)
- [x] T003 [US2] `src/pcms/realty.py` `realty_history`: như trên (nhãn "Vốn đã thanh toán/Vốn nhận lại/Chi phí/Hoàn chi phí")
- [x] T004 Test `tests/test_p19_acceptance.py`: thứ tự mới nhất trước, nhãn Hoàn chi tiêu/phần tách, `source_count`, tổng dòng = tóm tắt (danh mục và BĐS), số liệu cũ không đổi

## Phase 3: UI
- [x] T005 [US1][US2] `src/pcms/web/p01.js`/`p01.css`: `stmtRowHtml` chung + CSS ra `p01.css`; màn Kiểm tra dùng chung; `catHistory`, `realtyHistory`, `loanDetail` dùng dòng chuẩn; `tests/js/history_format.test.cjs`

## Phase 4: Nghiệm thu
- [x] T006 Hồi quy đầy đủ + node; dùng thử QA 8801 (desktop, 375px); SHA256
- [x] T007 `outputs/p19-handoff.md`; cập nhật IMPLEMENTATION-STATUS, HANDOFF, ACCEPTANCE, specs/README (hàng 017); PR, merge, restart 8792
