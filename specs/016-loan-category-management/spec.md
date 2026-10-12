# Feature Specification: Quản lý khoản vay và danh mục

**Feature Branch**: `016-loan-category-management`
**Created**: 2026-10-12
**Status**: Draft
**Input**: Thạch phỏng vấn 12/10/2026 (R87–R93 trong `PRODUCT-SPEC.md`): một người có nhiều khoản vay với lãi và ngày riêng; danh mục con của Gốc/Lãi/Đầu tư là tùy chọn; chọn khoản vay dễ đọc; đối tượng chỉ cho khoản vay và BĐS; màn Kiểm tra gom theo gốc + đối tượng; chuyển cả khoản vay sang danh mục khác (ví dụ Loans › Long debt); xóa hẳn danh mục chưa dùng.

**Tham chiếu**: spec 001 (nguồn), 002 (công nợ), 008 (danh mục), 009 (phân loại), 010 (hoàn chi), 014 (danh mục hoàn thiện), 015 (màn Kiểm tra). Không đổi quy tắc tiền, snapshot đã lưu, báo cáo đã duyệt.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Chọn đúng khoản vay khi phân loại (Priority: P1)
Khi phân loại tiền cho vay/lãi, Thạch chọn **người**, rồi chọn **một trong các khoản vay của người đó** hoặc **tạo khoản mới ngay trong ô chọn**; tên khoản vay hiển thị đủ để phân biệt, không còn chữ kỹ thuật.

**Why this priority**: một người có nhiều khoản vay (R88–R89); chọn nhầm khoản làm sai công nợ và lãi.

**Independent Test**: Kết có hai khoản vay (5tr ngày 20, 10tr ngày 25): phân loại một giao dịch gốc → chọn Kết → hiện đúng hai khoản với tên "Kết · 20/09/2026 · gốc 5.000.000 · dư 5.000.000" (và khoản còn lại), chọn khoản thứ hai; hoặc tạo khoản thứ ba mà không rời hộp thoại.

**Acceptance Scenarios**:
1. **Given** phân loại Gốc vay hoặc Lãi vay, **When** chọn người, **Then** chỉ hiện các khoản vay của người đó; chọn người có đúng một khoản thì khoản đó được chọn sẵn (vẫn đổi được).
2. **Given** người chưa có khoản vay nào, **When** chọn người, **Then** chỉ có lựa chọn tạo khoản mới.
3. **Given** danh sách khoản vay, **When** xem, **Then** mỗi khoản có dạng "người · ngày · gốc · dư hiện tại" (khoản chưa thiết lập ghi rõ "chưa thiết lập gốc"); không có chữ PERSON/LOAN/PROPERTY ở bất kỳ ô chọn đối tượng nào.
4. **Given** hệ thống gợi ý, **When** có nhiều khoản, **Then** không tự gộp hay tự chọn thay Thạch (trừ trường hợp đúng một khoản).
5. **Given** tạo khoản mới trong ô chọn, **When** lưu, **Then** khoản vay thuộc đúng người, tên theo quy tắc tên hiện có, và được chọn cho giao dịch đang phân loại.

### User Story 2 - Đối tượng chỉ cho khoản vay và BĐS (Priority: P1)
Thu nhập và Chuyển nội bộ không gắn đối tượng; Chi tiêu chỉ gắn khoản vay hoặc BĐS khi liên quan (chi hộ khoản vay spec 004/010, chi phí BĐS spec 011), không bao giờ gắn trực tiếp hồ sơ người; Gốc/Lãi gắn khoản vay; Đầu tư gắn BĐS. Danh mục con là tùy chọn ở mọi loại.

**Why this priority**: R87, R91 — tránh "danh mục con trùng tên người" và gắn người cho chi tiêu.

**Independent Test**: lưu Thu nhập kèm đối tượng, hoặc Chi tiêu kèm hồ sơ người → bị từ chối; Chi tiêu kèm khoản vay/BĐS vẫn lưu được (hành vi cũ) với thông báo rõ; Gốc vay không chọn danh mục con → lưu được; ô đối tượng không hiện khi loại là Chi tiêu/Thu nhập.

**Acceptance Scenarios**:
1. **Given** loại Thu nhập, Chuyển nội bộ hoặc Chưa phân loại có kèm đối tượng, hoặc Chi tiêu kèm hồ sơ người, **When** lưu, **Then** bị chặn; giao diện không hiện ô đối tượng cho Thu nhập/Chuyển nội bộ (Chi tiêu chọn khoản vay hoặc BĐS, không chọn người).
2. **Given** loại Gốc/Lãi/Đầu tư, **When** lưu không chọn danh mục con, **Then** lưu được nếu đã có đối tượng hợp lệ.
3. **Given** phân loại đã lưu trước đây có đối tượng ở loại không còn cho phép, **When** xem các màn, **Then** hiển thị như cũ, không bị đổi hay mất (chỉ chặn lưu mới).

### User Story 3 - Màn Kiểm tra gom theo gốc + đối tượng (Priority: P1)
Với giao dịch có đối tượng, màn Kiểm tra gom nhóm theo **danh mục của khoản vay/BĐS** (gốc hoặc nhóm đang gắn, xem Story 4) + **đối tượng**; danh mục con của giao dịch chỉ hiện làm nhãn trên dòng. Giao dịch không có đối tượng giữ gom theo đường dẫn danh mục.

**Why this priority**: R92 — hai nhóm "Kết" trước đây tách chỉ vì danh mục con.

**Independent Test**: dữ liệu có 4 giao dịch Gốc vay · Khoản Kết không danh mục con và 1 giao dịch cùng khoản có danh mục con "Kết" → một nhóm "Gốc vay · Khoản Kết" 5 giao dịch, giao dịch có danh mục con mang nhãn "Gốc vay › Kết".

**Acceptance Scenarios**:
1. **Given** giao dịch cùng khoản vay, **When** xem, **Then** cùng một nhóm dù danh mục con khác nhau; mỗi dòng giữ nhãn danh mục con (nếu có).
2. **Given** giao dịch không có đối tượng, **When** xem, **Then** nhóm theo đường dẫn danh mục như spec 015.
3. **Given** tổng nhóm và kiểm khớp, **When** xem, **Then** vẫn khớp số giao dịch và tiền với sao kê.

### User Story 4 - Chuyển cả khoản vay sang danh mục khác (Priority: P2)
Khoản vay có một "nhóm danh mục" (mặc định Gốc vay). Thạch chuyển cả khoản sang danh mục khác cùng loại Gốc vay (ví dụ Loans › Long debt) bằng một thao tác có **lý do và ngày**; mọi giao dịch **Gốc vay** của khoản đó xuất hiện dưới danh mục mới ở các màn Danh mục và Kiểm tra; dư gốc, lãi, công nợ không đổi; lịch sử chuyển được giữ.

**Why this priority**: R93 — Thạch tự quyết khoản nào thành nợ dài hạn; làm hàng loạt từng giao dịch là không thực tế.

**Independent Test**: khoản "Khoản Kết" có 5 giao dịch gốc; chuyển sang "Long debt" với lý do → tổng danh mục Long debt = tổng gốc của khoản, Gốc vay gốc không còn đếm khoản đó; dư gốc/phải thu của Kết không đổi; lịch sử hiện lần chuyển; snapshot cũ không đổi.

**Acceptance Scenarios**:
1. **Given** khoản vay và danh mục đích cùng loại Gốc vay đang hoạt động, **When** chuyển kèm lý do và ngày, **Then** thành công và ghi lịch sử (trước, sau, ngày, lý do, thời điểm ghi).
2. **Given** danh mục đích khác loại, đã lưu trữ hoặc thiếu lý do/ngày, **When** chuyển, **Then** bị chặn kèm thông báo rõ.
3. **Given** khoản đã chuyển, **When** xem Danh mục/Kiểm tra, **Then** giao dịch Gốc vay của khoản nằm dưới danh mục mới (kể cả giao dịch phát sinh sau); giao dịch Lãi vay vẫn ở Lãi vay.
4. **Given** chuyển về lại Gốc vay hoặc sang danh mục khác, **When** lưu, **Then** được phép và thêm một dòng lịch sử.
5. **Given** snapshot/báo cáo đã duyệt trước đó, **When** xem, **Then** không đổi.
6. **Given** danh mục đang có khoản vay gắn, **When** lưu trữ hoặc xóa, **Then** bị chặn (xem Story 5).

### User Story 5 - Xóa hẳn danh mục chưa từng dùng (Priority: P2)
Danh mục chưa từng được dùng (không giao dịch, không lịch sử phân loại, không khoản vay đang/đã gắn, không danh mục con) có thể xóa hẳn kèm lý do; danh mục đã từng dùng chỉ lưu trữ.

**Why this priority**: R93 — dọn danh mục tạo nhầm.

**Independent Test**: tạo "Thử" rồi xóa → biến mất khỏi cây và có bản ghi xóa; tạo danh mục, phân loại một giao dịch rồi phân loại lại sang nơi khác → vẫn không xóa được (đã từng dùng), chỉ lưu trữ.

**Acceptance Scenarios**:
1. **Given** danh mục chưa dùng và không có con, **When** xóa kèm lý do, **Then** xóa hẳn khỏi cây và ghi một bản ghi xóa (tên, đường dẫn, lý do, thời điểm).
2. **Given** danh mục đã từng được dùng (kể cả bị phân loại lại sau đó), có con, hoặc có khoản vay đã/đang gắn, **When** xóa, **Then** bị chặn và gợi ý lưu trữ.
3. **Given** danh mục gốc hệ thống, **When** xóa, **Then** không cho.

### Edge Cases
- Khoản vay chưa thiết lập gốc: vẫn chọn được, tên ghi "chưa thiết lập gốc", dư không có số.
- Người trùng tên: tên khoản vay vẫn khác nhau nhờ ngày/gốc; nếu vẫn trùng toàn bộ thì thêm hậu tố số thứ tự như quy tắc hiện có.
- Chuyển khoản vay khi danh mục đích có danh mục con: chuyển vào đúng danh mục được chọn, không tự chọn con.
- Giao dịch Gốc vay tách nhiều phần: chỉ phần Gốc vay của khoản đi theo khoản vay.
- Danh mục đích bị lưu trữ sau khi đã gắn: vẫn hiển thị khoản dưới danh mục đó (nhãn lưu trữ); chặn lưu trữ khi còn khoản gắn đang hoạt động.
- BĐS không có "nhóm danh mục" riêng trong đợt này.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001** (R88): chọn đối tượng cho Gốc/Lãi theo hai bước người → khoản vay của người đó; tạo khoản mới ngay trong ô chọn; không tự gộp.
- **FR-002** (R89): tên hiển thị khoản vay "người · ngày · gốc · dư hiện tại", không hiện loại hồ sơ bằng chữ kỹ thuật ở mọi ô chọn đối tượng.
- **FR-003** (R91): chặn lưu Thu nhập/Chuyển nội bộ/Chưa phân loại có đối tượng và mọi phân loại kèm hồ sơ người; Gốc/Lãi chỉ khoản vay, Đầu tư chỉ BĐS, Chi tiêu khoản vay hoặc BĐS; dữ liệu cũ không bị đổi.
- **FR-004** (R87): danh mục con tùy chọn với Gốc/Lãi/Đầu tư; không ép chọn.
- **FR-005** (R92): màn Kiểm tra gom giao dịch có đối tượng theo (danh mục hiệu lực của khoản + đối tượng); danh mục con của giao dịch là nhãn dòng; giao dịch không đối tượng giữ gom theo đường dẫn.
- **FR-006** (R93): thao tác chuyển khoản vay sang danh mục Gốc vay khác (lý do, ngày bắt buộc), ghi lịch sử, không đổi dư gốc/lãi/công nợ/snapshot.
- **FR-007**: sau chuyển, mọi tổng theo danh mục, lịch sử danh mục, báo cáo duyệt theo danh mục và màn Kiểm tra dùng danh mục hiệu lực của khoản cho phần Gốc vay; phần Lãi vay không đổi.
- **FR-008** (R93): xóa hẳn danh mục chưa từng dùng kèm lý do và bản ghi xóa; chặn nếu đã dùng, có con, có khoản vay gắn hoặc là gốc hệ thống.
- **FR-009**: lưu trữ danh mục bị chặn khi còn khoản vay đang gắn ở danh mục đó.
- **FR-010**: tất cả thao tác mới qua cùng cơ chế ghi sự kiện, sao lưu/khôi phục như các thao tác hiện có; đọc không đổi dữ liệu.

### Key Entities
- **Khoản vay**: hồ sơ hiện có (thuộc một người) bổ sung "danh mục nhóm" (mặc định Gốc vay) và lịch sử chuyển nhóm.
- **Lần chuyển nhóm**: danh mục trước, danh mục sau, ngày, lý do, thời điểm ghi.
- **Bản ghi xóa danh mục**: tên, đường dẫn, lý do, thời điểm.

## Success Criteria *(mandatory)*

- **SC-001**: chọn một trong hai khoản vay của cùng người và phân loại xong ≤ 4 thao tác, không thao tác nào tạo nhầm khoản.
- **SC-002**: dữ liệu mẫu hai nhóm "Kết" gộp thành một nhóm; tổng nhóm và kiểm khớp với sao kê vẫn đúng 100%.
- **SC-003**: sau khi chuyển một khoản vay, tổng danh mục đích tăng đúng bằng tổng gốc của khoản, danh mục cũ giảm tương ứng, và dư gốc/phải thu không đổi.
- **SC-004**: không phân loại mới nào lưu được cho Thu nhập có đối tượng hoặc gắn trực tiếp hồ sơ người; danh mục đã dùng không bao giờ bị xóa hẳn.
- **SC-005**: dữ liệu `outputs/p01-user-trial` không đổi (so sánh SHA256) trong suốt kiểm thử.

## Assumptions
- Chuyển nhóm chỉ áp dụng phần **Gốc vay**; Lãi vay giữ ở cây Lãi vay vì khác loại (Thạch nói "mọi giao dịch của khoản"; đề xuất này tránh trộn loại, có thể mở rộng sau nếu Thạch muốn).
- "Ngày" của lần chuyển là ngày Thạch ghi nhận quyết định; không đổi cách tính tổng theo kỳ (mọi giao dịch của khoản đi theo danh mục hiện tại).
- "Gốc" trong tên khoản vay = gốc đầu mốc + tổng gốc đã giải ngân theo chiều của khoản; "dư" = dư gốc hiện tại của Công nợ.
- Không thêm loại/kỳ hạn khoản vay (R90).
- Chỉ VND.
