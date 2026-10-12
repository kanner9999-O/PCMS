---
description: "Task list — 013 asset-overview"
---

# Tasks: Tổng hợp tài sản bản đầu
**Input**: `/specs/013-asset-overview/` · **Tests**: có (`tests/test_p15_acceptance.py`) · Ràng buộc: Decimal, không quy đổi tiền tệ, không đụng `outputs/p01-user-trial`, **chỉ `git add` đường dẫn cụ thể**, quy trình PR.

## Phase 1: Setup
- [X] T001 Baseline hồi quy vào `specs/013-asset-overview/baseline.txt` (unittest P01–P14 + `node --check` + `node tests/js/*.test.cjs`)
- [X] T002 SHA256 `outputs/p01-user-trial/**` vào `/tmp/pcms-013-data-before.sha256`

## Phase 2: Foundational
- [X] T003 Tạo `src/pcms/assets.py`: mixin `AssetOverview` với `asset_state(s)` (setdefault `asset_snapshots`), hàm rỗng `asset_view`, `change_assets`; `src/pcms/p01.py`: thêm mixin, dispatch `assets-*`, `'assets': self.asset_view(s)`, capability `'assets'`, build `P15-…`

## Phase 3: US1 — Tổng theo từng đồng tiền (P1) 🎯 MVP
- [X] T004 [US1] `asset_view`: khối VND (ngân hàng từ `report` tài khoản ACTIVE; phải thu/phải trả từ `debt_register`; BĐS từ `realty_view`) và USDT (crypto từ `crypto_view.totals.value`; phải thu và nhận trước từ `trx_view.totals`), `has_data` từng nhóm, `value=None` khi không có dữ liệu, tổng tài sản/nợ/ròng (Decimal), tỷ trọng 2 chữ số half-up trên tổng tài sản của đồng tiền, nhãn nợ lớn hơn tài sản, `target` từng nhóm, không có khóa hợp nhất
- [X] T005 [US1] Test `tests/test_p15_acceptance.py` (dựng bộ dữ liệu như `quickstart` §2): VND tài sản/nợ/ròng và tỷ trọng đúng; USDT 73.450/100/73.350; nhóm trống → `value=None`, không vào tỷ trọng; không có khóa cộng VND+USDT hay `fx`/`rate`; tài khoản ngân hàng/nơi giữ crypto lưu trữ bị loại; ròng âm có nhãn
- [X] T006 [US1] UI `p01.html` (nút `Tổng tài sản` trước `Công nợ`) và `p01.js`: `assetsMode` (wrapper `render`, capture-click, onclick đặt các mode khác false), `renderAssets()` hai khối VND/USDT (tài sản, nợ, ròng, tỷ trọng, "chưa có dữ liệu", nhãn không quy đổi), nút "Mở" từng nhóm đặt mode màn nguồn

## Phase 4: US2 — Cơ sở tính và cảnh báo (P1)
- [X] T007 [US2] BĐS theo R2 (`VALUE`/`COST`/`NONE`, `by_basis`, danh sách `NONE`), bank `as_of` (max `source_end`) và nhãn "theo dữ liệu nguồn đã ghi", `warnings[]` theo R6 (số lượng + `target`), `realty_basis`
- [X] T008 [US2] Test: BĐS A có giá trị 900 triệu, B chỉ có vốn 200 triệu → tổng BĐS 1.100 triệu, `by_basis` {VALUE 900, COST 200}, B trong cảnh báo `REALTY_COST_BASIS`; BĐS C không giá trị không vốn dương → ngoài tổng, trong `NONE` và cảnh báo `REALTY_NO_VALUE`; giao dịch chưa phân loại → `UNCLASSIFIED`; khoảng thiếu nguồn → `COVERAGE_GAPS`; coin chưa giá → `UNPRICED_COIN`; khoản vay chưa thiết lập → `LOAN_ISSUES` và không vào phải thu/phải trả
- [X] T009 [US2] UI: nhãn cơ sở từng nhóm (ngân hàng "đến ngày …", BĐS "giá trị hiện tại / theo giá gốc, chưa định giá"), tách tổng BĐS theo cơ sở, danh sách cảnh báo với nút mở màn nguồn, danh sách BĐS chưa có giá trị

## Phase 5: US3 — Không tính đôi, không dồn tích (P1)
- [X] T010 [US3] Test: BĐS thế chấp khoản vay 300 triệu → giá trị BĐS không đổi, `payable` gồm khoản vay; BingX có vị thế và nợ margin → tài sản USDT không đổi; khoản cho vay có lãi chưa thu → `receivable` chỉ gốc; `trx` tiền nhận trước vào nợ USDT và không vào doanh thu; thưởng staking không vào tổng

## Phase 6: US4 — Bản chụp (P2)
- [X] T011 [US4] `change_assets`: `assets-snapshot {note?}` lưu `{id,at,note,actor,data,hash}` (hash `digest` bản ghi không hash), không có sửa/xóa; `asset_view.snapshots[]` (mới nhất trước, kèm `delta_vs_previous`) và `delta` (hiện tại so với bản chụp gần nhất) cho `assets/liabilities/net` từng đồng tiền
- [X] T012 [US4] Test: lưu S1; đổi giá trị BĐS → `delta` đúng, S1.data không đổi và hash khớp; lưu S2 → `delta_vs_previous` của S2 so với S1; chưa có bản chụp → `delta=None`; hash đổi nếu sửa data (kiểm bằng tính lại); không có action sửa/xóa (action lạ bị chặn); backup/restore giữ nguyên; bản chụp không đổi các phân hệ khác
- [X] T013 [US4] UI: ô ghi chú + nút "Lưu bản chụp", danh sách bản chụp (ngày giờ giờ Việt Nam, ghi chú, tổng, chênh lệch so với bản trước), chênh lệch hiện tại so với lần chụp gần nhất, xem chi tiết bản chụp trong hộp thoại

## Phase 7: Polish & nghiệm thu
- [X] T014 `node --check`, `node tests/js/*.test.cjs`, toàn bộ unittest P01–P15; so với baseline; bất biến: các phân hệ nguồn không đổi khi mở/lưu bản chụp
- [X] T015 PO dùng thử UI trên `/tmp/pcms-assets-qa` (8801) theo `quickstart.md` §3; desktop và 375px; ghi lỗi, sửa, kiểm lại
- [X] T016 Đối chiếu SHA256 (T002) phải khớp
- [X] T017 Viết `outputs/p15-handoff.md` (file phải tồn tại trước khi tick); cập nhật `IMPLEMENTATION-STATUS.md`, `HANDOFF.md`, `ACCEPTANCE.md` (P15), `specs/README.md` (hàng 013) bằng `git update-index --cacheinfo`
- [ ] T018 Push nhánh, mở PR vào `main`, merge; `git fetch origin main:main`; restart 8792, kiểm chỉ đọc, đối chiếu checksum

## Dependencies
Phase 1 → 2 → US1 → US2 → US3 → US4 → Polish. Cùng sửa `assets.py`/`p01.js`/`test_p15_acceptance.py` nên tuần tự. MVP = US1 + US2.
