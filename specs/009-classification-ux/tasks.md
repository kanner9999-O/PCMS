---
description: "Task list — 009 classification-ux"
---

# Tasks: Cải thiện màn Phân loại giao dịch
**Input**: `/specs/009-classification-ux/` · **Tests**: có · Ràng buộc: Decimal/BigInt, không đụng `outputs/p01-user-trial`, **chỉ `git add` đường dẫn cụ thể** (phiên khác đang sửa `docs/product`, `specs/008-product-map`, `README.md`, `specs/README.md`).

## Phase 1: Setup
- [X] T001 Ghi baseline hồi quy vào `specs/009-classification-ux/baseline.txt` (`unittest` P01–P10 + `node --check` + `node tests/js/default_report_date.test.cjs`)
- [X] T002 Lưu SHA256 `outputs/p01-user-trial/**` vào `/tmp/pcms-009-data-before.sha256`

## Phase 2: US1 — Lý do tùy chọn (P1)
- [X] T003 [US1] `src/pcms/p01.py`: bỏ `require` lý do ở `classify` và `begin-adjustment`; lưu `reason=str(d.get('reason','')).strip()[:500]` (rỗng hợp lệ) cho `classification_history` và `adjustment_reason`; thông điệp audit không nối chuỗi rỗng; `approve` giữ nguyên yêu cầu lý do khi có bản duyệt trước
- [X] T004 [US1] `src/pcms/web/p01.js` hộp thoại `classify`: `field('Lý do / căn cứ phân loại (tùy chọn)','reason','text','',false)`; `begin-adjustment` gửi lý do có thể rỗng
- [X] T005 [US1] Test trong `tests/test_p11_acceptance.py`: phân loại không lý do (một và hàng loạt) lưu được và lịch sử `reason==''`; có lý do thì lưu; `begin-adjustment` không lý do mở được; `approve` bản mới không lý do vẫn bị chặn; hồi quy phân loại cũ y hệt

## Phase 3: US2 — Sắp xếp theo số tiền (P1)
- [X] T006 [US2] `src/pcms/web/p01.js`: biến `sortMode` ('date'|'amount_asc'|'amount_desc'), hàm so sánh `compareTx(mode)` một dòng (BigInt trị tuyệt đối; bằng nhau → ngày giảm dần → `order`), áp dụng trong `renderTable()`; select "Sắp xếp" cạnh ô tìm kiếm; đổi chế độ đặt `page=0`, không đổi `filter`/`classificationFilter`/`selected`
- [X] T007 [P] [US2] `tests/js/classification_sort.test.cjs`: trích `compareTx` từ `p01.js` bằng regex một dòng; test: tăng/giảm theo trị tuyệt đối với tiền vào và ra, hòa số tiền giữ ngày giảm dần, số tiền bằng 0, số lớn (> 2^53) so đúng

## Phase 4: US3 — Tạo nhanh đối tượng (P1)
- [X] T008 [US3] `src/pcms/categories.py` `change_quick_object(s,d)` đúng `research.md` R3 và `data-model.md`: LOAN (`party` hoặc `party_name`, `name?` mặc định `Khoản <tên người>` + hậu tố ` (n)` nếu trùng), PROPERTY, CATEGORY (tái dùng `change_category`); tên 1–100, chặn trùng cùng loại (NFC + casefold), `party` phải là PERSON; nguyên tử; không đổi `transactions`/`allocations`; `p01.py`: dispatch `object-quick-create`, capability `quick-object`, build `P11-…`
- [X] T009 [US3] Test trong `tests/test_p11_acceptance.py`: LOAN với người mới tạo đúng 2 hồ sơ và phân loại `principal` dùng được; LOAN với người có sẵn; tên khoản mặc định có hậu tố khi trùng; PROPERTY; CATEGORY dưới `expense` rồi phân loại bằng `node`; trùng tên bị chặn; lỗi ở bước sau (tên khoản vượt 100 ký tự) không để lại người mới (nguyên tử); `transactions`/`snapshots`/`debts` không đổi; khoản vay tạo nhanh hiện "cần thiết lập" (`completion_blocker.code=='NEEDS_SETUP'`); có một mục `audit` cho mỗi lần tạo nhanh; đối tượng vẫn tồn tại dù không có phân loại nào được lưu sau đó
- [X] T010 [US3] `src/pcms/web/p01.js` `splitRow`/`classify`: nút "+ Tạo nhanh …" theo danh mục (khoản vay / BĐS / danh mục con; ẩn với `transfer_pending`, `unknown`), khối inline tạo nhanh (không lồng hộp thoại; Enter không gửi form phân loại), gọi `act('object-quick-create',…)`, dựng lại select đối tượng và danh mục con của dòng và chọn sẵn mục mới; chỉ hiện khi `view.capabilities` có `quick-object`; dùng được cả khi phân loại hàng loạt (một đối tượng gắn cho mọi dòng được chọn) và ở từng phần khi tách giao dịch
- [X] T011 [US3] `p01.js`: đổi danh mục bỏ chọn hồ sơ không còn phù hợp (principal/interest cần LOAN, investment cần PROPERTY), ẩn khối tạo nhanh đang mở, cập nhật nhãn nút

## Phase 5: Polish & nghiệm thu
- [X] T012 `node --check`, `node tests/js/*.test.cjs`, toàn bộ `unittest` P01–P11; so với baseline
- [X] T013 PO dùng thử UI trên `/tmp/pcms-cls-qa` (8801) theo `quickstart.md` §3, desktop và 375px; ghi lỗi, sửa, kiểm lại
- [X] T014 Đối chiếu SHA256 dữ liệu vận hành (T002) phải khớp
- [X] T015 Viết `outputs/p11-handoff.md` (file phải tồn tại trước khi tick); cập nhật `IMPLEMENTATION-STATUS.md`, `HANDOFF.md`, `ACCEPTANCE.md` (P11), `PRODUCT-SPEC.md` (R67–R69 ghi yêu cầu của Thạch), `specs/README.md` (hàng 009) — dùng `git update-index --cacheinfo` cho `specs/README.md` vì có sửa đổi của phiên khác
- [ ] T016 Restart 8792, kiểm chỉ đọc, đối chiếu checksum; commit theo đường dẫn, `git branch -f main`, push

## Dependencies
Phase 1 → US1 → US2 → US3 → Polish. Cùng sửa `p01.js`/`p01.py`/`test_p11_acceptance.py` nên tuần tự (T007 file riêng, song song được).
