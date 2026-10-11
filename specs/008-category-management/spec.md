# Feature Specification: Quản lý danh mục và lịch sử từng danh mục

**Feature Branch**: `008-category-management`
**Created**: 2026-10-11
**Status**: Draft (chưa plan/tasks)
**Input**: Thạch hỏi "phần quản lý danh mục đang ở đâu" (11/10/2026). Hiện danh mục là danh sách cố định trong mã; chưa có nơi thêm/sửa danh mục, chưa có màn xem lịch sử và tổng từng danh mục. Nguồn yêu cầu: R06, R45, R46, R50, R55, R56, R58 · Tiêu chí: ACCEPTANCE A06, A41, A46, A51, A54 · Spec liên quan: 001 (phân loại), 002 (đối tượng khoản vay).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Quản lý cây danh mục (Priority: P1)
Thạch có một nơi để xem toàn bộ cây danh mục, tạo danh mục gốc/con, sửa tên, mô tả, danh mục cha và lưu trữ danh mục không dùng nữa; các danh mục nghiệp vụ gốc (Thu nhập, Chi tiêu, Gốc vay, Lãi vay, Đầu tư BĐS, Chuyển nội bộ) giữ tên và cấp cha, chỉ sửa mô tả (R55).

**Why this priority**: là phần R06 còn thiếu; phân loại hiện bị khóa vào danh sách cứng nên không thêm được việc/đối tượng mới như Đất E.

**Independent Test**: tạo "Mua BĐS → Đất E", đổi tên thành "Đất F", dùng ngay khi phân loại một giao dịch; thử tạo trùng tên, đặt danh mục làm cha của chính con nó (vòng lặp) — đều bị chặn kèm lý do.

**Acceptance Scenarios**:
1. **Given** danh mục gốc "Đầu tư BĐS", **When** tạo con "Đất E", **Then** "Đất E" chọn được khi phân loại và gắn tên tài sản.
2. **Given** danh mục đã dùng trong bản duyệt, **When** đổi tên, **Then** snapshot cũ giữ tên lúc duyệt, màn hiện hành hiện tên mới.
3. **Given** hai danh mục cùng cấp, **When** đặt tên trùng hoặc tạo vòng cha-con, **Then** bị chặn.
4. **Given** danh mục có giao dịch, **When** Thạch muốn bỏ, **Then** chỉ lưu trữ (ẩn khỏi lựa chọn mới), không xóa lịch sử.

### User Story 2 - Lịch sử và tổng từng danh mục truy nguyên được (Priority: P1)
Mở một danh mục thấy tổng tiền vào, tổng tiền ra, chênh vào–ra, nguyên tệ, số giao dịch, và danh sách giao dịch cấu thành (kể cả của danh mục con) với mã nguồn, ngày, tài khoản, nội dung, đối tượng, trạng thái, vào/ra; mở được dòng nguồn trong sao kê (R56, R58).

**Why this priority**: yêu cầu chung của Thạch — mọi số tổng phải truy về đúng tập dòng gốc.

**Independent Test**: danh mục cha có hai con: tổng cha = tổng các dòng của cả cây, mỗi dòng đếm một lần; tách riêng nguyên tệ; danh mục chưa có giao dịch hiển thị lịch sử rỗng và "thiếu dữ liệu", không số 0 giả.

**Acceptance Scenarios**:
1. **Given** danh mục cha có con, **When** xem cha, **Then** thấy giao dịch của cả con, mỗi dòng một lần, kèm tổng vào/ra/chênh riêng từng nguyên tệ.
2. **Given** giao dịch tách thành nhiều phần ở nhiều danh mục, **When** xem từng danh mục, **Then** chỉ tính phần thuộc danh mục đó, tổng các phần khớp tiền nguồn.
3. **Given** danh mục chưa có giao dịch, **When** mở, **Then** lịch sử rỗng và nêu rõ chưa có nguồn, không tạo giao dịch giả.

### User Story 3 - Dùng danh mục khi phân loại và kiểm toàn đợt (Priority: P2)
Danh sách danh mục khi phân loại lấy từ cây; phân loại hàng loạt và từng dòng vẫn chỉ đổi dòng được chọn; báo cáo duyệt đếm mỗi giao dịch đúng một lần ở nhóm trực tiếp (R45, R46, R50).

**Independent Test**: chọn 5 dòng, áp một danh mục con: chỉ 5 dòng đổi, tiền nguồn không đổi; báo cáo toàn đợt không trùng/thiếu.

### Edge Cases
- Đổi danh mục của giao dịch đã duyệt → qua điều chỉnh có lý do, không sửa snapshot (R21).
- Danh mục lưu trữ đang gắn giao dịch cũ vẫn hiển thị trong lịch sử, không chọn được cho dòng mới.
- Chuyển danh mục con sang cha khác: lịch sử các giao dịch đã duyệt giữ đường dẫn cũ trong snapshot.
- Danh mục cổ phiếu (R24) và Shop pending: không tạo sẵn; người dùng có thể tự tạo nhưng không có nghiệp vụ riêng.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Hệ thống MUST cho tạo danh mục gốc/con, sửa tên, mô tả, danh mục cha của danh mục tự tạo, và lưu trữ; MUST ngăn tên trùng cùng cấp và vòng lặp cha-con (R55).
- **FR-002**: Danh mục nghiệp vụ gốc MUST giữ tên và cấp cha; chỉ sửa mô tả (R55).
- **FR-003**: Danh mục MUST có lịch sử thay đổi (tên, cha, trạng thái, lý do); snapshot đã duyệt MUST giữ tên và đường dẫn tại thời điểm duyệt (R21).
- **FR-004**: Quy tắc nghiệp vụ liên kết đối tượng (khoản vay, tài sản) MUST kế thừa nhóm gốc của danh mục; đổi danh mục MUST xóa liên kết không còn phù hợp (R50).
- **FR-005**: Mỗi danh mục MUST có màn lịch sử gồm các giao dịch cấu thành (kể cả của con) với mã nguồn, ngày, tài khoản, nội dung, đối tượng, trạng thái, vào/ra theo nguyên tệ và lối mở dòng nguồn (R58).
- **FR-006**: Tổng của danh mục MUST gồm tổng vào, tổng ra, chênh vào–ra, số giao dịch theo từng nguyên tệ; MUST truy được về đúng tập dòng gốc; MUST NOT đếm đôi khi xem nhóm cha; hoàn tiền MUST NOT bị ẩn do bù trừ (R56, R58).
- **FR-007**: Danh mục chưa có nguồn MUST hiển thị lịch sử rỗng kèm trạng thái thiếu dữ liệu, MUST NOT tạo giao dịch giả hoặc mặc định bằng không (R58).
- **FR-008**: Lựa chọn danh mục khi phân loại MUST lấy từ cây hiện hành, loại danh mục đã lưu trữ khỏi lựa chọn mới; phân loại không được đổi tiền nguồn (R06, R45).
- **FR-009**: Thay đổi này MUST NOT sửa dữ liệu tài chính đã ghi, MUST NOT đổi kết quả báo cáo, snapshot hay công nợ đã có; dữ liệu cũ dùng danh mục cố định MUST tiếp tục hiển thị đúng sau khi chuyển sang cây.

### Key Entities
- **Danh mục**: tên, mô tả, danh mục cha, loại (hệ thống/tự tạo), trạng thái (hoạt động/lưu trữ), lịch sử thay đổi.
- **Phần phân loại của giao dịch**: tham chiếu danh mục (và đối tượng), tiền của phần.
- **Tổng danh mục**: dẫn xuất từ các phần phân loại, theo nguyên tệ.

## Success Criteria *(mandatory)*
- **SC-001**: Tạo, đổi tên và dùng một danh mục mới khi phân loại trong tối đa 3 thao tác, không cần sửa mã.
- **SC-002**: Với mọi danh mục, tổng hiển thị bằng đúng tổng các dòng liệt kê (đối chiếu khớp 100% trên bộ dữ liệu giả); mỗi giao dịch đếm một lần ở danh mục cha.
- **SC-003**: Từ một số tổng bất kỳ mở được dòng sao kê nguồn trong tối đa 2 thao tác.
- **SC-004**: 0 thay đổi ở snapshot, báo cáo và công nợ đã có sau khi chuyển danh mục cố định sang cây (đối chiếu số trước/sau và checksum dữ liệu vận hành).
- **SC-005**: Danh mục rỗng luôn hiển thị trạng thái thiếu dữ liệu, không bao giờ hiển thị 0 như đã đối soát.

## Assumptions
- Danh mục cổ phiếu và Shop vẫn pending (R24, R28): không tạo sẵn.
- Đối tượng tài sản đầy đủ (vốn, định giá) thuộc spec 007; ở đây danh mục con của "Đầu tư BĐS" chỉ là đối tượng chọn được khi phân loại (R55).
- Lưu trữ thay cho xóa vì mọi danh mục đã có giao dịch phải giữ lịch sử.
- Báo cáo đợt (R46) tiếp tục đếm mỗi giao dịch ở nhóm trực tiếp; tổng gộp cây nhiều cấp chỉ hiện ở màn danh mục.
