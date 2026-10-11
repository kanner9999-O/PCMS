# Feature Specification: Điều khoản lãi, xem trước và bảng kê lãi (P05–P06)

**Feature Branch**: `003-interest-statements` (baseline, đã phát hành trên `main`)
**Created**: 2026-10-11 (migrate từ PRODUCT-SPEC §1 P05–P06, §5 R30–R31, R42–R43)
**Status**: Implemented (P06, 11/10/2026)
**Nguồn yêu cầu**: R21, R29, R31, R42, R43 · Tiêu chí: ACCEPTANCE A36–A39 · Bàn giao: `outputs/p05-handoff.md`, `outputs/p06-handoff.md`, `outputs/p06-po-review.jpg`

## User Scenarios & Testing

### User Story 1 - Khai điều khoản lãi và xem trước (Priority: P1)
Nhập lãi suất VND/triệu/ngày (vd 500) hoặc %/tháng quy ước 30 ngày (vd 1,5%) kèm ngày hiệu lực và căn cứ; xem bảng lãi dự tính theo từng đoạn dư gốc.

**Independent Test**: 01–11/10 chia 120 triệu × 1 ngày + 90 triệu × 9 ngày = 465.000; 1,5%/tháng hiển thị tương đương 500 VND/triệu/ngày; đổi điều khoản giữ lịch sử.

### User Story 2 - Lập bảng kê lãi theo kỳ, chọn tiền nguồn, duyệt (Priority: P1)
Chọn khoảng → xem lãi dự tính → chủ động chọn phần tiền lãi nguồn trả cho khoảng này (kể cả tiền nhận ngoài khoảng) → miễn giảm nếu có → duyệt giữ phiên bản.

**Independent Test**: dự tính 1,5 triệu, chọn 1,2 triệu nhận ngoài kỳ → S1 còn 300 nghìn; điều chỉnh miễn 300 nghìn → S2 còn 0; S1 giữ nguyên.

**Acceptance Scenarios**:
1. **Given** bảng kê khác cùng khoản, **When** khoảng chồng nhau, **Then** bị chặn.
2. **Given** tiền đã dùng ở bản duyệt hiện hành, **When** chọn lại, **Then** bị chặn (không dùng trùng).
3. **Given** thay nguồn/điều khoản sau duyệt, **When** mở lại, **Then** cảnh báo và yêu cầu kiểm lại, không đổi số cũ.

### Edge Cases
- Miễn giảm không vượt phần chưa thanh toán; không tạo tiền, không giảm gốc.
- Phần tiền thừa để chưa phân bổ, không thành lợi nhuận.
- Không tự gọi phần chưa thu là quá hạn.
- Lỗi đã gặp: token duyệt dùng `review_token`, không dùng CSRF `token` (có hồi quy).

## Requirements

### Functional Requirements
- **FR-001**: Lãi suất MUST nhập được 2 kiểu, quy đổi hiển thị, không cộng hai loại; giữ dạng nhập gốc và ngày hiệu lực (R43).
- **FR-002**: Lãi MUST tính trên dư gốc từng đoạn, không vốn hóa lãi, giữ gốc lẻ triệu (R42, R31).
- **FR-003**: Quy ước xem trước (dư gốc cuối ngày, gồm ngày đầu/không gồm ngày cuối, làm tròn tổng half-up) MUST được nêu rõ và xác nhận riêng trên mỗi bảng kê; KHÔNG được ghi là người dùng đã chốt toàn cục.
- **FR-004**: Bảng kê MUST bất biến sau duyệt; điều chỉnh có lý do tạo phiên bản mới (R21).
- **FR-005**: Miễn giảm MUST có số tiền, ngày hiệu lực, lý do, xác nhận (R42).
- **FR-006**: Tiền thực thu dùng cho bảng kê MUST chọn chủ động, đúng khoản/chiều, tổng ≤ phần lãi nguồn.

### Key Entities
Điều khoản lãi · Đoạn tính · Bảng kê (nháp/duyệt/điều chỉnh) · Lựa chọn tiền nguồn · Miễn giảm.

## Success Criteria
- **SC-001**: P06 8 ca + 12 hồi quy đạt; PO kiểm luồng 1,5 triệu/1,2 triệu/300 nghìn (IMPLEMENTATION-STATUS §P06).

## Assumptions & Known limits
- Biên ngày/làm tròn chưa được người dùng chốt toàn cục (chỉ là quy ước xem trước). Chưa có quá hạn. VND only.
