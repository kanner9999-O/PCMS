# Tasks: Tách danh mục lưu trữ và vá dấu vết xóa

**Input**: `specs/045-category-archive-tabs/`
**Tests**: bắt buộc (SC-001…SC-005; Constitution V). Test viết trước mã cho phần backend.

## Phase 1: Setup

- [x] T001 Ghi R202 vào PRODUCT-SPEC.md và A63 vào ACCEPTANCE.md; thêm liên kết "sửa ở spec 045" vào `specs/044-category-delete-guard/review.md` (không sửa nội dung cũ)
- [x] T002 Khung test `tests/test_p48_category_archive.py` kế thừa fixture P18 (helpers tạo danh mục/đối tượng, đọc `categories` view, thử `category-delete` trên bản sao trạng thái, lấy danh sách `cleanup`)

## Phase 2: Foundational

- [x] T003 Đo `view()` trên bản sao chỉ đọc dữ liệu thật bằng mã P47 (mốc so sánh) — ghi vào `review.md`

## Phase 3: US3 — xóa đối tượng không mở khóa xóa danh mục (P1) 🎯 sửa lỗi trước

- [x] T004 [US3] Test: tạo danh mục + đối tượng OBJECT chưa dùng → `object-delete` thành công, `object_deleted[-1].memberships` có danh mục; danh mục `deletable=false`, `category-delete` từ chối, không có trong `cleanup`; lặp lại với `category-object-delete`; lặp lại với gỡ trước (`category-object-remove`) rồi xóa; danh mục chưa từng có đối tượng vẫn xóa được và có trong `cleanup` — `tests/test_p48_category_archive.py`
- [x] T005 [US3] `src/pcms/objects.py`: helper `obj_delete_trace(s,prof)` trả `[{category,status,history}]` của mọi quan hệ của hồ sơ; `object-delete` lưu vào `object_deleted[].memberships` trước khi bỏ quan hệ
- [x] T006 [US3] `src/pcms/categories.py`: `category-object-delete` dùng cùng helper; `cat_in_use_fast` coi danh mục có trong `object_deleted[].memberships` (`category`, `history[].from/from_/to`) là từng có đối tượng thành viên

## Phase 4: US4 — thông báo đúng hành vi (P2)

- [x] T007 [US4] Test: mọi lý do chặn xóa không chứa "gỡ hoặc chuyển"; lý do có số lượng và gợi ý "Lưu trữ để ẩn khỏi danh sách đang sử dụng" với danh mục hoạt động, "Giữ lưu trữ hoặc khôi phục" với danh mục đã lưu trữ; khoản vay đang gắn nêu phải chuyển khoản vay trước — `tests/test_p48_category_archive.py`
- [x] T008 [US4] `src/pcms/categories.py` `cat_in_use_fast`: viết lại thông báo theo `contracts/category-view.md`; `src/pcms/web/p01.js`: mô tả hộp "Xóa hẳn danh mục" và "Dọn danh mục chưa dùng" nêu đúng điều kiện (giao dịch, lịch sử cũ, đối tượng kể cả đã gỡ/xóa, khoản vay)

## Phase 5: US1 — tab Đang sử dụng và ghi chú tổng (P1)

- [x] T009 [US1] Test backend: `archived_share` của gốc/cha = tổng các phần thuộc danh mục lưu trữ bên dưới (giao dịch tách hai phần vào hai danh mục lưu trữ đếm một lần); `totals` không đổi trước/sau lưu trữ và khôi phục; null khi không có; xem theo kỳ (`category_view(start,end)`) cũng đúng (analysis C1) — `tests/test_p48_category_archive.py`
- [x] T010 [US1] `src/pcms/categories.py` `category_view`: tính `archived_share` cho `roots[]` và `nodes[]` trong cùng vòng tính tổng (cả xem theo kỳ)
- [x] T011 [US1] `src/pcms/web/p01.js`: biến `catTab` ('active' mặc định); thanh tab "Đang sử dụng" / "Đã lưu trữ (N)"; tab hoạt động bỏ danh mục lưu trữ khỏi cây, trừ khi còn con hoạt động (vẽ dạng ngữ cảnh "đã lưu trữ", không thao tác); dưới tổng gốc/cha có ghi chú "Gồm X giao dịch · vào/ra … thuộc K danh mục đã lưu trữ — Xem" mở tab lưu trữ; giữ tab qua mọi lần vẽ lại và đổi kỳ

## Phase 6: US2 — tab Đã lưu trữ (P1)

- [x] T012 [US2] Test backend: `delete_block` == lý do của lệnh xóa; `restore_block` khi cha đang lưu trữ; `archived_at`/`archive_reason` từ lần lưu trữ gần nhất, null khi không có; khẳng định không tạo được cha lưu trữ – con hoạt động (lưu trữ cha có con hoạt động, khôi phục con dưới cha lưu trữ, tạo/đổi cha vào danh mục lưu trữ đều bị chặn); danh mục lưu trữ bị từ chối khi phân loại mới/thêm đối tượng/migrate — `tests/test_p48_category_archive.py`
- [x] T013 [US2] `src/pcms/categories.py` `category_view`: `delete_block`, `restore_block`, `archived_at`, `archive_reason` cho `nodes[]`
- [x] T014 [US2] `src/pcms/web/p01.js|css`: tab Đã lưu trữ — ô tìm (lọc tại chỗ, không vẽ lại mất chữ), danh sách phẳng theo đường dẫn, số liệu, thời điểm/lý do (hoặc "không có dữ liệu"), đối tượng (chỉ đọc), Lịch sử, Khôi phục hoặc `restore_block`, Xóa hẳn hoặc `delete_block`; trống thì "Chưa có danh mục nào được lưu trữ"
- [x] T015 [US2] `src/pcms/web/p01.js`: bộ chọn theo cấp `cascChildren` và `levelOptions` cho đi qua danh mục lưu trữ còn con hoạt động (nhãn "đã lưu trữ"), không cho chọn chính nó

## Phase 7: Polish

- [x] T016 Build `P48-2026-10-28` (`src/pcms/p01.py`); toàn bộ test + node
- [x] T017 Bản sao chỉ đọc dữ liệu thật: tổng/Công nợ/báo cáo/Đối tượng/BĐS giống P47; `archived_share` Gốc vay; 3 danh mục lưu trữ; thời gian `view()` — `review.md`
- [x] T018 PO nghiệm thu UI dữ liệu giả (QA bền ở `PCMS-QA`) theo A63 — `review.md`
- [ ] T019 IMPLEMENTATION-STATUS (P48), phát hành (PR → merge khi xanh → kiểm `main` sạch → cập nhật thư mục vận hành → khởi động lại :8792 → hash dữ liệu), cập nhật QA :8807, hướng dẫn sử dụng ngắn

## Dependencies

T001–T003 → US3 (T004→T005→T006) → US4 (T007→T008) → US1 (T009→T010→T011) → US2 (T012→T013→T014→T015) → T016–T019. US4 sau US3 vì cùng sửa `cat_in_use_fast`. Giao diện T011/T014 dùng trường backend T010/T013.

## Parallel

T003 song song với T002. T005 và phần test T007 có thể viết song song (khác file). T017 ∥ T018.

## Implementation strategy

Sửa lỗi dữ liệu (US3) trước, rồi thông báo (US4), rồi tách tab (US1, US2). Một lần phát hành (nguyên tắc IX).
