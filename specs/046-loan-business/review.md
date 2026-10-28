# Review — spec 046: nghiệp vụ Cho vay / Đi vay (QA của người triển khai)

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
- **Trạng thái ban đầu**: bộ dữ liệu sạch. Mọi giao dịch đã phân loại danh mục nhưng **chưa** gắn nghiệp vụ và **chưa** có chi tiết, để PO tự đi từ bước 1.
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
   - Phân loại giao dịch vào danh mục nghiệp vụ và chọn người → hộp **Chi tiết nghiệp vụ** tự mở.
   - Bấm "Chi tiết nghiệp vụ" trên dòng giao dịch, hoặc "Ghi từ giao dịch nguồn" ở khoản vay.

   Trong hộp: chọn khoản, thành phần, số tiền, xem tác động → **Ghi nghiệp vụ**. Chưa đủ thông tin thì **Lưu nháp**; nháp chưa tính vào sổ.
4. **Miễn giảm lãi** hoặc **Hoàn tất** ngay trên dòng khoản vay. Hoàn tất chỉ được khi dư gốc 0, lãi còn thiếu 0 và không còn giao dịch chờ cùng người, cùng chiều.
5. Có băng vàng **Chưa đầy đủ** → **Mở danh sách chờ** để xử lý từng giao dịch.

## 7. Giới hạn còn lại (nêu rõ, chưa làm)

- **Khoản kiểu cũ** (6 hồ sơ "Khoản …" trên dữ liệu thật) vẫn theo luồng cũ: thiết lập, bảng kê lãi, hoàn tất kiểu cũ. Lãi theo ngày kiểu mới không áp cho khoản cũ. Muốn chuyển, người dùng tự Sửa phân loại sang danh mục có nghiệp vụ và ghi chi tiết; không có công cụ chuyển hàng loạt.
- **Không gắn nghiệp vụ được lên gốc hệ thống** (Gốc vay, Lãi vay…), chỉ lên danh mục tự tạo, kể cả danh mục con dưới Gốc vay.
- **Ngoài phạm vi theo brief**: nhập số dư đầu kỳ thủ công, trả trước, hoàn trả tiền thừa, lãi phạt, nhiều môi giới, thu hộ, phân bổ miễn giảm sang môi giới.
- **Trả vượt nghĩa vụ chỉ bị chặn.** Người dùng phải Sửa phân loại phần thừa sang danh mục khác; chưa có thành phần "tiền thừa".
- **Sửa mức lãi** áp cho cả khoản (sửa nhập sai). Không có lãi suất thay đổi theo thời gian.
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
