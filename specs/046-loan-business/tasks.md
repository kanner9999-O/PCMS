---
description: "Task list — spec 046 nghiệp vụ Cho vay / Đi vay"
---

# Tasks: Nghiệp vụ Cho vay / Đi vay gắn vào danh mục

**Input**: `specs/046-loan-business/`, gồm plan.md, spec.md, research.md, data-model.md, contracts/actions.md và quickstart.md.

**Tests**: bắt buộc. SC-001 và SC-005 yêu cầu test tự động; Constitution V yêu cầu bằng chứng. Mỗi test viết trước và phải chạy thất bại trước khi viết mã.

## Phase 1: Setup

- [X] T000 Cập nhật tài liệu lõi trước khi sửa mã (Constitution IX.3, analyze C1): PRODUCT-SPEC.md thêm R203–R212, ghi R186 thay một phần và các R cũ bị thay thế; ACCEPTANCE.md thêm A64
- [X] T001 Tạo khung mixin `LoanBusiness` trong src/pcms/loan_business.py (hằng số `DIRECTIONS`, `COMPONENTS`, `COMPONENT_RULES` theo bảng trong data-model.md; hàm `lb_state(s)` dùng setdefault cho `loans`, `loan_details`, `loan_waivers`), rồi thêm mixin này vào `P01Store` trong src/pcms/p01.py
- [X] T002 [P] Tạo file test tests/test_p49_loan_business.py với fixture dữ liệu giả theo bảng ví dụ trong spec: Hot Debt (nhóm chi) › Ngắn hạn, Vay bạn, Kết, Tươi, một BĐS, các giao dịch bước 1–8 đã phân loại, một khoản kiểu cũ ở gốc Gốc vay, một dòng lịch sử cũ trong Hot Debt

## Phase 2: Foundational (chặn mọi story)

- [X] T003 Viết test động cơ lãi trong tests/test_p49_loan_business.py: ví dụ 6 ngày cho 300.000; trả 40 triệu thì từ 26/10 mỗi ngày 30.000; lãi xem ngày 30/10 là 450.000; làm tròn 1.234.567 × 500 × 3 ngày ra 1.852; mức 0 cho lãi 0; giải ngân và trả trong cùng ngày tính 1 ngày
- [X] T004 Cài `lb_accrue(events, rate, as_of)` theo đoạn sự kiện (Decimal prec 80; cơ sở = dư cuối D−1 + giải ngân D; làm tròn tổng lũy kế bằng ROUND_HALF_UP) trong src/pcms/loan_business.py
- [X] T005 Cài `lb_effective(s,key)` (nghiệp vụ hiệu lực, kèm nút nơi gắn), `lb_scope_parts(s)` (nhóm (danh mục, người) → số tiền theo từng nguồn, lấy qua `cat_parts` và `cat_eff`) và `lb_sources(s)` (giao dịch ngân hàng, dòng lịch sử cũ đang hiệu lực) trong src/pcms/loan_business.py
- [X] T006 Cài `lb_fingerprint(s)` và lớp bọc bất biến trong `P01Store.change` (đổi tên phần thân hiện có thành `_change`; với hành động `lb-*` thì gọi `change_loan_business`) trong src/pcms/p01.py và src/pcms/loan_business.py. Dấu vân tay gồm: (1) nhóm của bản đã ghi, (2) nghiệp vụ hiệu lực của nháp, (3) nghiệp vụ hiệu lực của danh mục nơi tạo khoản, (4) quan hệ thành viên ACTIVE của mọi cặp (danh mục, người) có trong bản đã ghi, nháp hoặc khoản (analyze U1)

**Checkpoint**: động cơ lãi và hàm chọn phạm vi đã có test; mọi suite cũ vẫn xanh.

## Phase 3: User Story 1 — Gắn nghiệp vụ vào danh mục (P1) 🎯 MVP

**Independent Test**: kịch bản 1 trong quickstart.

- [X] T007 [US1] Viết test trong tests/test_p49_loan_business.py:
  - kế thừa;
  - con khác cha thì bị chặn;
  - cha có nhánh con khác nghiệp vụ thì bị chặn và nêu đường dẫn;
  - không suy nghiệp vụ từ tên;
  - không gắn được vào gốc hệ thống;
  - xem trước cho các số hợp lệ / thiếu / xung đột / không phải Người;
  - token sai thì bị chặn;
  - gỡ nghiệp vụ bị chặn khi có chi tiết (đã ghi hoặc nháp) hoặc có khoản;
  - đổi cha sang nhánh có nghiệp vụ khác bị chặn khi có chi tiết;
  - xóa hẳn danh mục có nghiệp vụ bị chặn; lưu trữ danh mục nghiệp vụ vẫn giữ và tính chi tiết đã ghi (analyze U2).
- [X] T008 [US1] Cài `lb_category_preview` cùng các hành động `lb-category-set` và `lb-category-clear` (lý do, lịch sử) trong src/pcms/loan_business.py
- [X] T009 [US1] Thêm vào `cat_in_use_fast` lý do chặn "đã gắn nghiệp vụ vay / có khoản vay / có chi tiết nghiệp vụ" kèm gợi ý Lưu trữ; thêm trường `business` cho từng nút trong `category_view` ở src/pcms/categories.py
- [X] T010 [US1] Kiểm tra đổi cha trong `category-edit`: sau khi chuyển, cây phải giữ bất biến "con không khác cha", tức không có nút mang nghiệp vụ riêng khác nghiệp vụ hiệu lực của cha mới. Cài trong src/pcms/categories.py, dùng hàm trong loan_business.py
- [X] T011 [US1] Thêm endpoint `/api/lb-category-preview` trong src/pcms/server.py
- [X] T012 [US1] Giao diện màn Danh mục trong src/pcms/web/p01.js:
  - dòng "Nghiệp vụ" (gắn tại đây / kế thừa từ / chưa gắn);
  - nút Gắn nghiệp vụ, mở hộp xem trước (hợp lệ, thiếu, xung đột, chặn) có ô lý do;
  - nút Gỡ nghiệp vụ.

## Phase 4: User Story 2 — Nhiều khoản vay mỗi người (P1)

- [X] T013 [US2] Viết test trong tests/test_p49_loan_business.py:
  - tạo CV-0001, CV-0002, ĐV-0001 với mã gợi ý; mã trùng thì bị chặn;
  - người phải là thành viên danh mục nghiệp vụ;
  - chiều cố định theo danh mục;
  - môi giới chỉ cho Cho vay;
  - sửa thông tin cần lý do và có lịch sử;
  - ngày theo dõi không được sau ngày nguồn đã liên kết;
  - ~~sửa mức lãi cho ra số lãi mới~~ — thay bởi T037 (vòng sửa 29/10: khóa điều khoản khi đã có phát sinh được ghi).
- [X] T014 [US2] Cài `lb-loan-create`, `lb-loan-edit` và hàm gợi ý mã trong src/pcms/loan_business.py

## Phase 5: User Story 3 — Chi tiết nghiệp vụ (P1)

- [X] T015 [US3] Viết test trong tests/test_p49_loan_business.py:
  - bước 6 (một giao dịch, hai khoản, cả gốc và lãi) ghi được;
  - thiếu tiền thì ghi bị chặn nhưng nháp vẫn lưu được và sổ không đổi;
  - thành phần sai chiều hoặc khoản của người khác thì bị chặn;
  - bản thay thế: sổ giữ bản cũ cho tới khi ghi bản mới; hủy cần lý do;
  - các trạng thái chờ (NO_PERSON, NO_LOAN, NOT_DETAILED, DRAFT);
  - dòng lịch sử cũ ghi được chi tiết;
  - liên kết cũ đúng chiều được tính là hợp lệ, không ghi đôi;
  - các đường song song bị chặn (classify, reclassify, chuyển đối tượng, gộp đối tượng, gỡ thành viên, hủy migrate);
  - phân loại mới vào danh mục nghiệp vụ không nhận hồ sơ LOAN hoặc BĐS.
- [X] T016 [US3] Cài `lb_detail_preview` (nhóm, khoản theo người và chiều, thành phần hợp lệ, số đã phân bổ / còn lại, tác động, các chặn) cùng các hành động `lb-detail-draft`, `lb-detail-post`, `lb-detail-void`, `lb-detail-discard` trong src/pcms/loan_business.py
- [X] T017 [US3] Trong `classify` (src/pcms/p01.py), `reclassify_preview` và `reclass_apply` cho dòng lịch sử cũ (src/pcms/reclassify.py): phần tiền mới trong danh mục có nghiệp vụ chỉ được gắn hồ sơ PERSON
- [X] T018 [US3] Thêm endpoint `/api/lb-detail-preview` trong src/pcms/server.py
- [X] T019 [US3] Giao diện trong src/pcms/web/p01.js:
  - bộ Chi tiết nghiệp vụ dùng chung: dòng nhập, thêm/xóa dòng, + Tạo khoản vay, số còn phải phân bổ, xem trước tác động, Lưu nháp / Ghi / Hủy;
  - tự mở bộ này sau khi phân loại vào danh mục nghiệp vụ;
  - nhãn trạng thái nghiệp vụ trên giao dịch trong lịch sử tài khoản.

## Phase 6: User Story 4 — Lãi, tất toán, miễn giảm, chặn vượt (P1)

- [X] T020 [US4] Viết test trong tests/test_p49_loan_business.py:
  - các bước 1–7 cho đúng từng số trong bảng;
  - thu gốc 110 triệu bị chặn;
  - thu lãi vượt số lãi tính tới ngày thu bị chặn;
  - miễn giảm vượt bị chặn; hủy miễn giảm;
  - hoàn tất bị chặn khi còn lãi; miễn giảm xong thì hoàn tất được;
  - khoản đã hoàn tất không nhận chi tiết mới; mở lại khoản;
  - hủy chi tiết của khoản đã hoàn tất bị chặn;
  - xem trước ghi nhãn PARTIAL / FULL.
- [X] T021 [US4] Cài `lb_check_loan` (kiểm nghĩa vụ theo từng ngày có sự kiện), `lb-waiver-add`, `lb-waiver-cancel`, `lb-loan-complete`, `lb-loan-reopen` trong src/pcms/loan_business.py

## Phase 7: User Story 5 — Môi giới (P2)

- [X] T022 [US5] Viết test trong tests/test_p49_loan_business.py:
  - phần theo điều khoản 120.000 và chênh lệch 180.000; mới thu 150.000 thì hai số này vẫn giữ nguyên;
  - trả môi giới không đổi gốc và lãi đã thu;
  - trả vượt phần theo điều khoản thì cảnh báo, không chặn;
  - Đi vay không nhận môi giới.
- [X] T023 [US5] Thêm các trường môi giới vào sổ (`broker_terms`, `spread_terms`, `broker_paid`, `broker_over`) trong src/pcms/loan_business.py

## Phase 8: User Story 6 — Một sổ, báo cáo, đồng nhất (P1)

- [X] T024 [US6] Viết test trong tests/test_p49_loan_business.py:
  - cùng một số ở Công nợ (loan_book), Tổng tài sản (asset_core), Danh mục (thành viên) và Đối tượng;
  - số đếm người, khoản, giao dịch không đếm đôi;
  - băng "chưa đầy đủ" có số và tổng vào/ra; khoản có `caution`;
  - duyệt sao kê khi còn nguồn chờ vẫn được; snapshot và `report()` không đổi sau khi ghi chi tiết;
  - khoản kiểu cũ giữ nguyên số.
- [X] T025 [US6] Cài `loan_book(s, as_of)` gồm `loans`, `legacy`, `people`, `by_category`, `by_account`, `summary`, `pending`, `sources` trong src/pcms/loan_business.py (`sources` dùng làm danh sách "Ghi từ giao dịch nguồn", lọc theo người/chiều — analyze U3); thêm `loan_book`, capability `loan-business` và build P49 vào `view()` trong src/pcms/p01.py
- [X] T026 [US6] `asset_core` lấy Phải thu/Phải trả từ `loan_book`, gồm cả khoản cũ (src/pcms/assets.py); `object_view` và `category_view` hiện khoản của người theo chiều (src/pcms/objects.py, src/pcms/categories.py); `obj_in_use` tính cả khoản vay
- [X] T027 [US6] Thêm endpoint `/api/loan-book` (chọn ngày xem, lọc danh mục) trong src/pcms/server.py
- [X] T028 [US6] Giao diện màn Công nợ trong src/pcms/web/p01.js và p01.css:
  - tổng theo chiều, số đếm, băng chưa đầy đủ, danh sách chờ;
  - lọc theo danh mục, chọn ngày xem;
  - khối theo người (Cho vay / Đi vay); dòng khoản với các nút (Ghi từ giao dịch nguồn, Miễn giảm, Hoàn tất / Mở lại, Sửa, Sổ chi tiết);
  - nút + Khoản vay mới;
  - giữ khối "Khoản vay cũ";
  - Đối tượng hiện hai chiều;
  - tóm tắt tài khoản có dòng "trong đó thuộc nghiệp vụ vay".

## Phase 9: Polish & Cross-Cutting

- [X] T029 [P] Viết test JS cho các hàm thuần (`lbComponentOptions`, `lbRemaining`) trong tests/js/loan_business.test.cjs
- [X] T030 Cập nhật IMPLEMENTATION-STATUS.md (P49); đối chiếu lại R203–R212/A64 với mã đã làm (phần tài liệu lõi đã làm ở T000)
- [X] T031 Chạy toàn bộ suite cùng node test; kiểm bất biến trên bản sao dữ liệu thật (so P48 với P49) theo quickstart.md; đo thời gian view() P48 vs P49 trên bản sao (analyze G1)
- [X] T032 Viết script seed QA /Users/nerkan/Documents/Working/PCMS-QA/seed_p49.py; dựng 8809; đi qua kịch bản 1–9 trên giao diện
- [X] T033 Viết specs/046-loan-business/traceability.md và review.md (danh sách thay đổi, kết quả test đã chạy, QA, giới hạn, hướng dẫn ngắn)

## Phase 10: Vòng sửa theo PO review 28/10 (29/10/2026)

**Goal**: sửa P1 (khóa điều khoản tài chính hồi tố) và P2 (phân loại mới cần Người + khoản có sẵn) trong một đợt. Nguồn: docs/po-review-046-2026-10-28.md.

- [X] T034 Viết test hồi quy tái hiện P1/P2 (lớp `ReviewP1RetroactiveTerms`, `ReviewP2PersonAndLoanRequired`) trong tests/test_p49_loan_business.py; chạy đỏ và lưu specs/046-loan-business/evidence/review-r1-red.txt
- [X] T035 Cập nhật spec.md (Clarifications 29/10, luồng màn 2, US2/US3, FR-003/004/005/006, Tư vấn kế toán), plan.md, data-model.md, contracts/actions.md, PRODUCT-SPEC.md (R204/R205), ACCEPTANCE.md (A64); chạy lại /speckit-analyze và ghi kết quả vào analysis.md
- [X] T036 [US2] Thêm `lb_terms_locked` và khóa `rate`/môi giới trong `lb-loan-edit`; thêm `terms_locked`, `terms_lock_reason` vào `loan_book.loans[]` trong src/pcms/loan_business.py
- [X] T037 [US2] Sửa test cũ coi tính lại lãi lịch sử là đúng (`test_edit_needs_reason_history_and_rate_correction_changes_interest`, `test_over_paying_broker_warns_not_blocks`) trong tests/test_p49_loan_business.py
- [X] T038 [US3] Thêm `lb_new_part_issue`, nhóm (danh mục, người, khoản) trong `lb_groups`/`lb_status`/`lb_detail_preview`/`loan_book`/`lb_fingerprint`, bất biến phần tiền lỗi mới trong `lb_guard` (src/pcms/loan_business.py)
- [X] T039 [US3] Áp kiểm ở `classify` (src/pcms/p01.py), `reclassify_preview`/`reclass_apply` (src/pcms/reclassify.py), `legacy_preview`/`legacy-import`/`legacy_items` (src/pcms/legacy_import.py)
- [X] T040 [US3] Giao diện: ô Khoản vay trong Phân loại (một dòng, hàng loạt, tách phần), Sửa phân loại, Migrate lịch sử cũ; khóa ô điều khoản trong Sửa thông tin khoản (src/pcms/web/p01.js); test JS hàm lọc khoản (tests/js/loan_business.test.cjs)
- [X] T041 Chạy toàn bộ suite + node; so P48/P49 trên bản sao dữ liệu thật; cập nhật seed QA và QA giao diện trên dữ liệu giả; cập nhật review.md, traceability.md, IMPLEMENTATION-STATUS.md

## Dependencies & Execution Order

- Setup (T001–T002) → Foundational (T003–T006) → US1 → US2 → US3 → US4 → US5 → US6 → Polish.
- US3 cần US1 (danh mục có nghiệp vụ) và US2 (khoản vay).
- US4 và US5 dùng động cơ của T004 và chi tiết của US3.
- US6 gom kết quả của tất cả.
- Giao diện (T012, T019, T028) làm sau phần backend của từng story. Các task này cùng sửa p01.js nên chạy tuần tự.

## Parallel Opportunities

- T002 song song với T001.
- T029 song song với T030.
- Các task khác đều đụng chung `loan_business.py` hoặc `p01.js`, nên chạy tuần tự.

## Implementation Strategy

- **MVP**: Phase 1–3 (gắn nghiệp vụ và kế thừa). Tuy vậy, sẽ chỉ phát hành trọn gói (Constitution IX) sau khi có review độc lập.
- Làm tăng dần theo từng story; sau mỗi phase chạy test của phase đó cộng toàn bộ suite.
