# Feature Specification: Nghiệp vụ Cho vay / Đi vay gắn vào danh mục

**Feature Branch**: `046-loan-business`

**Created**: 2026-10-28

**Status**: Draft (quyết định nghiệp vụ đã có trong brief của Thạch 28/10/2026; xem Clarifications)

**Input**: Brief của Thạch ngày 28/10/2026, "Triển khai nghiệp vụ Cho vay/Đi vay trên nền PCMS hiện tại theo các quyết định đã phỏng vấn". Codex đóng vai PO/reviewer độc lập; Claude phân tích kỹ thuật, triển khai và QA. Tham chiếu: Constitution III, IV, VII, VIII, IX; R43, R93, R146–R157, R179–R186, R191, R197–R202; spec 003, 004, 016, 040, 041, 042, 043, 045.

## Clarifications

### Session 2026-10-28 (quyết định trong brief; không hỏi lại)
- Nghiệp vụ chỉ gắn vào **danh mục**, không gắn vào đối tượng và không suy ra từ tên danh mục. Cha có nghiệp vụ thì cả nhánh kế thừa, con không được khác cha. Cha chưa có thì từng nhánh con gắn riêng.
- Một người có nhiều khoản vay. Mỗi khoản có mã, tên, ngày theo dõi, chiều và mức lãi riêng. Khoản vay phải được tạo trước khi liên kết giao dịch. Giải ngân thêm vào khoản cũ hay tạo khoản mới là do người dùng chọn.
- Lãi tính theo **đồng trên 1 triệu gốc mỗi ngày**, mức riêng từng khoản, 0 là không lãi.
  - Tính cả ngày giải ngân và ngày trả gốc.
  - Gốc đã trả làm giảm dư nợ ngay trong ngày trả, nhưng chỉ giảm cơ sở tính lãi từ ngày hôm sau.
- Không có hạn mức, lãi phạt, nhập lãi vào gốc, nhập số dư đầu kỳ thủ công, trả trước, thu hộ, hay nhiều môi giới trên một khoản.
- Môi giới chỉ có ở khoản Cho vay, gồm tên và mức đồng/triệu/ngày, tính theo điều khoản.
  - Không chia tiền lãi thực thu theo tỷ lệ môi giới.
  - Trả môi giới là một giao dịch tiền ra riêng.
- Được chốt sao kê khi nguồn đã khớp, dù chi tiết nghiệp vụ còn dở. Khi đó báo cáo công nợ ghi rõ là chưa đầy đủ.

### Quyết định kỹ thuật–nghiệp vụ do người triển khai chọn (brief cho phép; ghi rõ để PO đối chiếu)
- **Làm tròn**: lãi tính bằng số thập phân chính xác, không làm tròn từng ngày. Chỉ **tổng lãi lũy kế tới ngày xem** được làm tròn về đồng, theo kiểu nửa lên (0,5 → 1).
  - Mọi so sánh nghĩa vụ (trả lãi vượt, miễn giảm vượt) dùng số đã làm tròn này.
  - Phần môi giới theo điều khoản làm tròn cùng cách.
- **Cơ sở tính lãi của ngày D** = dư gốc cuối ngày D−1 + gốc giải ngân trong ngày D. Gốc trả trong ngày D chỉ trừ vào cơ sở từ ngày D+1.
- **Trả vượt nghĩa vụ** bị chặn ngay khi ghi, gồm:
  - thu/trả gốc lớn hơn dư gốc tại ngày đó;
  - lãi đã trả cộng miễn giảm lớn hơn lãi tính tới ngày đó;
  - ghi vào khoản đã hoàn tất.
- Trả môi giới vượt phần theo điều khoản thì **chỉ cảnh báo**, vì đó không phải nghĩa vụ của người vay và brief không chốt việc chặn.
- **Ngày theo dõi**: không liên kết được giao dịch có ngày trước ngày theo dõi. Hạn trả không bắt buộc.

### Kết quả `/speckit-clarify` (28/10/2026)
- Đã quét theo đủ danh mục của bộ lệnh (phạm vi, dữ liệu, luồng, phi chức năng, tích hợp, ngoại lệ, thuật ngữ, tiêu chí hoàn thành). Kết luận: **không có điểm mơ hồ trọng yếu nào cần hỏi Thạch**, nên không đặt câu hỏi.
- Những điểm có thể đổi kết quả tài chính đều đã được chốt:
  - brief đã chốt: quy ước ngày, chặn trả vượt, không bù trừ, cách tính môi giới;
  - brief giao người triển khai chọn và đã ghi ở trên: làm tròn, cơ sở tính lãi trong ngày.
- Còn để ngỏ, không chặn kế hoạch: hiệu năng sổ khi số khoản lớn (dữ liệu thật hiện chỉ 6 khoản) — đo ở bước QA.

## Mô hình *(sau quyết định)*

1. **Danh mục** vẫn là cây tổng hợp tiền vào/ra (Constitution VII). **Nghiệp vụ** là một lớp song song:
   - Một danh mục người dùng tạo có thể mang nghiệp vụ **Cho vay (Phải thu)** hoặc **Đi vay (Phải trả)**.
   - Nghiệp vụ hiệu lực của một danh mục là nghiệp vụ của chính nó, hoặc của danh mục tổ tiên gần nhất có gắn nghiệp vụ.
2. **Người** là đối tượng thành viên của danh mục, như hiện nay. **Khoản vay** là bản ghi thuộc đúng một người. Chiều của khoản cố định khi tạo, theo nghiệp vụ của danh mục nơi tạo khoản.
3. **Chi tiết nghiệp vụ** của một nguồn (giao dịch ngân hàng hoặc dòng lịch sử cũ) chia phần tiền nằm trong danh mục có nghiệp vụ thành các dòng.
   - Mỗi dòng gồm khoản vay, thành phần (gốc / lãi / phí môi giới) và số tiền.
   - Có hai dạng: **nháp** và **bản đã ghi**. Chỉ bản đã ghi được tính vào sổ.
4. **Sổ khoản vay** là một phép tính duy nhất trên các bản đã ghi, dùng cho mọi màn. Sổ cho ra:
   - dư gốc;
   - lãi theo điều khoản, lãi thực thu/trả, miễn giảm, lãi còn thiếu;
   - phần môi giới.
5. Tiền nguồn chỉ có một. Phân loại danh mục quyết định tiền thuộc danh mục nào. Chi tiết nghiệp vụ chỉ giải thích phần tiền đó: không sinh thêm tiền, không đổi sao kê, không đổi snapshot.

## Bản đồ ảnh hưởng *(Constitution IX; lập bằng tìm mã nguồn và đọc bản sao chỉ đọc của dữ liệu thật ngày 28/10/2026)*

**Dữ liệu thật hiện có:**
- 8 danh mục: Long Debt, Hot Debt, Property, Chi tiêu › Chi phí cố định, Chi tiêu › Tín dụng, cùng 3 danh mục đã lưu trữ.
- Hot Debt có thành viên Tươi và Kết.
- 6 hồ sơ khoản vay kiểu cũ. Chỉ Khoản Kết đã thiết lập Phải thu; chưa khoản nào có lãi suất.
- 16 phần phân loại cũ (11 gốc, 5 lãi) nằm ở gốc Gốc vay/Lãi vay và gắn khoản vay.
- 36 dòng lịch sử cũ, đều thuộc Property (BĐS, ngoài phạm vi).
- Chưa có bảng kê lãi. Có 2 snapshot đã duyệt.

**Module backend:**
- `categories.py`: gắn/gỡ nghiệp vụ trên danh mục, kế thừa, đổi cha, lưu trữ, `category_view`.
- `p01.py`:
  - `classify`: chặn phân loại lại nếu làm lệch chi tiết đã ghi; hồ sơ trong danh mục có nghiệp vụ phải là Người.
  - `view`: thêm capability.
  - `debt_register`: thêm khoản kiểu mới.
- `reclassify.py`: mức B và chặn khi đã có chi tiết nghiệp vụ.
- `objects.py`: chặn gỡ, chuyển, gộp đối tượng khi còn chi tiết đã ghi.
- `assets.py`: Phải thu/Phải trả lấy từ cùng một sổ.
- `legacy_import.py` (dòng lịch sử cũ): dùng làm nguồn cho chi tiết nghiệp vụ.
- Module mới `loan_business.py`: khoản vay, chi tiết nghiệp vụ, sổ khoản vay, lãi theo ngày, miễn giảm, hoàn tất, danh sách chờ.

**Màn hình:**
- Danh mục: nhãn và nút nghiệp vụ, bước xem trước khi gắn.
- Hộp Phân loại: lưu vào danh mục có nghiệp vụ thì mở luôn bộ Chi tiết nghiệp vụ.
- Lịch sử giao dịch: trạng thái "Chờ chi tiết nghiệp vụ" hoặc "Đã ghi nghiệp vụ".
- Công nợ: khoản kiểu mới, báo cáo theo người, khoản và danh mục; danh sách chờ.
- Đối tượng: hiện hai chiều của một người.
- Tổng tài sản.
- Tóm tắt tài khoản: thêm dòng "trong đó thuộc nghiệp vụ vay".

**Đường thao tác song song cần chặn hoặc đồng bộ:**
- phân loại, Sửa phân loại, phân loại hàng loạt;
- migrate lịch sử cũ, sửa phân loại dòng lịch sử cũ;
- chuyển đối tượng (`object_moves`), gỡ thành viên, gộp hồ sơ;
- đổi cha, lưu trữ, xóa hẳn danh mục (danh mục có nghiệp vụ hoặc chi tiết thì tính là "đã dùng");
- chuyển nhóm khoản vay cũ (`loan-regroup`);
- xóa hoặc lưu trữ đối tượng.

**Nguồn số liệu:**
- Hiện có hai nguồn: sổ Công nợ kiểu cũ (`debt_register`) và sổ nghiệp vụ theo cặp (`business_view`, đang ẩn).
- Sau thay đổi chỉ còn **một phép tính sổ khoản vay**. Khoản kiểu cũ tính như cũ trong cùng hàm. Công nợ, Tổng tài sản, Danh mục và Đối tượng đều đọc từ đó.

**Báo cáo, snapshot, mốc:**
- Không đổi báo cáo tài khoản, nội dung so sánh của snapshot, quy tắc duyệt, sổ Công nợ của khoản cũ.
- Bảng kê lãi và hoàn tất kiểu cũ (spec 003/004) giữ nguyên cho khoản cũ.

**Quy tắc cũ đổi trạng thái** (cập nhật vào PRODUCT-SPEC):
- R186 được **thay một phần**: Cho vay/Đi vay mở lại theo mô hình gắn nghiệp vụ vào danh mục; BĐS vẫn Pending.
- R146 (vai trò suy từ gốc) bị **thay thế** cho phần vay bởi R203–R212.
- Nghiệp vụ theo cặp đối tượng–danh mục bị **thay thế** cho phần vay bởi R203–R212: R147, R148, R149, R150, R152 (phần vay), R156, R157, R179, R180, R181, R182.
- R151 và R153 (phần BĐS) vẫn Pending.

**Kiểm tra đồng nhất giữa các màn:** test so dư gốc, lãi còn thiếu, số người, số khoản và số giao dịch giữa Công nợ, Danh mục, Đối tượng và Tổng tài sản.

## Luồng màn hình *(để PO đối chiếu trước khi triển khai)*

1. **Danh mục › chọn một danh mục**
   - Dòng "Nghiệp vụ" hiện một trong ba trạng thái: "Chưa gắn"; "Cho vay (Phải thu) · gắn tại đây"; "Cho vay (Phải thu) · kế thừa từ Hot Debt".
   - Có nút **Gắn nghiệp vụ** và **Gỡ nghiệp vụ**.
   - Gắn nghiệp vụ: chọn Cho vay hoặc Đi vay → **xem trước** gồm:
     - số danh mục trong nhánh;
     - lịch sử đã hợp lệ (liên kết cũ đúng chiều);
     - phần còn thiếu chi tiết (số giao dịch, tổng tiền vào/ra);
     - phần xung đột (đối tượng không phải Người; khoản cũ khác chiều hoặc chưa thiết lập);
     - nhánh con đang mang nghiệp vụ khác (có thì bị chặn).
   - Nhập lý do → Xác nhận.
2. **Phân loại giao dịch** vào danh mục có nghiệp vụ
   - Chọn danh mục theo cấp và chọn người thành viên như hiện nay → Lưu.
   - Hệ thống mở ngay **Chi tiết nghiệp vụ** (cách A). Nếu đóng hộp mà chưa ghi, giao dịch ở trạng thái "Chờ chi tiết nghiệp vụ" (cách B).
3. **Chi tiết nghiệp vụ** (một bộ dùng chung cho mọi lối vào)
   - Phần đầu: tiền nguồn, phần thuộc nghiệp vụ, ngày, người.
   - Mỗi dòng chọn:
     - khoản vay của người đó, cùng chiều; hoặc **+ Tạo khoản vay**;
     - thành phần theo chiều tiền (ví dụ tiền vào của Cho vay là "Thu gốc" hoặc "Thu lãi");
     - số tiền.
   - Dòng "Còn phải phân bổ".
   - **Xem trước tác động** của từng khoản:
     - dư gốc trước/sau;
     - "Tất toán một phần" hay "Tất toán toàn bộ gốc";
     - lãi tính tới ngày giao dịch, đã thu, còn thiếu sau giao dịch;
     - cảnh báo vượt nghĩa vụ.
   - Nút **Lưu nháp** luôn bấm được. Nút **Ghi nghiệp vụ** chỉ bấm được khi đã phân bổ đủ, khớp tiền và không vượt nghĩa vụ.
   - Bản đã ghi có thêm nút **Hủy nghiệp vụ** (cần lý do).
4. **Công nợ**
   - Đầu trang:
     - tổng Phải thu và tổng Phải trả, không bù trừ;
     - số người, số khoản, số giao dịch đã ghi;
     - băng vàng "Chưa đầy đủ: N giao dịch chờ chi tiết, vào X, ra Y" kèm nút **Mở danh sách chờ**.
   - Có bộ lọc theo danh mục nghiệp vụ.
   - Mỗi người có hai khối riêng **Cho vay** và **Đi vay**. Mỗi khoản hiện:
     - mã, tên, mức lãi, môi giới;
     - dư gốc;
     - lãi theo điều khoản tới ngày xem, lãi thực thu/trả, miễn giảm, lãi còn thiếu;
     - phần môi giới theo điều khoản và tiền môi giới đã trả thực tế;
     - đến hạn hoặc quá hạn, trạng thái.
   - Nút trên từng khoản:
     - **Ghi từ giao dịch nguồn**: chọn một giao dịch hoặc dòng lịch sử đã phân loại vào danh mục cùng chiều của người đó, rồi mở cùng bộ Chi tiết nghiệp vụ;
     - **Miễn giảm lãi**;
     - **Hoàn tất / Mở lại**;
     - **Sửa thông tin**;
     - **Sổ chi tiết**.
   - Nút **+ Khoản vay mới**: chọn danh mục nghiệp vụ, người, tên, mã (tự gợi ý), ngày theo dõi, hạn (tùy chọn), mức lãi, môi giới.
   - Khoản kiểu cũ giữ nguyên ở khối "Khoản vay cũ".
5. **Danh sách chờ chi tiết nghiệp vụ**: từng nguồn kèm lý do (thiếu người / thiếu khoản / chưa phân bổ đủ / còn nháp chưa ghi), và nút mở Chi tiết nghiệp vụ.

## Ví dụ số xuyên suốt *(dùng cho test và QA)*

Danh mục **Hot Debt** mang Cho vay; danh mục **Vay bạn** mang Đi vay. Người **Kết** là thành viên của cả hai.

| # | Ngày | Nguồn | Chi tiết nghiệp vụ | Kết quả kỳ vọng |
|---|------|-------|--------------------|-----------------|
| 1 | 20/10 | Ra 100.000.000 (Hot Debt, Kết) | CV-0001 (mức 500, môi giới Long 200): Giải ngân 100.000.000 | Dư gốc 100.000.000 |
| 2 | 22/10 | Ra 10.000.000 (Hot Debt, Kết) | CV-0002 (mức 600, không môi giới): Giải ngân 10.000.000 | Kết có 2 khoản Cho vay |
| 3 | 22/10 | Vào 50.000.000 (Vay bạn, Kết) | ĐV-0001 (mức 0): Nhận tiền vay 50.000.000 | Phải trả 50.000.000, không bù với Phải thu |
| 4 | 25/10 | Vào 40.150.000 (Hot Debt, Kết) | CV-0001: Thu gốc 40.000.000 + Thu lãi 150.000 | Tất toán một phần. Lãi 20–25/10 = 6 ngày × 50.000 = **300.000**; đã thu 150.000; **còn thiếu 150.000**. Môi giới theo điều khoản **120.000**; chênh lệch theo điều khoản **180.000**. Từ 26/10 cơ sở 60.000.000, lãi 30.000/ngày |
| 5 | 27/10 | Ra 120.000 (Hot Debt, Kết) | CV-0001: Trả phí môi giới 120.000 | Môi giới đã trả thực tế 120.000; không trừ gốc, không giảm lãi khách đã trả |
| — | xem 30/10 | — | — | CV-0001: lãi theo điều khoản 300.000 + 5 × 30.000 = **450.000**; đã thu 150.000; còn thiếu **300.000**. CV-0002: 9 ngày × 6.000 = **54.000** |
| 6 | 31/10 | Vào 70.360.000 (Hot Debt, Kết), **một giao dịch cho hai khoản** | CV-0001: Thu gốc 60.000.000 + Thu lãi 300.000. CV-0002: Thu gốc 10.000.000 + Thu lãi 60.000 | CV-0001: dư gốc 0; ngày 31/10 vẫn tính lãi (tổng 480.000); đã thu 450.000; **còn thiếu 30.000 → chưa hoàn tất**. CV-0002: lãi 22–31/10 = 10 × 6.000 = 60.000, đã thu đủ, dư gốc 0, hoàn tất được |
| 7 | 31/10 | — | Miễn giảm lãi CV-0001 30.000, lý do "Bớt lãi lẻ" | Lãi còn thiếu 0 → hoàn tất được; miễn giảm không phải tiền thu |
| 8 | 29/10 | Vào 5.000.000 (Hot Debt, Tươi); Tươi chưa có khoản | (chưa có) | "Chờ chi tiết nghiệp vụ: thiếu khoản vay". Công nợ báo chưa đầy đủ: 1 giao dịch, vào 5.000.000 |
| 9 | 25/10 | Thử ở bước 4: Thu gốc 110.000.000 | — | **Bị chặn** "vượt dư gốc 100.000.000 tại 25/10"; sổ không đổi |
| 10 | — | Khoản 1.234.567, mức 500, 3 ngày | — | 617,2835 × 3 = 1.851,8505 → **1.852** |

Môi giới CV-0001 tới 31/10 theo điều khoản: 120.000 + 6 × 12.000 = **192.000**. Chênh lệch theo điều khoản: 480.000 − 192.000 = **288.000** (trước chi phí khác). Tiền môi giới đã trả thực tế: 120.000. Không có số nào được trình bày là "tiền thực nhận của chủ khoản".

Kết trong báo cáo theo người: Cho vay có 2 khoản, dư gốc 0 sau bước 6; Đi vay có 1 khoản, dư 50.000.000. Hai chiều hiện riêng, không bù trừ.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gắn nghiệp vụ vào danh mục, kế thừa và chặn xung đột (Priority: P1)
Thạch gắn Cho vay cho Hot Debt; mọi danh mục con, cháu và đối tượng trong nhánh kế thừa Cho vay.
- Gắn nghiệp vụ khác cho con bị chặn.
- Gắn cho cha khi có nhánh con mang nghiệp vụ khác bị chặn.
- Trước khi gắn, xem trước được phần lịch sử.

**Why this priority**: là nền của mọi phần khác; sai chỗ này thì sai chiều Phải thu/Phải trả.

**Independent Test**: dữ liệu giả có cây 3 cấp.
- Gắn Cho vay cho cha → con hiện "kế thừa".
- Gắn Đi vay cho con → bị chặn.
- Gắn cho cha khi một con mang Đi vay → bị chặn, kèm đường dẫn nhánh xung đột.

**Acceptance Scenarios**:
1. **Given** Hot Debt › Ngắn hạn chưa có nghiệp vụ, **When** gắn Cho vay cho Hot Debt, **Then** Ngắn hạn hiện "Cho vay · kế thừa từ Hot Debt".
2. **Given** Hot Debt mang Cho vay, **When** gắn Đi vay cho Ngắn hạn, **Then** bị chặn "danh mục con không được khác nghiệp vụ của cha".
3. **Given** cha chưa có nghiệp vụ, con A mang Cho vay, con B mang Đi vay, **When** gắn Cho vay cho cha, **Then** bị chặn và nêu "Cha › B (Đi vay)"; không có gì bị ghi đè.
4. **Given** danh mục có giao dịch cũ, **When** bấm Gắn nghiệp vụ, **Then** xem trước số giao dịch hợp lệ, thiếu và xung đột; chưa xác nhận thì chưa có gì thay đổi.
5. **Given** nhánh đã có chi tiết nghiệp vụ (đã ghi hoặc nháp), **When** gỡ hoặc đổi nghiệp vụ, hay đổi cha sang nơi có nghiệp vụ khác, **Then** bị chặn và nêu số chi tiết.
6. **Given** danh mục tên "Cho vay" nhưng chưa gắn nghiệp vụ, **Then** danh mục đó không có nghiệp vụ.

---

### User Story 2 - Nhiều khoản vay cho một người (Priority: P1)
Thạch tạo khoản vay cho một người trong danh mục có nghiệp vụ, với mã, tên, ngày theo dõi, hạn (tùy chọn), mức lãi, môi giới. Một người có nhiều khoản, ở cả hai chiều.

**Independent Test**: tạo CV-0001, CV-0002 và ĐV-0001 cho Kết.
- Mã trùng bị chặn.
- Khoản Cho vay nhận môi giới; khoản Đi vay không có trường môi giới.

**Acceptance Scenarios**:
1. **Given** Kết là thành viên Hot Debt (Cho vay), **When** tạo khoản từ Hot Debt, **Then** khoản có chiều Cho vay và không đổi được chiều.
2. **Given** người chưa là thành viên danh mục nghiệp vụ nào cùng chiều, **When** tạo khoản, **Then** bị chặn và được hướng dẫn thêm người vào danh mục trước.
3. **Given** khoản đã có chi tiết đã ghi, **When** sửa mức lãi, **Then** cần lý do, lưu lịch sử và xem được số lãi thay đổi. Đây là sửa nhập sai cho cả khoản, không phải đổi lãi theo thời gian.

---

### User Story 3 - Chi tiết nghiệp vụ: tách nhiều khoản, gốc/lãi, nháp không ghi sổ (Priority: P1)
Giao dịch phân loại vào danh mục có nghiệp vụ được bóc thành các dòng (khoản vay, thành phần, số tiền). Có thể ghi ngay hoặc lưu nháp để làm sau.

**Independent Test**:
- Bước 6 (một giao dịch, hai khoản, cả gốc lẫn lãi) ghi được khi tổng khớp.
- Lưu nháp còn thiếu 360.000 thì sổ không đổi, giao dịch ở trạng thái "Chờ chi tiết".

**Acceptance Scenarios**:
1. **Given** chi tiết thiếu tiền, **When** bấm Ghi nghiệp vụ, **Then** bị chặn, kèm số còn thiếu. Lưu nháp vẫn được và sổ không đổi.
2. **Given** đã có bản đã ghi, **When** sửa nháp thay thế, **Then** sổ dùng bản hiện hành cho tới khi bản mới đủ và được ghi; bản cũ giữ trong lịch sử.
3. **Given** chưa chọn người, hoặc người chưa có khoản cùng chiều, **Then** trạng thái "Chờ chi tiết nghiệp vụ" ghi rõ lý do; hệ thống không tạo người hay khoản giả.
4. **Given** giao dịch đã ghi nghiệp vụ, **When** phân loại lại, Sửa phân loại, chuyển đối tượng hoặc gộp hồ sơ làm đổi phần tiền thuộc nghiệp vụ, **Then** bị chặn; phải hủy hoặc sửa chi tiết trước (có lý do).
5. **Given** dòng lịch sử cũ thuộc danh mục có nghiệp vụ, **Then** bóc tách được như giao dịch ngân hàng và không bị ghi đôi.
6. **Given** phần tiền cũ đã gắn khoản vay kiểu cũ đúng chiều, **Then** xem trước tính là "đã hợp lệ", giữ nguyên, không ghi lại.

---

### User Story 4 - Lãi theo ngày, tất toán một phần/toàn bộ, miễn giảm, chặn trả vượt (Priority: P1)
Sổ khoản vay tính lãi theo từng đoạn gốc, đúng quy ước ngày và quy tắc làm tròn. Khi ghi trả gốc thì xem được trước tác động tất toán. Miễn giảm có lịch sử. Trả vượt bị chặn.

**Independent Test**: bước 1–7 của ví dụ cho ra đúng từng số trong bảng.

**Acceptance Scenarios**:
1. Giải ngân 100.000.000 ngày 20/10, mức 500, trả hết ngày 25/10 → lãi 300.000.
2. Trả 40.000.000 ngày 25/10 → lãi 20–25/10 là 300.000; từ 26/10 mỗi ngày 30.000.
3. Khoản mức 0 → lãi 0, chỉ theo dõi gốc.
4. Hết gốc nhưng còn lãi → chưa hoàn tất được; miễn giảm đủ thì hoàn tất được.
5. Thu gốc vượt dư gốc, hoặc thu lãi vượt lãi tính tới ngày thu → bị chặn, kèm hướng dẫn xử lý phần thừa (phân loại phần thừa sang danh mục khác).
6. Hủy hoặc sửa chi tiết làm khoản đã hoàn tất thành sai, hoặc làm miễn giảm vượt lãi → bị chặn, kèm hướng dẫn mở lại khoản hoặc hủy miễn giảm trước.

---

### User Story 5 - Môi giới theo điều khoản (Priority: P2)
Khoản Cho vay có môi giới thì hiện phần môi giới và phần chênh lệch, cả hai ghi rõ là "theo điều khoản". Tiền trả môi giới là dòng "Trả phí môi giới" của một giao dịch tiền ra.

**Acceptance Scenarios**:
1. Mức 500, môi giới 200, gốc 100 triệu, 6 ngày → tổng lãi 300.000, môi giới 120.000, chênh lệch 180.000.
2. Mới thu 150.000 → thực thu 150.000, còn thiếu 150.000; môi giới vẫn 120.000 và chênh lệch vẫn 180.000 theo điều khoản. Không xuất hiện số 60.000/90.000.
3. Trả môi giới không đổi dư gốc và không đổi lãi đã thu.

---

### User Story 6 - Một nguồn công nợ, báo cáo chưa đầy đủ, nhất quán giữa các màn (Priority: P1)
Công nợ, Danh mục, Đối tượng và Tổng tài sản dùng cùng một số. Báo cáo theo danh mục, nghiệp vụ, người, khoản. Còn giao dịch chờ thì báo cáo ghi rõ chưa đầy đủ.

**Acceptance Scenarios**:
1. Sau ví dụ, Phải thu, Phải trả, dư gốc từng khoản và số giao dịch giống nhau ở mọi màn.
2. Còn giao dịch chờ → băng "Chưa đầy đủ" có số giao dịch, tổng vào/ra và nút mở danh sách; lãi dự tính kèm cảnh báo có thể thay đổi.
3. Còn giao dịch chờ trong phạm vi người/chiều → không cho Hoàn tất khoản.
4. Chốt sao kê ngân hàng vẫn được dù còn chi tiết nghiệp vụ chờ; snapshot cũ và nội dung so sánh không đổi.
5. Giao dịch tách cho hai khoản đếm là 1 giao dịch. Người có 3 khoản đếm là 1 người, 3 khoản.

### Edge Cases
- **Cùng ngày vừa giải ngân vừa trả**: giải ngân vào cơ sở ngay ngày đó, phần trả trừ từ hôm sau. Giải ngân rồi trả hết trong cùng ngày thì tính 1 ngày lãi.
- **Giao dịch có phần thuộc danh mục thường và phần thuộc danh mục nghiệp vụ**: chỉ bóc phần thuộc nghiệp vụ.
- **Giao dịch tách cho hai người ở hai phần phân loại**: mỗi phần chỉ chọn được khoản của đúng người đó.
- **Danh mục nghiệp vụ bị lưu trữ**: chi tiết đã ghi vẫn được tính; không phân loại mới vào được (R202).
- **Khoản kiểu cũ** (hồ sơ "Khoản …"): vẫn hiện với số cũ; không tự chuyển sang khoản mới, không tự tính lãi mới.
- **Đối tượng không phải Người** (BĐS, Khác) trong danh mục nghiệp vụ: xem trước báo xung đột; không tạo khoản vay cho đối tượng đó.
- **Ngày xem**: trước ngày giải ngân đầu tiên thì lãi 0; ngày xem trong tương lai thì ghi "dự tính".
- **Thành phần không hợp chiều tiền**: tiền vào của Cho vay không chọn được "Giải ngân"; tiền ra của Cho vay không chọn được "Thu lãi"; Đi vay không có môi giới.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001 (R203)**: Gắn nghiệp vụ vào danh mục.
  - Chỉ gắn vào danh mục người dùng tạo; không gắn vào đối tượng; không suy từ tên.
  - Nghiệp vụ hiệu lực = của chính danh mục hoặc của tổ tiên gần nhất. Con không được khác cha.
  - Gắn cho cha bị chặn nếu có nhánh con mang nghiệp vụ khác, kèm danh sách nhánh.
  - Khi gắn: có xem trước (hợp lệ / thiếu / xung đột), lý do và lịch sử.
- **FR-002 (R203)**: Giữ nghiệp vụ hiệu lực không bị đổi âm thầm.
  - Gỡ hoặc đổi nghiệp vụ, đổi cha, chuyển nhánh làm đổi nghiệp vụ hiệu lực → bị chặn khi nhánh có chi tiết nghiệp vụ (đã ghi hoặc nháp) hoặc có khoản vay được tạo từ nhánh.
  - Lưu trữ danh mục giữ nguyên chi tiết đã ghi.
  - Danh mục có nghiệp vụ hoặc có chi tiết thì không xóa hẳn được (bổ sung R201).
- **FR-003 (R204)**: Khoản vay thuộc đúng một Người, gồm:
  - mã duy nhất (gợi ý CV-xxxx / ĐV-xxxx); tên 1–100 ký tự; ngày theo dõi; hạn (không bắt buộc);
  - chiều cố định, lấy từ danh mục nghiệp vụ nơi tạo (người phải là thành viên của nhánh đó);
  - mức lãi ≥ 0 đồng/triệu/ngày;
  - môi giới, chỉ cho Cho vay: tên và mức ≥ 0.
  - Sửa thông tin cần lý do, có lịch sử. Không tạo khoản tự động.
- **FR-004 (R205)**: Chi tiết nghiệp vụ.
  - Áp dụng cho giao dịch ngân hàng và dòng lịch sử cũ có phần tiền trong danh mục có nghiệp vụ.
  - Mỗi dòng: khoản vay của đúng người của phần tiền đó và cùng chiều; thành phần hợp chiều tiền; số tiền dương.
  - Chỉ ghi được khi: tổng các dòng của từng phần khớp đúng phần tiền; không vượt nghĩa vụ; khoản chưa hoàn tất; ngày nguồn từ ngày theo dõi trở đi.
  - Nháp lưu được bất cứ lúc nào và không tính vào sổ.
  - Khi sửa, bản hiện hành giữ nguyên tới khi bản thay thế được ghi. Hủy cần lý do. Mọi phiên bản đều được giữ.
- **FR-005 (R205)**: Trạng thái và chặn sửa.
  - Mỗi nguồn ở trạng thái "Chờ chi tiết nghiệp vụ" hoặc "Đã ghi nghiệp vụ", kèm lý do còn thiếu; có danh sách chờ.
  - Phân loại, Sửa phân loại, chuyển đối tượng, gộp hồ sơ, gỡ thành viên làm đổi phần tiền đã ghi nghiệp vụ → bị chặn.
  - Hồ sơ gắn cho phần tiền mới trong danh mục có nghiệp vụ phải là Người.
- **FR-006 (R206)**: Lãi theo ngày, tính bằng số thập phân chính xác.
  - Lãi ngày D = cơ sở(D) / 1.000.000 × mức; cơ sở(D) = dư gốc cuối ngày D−1 + gốc giải ngân ngày D.
  - Tổng lũy kế tới ngày xem làm tròn về đồng, nửa lên.
  - Sổ cho ra: lãi theo điều khoản tới ngày xem, lãi thực thu/trả, miễn giảm, lãi còn thiếu.
  - Không thay đổi lãi theo thời gian, không lãi phạt, không nhập lãi vào gốc.
- **FR-007 (R207)**: Khi ghi gốc, xem trước tác động: dư gốc trước/sau, tất toán một phần/toàn bộ, lãi còn thiếu. Bắt đầu từ khoản vay ("Ghi từ giao dịch nguồn") dùng cùng một cơ chế.
- **FR-008 (R207)**: Miễn giảm lãi có số tiền, ngày, lý do, lịch sử; hủy cần lý do. Không được vượt lãi còn thiếu tại ngày đó và không phải tiền thu.
- **FR-009 (R207)**: Hoàn tất khoản là thao tác người dùng xác nhận.
  - Điều kiện: dư gốc 0, lãi còn thiếu 0, không còn nguồn chờ trong phạm vi người/chiều của khoản.
  - Mở lại cần lý do.
  - Khoản đã hoàn tất không nhận chi tiết hay miễn giảm mới.
- **FR-010 (R208)**: Trả vượt bị chặn.
  - Gốc vượt dư gốc.
  - Lãi đã thu/trả cộng miễn giảm vượt lãi tính tới ngày đó, xét tại mọi ngày có phát sinh.
  - Không tạo dư âm, doanh thu hay tiền trả trước.
- **FR-011 (R209)**: Môi giới chỉ cho khoản Cho vay.
  - Phần môi giới theo điều khoản = cơ sở như FR-006 × mức môi giới. Chênh lệch theo điều khoản = lãi theo điều khoản − phần môi giới.
  - Tiền trả môi giới là thành phần "Trả phí môi giới" của tiền ra; không đổi gốc hay lãi đã thu. Trả vượt phần theo điều khoản thì cảnh báo, không chặn.
  - Không chia lãi thực thu theo tỷ lệ. Miễn giảm không tự phân bổ sang môi giới; giới hạn này hiện công khai.
- **FR-012 (R210)**: Một phép tính sổ khoản vay cho Công nợ, Danh mục, Đối tượng, Tổng tài sản và báo cáo. Khoản kiểu cũ tính trong cùng hàm theo quy tắc cũ, không đếm đôi.
- **FR-013 (R211)**: Báo cáo theo danh mục nghiệp vụ, chiều, người và khoản.
  - Đếm riêng số người, số khoản, số giao dịch.
  - Phân biệt tiền vào/ra với thu nhập/chi phí, và lãi theo điều khoản với lãi thực thu/trả.
  - Người có hai chiều thì trình bày hai khối, không bù trừ.
- **FR-014 (R211)**: Còn nguồn chờ thì báo cáo ghi "Chưa đầy đủ" (số giao dịch, tổng vào/ra, nút mở danh sách) và lãi dự tính có cảnh báo. Duyệt sao kê không bị chặn.
- **FR-015 (R212)**: Không đổi tiền nguồn, sao kê, nội dung so sánh của snapshot, báo cáo tài khoản, khoản kiểu cũ và bảng kê cũ. Phân loại nghiệp vụ không tạo thêm tiền ngân hàng.
- **FR-016**: Nghiệp vụ BĐS và mô hình nghiệp vụ theo cặp (spec 031) vẫn tạm dừng.

### Key Entities
- **Nghiệp vụ danh mục**: loại (Cho vay / Đi vay), lịch sử gắn và gỡ (thời điểm, lý do).
- **Khoản vay**: mã, tên, người, chiều, danh mục nơi tạo, ngày theo dõi, hạn, mức lãi, môi giới (tên, mức), trạng thái hoàn tất, lịch sử.
- **Chi tiết nghiệp vụ**: nguồn (giao dịch hoặc dòng lịch sử cũ), các phiên bản đã ghi (dòng, thời điểm, lý do), nháp, lịch sử hủy.
- **Miễn giảm lãi**: khoản, ngày, số tiền, lý do, trạng thái, lịch sử.
- **Sổ khoản vay** (chỉ đọc): các đoạn gốc, lãi, môi giới, trạng thái, cảnh báo.

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: 100% số trong bảng ví dụ (bước 1–10) đúng tới từng đồng, kiểm bằng test tự động.
- **SC-002**: Chênh lệch bằng 0 giữa Công nợ, Danh mục, Đối tượng và Tổng tài sản trên bộ dữ liệu giả, cho: Phải thu, Phải trả, dư gốc, lãi còn thiếu, số người, số khoản, số giao dịch.
- **SC-003**: Không có trường hợp nào nháp hoặc chi tiết chưa đủ làm đổi số trong sổ.
- **SC-004**: So từng trường trên bản sao dữ liệu thật trước/sau: snapshot đã duyệt, báo cáo tài khoản và số của khoản kiểu cũ không đổi.
- **SC-005**: Mọi đường sửa song song đều bị chặn khi làm lệch chi tiết đã ghi, mỗi đường có test: phân loại, Sửa phân loại, chuyển đối tượng, gộp hồ sơ, gỡ thành viên, đổi cha, gỡ nghiệp vụ, xóa danh mục.
- **SC-006**: Đi hết ví dụ 1–8 qua giao diện trên dữ liệu giả mà không phải làm gì ngoài giao diện.

## Tư vấn kế toán *(Constitution VIII)*

- **Ghi nhận theo bản chất kinh tế**:
  - Giải ngân không phải chi phí; thu gốc không phải thu nhập.
  - Lãi thu là thu nhập tài chính. Lãi trả và phí môi giới là chi phí tài chính.
  - Danh mục Hot Debt đang nằm trong nhóm chi; cây danh mục vẫn tổng hợp tiền vào/ra như cũ.
  - Báo cáo nghiệp vụ và tóm tắt tài khoản ghi rõ phần "thuộc nghiệp vụ vay, không phải chi tiêu/thu nhập". Báo cáo tài khoản đã lưu và snapshot không đổi, để giữ tính bất biến.
- **Phải thu và Phải trả không bù trừ**, kể cả khi cùng một người.
- **Lãi**:
  - Hiển thị cả lãi theo điều khoản (dồn tích tới ngày xem) lẫn lãi thực thu/trả.
  - Theo nguyên tắc **thận trọng**, lãi theo điều khoản chưa thu là **số dự tính để theo dõi**, không ghi doanh thu.
  - Ghi nhận doanh thu dồn tích hoặc trích dự phòng nợ khó đòi **cần kế toán viên xác nhận**.
- **Miễn giảm lãi** là giảm nghĩa vụ, không phải tiền thu và không phải chi phí tiền mặt. Giữ dấu vết để giải thích chênh lệch giữa lãi theo điều khoản và lãi thực thu.
- **Môi giới**:
  - Phần theo điều khoản là số tham chiếu, chưa phải nghĩa vụ phải trả đã ghi nhận. Chi phí môi giới thực tế là số tiền đã trả.
  - Khi miễn giảm lãi, phần môi giới có giảm theo hay không tùy thỏa thuận; hệ thống **không tự suy diễn**.
- **Làm tròn** một lần trên tổng lũy kế (nửa lên): nhất quán, tránh sai số cộng dồn của việc làm tròn từng ngày, và khớp ví dụ của Thạch.
- **Số dư đầu kỳ** chưa nhập được. Khoản có lịch sử trước ngày theo dõi sẽ thiếu số; hệ thống ghi "dữ liệu chưa đầy đủ" và không tạo giao dịch giả.
- **Thuế / pháp lý**: lãi cho vay của cá nhân có thể phát sinh nghĩa vụ thuế thu nhập từ đầu tư vốn, và mức lãi có giới hạn theo pháp luật. **Cần kế toán viên / chuyên viên thuế xác nhận.** Hệ thống không tính thuế và không kiểm trần lãi.

## Assumptions
- **Thành phần trong phạm vi**:
  - Cho vay: Giải ngân / Thu gốc / Thu lãi / Trả phí môi giới.
  - Đi vay: Nhận tiền vay / Trả gốc / Trả lãi.
  - Hoàn trả tiền thừa và tiền trả trước nằm ngoài phạm vi.
- Ngày xem mặc định là hôm nay và chọn lại được.
- Mã khoản do hệ thống gợi ý theo chiều; người dùng sửa được; duy nhất trong toàn hệ thống.
- Khoản kiểu cũ giữ luồng thiết lập, bảng kê và hoàn tất cũ. Muốn đưa sang mô hình mới, người dùng tự Sửa phân loại giao dịch vào danh mục có nghiệp vụ rồi ghi chi tiết; hệ thống không tự chuyển.
- Chỉ gắn nghiệp vụ trên danh mục người dùng tạo, không trên gốc hệ thống (Gốc vay, Lãi vay…), vì liên kết cũ ở các gốc này đã có chiều riêng trên khoản cũ.
- Mức lãi và mức môi giới tối đa 100.000 đ/triệu/ngày: giới hạn kỹ thuật chặn nhập nhầm, không phải quy tắc nghiệp vụ.
- Mọi thao tác ghi đều cần người dùng xác nhận; không có thao tác tự động trên dữ liệu thật.
