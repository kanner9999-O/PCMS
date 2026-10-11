# Feature Specification: Hoàn thiện hành trình công nợ

**Feature Branch**: `005-debt-journey-polish`
**Created**: 2026-10-11
**Status**: Draft
**Input**: Rà hành trình xuyên suốt bằng dữ liệu giả ngày 11/10/2026 (bộ QA riêng, không phải dữ liệu thật) phát hiện bốn chỗ khó dùng ở màn Công nợ và báo cáo dòng tiền khoản vay. Nguồn yêu cầu: R47 (tổng quan người nợ), R53 (báo cáo và phạm vi chi phí). Tham chiếu spec 002 (sổ công nợ) và spec 004 (tất toán và báo cáo).

**Phạm vi:** chỉ thay đổi cách hiển thị, mặc định và liên kết trên dữ liệu đã có. Không đổi quy tắc tính tiền, tính lãi, phân bổ, tất toán hay duyệt; không thêm dữ liệu tài chính mới.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Báo cáo dòng tiền mở ra là thấy số (Priority: P1)

Thạch mở báo cáo dòng tiền khoản vay (tuần/tháng/quý). Hiện nay hộp thoại mặc định chọn ngày hôm nay, nên khi nguồn sao kê kết thúc ở kỳ trước, báo cáo toàn số 0 và Thạch không biết là do chưa chọn đúng kỳ hay do không có tiền. Thạch cần thấy ngay kỳ có dữ liệu và hiểu kỳ nào chưa có nguồn.

**Why this priority**: Đây là đầu ra chính của P07, và là lần đầu người dùng thấy kết quả; báo cáo toàn 0 dễ bị hiểu nhầm là sai.

**Independent Test**: Với bộ dữ liệu giả có nguồn tới 30/09/2026 và hôm nay là 11/10/2026, mở báo cáo kỳ "Tháng": thấy ngay số của tháng 09/2026, hoặc một thông báo rõ ràng rằng tháng hiện tại chưa có nguồn kèm lối chọn tháng có dữ liệu.

**Acceptance Scenarios**:

1. **Given** nguồn ngân hàng mới nhất kết thúc ở một kỳ trước kỳ chứa ngày hôm nay, **When** Thạch mở báo cáo, **Then** ngày mặc định rơi vào kỳ có dữ liệu mới nhất và giao diện nêu kỳ đó đang được chọn.
2. **Given** kỳ được chọn nằm ngoài mọi kỳ nguồn đã ghi, **When** báo cáo hiển thị, **Then** có dòng cảnh báo "Kỳ này chưa có nguồn" kèm khoảng nguồn đã ghi, thay vì chỉ hiện các số 0.
3. **Given** Thạch tự đổi ngày hoặc kỳ, **When** xem lại báo cáo, **Then** giá trị Thạch chọn được giữ, không bị ghi đè bởi mặc định.

---

### User Story 2 - Tổng quan công nợ ở đầu màn (Priority: P1)

Thạch mở màn Công nợ và muốn biết ngay tổng phải thu, tổng phải trả, bao nhiêu người và bao nhiêu khoản đang hoạt động, đã hoàn tất, cần kiểm tra lại, rồi mới đi xuống từng người (R47). Hiện nay mỗi người đã có dòng phải thu/phải trả riêng (đúng R47) nhưng không có tổng toàn bộ ở đầu màn và không có số khoản theo trạng thái.

**Why this priority**: R47 yêu cầu tổng người còn nợ và dư nợ từng người; đây là thiếu sót lớn nhất so với yêu cầu đã xác nhận.

**Independent Test**: Với bộ giả 3 người (An hoàn tất, Bình 100 triệu phải thu, Chi hết gốc), đầu màn hiển thị phải thu 100.000.000 VND, phải trả 0 VND, 3 người, số khoản theo từng trạng thái; mỗi người có dòng tổng của chính người đó.

**Acceptance Scenarios**:

1. **Given** có nhiều người và nhiều khoản, **When** mở màn Công nợ, **Then** đầu màn hiển thị tổng phải thu và tổng phải trả theo dữ liệu, tách riêng và không bù trừ nhau, kèm số người và số khoản theo từng trạng thái.
2. **Given** một người có nhiều khoản, **When** xem người đó, **Then** vẫn thấy tổng phải thu/phải trả của người rồi từng khoản bên dưới (không hồi quy).
3. **Given** sổ còn ở mức NHÁP hoặc còn giao dịch chưa phân loại, **When** hiển thị tổng, **Then** các tổng mang nhãn "theo dữ liệu hiện có" như bản hiện tại, không trình bày như công nợ đã xác nhận.
4. **Given** có khoản chưa thiết lập gốc đầu, **When** hiển thị tổng, **Then** khoản đó được đếm là "cần thiết lập" và không được cộng thành số 0 giả.

---

### User Story 3 - Khoản hết gốc còn việc phải làm thì phải được nói ra (Priority: P2)

Thạch thấy một khoản có Gốc 0 nhưng trạng thái chỉ ghi "Đang hoạt động", không biết còn thiếu gì để tất toán. Cần một dòng gợi ý việc tiếp theo dựa đúng điều kiện tất toán đã có ở spec 004 (bảng kê lãi chưa phủ tới hết ngày, còn lãi chưa xử lý, có nháp). Nhãn trạng thái hiện còn lặp ("Đã hoàn tất · Hoàn tất / lịch sử") gây rối.

**Why this priority**: Giúp Thạch biết việc kế tiếp mà không phải đoán, nhưng không làm thay đổi nghiệp vụ nên ưu tiên sau hai mục trên.

**Independent Test**: Khoản giả "Chi · hết gốc còn lãi" hiển thị lý do chưa tất toán được và đường tới Bảng kê lãi; khoản "An" đã hoàn tất chỉ hiện một nhãn trạng thái duy nhất.

**Acceptance Scenarios**:

1. **Given** khoản có gốc bằng 0 nhưng chưa đủ điều kiện tất toán, **When** xem danh sách, **Then** hiện đúng lý do còn thiếu (lấy từ kiểm tra tất toán hiện có) và lối đi tới bước cần làm.
2. **Given** khoản đã hoàn tất, **When** xem danh sách, **Then** trạng thái chỉ xuất hiện một lần và có lối xem lịch sử tất toán.
3. **Given** khoản thiếu thiết lập, **When** xem danh sách, **Then** gợi ý "Cần thiết lập" thay vì gợi ý tất toán.

---

### User Story 4 - Đi lại giữa tài khoản ngân hàng và công nợ (Priority: P3)

Từ màn tài khoản, Thạch thấy giao dịch đã phân loại vào khoản vay hoặc phần chưa phân loại có thể ảnh hưởng công nợ, nhưng không có lối đi sang Công nợ; ngược lại từ khoản vay đã có đường truy tới giao dịch nguồn (spec 002) nhưng chưa có đường quay về tài khoản.

**Why this priority**: Cải thiện đi lại, không chặn việc dùng.

**Independent Test**: Từ tài khoản giả, mở được Công nợ bằng một thao tác; từ một khoản, mở được tài khoản và giao dịch nguồn tương ứng.

**Acceptance Scenarios**:

1. **Given** tài khoản có giao dịch gắn khoản vay, **When** xem tổng quan tài khoản, **Then** có lối sang Công nợ và số khoản liên quan.
2. **Given** đang xem một khoản, **When** muốn xem nguồn, **Then** mở được tài khoản đúng với giao dịch cấu thành và quay lại được.

---

### Edge Cases

- Chưa có nguồn nào: báo cáo và tổng quan hiển thị trạng thái rỗng rõ ràng, không hiện số 0 như thể đã đối soát.
- Nhiều tài khoản có kỳ nguồn khác nhau: kỳ mặc định lấy theo kỳ nguồn mới nhất của các tài khoản liên quan, và nêu rõ.
- Khoản có cả phải thu và phải trả cùng một người: hai tổng vẫn tách riêng, không bù trừ.
- Khoản thuộc nhiều trạng thái bộ lọc: số đếm trạng thái không đếm trùng.
- Bộ lọc người/khoản đang bật: tổng quan nêu rõ đang tính toàn bộ hay phần đang lọc, và báo cáo dòng tiền vẫn gồm khoản đã tất toán (spec 004).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Báo cáo dòng tiền khoản vay MUST chọn mặc định một ngày thuộc kỳ có dữ liệu nguồn mới nhất khi ngày hôm nay nằm ngoài các kỳ nguồn, và MUST nêu kỳ đang chọn.
- **FR-002**: Báo cáo MUST cảnh báo rõ khi kỳ được chọn chưa có nguồn, kèm khoảng nguồn đã ghi, thay vì chỉ hiển thị 0 VND.
- **FR-003**: Lựa chọn ngày/kỳ do người dùng chủ động chọn MUST được giữ nguyên.
- **FR-004**: Màn Công nợ MUST hiển thị ở đầu: tổng phải thu, tổng phải trả (tách riêng, không bù trừ), số người, số khoản theo trạng thái (đang hoạt động, đã hoàn tất, cần kiểm tra lại, cần thiết lập).
- **FR-005**: Dòng phải thu/phải trả của từng người đã có MUST được giữ nguyên, hiển thị trước danh sách khoản (R47).
- **FR-006**: Các tổng MUST giữ nhãn dữ liệu NHÁP/"theo dữ liệu hiện có" như hiện hành và MUST NOT được trình bày như công nợ đã xác nhận.
- **FR-007**: Khoản chưa thiết lập MUST được đếm riêng là "cần thiết lập", không cộng vào tổng như số 0.
- **FR-008**: Khoản có gốc bằng 0 nhưng chưa tất toán được MUST hiển thị lý do còn thiếu theo đúng điều kiện tất toán hiện có và lối đi tới bước cần làm; hệ thống MUST NOT tự tất toán, tự duyệt hay đổi trạng thái.
- **FR-009**: Trạng thái khoản MUST chỉ hiện một nhãn nhất quán, không lặp nhãn.
- **FR-010**: Từ tài khoản MUST có lối sang Công nợ; từ khoản MUST có lối tới tài khoản và giao dịch nguồn, kèm đường quay lại.
- **FR-011**: Thay đổi này MUST NOT sửa dữ liệu tài chính, MUST NOT đổi cách tính tiền/lãi/phân bổ/tất toán, và MUST NOT đổi kết quả của bất kỳ báo cáo hay snapshot nào đã có.

### Key Entities

- **Tổng quan công nợ**: số tổng hợp phải thu, phải trả, số người, số khoản theo trạng thái; chỉ là cách hiển thị từ dữ liệu sổ đã có.
- **Kỳ báo cáo**: ngày chọn, loại kỳ (tuần/tháng/quý), kỳ nguồn đã ghi dùng để gợi ý mặc định.
- **Gợi ý việc kế tiếp của khoản**: lý do chưa tất toán được và đích điều hướng, suy ra từ kiểm tra tất toán sẵn có.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Với bộ dữ liệu giả nguồn tới 30/09/2026, mở báo cáo trong ngày 11/10/2026 thấy kỳ có dữ liệu hoặc cảnh báo "chưa có nguồn" mà không phải đổi ngày thủ công (0 thao tác đổi ngày để thoát khỏi toàn số 0).
- **SC-002**: Thạch đọc được tổng phải thu, tổng phải trả và số khoản theo trạng thái trong vòng một màn hình đầu, không cuộn xuống từng người.
- **SC-003**: 100% khoản có gốc 0 mà chưa tất toán được hiển thị lý do cụ thể; 0 khoản bị tự đổi trạng thái.
- **SC-004**: Từ tài khoản tới công nợ và ngược lại đi được trong tối đa 2 thao tác.
- **SC-005**: Dữ liệu tài chính, báo cáo và snapshot cũ cho kết quả y hệt trước và sau thay đổi (đối chiếu số trên bộ giả và kiểm tra checksum dữ liệu vận hành không đổi).

## Assumptions

- Chỉ dùng dữ liệu và kiểm tra tất toán đã có; không thêm khái niệm quá hạn (chưa có hạn cam kết) — giữ như spec 003/004.
- Kỳ mặc định khi hôm nay ngoài kỳ nguồn là kỳ chứa ngày nguồn mới nhất; nếu sau này Thạch muốn mặc định khác thì đổi ở bước làm rõ.
- Tổng quan tính trên toàn bộ khoản, độc lập bộ lọc hiển thị, và nêu rõ điều đó (nhất quán với cách báo cáo hiện hành không cắt theo bộ lọc).
- Giới hạn VND như các đợt trước; không kiểm mobile riêng ở đợt này (ghi vào giới hạn khi bàn giao).
- Đợt này không kiểm hay thao tác trên `outputs/p01-user-trial`; nghiệm thu bằng bộ dữ liệu giả riêng (constitution I, V).
