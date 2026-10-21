# Feature Specification: Đồng nhất mô hình đối tượng – danh mục – khoản vay – nghiệp vụ trên toàn hệ thống

**Feature Branch**: `041-unified-object-model`

**Created**: 2026-10-21

**Status**: Draft (chờ phỏng vấn gộp)

**Input**: Thạch phản ánh các màn hình không ăn khớp và phải sửa từng màn. Thạch yêu cầu rà soát toàn hệ thống rồi làm **một đợt** theo đầy đủ quy trình Spec Kit (Constitution IX). Spec bao trùm và thay thế phần chồng lấn của spec 031, 032, 033, 035, 037, 040. Tham chiếu: Constitution VII, VIII, IX; R84–R86, R136, R146–R184.

## Mô hình đã chốt (nguồn: Thạch, 15–21/10/2026)
1. **Danh mục** là cây cha → con nhiều cấp, chỉ tổng hợp dòng tiền (nhóm mặc định); không mang nghiệp vụ.
2. **Đối tượng** = tên riêng (duy nhất toàn hệ thống) + loại (Người, Bất động sản, Khác; thêm loại sau). Một đối tượng thuộc 0..n danh mục. Danh mục có 0..n đối tượng.
3. **Khoản vay thuộc về một người**, hiện bên trong đối tượng Người; không là loại đối tượng riêng.
4. **Nghiệp vụ** (Cho vay, Đi vay, Bất động sản) gắn cho đối tượng trong danh mục. Phải thu và Phải trả không bù trừ.

## Bản đồ tác động *(bắt buộc; Constitution IX; lập bằng tìm kiếm mã nguồn và đối chiếu bản sao chỉ đọc của dữ liệu thật 21/10/2026)*

- **Module backend**: `p01.py` (`debt_register` nguồn số dư khoản vay; action `profile`; `classify`; `view`), `categories.py` (`category_view`, `classification_review`, `category_review`, `loan_options`, `change_quick_object`, `category-object-*`), `business.py` (sổ nghiệp vụ tính lại riêng, hợp nhất), `objects.py` (màn Đối tượng, `obj_party_loans`), `legacy_import.py` (tạo đối tượng loại Khác), `assets.py` (Phải thu/Phải trả từ Công nợ), `loan_completion.py`, `interest_settlement.py`, `realty.py` (BĐS, thế chấp, góp vốn), `account_history.py`.
- **Màn hình / giao diện**: Công nợ; Hồ sơ liên kết (hộp); Danh mục (kèm khối Nghiệp vụ và lối vào migrate); Đối tượng; Bất động sản (nút Thêm BĐS); Tổng tài sản; Kiểm tra phân loại; hộp Phân loại (kể cả tạo nhanh); hộp Thêm đối tượng; Migrate lịch sử cũ; mọi hộp Lịch sử.
- **Đường tạo/sửa/xóa song song**: (1) `object-create` (màn Đối tượng, hộp Thêm đối tượng); (2) `profile` (hộp Hồ sơ liên kết: Người/Khoản vay/BĐS); (3) `object-quick-create` (phân loại; nút Thêm BĐS ở màn BĐS); (4) `category-object-add` với tên mới (tạo loại Khác); (5) `legacy-import` (tạo loại Khác). Năm đường, quy tắc kiểm tra khác nhau.
- **Nguồn số liệu trùng nhau**: số dư/Phải thu của khoản vay được tính ở ba nơi: `debt_register` (Công nợ, Tổng tài sản), `business_view` (sổ nghiệp vụ), `loan_options`. Dữ liệu thật hôm nay: Công nợ 0, Tổng tài sản 0, sổ nghiệp vụ **105.000.000** (Khoản Kết bị sổ Công nợ đánh dấu NEGATIVE_PRINCIPAL nên loại khỏi tổng, sổ nghiệp vụ không phát hiện).
- **Dữ liệu đã lưu / dữ liệu thật**: 22 hồ sơ (8 Người, 6 Khoản vay, 5 BĐS, 1 Khác); 6 khoản vay đang là thành viên Gốc vay; Kết và Tươi (Người) thuộc Hot Debt; BĐS Xuân Mai ở hai danh mục, Kỳ Sơn chưa thuộc danh mục nào; 5/6 khoản vay chưa thiết lập chiều; Đồng Cạn đã tạo. Chỉ đổi bằng nút xem trước + xác nhận của Thạch.
- **Báo cáo / snapshot / mốc**: không đổi quy tắc tiền, báo cáo, snapshot, sổ Công nợ.
- **Spec & quy tắc cũ bị thay thế**: R151 (hồ sơ khoản vay làm thành viên danh mục, đã thay bởi R179), R148 và R156 (chặn theo loại gốc, đã bỏ), cách đặt tên nhóm trong Kiểm tra phân loại (R85), các đường tạo hồ sơ riêng lẻ (spec 029, 033, 035, 037).
- **Kiểm tra đồng nhất giữa các màn**: bộ test tự động so Danh mục ↔ Đối tượng ↔ Công nợ ↔ Nghiệp vụ ↔ Tổng tài sản ↔ Kiểm tra phân loại trên dữ liệu giả mô phỏng đúng cấu trúc dữ liệu thật (người có khoản vay âm đầu kỳ, khoản chưa thiết lập chiều, BĐS nhiều danh mục, BĐS chưa thuộc danh mục).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Một nguồn sự thật cho số dư khoản vay (Priority: P1)
Mọi màn hiển thị số dư, Phải thu, Phải trả của khoản vay đều lấy từ **một nguồn duy nhất là sổ Công nợ**. Khoản bị sổ Công nợ loại vì lỗi (âm đầu kỳ, thiếu thiết lập, thiếu nguồn) thì mọi màn đều hiện cùng cảnh báo và **không** cộng vào Phải thu.

**Why this priority**: Con số tài chính phải nhất quán; hiện ba màn cho ba kết quả (0 / 0 / 105.000.000).

**Independent Test**: dữ liệu giả có khoản vay với chuỗi giải ngân/thu gốc làm số dư âm giữa kỳ; mọi màn cho cùng số Phải thu và cùng cảnh báo.

**Acceptance Scenarios**:
1. **Given** khoản vay có lỗi sổ Công nợ, **When** xem sổ nghiệp vụ, **Then** hiện cảnh báo giống Công nợ và không cộng vào Phải thu.
2. **Given** khoản vay hợp lệ, **Then** số dư ở Công nợ, Tổng tài sản, sổ nghiệp vụ, hộp Phân loại bằng nhau.

### User Story 2 - Một đường tạo đối tượng có loại (Priority: P1)
Mọi nơi tạo đối tượng (màn Đối tượng, hộp Thêm đối tượng, hộp Hồ sơ liên kết, tạo nhanh khi phân loại, nút Thêm BĐS, migrate lịch sử cũ) đều tạo qua **một cách duy nhất**, bắt buộc có loại (Người, Bất động sản, Khác) và cùng quy tắc tên duy nhất; migrate lịch sử cũ hỏi loại khi tạo đối tượng mới.

**Acceptance Scenarios**:
1. **Given** mọi lối tạo, **When** tạo đối tượng mới, **Then** có loại và cùng quy tắc, không còn đối tượng loại Khác chỉ do không được hỏi.
2. **Given** hộp Hồ sơ liên kết, **Then** không tạo được thứ trái mô hình (khoản vay làm đối tượng độc lập); khoản vay chỉ tạo bên trong người.

### User Story 3 - Hiển thị đồng nhất tên người (Priority: P1)
Ở mọi màn (Kiểm tra phân loại, lịch sử, báo cáo phân loại, hộp phân loại, Danh mục, Đối tượng), tiền của khoản vay hiển thị theo **tên người** ("Gốc vay · Kết"), khoản vay cụ thể chỉ hiện ở chỗ cần phân biệt.

### User Story 4 - Cấu trúc dữ liệu thật chuyển bằng một nút (Priority: P1)
"Hợp nhất hồ sơ nghiệp vụ" (xem trước + xác nhận, idempotent) đưa dữ liệu thật về mô hình mới: người là thành viên danh mục; khoản vay thôi là thành viên; BĐS có danh mục rõ ràng (một danh mục chính, BĐS chưa thuộc danh mục được báo). Sau khi chuyển, kiểm tra đồng nhất giữa các màn báo sạch.

### User Story 5 - Phân biệt báo cáo và tổng hợp danh mục (Priority: P2)
Danh mục thuộc nhóm mặc định chỉ tổng hợp tiền vào/ra. Tiền cho vay hoặc mua BĐS đặt trong danh mục đang tính vào Chi tiêu/Thu nhập hiển thị cảnh báo ở mọi màn có tổng Chi tiêu/Thu nhập (không chỉ ở khối nghiệp vụ). Việc tách khỏi báo cáo Chi tiêu (phương án B trước đây) **chờ quyết định** trong phỏng vấn.

### Edge Cases
- Người có cả khoản Phải thu và Phải trả cùng danh mục: báo xung đột, không tự gộp.
- Khoản vay chưa thiết lập chiều: hiện "chưa thiết lập" ở mọi màn, không đoán chiều, không cộng số dư.
- Đối tượng loại Khác đang mang nghiệp vụ hoặc giao dịch: đổi loại theo quy tắc chặn đã có.
- Người có khoản vay trong nhiều danh mục khác nhau: mỗi danh mục một mục thành viên và một sổ.
- BĐS có hợp đồng/thanh toán: không đổi loại; tên không trùng.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Số dư, Phải thu, Phải trả của khoản vay chỉ do sổ Công nợ tính; sổ nghiệp vụ, Tổng tài sản, hộp Phân loại, Đối tượng chỉ đọc từ đó, và hiện cảnh báo lỗi của khoản vay giống nhau.
- **FR-002**: Chỉ có một thao tác tạo đối tượng (tên + loại, tên duy nhất toàn hệ thống kể cả đã lưu trữ); mọi lối tạo (kể cả migrate, tạo nhanh, thêm BĐS, Hồ sơ liên kết) gọi đúng thao tác đó.
- **FR-003**: Khoản vay chỉ tạo bên trong một người; không còn đường tạo khoản vay đứng riêng làm đối tượng.
- **FR-004**: Tiền của khoản vay luôn hiển thị theo tên người ở mọi màn; khoản vay cụ thể hiện kèm khi cần phân biệt.
- **FR-005**: Hợp nhất cấu trúc dữ liệu thật bằng nút xem trước + xác nhận, idempotent, có bản ghi, không đổi tiền, báo cáo, snapshot, sổ Công nợ; xử lý BĐS nhiều danh mục và BĐS chưa thuộc danh mục theo quyết định phỏng vấn.
- **FR-006**: Bộ kiểm tra đồng nhất tự động giữa Danh mục, Đối tượng, Công nợ, Nghiệp vụ, Tổng tài sản, Kiểm tra phân loại; chạy trong test và hiển thị cảnh báo trong giao diện khi lệch.
- **FR-007**: Cảnh báo "đang tính vào Chi tiêu/Thu nhập" hiển thị ở mọi màn có tổng đó, cho tiền cho vay/BĐS nằm trong danh mục loại tương ứng.
- **FR-008**: Không đổi quy tắc tiền (Decimal), báo cáo, snapshot, mốc; dữ liệu thật chỉ đổi bằng thao tác xác nhận của Thạch.

### Key Entities
- **Đối tượng**: tên riêng duy nhất, loại, trạng thái (hoạt động / lưu trữ), thuộc 0..n danh mục.
- **Thành viên danh mục**: cặp (đối tượng, danh mục), có thể mang nghiệp vụ và lịch sử.
- **Khoản vay**: bản ghi chi tiết thuộc một Người; chiều, gốc đầu mốc, lãi; nguồn số dư duy nhất là sổ Công nợ.
- **Nghiệp vụ**: Cho vay, Đi vay, Bất động sản; gắn cho thành viên danh mục.

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: Với cùng dữ liệu, mọi màn hiển thị cùng Phải thu, Phải trả và cùng cảnh báo cho mỗi khoản vay (chênh lệch giữa các màn bằng 0).
- **SC-002**: Danh sách đối tượng ở Danh mục và Đối tượng trùng nhau: mọi đối tượng cùng loại, cùng danh mục, cùng số giao dịch; số cảnh báo không đồng nhất sau khi hợp nhất bằng 0.
- **SC-003**: 100% lối tạo đối tượng yêu cầu loại và áp quy tắc tên duy nhất như nhau (kiểm bằng test cho từng lối).
- **SC-004**: Bộ test đồng nhất giữa các màn chạy xanh trên dữ liệu giả mô phỏng đủ các trường hợp của dữ liệu thật.
- **SC-005**: `outputs/p01-user-trial` không đổi bởi phiên làm việc; báo cáo, snapshot, sổ Công nợ trước/sau hợp nhất giống hệt.

## Tư vấn kế toán *(Constitution VIII)*

- **Một nguồn sự thật cho số dư khoản vay** là nguyên tắc đối chiếu sổ chi tiết với sổ tổng hợp: nhiều nơi tự tính cùng một số sẽ sinh chênh lệch không giải thích được. Khoản vay có số dư âm giữa kỳ (thu gốc trước giải ngân hoặc thiếu số đầu kỳ) là **dấu hiệu thiếu dữ liệu**, phải bị loại khỏi tổng và báo, không được "trông có vẻ đúng" ở màn khác.
- **Phải thu và Phải trả không bù trừ**; người có cả hai ở cùng danh mục phải tách danh mục.
- **Cho vay và mua BĐS không phải chi tiêu**: đặt trong danh mục tính vào Chi tiêu làm báo cáo lệch bản chất. Giải pháp tách khỏi báo cáo Chi tiêu làm số báo cáo cũ thay đổi, cần xem trước chênh lệch và xác nhận; báo cáo nộp cơ quan nhà nước cần kế toán viên/thuế xác nhận.
- Cơ sở tiền thực thu/chi; dồn tích lãi, dự phòng, xóa nợ cần kế toán viên xác nhận (ngoài phạm vi).

## Assumptions
- Loại đối tượng giữ Người, Bất động sản, Khác; loại do người dùng tự thêm làm đợt sau.
- Khoản vay giữ làm bản ghi chi tiết (gốc, chiều, lãi) bên trong người để sổ Công nợ không đổi.
- Nguồn sự thật số dư khoản vay là sổ Công nợ đang có.
- Quyết định mở (xem phỏng vấn gộp): cách đặt Hồ sơ liên kết; BĐS nhiều danh mục; báo cáo Chi tiêu với tiền cho vay.
