---
description: "Task list — 015 classification-review"
---

# Tasks: Màn Kiểm tra phân loại
**Input**: `/specs/015-classification-review/` · **Tests**: có (`tests/test_p17_acceptance.py`) · Ràng buộc: Decimal, chỉ đọc, không đổi snapshot/báo cáo, không đụng `outputs/p01-user-trial`, **chỉ `git add` đường dẫn cụ thể**, quy trình PR.

## Phase 1: Setup
- [x] T001 Baseline hồi quy vào `specs/015-classification-review/baseline.txt` (unittest P01–P16 + `node --check` + `node tests/js/*.test.cjs`)
- [x] T002 SHA256 `outputs/p01-user-trial/**` vào `/tmp/pcms-015-data-before.sha256`

## Phase 2: US1 + US2 + US3 — Backend (P1) 🎯 MVP
- [x] T003 [US1] `src/pcms/categories.py` `classification_review(d,s=None)`: gom nhóm theo R2, dòng theo R3 (kể cả `split`, nhãn hoàn chi, `status`, số liên kết nguồn), nhóm Chưa phân loại riêng; `summary` (tổng giao dịch, đã/chưa phân loại, vào, ra, ròng); `p01.py` build `P17-…`; `server.py` route `/api/classification-review`
- [x] T004 [US2] Phạm vi `all|recent|range` (R5, dùng `cat_period` và hai đầu bao gồm), sắp xếp R4 (nhóm `latest` giảm dần, Chưa phân loại cuối; dòng theo thời điểm phân loại rồi ngày), cờ `recent` (24 giờ) và `scope.cutoff`
- [x] T005 [US3] `checks` và `reconciled` theo R6 (số giao dịch, tiền vào, tiền ra) trong phạm vi
- [x] T006 Test `tests/test_p17_acceptance.py`: ba giao dịch "Kết" (-500tr, +200tr, +300tr) → nhóm "Gốc vay · Kết" 3 dòng, vào 500tr, ra 500tr; Chi tiêu › danh mục con đủ dòng; gốc tự tạo và nhóm nhóm chi có `net_spend`; giao dịch tách hai phần có mặt ở cả hai nhóm với số tiền phần và `split`; hoàn chi nhãn "Hoàn chi tiêu"; Chưa phân loại là nhóm riêng cuối; sắp xếp theo thời điểm phân loại (dùng `classification_history[].at` đặt tay trong bản sao state để kiểm thứ tự xác định); `recent` đúng theo cutoff; `scope=recent` chỉ giao dịch phân loại trong 24 giờ và không có Chưa phân loại; `scope=range` bao gồm hai đầu, ngày sai/`start>end`/`scope` lạ bị chặn; tổng nhóm = Σ dòng, tổng toàn bộ = nguồn, `reconciled`; làm lệch cố ý (bản sao state) → không khớp kèm chênh lệch; đã duyệt → `APPROVED`; tài khoản rỗng → `empty`; tài khoản lạ bị chặn; đọc không tăng số sự kiện

## Phase 3: UI (US1–US3)
- [x] T007 `src/pcms/web/p01.js`: hàm thuần `checkRowLabel(row)` một dòng (nhãn dòng: "Hoàn chi tiêu"/tên nhóm; ghi chú tách phần) và `tests/js/classification_check.test.cjs`; `checkMode` (wrapper `render`, capture-click tắt khi chọn mục khác), nút "Kiểm tra phân loại" trong bước Phân loại (`#bulk` toolbar), "← Quay lại phân loại"
- [x] T008 `renderClassificationCheck()`: thanh tóm tắt (đã phân loại/tổng, chưa phân loại nổi bật, tổng vào/ra/chênh, kiểm khớp), chọn phạm vi (Cả tài khoản mặc định, 24 giờ qua, khoảng ngày + Áp dụng), nhóm `<details open>` kiểu sao kê (ngày+mã / nội dung+Xem nguồn / số tiền ra-vào màu / nhãn + dấu "Mới"), tổng nhóm (chi tiêu: chi, hoàn chi, chi ròng), thu gọn/mở tất cả, tổng toàn bộ cuối trang, `sourceDetail` cho "Xem nguồn"

## Phase 4: Polish & nghiệm thu
- [x] T009 `node --check`, `node tests/js/*.test.cjs`, toàn bộ unittest P01–P17; so với baseline; chứng minh chỉ đọc (số sự kiện không đổi)
- [x] T010 PO dùng thử UI trên `/tmp/pcms-check-qa` (8801) theo `quickstart.md` §3; desktop và 375px; ghi lỗi, sửa, kiểm lại
- [x] T011 Đối chiếu SHA256 (T002) phải khớp
- [x] T012 Viết `outputs/p17-handoff.md` (file phải tồn tại trước khi tick); cập nhật `IMPLEMENTATION-STATUS.md`, `HANDOFF.md`, `ACCEPTANCE.md` (P17), `specs/README.md` (hàng 015) bằng `git update-index --cacheinfo`
- [x] T013 Push nhánh, mở PR vào `main`, merge; `git fetch origin main:main`; restart 8792, kiểm chỉ đọc, đối chiếu checksum

## Dependencies
Phase 1 → 2 → 3 → 4. Cùng sửa `categories.py`/`p01.js`/`test_p17_acceptance.py` nên tuần tự; `tests/js/classification_check.test.cjs` file riêng.
