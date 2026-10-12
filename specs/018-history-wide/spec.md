# Feature Specification: Lịch sử rộng, một dòng một giao dịch

**Feature Branch**: `018-history-wide` · **Created**: 2026-10-12 · **Status**: Draft
**Input**: Thạch xem lịch sử "Chi tiêu › Chi phí cố định" (R94) và muốn rộng hơn, mọi thông tin nền nằm trên một dòng (R95). Chỉ đổi cách trình bày; không đổi số liệu. Tham chiếu spec 017.

## User Scenarios & Testing
### User Story 1 - Lịch sử rộng, một giao dịch một dòng (Priority: P1)
Mở lịch sử danh mục, khoản vay hoặc BĐS: hộp đủ rộng và mỗi giao dịch hiện trên một dòng gồm ngày, mã tham chiếu, nội dung (kèm tài khoản), nút Xem nguồn, số tiền, nhãn và trạng thái.

**Independent Test**: màn rộng ≥ 1300px, lịch sử "Chi phí cố định" 2 giao dịch → mỗi giao dịch cao đúng một hàng (cùng một đường ngang cho ngày, mã, số tiền, nhãn); màn hẹp và 375px tự xếp nhiều dòng, không tràn ngang.

**Acceptance Scenarios**:
1. **Given** hộp lịch sử trên màn rộng, **When** mở, **Then** hộp rộng hơn hộp thường và mỗi dòng giao dịch một hàng (nội dung dài tự xuống dòng trong ô nội dung nhưng các cột khác không đổi hàng).
2. **Given** màn/khung hẹp, **When** mở, **Then** dòng xếp hai hoặc ba tầng như cũ, không tràn ngang.
3. **Given** màn Kiểm tra phân loại, **When** khung đủ rộng, **Then** cũng hiện một dòng một giao dịch; khung hẹp xếp nhiều tầng.
4. **Given** nút Xem nguồn, **When** bấm, **Then** mở chi tiết nguồn như cũ.

## Requirements
- **FR-001** (R95): hộp lịch sử rộng hơn hộp thường; dòng giao dịch một hàng khi khung đủ rộng, nhiều tầng khi hẹp (theo bề rộng khung chứa).
- **FR-002**: các cột: ngày, mã tham chiếu, nội dung + tài khoản, Xem nguồn, số tiền, nhãn + trạng thái + ghi chú tách phần.
- **FR-003**: không đổi dữ liệu, tổng, thứ tự, hành vi Xem nguồn.

## Success Criteria
- **SC-001**: trên màn ≥ 1300px mỗi giao dịch một hàng (đo bằng vị trí các ô cùng hàng).
- **SC-002**: 375px và 768px không tràn ngang.
- **SC-003**: dữ liệu thật không đổi (SHA256).

## Assumptions
- "Rộng" = tới 1280px; ngưỡng một dòng theo bề rộng khung chứa ≥ 1060px.
