# Feature Specification: Kinh doanh TRX — thưởng staking, thuê Energy, bán TRX

**Feature Branch**: `006-trx-energy`
**Created**: 2026-10-11 (migrate từ PRODUCT-SPEC §5 F07)
**Status**: Clarified 11/10/2026 → đang triển khai bản đầu (xem Clarifications)
**Nguồn yêu cầu**: R33–R41, R48, R63–R66 · Chi tiết gốc: PRODUCT-SPEC.md dòng 270–343 (không sao chép lại ở đây)

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
- **FR-005**: Công nợ khách tính bằng USDT; thu VND quy đổi bằng tỷ giá người dùng nhập tại lần thu (R64, R39).
- **FR-006**: Báo cáo theo tiền thực thu, không chia theo thời gian dịch vụ; không lãi/lỗ bán TRX; thưởng chỉ ghi số lượng (R65, R66).
- **FR-007**: Gói tháng chỉ ghi nhận tài chính: tên gói, mức cấp, phí, khoảng dịch vụ; không điều khiển cấp/thu hồi (R41, R63).

### Key Entities
Khách · Đơn (dòng Energy/Bán TRX) · Điều khoản · Khoản thu & phân bổ · Thưởng stake.

## Clarifications

### Session 2026-10-11 (Thạch trả lời phỏng vấn, ghi ở PRODUCT-SPEC R63–R66)
- Q: Gói tháng "1 triệu Energy" nghĩa là gì? → A: mức cấp duy trì; app chỉ ghi nhận tài chính (R63).
- Q: Đơn vị báo giá? → A: USDT; khách trả VND thì ghi VND + tỷ giá nhập tay + USDT cấn (R64).
- Q: Doanh thu gói tháng? → A: theo tiền thực thu, không chia theo thời gian dịch vụ (R65).
- Q: Bán TRX/thưởng có tính lãi/lỗ không? → A: chưa, chỉ ghi số lượng và tiền thu (R66).

## Phạm vi bản đầu (quyết định PO để triển khai)
Ghi nhận thủ công: khách → đơn (dòng Energy một lần / gói tháng / bán TRX, điều khoản thu trước-sau lưu theo đơn, hạn thu nếu có) → khoản thu (USDT hoặc VND quy đổi, tùy chọn gắn giao dịch ngân hàng đã có để không ghi tiền hai lần) → phân bổ vào dòng; phần chưa phân bổ nằm "chờ phân bổ" → thưởng staking ghi số lượng → báo cáo theo tiền thực thu (tuần/tháng/quý). Không snapshot riêng, không tự quá hạn, không tích hợp blockchain.

Chưa làm ở bản đầu (backlog): snapshot/duyệt riêng cho TRX, lãi/lỗ bán TRX, nguồn USDT tự động từ ví/sàn (khoản thu USDT nhập tay kèm ghi chú bằng chứng).

## Success Criteria
- **SC-001**: Ba kỳ gói tháng × 100 USDT cho một khách → phải thu 300 USDT; thu 200 USDT phân bổ hai dòng → còn nợ 100; tiền chỉ ghi một lần ở ngày nhận.
- **SC-002**: Khách trả VND: lưu VND thực nhận, tỷ giá, USDT cấn; đổi tỷ giá lần sau không đổi lần trước; ngân hàng không tăng USDT.
- **SC-003**: Gắn một giao dịch ngân hàng vào khoản thu chỉ một lần cho số tiền của nó; vượt số tiền bị chặn.
- **SC-004**: Báo cáo tuần/tháng/quý chỉ hiện tiền thực thu theo ngày nhận, tách loại dòng, VND riêng, số TRX bán/thưởng; không có chỉ tiêu lãi/lỗ; không có "quá hạn" khi đơn không có hạn.
- **SC-005**: Void có lý do hoàn số liệu và giữ bản ghi; dữ liệu `outputs/p01-user-trial` không đổi checksum.
