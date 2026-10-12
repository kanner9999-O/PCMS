---
description: "Task list — 014 category-completion"
---

# Tasks: Hoàn thiện Danh mục
**Input**: `/specs/014-category-completion/` · **Tests**: có (`tests/test_p16_acceptance.py`) · Ràng buộc: Decimal, không đổi snapshot/báo cáo cũ, không đụng `outputs/p01-user-trial`, **chỉ `git add` đường dẫn cụ thể**, quy trình PR.

## Phase 1: Setup
- [X] T001 Baseline hồi quy vào `specs/014-category-completion/baseline.txt` (unittest P01–P15 + `node --check` + `node tests/js/*.test.cjs`)
- [X] T002 SHA256 `outputs/p01-user-trial/**` vào `/tmp/pcms-014-data-before.sha256`

## Phase 2: US1 — Gốc tự tạo theo loại (P1) 🎯 MVP
- [X] T003 [US1] `src/pcms/categories.py`: hằng `ROOT_TYPES={'income','expense','investment'}`; `cat_depth` theo chuỗi tổ tiên (gốc tự tạo = 1); `cat_path` bỏ qua cha `None`; `cat_name_ok` cho gốc (duy nhất trong tên 7 gốc hệ thống ∪ gốc tự tạo, NFC + casefold, tính cả đã lưu trữ); `category-create` không `parent` + `type` bắt buộc ∈ ROOT_TYPES → tạo nút `parent=None`, `root=type`; `category-edit` không đổi cha/loại gốc tự tạo; `category-restore` chấp nhận `parent=None`; `cat_parent_ok` nhận gốc tự tạo ACTIVE làm cha (kế thừa `root`); chuyển nút con sang gốc tự tạo chỉ cùng loại; `cat_keys` bỏ khóa gốc hệ thống khi chuỗi kết thúc ở gốc tự tạo
- [X] T004 [US1] Test `tests/test_p16_acceptance.py`: tạo gốc nhóm chi "Kinh doanh nhỏ"; thiếu loại/loại sai bị chặn; tên "chi tiêu", "CHI TIÊU", "Kinh doanh nhỏ" lần hai, tên trùng gốc đã lưu trữ đều bị chặn; con kế thừa loại, cấp 5 bị chặn; đổi tên ok, đổi loại/cha gốc bị chặn; lưu trữ cần lý do, chặn nếu còn con hoạt động; khôi phục; nhóm chi nhận tiền ra và tiền vào (hoàn chi), nhóm thu chỉ nhận tiền vào, nhóm đầu tư cần hồ sơ BĐS; lưu `category`=loại + `node`; tổng gốc tự tạo riêng và gốc hệ thống cùng loại không bị cộng; `report()` theo loại vẫn gộp; chuyển con giữa gốc hệ thống và gốc tự tạo cùng loại ok, khác loại bị chặn; snapshot đóng băng tên/đường dẫn gốc tự tạo
- [X] T005 [US1] UI `src/pcms/web/p01.js`: nút "+ Gốc mới" (tên + loại), hiển thị gốc tự tạo ngang hàng gốc hệ thống (panel, tổng riêng, + con, sửa tên, lưu trữ/khôi phục, lịch sử), ẩn ô cha khi sửa gốc tự tạo, gốc tự tạo chọn được ở `nodeSelect` theo loại

## Phase 3: US2 — Xem theo kỳ (P1)
- [X] T006 [US2] `categories.py`: helper `cat_period(d)` (ISO, `start<=end`, lỗi tiếng Việt); `category_view(s,start=None,end=None)` lọc `t['date']`, trả `period`; `category_history` nhận `start`/`end`/`account`, trả `period`, `evidence` theo kỳ; `p01.py`/`server.py`: route `POST /api/category-view {start,end}` và build `P16-…`
- [X] T007 [US2] Test: giao dịch tháng 9 và 10 → lọc tháng 9 tổng và `transactions` chỉ tháng 9, lịch sử cùng kỳ và tổng khớp 100% các dòng liệt kê; `start>end`/ngày sai bị chặn; kỳ trống → `evidence` `EMPTY` kèm `source_notice` và UI-state "chưa có giao dịch trong kỳ này"; không bộ lọc → như trước (bằng `view['categories']`); hai đầu kỳ bao gồm; đọc không ghi sự kiện
- [X] T008 [US2] `p01.js`: hàm thuần `catPeriodRange(preset,todayVN)` (tháng này/tháng trước/quý này/quý trước, một dòng) + bộ lọc kỳ (preset + khoảng ngày tùy chọn) trên màn Danh mục gọi `/api/category-view`, hiển thị kỳ đang lọc, "chưa có giao dịch trong kỳ này", truyền kỳ cho lịch sử; `tests/js/category_period.test.cjs`: kiểm tháng/quý, biên năm, quý 4 → quý 1 năm sau

## Phase 4: US3 — Báo cáo duyệt theo danh mục (P1)
- [X] T009 [US3] `categories.py`: `category_review(d,s=None)` đúng `research.md` R5 và `data-model.md`; `server.py`: route `POST /api/category-review {account}`
- [X] T010 [US3] Test: tài khoản 7 giao dịch có giao dịch tách hai danh mục, gốc tự tạo, chưa phân loại → mỗi mục đúng `transactions`/`objects`/`in`/`out`/`net_spend`, cha đếm giao dịch một lần, `checks.*.ok` đều true và `reconciled`; làm lệch cố ý (sửa số tiền một phần phân bổ trên bản sao state) → `ok` false kèm chênh lệch; tài khoản rỗng → trạng thái rỗng; báo cáo gồm toàn bộ giao dịch của tài khoản (không phụ thuộc bộ lọc); chi tiết `category_history(account=…)` chỉ dòng của tài khoản đó; đọc không ghi sự kiện
- [X] T011 [US3] `p01.js`: trong bước xem toàn đợt (nơi gọi `summary(r)`) thêm khối "Theo danh mục" gọi `/api/category-review`: cây lồng, số giao dịch, số đối tượng, vào/ra (Chi tiêu: chi, hoàn chi, chi ròng), khối kiểm đối chiếu khớp/không khớp, nút Chi tiết mở lịch sử (có `account`) và `sourceDetail`

## Phase 5: Polish & nghiệm thu
- [X] T012 `node --check`, `node tests/js/*.test.cjs`, toàn bộ unittest P01–P16; so với baseline; snapshot/báo cáo cũ không đổi (so hash và kết quả trước/sau trên bộ dữ liệu giả)
- [X] T013 PO dùng thử UI trên `/tmp/pcms-cat2-qa` (8801) theo `quickstart.md` §3; desktop và 375px; ghi lỗi, sửa, kiểm lại
- [X] T014 Đối chiếu SHA256 (T002) phải khớp
- [X] T015 Viết `outputs/p16-handoff.md` (file phải tồn tại trước khi tick); cập nhật `IMPLEMENTATION-STATUS.md`, `HANDOFF.md`, `ACCEPTANCE.md` (P16), `specs/README.md` (hàng 014; ghi chú 008 đã hoàn thiện) bằng `git update-index --cacheinfo`
- [ ] T016 Push nhánh, mở PR vào `main`, merge; `git fetch origin main:main`; restart 8792, kiểm chỉ đọc, đối chiếu checksum

## Dependencies
Phase 1 → US1 → US2 → US3 → Polish. Cùng sửa `categories.py`/`p01.js`/`test_p16_acceptance.py` nên tuần tự; `tests/js/category_period.test.cjs` file riêng. MVP = US1 + US3.
