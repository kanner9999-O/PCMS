# Feature Specification: Thêm đối tượng vào danh mục theo loại, có gợi ý tìm kiếm

**Feature Branch**: `035-object-suggest` · **Created**: 2026-10-16 · **Status**: Draft
**Input**: Thạch: trong hộp "Thêm đối tượng" (màn Danh mục) cần liệt kê đối tượng theo **loại đối tượng** và có **gợi ý tìm kiếm** để nhanh chóng chọn đối tượng thêm vào danh mục. Tham chiếu spec 026, 029, 033; Constitution VII; R158–R163. Chỉ đổi giao diện chọn; không đổi quy tắc dữ liệu.

## Tư vấn kế toán (Constitution VIII)
Không có logic kế toán mới. Giữ quy tắc: tên đối tượng duy nhất toàn hệ thống (tránh hai sổ chi tiết cho cùng một đối tượng), đối tượng đã lưu trữ không thêm vào danh mục mới. Danh sách gợi ý chỉ liệt kê đối tượng đang hoạt động, chưa thuộc danh mục này.

## User Scenarios & Testing
### User Story 1 - Danh sách theo loại + lọc loại (P1)
Hộp liệt kê đối tượng chưa thuộc danh mục, **nhóm theo loại** (Người, Bất động sản, Khác), có nút lọc nhanh theo loại kèm số lượng.
1. **Given** có Người và BĐS chưa thuộc danh mục, **Then** hiện hai nhóm có tiêu đề; lọc "Người" chỉ còn nhóm Người.
2. Đối tượng đã thuộc danh mục, đã lưu trữ, đã gộp không hiện.

### User Story 2 - Gợi ý tìm kiếm (P1)
Gõ vào ô tìm: danh sách thu hẹp tức thì theo tên, **không phân biệt hoa/thường và dấu** ("tuoi" khớp "Tươi"), đoạn khớp được tô, khớp đầu tên xếp trước; ↑/↓ chọn, Enter thêm vào danh sách chọn, Esc xóa ô tìm.
1. "ket" gợi ý "Kết", "Kết2"; "xuan mai" khớp "Xuân Mai".

### User Story 3 - Chọn nhiều và tạo mới tại chỗ (P1)
Chọn nhiều đối tượng một lần (hiện thành thẻ "Đã chọn"); nếu tên gõ vào chưa có thì hiện "+ Tạo mới «tên»" kèm chọn loại (Người / BĐS / Khác); tên đã có (kể cả đã thuộc danh mục hay đã lưu trữ) thì báo lý do, không tạo trùng. Bấm Thêm: tạo các đối tượng mới rồi thêm tất cả vào danh mục.

## Requirements
- **FR-001** (R166): hộp "Thêm đối tượng" liệt kê đối tượng đang hoạt động chưa thuộc danh mục, nhóm theo loại, lọc theo loại có số lượng.
- **FR-002** (R167): gợi ý tìm theo tên không phân biệt hoa/thường/dấu, tô đoạn khớp, khớp đầu tên xếp trước, điều khiển bằng bàn phím.
- **FR-003** (R168): chọn nhiều; tạo mới tại chỗ với loại (qua `object-create`); chặn trùng tên với thông báo rõ.
- **FR-004**: không đổi dữ liệu, quy tắc tiền, báo cáo.
## Success Criteria
SC-001 tìm ra đối tượng trong ≤ 3 thao tác (gõ, chọn, Thêm); SC-002 "tuoi" tìm được "Tươi"; SC-003 dữ liệu thật không đổi bởi phiên làm việc.
