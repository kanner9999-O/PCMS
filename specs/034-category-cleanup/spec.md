# Feature Specification: Dọn danh mục con chưa dùng

**Feature Branch**: `034-category-cleanup` · **Created**: 2026-10-15 · **Status**: Draft
**Input**: Thạch: "Xóa cho ta những danh mục con mà chưa có giao dịch nào trên hệ thống." Dữ liệu thật chỉ đổi bằng thao tác của Thạch (Constitution I, II), nên tính năng có **xem trước và xác nhận**; không tự xóa trên dữ liệu thật. Tham chiếu spec 016, 026, 030; R136.

## Tư vấn kế toán (Constitution VIII)
Danh mục chưa từng có phân loại nên xóa không làm mất bằng chứng hay đổi số liệu; vẫn ghi bản ghi đã xóa (tên, đường dẫn, lý do, thời điểm). Danh mục đã dùng, đã duyệt, có đối tượng, có khoản vay, có nhập lịch sử cũ thì **giữ** (chỉ lưu trữ).

## User Scenarios
### User Story 1 - Xem trước rồi dọn một lần (P1)
Nút "Dọn danh mục chưa dùng" ở màn Danh mục liệt kê các danh mục con xóa được; Thạch xác nhận thì xóa hết, danh mục cha trống sau khi xóa con cũng xóa nếu cũng chưa dùng.
1. **Given** có danh mục con chưa dùng và đã dùng, **When** xem trước, **Then** chỉ liệt kê danh mục chưa dùng, không đụng danh mục đã dùng và danh mục gốc.
2. **When** xác nhận, **Then** xóa đúng danh sách; số liệu, báo cáo, snapshot không đổi; có bản ghi đã xóa.
3. **Given** danh mục có đối tượng, khoản vay, nhập lịch sử cũ hoặc con còn giữ, **Then** không nằm trong danh sách.

## Requirements
- **FR-001** (R164): danh sách xóa được = danh mục con (có cha) chưa từng dùng phân loại, không có danh mục con còn giữ, không có đối tượng đang thuộc, không có khoản vay gắn, không có nhập lịch sử cũ, không bị chuyển đối tượng tham chiếu; xét lặp từ lá lên.
- **FR-002** (R165): `category-cleanup` cần `confirm` và danh sách `ids` khớp đúng danh sách hiện tại (đổi giữa chừng thì từ chối); xóa mỗi danh mục kèm bản ghi `category_deleted`.
- **FR-003**: không đổi danh mục gốc, tiền, snapshot, báo cáo; không đụng dữ liệu thật ngoài thao tác của Thạch.
## Success Criteria
SC-001 chỉ danh mục chưa dùng bị xóa; SC-002 báo cáo không đổi; SC-003 `outputs/p01-user-trial` không đổi bởi phiên làm việc.
