# Feature Specification: Bất động sản bản đầu

**Feature Branch**: `011-realty`
**Created**: 2026-10-11
**Status**: Draft
**Input**: Thạch yêu cầu làm tiếp phần Bất động sản (11/10/2026) và đã trả lời phỏng vấn: bản đầu gồm hồ sơ cơ bản + thế chấp + góp vốn nhiều người; quyền lợi ghi bằng số tiền góp từng người; hiển thị vốn và giá trị hiện tại cạnh nhau, chênh lệch có nhãn chưa thực hiện. Nguồn yêu cầu: R18, R27, R58, R71–R73 · Spec liên quan: 001, 002, 007 (backlog tài sản), 008, 009, 010.

**Phạm vi:** màn Bất động sản cho các hồ sơ BĐS đã có; **không** gồm chung cư theo tiến độ, tổng tài sản/định giá tổng hợp, crypto (để đợt sau). Không đổi quy tắc tiền hiện có.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Xem từng BĐS với vốn đã thanh toán có nguồn (Priority: P1)
Thạch mở màn Bất động sản thấy danh sách từng BĐS: vốn đã thanh toán (tổng các giao dịch phân loại Đầu tư BĐS gắn đúng BĐS đó), liệt kê đủ các lần thanh toán và mở được dòng sao kê nguồn; chi phí gắn BĐS (giao dịch Chi tiêu gắn BĐS, có hoàn chi).

**Why this priority**: R58 — vốn mua Đất A 600 triệu phải liệt kê đủ các lần thanh toán cấu thành và truy được nguồn.

**Independent Test**: BĐS "Đất A" có ba lần thanh toán 200 + 150 + 250 triệu → hiển thị vốn 600 triệu với ba dòng nguồn; thêm một lần thanh toán mới (chờ duyệt) → vốn tăng và dòng mới ghi trạng thái chờ duyệt; BĐS chưa có giao dịch hiển thị "chưa có nguồn", không 0 giả.

**Acceptance Scenarios**:
1. **Given** BĐS có các giao dịch Đầu tư BĐS đã gắn, **When** mở màn, **Then** vốn = tổng các lần thanh toán ra trừ tiền nhận lại (nếu có), hiển thị riêng từng số.
2. **Given** BĐS, **When** mở lịch sử, **Then** thấy từng lần (ngày, tài khoản, nội dung, số tiền, chiều, trạng thái nháp/đã duyệt) và mở được dòng nguồn.
3. **Given** chi phí Chi tiêu gắn BĐS và khoản hoàn chi, **When** xem, **Then** thấy chi phí, hoàn chi và chi phí ròng riêng.
4. **Given** BĐS chưa có giao dịch nào, **When** xem, **Then** hiển thị "chưa có nguồn thanh toán" kèm kỳ nguồn đã ghi, không hiển thị 0 như đã đối soát.

### User Story 2 - Giá trị hiện tại nhập tay, hiển thị cạnh vốn (Priority: P1)
Thạch ghi giá trị hiện tại của BĐS kèm ngày và nguồn (ví dụ báo giá môi giới); có lịch sử, hủy được kèm lý do. Vốn đã thanh toán và giá trị hiện tại hiện cạnh nhau; chênh lệch ghi nhãn "chưa thực hiện", không gọi là lãi/lỗ.

**Independent Test**: vốn 600 triệu, giá trị 900 triệu (ngày, nguồn) → hiển thị cạnh nhau và "chênh lệch chưa thực hiện +300 triệu (chưa trừ chi phí và nợ, không phải lãi/lỗ)"; thêm giá trị mới thì giá trị cũ vào lịch sử; hủy giá trị mới (lý do) thì giá trị hiện tại quay về bản hiệu lực trước.

**Acceptance Scenarios**:
1. **Given** chưa có giá trị, **When** xem, **Then** hiển thị "chưa có giá trị hiện tại" và không có chênh lệch.
2. **Given** nhiều giá trị, **When** xem, **Then** giá trị hiện tại là bản hiệu lực có ngày mới nhất; lịch sử hiện đủ bản (cả đã hủy).
3. **Given** nhập giá trị thiếu ngày hoặc nguồn, **When** lưu, **Then** bị chặn kèm lý do.

### User Story 3 - Thế chấp: liên kết BĐS với khoản vay (Priority: P2)
Thạch ghi một BĐS đang thế chấp cho một khoản vay (đã có trong Công nợ) kèm mục đích dùng tiền vay. Hệ thống không coi tiền vay là thu nhập và không trừ nợ khỏi giá trị BĐS lần hai.

**Independent Test**: liên kết "Đất B" với khoản vay "Vay NH 1" mục đích "mua căn hộ"; hiển thị khoản vay và dư gốc theo dữ liệu công nợ; giá trị BĐS không bị trừ nợ; liên kết khoản vay đó với BĐS thứ hai khi liên kết đầu còn hiệu lực bị chặn; kết thúc liên kết (có lý do) thì liên kết được BĐS khác.

**Acceptance Scenarios**:
1. **Given** khoản vay chưa thế chấp, **When** liên kết với BĐS, **Then** hiện khoản vay, mục đích, dư gốc theo dữ liệu công nợ (hoặc "chưa xác định" nếu khoản vay chưa thiết lập).
2. **Given** khoản vay đã thế chấp BĐS khác còn hiệu lực, **When** liên kết, **Then** bị chặn.
3. **Given** liên kết hiệu lực, **When** kết thúc kèm lý do, **Then** liên kết vào lịch sử, không xóa.

### User Story 4 - Góp vốn nhiều người (Priority: P2)
Với BĐS góp vốn, Thạch ghi số tiền mỗi người góp (người là hồ sơ người) kèm bằng chứng; các số hiển thị riêng, không quy đổi ra tỷ lệ, không suy quyền lợi từ tiền đã chuyển. Phần Thạch tự góp là vốn đã thanh toán có nguồn từ sao kê.

**Independent Test**: BĐS "Đất C" có người A góp 300 triệu, B góp 200 triệu (nhập tay, có bằng chứng) và vốn của Thạch 500 triệu từ sao kê → hiển thị ba số riêng, không có cột phần trăm; hủy một khoản góp (lý do) thì loại khỏi tổng người góp nhưng giữ lịch sử.

**Acceptance Scenarios**:
1. **Given** BĐS, **When** ghi khoản góp của một người với số tiền, bằng chứng, **Then** hiển thị dưới "Người khác góp" cùng tổng.
2. **Given** khoản góp thiếu bằng chứng hoặc người không phải hồ sơ người, **When** lưu, **Then** bị chặn.
3. **Given** bất kỳ trường hợp nào, **When** xem, **Then** không có tỷ lệ phần trăm hay "quyền lợi" suy ra tự động.

### Edge Cases
- BĐS chưa có thiết lập nào: vẫn hiển thị với "chưa có nguồn / chưa có giá trị".
- Giá trị hiện tại ngày trước các giao dịch: chấp nhận (là dữ liệu nhập tay có ngày).
- Giao dịch Đầu tư BĐS là tiền vào (nhận lại/bán): hiển thị riêng là "tiền nhận lại", không suy là lãi.
- Khoản vay thế chấp chưa thiết lập gốc đầu: hiển thị "cần thiết lập", không suy dư nợ.
- Hủy giá trị hoặc khoản góp đã dùng làm căn cứ: không xóa, lịch sử giữ cả bản hủy.
- Chênh lệch chưa thực hiện không bao gồm chi phí, nợ thế chấp hay thuế; luôn kèm nhãn.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Màn Bất động sản MUST liệt kê mọi hồ sơ BĐS, mỗi BĐS hiển thị riêng: vốn đã thanh toán (tiền ra Đầu tư BĐS), tiền nhận lại (tiền vào Đầu tư BĐS), chi phí gắn BĐS (Chi tiêu), hoàn chi gắn BĐS (R58, spec 010).
- **FR-002**: Mỗi BĐS MUST có lịch sử các lần thanh toán/chi phí với ngày, tài khoản, nội dung, số tiền, chiều, trạng thái (nháp/đã duyệt) và lối mở dòng sao kê nguồn; tổng MUST truy được về đúng tập dòng liệt kê, mỗi giao dịch đếm đúng phần thuộc BĐS.
- **FR-003**: BĐS chưa có giao dịch MUST hiển thị trạng thái thiếu dữ liệu kèm kỳ nguồn đã ghi, MUST NOT hiển thị 0 như đã đối soát.
- **FR-004**: Giá trị hiện tại MUST do người dùng nhập tay với số tiền VND nguyên dương, ngày và nguồn bắt buộc; có lịch sử; hủy cần lý do và không xóa; giá trị hiện tại là bản hiệu lực có ngày mới nhất.
- **FR-005**: Vốn và giá trị hiện tại MUST hiển thị cạnh nhau; chênh lệch (giá trị hiện tại − vốn đã thanh toán ròng) MUST mang nhãn "chưa thực hiện, chưa trừ chi phí/nợ, không phải lãi/lỗ"; không có giá trị thì MUST NOT có chênh lệch (R73).
- **FR-006**: Thế chấp MUST liên kết một BĐS với một khoản vay đã có, kèm mục đích dùng tiền vay (bắt buộc); một khoản vay chỉ có tối đa một liên kết hiệu lực; kết thúc liên kết cần lý do, giữ lịch sử.
- **FR-007**: Hệ thống MUST hiển thị dư gốc khoản vay thế chấp theo dữ liệu công nợ (hoặc "chưa xác định"/"cần thiết lập"), MUST NOT coi tiền vay là thu nhập và MUST NOT trừ nợ khỏi giá trị BĐS hay chênh lệch.
- **FR-008**: Góp vốn MUST ghi người (hồ sơ người), số tiền VND nguyên dương, bằng chứng bắt buộc, ngày tùy chọn; hiển thị riêng từng người và tổng, kèm vốn của Thạch từ sao kê; MUST NOT tính tỷ lệ phần trăm hay suy quyền lợi từ số tiền đã chuyển (R72, R27).
- **FR-009**: Mọi thay đổi (giá trị, thế chấp, góp vốn) MUST có lịch sử, hủy có lý do, không xóa bản ghi.
- **FR-010**: Thay đổi MUST NOT đổi kết quả báo cáo, snapshot, công nợ, bảng kê lãi hay danh mục đã có; MUST NOT sửa dữ liệu vận hành khi kiểm thử.

### Key Entities
- **Hồ sơ BĐS**: đã có (loại BĐS); giao dịch gắn qua phần phân loại Đầu tư BĐS / Chi tiêu có hồ sơ BĐS.
- **Giá trị hiện tại**: BĐS, số tiền, ngày, nguồn, ghi chú, trạng thái, lý do hủy.
- **Liên kết thế chấp**: BĐS, khoản vay, mục đích, trạng thái, lý do kết thúc.
- **Khoản góp vốn**: BĐS, người, số tiền, ngày, bằng chứng, trạng thái, lý do hủy.

## Success Criteria *(mandatory)*
- **SC-001**: Với "Đất A" ba lần thanh toán 200 + 150 + 250 triệu, màn hiển thị vốn 600 triệu và đủ ba dòng, mở được dòng nguồn trong tối đa 2 thao tác từ tổng.
- **SC-002**: Vốn, giá trị hiện tại (ngày, nguồn) và chênh lệch có nhãn hiện cùng một màn hình cho mỗi BĐS; 0 chỗ gọi chênh lệch là lãi/lỗ.
- **SC-003**: Một khoản vay chỉ thế chấp được một BĐS hiệu lực tại một thời điểm (100% thử nghiệm); giá trị và chênh lệch BĐS không bị trừ nợ.
- **SC-004**: Số tiền góp từng người hiển thị riêng, 0 tỷ lệ phần trăm hoặc quyền lợi suy ra tự động.
- **SC-005**: 0 thay đổi ở snapshot, báo cáo, công nợ và danh mục đã có; checksum dữ liệu vận hành không đổi.

## Assumptions
- Quyết định phạm vi R71–R73 do Thạch trả lời phỏng vấn ngày 11/10/2026.
- BĐS được tạo bằng cách đã có (Hồ sơ liên kết hoặc tạo nhanh khi phân loại); màn này có thêm lối tạo BĐS nhanh.
- Chỉ VND; chung cư theo tiến độ, tổng tài sản/định giá tổng hợp, crypto để đợt sau (spec 007).
- Giá trị hiện tại là dữ liệu nhập tay, không lấy tự động từ nguồn giá nào.
- "Vốn đã thanh toán" chỉ tính từ giao dịch ngân hàng đã phân loại và gắn BĐS; khoản thanh toán chưa phân loại không nằm trong vốn (hiển thị cảnh báo nếu còn dòng chưa phân loại trong tài khoản).
