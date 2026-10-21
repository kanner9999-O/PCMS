# Feature Specification: Tách danh mục và đối tượng; tạm dừng nghiệp vụ; đồng nhất các màn

**Feature Branch**: `041-unified-object-model`

**Created**: 2026-10-21

**Status**: Draft → đã phỏng vấn gộp (xem Clarifications)

**Input**: Thạch phản ánh các màn hình không ăn khớp và phải sửa từng màn; yêu cầu rà soát toàn hệ thống và làm **một đợt** theo đủ quy trình Spec Kit (Constitution IX). Spec bao trùm và **thay thế phần chồng lấn** của spec 031, 032, 033, 035, 037, 040. Tham chiếu: Constitution VII, VIII, IX; R84–R86, R136, R146–R184.

## Clarifications

### Session 2026-10-21 (Thạch trả lời phỏng vấn gộp)
- Q: Hộp "Hồ sơ liên kết"? → A: **Bỏ hộp này.** Tạo đối tượng đi qua màn Đối tượng (và hộp Thêm đối tượng trong danh mục).
- Q: Tiền cho vay / mua BĐS đặt trong danh mục tính vào Chi tiêu? → A: **Nghiệp vụ tạm dừng.** Thạch chưa quyết định cách làm nghiệp vụ; hiện **chỉ lưu các giao dịch đó dưới dạng thu và chi**. Sau này mới tính việc phân loại giao dịch vào từng nghiệp vụ.
- Q: BĐS nhiều danh mục, nghiệp vụ gắn ở đâu? → A: **Danh mục và loại đối tượng là hai thứ hoàn toàn khác nhau**, tách bạch. **Tên danh mục không liên quan nghiệp vụ.** Sau này sẽ có tính năng gán nghiệp vụ cho một **nhóm danh mục** (ví dụ Property → nghiệp vụ bất động sản; Long Debt → nghiệp vụ vay/nợ); hiện **để pending**, chưa quyết định có "nhóm nghiệp vụ chung cho danh mục" hay không.
- Q: Migrate lịch sử cũ tạo đối tượng mới? → A: giữ đề xuất (hỏi loại khi tạo đối tượng mới; gợi ý mặc định theo ngữ cảnh) — Thạch không phản đối (xem Assumptions).
- Q: Cách hiển thị tên? → A: **Chỉ hiển thị tên người** (đó là đối tượng). Một người có nhiều khoản vay là **nghiệp vụ vay khác, chưa làm tới**.

## Mô hình hiện hành (sau quyết định)
1. **Danh mục**: cây cha → con nhiều cấp, nhóm mặc định, chỉ tổng hợp tiền vào/ra. **Tên danh mục không mang nghiệp vụ.**
2. **Đối tượng**: tên riêng (duy nhất toàn hệ thống) + loại (Người, Bất động sản, Khác; thêm loại sau); thuộc 0..n danh mục.
3. **Nghiệp vụ (Cho vay / Đi vay / BĐS / sổ nghiệp vụ): TẠM DỪNG (Pending).** Mã và dữ liệu đã lưu được giữ nguyên nhưng **ẩn khỏi giao diện**, chờ quyết định (gồm khả năng gán nghiệp vụ cho nhóm danh mục).
4. **Sổ Công nợ, màn Bất động sản, Tổng tài sản** giữ nguyên chức năng hiện có trên dữ liệu đã lưu (đóng băng, không mở rộng); không thêm nghiệp vụ mới.

## Bản đồ tác động *(Constitution IX; lập bằng tìm kiếm mã nguồn và đối chiếu bản sao chỉ đọc của dữ liệu thật 21/10/2026)*

- **Module backend**: `business.py` (tạm dừng: cờ bật/tắt, hợp nhất chỉ còn đồng bộ thành viên), `categories.py` (`category_view`, `classification_review`, `category_history`, `change_quick_object`), `objects.py` (một hàm tạo đối tượng dùng chung, `issues`), `legacy_import.py` (tạo đối tượng có loại), `p01.py` (`view`, action `profile`, `classify`), `realty.py` (nút Thêm BĐS).
- **Màn hình / giao diện**: ẩn khối **Nghiệp vụ** và nút/chip nghiệp vụ ở Danh mục, cảnh báo Chi tiêu/Thu nhập, nút "Hợp nhất hồ sơ nghiệp vụ" (chuyển thành đồng bộ thành viên); **bỏ** nút và hộp "Hồ sơ liên kết"; Đối tượng (không hiện khoản vay/nghiệp vụ); Kiểm tra phân loại và mọi lịch sử (tên người); hộp Phân loại (tên người, khoản vay tự xác định khi chỉ có một); hộp Thêm đối tượng; Migrate lịch sử cũ (hỏi loại).
- **Đường tạo đối tượng song song** (5): màn Đối tượng và hộp Thêm đối tượng; hộp Hồ sơ liên kết (bỏ); tạo nhanh khi phân loại và nút Thêm BĐS; thêm theo tên trong danh mục; migrate lịch sử cũ → dồn về **một hàm tạo** có loại.
- **Nguồn số liệu trùng nhau**: số dư khoản vay hiện ở Công nợ, Tổng tài sản (cùng sổ Công nợ) và sổ nghiệp vụ (tính riêng, **105.000.000** so với 0). Ẩn sổ nghiệp vụ loại bỏ nguồn thứ hai khỏi giao diện; sổ Công nợ là nguồn duy nhất.
- **Dữ liệu đã lưu / dữ liệu thật**: 22 hồ sơ; 6 khoản vay đang là thành viên Gốc vay; 1 cặp có nghiệp vụ Cho vay (Khoản Kết) sẽ bị ẩn; BĐS Xuân Mai ở hai danh mục, Kỳ Sơn chưa thuộc danh mục; chỉ đổi bằng nút xem trước + xác nhận của Thạch.
- **Báo cáo / snapshot / mốc**: không đổi quy tắc tiền, báo cáo, snapshot, sổ Công nợ, phân loại gốc đã lưu.
- **Spec & quy tắc cũ chuyển trạng thái**: R146–R153 (vai trò danh mục, nghiệp vụ gắn đối tượng), R156–R157 (nghiệp vụ mọi danh mục, cảnh báo Chi tiêu), R179–R182 (người sở hữu khoản vay là thành viên có nghiệp vụ) → **Pending**; R84–R86 (hiển thị) và R136 (cấu trúc danh mục) giữ; R148 đã bỏ; cách tạo đối tượng của spec 029, 033, 035, 037 → một hàm tạo.
- **Kiểm tra đồng nhất giữa các màn**: test tự động so Danh mục ↔ Đối tượng ↔ Kiểm tra phân loại ↔ Lịch sử (cùng tên người, cùng danh mục, cùng số giao dịch) trên dữ liệu giả mô phỏng cấu trúc thật (người có một khoản vay, khoản chưa thiết lập, khoản số dư âm, BĐS nhiều danh mục, BĐS chưa thuộc danh mục).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Danh mục và đối tượng tách bạch; không còn khái niệm nghiệp vụ trên giao diện (Priority: P1)
Giao diện chỉ còn: danh mục (cây, nhóm mặc định) và đối tượng (tên + loại). Không còn khối Nghiệp vụ, nút/chip nghiệp vụ, cảnh báo "tính vào Chi tiêu", hay chữ Cho vay/Đi vay gắn với đối tượng/danh mục. Giao dịch cho vay/mua BĐS chỉ là thu và chi trong danh mục.

**Why this priority**: Thạch chưa quyết định nghiệp vụ; hiển thị nghiệp vụ nửa vời làm số liệu và màn hình lệch nhau.

**Independent Test**: dữ liệu giả có cặp đã gắn nghiệp vụ; mở Danh mục, Đối tượng, Kiểm tra phân loại: không có chỗ nào hiện nghiệp vụ; dữ liệu nghiệp vụ vẫn còn trong dữ liệu lưu.

**Acceptance Scenarios**:
1. **Given** dữ liệu có cặp mang nghiệp vụ, **When** mở Danh mục/Đối tượng, **Then** không hiện chip/nút/khối nghiệp vụ; tổng và lịch sử không đổi.
2. **Given** gọi hành động gắn nghiệp vụ trực tiếp, **Then** bị từ chối với thông báo "nghiệp vụ tạm dừng chờ quyết định".

### User Story 2 - Bỏ hộp Hồ sơ liên kết; một đường tạo đối tượng có loại (Priority: P1)
Không còn nút/hộp "Hồ sơ liên kết". Mọi lối tạo đối tượng (màn Đối tượng, hộp Thêm đối tượng, tạo nhanh khi phân loại, nút Thêm BĐS, migrate lịch sử cũ) dùng **một hàm tạo duy nhất**: tên duy nhất toàn hệ thống (kể cả đã lưu trữ) + loại Người/Bất động sản/Khác.

**Acceptance Scenarios**:
1. **Given** từng lối tạo, **When** tạo đối tượng mới, **Then** có loại và cùng quy tắc tên.
2. **Given** migrate lịch sử cũ với tên chưa có, **Then** hộp hỏi loại (gợi ý theo ngữ cảnh) và đối tượng tạo ra đúng loại.

### User Story 3 - Hiển thị đồng nhất tên người (Priority: P1)
Ở mọi màn (Kiểm tra phân loại, mọi lịch sử, hộp phân loại, Danh mục, Đối tượng), tiền của khoản vay hiển thị theo **tên người**; không hiện "Khoản …". Khi người chỉ có một khoản vay, hộp phân loại tự xác định khoản đó (không hỏi); người có nhiều khoản vay: chưa hỗ trợ chọn khoản (nghiệp vụ khác, chưa làm tới) — hiện thông báo rõ.

**Acceptance Scenarios**:
1. **Given** tiền gốc vay của Kết, **When** xem Kiểm tra phân loại, **Then** nhóm là "Gốc vay · Kết".
2. **Given** Kết có đúng một khoản vay, **When** phân loại vào Gốc vay chọn người Kết, **Then** lưu gắn khoản vay đó mà không hỏi thêm.

### User Story 4 - Đồng bộ danh mục và đối tượng (Priority: P1)
Nút "Đồng bộ danh mục và đối tượng" (xem trước + xác nhận, idempotent): người sở hữu khoản vay trở thành thành viên danh mục chứa khoản vay; hồ sơ khoản vay thôi là thành viên (giữ bản ghi); **không gắn nghiệp vụ**. Sau đồng bộ, Danh mục và Đối tượng liệt kê cùng người, cùng danh mục, cùng số giao dịch.

### User Story 5 - Kiểm tra đồng nhất giữa các màn (Priority: P2)
Bộ kiểm tra tự động (test) và cảnh báo trong giao diện khi Danh mục và Đối tượng lệch nhau.

### Edge Cases
- Người có nhiều khoản vay: hộp phân loại báo "chưa hỗ trợ" thay vì đoán khoản.
- Khoản vay chưa thiết lập: vẫn gắn được khi người chỉ có một khoản (Công nợ vẫn báo thiếu thiết lập như cũ).
- Đối tượng loại Khác tạo từ migrate cũ: giữ nguyên, đổi loại theo quy tắc chặn đã có.
- Dữ liệu cũ có nghiệp vụ đã gắn: giữ trong dữ liệu, ẩn khỏi giao diện, không mất khi bật lại sau này.
- BĐS ở nhiều danh mục hoặc chưa thuộc danh mục: hợp lệ (đối tượng thuộc 0..n danh mục); chỉ hiện ở Đối tượng như một dữ kiện.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Nghiệp vụ tạm dừng: mọi thành phần giao diện về nghiệp vụ (khối, nút, chip, nhãn Cho vay/Đi vay, cảnh báo tính vào Chi tiêu/Thu nhập) bị ẩn; hành động gắn/gỡ nghiệp vụ bị từ chối với thông báo tạm dừng; dữ liệu nghiệp vụ đã lưu giữ nguyên.
- **FR-002**: Bỏ nút và hộp "Hồ sơ liên kết" khỏi giao diện.
- **FR-003**: Một hàm tạo đối tượng dùng chung cho mọi lối tạo (tên 1–100 ký tự, duy nhất toàn hệ thống kể cả đã lưu trữ, loại hợp lệ, tùy chọn danh mục); migrate lịch sử cũ nhận và hỏi loại khi tạo đối tượng mới.
- **FR-004**: Tiền của khoản vay hiển thị theo tên người ở Kiểm tra phân loại, mọi lịch sử, hộp phân loại, Danh mục, Đối tượng; hộp phân loại tự xác định khoản vay khi người chỉ có một, báo rõ khi có nhiều.
- **FR-005**: Đồng bộ danh mục và đối tượng bằng nút xem trước + xác nhận, idempotent, có bản ghi, không gắn nghiệp vụ, không đổi tiền, báo cáo, snapshot, sổ Công nợ.
- **FR-006**: Màn Đối tượng không hiện khoản vay/nghiệp vụ; hiện loại, danh mục, số giao dịch, trạng thái, cảnh báo lệch với Danh mục kèm nút đồng bộ.
- **FR-007**: Bộ test đồng nhất giữa Danh mục, Đối tượng, Kiểm tra phân loại, Lịch sử.
- **FR-008**: Không đổi quy tắc tiền (Decimal), báo cáo, snapshot, mốc, sổ Công nợ; dữ liệu thật chỉ đổi bằng thao tác xác nhận của Thạch.

### Key Entities
- **Đối tượng**: tên riêng duy nhất, loại (Người, Bất động sản, Khác), trạng thái, thuộc 0..n danh mục.
- **Thành viên danh mục**: cặp (đối tượng, danh mục), có lịch sử; (trường nghiệp vụ giữ trong dữ liệu nhưng tạm dừng).
- **Khoản vay**: bản ghi kỹ thuật thuộc một Người, giữ để sổ Công nợ hoạt động; không hiện như đối tượng.

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: 0 thành phần nghiệp vụ hiển thị trên Danh mục, Đối tượng, Kiểm tra phân loại, lịch sử (kiểm bằng test giao diện/dữ liệu trả về).
- **SC-002**: 100% lối tạo đối tượng tạo qua một hàm với quy tắc tên và loại như nhau (test từng lối).
- **SC-003**: Danh sách đối tượng ở Danh mục và Đối tượng trùng nhau sau đồng bộ: cùng người, cùng danh mục, cùng số giao dịch (chênh lệch 0).
- **SC-004**: Không còn nhãn "Khoản …" ở Kiểm tra phân loại và lịch sử; mọi nhóm của khoản vay mang tên người.
- **SC-005**: `outputs/p01-user-trial` không đổi bởi phiên làm việc; báo cáo, snapshot, sổ Công nợ trước/sau giống hệt.

## Tư vấn kế toán *(Constitution VIII)*

- **Tạm dừng nghiệp vụ là phương án an toàn về kế toán**: cho vay/mua BĐS ghi nhận tạm là **dòng tiền thu/chi** (cash basis) trung thực với sao kê, không tự suy ra phải thu/phải trả/giá gốc khi chưa chốt nghiệp vụ; tránh hai sổ cho cùng một số (hiện 0 so với 105.000.000).
- Khi chốt nghiệp vụ sau này (gồm gán nghiệp vụ cho **nhóm danh mục**), cần: sổ Công nợ là nguồn duy nhất cho số dư khoản vay; Phải thu/Phải trả không bù trừ; cho vay và mua BĐS không phải chi tiêu khi báo cáo; báo cáo nộp cơ quan nhà nước cần kế toán viên/thuế xác nhận.
- Danh mục tổng hợp thu/chi tách khỏi loại đối tượng là cách tổ chức sổ chi tiết theo chủ thể (đối tượng) độc lập với tài khoản tổng hợp (danh mục).

## Assumptions
- Giữ Người, Bất động sản, Khác; loại tự thêm làm đợt sau.
- Migrate lịch sử cũ bắt buộc loại khi tạo đối tượng mới; gợi ý mặc định theo danh mục (Gốc vay → Người, danh mục chứa BĐS → Bất động sản), người dùng đổi được.
- Sổ Công nợ, màn Bất động sản, Tổng tài sản giữ nguyên như hiện có (không mở rộng) vì Thạch không yêu cầu đổi; nếu Thạch muốn ẩn/đổi chúng thì là quyết định riêng.
- Mã nghiệp vụ không xóa: cờ tạm dừng cho phép bật lại sau khi Thạch quyết định cách làm.
