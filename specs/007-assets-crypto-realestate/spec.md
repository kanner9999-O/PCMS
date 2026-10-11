# Feature Specification: Tài sản — crypto/ví, BĐS, định giá và tổng quan

**Feature Branch**: `007-assets-crypto-realestate` (chưa bắt đầu)
**Created**: 2026-10-11 (migrate từ PRODUCT-SPEC §3, §5 F05, mục BĐS)
**Status**: Draft — backlog, **chưa triển khai**; nhiều công thức còn mở
**Nguồn yêu cầu**: R01, R11, R15, R16, R18, R19, R23, R25, R26, R27 · Cổ phiếu (R24), chốt tháng (R22), Shop (R08, R28, R32): **PENDING** — không đưa vào đây, không tự mở lại

## User Scenarios & Testing

### User Story 1 - Ví và sàn crypto từ một mốc (Priority: P1)
Khai báo Binance, BingX và các ví riêng bằng tên dễ nhớ; số lượng từng coin tại mốc bắt đầu (không bắt buộc nhập lại toàn lịch sử, R25–R26). Số lượng mốc là trạng thái ban đầu, không tính là thu nhập hay giao dịch mua.

**Independent Test**: khai ví với 3 coin → xem theo nơi giữ và theo coin; không cộng tổng sàn thêm với thành phần của nó.

### User Story 2 - BĐS với vốn, quyền lợi, thế chấp (Priority: P2)
Mỗi BĐS có vốn đã góp, chi phí, quyền lợi, giá trị hiện tại có ngày/nguồn; tài sản thế chấp liên kết khoản vay (không cộng nợ hai lần); căn chung cư theo tiến độ ghi giá hợp đồng/đã trả/còn cam kết (R27).

### User Story 3 - Tổng quan và tỷ trọng (Priority: P3)
Hiển thị vốn bỏ vào và giá trị hiện tại; tỷ trọng theo giá trị hiện tại; theo nơi giữ (R15, R18).

### Edge Cases
- Không gộp tài sản chỉ vì trùng ticker; chưa rõ thì giữ tách và đánh dấu chờ xác minh.
- Không dùng giá trị danh nghĩa futures làm giá trị tài sản; không cộng ký quỹ hai lần (R19).
- Vốn lịch sử thiếu = "chưa xác định", không thay bằng giá tại mốc.

## Requirements

### Functional Requirements
- **FR-001**: Không yêu cầu seed phrase/private key; không kết nối tự động sàn/ngân hàng.
- **FR-002**: VND giữ VND, USDT giữ USDT; tổng hợp USDT là hướng tương lai (R09).
- **FR-003**: Lãi/lỗ chỉ hiển thị trong phạm vi có đủ căn cứ vốn.
- **FR-004**: Tái dùng nền tảng nguồn/snapshot/bảng kê của 001–004.

## Điểm còn mở (phải hỏi Thạch)
Cách tính vốn khi bán một phần; mẫu số tỷ trọng (tiền mặt, phải thu, trừ nợ); nguồn và ngày giá; tỷ giá/FX; danh sách coin theo ví; mẫu dữ liệu sàn; trường đặc thù futures/margin/Earn; quyền lợi các BĐS góp vốn; tổng số BĐS.

## Success Criteria
- **SC-001**: chờ chốt công thức; không nghiệm thu bằng số tổng khi chưa có chính sách định giá.
