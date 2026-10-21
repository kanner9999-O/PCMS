# Tasks: 041 — Tách danh mục và đối tượng; tạm dừng nghiệp vụ; đồng nhất các màn

Tests: bắt buộc (Constitution V). Thứ tự: nền tảng → US1..US5 → hoàn thiện.

## Phase 1: Nền tảng (chặn mọi story)
- [x] T001 `src/pcms/objects.py`: thêm `create_profile(s,name,kind,category=None)` (tên 1–100 ký tự, `require_free_name`, kind ∈ PERSON/PROPERTY/OBJECT, tùy chọn thành viên danh mục) và `disp_name(s,profile_id)` (LOAN → tên người, khác → tên hồ sơ).
- [x] T002 `src/pcms/business.py`: cờ `business_enabled=False` (thuộc tính lớp), `change_business` từ chối `business-set|clear` khi tắt ("Nghiệp vụ tạm dừng, chờ quyết định"), `biz_guard_*` bỏ qua khi tắt, `business_view` trả `{enabled:false}` khi tắt.

## Phase 2: US1 — Ẩn nghiệp vụ (P1)
- [x] T003 [US1] `src/pcms/p01.py` `view()`: `business` chỉ `{enabled:false}` khi tắt; `objects.rows` bỏ `loans`, `business` khi tắt (`objects.py object_view`); `categories.py category_view` không trả `business`, `loans` khi tắt.
- [x] T004 [US1] `src/pcms/web/p01.js`: ẩn khối/nút/chip Nghiệp vụ, nhãn Cho vay/Đi vay, cảnh báo Chi tiêu/Thu nhập, khoản vay ở màn Đối tượng khi `!view.business?.enabled`.

## Phase 3: US2 — Một đường tạo đối tượng (P1)
- [x] T005 [US2] Dùng `create_profile` trong `objects.py object-create`, `categories.py change_quick_object` (PERSON/PROPERTY), `category-object-add` (tên mới, kind OBJECT), `p01.py action 'profile'` (PERSON/PROPERTY), `legacy_import.py` (nhận `type`, mặc định OBJECT).
- [x] T006 [US2] `src/pcms/web/p01.js`+`p01.html`: bỏ nút `#profiles` và hộp `profiles()`; hộp phân loại tạo nhanh đối tượng dùng `object-create` có chọn loại; migrate hỏi loại (gợi ý theo danh mục) và gửi `type`.

## Phase 4: US3 — Tên người (P1)
- [x] T007 [US3] `src/pcms/categories.py`: `classification_review`, `category_history`, `category_view` dùng `disp_name` (không còn "Khoản …").
- [x] T008 [US3] `src/pcms/web/p01.js`: `objectOptions`/`membersOf`/hộp phân loại hiển thị tên người; `loanSelectSync` tự xác định khoản vay khi chỉ có một, hiện ô chọn khi có nhiều.

## Phase 5: US4 — Đồng bộ danh mục và đối tượng (P1)
- [x] T009 [US4] `src/pcms/business.py`: `business_migration_rows`/`change_business_migrate` khi tắt chỉ `ADD_ONLY`/`RETIRE_ONLY` (không gắn loại, bỏ nhánh BĐS); UI đổi nhãn "Đồng bộ danh mục và đối tượng" và hộp xem trước.

## Phase 6: US5 — Kiểm tra đồng nhất (P2)
- [x] T010 [US5] `tests/test_p40_acceptance.py`: kịch bản quickstart 1–5 (nghiệp vụ ẩn, một đường tạo, tên người, phân loại một/nhiều khoản, đồng bộ → Danh mục = Đối tượng; báo cáo/`debt_register`/snapshot không đổi).
- [x] T011 [US5] Sửa `tests/test_p33_acceptance.py` (và lớp kế thừa P34/P39) chạy với `business_enabled=True` trong `setUp`; thêm test cờ tắt.

## Phase 7: Hoàn thiện
- [x] T012 `PRODUCT-SPEC.md` (R185–R190; R146–R153, R156–R157, R179–R182 → Pending), `IMPLEMENTATION-STATUS.md`, `specs/README.md`.
- [x] T013 QA trình duyệt trên bộ giả (quickstart 6), đối chiếu bản sao dữ liệu thật (quickstart 7), chạy toàn bộ test, tăng build.
- [x] T014 PR, merge khi mọi test xanh, khởi động lại server thật.

## Phụ thuộc
T001–T002 → T003–T011 → T012–T014. T004/T006/T008/T009 cùng sửa `p01.js`: làm tuần tự.
