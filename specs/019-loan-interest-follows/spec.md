# Feature Specification: Lãi vay đi cùng khoản vay

**Feature Branch**: `019-loan-interest-follows` · **Created**: 2026-10-13 · **Status**: Draft
**Input**: Thạch xác nhận (R96): chuyển khoản vay sang danh mục khác thì lãi cũng chuyển cùng. Sửa giả định ở spec 016 (lãi ở lại Lãi vay). Tham chiếu spec 016, 008, 014, 015, 017.

## User Scenarios & Testing
### User Story 1 - Lãi chuyển cùng khoản vay (Priority: P1)
Sau khi chuyển khoản "Kết 10tr" sang Loans › Long debt, mọi giao dịch gốc **và lãi** của khoản hiện dưới danh mục mới ở màn Danh mục, lịch sử và màn Kiểm tra.

**Independent Test**: khoản có giải ngân 10tr, trả gốc 3tr, nhận lãi 200.000; chuyển sang Long debt → Long debt vào 3.200.000, ra 10.000.000, 3 giao dịch; Lãi vay (gốc hệ thống) không còn đếm khoản này; dư gốc, công nợ, bảng kê lãi không đổi; chuyển về Gốc vay thì lãi trở lại Lãi vay.

**Acceptance Scenarios**:
1. **Given** khoản vay đã chuyển nhóm, **When** xem Danh mục/Lịch sử/Kiểm tra, **Then** phần gốc và phần lãi của khoản đều thuộc danh mục mới; dòng lãi mang nhãn "Lãi vay".
2. **Given** khoản vay chưa chuyển, **When** xem, **Then** lãi vẫn ở Lãi vay như cũ.
3. **Given** chuyển về Gốc vay, **When** xem, **Then** lãi trở lại Lãi vay, gốc ở Gốc vay.
4. **Given** báo cáo duyệt/snapshot và công nợ/bảng kê lãi, **When** xem, **Then** không đổi.

## Requirements
- **FR-001** (R96): phần Gốc và Lãi gắn khoản vay đã có nhóm đều dùng nhóm làm danh mục hiệu lực; phần lãi giữ nhãn "Lãi vay" trên dòng.
- **FR-002**: danh mục đích vẫn là danh mục Gốc vay đang hoạt động (chứa cả gốc lẫn lãi của khoản gắn).
- **FR-003**: không đổi phân bổ, dư gốc, công nợ, bảng kê lãi, snapshot, báo cáo theo loại.

## Success Criteria
- **SC-001**: tổng danh mục đích tăng đúng bằng gốc + lãi của khoản; danh mục cũ giảm tương ứng.
- **SC-002**: dư gốc/phải thu/bảng kê lãi không đổi; dữ liệu thật không đổi (SHA256).

## Assumptions
- Báo cáo "theo loại" của kỳ (gốc vay/lãi vay vào ra) vẫn theo loại phân bổ gốc, không theo nhóm.
