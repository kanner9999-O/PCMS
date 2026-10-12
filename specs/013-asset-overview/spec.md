# Feature Specification: Tổng hợp tài sản bản đầu

**Feature Branch**: `013-asset-overview`
**Created**: 2026-10-12
**Status**: Draft
**Input**: Thạch yêu cầu làm tiếp tổng hợp tài sản (12/10/2026) và đã chốt qua phỏng vấn: không quy đổi tiền tệ (hai tổng VND và USDT riêng); tài sản, nợ và tài sản ròng hiển thị riêng; có lưu bản chụp theo ngày. Thạch giao PO quyết định cách tính BĐS chưa có giá trị hiện tại theo nghiệp vụ kế toán. Nguồn yêu cầu: R09, R15, R18, R19, R42, R77–R80 · Spec liên quan: 002 (công nợ), 004, 006 (TRX/Energy), 011 (BĐS), 012 (crypto).

**Phạm vi:** màn **Tổng tài sản** chỉ hợp nhất dữ liệu đã có, không nhập thêm số liệu mới và không đổi quy tắc ở các phân hệ nguồn. Không quy đổi tiền tệ, không tỷ giá, không phân tích rủi ro/đầu tư, không cổ phiếu/shop.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Thấy tổng tài sản, nợ và tài sản ròng theo từng đồng tiền (Priority: P1)
Thạch mở màn Tổng tài sản thấy hai khối riêng, **VND** và **USDT**; mỗi khối có tài sản theo từng nhóm, nợ theo từng nhóm, tài sản ròng (tài sản − nợ) và tỷ trọng từng nhóm trong tổng tài sản của đồng tiền đó.

**Why this priority**: R15 — Thạch cần biết tiền đang ở đâu và tỷ trọng; R77/R78 — không quy đổi, tài sản, nợ, ròng hiển thị riêng.

**Independent Test**: dữ liệu giả: ngân hàng 200.000.000; cho vay còn phải thu 100.000.000; BĐS giá trị hiện tại 900.000.000; vay phải trả 300.000.000 → khối VND: tài sản 1.200.000.000 (ngân hàng 16,67% · phải thu 8,33% · BĐS 75%), nợ 300.000.000, ròng 900.000.000; crypto 73.150 USDT + phải thu khách 300 USDT − nhận trước 100 USDT → khối USDT: tài sản 73.450, nợ 100, ròng 73.350; không có số hợp nhất VND+USDT.

**Acceptance Scenarios**:
1. **Given** dữ liệu ở nhiều phân hệ, **When** mở màn, **Then** hiển thị hai khối VND và USDT độc lập, mỗi khối có tài sản, nợ, tài sản ròng và tỷ trọng theo nhóm.
2. **Given** một nhóm không có dữ liệu, **When** xem, **Then** nhóm hiển thị "chưa có dữ liệu" (không phải 0 như đã đối soát) và không vào tỷ trọng.
3. **Given** bất kỳ dữ liệu, **When** xem, **Then** không có con số cộng VND với USDT.
4. **Given** tài khoản ngân hàng đã lưu trữ hoặc nơi giữ crypto đã lưu trữ, **When** tính tổng, **Then** bị loại khỏi tổng như ở phân hệ nguồn.

### User Story 2 - Cơ sở tính và cảnh báo độ tin cậy (Priority: P1)
Mỗi nhóm ghi rõ cơ sở tính và nguồn; bất động sản chưa có giá trị hiện tại được tính theo **giá gốc** (vốn đã thanh toán ròng) và đánh dấu "theo giá gốc, chưa định giá"; có danh sách cảnh báo độ tin cậy.

**Why this priority**: R79 (quyết định theo nghiệp vụ kế toán) và nguyên tắc không tự khẳng định số chưa đủ căn cứ.

**Independent Test**: hai BĐS: A có giá trị hiện tại 900 triệu, B chưa có giá trị và vốn ròng 200 triệu → BĐS tổng 1.100 triệu, tách "theo giá trị hiện tại 900 triệu" và "theo giá gốc 200 triệu (B)"; cảnh báo B chưa định giá; coin XYZ chưa giá nằm ngoài tổng USDT và có cảnh báo.

**Acceptance Scenarios**:
1. **Given** BĐS có giá trị hiện tại, **When** xem, **Then** dùng giá trị hiện tại, cơ sở "giá trị hiện tại" kèm ngày.
2. **Given** BĐS chưa có giá trị hiện tại nhưng có vốn ròng dương, **When** xem, **Then** dùng vốn ròng, cơ sở "giá gốc, chưa định giá", tách riêng trong tổng BĐS.
3. **Given** BĐS không có cả giá trị và vốn dương, **When** xem, **Then** nằm ngoài tổng, liệt kê "chưa có giá trị".
4. **Given** còn giao dịch chưa phân loại, khoảng chưa có nguồn, khoản vay lỗi/chưa thiết lập, coin chưa giá, **When** xem, **Then** mỗi trường hợp có cảnh báo kèm số lượng và lối tới màn nguồn.
5. **Given** số tiền ngân hàng, **When** xem, **Then** ghi "theo dữ liệu nguồn đã ghi đến ngày …", không phải số dư thực đã đối soát.

### User Story 3 - Quy tắc không tính đôi và không dồn tích (Priority: P1)
Khoản vay thế chấp chỉ nằm ở phần nợ, không bị trừ vào giá trị BĐS; nợ margin và vị thế sàn không cộng/trừ; lãi cho vay không dồn tích (chỉ gốc).

**Independent Test**: BĐS thế chấp khoản vay 300 triệu → BĐS vẫn tính đủ giá trị, khoản vay hiện ở nợ phải trả; BingX có vị thế và nợ margin → không đổi tài sản USDT; khoản cho vay có lãi chưa thu → phải thu chỉ gồm gốc.

### User Story 4 - Lưu bản chụp và so sánh (Priority: P2)
Thạch bấm "Lưu bản chụp" để ghi lại tổng, từng thành phần, cơ sở tính, cảnh báo và ngày; bản chụp bất biến. Màn hiển thị danh sách bản chụp và chênh lệch giữa hiện tại và lần chụp gần nhất (theo từng tổng, từng đồng tiền).

**Independent Test**: lưu bản chụp S1; thêm giá trị BĐS mới; xem: hiện tại so với S1 có chênh lệch đúng; S1 không đổi; lưu S2 thì S1 vẫn nguyên và S2 so với S1.

**Acceptance Scenarios**:
1. **Given** dữ liệu hiện tại, **When** bấm lưu bản chụp, **Then** bản ghi bất biến gồm ngày, tổng, nhóm, cơ sở, cảnh báo và mã kiểm chứng.
2. **Given** có bản chụp, **When** dữ liệu nguồn đổi, **Then** bản chụp cũ giữ nguyên số liệu lúc chụp.
3. **Given** nhiều bản chụp, **When** xem danh sách, **Then** mỗi bản chụp hiển thị chênh lệch so với bản trước đó.
4. **Given** chưa có bản chụp, **When** xem, **Then** hiển thị "chưa có bản chụp" và không hiển thị chênh lệch.

### Edge Cases
- Không có dữ liệu nào ở một đồng tiền: khối hiển thị "chưa có dữ liệu", không có tỷ trọng.
- Tài sản ròng âm: hiển thị số âm đúng nghĩa kèm nhãn "nợ lớn hơn tài sản", không cắt về 0.
- Phải thu khách TRX/Energy tính theo số còn nợ USDT; tiền khách nhận chưa phân bổ là nợ (nhận trước), không là doanh thu.
- Khoản vay có lỗi/chưa thiết lập: không vào phải thu/phải trả (như ở Công nợ) và được đếm trong cảnh báo.
- Tài khoản ngân hàng có khoảng chưa có nguồn hoặc chưa duyệt: vẫn tính theo dữ liệu đã ghi nhưng có cảnh báo.
- Thưởng staking TRX chỉ ghi số lượng: không vào tổng (thông tin phụ).
- Bản chụp lưu khi có cảnh báo: cảnh báo được lưu cùng.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Màn Tổng tài sản MUST hiển thị hai khối độc lập VND và USDT; MUST NOT cộng hay quy đổi giữa hai đồng tiền (R77, R09).
- **FR-002**: Khối VND MUST gồm tài sản: tiền các tài khoản ngân hàng đang hoạt động (số dư theo dữ liệu nguồn đã ghi), phải thu gốc cho vay, bất động sản; nợ: phải trả gốc đi vay; tài sản ròng = tài sản − nợ (R78).
- **FR-003**: Khối USDT MUST gồm tài sản: giá trị crypto có giá, phải thu khách TRX/Energy còn nợ; nợ: tiền khách nhận trước chờ phân bổ; tài sản ròng = tài sản − nợ (R78).
- **FR-004**: Bất động sản MUST dùng giá trị hiện tại do người dùng nhập khi có; nếu chưa có thì dùng vốn đã thanh toán ròng dương theo nguyên tắc giá gốc, ghi rõ cơ sở "theo giá gốc, chưa định giá" và tách riêng trong tổng BĐS; BĐS không có cả hai MUST nằm ngoài tổng và được liệt kê (R79).
- **FR-005**: Khoản vay thế chấp MUST chỉ tính ở nợ phải trả và MUST NOT bị trừ vào giá trị BĐS; nợ margin và vị thế đang mở MUST NOT cộng hay trừ vào tài sản (R19, R78).
- **FR-006**: Phải thu và phải trả MUST chỉ gồm gốc, MUST NOT dồn tích lãi (R42); khoản vay lỗi/chưa thiết lập MUST bị loại khỏi tổng như ở Công nợ và được đếm trong cảnh báo.
- **FR-007**: Mỗi nhóm MUST hiển thị tỷ trọng trong tổng tài sản của đồng tiền đó (chỉ nhóm có dữ liệu); nhóm không có dữ liệu MUST hiển thị "chưa có dữ liệu" và MUST NOT hiện 0 như đã đối soát.
- **FR-008**: Mỗi thành phần MUST ghi cơ sở tính, ngày của số liệu (khi có) và lối mở màn nguồn (ngân hàng, Công nợ, Bất động sản, Crypto, TRX/Energy).
- **FR-009**: Màn MUST có danh sách cảnh báo độ tin cậy với số lượng: giao dịch chưa phân loại, khoảng chưa có nguồn, khoản vay lỗi/chưa thiết lập, coin chưa có giá, BĐS theo giá gốc, BĐS chưa có giá trị.
- **FR-010**: Hệ thống MUST cho lưu bản chụp bất biến gồm ngày giờ, các tổng, từng nhóm, cơ sở tính, cảnh báo và mã kiểm chứng; MUST hiển thị danh sách bản chụp và chênh lệch giữa hiện tại và bản chụp gần nhất, và giữa từng bản chụp với bản trước nó; bản chụp MUST NOT bị sửa hay xóa (R80).
- **FR-011**: Tính năng MUST NOT đổi kết quả, snapshot, công nợ, danh mục, BĐS, crypto, TRX/Energy đã có; MUST NOT yêu cầu nhập số liệu mới; MUST NOT sửa dữ liệu vận hành khi kiểm thử.

### Key Entities
- **Tổng tài sản (hiện tại)**: dẫn xuất từ các phân hệ, theo đồng tiền: nhóm tài sản, nhóm nợ, tổng, ròng, tỷ trọng, cảnh báo.
- **Bản chụp tổng tài sản**: ngày giờ, ghi chú, bản sao các tổng và nhóm, cảnh báo, mã kiểm chứng.

## Success Criteria *(mandatory)*
- **SC-001**: Với bộ dữ liệu ví dụ (ngân hàng 200 triệu, phải thu 100 triệu, BĐS 900 triệu, nợ 300 triệu; crypto 73.150 USDT + phải thu 300 − nhận trước 100) màn hiển thị đúng tài sản 1,2 tỷ VND, nợ 300 triệu, ròng 900 triệu; tài sản 73.450 USDT, nợ 100, ròng 73.350 USDT; tỷ trọng đúng; 0 con số hợp nhất hai đồng tiền.
- **SC-002**: Mọi BĐS tính theo giá gốc luôn được gắn nhãn cơ sở và liệt kê (100% trường hợp thử); BĐS thế chấp không bị trừ nợ.
- **SC-003**: Nhóm không có dữ liệu hiển thị "chưa có dữ liệu" 100% trường hợp thử, không bao giờ hiện 0 như đã đối soát.
- **SC-004**: Bản chụp giữ nguyên số liệu sau khi dữ liệu nguồn thay đổi (100% trường hợp thử) và chênh lệch so với bản trước đúng.
- **SC-005**: 0 thay đổi ở snapshot, báo cáo, công nợ, danh mục, BĐS, crypto, TRX/Energy đã có; checksum dữ liệu vận hành không đổi.

## Assumptions
- Quyết định giá gốc cho BĐS chưa định giá do PO đưa ra theo nghiệp vụ kế toán (nguyên tắc giá gốc), theo ủy quyền của Thạch; Thạch phản hồi nếu muốn cách khác.
- Số dư ngân hàng là số theo dữ liệu nguồn đã ghi (cộng cả giao dịch chưa duyệt/chưa phân loại), kèm cảnh báo khi còn dòng chưa phân loại hoặc khoảng thiếu nguồn.
- Phải thu/phải trả là gốc theo dữ liệu Công nợ (nháp), không gồm lãi chưa thu (lãi ghi theo tiền thực thu).
- Phải thu khách TRX/Energy và tiền nhận trước chỉ tính trên đơn/khoản thu còn hiệu lực (không tính đã hủy).
- Thưởng staking TRX và số lượng TRX bán chỉ là thông tin số lượng, không vào tổng.
- Tổng tài sản không bao gồm cổ phiếu, shop, chung cư theo tiến độ (chưa triển khai).
- Chỉ VND và USDT như các đợt trước; tài khoản ngân hàng chỉ VND.
