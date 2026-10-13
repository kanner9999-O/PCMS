# Feature Specification: Chung cư theo tiến độ

**Feature Branch**: `021-realty-progress` · **Created**: 2026-10-13 · **Status**: Draft
**Input**: Thạch muốn ghi giá hợp đồng và các đợt thanh toán theo tiến độ của căn chung cư, biết đã trả bao nhiêu và còn phải trả bao nhiêu (R101–R104). Tham chiếu spec 011 (BĐS), 013 (tổng tài sản), 017 (định dạng lịch sử). Không đổi vốn từ sao kê, không bù trừ, không tính nợ.

## User Scenarios & Testing
### User Story 1 - Giá hợp đồng và lịch đợt thanh toán (Priority: P1)
Thạch nhập giá hợp đồng (ngày, lý do) và ngày bàn giao dự kiến cho một BĐS, rồi nhập từng đợt (tên, ngày dự kiến, số tiền, ghi chú). Màn BĐS hiện tổng các đợt, chênh lệch với giá hợp đồng nếu có.

**Independent Test**: căn "CC A" giá hợp đồng 2.000.000.000; ba đợt 600.000.000 (01/09), 700.000.000 (01/12), 700.000.000 (01/03/2027) → tổng đợt 2.000.000.000, chênh 0; cập nhật giá 1.950.000.000 lý do chiết khấu → giá hiện tại mới, lịch sử có cả hai, chênh −50.000.000 hiển thị.

**Acceptance Scenarios**:
1. **Given** BĐS, **When** nhập giá hợp đồng với ngày và lý do, **Then** giá hiện tại là bản có ngày mới nhất, các bản cũ giữ trong lịch sử; hủy được kèm lý do.
2. **Given** các đợt, **When** xem, **Then** thấy từng đợt theo ngày dự kiến, tổng các đợt và chênh với giá hợp đồng (không tự sửa).
3. **Given** thiếu tên/ngày/số tiền > 0 hoặc số không nguyên VND, **When** lưu, **Then** bị chặn kèm lý do.

### User Story 2 - Gắn giao dịch vào đợt, thấy đã trả/còn phải trả (Priority: P1)
Thạch gắn giao dịch ngân hàng đã phân loại Đầu tư BĐS (gắn đúng BĐS) vào một đợt. Mỗi đợt hiện đã trả, còn lại và trạng thái (chưa trả / trả một phần / đã trả / quá hạn).

**Independent Test**: giao dịch ra 600.000.000 phân loại Đầu tư BĐS gắn "CC A" → gắn vào Đợt 1 → Đợt 1 đã trả 600.000.000, còn 0, "Đã trả"; trả đợt 2 làm hai giao dịch 300.000.000 → "Trả một phần" rồi "Đã trả"; cam kết còn lại = tổng còn lại các đợt.

**Acceptance Scenarios**:
1. **Given** giao dịch ra đã phân loại Đầu tư BĐS gắn BĐS và chưa gắn đợt, **When** gắn vào đợt của BĐS đó, **Then** đợt cập nhật; giao dịch khác BĐS hoặc đã gắn đợt khác bị chặn.
2. **Given** đợt đã trả đủ hoặc vượt, **When** xem, **Then** "Đã trả" (vượt thì cảnh báo trả quá).
3. **Given** đợt quá ngày dự kiến và chưa đủ, **When** xem, **Then** nhãn "Quá hạn" kèm số ngày; không có số tiền nợ nào được cộng.
4. **Given** giao dịch đã gắn bị phân loại lại khỏi Đầu tư BĐS đó, **When** xem, **Then** phần gắn đó không tính và báo "giao dịch không còn là thanh toán BĐS".
5. **Given** bỏ gắn (lý do) hoặc hủy đợt, **When** xem, **Then** số đã trả cập nhật, bản ghi giữ lại; không hủy đợt đang có giao dịch gắn.

### User Story 3 - Cam kết chưa thanh toán hiển thị riêng (Priority: P2)
Màn BĐS và Tổng tài sản có một dòng "Cam kết chưa thanh toán theo hợp đồng" (tổng còn lại các đợt), nói rõ không vào nợ và không trừ giá trị BĐS.

**Acceptance Scenarios**:
1. **Given** có đợt chưa trả, **When** xem Tổng tài sản, **Then** dòng cam kết hiện riêng; tài sản, nợ, ròng không đổi so với không có lịch.
2. **Given** thế chấp và khoản vay, **When** xem, **Then** dùng liên kết thế chấp hiện có, không gắn từng đợt.

### Edge Cases
- BĐS không có lịch: màn giữ nguyên như trước.
- Số đợt nhiều: danh sách theo ngày dự kiến, cuộn trong khung.
- Giao dịch tách nhiều phần có nhiều phần Đầu tư BĐS cùng BĐS: gắn cả giao dịch, số tiền là tổng các phần Đầu tư ra của BĐS đó.
- Tiền vào (nhận lại) Đầu tư BĐS không gắn được đợt.

## Requirements
- **FR-001** (R101): hành động ghi, hủy giá hợp đồng (VND nguyên > 0, ngày, lý do, ngày bàn giao dự kiến tùy chọn), lịch sử, giá hiện tại = ngày mới nhất.
- **FR-002** (R102): hành động thêm đợt, hủy đợt (tên 1–100 ký tự, ngày hợp lệ, số tiền VND nguyên > 0, ghi chú ≤ 500, lý do khi hủy).
- **FR-003** (R102): gắn / bỏ gắn giao dịch vào đợt; số đã trả = tổng phần Đầu tư ra gắn BĐS hiện có của các giao dịch đang gắn; một giao dịch gắn tối đa một đợt đang hoạt động.
- **FR-004** (R103): trạng thái đợt (chưa trả, trả một phần, đã trả, trả quá) và cờ quá hạn theo ngày hôm nay (giờ Việt Nam); cam kết = Σ max(0, số tiền đợt − đã trả) trên các đợt đang hoạt động; chênh = giá hợp đồng − tổng các đợt.
- **FR-005** (R103): không đổi vốn từ sao kê, giá trị BĐS, nợ, tổng tài sản; cam kết là một dòng riêng.
- **FR-006** (R104): không thêm liên kết khoản vay với đợt.
- **FR-007**: đọc không ghi; sao lưu/khôi phục như các thao tác khác.

## Success Criteria
- **SC-001**: ví dụ số ở Story 1–2 cho đúng số (tổng đợt, chênh, đã trả, còn lại, cam kết).
- **SC-002**: BĐS không có lịch và Tổng tài sản không có lịch cho số liệu y như trước (hồi quy P13, P15).
- **SC-003**: nhập một đợt hoặc gắn một giao dịch trong một hộp thoại; dữ liệu thật không đổi (SHA256).

## Assumptions
- "Hôm nay" theo giờ Việt Nam; quá hạn chỉ là nhắc, không phát sinh số nợ.
- Mỗi đợt dùng chung một đồng VND; không quy đổi.
- Gắn giao dịch không đổi phân loại hay phân bổ của giao dịch.
