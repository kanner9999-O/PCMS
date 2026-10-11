---
description: "Task list — 008 category-management"
---

# Tasks: Quản lý danh mục và lịch sử từng danh mục
**Input**: `/specs/008-category-management/` (spec, plan, research, data-model, contracts/api.md, quickstart) · **Tests**: có (`tests/test_p10_acceptance.py`) · Ràng buộc: Decimal, không đụng `outputs/p01-user-trial`, gate UI theo capability `category-tree`, **chỉ `git add` đường dẫn cụ thể** (có phiên khác đang sửa `docs/product`, `specs/008-product-map`, `README.md` trong cùng thư mục).

## Phase 1: Setup
- [X] T001 Ghi baseline hồi quy vào `specs/008-category-management/baseline.txt`: `unittest` P01–P09 + `node --check src/pcms/web/p01.js` + `node tests/js/default_report_date.test.cjs`
- [X] T002 Lưu SHA256 `outputs/p01-user-trial/**` vào `/tmp/pcms-008-data-before.sha256`

## Phase 2: Foundational
- [X] T003 Tạo `src/pcms/categories.py`: hằng `ROOTS` (income→Thu nhập, expense→Chi tiêu, principal→Gốc vay, interest→Lãi vay, investment→Đầu tư BĐS, transfer→Chuyển nội bộ, unknown→Chưa phân loại; `transfer_pending` thuộc `transfer`), mixin `Categories` với hàm rỗng `change_category`, `category_view`, `category_history` (để T004 chạy được; T005/T008 điền nội dung), helper `cat_state(s)` (setdefault `categories`=[] và `category_roots`={}), `norm_name()` (strip + NFC + casefold), `depth()`, `path()`, `descendants()`, `root_of()`
- [X] T004 Trong `src/pcms/p01.py`: thêm `Categories` vào bases `P01Store`; dispatch `category-*` trong `change()`; thêm `'category-tree'` vào capabilities và `'categories': self.category_view(s)` vào `view()`; `build` `P10-…`. Trong `src/pcms/server.py` thêm route `POST /api/category-history` → `store.category_history(data)`

## Phase 3: US1 — Quản lý cây danh mục (P1) 🎯 MVP
**Kiểm độc lập**: tạo "Ăn uống" dưới Chi tiêu, đổi tên, thử tên trùng/vòng lặp/quá 4 cấp (bị chặn), lưu trữ có lý do, khôi phục.
- [X] T005 [US1] `change_category` trong `categories.py` cho `category-create`, `category-edit` (name/description/parent/reason), `category-archive` (lý do bắt buộc, chặn nếu còn con ACTIVE), `category-restore` (cha phải ACTIVE), `category-root-describe` (chỉ mô tả gốc ≤500); ràng buộc đúng `data-model.md`: tên 1–100 sau trim, trùng tên giữa các nút cùng cha (NFC+casefold, tính cả ARCHIVED), vòng lặp, độ sâu ≤4 kể cả gốc (tính cả cây con của nút chuyển), mô tả ≤500, mỗi thay đổi ghi `history` `{at, action, before, after, reason}`, không bao giờ xóa nút
- [X] T006 [US1] Test trong `tests/test_p10_acceptance.py`: tạo/đổi tên/đổi cha; tên trùng (khác hoa thường, cùng cha) bị chặn nhưng khác cha được; tên trùng với nút ARCHIVED bị chặn; vòng lặp (cha = chính nó, cha = hậu duệ); cấp thứ 5 bị chặn và chuyển cây con vượt 4 cấp bị chặn; lưu trữ thiếu lý do/còn con ACTIVE bị chặn; khôi phục; sửa tên gốc bị chặn nhưng mô tả gốc được; lịch sử đầy đủ
- [X] T007 [US1] UI trong `src/pcms/web/p01.html` (nút `Danh mục`) và `src/pcms/web/p01.js`: `catMode` (wrapper `render` như `trxMode`, capture-click tắt khi chọn tài khoản/Công nợ/TRX/Hồ sơ), `renderCategories()` cây thụt lề với nhãn "đã lưu trữ", hộp thoại tạo/sửa/lưu trữ/khôi phục/mô tả gốc (`modal`, `act`, `field`, `esc`)

## Phase 4: US2 — Tổng và lịch sử truy nguyên (P1)
**Kiểm độc lập**: cha có hai con, tổng cha = tổng cây, mỗi giao dịch một lần; mở lịch sử thấy dòng nguồn; danh mục rỗng hiện thiếu dữ liệu.
- [X] T008 [US2] `category_view(s)` và `category_history(d,s=None)` trong `categories.py` theo research R3/R4: tổng `in/out/net/parts/transactions` (Decimal, VND) cho gốc và nút, giao dịch chưa phân loại thuộc gốc `unknown`, `transfer_pending` thuộc `transfer`; lịch sử gồm `transaction,date,account,reference,description,amount,direction,category_path,object,status(DRAFT|APPROVED),node_status,sources`, sắp theo ngày, kèm `evidence` (EMPTY_NO_SOURCE|EMPTY|HAS_DATA) và `source_notice`
- [X] T009 [US2] Test: giao dịch tách hai phần vào hai nhóm con của cùng cha → cha đếm giao dịch một lần, mỗi con nhận phần của mình, tổng gốc = Σ phần; tổng gốc = Σ allocations theo khóa; chưa phân loại vào `unknown`; nút ARCHIVED vẫn tính vào tổng cha; danh mục rỗng `evidence` ≠ HAS_DATA và không có số 0 như đối soát; hoàn tiền (vào dưới Chi tiêu) hiện ở `in` không bù trừ; đọc `view` không ghi sự kiện
- [X] T010 [US2] UI trong `p01.js`: tổng vào/ra/chênh/số giao dịch trên từng dòng cây, nút `Lịch sử` gọi `/api/category-history` rồi hiện danh sách (ngày, tài khoản, nội dung, đối tượng, vào/ra, trạng thái, nút `Xem nguồn` → `sourceDetail`), hiện `source_notice` và nhãn "thiếu dữ liệu" khi rỗng

## Phase 5: US3 — Dùng khi phân loại và đóng băng khi duyệt (P2)
- [X] T011 [US3] Trong `p01.py` `classify`: mỗi phần nhận `node` tùy chọn — kiểm nút tồn tại, ACTIVE, `root == category`; lưu `node` vào allocation **chỉ khi có** (allocation cũ giữ nguyên dạng); test trong `test_p10_acceptance.py`: node sai gốc/ARCHIVED/không tồn tại bị chặn; phân loại hàng loạt 5 dòng chỉ đổi 5 dòng, tiền nguồn không đổi; allocation không dùng node giống hệt trước thay đổi; đổi `category` mà `node` không cùng gốc bị chặn; đổi danh mục của giao dịch đã duyệt vẫn đi qua `begin-adjustment` hiện có (không đổi luồng)
- [X] T012 [US3] UI: hộp thoại phân loại (`classify`/`splitRow` trong `p01.js`) thêm select "Danh mục con" lọc theo `category` đã chọn, tự xóa khi đổi `category`, gửi `node` trong `parts`; chỉ hiện khi `view.capabilities` có `category-tree` và gốc đó có nút ACTIVE
- [X] T013 [US3] Trong `p01.py` `approve`: nếu `state['categories']` không rỗng thêm `category_tree` (id, name, parent, path, status) vào `snap` **trước** khi tính hash; nếu rỗng không thêm khóa (snapshot cũ/không dùng cây giữ nguyên); `showSnapshot` trong `p01.js` hiện tên nhóm con từ `category_tree` của snapshot; test: duyệt, đổi tên nút, snapshot cũ vẫn tên cũ và hash không đổi, snapshot mới tên mới; báo cáo `report()` cho dữ liệu cũ y hệt trước thay đổi

## Phase 6: Polish & nghiệm thu
- [X] T013b Test quy mô trong `tests/test_p10_acceptance.py`: tạo ~2.000 giao dịch giả có phân loại vào cây, `category_view` và `category_history` chạy dưới 3 giây; ghi giới hạn nếu chưa đo 10.000
- [X] T014 `node --check src/pcms/web/p01.js`; chạy toàn bộ `unittest` P01–P10; so với baseline
- [X] T015 PO dùng thử UI trên `/tmp/pcms-cat-qa` (cổng 8801) theo `quickstart.md` §3, desktop và 375px không tràn ngang; ghi lỗi, sửa, kiểm lại
- [X] T016 Đối chiếu SHA256 dữ liệu vận hành (T002) phải khớp
- [X] T017 Viết `outputs/p10-handoff.md` (file phải tồn tại trước khi tick); cập nhật `IMPLEMENTATION-STATUS.md`, `HANDOFF.md`, `ACCEPTANCE.md` (P10), `specs/README.md` (hàng 008 → Implemented) — chỉ `git add` các file của mình
- [X] T018 Restart 8792, kiểm chỉ đọc, đối chiếu checksum; commit theo đường dẫn, merge `main`, push

## Dependencies
Phase 1 → 2 → US1 → US2 → US3 → Polish. Mọi story cùng sửa `categories.py`/`p01.js`/`test_p10_acceptance.py` nên tuần tự. MVP = US1 + US2.
