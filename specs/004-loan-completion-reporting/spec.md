# Feature Specification: Tất toán có căn cứ và báo cáo dòng tiền khoản vay (P07)

**Feature Branch**: `004-loan-completion-reporting` (baseline, đã phát hành trên `main`)
**Created**: 2026-10-11 (migrate từ PRODUCT-SPEC §1 P07)
**Status**: Implemented (P07, 11/10/2026)
**Nguồn yêu cầu**: R29, R42, R53 · Tiêu chí: ACCEPTANCE A49 · Bàn giao: `outputs/p07-handoff.md`, `outputs/p07-po-review.jpg`

## User Scenarios & Testing

### User Story 1 - Tất toán và mở lại có căn cứ (Priority: P1)
Tất toán là thao tác xác nhận có ngày, căn cứ, lý do; hết gốc không tự là hết nợ.

**Independent Test**: khoản "hết gốc còn lãi" bị chặn tất toán; khoản đủ gốc/lãi/bảng kê duyệt được tất toán; mở lại có lý do rồi tất toán lại, lịch sử giữ cả 3 sự kiện.

**Acceptance Scenarios**:
1. **Given** gốc = 0 nhưng bảng kê không bao phủ tới hết ngày tất toán, **When** tất toán, **Then** bị chặn.
2. **Given** nguồn/điều khoản đổi sau tất toán, **When** xem, **Then** trạng thái "Cần kiểm tra lại", bằng chứng cũ không bị viết lại.
3. **Given** ngày tất toán trước giao dịch đã ghi, **When** nhập, **Then** bị chặn.

### User Story 2 - Báo cáo tuần/tháng/quý (Priority: P1)
Báo cáo theo ngày chọn (tuần Hai–CN, tháng, quý) từ phân bổ nguồn, gồm cả khoản đã tất toán; tách lãi nhận, lãi trả, thu hồi gốc, nhận vay/giải ngân, chi phí gắn khoản.

**Independent Test**: tháng 09 giả lập: lãi 2,7 triệu, chi phí 0,2 triệu, chênh 2,5 triệu, thu gốc 200 triệu riêng; lọc người hoàn tất không cắt báo cáo.

### Edge Cases
- Miễn giảm không thành tiền chi; thu gốc không thành doanh thu.
- "Chênh tiền" ≠ lợi nhuận ròng; không gom mọi chi tiêu ngân hàng vào chi phí cho vay.
- Lọc trạng thái không loại khoản tất toán khỏi báo cáo.

## Requirements

### Functional Requirements
- **FR-001**: Tất toán MUST yêu cầu gốc = 0, bảng kê duyệt phủ tới hết ngày tất toán (end-exclusive ngày kế), không còn phải thu/trả, không có nháp/nguồn đổi chưa xử lý.
- **FR-002**: Lãi = 0 MUST có điều khoản/bảng kê xác nhận, không suy từ thiếu dữ liệu.
- **FR-003**: Mở lại MUST có lý do; lịch sử tất toán bất biến.
- **FR-004**: Báo cáo MUST theo phân bổ nguồn, không cộng snapshot.
- **FR-005**: Chỉ tiêu "lãi nhận − lãi trả − chi phí gắn khoản + hoàn chi phí" MUST được gọi là chênh tiền, không phải lợi nhuận ròng (R53).

### Key Entities
Sự kiện tất toán/mở lại · Trạng thái khoản (Đang hoạt động/Đã hoàn tất/Cần kiểm tra lại) · Báo cáo dòng tiền theo kỳ.

## Success Criteria
- **SC-001**: 19 ca kết hợp + 5 ca P07 cuối đạt; PO kiểm tháng 09 và luồng mở lại (IMPLEMENTATION-STATUS §P07).

## Assumptions & Known limits
- Chưa kiểm mobile, dữ liệu lớn. R53 (phạm vi chi phí) và R47 (tổng quan người) chưa chứng minh đủ → spec 005.
