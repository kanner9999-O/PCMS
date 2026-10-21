# Feature Specification: Ghi chú hiển thị cạnh cột nhãn; bỏ tên danh mục/đối tượng thừa trong lịch sử

**Feature Branch**: `039-history-note-layout` · **Created**: 2026-10-21 · **Status**: Draft
**Input**: Thạch xem lịch sử đối tượng thấy mỗi dòng hiện "Property · Đồi 3 (Chị Hương)" và nhãn "Lịch sử cũ": muốn dòng ghi chú (note) hiển thị **ngay cạnh cột "Lịch sử cũ"**, và **bỏ tên danh mục/đối tượng** vì thừa. Tham chiếu spec 038, 033; chuẩn lịch sử R84–R86. Chỉ đổi hiển thị.

## Tư vấn kế toán (Constitution VIII)
Không có logic kế toán. Giữ thông tin đủ truy vết: tiêu đề lịch sử đã nêu danh mục/đối tượng đang xem; chỉ hiện thêm nhãn khi nó **cung cấp thông tin mới** (danh mục con khác, hoàn chi, lãi vay).

## Requirements
- **FR-001** (R177): ghi chú, số chứng từ và nút sửa ghi chú nằm trong **cột nhãn**, cùng dòng với nhãn trạng thái (ví dụ "Lịch sử cũ"); cột nhãn rộng hơn để ghi chú không bị cắt.
- **FR-002** (R178): lịch sử **của một đối tượng**: không hiện tên đối tượng và đường dẫn danh mục khi chúng đã nằm ở tiêu đề (chỉ hiện đường dẫn khi đối tượng xuất hiện ở nhiều danh mục khác nhau, và các nhãn đặc biệt Hoàn chi tiêu / Lãi vay). Lịch sử **của một danh mục**: bỏ đường dẫn trùng tiêu đề, giữ tên đối tượng (cần để phân biệt) và đường dẫn danh mục con khác.
- **FR-003**: không đổi dữ liệu, tiền, báo cáo.
## Success Criteria
SC-001 dòng lịch sử cũ của một đối tượng chỉ còn "Lịch sử cũ" + ghi chú ở cột nhãn; SC-002 dữ liệu không đổi.
