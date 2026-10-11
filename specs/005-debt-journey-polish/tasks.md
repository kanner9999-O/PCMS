---
description: "Task list — 005 debt-journey-polish"
---

# Tasks: Hoàn thiện hành trình công nợ

**Input**: `/specs/005-debt-journey-polish/` (plan.md, spec.md, research.md, data-model.md, contracts/ui-and-state.md, quickstart.md)
**Tests**: có — backend bằng `unittest` (`tests/test_p08_acceptance.py`), cú pháp JS bằng `node --check`, UI do PO dùng thử theo quickstart (constitution V).
**Ràng buộc chung**: không đụng `outputs/p01-user-trial`; Decimal cho tiền; không thêm hành động ghi; UI mới gate theo `view.debts.summary`.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [X] T001 Chạy hồi quy nền trước khi sửa và ghi kết quả vào `specs/005-debt-journey-polish/baseline.txt`: `PYTHONPATH=src:tests python3 -m unittest test_p07_acceptance test_p06_acceptance test_p05_acceptance test_p04_acceptance` và `node --check src/pcms/web/p01.js`
- [X] T002 Lưu SHA256 các file dữ liệu vận hành `outputs/p01-user-trial/**` vào `/tmp/pcms-005-data-before.sha256` (chỉ đọc; đối chiếu ở T020)

## Phase 2: Foundational (chặn mọi user story)

- [X] T003 Thêm `LoanCompletion.completion_blocker(self, s, profile)` trong `src/pcms/loan_completion.py` theo research R3 / data-model: trả `None` nếu khoản đã hoàn tất, gốc ≠ 0 hoặc status ≠ `ACTIVE`; `{'code':'NEEDS_SETUP'}` nếu chưa có `debt_setup`; khi gốc = 0 và `ACTIVE` gọi `closure_preview` với `closing_date` = ngày giao dịch gần nhất của khoản (hoặc `debt_setup.effective_date` nếu chưa có giao dịch), bắt `ValidationError` → `{'code':'BLOCKED','message':<thông điệp lỗi>}`, hợp lệ → `{'code':'READY'}`. Chỉ đọc, không đổi state
- [X] T004 Trong `src/pcms/p01.py` hàm `debt_register` (sau dòng gán `completion_status`): gán `loan['completion_blocker']=self.completion_blocker(s,loan['id'])` cho mỗi khoản; thêm khóa `summary` vào dict trả về: `receivable_total`, `payable_total` (Decimal cộng đúng tập `people[i].receivable/payable`, xuất bằng `S()`), `people` (đếm), `loans_by_status` `{ACTIVE,COMPLETED,NEEDS_REVIEW}`, `needs_setup`, `excluded`, `draft: True` — đúng tên và nghĩa ở `data-model.md`

**Checkpoint**: `GET /api/state` trả `debts.summary` và `completion_blocker`; các khóa cũ nguyên trạng.

## Phase 3: User Story 1 — Báo cáo dòng tiền mở ra là thấy số (P1) 🎯 MVP

**Mục tiêu**: mở báo cáo khi hôm nay ngoài kỳ nguồn thì thấy ngay kỳ có dữ liệu hoặc cảnh báo "chưa có nguồn".
**Kiểm độc lập**: bộ giả nguồn tới 30/09/2026, mở báo cáo ngày 11/10/2026 → ngày mặc định 30/09/2026 kèm dòng giải thích; đổi sang 11/2026 → cảnh báo.

- [X] T005 [US1] Trong `src/pcms/web/p01.js` thêm hàm thuần `defaultReportDate(reports,today)`: nếu `today` thuộc một `source_periods` (so khớp chuỗi ISO, `end` là ngày cuối có nguồn) của bất kỳ `reports[]` thì trả `today`, ngược lại trả `source_end` lớn nhất, không có nguồn thì `today`; trả cả cờ `usedLatestSource`
- [X] T006 [US1] Trong `loanCashReport()` (`src/pcms/web/p01.js`) dùng `defaultReportDate(view.reports,today)` làm giá trị mặc định ô ngày; khi `usedLatestSource` hiện dòng "Đang chọn ngày nguồn mới nhất: DD/MM/YYYY (hôm nay chưa có nguồn)"; không ghi đè giá trị người dùng đã đổi
- [X] T007 [US1] Trong `loanCashReport()` sau khi nhận kết quả: nếu khoảng `[r.start, r.end)` không giao với mọi `source_periods` hiện "Kỳ này chưa có nguồn" + liệt kê các khoảng nguồn đã ghi; giao một phần hiện "Chỉ có nguồn cho một phần kỳ"; giữ nguyên các số báo cáo (FR-011)
- [X] T008 [P] [US1] Kiểm hàm `defaultReportDate` bằng node: tạo `tests/js/default_report_date.test.cjs` nạp hàm (tách bằng cách đọc nguồn `p01.js` và `eval` đoạn hàm, hoặc xuất hàm dưới guard `if(typeof module!=='undefined')`) với 4 ca: hôm nay trong kỳ, hôm nay ngoài kỳ, nhiều tài khoản kỳ khác nhau, không có nguồn; chạy bằng `node tests/js/default_report_date.test.cjs`

## Phase 4: User Story 2 — Tổng quan công nợ ở đầu màn (P1)

**Mục tiêu**: thấy tổng phải thu/phải trả, số người, số khoản theo trạng thái ngay đầu màn Công nợ.
**Kiểm độc lập**: bộ giả 3 người → phải thu 100.000.000, phải trả 0, 3 người, 1 hoàn tất / 2 đang hoạt động.

- [X] T009 [P] [US2] Tạo `tests/test_p08_acceptance.py` (import `seed` từ `test_p07_acceptance`, store tạm bằng `tempfile`): test `summary` — phải thu = 100000000.00 theo định dạng `S()`, phải trả = 0, `people`=3, `loans_by_status`={ACTIVE:2,COMPLETED:1,NEEDS_REVIEW:0}, `needs_setup`=0; tổng bằng cộng các `people[i].receivable/payable`; thêm ca khoản chưa thiết lập được đếm vào `needs_setup` và `excluded`, không cộng vào tổng
- [X] T010 [US2] Trong `src/pcms/web/p01.js` hàm `renderDebts()`: khi `view.debts.summary` tồn tại, chèn khối "Tổng quan" đầu màn (phải thu, phải trả — hai số riêng; số người; số khoản theo trạng thái; số cần thiết lập; nhãn "NHÁP · theo dữ liệu hiện có"; câu "Tổng quan tính trên toàn bộ khoản, không theo bộ lọc"). Dùng `fmt()` đã có, không cộng tiền bằng `Number`. Không có `summary` → hiển thị như cũ
- [X] T011 [US2] Giữ dòng phải thu/phải trả từng người hiện có nguyên vẹn (FR-005) và kiểm bằng test trong `tests/test_p08_acceptance.py` rằng `people[i]` không đổi so với trước thay đổi (so với giá trị kỳ vọng của bộ giả: Bình 100.000.000, An 0, Chi 0)

## Phase 5: User Story 3 — Khoản hết gốc chưa tất toán được thì nói lý do (P2)

**Mục tiêu**: khoản gốc 0 hiện lý do còn thiếu hoặc "đủ điều kiện kiểm tra", bỏ nhãn lặp.
**Kiểm độc lập**: "Chi · hết gốc còn lãi" có `completion_blocker.code=='BLOCKED'` với thông điệp; "An" chỉ một nhãn trạng thái.

- [X] T012 [P] [US3] Trong `tests/test_p08_acceptance.py` thêm test `completion_blocker`: khoản Chi (gốc 0, ACTIVE, bảng kê duyệt không phủ hết) → `BLOCKED` kèm `message` không rỗng; khoản An (đã hoàn tất) → `None`; khoản Bình (gốc ≠ 0) → `None`; khoản chưa thiết lập → `NEEDS_SETUP`; khoản đủ điều kiện (dựng bằng cách tạo bảng kê phủ đủ cho Chi theo mẫu `seed`) → `READY`; gọi `debt_register` hai lần không làm `events` tăng và `completion_status` không đổi
- [X] T013 [US3] Trong `renderDebts()` wrapper (`src/pcms/web/p01.js`, đoạn `renderDebts=function(){...}` dòng ~78) hiển thị theo `l.completion_blocker`: `BLOCKED` → dòng "Chưa thể hoàn tất: {message}" (escape bằng `esc`) + nút "Xem bảng kê lãi" gọi `settlementList(l.id)`; `READY` → "Đủ điều kiện kiểm tra hoàn tất" + nút gọi `completionCheck(l.id)`; `NEEDS_SETUP` → "Cần thiết lập" (nút thiết lập đã có); không tự gọi hành động ghi
- [X] T014 [US3] Cùng wrapper: thay nút `${completionLabels[l.completion_status]} · Hoàn tất / lịch sử` bằng chip nhãn trạng thái + nút "Hoàn tất / lịch sử" (không lặp chữ trạng thái trong nút); giữ `data-completion` để `completionPanel` vẫn hoạt động (research R4)

## Phase 6: User Story 4 — Đi lại giữa tài khoản và công nợ (P3)

**Mục tiêu**: từ tài khoản sang Công nợ và từ khoản về tài khoản trong ≤ 2 thao tác.

- [X] T015 [US4] Trong màn tổng quan tài khoản (`render()` / khối "Tình trạng tài khoản" trong `src/pcms/web/p01.js`) thêm dòng "Khoản vay liên quan: N · Mở Công nợ" khi N>0, N = số khoản (`profile` LOAN) có phân bổ trong giao dịch của tài khoản đó; nút đặt `debtMode=true` rồi `render()` giống `$('#debts').onclick`
- [X] T016 [US4] Trong `loanDetail(id)` (`src/pcms/web/p01.js`) thêm nút "Mở tài khoản" đưa người dùng tới tài khoản chứa giao dịch cấu thành (tài khoản của giao dịch đầu tiên nếu nhiều tài khoản; nêu rõ khi có nhiều), đặt `debtMode=false` và chọn tài khoản đó; nút "Công nợ" ở thanh bên đã có là đường quay lại

## Phase 7: Polish & nghiệm thu

- [X] T017 [P] Chạy `node --check src/pcms/web/p01.js` và `node tests/js/default_report_date.test.cjs`; sửa lỗi cú pháp nếu có
- [X] T018 Chạy `PYTHONPATH=src:tests python3 -m unittest test_p08_acceptance test_p07_acceptance test_p06_acceptance test_p05_acceptance test_p04_acceptance`; so với `baseline.txt` (T001): không ca nào cũ hỏng; báo cáo `loan_cash_report` cho cùng `{date,period}` trên bộ giả y hệt trước/sau (đã có kỳ vọng tháng 09: lãi 2,7 triệu, chi phí 0,2 triệu, chênh 2,5 triệu, thu gốc 200 triệu)
- [X] T019 PO dùng thử UI: khởi động bộ giả mới (`/tmp/pcms-claude-qa`, cổng 8801) theo `quickstart.md` §1 và đi đủ các kịch bản §3 (5 bước); chụp ảnh bằng chứng lưu `outputs/p08-po-review.jpg`; ghi lỗi tìm thấy, sửa rồi kiểm lại
- [X] T020 Đối chiếu SHA256 `outputs/p01-user-trial/**` với `/tmp/pcms-005-data-before.sha256` — phải khớp 100% (SC-005); nếu lệch dừng và báo Thạch
- [X] T021 Viết `outputs/p08-handoff.md` (mã đổi, cách chạy, bằng chứng, giới hạn: chưa kiểm mobile, dữ liệu lớn); cập nhật `IMPLEMENTATION-STATUS.md` (mục P08 ở đầu), `HANDOFF.md`, `README.md`, `ACCEPTANCE.md` (thêm tiêu chí P08 tương ứng SC-001…SC-005), `specs/README.md` (005 → Implemented); không đổi hành vi nghiệp vụ trong `PRODUCT-SPEC.md`
- [X] T022 Báo Thạch trước khi restart cổng 8792; sau khi đồng ý: restart đúng backend, mở UI chính **chỉ đọc**, xác nhận không ghi dữ liệu; commit, merge `main`, push

## Dependencies & thứ tự

- Phase 1 → Phase 2 (T003 trước T004) → các story. US1 độc lập hoàn toàn với Phase 2 (chỉ UI), có thể làm song song với Phase 2.
- US2 cần T004; US3 cần T003+T004; US4 độc lập với backend.
- Trong `src/pcms/web/p01.js` các task [US1] [US2] [US3] [US4] cùng sửa một file → **không** chạy song song; thứ tự đề nghị T005–T008 → T010–T011 → T013–T014 → T015–T016.
- T009, T012 cùng file test → làm tuần tự; T008 [P] file riêng.

## Parallel ví dụ
- T008 (`tests/js/...`) song song với T003/T004 (backend).
- T009 song song với T010 khi T004 xong (khác file).

## Chiến lược triển khai
- **MVP = US1 + US2** (cả hai P1): đủ để Thạch thấy báo cáo có số và tổng quan. US3 rồi US4 thêm sau, mỗi story kiểm độc lập.
- Một coder duy nhất làm tuần tự theo thứ tự trên (constitution VI); PO nghiệm thu ở T019.
