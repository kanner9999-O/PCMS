# Feature Specification: Kinh doanh TRX — thưởng staking, thuê Energy, bán TRX

**Feature Branch**: `006-trx-energy` (chưa bắt đầu)
**Created**: 2026-10-11 (migrate từ PRODUCT-SPEC §5 F07)
**Status**: Draft — backlog, **chưa triển khai**; có điểm nghiệp vụ còn mở nên cần `/speckit-clarify` trước khi plan
**Nguồn yêu cầu**: R33–R41, R48 · Chi tiết gốc: PRODUCT-SPEC.md dòng 270–343 (không sao chép lại ở đây)

## User Scenarios & Testing

### User Story 1 - Danh sách khách và công nợ dịch vụ (Priority: P1)
Mở TRX/Energy bằng danh sách khách, thông tin gói và công nợ; ghi tiền thu chọn rõ khách, phân bổ vào đúng khoản (R48).

**Independent Test**: ba kỳ × 100 USDT = phải thu 300; thu 200 còn 100; tiền chỉ ghi một lần ở ngày nhận.

### User Story 2 - Đơn thuê Energy và bán TRX (Priority: P1)
Hồ sơ khách → đơn gồm dòng Energy một lần/gói tháng/bán TRX; ghi nhận thủ công kèm bằng chứng. Gói tháng phí cố định dù không dùng (R37).

### User Story 3 - Thu bằng USDT hoặc VND quy đổi (Priority: P2)
Mỗi lần trả VND lưu VND thực nhận, tỷ giá nhập tay, thời điểm, USDT cấn nợ; không đổi lại theo giá thị trường (R36, R39).

### User Story 4 - Thưởng staking (Priority: P3)
Ghi thưởng theo ngày/nguồn/claim; APY chỉ tham khảo có nhãn (R33–R34).

### Edge Cases
- Thu thừa/trước: chờ phân bổ, không tự là doanh thu hay tất toán (R40).
- Ngày hết gói ≠ ngày thực thu hồi; lưu riêng.
- Không cộng TRX gốc hai lần giữa business và danh mục crypto.

## Requirements

### Functional Requirements
- **FR-001**: MUST là ghi nhận/quản lý tài chính thủ công; KHÔNG claim, delegate, unstake hay chuyển tài sản; KHÔNG quản gia hạn/cấp/cắt Energy hoặc nhắc gia hạn (R41).
- **FR-002**: Điều khoản thanh toán MUST lưu theo từng đơn; hạn thu sau phải là ngày cụ thể (R38).
- **FR-003**: Kỳ dịch vụ, hạn thanh toán, ngày thu thực MUST là ba mốc tách; quá hạn chỉ khi có hạn cam kết (R40).
- **FR-004**: Tiền thu MUST phân bổ vào nhiều dòng/đơn nhưng tổng khớp nguồn; không ghi tiền lần hai.
- **FR-005**: Tái dùng cơ chế phân bổ nguồn, snapshot bất biến, bảng kê đã có ở spec 001–004.

### Key Entities
Khách · Đơn (dòng Energy/Bán TRX) · Điều khoản · Khoản thu & phân bổ · Thưởng stake.

## Điểm còn mở (phải hỏi Thạch trước khi plan)
Lượng ghi trên gói tháng là mức cấp duy trì hay tổng hạn mức; đơn vị báo giá USD/USDT; nguồn tỷ giá; phương pháp ghi nhận doanh thu theo thời gian; giá vốn thưởng. Không tự chọn công thức.

## Success Criteria
- **SC-001**: PO kiểm bằng dữ liệu giả toàn luồng khách → đơn → thu → phân bổ → báo cáo → điều chỉnh (tiêu chí chi tiết chờ chốt ở ACCEPTANCE).
