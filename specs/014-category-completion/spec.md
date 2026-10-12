# Feature Specification: Hoàn thiện Danh mục

**Feature Branch**: `014-category-completion`
**Created**: 2026-10-12
**Status**: Draft
**Input**: Thạch yêu cầu tiếp tục hoàn thiện phần Danh mục (12/10/2026) và đã chốt qua phỏng vấn: cho tạo danh mục gốc mới kế thừa quy tắc theo loại; xem tổng theo kỳ; báo cáo duyệt theo danh mục. Nguồn yêu cầu: R46, R55, R56, R58, R81–R83 · Spec liên quan: 001, 008 (quản lý danh mục), 009, 010 (hoàn chi).

**Phạm vi:** bổ sung cho màn Danh mục đã có (spec 008). **Không** gồm: gộp danh mục, loại "trung tính", tổng đa tiền tệ. Không đổi quy tắc tiền hay kết quả snapshot/báo cáo đã có.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tự tạo danh mục gốc mới theo loại (Priority: P1)
Thạch tạo danh mục gốc mới (ví dụ "Kinh doanh nhỏ", "Giáo dục") ngang hàng 7 gốc hệ thống, bắt buộc chọn một loại kế thừa quy tắc: **nhóm thu** (như Thu nhập), **nhóm chi** (như Chi tiêu, nhận cả chi và hoàn chi) hoặc **nhóm đầu tư** (gắn hồ sơ BĐS). Gốc mới có tổng riêng và danh mục con của riêng nó.

**Why this priority**: R81 — Thạch cần nhóm cấp cao của riêng mình, không bị buộc phải đặt dưới 7 gốc cố định.

**Independent Test**: tạo gốc "Kinh doanh nhỏ" loại nhóm chi; tạo con "Nhập hàng" dưới nó; phân loại một giao dịch chi vào "Nhập hàng" → tổng của "Kinh doanh nhỏ" tăng, tổng gốc hệ thống "Chi tiêu" không tăng; báo cáo duyệt theo loại vẫn tính vào chi tiêu.

**Acceptance Scenarios**:
1. **Given** màn Danh mục, **When** tạo gốc mới với tên và loại, **Then** hiển thị ngang hàng 7 gốc hệ thống và chọn được khi phân loại giao dịch hợp chiều tiền.
2. **Given** tên trùng một gốc bất kỳ (kể cả gốc hệ thống như "Chi tiêu") không phân biệt hoa/thường, **When** tạo, **Then** bị chặn.
3. **Given** gốc nhóm chi, **When** phân loại tiền vào, **Then** được (hoàn chi); gốc nhóm thu chỉ nhận tiền vào; gốc nhóm đầu tư yêu cầu hồ sơ BĐS như Đầu tư BĐS.
4. **Given** gốc đã tạo, **When** đổi tên, lưu trữ (có lý do) hoặc khôi phục, **Then** hoạt động như danh mục con; **loại không đổi được**.
5. **Given** giao dịch dưới gốc mới, **When** xem tổng gốc hệ thống cùng loại, **Then** không bị cộng (tổng riêng, không đếm đôi).

### User Story 2 - Xem tổng và lịch sử theo kỳ (Priority: P1)
Màn Danh mục và lịch sử từng danh mục có bộ lọc kỳ: tháng này, tháng trước, quý này, quý trước, hoặc khoảng ngày tùy chọn, theo **ngày giao dịch**. Tổng vào/ra/chênh (Chi tiêu: chi, hoàn chi, chi ròng) và số giao dịch tính trong kỳ.

**Why this priority**: R82 — để thấy chi tiêu từng danh mục trong một tháng.

**Independent Test**: giao dịch ở tháng 9 và tháng 10; lọc tháng 9 → chỉ tổng tháng 9; lọc "tất cả" → như hiện nay; lịch sử danh mục theo cùng kỳ.

**Acceptance Scenarios**:
1. **Given** bộ lọc kỳ, **When** chọn tháng, **Then** tổng và số giao dịch của mọi danh mục chỉ gồm giao dịch trong tháng đó.
2. **Given** kỳ không có giao dịch, **When** xem, **Then** danh mục hiển thị "chưa có giao dịch trong kỳ này" (không phải 0 như đã đối soát) kèm kỳ nguồn đã ghi.
3. **Given** kỳ tùy chọn có ngày kết thúc trước ngày bắt đầu hoặc ngày không hợp lệ, **When** áp dụng, **Then** bị chặn kèm lý do.
4. **Given** lọc kỳ, **When** mở lịch sử một danh mục, **Then** danh sách và tổng trong lịch sử dùng cùng kỳ và nêu kỳ đang lọc.
5. **Given** kỳ vượt kỳ nguồn đã ghi, **When** xem, **Then** có ghi chú nguồn chỉ phủ các kỳ đã ghi.

### User Story 3 - Báo cáo duyệt theo danh mục (Priority: P1)
Trong bước xem toàn đợt trước khi duyệt, Thạch thấy báo cáo theo danh mục: từng gốc, danh mục con kèm số giao dịch, số đối tượng liên quan, tiền vào/ra (Chi tiêu: chi, hoàn chi, chi ròng), mở được chi tiết từng danh mục; và kiểm đối chiếu đủ số giao dịch gốc và tổng tiền, không trùng, không thiếu.

**Why this priority**: R46 — duyệt phải kiểm được đủ và đúng, không chỉ nhìn tổng theo loại.

**Independent Test**: tài khoản có 7 giao dịch (một tách hai danh mục) → báo cáo hiển thị đúng số giao dịch mỗi danh mục, mỗi giao dịch đếm một lần ở cha, tổng số giao dịch khớp 7, tổng tiền vào/ra khớp nguồn; chưa phân loại là một nhóm riêng.

**Acceptance Scenarios**:
1. **Given** tài khoản đang duyệt, **When** mở báo cáo theo danh mục, **Then** thấy mọi gốc (kể cả gốc tự tạo và Chưa phân loại) và danh mục con lồng nhau với số giao dịch, số đối tượng, vào/ra.
2. **Given** giao dịch tách nhiều phần, **When** xem, **Then** mỗi danh mục nhận phần của nó, danh mục cha đếm giao dịch một lần.
3. **Given** báo cáo, **When** kiểm đối chiếu, **Then** hiển thị khớp/không khớp cho: số giao dịch gốc so với số giao dịch phân vào các nhóm (mỗi giao dịch đúng một lần ở cấp gốc ít nhất một nhóm), tổng tiền vào, tổng tiền ra; không khớp được nêu rõ.
4. **Given** danh mục, **When** bấm mở chi tiết, **Then** thấy các dòng giao dịch (ngày, nội dung, vào/ra, đối tượng, trạng thái) của tài khoản đang duyệt và mở được dòng nguồn.
5. **Given** bộ lọc giao diện ở bước phân loại, **When** xem báo cáo duyệt, **Then** báo cáo luôn gồm toàn bộ giao dịch của tài khoản, không phụ thuộc bộ lọc.

### Edge Cases
- Đổi cha một danh mục con sang gốc tự tạo cùng loại: được (cùng loại), tổng chuyển theo; sang gốc khác loại: bị chặn.
- Gốc tự tạo đã lưu trữ: loại khỏi lựa chọn mới, lịch sử vẫn tính vào tổng và báo cáo cũ.
- Gốc tự tạo nhóm đầu tư: phần phân loại vẫn dùng loại Đầu tư BĐS (cần hồ sơ BĐS) để các phân hệ BĐS/tổng tài sản nhận đúng.
- Hai tên chỉ khác hoa/thường hoặc khoảng trắng đầu/cuối: coi là trùng (tên khác dấu tiếng Việt là tên khác, như spec 008).
- Bản duyệt cũ: snapshot giữ nguyên danh mục lúc duyệt (kể cả gốc tự tạo); đổi tên gốc không đổi snapshot cũ.
- Tài khoản không có giao dịch: báo cáo duyệt hiển thị trạng thái rỗng, không số 0 giả.
- Không còn giao dịch chưa phân loại: nhóm Chưa phân loại hiển thị 0 giao dịch kèm trạng thái đã phân loại hết.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Hệ thống MUST cho tạo danh mục gốc mới ngang hàng gốc hệ thống với tên 1–100 ký tự và loại bắt buộc thuộc {nhóm thu, nhóm chi, nhóm đầu tư}; loại MUST NOT đổi sau khi tạo (R81).
- **FR-002**: Tên gốc mới MUST không trùng tên bất kỳ gốc nào (kể cả gốc hệ thống, cả gốc đã lưu trữ), không phân biệt hoa/thường và khoảng trắng đầu/cuối.
- **FR-003**: Gốc mới MUST kế thừa quy tắc theo loại: nhóm thu chỉ nhận tiền vào (và loại Thu nhập); nhóm chi nhận cả chi và hoàn chi; nhóm đầu tư yêu cầu hồ sơ BĐS; danh mục con kế thừa loại của gốc; độ sâu tối đa 4 cấp kể cả gốc.
- **FR-004**: Gốc mới MUST đổi tên, lưu trữ (có lý do) và khôi phục được; MUST NOT xóa; đổi tên MUST không làm đổi snapshot cũ.
- **FR-005**: Tổng của gốc mới MUST riêng, MUST NOT cộng vào gốc hệ thống cùng loại; báo cáo theo loại và các phân hệ khác (BĐS, tổng tài sản, hoàn chi) MUST tiếp tục nhận đúng loại.
- **FR-006**: Màn Danh mục và lịch sử danh mục MUST có bộ lọc kỳ (tháng này, tháng trước, quý này, quý trước, tùy chọn khoảng ngày, tất cả) theo ngày giao dịch; tổng, số giao dịch và danh sách MUST chỉ gồm giao dịch trong kỳ; khoảng ngày không hợp lệ MUST bị chặn (R82).
- **FR-007**: Kỳ không có giao dịch MUST hiển thị "chưa có giao dịch trong kỳ này" kèm kỳ nguồn đã ghi, MUST NOT hiển thị 0 như đã đối soát.
- **FR-008**: Báo cáo duyệt theo danh mục MUST liệt kê mọi gốc (hệ thống, tự tạo, Chưa phân loại) và danh mục con lồng nhau, mỗi mục có số giao dịch, số đối tượng liên quan (số hồ sơ người/khoản vay/BĐS khác nhau gắn vào các phần phân loại của mục), tiền vào, tiền ra (Chi tiêu và danh mục nhóm chi: chi, hoàn chi, chi ròng) (R83).
- **FR-009**: Báo cáo duyệt MUST đếm mỗi giao dịch đúng một lần ở danh mục cha, phần tách chỉ tính phần thuộc mục; MUST có kiểm đối chiếu số giao dịch gốc và tổng tiền vào/ra nguồn so với tổng các nhóm và nêu rõ khớp hay không khớp (R46).
- **FR-010**: Mỗi mục của báo cáo duyệt MUST mở được chi tiết các dòng (ngày, nội dung, vào/ra, đối tượng, trạng thái, nguồn); báo cáo MUST gồm toàn bộ giao dịch của tài khoản và độc lập bộ lọc giao diện.
- **FR-011**: Thay đổi MUST NOT đổi quy tắc tiền, kết quả snapshot/báo cáo/công nợ/BĐS/crypto/TRX đã có, MUST NOT sửa dữ liệu vận hành khi kiểm thử; snapshot đã có MUST giữ nguyên.

### Key Entities
- **Danh mục gốc tự tạo**: tên, loại (thu/chi/đầu tư), trạng thái, lịch sử thay đổi; danh mục con dưới nó.
- **Bộ lọc kỳ**: loại kỳ hoặc khoảng ngày; chỉ là trạng thái xem.
- **Dòng báo cáo theo danh mục**: danh mục, số giao dịch, số đối tượng, vào, ra, (chi ròng), chi tiết.

## Success Criteria *(mandatory)*
- **SC-001**: Tạo một gốc mới và dùng nó khi phân loại trong tối đa 4 thao tác; tổng gốc hệ thống cùng loại không bị đếm thêm (100% trường hợp thử).
- **SC-002**: Lọc tháng cho ra tổng đúng bằng tổng các dòng trong lịch sử của tháng đó ở mọi danh mục (đối chiếu khớp 100%).
- **SC-003**: Báo cáo duyệt theo danh mục khớp số giao dịch gốc và tổng tiền vào/ra nguồn ở bộ dữ liệu ví dụ; trường hợp cố ý lệch được báo "không khớp".
- **SC-004**: Từ một dòng báo cáo theo danh mục mở được dòng sao kê nguồn trong tối đa 2 thao tác.
- **SC-005**: 0 thay đổi ở snapshot, báo cáo, công nợ, BĐS, crypto, TRX đã có; checksum dữ liệu vận hành không đổi.

## Assumptions
- Loại "trung tính" không làm: nhóm chi đã nhận cả hai chiều (chi và hoàn chi), đủ cho nhu cầu hiện tại; Thạch phản hồi nếu cần loại khác.
- Gốc tự tạo nhóm chi/thu/đầu tư dùng loại phân loại tương ứng (Chi tiêu/Thu nhập/Đầu tư BĐS) ở phần ghi nhận để báo cáo theo loại và các phân hệ khác không đổi.
- Kỳ lọc theo múi giờ Việt Nam và ngày giao dịch trong sao kê.
- "Số đối tượng liên quan" đếm các hồ sơ (người/khoản vay/BĐS) khác nhau gắn vào phần phân loại; phần không có đối tượng không tính.
- Gộp danh mục để đợt sau nếu Thạch cần.
