# Research: 016 loan-category-management

**Quyết định 1 — nhóm danh mục là thuộc tính của khoản vay, không sửa từng phân bổ.** Mỗi khoản vay có `group` (id danh mục Gốc vay, hoặc rỗng = Gốc vay) và `group_history`. Lúc tính tổng/hiển thị, phần **Gốc vay** gắn khoản vay dùng `group` làm danh mục hiệu lực; phân bổ gốc của giao dịch không đổi. *Vì sao*: chuyển cả khoản bằng một thao tác, giao dịch phát sinh sau tự theo, không viết lại lịch sử phân loại, snapshot (báo cáo đã duyệt lưu riêng) không bị đụng. *Phương án bỏ*: sửa phân bổ hàng loạt (đổi nhiều giao dịch, ghi đè lịch sử phân loại, ảnh hưởng đã duyệt).

**Quyết định 2 — chỉ phần Gốc vay đi theo nhóm.** Lãi vay ở cây khác (loại khác). Ghi ở Assumptions của spec.

**Quyết định 3 — một điểm hợp nhất.** Thêm `cat_eff(s,p)` trả bản sao phần với `node` hiệu lực; `cat_parts` dùng nó nên `category_view`, `category_history`, `category_review` tự đúng; `classification_review` dùng cùng hàm cho nhóm đối tượng.

**Quyết định 4 — gom màn Kiểm tra theo (danh mục đỉnh hiệu lực + đối tượng).** Với phần có đối tượng: danh mục đỉnh = đường dẫn nhóm của khoản (nếu có `group`) hoặc gốc/gốc tự tạo của danh mục con; nhãn dòng = đường dẫn danh mục con của chính giao dịch. Phần không đối tượng giữ đường dẫn như 015.

**Quyết định 5 — chặn đối tượng ở loại không cho phép tại lúc lưu (`classify`).** Dữ liệu cũ không đổi (không migrate).

**Quyết định 6 — xóa hẳn = kiểm "chưa từng dùng" bằng quét id** trong phân bổ hiện tại, `classification_history`, báo cáo trong snapshot và `group`/`group_history` của khoản vay; kèm không có con và không phải gốc hệ thống. Ghi `category_deleted`.

**Quyết định 7 — nhãn khoản vay tính ở backend** (`loan_options` trong `view()`), giao diện chỉ ghép chữ.
