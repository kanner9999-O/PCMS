# Feature Specification: Quản lý đối tượng

**Feature Branch**: `033-object-management` · **Created**: 2026-10-15 · **Status**: Draft
**Input**: Thạch (15/10/2026): màn quản lý đối tượng riêng, đối tượng = tên riêng + loại (Người, Bất động sản), đủ thêm/sửa/xóa; danh mục có 0, 1 hoặc nhiều đối tượng (Cho vay có Mỹ, Kết, Tươi; Chi tiêu không có). Đã chốt: khoản vay thuộc về một người (hiện bên trong đối tượng Người, không là loại riêng); loại hiển thị Người / Bất động sản / Khác; đổi loại chỉ khi chưa mang dữ liệu đặc thù; xóa hẳn khi chưa dùng, đã dùng thì lưu trữ; màn riêng nhưng vẫn tạo nhanh trong danh mục. Tham chiếu spec 026, 029, 031, 032; Constitution VII, VIII; R136–R157.

## Tư vấn kế toán (Constitution VIII)
- **Đối tượng là chiều chi tiết (sổ chi tiết theo đối tượng)**: tên riêng + loại; loại quyết định loại sổ chi tiết (Người: công nợ; BĐS: tài sản). Không xóa hẳn đối tượng đã phát sinh (lịch sử bất biến) mà **lưu trữ**.
- **Khoản vay là quan hệ giữa hai bên**: khoản vay thuộc một Người (hoặc tổ chức); BĐS chỉ có thể là tài sản thế chấp hoặc mục đích vay (liên kết "BĐS liên quan" để đợt sau, cần kế toán viên xác nhận cách hạch toán).
- **Đổi loại** làm đổi sổ chi tiết nên chặn khi đã có khoản vay, hợp đồng BĐS, nghiệp vụ hoặc phân loại đầu tư. Lưu trữ chặn khi còn dư nợ gốc.
- Tên duy nhất toàn hệ thống (R138): người trùng tên thật phân biệt bằng hậu tố, ví dụ "Kết (anh)".

## User Scenarios & Testing
### User Story 1 - Màn Đối tượng: xem, tìm, tạo (P1)
Màn "Đối tượng" liệt kê mọi đối tượng (Người, Bất động sản, Khác), tìm theo tên, lọc theo loại, hiện danh mục đang thuộc, nghiệp vụ, khoản vay (của Người), tổng vào/ra, trạng thái. Tạo đối tượng với tên + loại, có thể gắn luôn vào một danh mục.
1. **Given** hệ thống có đối tượng, **When** mở màn, **Then** thấy danh sách theo loại, khoản vay hiện trong đối tượng Người.
2. **Given** tên đã tồn tại (kể cả đã lưu trữ), **When** tạo, **Then** bị chặn.
3. **Given** tạo kèm danh mục, **Then** đối tượng thuộc danh mục đó.

### User Story 2 - Sửa tên, đổi loại có điều kiện (P1)
1. Đổi tên (duy nhất), có lịch sử. 2. Đổi loại cần lý do; chặn khi đối tượng đang là bên của khoản vay, mang nghiệp vụ, hoặc BĐS đã có dữ liệu BĐS/đầu tư; "Khác" đổi sang Người/BĐS tự do; Khoản vay không đổi loại ở đây.

### User Story 3 - Lưu trữ, khôi phục, xóa (P1)
1. Chưa từng dùng → xóa hẳn (có lý do). 2. Đã dùng → chỉ lưu trữ (ẩn khỏi danh sách chọn, giữ lịch sử); chặn lưu trữ khi còn dư nợ gốc; khôi phục được. 3. Đối tượng lưu trữ không thêm vào danh mục mới và không phân loại mới.

### User Story 4 - Lịch sử đối tượng (P2)
Lịch sử giao dịch chuẩn của đối tượng qua mọi danh mục (Người gồm cả khoản vay của họ).

## Requirements
- **FR-001** (R158): `objects` trong `view`: danh sách đối tượng (Người, BĐS, Khác; khoản vay lồng trong Người), trạng thái, danh mục, nghiệp vụ, tổng vào/ra, lý do không đổi loại/xóa được.
- **FR-002** (R159): `object-create` (tên 1–100 duy nhất toàn hệ thống kể cả lưu trữ, loại ∈ Người/BĐS/Khác, tùy chọn danh mục).
- **FR-003** (R160): `object-edit` đổi tên/loại; đổi loại cần lý do và bị chặn theo quy tắc ở Tư vấn kế toán.
- **FR-004** (R161): `object-archive` (lý do; chặn khi còn dư nợ gốc), `object-restore`; đối tượng lưu trữ không thêm vào danh mục mới, không dùng phân loại mới.
- **FR-005** (R162): `object-delete` chỉ khi chưa được tham chiếu ở bất kỳ đâu; có lý do và bản ghi `object_deleted`.
- **FR-006** (R163): giữ quy tắc 0/1/nhiều đối tượng mỗi danh mục; danh mục không có đối tượng phân loại thẳng.
- **FR-007**: lịch sử đối tượng qua mọi danh mục.
- **FR-008**: không đổi quy tắc tiền, snapshot, báo cáo; không đụng dữ liệu thật.

## Success Criteria
- **SC-001** Mọi thao tác thêm/sửa/lưu trữ/khôi phục/xóa có kiểm thử và chặn đúng lý do. **SC-002** Báo cáo, snapshot, tổng danh mục không đổi. **SC-003** `outputs/p01-user-trial` không đổi.

## Assumptions
Loại do người dùng tự thêm và liên kết "BĐS liên quan" của khoản vay làm đợt sau.
