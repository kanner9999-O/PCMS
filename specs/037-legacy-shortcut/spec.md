# Feature Specification: Migrate lịch sử cũ ngay khi tạo đối tượng của danh mục

**Feature Branch**: `037-legacy-shortcut` · **Created**: 2026-10-21 · **Status**: Draft
**Input**: Thạch: trong phần tạo đối tượng của từng danh mục cần có phần nhập (import) dữ liệu khi khởi tạo, áp dụng khi có dữ liệu cũ cần migrate. Tham chiếu spec 027, 028, 033, 035; Constitution I, II, VII; R84–R86, R136, R166–R168. Dùng lại trình migrate lịch sử cũ đã có (xem trước, kiểm tổng, xác nhận); chỉ thêm lối vào đúng ngữ cảnh. Không đổi quy tắc tiền hay dữ liệu thật.

## Tư vấn kế toán (Constitution VIII)
Không có logic kế toán mới. Giữ nguyên: lịch sử cũ nằm ngoài chuỗi sao kê; tính vào tổng của đối tượng và danh mục; không đổi số dư tài khoản, mốc, snapshot; dòng trùng mã tham chiếu với sao kê ngân hàng tự loại để không đếm kép; có xem trước và kiểm tổng trước khi ghi; hủy được.

## User Scenarios & Testing
### User Story 1 - Từ hộp "Thêm đối tượng" (P1)
Hộp có khu "Có dữ liệu cũ cần migrate?" với nút "Migrate lịch sử cũ…". Bấm thì mở trình migrate với **danh mục đã chọn sẵn** và **đối tượng điền sẵn**: đối tượng có sẵn đang chọn, hoặc tên đối tượng mới đang gõ/tạo; nếu chưa có thì để trống để nhập tên. Sau đó theo luồng cũ (dán dữ liệu, xem trước, ghi); đối tượng mới được tạo cùng lúc khi ghi.
1. **Given** gõ "Mỹ" (chưa có) trong hộp, **When** bấm Migrate, **Then** trình migrate mở với danh mục hiện tại và tên Mỹ.
2. **Given** chọn đối tượng có sẵn, **Then** trình migrate chọn sẵn đối tượng đó.

### User Story 2 - Từ từng đối tượng của danh mục (P1)
Mỗi đối tượng trong khối Đối tượng của danh mục có nút "Migrate lịch sử" mở trình migrate chọn sẵn danh mục và đối tượng đó.

## Requirements
- **FR-001** (R172): trình migrate nhận cấu hình mở sẵn (danh mục theo cấp, đối tượng hoặc tên mới); mặc định cũ (Long Debt) vẫn dùng khi không có.
- **FR-002** (R173): lối vào từ hộp "Thêm đối tượng" và từ từng đối tượng của danh mục.
- **FR-003**: không đổi API, quy tắc, báo cáo; dữ liệu thật chỉ đổi khi Thạch tự bấm ghi.
- **FR-004** (R173): chống ghi nhầm — `legacy_preview/legacy-import` từ chối khi vừa chọn đối tượng có sẵn vừa nhập tên khác; giao diện tự bỏ ô còn lại và nêu rõ đối tượng đích ở bản xem trước. (Sự cố thật: 21/10/2026 hai lần migrate "Đồng Cạn" đã ghi vào Xuân Mai.)
## Success Criteria
SC-001 từ hộp thêm đối tượng đến màn dán dữ liệu ≤ 1 thao tác, danh mục và đối tượng đã điền sẵn; SC-002 dữ liệu thật không đổi bởi phiên làm việc.
