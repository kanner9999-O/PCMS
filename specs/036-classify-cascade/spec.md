# Feature Specification: Phân loại giao dịch theo cây danh mục cha → con và đối tượng của danh mục

**Feature Branch**: `036-classify-cascade` · **Created**: 2026-10-16 · **Status**: Draft
**Input**: Thạch: trong "Tạo phiên điều chỉnh phân loại" (hộp phân loại giao dịch), phần hiển thị danh mục phải theo quy tắc đã thống nhất khi quản lý danh mục (Constitution VII; R136, R84–R86, R166). Hiện hộp còn hiển thị kiểu cũ: ô loại gốc cố định + một ô phẳng liệt kê đường dẫn con; gốc tự tạo (Property, Long Debt) lẫn trong ô con theo "loại". Chỉ đổi giao diện chọn, không đổi quy tắc tiền, phân loại gốc, báo cáo.

## Tư vấn kế toán (Constitution VIII)
Không có logic kế toán mới. Giữ nguyên: giao dịch ghi nhận theo loại gốc của danh mục chọn (báo cáo không đổi); thu nhập chỉ cho tiền vào; chi tiêu nhận chi và hoàn chi. Giao diện chỉ giúp chọn đúng danh mục và đối tượng, tránh phân loại nhầm do danh sách phẳng khó đọc.

## User Scenarios & Testing
### User Story 1 - Chọn danh mục theo cấp (P1)
Cấp 1 liệt kê **cùng danh sách gốc như màn Danh mục** (gốc hệ thống và gốc tự tạo, ngang hàng, tên danh mục, không còn khái niệm "nhóm chi/thu"), cộng "Chưa phân loại" và "Chuyển nội bộ · chờ đối ứng". Chọn một gốc thì hiện thêm ô cấp tiếp theo gồm các danh mục con trực tiếp (kèm lựa chọn "không chọn danh mục con"), lặp tới tối đa 4 cấp. Danh mục được chọn là cấp sâu nhất đã chọn.
1. **Given** Property (gốc tự tạo) có con "Chung cư", **When** chọn Property → Chung cư, **Then** giao dịch gắn danh mục Chung cư, loại gốc ghi nhận theo gốc của Property.
2. **Given** tiền ra, **Then** gốc Thu nhập và gốc tự tạo loại thu không hiện; tiền vào hiện đủ (Chi tiêu hiện "hoàn chi").
3. **Given** giao dịch đã phân loại, **When** mở lại, **Then** các ô cấp dựng sẵn đúng đường dẫn đã chọn.

### User Story 2 - Đối tượng của danh mục đã chọn (P1)
Đối tượng chỉ tải từ danh mục đang chọn (cấp sâu nhất); đổi danh mục thì danh sách đối tượng đổi theo; danh mục không có đối tượng thì không hiện ô đối tượng; tạo nhanh đối tượng/danh mục con vẫn dùng được và danh mục con mới nằm dưới danh mục đang chọn.

## Requirements
- **FR-001** (R169): cấp 1 = gốc hệ thống + gốc tự tạo đang hoạt động (như màn Danh mục) + Chưa phân loại + Chuyển nội bộ chờ đối ứng; cấp sau = danh mục con trực tiếp đang hoạt động; tối đa 4 cấp; luôn có lựa chọn dừng ở cấp hiện tại.
- **FR-002** (R170): loại gốc ghi nhận và danh mục (node) gửi lên khi lưu suy từ danh mục cấp sâu nhất; không đổi API, quy tắc, báo cáo.
- **FR-003** (R171): lọc theo hướng tiền: tiền ra không hiện gốc loại thu; dựng sẵn đường dẫn từ phân loại đã có (kể cả gốc tự tạo).
- **FR-004**: đối tượng chỉ của danh mục chọn; tạo nhanh danh mục con mặc định nằm dưới danh mục đang chọn.
## Success Criteria
SC-001 chọn được danh mục sâu 3–4 cấp mà không cần đọc đường dẫn dài; SC-002 phân loại trước/sau bằng giao diện cũ và mới cho cùng kết quả dữ liệu; SC-003 dữ liệu thật không đổi bởi phiên làm việc.
