# Feature Specification: Danh mục có đối tượng riêng

**Feature Branch**: `026-category-objects` · **Created**: 2026-10-14 · **Status**: Draft
**Input**: Thạch mô tả mô hình: danh mục gốc → nhiều danh mục con nhiều cấp; mỗi danh mục có danh sách đối tượng riêng (Cho vay dài hạn: A, B, C; Chung cư: Chung cư A, B, C); đối tượng chỉ cần tên, là hồ sơ chung gán được nhiều danh mục; thao tác thêm/đổi tên/gỡ/xóa/chuyển/xem tổng và lịch sử (R123–R128). Thay cơ chế "loại đối tượng" của spec 025. Tham chiếu spec 008, 014, 016, 017, 025. Chưa có nghiệp vụ riêng từng đối tượng.

## User Scenarios & Testing
### User Story 1 - Thấy cây danh mục và đối tượng của từng danh mục (Priority: P1)
Màn Danh mục hiện mọi danh mục gốc (hệ thống và tự tạo) với cây con nhiều cấp; dưới mỗi danh mục là danh sách **đối tượng của nó**, mỗi đối tượng kèm số giao dịch và tổng vào/ra.

**Independent Test**: tạo "Bất động sản" (gốc nhóm đầu tư) › "Chung cư" › đối tượng Chung cư A, B, C và "Đất nền" › Mảnh đất A; màn hiện đúng cây và danh sách đối tượng; phân loại 2 giao dịch vào Chung cư A → A hiện 2 giao dịch, tổng đúng.

**Acceptance Scenarios**:
1. **Given** danh mục có đối tượng, **When** mở màn Danh mục, **Then** mỗi danh mục liệt kê đối tượng của chính nó (không gộp con) kèm số giao dịch, vào, ra.
2. **Given** danh mục cho nhiều cấp con, **When** xem, **Then** cây hiển thị đủ cấp, con lồng dưới cha.
3. **Given** danh mục chưa có đối tượng, **When** xem, **Then** chỉ có nút "+ Đối tượng".

### User Story 2 - Thêm, đổi tên, gỡ, xóa đối tượng (Priority: P1)
Mỗi danh mục có "+ Đối tượng": tạo mới (chỉ tên) hoặc chọn hồ sơ có sẵn (người, khoản vay, BĐS, đối tượng khác). Đổi tên hồ sơ, gỡ khỏi danh mục (giữ lịch sử), xóa hẳn đối tượng chưa từng dùng.

**Acceptance Scenarios**:
1. **Given** tên mới hợp lệ, **When** thêm, **Then** tạo hồ sơ đối tượng và gán vào danh mục; tên trùng (không phân biệt hoa/thường) trong cùng loại bị chặn.
2. **Given** một hồ sơ có sẵn, **When** gán vào danh mục thứ hai, **Then** cùng một hồ sơ xuất hiện ở cả hai danh mục (tổng hợp riêng từng danh mục).
3. **Given** đối tượng đã gán, **When** gán lại cùng danh mục, **Then** bị chặn.
4. **Given** gỡ khỏi danh mục, **When** xem, **Then** không còn trong danh sách phân loại mới; giao dịch đã phân loại không đổi.
5. **Given** đối tượng chưa từng dùng, **When** xóa kèm lý do, **Then** xóa hẳn và ghi bản ghi xóa; đã dùng hoặc là hồ sơ người/khoản vay/BĐS thì không xóa được (chỉ gỡ).

### User Story 3 - Chuyển đối tượng sang danh mục khác (Priority: P2)
Chuyển đối tượng từ danh mục này sang danh mục khác **cùng loại gốc** (ví dụ Cho vay dài hạn → Nợ xấu cùng nhóm), kèm lý do; giao dịch của đối tượng ở danh mục cũ hiện dưới danh mục mới; có lịch sử chuyển.

**Acceptance Scenarios**:
1. **Given** đối tượng A ở danh mục X có 2 giao dịch, **When** chuyển sang Y cùng loại, **Then** tổng của X giảm, Y tăng đúng 2 giao dịch; A không còn trong X, có trong Y; lịch sử ghi lý do và thời điểm.
2. **Given** danh mục đích khác loại gốc, đã lưu trữ, hoặc đối tượng đã có ở đích, **When** chuyển, **Then** bị chặn.
3. **Given** snapshot/báo cáo đã duyệt, **When** chuyển, **Then** không đổi.

### User Story 4 - Phân loại theo danh mục → danh mục con → đối tượng của danh mục (Priority: P1)
Hộp phân loại: chọn danh mục, danh mục con; ô Đối tượng chỉ liệt kê **đối tượng của chính danh mục (hoặc danh mục con) đã chọn**, có "+ Tạo nhanh đối tượng" (tạo và gán vào danh mục đang chọn). Đối tượng không bắt buộc.

**Acceptance Scenarios**:
1. **Given** Chung cư có A, B, C, **When** chọn Chung cư, **Then** ô đối tượng liệt kê đúng A, B, C; chọn danh mục khác thì đổi danh sách.
2. **Given** danh mục không có đối tượng, **When** chọn, **Then** không có ô đối tượng.
3. **Given** đối tượng không thuộc danh mục đã chọn, **When** lưu, **Then** bị chặn (trừ hồ sơ cũ đã gắn từ trước ở danh mục chưa có đối tượng: quy tắc cũ cho dữ liệu đã có).

### User Story 5 - Xem tổng và lịch sử từng đối tượng (Priority: P2)
Từ đối tượng trong danh mục: mở lịch sử giao dịch (định dạng chuẩn, spec 017) chỉ gồm giao dịch của đối tượng đó trong danh mục đó.

### Edge Cases
- Đối tượng lưu trữ/gỡ vẫn hiện ở lịch sử cũ.
- Hồ sơ cũ (người, khoản vay, BĐS) gán vào danh mục: dùng được ngay; công nợ/vốn BĐS giữ nguyên.

## Requirements
- **FR-001** (R124, R125): danh sách đối tượng theo danh mục (danh mục con hoặc gốc hệ thống/tự tạo, trừ Chưa phân loại); hành động thêm (tạo tên mới loại "đối tượng" hoặc gán hồ sơ có sẵn), đổi tên, gỡ, xóa, chuyển.
- **FR-002** (R126, R128): khi lưu phân loại, đối tượng (nếu có) phải thuộc danh sách của chính danh mục/danh mục con đã chọn; danh mục chưa có đối tượng giữ quy tắc cũ cho hồ sơ đã có (gốc/lãi→khoản vay, đầu tư→BĐS, chi tiêu→khoản vay/BĐS); bỏ khai báo loại đối tượng của spec 025.
- **FR-003** (R127): chuyển đối tượng chỉ trong cùng loại gốc, kèm lý do, giao dịch của đối tượng ở danh mục cũ hiện ở danh mục mới ở mọi màn tổng hợp; lịch sử chuyển; snapshot không đổi.
- **FR-004** (R127): xóa hẳn chỉ khi đối tượng loại "đối tượng" chưa từng được dùng (phân loại hiện tại, lịch sử, snapshot) kèm lý do và bản ghi xóa.
- **FR-005** (R123, R127): màn Danh mục hiển thị đối tượng từng danh mục kèm số giao dịch và vào/ra; lịch sử giao dịch của một đối tượng trong danh mục.
- **FR-006**: không đổi tiền, snapshot, báo cáo theo loại; đọc không ghi.

## Success Criteria
- **SC-001**: ví dụ Chung cư A/B/C, Đất nền, Cho vay dài hạn A/B/C hiển thị và phân loại đúng (tổng tính tay khớp).
- **SC-002**: chuyển đối tượng làm tổng danh mục cũ giảm và mới tăng đúng bằng giao dịch của đối tượng; tiền không đổi.
- **SC-003**: đối tượng sai danh mục bị chặn 100%; dữ liệu thật không đổi (SHA256); 375px không tràn ngang.

## Assumptions
- Hồ sơ đối tượng mới có loại `OBJECT` (chỉ tên); loại nghiệp vụ bổ sung sau.
- Tổng của đối tượng trong danh mục tính các phần phân loại trực tiếp vào danh mục đó (không gộp danh mục con).
- Khai báo "loại đối tượng" của 025 bị thay thế; dữ liệu đã khai (nếu có) không còn tác dụng, danh mục cần được gán đối tượng cụ thể.
