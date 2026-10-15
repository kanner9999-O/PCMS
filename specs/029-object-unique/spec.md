# Feature Specification: Tên đối tượng duy nhất và gộp đối tượng trùng

**Feature Branch**: `029-object-unique` · **Created**: 2026-10-15 · **Status**: Draft
**Input**: Thạch thấy trong danh mục Property có hai đối tượng "Xuân Mai" cùng tồn tại; cần kiểm tính duy nhất và sửa (R138–R140). Nguyên nhân kiểm trên dữ liệu thật (chỉ đọc): một hồ sơ BĐS "Xuân Mai" có sẵn và một hồ sơ loại "đối tượng" "Xuân Mai" tạo sau (migrate theo tên chỉ tìm trong loại "đối tượng"); tương tự "Hòa Sơn"; luật không trùng tên hiện chỉ kiểm trong cùng loại. Tham chiếu spec 026, 027. Tuân Constitution VII (danh mục) và VIII (kế toán).

## Tư vấn kế toán (Constitution VIII)
- **Khuyến nghị**: mỗi đối tượng là **một hồ sơ duy nhất** trong sổ chi tiết; hai hồ sơ cùng tên làm số dư và lịch sử bị phân tán, dễ đếm thiếu hoặc đếm kép. Gộp phải có dấu vết (ai/khi nào/vì sao), không xóa hay sửa chứng từ gốc.
- **Hệ quả**: tổng theo đối tượng gom đúng về một hồ sơ; giao dịch ngân hàng đã phân loại giữ nguyên phân loại gốc, chỉ cách xem gộp theo bản ghi gộp.
- **Cần kế toán viên xác nhận**: không có.

## User Scenarios & Testing
### User Story 1 - Không tạo được đối tượng trùng tên (Priority: P1)
**Independent Test**: có BĐS "Xuân Mai"; thêm đối tượng "xuân  mai" (khác hoa/thường, thừa khoảng trắng) bị chặn kèm gợi ý chọn hồ sơ có sẵn; đổi tên một đối tượng thành tên đã có bị chặn; tạo hồ sơ người trùng tên một BĐS bị chặn; migrate theo tên "Xuân Mai" dùng lại BĐS có sẵn và gán vào danh mục thay vì tạo mới.

**Acceptance Scenarios**:
1. **Given** hồ sơ bất kỳ loại có tên X, **When** tạo hoặc đổi tên hồ sơ khác thành X (đã chuẩn hóa), **Then** bị chặn với thông báo nêu loại hồ sơ đã có.
2. **Given** migrate theo tên trùng hồ sơ có sẵn (mọi loại), **When** ghi, **Then** dùng lại hồ sơ đó và gán vào danh mục nếu chưa thuộc.
3. **Given** tên hợp lệ chưa dùng, **When** tạo, **Then** thành công như cũ.

### User Story 2 - Cảnh báo và gộp đối tượng trùng đã có (Priority: P1)
Trong danh sách đối tượng của danh mục, đối tượng trùng tên hồ sơ khác hiện nhãn "Trùng tên với …" và nút **Gộp**; gộp loại "đối tượng" vào hồ sơ đích kèm lý do.

**Acceptance Scenarios**:
1. **Given** OBJECT "Xuân Mai" và BĐS "Xuân Mai" cùng thuộc Property, **When** gộp OBJECT vào BĐS, **Then** trong Property chỉ còn BĐS; lịch sử cũ của OBJECT hiện dưới BĐS; tổng đúng bằng tổng hai hồ sơ cộng lại; OBJECT bị ẩn mọi nơi.
2. **Given** đối tượng bị gộp có giao dịch ngân hàng đã phân loại, **When** gộp, **Then** phân loại gốc không đổi nhưng các màn tổng hợp và lịch sử tính về hồ sơ đích.
3. **Given** hồ sơ nguồn không phải loại "đối tượng", gộp vào chính nó, đích đã bị gộp, hoặc thiếu lý do, **When** gộp, **Then** bị chặn.
4. **Given** gộp xong, **When** xem Danh mục, **Then** hiện bản ghi gộp (nguồn, đích, lý do, thời điểm).

## Requirements
- **FR-001** (R138): khóa tên chuẩn hóa (NFC, bỏ khoảng trắng thừa, không phân biệt hoa/thường); kiểm duy nhất toàn bộ hồ sơ chưa bị gộp ở mọi đường tạo/đổi tên; migrate theo tên dùng lại hồ sơ có sẵn.
- **FR-002** (R139): view đối tượng thêm `duplicate_of` (hồ sơ khác cùng tên); giao diện cảnh báo.
- **FR-003** (R140): hành động gộp `category-object-merge {from, into, reason}`: chỉ từ loại "đối tượng"; chuyển thành viên danh mục (bỏ trùng), lịch sử cũ và lần migrate sang đích; bản ghi `profile_merges`; hồ sơ nguồn đánh dấu `merged_into` và ẩn; phân bổ ngân hàng giữ nguyên, các màn danh mục đọc qua bản ghi gộp.
- **FR-004**: không đổi tiền, snapshot, dữ liệu sao kê; đọc không ghi.

## Success Criteria
- **SC-001**: không còn đường nào tạo được hai hồ sơ trùng tên (kiểm bằng test mọi đường).
- **SC-002**: gộp OBJECT vào BĐS cho tổng bằng tổng hai bên cộng lại, không đếm kép; dữ liệu thật không đổi cho tới khi Thạch tự bấm Gộp.

## Assumptions
- Tên khác dấu tiếng Việt là tên khác (Hà ≠ Hạ); không chặn theo khớp không dấu.
- Hồ sơ trùng đã có từ trước không bị sửa tự động; Thạch chủ động gộp.
