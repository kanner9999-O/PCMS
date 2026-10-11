# Feature Specification: Hoàn chi tiêu

**Feature Branch**: `010-expense-refund`
**Created**: 2026-10-11
**Status**: Draft
**Input**: Thạch hỏi ngày 11/10/2026: chi trả hộ nhiều người rồi những người còn lại hoàn tiền thì khoản tiền vào có được tính là chi tiêu không. Quyết định PO được Thạch đồng ý: tính là **hoàn chi tiêu**. Nguồn yêu cầu: R06, R50, R53, R56, R58 · Spec liên quan: 001 (phân loại), 004 (báo cáo dòng tiền khoản vay), 008 (danh mục), 009 (màn phân loại).

**Phạm vi:** cho phép phân loại tiền vào là hoàn chi dưới Chi tiêu và hiển thị đúng chi / hoàn chi / chi ròng; không đổi quy tắc tiền khác, không gắn từng khoản hoàn vào khoản chi cụ thể ở bản đầu.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Phân loại tiền vào là hoàn chi tiêu (Priority: P1)
Thạch trả 1.000.000 tiền cơm cho 3 người, hai người còn lại chuyển trả 300.000 mỗi người. Thạch phân loại khoản trả là Chi tiêu và hai khoản nhận là **hoàn chi tiêu** (cùng danh mục Chi tiêu hoặc danh mục con như Ăn uống), không phải Thu nhập.

**Why this priority**: hiện tiền vào chỉ phân loại được là Thu nhập, làm báo cáo ghi chi 1.000.000 và thu nhập 600.000 trong khi thực tế chi ròng là 400.000 và không có thu nhập.

**Independent Test**: với một giao dịch ra 1.000.000 và hai giao dịch vào 300.000: phân loại cả ba vào Chi tiêu → chi 1.000.000, hoàn chi 600.000, chi ròng 400.000, thu nhập 0.

**Acceptance Scenarios**:
1. **Given** giao dịch tiền vào, **When** chọn loại Chi tiêu, **Then** lưu được và nhãn hiển thị là "Hoàn chi tiêu".
2. **Given** giao dịch tiền ra, **When** chọn Thu nhập, **Then** vẫn bị chặn như hiện nay (chỉ Chi tiêu nhận được cả hai chiều).
3. **Given** phân loại hàng loạt nhiều dòng tiền vào, **When** áp Chi tiêu, **Then** tất cả được gán hoàn chi, tiền nguồn không đổi.
4. **Given** tiền vào đã gán Thu nhập từ trước, **When** Thạch phân loại lại thành hoàn chi, **Then** đi qua luồng điều chỉnh hiện có (lịch sử trước/sau giữ nguyên; bản duyệt cũ không bị đổi).

### User Story 2 - Báo cáo và tổng danh mục hiển thị chi, hoàn chi, chi ròng (Priority: P1)
Báo cáo toàn đợt, màn Danh mục và lịch sử từng danh mục hiển thị ba số riêng cho Chi tiêu: tổng chi, tổng hoàn chi, chi ròng (chi trừ hoàn chi). Không bù trừ âm thầm: số chi và số hoàn chi luôn nhìn thấy riêng (R56).

**Why this priority**: yêu cầu R56 của Thạch là hoàn tiền không bị ẩn do bù trừ, đồng thời Thạch cần biết chi ròng thực tế.

**Independent Test**: sau US1, báo cáo duyệt và màn Danh mục hiển thị "Chi 1.000.000 · Hoàn chi 600.000 · Chi ròng 400.000"; mở lịch sử Chi tiêu thấy cả ba dòng, hai dòng vào ghi "Hoàn chi"; Thu nhập không đổi.

**Acceptance Scenarios**:
1. **Given** danh mục Chi tiêu có chi và hoàn chi, **When** xem báo cáo duyệt, **Then** thấy dòng chi, dòng hoàn chi và dòng chi ròng riêng.
2. **Given** danh mục con (ví dụ Ăn uống) có hoàn chi, **When** xem tổng, **Then** cha và con đều hiển thị chi, hoàn chi, chi ròng, mỗi giao dịch đếm một lần ở cha.
3. **Given** lịch sử danh mục, **When** xem dòng tiền vào dưới Chi tiêu, **Then** ghi rõ "Hoàn chi", không hiển thị như thu nhập.
4. **Given** hoàn chi lớn hơn chi trong cùng danh mục (chi ròng âm), **When** xem tổng, **Then** hiển thị số âm đúng nghĩa (đã hoàn nhiều hơn đã chi) kèm nhãn, không cắt về 0.
5. **Given** báo cáo dòng tiền khoản vay (spec 004), **When** có hoàn chi gắn khoản vay, **Then** vẫn tính vào "Hoàn chi phí gắn rõ khoản vay" như đã định nghĩa.

### User Story 3 - Thu nhập không bị tăng và không đổi dữ liệu cũ (Priority: P2)
Thu nhập chỉ gồm các khoản phân loại Thu nhập. Dữ liệu và bản duyệt đã có không đổi sau khi triển khai; tiền vào đã gán Thu nhập giữ nguyên cho đến khi Thạch tự điều chỉnh.

**Independent Test**: dữ liệu cũ cho kết quả y hệt; snapshot cũ cùng mã kiểm chứng.

### Edge Cases
- Tiền vào có gắn hồ sơ khoản vay với loại Chi tiêu: giữ ý nghĩa hoàn chi phí gắn khoản vay (spec 004).
- Giao dịch vào được tách thành nhiều phần: phần Chi tiêu là hoàn chi, phần khác theo loại đã chọn; tổng các phần bằng tiền nguồn.
- Hoàn chi vượt tổng chi của danh mục: chấp nhận (không chặn), hiển thị chi ròng âm; không suy ra là thu nhập.
- Hoàn chi nhận ngoài kỳ nguồn của khoản chi gốc: vẫn là hoàn chi theo ngày giao dịch, không tự ghép vào khoản chi cụ thể.
- Chuyển nội bộ giữa hai tài khoản của Thạch không phải hoàn chi (tách riêng như R57).

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Hệ thống MUST cho phân loại tiền vào là Chi tiêu (hoàn chi) và MUST tiếp tục chặn Thu nhập cho tiền ra.
- **FR-002**: Phần phân loại Chi tiêu của tiền vào MUST hiển thị nhãn "Hoàn chi tiêu" ở danh sách giao dịch, hộp thoại phân loại, lịch sử danh mục và bản xem snapshot.
- **FR-003**: Báo cáo toàn đợt MUST hiển thị riêng tổng chi, tổng hoàn chi và chi ròng cho Chi tiêu; số chi và hoàn chi MUST NOT bị bù trừ ẩn (R56).
- **FR-004**: Màn Danh mục và lịch sử từng danh mục MUST hiển thị chi, hoàn chi, chi ròng cho Chi tiêu và các danh mục con của nó, theo nguyên tệ, mỗi giao dịch đếm một lần ở danh mục cha (R58, spec 008).
- **FR-005**: Chi ròng MUST bằng tổng chi trừ tổng hoàn chi, MUST hiển thị âm khi hoàn chi lớn hơn chi.
- **FR-006**: Thu nhập MUST chỉ gồm phần phân loại Thu nhập; hoàn chi MUST NOT cộng vào Thu nhập.
- **FR-007**: Phân loại hàng loạt và tách phần MUST hỗ trợ hoàn chi với cùng quy tắc tổng phần bằng tiền nguồn (R45).
- **FR-008**: Chưa gắn từng khoản hoàn với khoản chi cụ thể ở bản đầu; hệ thống MUST NOT tự ghép.
- **FR-009**: Thay đổi MUST NOT đổi kết quả báo cáo, snapshot, công nợ, bảng kê lãi đã có; MUST NOT sửa dữ liệu vận hành khi kiểm thử; tiền vào đã gán Thu nhập MUST giữ nguyên.

### Key Entities
- **Phần phân loại**: danh mục, số tiền, chiều tiền; phần Chi tiêu có chiều vào là hoàn chi.
- **Tổng Chi tiêu**: chi, hoàn chi, chi ròng, số giao dịch, theo nguyên tệ.

## Success Criteria *(mandatory)*
- **SC-001**: Với ví dụ cơm 1.000.000 và hai khoản hoàn 300.000, báo cáo hiển thị chi 1.000.000, hoàn chi 600.000, chi ròng 400.000 và thu nhập 0 — đúng 100% khi đối chiếu.
- **SC-002**: Phân loại một khoản tiền vào là hoàn chi trong tối đa 3 thao tác, như phân loại thường.
- **SC-003**: Số chi và số hoàn chi luôn nhìn thấy riêng ở báo cáo, màn Danh mục và lịch sử (0 chỗ chỉ hiện số ròng).
- **SC-004**: 0 thay đổi ở snapshot, báo cáo và công nợ đã có (đối chiếu số trước/sau và checksum dữ liệu vận hành).
- **SC-005**: Tổng chi, hoàn chi, chi ròng của danh mục cha khớp tổng các dòng liệt kê, mỗi giao dịch một lần.

## Assumptions
- Quyết định "hoàn chi" do PO đề xuất và Thạch đồng ý ("Triển khai theo đề xuất ở trên").
- Bản đầu chỉ cần cùng danh mục; truy được "hoàn này cho bữa nào" là mức chi tiết sau nếu Thạch yêu cầu.
- Thu nhập từ người khác chuyển trả không phải hoàn chi (khoản nhận không liên quan chi tiêu vẫn là Thu nhập); Thạch tự chọn khi phân loại, hệ thống không tự đoán.
- Danh mục mặc định khi mở hộp thoại cho tiền vào vẫn là Thu nhập; Thạch tự chọn Chi tiêu (hoàn chi) khi đó là hoàn tiền.
- Chỉ VND như các đợt trước.
