# Feature Specification: Mua/bán/chuyển crypto

**Feature Branch**: `020-crypto-movements` · **Created**: 2026-10-13 · **Status**: Draft
**Input**: Thạch muốn ghi mua/bán/chuyển để số dư coin tự cập nhật thay vì xác nhận tay mọi lần (R97–R100). Tham chiếu spec 012 (crypto bản đầu), 013 (tổng tài sản), 017 (định dạng lịch sử). Không đổi quy tắc tiền, không quy đổi VND/USDT, không tính lãi/lỗ, không liên kết sao kê VND, không tự lấy giá/dữ liệu sàn.

## User Scenarios & Testing
### User Story 1 - Mua/bán coin trên một nơi giữ (Priority: P1)
Thạch ghi một lần mua hoặc bán: nơi giữ, coin (và mạng), số lượng, giá USDT mỗi coin, ngày, nguồn, phí tùy chọn. Số dư coin và số dư USDT của nơi giữ tự cộng trừ đúng.

**Independent Test**: Binance có mốc BTC 0,5 và USDT 10.000 ngày 01/10; mua 0,1 BTC giá 60.000 ngày 05/10 phí 6 USDT → BTC 0,6; USDT 10.000 − 6.000 − 6 = 3.994; bán 0,2 BTC giá 65.000 ngày 08/10 → BTC 0,4; USDT 3.994 + 13.000 = 16.994.

**Acceptance Scenarios**:
1. **Given** mốc xác nhận, **When** ghi mua/bán có ngày sau mốc, **Then** số dư coin và USDT của nơi giữ đổi đúng, kèm số giao dịch sau mốc.
2. **Given** giao dịch có ngày bằng hoặc trước mốc, **When** xem, **Then** không cộng lần nữa (mốc đã gồm).
3. **Given** phí bằng coin hoặc bằng USDT, **When** ghi, **Then** phí trừ vào đúng tài sản và hiển thị riêng.
4. **Given** thiếu nguồn/ngày/số lượng/giá hợp lệ, hoặc mua coin bằng chính nó, **When** lưu, **Then** bị chặn kèm lý do.
5. **Given** bán nhiều hơn số dư, **When** xem, **Then** số dư âm bị cảnh báo và không tính vào giá trị/tỷ trọng.

### User Story 2 - Chuyển giữa hai nơi giữ (Priority: P1)
Thạch ghi chuyển coin từ nơi giữ A sang B: số gửi, số nhận (chênh là phí mạng), ngày, nguồn.

**Independent Test**: chuyển 0,3 BTC từ Binance sang Ví lạnh nhận 0,2995 → Binance −0,3, Ví lạnh +0,2995, phí mạng 0,0005; tổng BTC giảm đúng 0,0005.

**Acceptance Scenarios**:
1. **Given** hai nơi giữ đang hoạt động khác nhau, **When** ghi chuyển, **Then** hai bên đổi đúng; số nhận lớn hơn số gửi hoặc cùng nơi bị chặn.
2. **Given** nơi nhận chưa có mốc cho coin đó, **When** xem, **Then** hiện số theo giao dịch kèm cảnh báo "chưa có mốc xác nhận".

### User Story 3 - Đối chiếu khi xác nhận lại, hủy giao dịch, xem lịch sử (Priority: P2)
Xác nhận số dư mới sau khi đã có giao dịch: hệ thống so với số sổ cái và báo chênh lệch, không tự sửa. Hủy giao dịch giữ bản ghi. Danh sách giao dịch xem được theo thứ tự mới nhất trước.

**Acceptance Scenarios**:
1. **Given** sổ cái nói 0,4 BTC, **When** xác nhận 0,39, **Then** hiện "chênh −0,01 so với sổ cái" và số hiện tại là 0,39 (mốc mới).
2. **Given** giao dịch đã hủy, **When** xem, **Then** không tính vào số dư, vẫn hiện trong lịch sử kèm lý do.
3. **Given** tổng tài sản (spec 013), **When** có giao dịch, **Then** giá trị crypto dùng số lượng sổ cái.

### Edge Cases
- Coin cùng ticker khác mạng tách riêng; USDT dùng mạng ghi trên giao dịch (mặc định rỗng) phải khớp mốc.
- Nơi giữ đã lưu trữ: không nhận giao dịch mới; số cũ giữ.
- Ngày giao dịch trước mốc bắt đầu theo dõi của nơi giữ: bị chặn.
- Chỉ trạng thái "đang giữ" bị ảnh hưởng; Earn, ký quỹ, vị thế, nợ margin giữ như xác nhận tay.

## Requirements
- **FR-001** (R97): số lượng "đang giữ" của (nơi giữ, coin, mạng) = mốc xác nhận mới nhất + giao dịch có ngày **sau** ngày mốc; không có mốc thì = tổng giao dịch kèm cảnh báo.
- **FR-002** (R98): hành động ghi mua, bán, chuyển (nơi giữ đang hoạt động, ngày, nguồn bắt buộc; số lượng ≤ 18 chữ số thập phân; giá > 0 ≤ 12 chữ số thập phân) và hủy có lý do; chỉ USDT, không liên kết sao kê VND.
- **FR-003** (R100): phí tùy chọn bằng coin hoặc bằng đồng định giá, trừ vào đúng tài sản; chuyển: số nhận ≤ số gửi, chênh là phí mạng.
- **FR-004** (R99): không tính lãi/lỗ đã thực hiện; giữ nguyên chênh lệch chưa thực hiện của spec 012.
- **FR-005** (R97): khi xác nhận mới có giao dịch trong khoảng sau mốc trước, hiển thị chênh lệch (xác nhận − sổ cái), không sửa dữ liệu.
- **FR-006**: số dư âm không vào giá trị, tỷ trọng, tổng; cảnh báo hiển thị.
- **FR-007**: danh sách giao dịch (mới nhất trước) với nhãn mua/bán/chuyển, số lượng, giá, USDT, phí, nơi giữ, trạng thái; hủy giữ bản ghi.
- **FR-008**: không đổi Earn/ký quỹ/vị thế/nợ margin, giá, vốn, tổng tài sản ngoài việc dùng số lượng sổ cái.

## Success Criteria
- **SC-001**: các ví dụ số ở Story 1–2 cho đúng số (tính tay khớp 100%).
- **SC-002**: không có giao dịch thì mọi số liệu giống hệt trước đợt này (hồi quy P14, P15 giữ nguyên).
- **SC-003**: ghi một lần mua/bán ≤ 1 hộp thoại; dữ liệu thật không đổi (SHA256).

## Assumptions
- Giao dịch cùng ngày với mốc được coi là đã nằm trong mốc.
- Đồng định giá mặc định USDT, mạng rỗng; Thạch có thể nhập mạng nếu mốc USDT có mạng.
- Số dư âm có thể do thiếu mốc hoặc nhập sai; hệ thống chỉ cảnh báo.
