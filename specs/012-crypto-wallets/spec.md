# Feature Specification: Crypto / ví bản đầu

**Feature Branch**: `012-crypto-wallets`
**Created**: 2026-10-12
**Status**: Draft
**Input**: Thạch yêu cầu làm tiếp phần crypto/ví (12/10/2026) và đã trả lời phỏng vấn: cập nhật số lượng bằng xác nhận số dư theo ngày; bản đầu có giá nhập tay và tách trạng thái trên sàn; giá trị USDT, tỷ trọng theo nơi giữ và theo coin. Nguồn yêu cầu: R01, R09, R15, R16, R18, R19, R23, R25, R26, R74–R76 · Spec liên quan: 007 (backlog tài sản), 011 (BĐS).

**Phạm vi:** ghi nhận thủ công số dư coin theo nơi giữ, giá nhập tay, vốn tùy chọn, giá trị và tỷ trọng. **Không** gồm: tự tính số lượng từ giao dịch mua/bán/chuyển, giá tự động, tích hợp sàn/ví, tổng tài sản hợp nhất, chung cư tiến độ. Không lưu seed phrase/private key.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Nơi giữ và số dư coin theo xác nhận (Priority: P1)
Thạch khai báo các nơi giữ (ví riêng, Binance, BingX) và xác nhận số lượng từng coin tại một ngày kèm nguồn (ảnh chụp, mã giao dịch, ghi chú). Số hiện tại là lần xác nhận có ngày mới nhất; mọi lần xác nhận giữ trong lịch sử, hủy được kèm lý do.

**Why this priority**: R74 — theo dõi từ một mốc, không nhập lại toàn bộ lịch sử; đây là nền cho giá trị và tỷ trọng.

**Independent Test**: ví "Ví lạnh 1" xác nhận BTC 0,5 ngày 01/10; xác nhận lại BTC 0,6 ngày 08/10 → số hiện tại 0,6 và lịch sử có cả hai; hủy lần 08/10 (lý do) → hiện tại quay về 0,5.

**Acceptance Scenarios**:
1. **Given** một nơi giữ, **When** xác nhận số lượng coin với ngày, nguồn, **Then** số hiện tại cập nhật và lịch sử ghi đủ.
2. **Given** hai xác nhận cùng coin, **When** xem, **Then** số hiện tại là bản có ngày mới nhất (hòa ngày thì bản tạo sau).
3. **Given** xác nhận thiếu nguồn hoặc ngày, **When** lưu, **Then** bị chặn kèm lý do.
4. **Given** coin cùng ticker nhưng khác mạng (ví dụ USDT mạng TRC20 và ERC20), **When** xem, **Then** hiển thị tách riêng, không gộp.
5. **Given** xác nhận số lượng bằng 0, **When** lưu, **Then** hợp lệ (coin đã rút hết) và hiển thị số hiện tại bằng 0.

### User Story 2 - Tách trạng thái trên sàn (Priority: P1)
Với Binance/BingX, mỗi coin có thể xác nhận riêng các trạng thái: đang giữ, đang Earn/khóa, ký quỹ, vị thế đang mở, nợ margin. Các số hiển thị riêng; tổng sàn chỉ là tổng các thành phần tài sản, không cộng đôi.

**Why this priority**: R19 — không lấy giá trị danh nghĩa futures làm tài sản, không cộng ký quỹ hai lần, nợ margin hiển thị riêng.

**Independent Test**: BingX: BTC đang giữ 0,2, ký quỹ 0,1, vị thế đang mở 5 hợp đồng, nợ margin 0,05 → giá trị tài sản chỉ tính 0,2 + 0,1; vị thế và nợ hiển thị riêng, không cộng, không trừ.

**Acceptance Scenarios**:
1. **Given** ví riêng, **When** xác nhận số dư, **Then** chỉ có trạng thái "đang giữ" (ví không có Earn/margin).
2. **Given** sàn, **When** xem một coin, **Then** thấy từng trạng thái riêng kèm ngày và nguồn từng lần xác nhận.
3. **Given** vị thế đang mở hoặc nợ margin, **When** tính giá trị, **Then** không được cộng vào giá trị tài sản và không trừ vào; hiển thị ở khu riêng kèm nhãn.
4. **Given** nhập số trạng thái, **When** xem tổng nơi giữ, **Then** tổng là tổng các thành phần tài sản (đang giữ, Earn/khóa, ký quỹ) đã có giá, hiển thị kèm ghi chú "người dùng xác nhận các thành phần không chồng nhau".

### User Story 3 - Giá hiện tại, giá trị USDT và tỷ trọng (Priority: P1)
Thạch nhập giá hiện tại của từng coin bằng USDT kèm ngày và nguồn (giữ lịch sử, hủy có lý do). App hiển thị giá trị USDT của từng coin/nơi giữ và tỷ trọng theo nơi giữ và theo coin, chỉ cho coin có giá; coin chưa có giá liệt kê riêng "chưa có giá".

**Why this priority**: R15, R18, R76 — Thạch cần biết tiền đang ở đâu và tỷ trọng, nhưng không có giá tự động.

**Independent Test**: BTC 0,5 @ 60.000 USDT = 30.000; ETH 10 @ 2.500 = 25.000; coin XYZ chưa có giá → tổng 55.000, BTC 54,55%, ETH 45,45%; XYZ nằm ở danh sách "chưa có giá"; tỷ trọng theo nơi giữ tính tương tự.

**Acceptance Scenarios**:
1. **Given** chưa có giá, **When** xem, **Then** coin hiện số lượng, "chưa có giá", không có giá trị, không vào mẫu số tỷ trọng.
2. **Given** nhiều giá, **When** xem, **Then** giá hiện tại là bản có ngày mới nhất, hiển thị kèm ngày và nguồn.
3. **Given** giá nhập tay có ngày cũ, **When** xem, **Then** hiển thị ngày giá để Thạch thấy độ cũ.
4. **Given** tỷ trọng, **When** hiển thị, **Then** chỉ trong phạm vi tài sản crypto có giá, không đặt ngưỡng rủi ro, mẫu số nêu rõ.

### User Story 4 - Vốn bỏ vào và mốc theo dõi (Priority: P2)
Thạch ghi vốn bỏ vào của từng coin (USDT) nếu biết, kèm nguồn và ngày; thiếu vốn thì "chưa xác định". Khi có vốn và giá, hiển thị vốn cạnh giá trị và chênh lệch có nhãn "chưa thực hiện, không phải lãi/lỗ". Mỗi nơi giữ có mốc bắt đầu theo dõi tùy chọn.

**Independent Test**: BTC vốn 25.000 USDT, giá trị 30.000 → chênh lệch +5.000 có nhãn; coin không có vốn → "vốn chưa xác định", không chênh lệch, không lãi/lỗ.

### Edge Cases
- Hai nơi giữ cùng một coin: giá trị và tỷ trọng theo coin gộp các nơi giữ (vì cùng định danh ticker + mạng), tỷ trọng theo nơi giữ tách riêng.
- Xác nhận số dư ngày trước mốc bắt đầu theo dõi: bị chặn kèm lý do.
- Số lượng có phần thập phân dài (đến 18 chữ số thập phân): giữ đúng, không làm tròn.
- Giá bằng 0 hoặc âm: bị chặn.
- Nơi giữ đã lưu trữ: ẩn khỏi lựa chọn mới, lịch sử vẫn xem được, không tính vào tổng hiện tại.
- Coin chưa ghi mạng: hiển thị "chưa ghi mạng" và vẫn tách khỏi coin cùng ticker đã ghi mạng.
- Không có seed phrase/private key ở bất kỳ ô nào; ô nguồn chỉ là mô tả bằng chứng.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Hệ thống MUST cho khai báo nơi giữ (ví riêng hoặc sàn) có tên, loại, mốc bắt đầu theo dõi tùy chọn, ghi chú; cho lưu trữ có lý do, không xóa.
- **FR-002**: Hệ thống MUST cho xác nhận số dư coin theo nơi giữ gồm: ticker, mạng (tùy chọn), trạng thái, số lượng ≥ 0 (tối đa 18 chữ số thập phân), ngày, nguồn bắt buộc; số hiện tại của mỗi (nơi giữ, coin, trạng thái) là bản hiệu lực có ngày mới nhất (R74).
- **FR-003**: Ví riêng MUST chỉ có trạng thái đang giữ; sàn MUST có năm trạng thái: đang giữ, đang Earn/khóa, ký quỹ, vị thế đang mở, nợ margin (R75, R19).
- **FR-004**: Mọi xác nhận, giá và vốn MUST có lịch sử, hủy cần lý do, không xóa bản ghi.
- **FR-005**: Giá trị tài sản MUST chỉ tính từ các trạng thái đang giữ, đang Earn/khóa và ký quỹ có giá; vị thế đang mở và nợ margin MUST hiển thị riêng, MUST NOT cộng hoặc trừ vào giá trị tài sản (R19).
- **FR-006**: Giá hiện tại MUST do người dùng nhập bằng USDT dương kèm ngày và nguồn; hiển thị ngày giá; coin chưa có giá MUST hiển thị "chưa có giá" và MUST NOT vào giá trị hoặc mẫu số tỷ trọng.
- **FR-007**: Giá trị MUST hiển thị bằng USDT theo coin, theo nơi giữ, và tổng; tỷ trọng MUST hiển thị theo nơi giữ và theo coin, chỉ trên tài sản có giá, nêu rõ mẫu số; MUST NOT đặt ngưỡng rủi ro (R76).
- **FR-008**: Coin MUST được định danh bằng ticker và mạng; coin khác mạng hoặc chưa ghi mạng MUST tách riêng, MUST NOT gộp theo ticker (R76).
- **FR-009**: Vốn bỏ vào MUST ghi theo từng coin (USDT dương, ngày, nguồn); thiếu vốn MUST hiển thị "chưa xác định"; chênh lệch (giá trị − vốn) chỉ hiển thị khi có cả vốn và giá và MUST mang nhãn "chưa thực hiện, không phải lãi/lỗ" (R18).
- **FR-010**: Hệ thống MUST NOT tự suy số lượng từ giao dịch ngân hàng hoặc giao dịch sàn, MUST NOT lấy giá tự động, MUST NOT tích hợp sàn/ví, MUST NOT yêu cầu hay lưu seed phrase/private key.
- **FR-011**: Thay đổi MUST NOT đổi kết quả báo cáo, snapshot, công nợ, danh mục, BĐS đã có; MUST NOT sửa dữ liệu vận hành khi kiểm thử.

### Key Entities
- **Nơi giữ**: tên, loại (ví riêng/sàn), mốc theo dõi, trạng thái (hoạt động/lưu trữ).
- **Xác nhận số dư**: nơi giữ, coin (ticker + mạng), trạng thái, số lượng, ngày, nguồn, trạng thái bản ghi.
- **Giá**: coin, giá USDT, ngày, nguồn.
- **Vốn**: coin, số tiền USDT, ngày, nguồn.

## Success Criteria *(mandatory)*
- **SC-001**: Với ví lạnh BTC 0,5 → xác nhận lại 0,6 → hủy, hiện tại quay về 0,5 và lịch sử đủ ba bản ghi; xác nhận một số dư trong tối đa 3 thao tác.
- **SC-002**: Với BTC 0,5 @ 60.000 và ETH 10 @ 2.500, tổng giá trị 55.000 USDT, tỷ trọng 54,55% / 45,45%; coin chưa có giá nằm ngoài mẫu số 100% trường hợp thử.
- **SC-003**: Vị thế đang mở và nợ margin xuất hiện ở khu riêng và 0 lần được cộng/trừ vào giá trị tài sản.
- **SC-004**: Coin cùng ticker khác mạng luôn hiển thị tách riêng (100% trường hợp thử); 0 tỷ lệ/lãi/lỗ suy ra khi thiếu vốn hoặc giá.
- **SC-005**: 0 thay đổi ở snapshot, báo cáo, công nợ, danh mục, BĐS đã có; checksum dữ liệu vận hành không đổi.

## Assumptions
- Phạm vi do Thạch trả lời phỏng vấn 12/10/2026 (R74–R76).
- Người dùng tự bảo đảm các thành phần trạng thái trên sàn không chồng nhau (app không kiểm chéo với số tổng sàn).
- Giá trị và tỷ trọng chỉ trong phạm vi tài sản crypto, không hợp nhất với BĐS/tiền ngân hàng (tổng tài sản hợp nhất để đợt sau).
- Chỉ USDT là đơn vị giá trị; không quy đổi VND.
- Nguồn xác nhận là mô tả bằng chữ (ảnh chụp màn hình, mã giao dịch…), app không lưu tệp.
