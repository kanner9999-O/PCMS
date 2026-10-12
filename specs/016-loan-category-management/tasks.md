---
description: "Task list — 016 loan-category-management"
---

# Tasks: Quản lý khoản vay và danh mục
**Input**: `/specs/016-loan-category-management/` · **Tests**: có · Ràng buộc: Decimal, không đổi snapshot/phân bổ cũ, không đụng `outputs/p01-user-trial`, **chỉ `git add` đường dẫn cụ thể**, quy trình PR.

## Phase 1: Setup
- [x] T001 Baseline hồi quy vào `specs/016-loan-category-management/baseline.txt` (unittest + `node --check` + `node tests/js/*.test.cjs`)
- [x] T002 SHA256 `outputs/p01-user-trial/**` vào `/tmp/pcms-016-data-before.sha256`

## Phase 2: Backend (US2–US5)
- [x] T003 [US2] `src/pcms/p01.py`: chặn đối tượng theo loại (FR-003: Thu nhập/Chuyển nội bộ không đối tượng; không gắn hồ sơ người); danh mục con tùy chọn không đổi (FR-004)
- [x] T004 [US4] `src/pcms/categories.py`: `cat_eff`, `cat_parts` dùng danh mục hiệu lực, hành động `loan-regroup` + lịch sử (FR-006/007), chặn lưu trữ khi còn khoản gắn (FR-009)
- [x] T005 [US5] `src/pcms/categories.py`: `category-delete` + `category_deleted`, `deletable`/`loans` trong `category_view` (FR-008)
- [x] T006 [US1] `src/pcms/categories.py` `loan_options` và `p01.py` `view()`/dispatch/build `P18-…` (FR-001/002)
- [x] T007 [US3] `classification_review`: nhóm theo danh mục đỉnh hiệu lực + đối tượng, nhãn dòng = danh mục con (FR-005)
- [x] T008 Test `tests/test_p18_acceptance.py`: hai nhóm Kết gộp một; Chi tiêu có đối tượng bị chặn, Gốc không con lưu được, dữ liệu cũ giữ; chuyển khoản vay (tổng danh mục đúng, dư gốc/phải thu không đổi, lịch sử, snapshot cũ không đổi, giao dịch sau theo nhóm mới, lãi không đổi, về lại Gốc vay, lỗi khác loại/lưu trữ/thiếu lý do/ngày); xóa chưa dùng được và bản ghi xóa, đã dùng/có con/có khoản gắn/gốc hệ thống bị chặn, lưu trữ bị chặn khi còn khoản gắn; `loan_options` nhãn đúng; đọc không đổi số sự kiện

## Phase 3: UI (US1, US4, US5)
- [x] T009 [US1] `src/pcms/web/p01.js`: người → khoản vay, BĐS chỉ BĐS, ẩn ô đối tượng ở loại khác, bỏ chữ loại hồ sơ, tạo nhanh khoản vay theo người đã chọn; hàm thuần `loanLabel` và `tests/js/loan_label.test.cjs`
- [x] T010 [US4][US5] Nút "Chuyển danh mục" + lịch sử trong chi tiết khoản vay; nút "Xóa" ở danh mục chưa dùng; nhãn dòng ở màn Kiểm tra

## Phase 4: Polish & nghiệm thu
- [x] T011 `node --check`, `node tests/js/*.test.cjs`, toàn bộ unittest; so với baseline
- [x] T012 PO dùng thử UI trên `/tmp/pcms-016-qa` (8801) theo `quickstart.md`; desktop và 375px; ghi lỗi, sửa, kiểm lại
- [x] T013 Đối chiếu SHA256 (T002) phải khớp
- [x] T014 Viết `outputs/p18-handoff.md` (file phải tồn tại trước khi tick); cập nhật `IMPLEMENTATION-STATUS.md`, `HANDOFF.md`, `ACCEPTANCE.md`, `specs/README.md` (hàng 016, `git update-index --cacheinfo`)
- [x] T015 Push, PR, merge, `git fetch origin main:main`, restart 8792, kiểm chỉ đọc + checksum

## Dependencies
Phase 1 → 2 → 3 → 4; T004–T007 cùng sửa `categories.py` nên tuần tự.
