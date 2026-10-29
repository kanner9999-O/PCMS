# Review — spec 046: nghiệp vụ Cho vay / Đi vay (QA của người triển khai)

> **Vòng sửa 29/10/2026** theo `docs/po-review-046-2026-10-28.md` (PO chưa nghiệm thu P1, P2): xem **§9**. PO cần nghiệm thu lại; chưa merge, chưa phát hành.
>
> **Đây là QA của Claude, người triển khai, không phải nghiệm thu độc lập.** Codex (PO) chưa nghiệm thu. **Chưa phát hành lên dữ liệu thật.** App thật 8792 vẫn chạy P48. Nhánh `046-loan-business` chỉ được merge và phát hành sau khi có review độc lập.

## 1. Quy trình Spec Kit đã gọi (28/10/2026)

| Lệnh | Kết quả |
|---|---|
| `/speckit-specify` | `spec.md`, `checklists/requirements.md` (16/16). Có bản đồ ảnh hưởng, luồng màn hình, ví dụ số xuyên suốt, Tư vấn kế toán. |
| `/speckit-clarify` | Không có điểm mơ hồ trọng yếu nên không hỏi; kết quả ghi trong spec, mục Clarifications. |
| `/speckit-plan` | `plan.md`, `research.md`, `data-model.md`, `contracts/actions.md`, `quickstart.md`. Constitution check đạt cả trước và sau thiết kế. |
| `/speckit-tasks` | `tasks.md`: 34 task (T000–T033). |
| `/speckit-analyze` | `analysis.md`: 1 CRITICAL (tài liệu lõi phải cập nhật trước), 1 HIGH (gỡ thành viên lọt khỏi bất biến), 4 MEDIUM/LOW. Tất cả đã xử lý trước khi implement; ghi trong mục "Xử lý sau analyze". |
| `/speckit-implement` | Toàn bộ task đã đánh dấu [X]. Không có hook nào (`.specify/extensions.yml` không có). |

## 2. Danh sách thay đổi

**Tài liệu lõi**
- PRODUCT-SPEC: thêm R203–R212.
- R186 được ghi là "thay một phần".
- 12 quy tắc nghiệp vụ theo cặp (R146–R150, R152, R156, R157, R179–R182) ghi "phần vay bị thay thế, phần BĐS vẫn Pending".
- ACCEPTANCE: thêm A64. IMPLEMENTATION-STATUS: thêm P49.

**Module mới `src/pcms/loan_business.py`**
- Nghiệp vụ hiệu lực trên cây danh mục.
- Khoản vay, chi tiết nghiệp vụ có phiên bản và nháp, miễn giảm, hoàn tất.
- Động cơ lãi theo đoạn sự kiện.
- Kiểm nghĩa vụ.
- Sổ `loan_book`.
- Dấu vân tay bất biến.

**`p01.py`**
- `change()` bọc bất biến cho mọi hành động không phải `lb-*`.
- `classify`: phần tiền mới trong danh mục nghiệp vụ chỉ nhận hồ sơ Người.
- `view()` có `loan_book`, capability `loan-business`, build P49.

**`categories.py`**
- `cat_in_use_fast` thêm lý do chặn xóa: đã gắn nghiệp vụ (kể cả đã gỡ) / có khoản vay / có chi tiết nghiệp vụ.
- `category_view`: thêm `business` cho từng nút và `biz_loans` cho từng thành viên.

**`assets.py`**
- Phải thu/Phải trả cộng khoản mới từ cùng sổ.
- Cảnh báo `LOAN_PENDING`.

**`objects.py`**
- `biz_loans` theo hai chiều, `loan_business` trên từng danh mục.
- Người có khoản vay thì không xóa hẳn được.
- Còn gốc/lãi thì không lưu trữ được.

**`server.py`**: endpoint `/api/lb-category-preview`, `/api/lb-detail-preview`, `/api/loan-book`.

**`web/p01.js`**
- Màn Danh mục:
  - nhãn nghiệp vụ, nút Gắn/Gỡ, hộp xem trước;
  - tổng của danh mục nghiệp vụ ghi "Tiền ra / Tiền vào" thay cho "Chi / Hoàn chi".
- Bộ Chi tiết nghiệp vụ: dòng nhập, số còn phải phân bổ, xem trước tác động, nháp / ghi / hủy, + Tạo khoản vay.
- Tự mở bộ Chi tiết nghiệp vụ sau khi phân loại.
- Nhãn trạng thái trên dòng giao dịch.
- Màn Công nợ:
  - thẻ tổng, băng "Chưa đầy đủ", danh sách chờ;
  - lọc theo danh mục, chọn ngày xem;
  - khối theo người, mỗi người hai chiều;
  - sổ chi tiết, miễn giảm, hoàn tất / mở lại, sửa khoản, "Ghi từ giao dịch nguồn";
  - bảng theo danh mục;
  - đầu mục "Khoản vay cũ".
- Màn Đối tượng: hiện hai chiều.
- Tóm tắt tài khoản: dòng "trong đó thuộc nghiệp vụ vay".

**Sửa lỗi có sẵn từ P43 (spec 041), phát hiện khi QA**
- Lỗi: nút "+ Tạo người / khoản vay" trên màn Công nợ gọi hàm `profiles`, mà hàm này đã bị xóa.
- Hậu quả: màn Công nợ văng `ReferenceError` ngay sau khi vẽ, nên các nút phía sau không được gắn sự kiện.
- Lỗi vẫn còn trên `main` và **trên app thật 8792**.
- Đã sửa: nút cũ mở hộp "Khoản vay mới"; khi có nghiệp vụ mới thì ẩn nút này.

**Test**: `tests/test_p49_loan_business.py` (36 test), `tests/js/loan_business.test.cjs`.

## 3. Kết quả đã chạy thật

| Kiểm | Kết quả |
|---|---|
| Toàn bộ suite Python (`unittest discover`) | **483 tests OK** (447 cũ + 36 mới), 100,6 giây |
| `node --test tests/js/` | **10/10 pass** (9 cũ + 1 mới) |
| Bản sao dữ liệu thật: so `view()` giữa P48 và P49 | **Giống hệt** cả 11 nhóm: báo cáo tài khoản, snapshot, Công nợ cũ (`debts`), bảng kê lãi, readiness, BĐS, danh mục (bỏ qua trường mới), kiểm tra phân loại, đối tượng (bỏ qua trường mới), tổng tài sản, `loan_options` |
| Thời gian `view()` trên bản sao thật | P48: 1,26–1,30 giây; P49: 1,26–1,38 giây (đạt mục tiêu ≤ +20%) |
| Xem trước gắn nghiệp vụ trên bản sao thật (chỉ đọc) | Hot Debt và Long Debt: 0 hợp lệ, 0 thiếu, 0 xung đột. Liên kết vay thật đều nằm ở gốc Gốc vay/Lãi vay (khoản cũ). |

**Về TDD, nói thẳng**:
- Test và mã viết cùng một đợt, không phải toàn bộ test đều được viết trước và chạy thất bại trước.
- Lần chạy đầu có 8 ca hỏng. Hai trong số đó là lỗi mã thật:
  - mức lãi bị lưu dạng `2E+2`;
  - liên kết khoản cũ ngoài gốc Gốc vay/Lãi vay bị coi là hợp lệ, trong khi sổ cũ không tính các liên kết này.
- Các ca còn lại là kỳ vọng sai của test hoặc thiếu phần nối dữ liệu.

## 4. QA giao diện của người triển khai (dữ liệu giả, cổng 8810)

| # | Kịch bản (quickstart) | Kết quả |
|---|---|---|
| QA-1 | Gắn Đi vay cho Ngắn hạn, rồi gắn Cho vay cho Hot Debt | Bị chặn và nêu đúng nhánh. Gỡ Ngắn hạn xong thì xem trước: thiếu 7 giao dịch (vào 115.510.000 · ra 112.120.000), xung đột L8 (BĐS), "Nhà QA" không phải Người. Xác nhận xong, Ngắn hạn hiện "kế thừa từ Hot Debt". Danh mục tên "Cho vay" không có nghiệp vụ. |
| QA-2 | Tạo CV-0001 (500, MG Long 200), CV-0002 (600), ĐV-0001 (0) | Mã tự gợi ý đúng. Ô môi giới ẩn với khoản Đi vay. |
| QA-3 | Ghi L1, L2, L3, L4 | L1: xem trước 0 → 100.000.000, lãi ngày đầu 50.000. L4 thử thu gốc 110 triệu → bị chặn "vượt dư gốc 100.000.000", nút Ghi bị khóa. Sửa thành 40 triệu + lãi 150.000 (nút "+ Thêm dòng" tự điền 150.000) → lãi 300.000, thu 150.000, còn thiếu 150.000, môi giới 120.000, "Tất toán một phần". |
| QA-3b | Ghi L5 (môi giới), L7 nháp rồi ghi đủ | Nháp còn thiếu 360.000 → sổ không đổi, trạng thái "Chờ chi tiết · có nháp". Mở lại thì nháp được nạp; thêm 2 dòng lãi → CV-0001 lãi 480.000, đã thu 450.000, còn thiếu 30.000, "Tất toán toàn bộ gốc", môi giới 192.000, đã trả 120.000. CV-0002 lãi 60.000, hoàn tất được. |
| QA-5 | Đường sửa song song trên giao dịch đã ghi | Sửa phân loại L1, chuyển Kết sang Long Debt, gỡ Kết khỏi Hot Debt, gỡ nghiệp vụ Hot Debt: tất cả bị chặn, kèm hướng dẫn. |
| QA-6 | Băng "Chưa đầy đủ" | "3 giao dịch · vào 7.000.000 · ra 2.000.000" (L6 Tươi, L8 BĐS, dòng lịch sử cũ) và nút Mở danh sách chờ. |
| QA-7 | Miễn giảm và hoàn tất | Miễn giảm 30.000 ngày 31/10 → còn thiếu 0 → Hoàn tất (có lý do) → trạng thái Đã hoàn tất. |
| QA-8 | Đồng nhất giữa các màn | Tổng tài sản: Phải thu 3.000.000 (khoản cũ 3.000.000 + khoản mới 0), Phải trả 50.000.000. Khớp với Công nợ, Danh mục (Kết: CV-0001 = 0, CV-0002 = 0; Vay bạn: ĐV-0001 = 50.000.000) và Đối tượng (hai chiều). Tóm tắt tài khoản: thuộc nghiệp vụ vay, vào 167.510.000 · ra 110.120.000. |
| QA-9 | Snapshot, dòng lịch sử cũ, trả vượt | Duyệt sao kê khi còn 3 nguồn chờ → được. Ghi dòng lịch sử cũ của Tươi (giải ngân 2.000.000). Hủy rồi ghi lại → phiên bản POSTED / VOID / POSTED. Snapshot và tổng báo cáo giữ nguyên, không mở phiên điều chỉnh. L6 của Tươi (vào 5.000.000) ghi gốc 2.000.000 + lãi 3.000.000 → bị chặn "vượt lãi tính theo điều khoản 45.000". |

**Lỗi tìm thấy khi QA, đã sửa và test lại:**
1. Danh mục gốc tự tạo (Hot Debt, Vay bạn…) thiếu nhãn và nút nghiệp vụ, vì được vẽ bằng một hàm khác.
2. Xem trước khi bị chặn vẫn ghi "0 giao dịch", dễ hiểu nhầm. Nay ghi rõ là chưa tính.
3. Tổng của danh mục nghiệp vụ ghi "Chi / Hoàn chi / Chi ròng", sai bản chất kế toán. Nay ghi "Tiền ra / Tiền vào".
4. Thứ tự thành phần bị đảo ("Trả phí môi giới" đứng trước "Giải ngân").
5. Cột "Đã trả lãi" ở tiền ra của khoản Cho vay. Nay là "Lãi thực thu/trả".
6. Ngày xem mặc định "hôm nay" giấu phát sinh đã ghi có ngày muộn hơn. Nay mặc định là ngày muộn hơn giữa hôm nay và phát sinh cuối, có ghi "dự tính". Đã có test.
7. Lỗi có sẵn `profiles is not defined` trên màn Công nợ (xem §2).
8. Câu hướng dẫn trong thông báo chặn chỉ sai chỗ có nút Hủy.

## 5. Bộ QA cho PO

- **Địa chỉ**: http://localhost:8809, chạy mã P49 từ worktree `PCMS-wt-046`, chỉ có dữ liệu giả.
- **Thư mục dữ liệu**: `/Users/nerkan/Documents/Working/PCMS-QA/p49-po`.
- **Trạng thái ban đầu** (dựng lại 29/10, build `P49-2026-10-29`): bộ dữ liệu sạch, 10 giao dịch. L1–L8 và E1 đã phân loại danh mục (trước khi gắn nghiệp vụ, tức là "phần tiền cũ"), **chưa** gắn nghiệp vụ và **chưa** có chi tiết. **L9** (31/10, ra 3.000.000, "Ket vay them") để **chưa phân loại**, dùng thử quy tắc người + khoản. Một dòng lịch sử cũ FT900 của Tươi. Chưa có khoản vay nào.
- **Bộ đã dùng cho QA vòng sửa** (giữ để đối chiếu, không dùng cho nghiệm thu): `/Users/nerkan/Documents/Working/PCMS-QA/p49-claude-r1`.
- **Dựng lại**:
  ```bash
  cd /Users/nerkan/Documents/Working/PCMS-wt-046
  PYTHONPATH=src python3 /Users/nerkan/Documents/Working/PCMS-QA/seed_p49.py /Users/nerkan/Documents/Working/PCMS-QA/p49-po
  PYTHONPATH=src python3 -m pcms serve --p01 --data /Users/nerkan/Documents/Working/PCMS-QA/p49-po --port 8809
  ```
- **Kịch bản và số kỳ vọng**: xem `quickstart.md` và bảng ví dụ trong `spec.md`.

## 6. Hướng dẫn ngắn

1. **Danh mục** → chọn danh mục (ví dụ Hot Debt) → **Gắn nghiệp vụ** → chọn Cho vay hoặc Đi vay → xem trước (hợp lệ / thiếu / xung đột) → nhập lý do → Xác nhận. Các danh mục con tự kế thừa.
2. **Công nợ** → **+ Khoản vay mới**: chọn danh mục nghiệp vụ, người (phải là thành viên), tên, mức lãi (đồng/triệu/ngày), môi giới nếu có.
3. Tạo chi tiết nghiệp vụ bằng một trong hai cách:
   - Phân loại giao dịch vào danh mục nghiệp vụ, chọn người **và khoản vay** (bắt buộc; người nhiều khoản thì "+ Tách thêm phần", mỗi phần một khoản) → hộp **Chi tiết nghiệp vụ** tự mở. Đóng hộp thì giao dịch "Chờ chi tiết nghiệp vụ", sổ chưa đổi.
   - Bấm "Chi tiết nghiệp vụ" trên dòng giao dịch, hoặc "Ghi từ giao dịch nguồn" ở khoản vay.

   Trong hộp: chọn khoản, thành phần, số tiền, xem tác động → **Ghi nghiệp vụ**. Chưa đủ thông tin thì **Lưu nháp**; nháp chưa tính vào sổ.
4. **Miễn giảm lãi** hoặc **Hoàn tất** ngay trên dòng khoản vay. Hoàn tất chỉ được khi dư gốc 0, lãi còn thiếu 0 và không còn giao dịch chờ cùng người, cùng chiều.
5. Có băng vàng **Chưa đầy đủ** → **Mở danh sách chờ** để xử lý từng giao dịch.

## 7. Giới hạn còn lại (nêu rõ, chưa làm)

- **Khoản kiểu cũ** (6 hồ sơ "Khoản …" trên dữ liệu thật) vẫn theo luồng cũ: thiết lập, bảng kê lãi, hoàn tất kiểu cũ. Lãi theo ngày kiểu mới không áp cho khoản cũ. Muốn chuyển, người dùng tự Sửa phân loại sang danh mục có nghiệp vụ và ghi chi tiết; không có công cụ chuyển hàng loạt.
- **Không gắn nghiệp vụ được lên gốc hệ thống** (Gốc vay, Lãi vay…), chỉ lên danh mục tự tạo, kể cả danh mục con dưới Gốc vay.
- **Ngoài phạm vi theo brief**: nhập số dư đầu kỳ thủ công, trả trước, hoàn trả tiền thừa, lãi phạt, nhiều môi giới, thu hộ, phân bổ miễn giảm sang môi giới.
- **Trả vượt nghĩa vụ chỉ bị chặn.** Người dùng phải Sửa phân loại phần thừa sang danh mục khác; chưa có thành phần "tiền thừa".
- **Không đổi được mức lãi / môi giới sau khi đã có phát sinh được ghi** (vòng sửa 29/10). Không có lãi suất thay đổi theo ngày hiệu lực; nhập sai thì hủy chi tiết, tạo khoản mới đúng điều khoản và ghi lại.
- **Đổi khoản của một phần tiền đã phân loại** phải qua Sửa phân loại (hộp Chi tiết nghiệp vụ không đổi được khoản đã chọn).
- **Hộp phân loại không có nút tạo khoản tại chỗ**: người chưa có khoản phải tạo ở Công nợ → + Khoản vay mới trước (gợi ý hiện ngay trong hộp).
- **Nhãn phân loại trên dòng giao dịch** vẫn ghi theo loại gốc ("Chi tiêu · 100.000.000"), kèm nhãn trạng thái nghiệp vụ bên cạnh; chưa đổi thành tên danh mục.
- **Chưa kiểm**: giao diện trên điện thoại; dữ liệu lớn (nhiều trăm khoản).
- **README, HANDOFF.md chưa cập nhật.** README đang có thay đổi dở của Thạch trong thư mục vận hành; HANDOFF vẫn ghi P07.
- **Thuế / pháp lý** (thuế thu nhập từ lãi cho vay, trần lãi): cần kế toán viên xác nhận; hệ thống không tính.

## 8. Trạng thái phát hành

- Mã nằm trên nhánh `046-loan-business` (worktree `PCMS-wt-046`).
- **Chưa merge và chưa phát hành.** App thật 8792 vẫn P48; dữ liệu thật không bị chạm. Mọi kiểm tra đều chạy trên bản sao trong scratchpad.
- Sau khi PO nghiệm thu độc lập đạt, mới làm theo quy trình phát hành:
  1. Merge.
  2. Kiểm `main` sạch.
  3. Lấy hash dữ liệu trước.
  4. `merge --ff-only` vào thư mục vận hành.
  5. Khởi động lại 8792.
  6. Lấy hash dữ liệu sau và so.

## 9. Vòng sửa theo PO review 28/10 (29/10/2026)

Nguồn: `docs/po-review-046-2026-10-28.md`. Không mở spec mới; tiếp tục trên worktree `PCMS-wt-046`, nhánh `046-loan-business`. Đây vẫn là QA của người triển khai; **PO chưa nghiệm thu lại**.

### 9.1 Quy trình đã chạy thật
| Bước | Bằng chứng |
|---|---|
| Test hồi quy viết **trước** khi sửa mã: 13 test mới (`ReviewP1RetroactiveTerms` 4, `ReviewP2PersonAndLoanRequired` 9) | `evidence/review-r1-red.txt`: 12/13 đỏ (9 fail, 3 error); 1 test đã xanh sẵn (`test_old_parts_without_loan_stay_visible_and_untouched` — giữ để chống hồi quy) |
| Cập nhật spec (Clarifications 29/10, bổ sung bản đồ ảnh hưởng, luồng màn 2, US2/US3, FR-003/004/005/006, SC-007/008, Tư vấn kế toán), plan, data-model, contracts, tasks (Phase 10, T034–T041); PRODUCT-SPEC R204/R205; ACCEPTANCE A64 | diff của commit vòng sửa |
| `/speckit-analyze` chạy lại bằng bộ lệnh đang cài (`check-prerequisites.sh`; không có hook) | `analysis.md` mục "Chạy lại /speckit-analyze — vòng sửa": 0 CRITICAL, 1 HIGH (bản đồ ảnh hưởng), 2 MEDIUM, 2 LOW; đã xử lý R1–R4 trước khi implement |
| `/speckit-implement` cho Phase 10 (checklist requirements 16/16) | tasks.md T034–T041 [X] |
| Test xanh sau khi sửa | `evidence/review-r1-green.txt` (13/13) |

### 9.2 Cách sửa
**P1 — khóa điều khoản hồi tố**
- `lb_terms_locked(s, loan)`: khoản đã xuất hiện trong dòng của **bất kỳ** phiên bản chi tiết nào (đang ghi, đã bị thay, hay trước bản hủy) hoặc có miễn giảm (kể cả đã hủy) → khóa. Nháp không tính.
- `lb-loan-edit` chặn đổi `rate`, thêm/bỏ môi giới, đổi mức môi giới khi khóa. Tên/biệt danh môi giới, tên, mã, ngày theo dõi, hạn vẫn sửa theo quy tắc cũ (ngày theo dõi vẫn không được sau nguồn đã liên kết).
- Hủy chi tiết hay mở lại khoản **không mở khóa**, vì các phiên bản cũ luôn được giữ. Không thêm tính năng ngày hiệu lực.
- `loan_book.loans[]` thêm `terms_locked`, `terms_lock_reason`. Form "Sửa khoản" khóa ô mức lãi và mức môi giới (khoản chưa có môi giới thì khóa cả tên môi giới), hiện lý do ngay trên form.
- Sửa 2 test cũ coi tính lại lãi lịch sử là đúng:
  - `test_edit_needs_reason_history_and_rate_correction_changes_interest` → `test_edit_needs_reason_history_rate_correctable_only_before_posting`;
  - `test_over_paying_broker_warns_not_blocks` (trước đây sửa mức môi giới sau khi ghi; nay dùng khoản mới có mức thấp đặt từ đầu).

**P2 — phân loại mới phải có người + khoản**
- Phần phân loại có thêm trường `loan`. Hàm kiểm chung `lb_part_check`:
  - danh mục hiệu lực có nghiệp vụ → cần hồ sơ Người và khoản của đúng người đó, đúng chiều, chưa hoàn tất;
  - phần có khoản mà danh mục không mang nghiệp vụ → lỗi.
- Áp ở mọi đường ghi:
  - `classify`: một dòng, hàng loạt, tách phần. Phần giữ y nguyên phần cũ được miễn, để không ép sửa dữ liệu cũ khi chỉ đổi ghi chú.
  - `reclassify_preview`: block `LOAN_BUSINESS`, payload giữ `loan`; với dòng lịch sử cũ, `reclass_apply` lưu `loan`.
  - `legacy_preview` / `legacy-import`: cần Người có sẵn và khoản; lưu `loan` vào lần migrate và từng dòng; `legacy_items` mang `loan`.
- **Lưới an toàn chung**: dấu vân tay có thêm tập phần tiền thô và tập phần vi phạm; `lb_guard` chặn mọi thao tác tạo phần vi phạm **mới**. Gồm phần mới/đổi thiếu người hoặc khoản, và phần đã chọn khoản trở nên lệch người/chiều hay mất nghiệp vụ (đổi cha danh mục, chuyển đối tượng, gỡ nghiệp vụ).
  - Phần y nguyên có từ trước mà trở thành thuộc nghiệp vụ (gắn nghiệp vụ, chuyển nhánh) được giữ và vào danh sách chờ: đây là ngoại lệ lịch sử.
- **Chi tiết nghiệp vụ** nhóm theo (danh mục, người, khoản).
  - Phần đã chọn khoản chỉ nhận dòng của đúng khoản đó; dòng sai khoản bị chặn kèm mã khoản đúng.
  - Phần cũ không có khoản (nhóm null) vẫn chọn được khoản bất kỳ của người đó cùng chiều.
  - Ghi chỉ khi mọi phần đủ; nháp không vào sổ; bản đã ghi giữ nguyên khi đang sửa (không đổi).
- **Giao diện**:
  - ô **Khoản vay** (lọc theo người, chiều, chưa hoàn tất), kèm gợi ý, trong hộp Phân loại (một dòng và hàng loạt), Sửa phân loại, Migrate lịch sử cũ;
  - nút "+ Tách thêm phần" hiện khi đã có danh mục nghiệp vụ;
  - thiếu người hoặc khoản thì không gửi, hộp giữ nguyên;
  - hộp Chi tiết nghiệp vụ ghi "Kết · khoản CV-0001" trên từng phần và ẩn "+ Tạo khoản vay" ở phần đã chọn khoản.
- Mã chờ mới `LOAN_MISMATCH` (khoản đã chọn không còn khớp). Build `P49-2026-10-29`.

### 9.3 Ca kiểm tự động (13 test mới, tests/test_p49_loan_business.py)
| Test | Kiểm |
|---|---|
| `ReviewP1…test_rate_edit_blocked_after_posting_and_history_unchanged` | Tái hiện review: `example(4)`, sửa 500 → 700 bị chặn; ngày 25/10 lãi 300.000, dư lãi 150.000 không đổi; `terms_locked` + lý do |
| `…test_broker_terms_locked_but_name_and_non_financial_fields_editable` | đổi mức, bỏ, thêm môi giới bị chặn; đổi biệt danh, tên, mã, hạn được; quy tắc ngày theo dõi giữ nguyên |
| `…test_edit_allowed_before_any_posting_drafts_do_not_lock` | chỉ có nháp → sửa lãi và môi giới được, có lịch sử |
| `…test_void_and_reopen_do_not_unlock_terms` | hủy hết chi tiết (0 nguồn) vẫn khóa; hoàn tất → mở lại vẫn khóa |
| `ReviewP2…test_no_person_or_no_loan_rejected_and_not_saved` | Tái hiện review: E1 vào Hot Debt không người → chặn; có người, không khoản → chặn; phân loại giữ nguyên, không vào sổ |
| `…test_wrong_loan_rejected` | khoản của người khác, khác chiều, không tồn tại, khoản ở danh mục không nghiệp vụ → chặn |
| `…test_person_and_loan_saves_pending_without_posting` | có người + khoản → lưu, "Chờ chi tiết", sổ không đổi (tương đương đóng/hủy hộp thứ hai), chi tiết chỉ đưa đúng khoản |
| `…test_split_one_transaction_across_two_loans_of_one_person` | một giao dịch 2 phần cho CV-0001/CV-0002; đảo khoản bị chặn; chỉ ghi 1 phần bị chặn; ghi đủ thì sổ đúng |
| `…test_bulk_classification_same_rule` | hàng loạt: thiếu khoản bị chặn; có khoản thì cả hai giao dịch gắn khoản |
| `…test_reclassify_preview_and_commit_require_loan` | Sửa phân loại: xem trước báo chặn khi thiếu khoản; có khoản thì xác nhận được, phần có `loan` |
| `…test_legacy_import_requires_loan_and_links_it` | migrate: người có sẵn thiếu khoản, hoặc người mới → chặn; có khoản thì từng dòng gắn khoản |
| `…test_old_parts_without_loan_stay_visible_and_untouched` | phần cũ thiếu khoản vẫn trong danh sách chờ; lưu lại phân loại y nguyên (chỉ đổi ghi chú) được, không bị sửa |
| `…test_moving_or_clearing_cannot_strand_loan_links` | chuyển nhánh có phần đã gắn khoản sang cha không mang nghiệp vụ → chặn |

Test cũ phải chỉnh vì hành vi mới đúng hơn: `test_pending_reasons` (phần E1 không người nay tạo trước khi gắn nghiệp vụ), `test_pending_in_same_person_direction_blocks_completion` và `test_legacy_link_valid_not_double_and_legacy_row_detail` (thêm khoản khi phân loại / migrate), cùng 2 test P1 ở trên. JS: `loan_business.test.cjs` thêm `lbLineIn`/`lbRemaining` theo khoản và `lbLoansFor`.

### 9.4 Kết quả thực chạy (29/10/2026, worktree)
| Kiểm | Kết quả |
|---|---|
| `PYTHONPATH=src:tests python3 -m unittest discover -s tests` | **496 tests OK** (trước vòng sửa 483) |
| `node tests/js/*.cjs` | **10/10 OK** |
| Bản sao dữ liệu thật trong scratchpad: `view()` P48 (thư mục vận hành, `589f449`) vs P49 vòng sửa | **Giống hệt 13 nhóm**: assets, categories, crypto, debts, interest_statements, loan_options, objects, readiness, realty, reports, snapshots, transactions (tiền và phân loại), trx. Đã xóa bản sao sau khi so |
| Thời gian `view()` trên bản sao | P48 1,27–1,33 giây; P49 1,26–1,27 giây |
| Hash dữ liệu thật trước và sau | `outputs/p01-user-trial` 161 file `a1ec41f0`; `private-data` 30 file `4421df5d`: **không đổi**. Thư mục vận hành chỉ có thay đổi dở của Thạch (không đụng) |

### 9.5 QA giao diện của người triển khai (dữ liệu giả, cổng 8809, bộ `p49-claude-r1`)
Setup qua API của trang: gắn Cho vay cho Hot Debt, tạo CV-0001 (500, môi giới Long 200) và CV-0002 (600) cho Kết. Các bước dưới đây đi trên giao diện.
| # | Thao tác | Kết quả |
|---|---|---|
| R1 | Phân loại L9 vào Hot Debt, chưa chọn người → Lưu | Gợi ý "chọn Người, rồi chọn khoản vay"; thông báo chặn; hộp giữ nguyên; L9 vẫn "Chưa phân loại" |
| R2 | Gọi thẳng API `classify` không người / có người không khoản | Cả hai bị chặn bằng thông báo tiếng Việt; phân loại L9 vẫn rỗng |
| R3 | Chọn Kết → ô Khoản vay hiện CV-0001, CV-0002; tách 2 phần 2.000.000 CV-0001 + 1.000.000 CV-0002 → Lưu | Lưu được; hộp Chi tiết nghiệp vụ tự mở với 2 phần "Kết · khoản CV-0001" / "khoản CV-0002", mỗi phần chỉ có đúng khoản đó |
| R4 | Đóng hộp Chi tiết (hủy) | Sổ không đổi (gốc 0, 0 nguồn); L9 "Chờ chi tiết nghiệp vụ"; danh sách chờ 9 nguồn (gồm các phần cũ L1–L8, FT900) |
| R5 | Ghi L1 vào CV-0001, mở "Sửa khoản CV-0001" | Form hiện lý do khóa; ô mức lãi, mức môi giới chỉ đọc (mờ); gõ 700 không nhận; đổi tên + lý do → lưu được |
| R6 | API `lb-loan-edit` rate 700 / mức môi giới 300 | Bị chặn; lãi CV-0001 ngày 25/10 vẫn 300.000 |
| R7 | Hủy chi tiết L1 rồi thử sửa lãi CV-0001; mở form CV-0002 (chưa ghi) | Vẫn khóa (0 nguồn đang ghi); CV-0002 không khóa, sửa 600 → 650 được |
| R8 | Sửa phân loại E1 → Hot Debt · Kết, chưa chọn khoản → Xem trước | Chặn; chọn CV-0002 → xem trước hiện "Khoản vay: CV-0002", xác nhận → phần E1 gắn CV-0002, "Chờ chi tiết" |
| R9 | Migrate lịch sử cũ vào Hot Debt cho Tươi (chưa có khoản) | Xem trước bị chặn "chọn khoản vay của Tươi… tạo ở Công nợ"; tạo CV-0003 → ô Khoản hiện CV-0003 → ghi; dòng FT901 gắn CV-0003; dòng cũ FT900 vẫn chờ |
| R10 | Phân loại hàng loạt L8 + L6 vào Hot Debt · Kết, không chọn khoản | Ô Khoản vay hiện; Lưu bị chặn; không giao dịch nào đổi |
| — | Console | Không có lỗi JS; các 400/403 là các lần cố ý thử bị chặn |

**Lỗi tìm thấy trong QA vòng này (đã sửa):** mở Migrate với người đã chọn sẵn thì ô Khoản vay không hiện và gợi ý vẫn "chọn Người". Server vẫn chặn đúng; sửa bằng cách đồng bộ ô khoản sau khi điền sẵn người. Các ô bị khóa trong form Sửa khoản trước đó trông như ô thường; đã làm mờ.

**Chưa kiểm trên giao diện** (có test tự động): mở lại khoản đã hoàn tất rồi sửa lãi; chuyển nhánh làm lệch khoản.

### 9.6 Hướng dẫn kiểm độc lập ngắn cho Codex
1. Mở http://localhost:8809 (bộ sạch `p49-po`; dựng lại bằng lệnh ở §5).
2. Danh mục → Hot Debt → Gắn nghiệp vụ Cho vay. Công nợ → + Khoản vay mới: tạo 2 khoản cho Kết.
3. Phân loại **L9** vào Hot Debt: thử thiếu người, thiếu khoản (phải bị chặn, L9 vẫn chưa phân loại); rồi tách 2 phần cho 2 khoản; đóng hộp Chi tiết → kiểm Công nợ không đổi.
4. Ghi chi tiết một giao dịch cũ (ví dụ L1 → CV-0001 Giải ngân) → Sửa khoản: ô lãi bị khóa; thử API như PO review; hủy chi tiết rồi thử lại.
5. Sửa phân loại E1 và Migrate lịch sử vào Hot Debt: phải chọn khoản.
6. Lệnh test: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests python3 -m unittest test_p49_loan_business` (49 test).

### 9.7 File thay đổi trong vòng sửa
- Mã: `src/pcms/loan_business.py`, `src/pcms/p01.py`, `src/pcms/reclassify.py`, `src/pcms/legacy_import.py`, `src/pcms/web/p01.js`.
- Test: `tests/test_p49_loan_business.py`, `tests/js/loan_business.test.cjs`.
- Tài liệu: `specs/046-loan-business/{spec,plan,tasks,analysis,data-model,review,traceability,quickstart}.md`, `contracts/actions.md`, `evidence/review-r1-red.txt`, `evidence/review-r1-green.txt`; `PRODUCT-SPEC.md`, `ACCEPTANCE.md`, `IMPLEMENTATION-STATUS.md`.
- Ngoài repo: `/Users/nerkan/Documents/Working/PCMS-QA/seed_p49.py` (thêm L9).

### 9.8 Trạng thái
Chưa merge, chưa phát hành. PR [kanner9999-O/PCMS#48](https://github.com/kanner9999-O/PCMS/pull/48) cập nhật thêm commit vòng sửa. Chờ PO nghiệm thu lại; không tự đánh dấu PO đã chấp nhận.
