# Tasks: Chặn xóa hẳn danh mục còn dữ liệu ngoài giao dịch ngân hàng

**Input**: `specs/044-category-delete-guard/` (spec, plan, research, data-model, contracts, quickstart)
**Tests**: bắt buộc (SC-001, SC-003; Constitution V).

## Phase 1: Setup

- [x] T001 Ghi R201 vào PRODUCT-SPEC.md và A62 vào ACCEPTANCE.md (Constitution, quy trình bước 1)

## Phase 2: Foundational

- [x] T002 Thêm khung test `tests/test_p47_category_delete.py` kế thừa fixture P18 (tài khoản, giao dịch giả, `nodes()`, `err()`), helper `can_delete(name)` đọc `deletable` từ `/api/state` view và helper thử `category-delete` để đối chiếu màn–lệnh (SC-003)

## Phase 3: User Story 1 — không xóa danh mục còn lịch sử cũ (P1) 🎯 MVP

**Independent test**: nhập lịch sử cũ vào danh mục giả rồi thử xóa.

- [x] T003 [US1] Test: dòng lịch sử cũ ở danh mục (lần migrate ACTIVE) → `deletable=false`, lệnh xóa từ chối với "Còn 1 dòng lịch sử cũ", Lưu trữ vẫn được; tổng không đổi — `tests/test_p47_category_delete.py`
- [x] T004 [US1] Test: lần migrate đã hủy (`legacy-void`) vẫn chặn; dòng đã "Sửa phân loại" sang danh mục khác vẫn chặn danh mục cũ — `tests/test_p47_category_delete.py`
- [x] T005 [US1] Mở rộng `cat_in_use_fast` trong `src/pcms/categories.py`: đếm `legacy_entries` có `category`==id hoặc trong `classification_history[].before/after.category` (mọi lần migrate) → "Còn N dòng lịch sử cũ (kể cả lần migrate đã hủy) thuộc hoặc từng thuộc danh mục này; chỉ có thể lưu trữ."; rồi `legacy_batches[].category` → "Danh mục được ghi trong N lần migrate lịch sử cũ; chỉ có thể lưu trữ." (thứ tự sau kiểm giao dịch ngân hàng, theo research R3)

## Phase 4: User Story 2 — không xóa danh mục còn đối tượng (P1)

**Independent test**: thêm đối tượng vào danh mục giả, thử xóa; gỡ đối tượng, thử lại.

- [x] T006 [US2] Test: thành viên hoạt động → chặn "Còn N đối tượng thành viên"; gỡ hết (`category-object-remove`) → vẫn chặn "từng có đối tượng thành viên"; lịch sử chuyển đối tượng (`object_moves`) → chặn — `tests/test_p47_category_delete.py`
- [x] T007 [US2] Mở rộng `cat_in_use_fast` trong `src/pcms/categories.py`: `category_objects` ACTIVE (đếm) → "Còn N đối tượng thành viên; gỡ hoặc chuyển đối tượng, hoặc lưu trữ danh mục."; `category_objects` khác ACTIVE hoặc `history[].from/to`, `object_moves[].from/to` → "Danh mục từng có đối tượng thành viên (đã gỡ/chuyển); chỉ có thể lưu trữ."

## Phase 5: User Story 3 — danh mục chưa dùng vẫn xóa được (P2)

- [x] T008 [US3] Test: danh mục mới trống `deletable=true`, xóa thành công có bản ghi `category_deleted`; danh mục đã lưu trữ theo cùng quy tắc (trống → xóa được; có lịch sử cũ → chặn); với mọi danh mục trong các test trên `deletable` == (lệnh xóa thành công) — `tests/test_p47_category_delete.py`

## Phase 6: Polish & cross-cutting

- [x] T009 Cập nhật build `P47-2026-10-28` trong `src/pcms/p01.py`; chạy toàn bộ test + `node --test tests/js/`
- [x] T010 Đối chiếu bản sao chỉ đọc dữ liệu thật: `deletable` Property/Hot Debt=false, Bianance/Long Debt=true; tổng danh mục/đối tượng/công nợ/báo cáo giống P46; thời gian `category_view` — ghi vào `specs/044-category-delete-guard/review.md`
- [x] T011 PO nghiệm thu UI trên dữ liệu giả (quickstart 4) — `specs/044-category-delete-guard/review.md`
- [x] T012 IMPLEMENTATION-STATUS.md (P47); README trong thư mục vận hành đang có thay đổi dở của người dùng nên không sửa, HANDOFF.md cũ (P07) ghi là còn lệch; phát hành: PR → merge khi xanh → kiểm `main` sạch → cập nhật thư mục vận hành → khởi động lại `:8792` → hash dữ liệu trước/sau

## Dependencies

T001 → T002 → (T003, T004 → T005) → (T006 → T007) → T008 → T009 → T010 → T011 → T012. US1 và US2 sửa cùng hàm nên làm tuần tự; test viết trước mã (T003/T004 trước T005, T006 trước T007).

## Parallel

Ít cơ hội song song (một file mã, một file test). T010 và T011 có thể chạy song song sau T009.

## Implementation strategy

MVP = US1 (chặn mồ côi lịch sử cũ — rủi ro thật với Property); US2 trong cùng lần phát hành theo nguyên tắc IX (một lần phát hành).
