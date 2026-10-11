# Feature Specification: Cải thiện màn Phân loại giao dịch

**Feature Branch**: `009-classification-ux`
**Created**: 2026-10-11
**Status**: Draft
**Input**: Feedback của Thạch ngày 11/10/2026 (3 yêu cầu về màn Phân loại giao dịch). Nguồn yêu cầu: R45 (chọn nhiều dòng), R50 (phân loại có đối tượng, món mới tạo ngay), R55 (cây danh mục), R21 (điều chỉnh sau duyệt có lý do) · Spec liên quan: 001 (phân loại), 008 (danh mục), 002 (đối tượng khoản vay).

**Phạm vi:** chỉ thay đổi cách nhập liệu và hiển thị ở màn Phân loại; không đổi quy tắc tiền, không đổi phân bổ, snapshot hay báo cáo đã có.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Lý do phân loại là tùy chọn (Priority: P1)
Thạch lưu phân loại mà không phải gõ lý do. Có thể gõ khi muốn ghi chú.

**Why this priority**: Lý do bắt buộc làm chậm việc phân loại hàng loạt nhiều giao dịch thông thường; Thạch đã yêu cầu bỏ ràng buộc này.

**Independent Test**: phân loại một và nhiều giao dịch với ô lý do để trống → lưu được; phân loại có lý do → lý do được lưu trong lịch sử.

**Acceptance Scenarios**:
1. **Given** hộp thoại phân loại, **When** để trống lý do và bấm lưu, **Then** phân loại được lưu và lịch sử trước/sau ghi lý do rỗng.
2. **Given** Thạch có gõ lý do, **When** lưu, **Then** lý do hiện trong lịch sử phân loại như hiện nay.
3. **Given** tài khoản đã có bản duyệt, **When** phân loại lại một dòng đã duyệt mà không gõ lý do, **Then** vẫn mở được phiên điều chỉnh và lưu; yêu cầu lý do khi **duyệt phiên bản mới** (R21) giữ nguyên.

### User Story 2 - Sắp xếp danh sách giao dịch theo số tiền (Priority: P1)
Thạch sắp xếp danh sách giao dịch theo số tiền (nhỏ → lớn, lớn → nhỏ) bên cạnh thứ tự theo ngày hiện có, để gom các giao dịch nhỏ đặc thù (thường là chi tiêu) rồi chọn và phân loại hàng loạt.

**Why this priority**: là cách Thạch tìm và xử lý nhanh nhóm giao dịch nhỏ thuộc Chi tiêu.

**Independent Test**: với danh sách có tiền vào và tiền ra nhiều mức, chọn "Số tiền nhỏ → lớn" → các dòng xếp theo giá trị tuyệt đối tăng dần; chọn 5 dòng đầu, áp Chi tiêu → chỉ 5 dòng đổi.

**Acceptance Scenarios**:
1. **Given** danh sách giao dịch, **When** chọn sắp xếp theo số tiền tăng/giảm, **Then** thứ tự theo độ lớn số tiền (không phụ thuộc chiều vào/ra), các dòng cùng số tiền giữ thứ tự theo ngày.
2. **Given** đang lọc (chưa phân loại, từ khóa) và đang có dòng được chọn, **When** đổi cách sắp xếp, **Then** bộ lọc và dòng đã chọn giữ nguyên; phân trang quay về trang đầu của thứ tự mới.
3. **Given** bất kỳ cách sắp xếp nào, **When** xem báo cáo/duyệt, **Then** báo cáo vẫn gồm toàn bộ giao dịch như cũ (sắp xếp chỉ là cách xem).

### User Story 3 - Tạo nhanh đối tượng ngay trong hộp thoại phân loại (Priority: P1)
Khi chọn danh mục, Thạch tạo nhanh "đối tượng" tại chỗ và gắn luôn vào giao dịch: người/khoản vay (Gốc vay, Lãi vay), BĐS (Đầu tư BĐS), danh mục con (Thu nhập, Chi tiêu), không phải rời hộp thoại để tạo hồ sơ rồi quay lại.

**Why this priority**: loại bỏ vòng đi-về giữa Hồ sơ liên kết/Danh mục và Phân loại; R50 đã yêu cầu món mới tạo ngay khi phân loại.

**Independent Test**: phân loại giao dịch chi cho vay: chọn Gốc vay → "Tạo nhanh" → nhập tên người (mới hoặc chọn người có sẵn) → khoản vay mới được tạo và gắn ngay; hoàn tất trong một lần lưu phân loại, không rời hộp thoại.

**Acceptance Scenarios**:
1. **Given** danh mục Gốc vay hoặc Lãi vay, **When** chọn "Tạo nhanh", **Then** có thể chọn người có sẵn hoặc gõ tên người mới, và khoản vay mới (gắn người đó) được tạo và chọn sẵn cho giao dịch.
2. **Given** danh mục Đầu tư BĐS, **When** tạo nhanh với một tên, **Then** hồ sơ BĐS mới được tạo và chọn sẵn.
3. **Given** danh mục Thu nhập hoặc Chi tiêu, **When** tạo nhanh với một tên, **Then** danh mục con mới dưới danh mục đó được tạo (theo quy tắc spec 008) và chọn sẵn.
4. **Given** tên trùng với đối tượng/danh mục đã có cùng loại, **When** tạo nhanh, **Then** bị chặn kèm lý do và đề nghị chọn cái có sẵn.
5. **Given** Thạch tạo nhanh nhưng đóng hộp thoại mà không lưu phân loại, **When** xem Hồ sơ/Danh mục, **Then** đối tượng đã tạo vẫn tồn tại (không bị xóa tự động) và có thể dùng sau.

### Edge Cases
- Phân loại hàng loạt (nhiều dòng): tạo nhanh vẫn dùng được và gắn cùng một đối tượng cho mọi dòng được chọn, trừ khi quy tắc hiện có yêu cầu gắn riêng.
- Tách một giao dịch thành nhiều phần: mỗi phần có thể tạo nhanh đối tượng riêng.
- Đổi danh mục sau khi đã chọn đối tượng: đối tượng không còn phù hợp bị bỏ chọn (R50).
- Khoản vay tạo nhanh chưa có thiết lập gốc đầu: hiển thị "cần thiết lập" ở Công nợ như hiện hành, không tự suy dư nợ.
- Sắp xếp theo số tiền khi nhiều dòng cùng số tiền hoặc số tiền bằng 0: thứ tự ổn định theo ngày.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Lưu phân loại MUST không yêu cầu lý do; lý do nếu có MUST được lưu trong lịch sử phân loại; lý do rỗng MUST hợp lệ.
- **FR-002**: Mở phiên điều chỉnh để phân loại lại dòng đã duyệt MUST không yêu cầu lý do; lý do bắt buộc khi duyệt phiên bản mới (R21) MUST giữ nguyên.
- **FR-003**: Danh sách giao dịch MUST có ba cách sắp xếp: theo ngày (mặc định hiện nay), số tiền tăng dần, số tiền giảm dần (theo giá trị tuyệt đối, bất kể vào/ra); các dòng bằng nhau MUST giữ thứ tự theo ngày.
- **FR-004**: Đổi cách sắp xếp MUST giữ nguyên bộ lọc, ô tìm kiếm và tập dòng đã chọn; MUST đưa phân trang về trang đầu; MUST NOT đổi phạm vi báo cáo hay số dòng được duyệt.
- **FR-005**: Hộp thoại phân loại MUST có "Tạo nhanh" đối tượng theo danh mục: Gốc vay/Lãi vay → khoản vay (kèm người có sẵn hoặc tên người mới), Đầu tư BĐS → BĐS, Thu nhập/Chi tiêu → danh mục con; đối tượng mới MUST được chọn sẵn sau khi tạo.
- **FR-006**: Tạo nhanh MUST áp dụng đúng quy tắc hiện có: tên 1–100 ký tự, chặn trùng, khoản vay phải gắn người, danh mục con theo quy tắc cây (≤4 cấp, không trùng tên cùng cha).
- **FR-007**: Tạo nhanh MUST là một thao tác nguyên tử (người mới và khoản vay mới cùng được tạo hoặc cùng không), lưu lịch sử audit như tạo hồ sơ/danh mục thông thường, và MUST NOT tự phân loại hay ghi tiền.
- **FR-008**: Thay đổi này MUST NOT đổi kết quả phân bổ tiền, snapshot, báo cáo, công nợ đã có; MUST NOT sửa dữ liệu vận hành khi kiểm thử.

### Key Entities
- **Phần phân loại**: danh mục, số tiền, đối tượng (người/khoản vay/BĐS), danh mục con; lý do thuộc lần lưu phân loại và là tùy chọn.
- **Đối tượng tạo nhanh**: hồ sơ khoản vay (kèm người), hồ sơ BĐS hoặc danh mục con, tạo từ hộp thoại phân loại.
- **Chế độ sắp xếp**: ngày / số tiền tăng / số tiền giảm; chỉ là trạng thái xem.

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: Phân loại một giao dịch bằng danh mục có sẵn xong trong tối đa 3 thao tác (chọn dòng, chọn danh mục, lưu), không bắt buộc gõ chữ.
- **SC-002**: Từ danh sách, gom 10 giao dịch số tiền nhỏ nhất và phân loại hàng loạt vào Chi tiêu trong tối đa 5 thao tác; chỉ đúng 10 dòng đổi, số tiền nguồn không đổi.
- **SC-003**: Tạo và gắn một khoản vay mới cho người mới ngay khi phân loại trong một hộp thoại, không rời màn, tối đa 6 thao tác.
- **SC-004**: 0 thay đổi ở snapshot, báo cáo và công nợ đã có sau triển khai (đối chiếu số liệu bộ dữ liệu giả và checksum dữ liệu vận hành).
- **SC-005**: Đổi cách sắp xếp không làm mất bộ lọc và dòng đã chọn trong 100% trường hợp thử.

## Assumptions
- "Đối tượng" ở yêu cầu của Thạch hiểu theo R50: người/khoản vay, BĐS (hồ sơ liên kết) và danh mục con (spec 008) tùy danh mục; nếu Thạch muốn khác thì chỉnh ở phiên bản sau.
- Lý do tùy chọn áp dụng cho phân loại và mở phiên điều chỉnh; lý do khi duyệt phiên bản mới vẫn bắt buộc theo R21 (chưa có yêu cầu đổi).
- Sắp xếp theo số tiền dùng giá trị tuyệt đối vì mục đích là gom khoản nhỏ bất kể chiều.
- Mặc định sắp xếp vẫn là theo ngày mới nhất trước như hiện nay.
- Chỉ VND như các đợt trước.
