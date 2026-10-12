# Feature Specification: Màn Kiểm tra phân loại

**Feature Branch**: `015-classification-review`
**Created**: 2026-10-12
**Status**: Draft
**Input**: Thạch muốn sau khi phân loại một lượt giao dịch có thể rà lại giao dịch đã vào danh mục nào và gắn đúng đối tượng chưa; đã xem bản nháp hai lần và xác nhận phạm vi mặc định cả tài khoản, ưu tiên khoản vừa phân loại lên đầu, hiển thị kiểu sao kê ngân hàng và cần quan sát tổng. Nguồn yêu cầu: R46, R50, R58, R83, R84–R86 · Spec liên quan: 001, 008, 009, 010, 014.

**Phạm vi:** màn **chỉ xem**, tính từ dữ liệu phân loại sẵn có. Không sửa phân loại, không nút "đã kiểm", không đổi quy tắc tiền, snapshot hay báo cáo.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Rà lại phân loại theo nhóm, giao dịch hiện đủ (Priority: P1)
Thạch mở màn Kiểm tra phân loại và thấy các giao dịch được gom theo danh mục; giao dịch có gắn đối tượng (người, khoản vay, BĐS) được gom thêm theo đối tượng ("Gốc vay · Kết"). Mỗi nhóm liệt kê **tất cả** giao dịch của nó, mặc định mở sẵn.

**Why this priority**: là mục đích chính của Thạch (R84): kiểm tra phân loại có đúng ý chưa.

**Independent Test**: ba giao dịch 24/09 gắn khoản vay "Kết" (-500.000.000, +200.000.000, +300.000.000) → nhóm "Gốc vay · Kết" hiển thị 3 giao dịch, vào 500.000.000, ra 500.000.000, ròng 0; nhóm Chi tiêu › Ăn uống hiển thị đủ 12 giao dịch của nó.

**Acceptance Scenarios**:
1. **Given** giao dịch đã phân loại, **When** mở màn, **Then** mỗi danh mục (đường dẫn danh mục con) là một nhóm, kèm số giao dịch và tổng.
2. **Given** giao dịch phân loại có đối tượng, **When** xem, **Then** nằm ở nhóm "Danh mục · Đối tượng" riêng (ví dụ "Gốc vay · Kết"), mỗi đối tượng một nhóm.
3. **Given** giao dịch tách nhiều phần ở nhiều nhóm, **When** xem, **Then** xuất hiện ở mỗi nhóm với số tiền phần của nhóm đó và ghi chú đây là phần của giao dịch tổng.
4. **Given** mọi nhóm, **When** mở màn, **Then** tất cả giao dịch hiển thị sẵn (không cần bấm), có nút thu gọn/mở tất cả.
5. **Given** nhóm Chưa phân loại, **When** xem, **Then** liệt kê riêng các giao dịch chưa phân loại.

### User Story 2 - Khoản vừa phân loại lên đầu (Priority: P1)
Phạm vi mặc định là cả tài khoản; các nhóm và các dòng trong nhóm được sắp theo thời điểm phân loại mới nhất trước, để Thạch thấy ngay việc mình vừa làm. Có thể chọn "24 giờ qua" hoặc một khoảng ngày để thu hẹp.

**Why this priority**: R85 — Thạch thường xuyên rà lại việc vừa phân loại.

**Independent Test**: phân loại ba giao dịch cho "Kết" sau khi đã có nhóm Chi tiêu từ trước → nhóm "Gốc vay · Kết" nằm trên nhóm Chi tiêu; trong nhóm, dòng vừa phân loại nằm trên dòng cũ; chọn "24 giờ qua" chỉ còn các giao dịch phân loại trong 24 giờ.

**Acceptance Scenarios**:
1. **Given** nhiều nhóm phân loại ở các thời điểm khác nhau, **When** mở màn, **Then** nhóm có lần phân loại mới nhất nằm trên cùng; Chưa phân loại nằm cuối.
2. **Given** các dòng trong cùng nhóm, **When** xem, **Then** dòng phân loại gần nhất nằm trên, hòa thì theo ngày giao dịch mới nhất.
3. **Given** chọn "24 giờ qua", **When** áp dụng, **Then** chỉ gồm giao dịch có lần phân loại trong 24 giờ gần nhất (Chưa phân loại không gồm).
4. **Given** chọn khoảng ngày, **When** áp dụng, **Then** chỉ gồm giao dịch có ngày trong khoảng (hai đầu bao gồm); ngày sai hoặc kết thúc trước bắt đầu bị chặn.
5. **Given** giao dịch phân loại gần đây, **When** xem, **Then** có dấu "Mới" để nhận ra.

### User Story 3 - Quan sát tổng kiểu sao kê ngân hàng (Priority: P1)
Mỗi dòng giao dịch hiển thị như sao kê: ngày kèm mã tham chiếu, nội dung kèm nút "Xem nguồn · n liên kết", số tiền (ra/vào), trạng thái phân loại. Có thanh tóm tắt và tổng cuối trang để Thạch quan sát tổng và kiểm khớp.

**Why this priority**: R86 — Thạch chỉ quan tâm tên danh mục, giao dịch kiểu sao kê và tổng.

**Independent Test**: tài khoản 53 giao dịch → thanh tóm tắt hiển thị đã phân loại 50/53, chưa phân loại 3, tổng vào, tổng ra, chênh; cuối trang tổng toàn bộ; kiểm đối chiếu báo khớp số giao dịch và tiền với sao kê; làm lệch cố ý thì báo không khớp.

**Acceptance Scenarios**:
1. **Given** màn đang mở, **When** xem đầu trang, **Then** có số đã phân loại/tổng, số chưa phân loại (nổi bật), tổng vào, tổng ra, chênh lệch, và kết quả kiểm khớp.
2. **Given** nhóm Chi tiêu (và nhóm chi), **When** xem tổng nhóm, **Then** hiển thị chi, hoàn chi, chi ròng; nhóm khác hiển thị vào, ra, ròng.
3. **Given** nút "Xem nguồn", **When** bấm, **Then** mở chi tiết dòng sao kê nguồn như ở các màn khác.
4. **Given** cuối trang, **When** xem, **Then** có tổng toàn bộ kèm "đủ N/N giao dịch" hoặc cảnh báo thiếu.
5. **Given** số tiền ra/vào, **When** xem, **Then** ra màu và dấu khác vào, đúng như sao kê.

### Edge Cases
- Tài khoản chưa có giao dịch: màn hiển thị trạng thái rỗng.
- Không có giao dịch nào đã phân loại: chỉ có nhóm Chưa phân loại; thanh tóm tắt báo 0/N.
- Giao dịch chuyển nội bộ đã ghép: nhóm "Chuyển nội bộ" như các màn khác.
- Nhóm không có giao dịch trong phạm vi: không hiển thị.
- Bộ lọc của danh sách phân loại ở bước 2 không ảnh hưởng màn này (luôn là phạm vi đã chọn ở màn này).
- Giao dịch đã duyệt (nằm trong snapshot): hiển thị bình thường kèm trạng thái "đã duyệt".
- Số giao dịch lớn (vài trăm): màn vẫn mở được trong thời gian chấp nhận được, mặc định mở sẵn.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Hệ thống MUST có màn Kiểm tra phân loại mở từ bước Phân loại của tài khoản và có nút quay lại; màn MUST chỉ xem, MUST NOT sửa dữ liệu (R84).
- **FR-002**: Màn MUST gom giao dịch thành nhóm theo danh mục (đường dẫn danh mục con, gồm gốc tự tạo) và, khi phần phân loại có đối tượng, thành nhóm riêng "Danh mục · Đối tượng"; giao dịch chưa phân loại MUST ở nhóm riêng.
- **FR-003**: Mỗi nhóm MUST hiển thị số giao dịch và tổng vào, tổng ra (nhóm chi: chi, hoàn chi, chi ròng) và MUST liệt kê tất cả giao dịch của nhóm, mặc định mở sẵn, có thu gọn/mở tất cả.
- **FR-004**: Giao dịch tách nhiều phần MUST xuất hiện ở mỗi nhóm có phần của nó với số tiền của phần đó và ghi chú về giao dịch tổng; tổng nhóm MUST cộng theo phần.
- **FR-005**: Phạm vi mặc định MUST là cả tài khoản; MUST cho chọn 24 giờ qua (theo thời điểm phân loại) hoặc khoảng ngày (hai đầu bao gồm, theo ngày giao dịch); khoảng ngày không hợp lệ MUST bị chặn (R85).
- **FR-006**: Nhóm và dòng MUST sắp theo thời điểm phân loại mới nhất trước (hòa thì theo ngày giao dịch mới nhất), Chưa phân loại ở cuối; giao dịch phân loại trong 24 giờ gần nhất MUST có dấu "Mới".
- **FR-007**: Mỗi dòng MUST hiển thị kiểu sao kê: ngày và mã tham chiếu, nội dung và nút "Xem nguồn · n liên kết", số tiền ra/vào, nhãn phân loại (nhãn "Hoàn chi tiêu" cho tiền vào Chi tiêu), trạng thái nháp/đã duyệt (R86).
- **FR-008**: Màn MUST có thanh tóm tắt: đã phân loại/tổng, chưa phân loại (nổi bật), tổng vào, tổng ra, chênh lệch, kết quả kiểm khớp đủ số giao dịch và tiền với sao kê; và tổng toàn bộ cuối trang.
- **FR-009**: Kiểm khớp MUST so số giao dịch gốc và tổng tiền vào/ra nguồn với tổng các nhóm, và MUST nêu rõ khớp hoặc không khớp kèm chênh lệch (R46).
- **FR-010**: Màn MUST NOT đổi kết quả, snapshot, báo cáo, công nợ đã có và MUST NOT sửa dữ liệu vận hành khi kiểm thử.

### Key Entities
- **Nhóm kiểm tra**: tên (danh mục hoặc "danh mục · đối tượng"), loại, số giao dịch, tổng vào/ra, thời điểm phân loại mới nhất, danh sách dòng.
- **Dòng giao dịch kiểm tra**: ngày, mã tham chiếu, nội dung, số tiền (phần), chiều, nhãn phân loại, đối tượng, thời điểm phân loại, trạng thái, số liên kết nguồn.

## Success Criteria *(mandatory)*
- **SC-001**: Từ danh sách phân loại mở màn Kiểm tra trong 1 thao tác và thấy đủ giao dịch của mọi nhóm không phải bấm mở thêm.
- **SC-002**: Sau khi phân loại một lượt, nhóm vừa phân loại nằm trên cùng (100% trường hợp thử).
- **SC-003**: Tổng vào/ra toàn bộ và theo nhóm khớp 100% các dòng liệt kê; kiểm khớp báo đúng cả khi cố ý làm lệch.
- **SC-004**: Từ một dòng mở được dòng sao kê nguồn trong 1 thao tác.
- **SC-005**: Màn không làm đổi bất kỳ dữ liệu nào (số sự kiện lưu không tăng); checksum dữ liệu vận hành không đổi.

## Assumptions
- Thời điểm phân loại lấy từ lịch sử phân loại sẵn có của giao dịch (lần gần nhất).
- "Mới" là phân loại trong 24 giờ gần nhất theo giờ máy chủ.
- Nhóm đối tượng chỉ tạo khi phần phân loại có hồ sơ gắn; phần không có đối tượng nằm ở nhóm danh mục chung.
- Không có nút "đã kiểm" ở bản đầu (Thạch chọn); chỉ xem.
- Chỉ VND như các đợt trước.
