# Feature Specification: Người là đối tượng của danh mục, khoản vay là mục con — đồng nhất Danh mục và Quản lý đối tượng

**Feature Branch**: `040-person-owns-loan` · **Created**: 2026-10-21 · **Status**: Draft
**Input**: Thạch kiểm thấy màn Danh mục và màn Đối tượng không ăn khớp (Danh mục liệt kê 6 "khoản vay" làm đối tượng của Gốc vay; màn Đối tượng liệt kê 6 người nhưng "chưa thuộc danh mục nào"). Thạch chọn **phương án B**: theo nghiệp vụ đã thống nhất, **một đối tượng (người) thuộc danh mục**, khoản vay là mục con của người; các loại đối tượng hiện có giữ nguyên, bổ sung sau. Tham chiếu spec 031, 032, 033, 037; Constitution I, II, IV, VII, VIII; R136, R146–R153, R158–R163.

## Tư vấn kế toán (Constitution VIII)
- Khoản vay là quan hệ giữa **hai bên**: người cho vay / đi vay là chủ thể của sổ chi tiết. Vì vậy **người** là đối tượng của danh mục, khoản vay (từng hợp đồng: gốc đầu mốc, chiều, lãi) là chi tiết con. Một người có nhiều khoản vay thì gom một đối tượng, sổ chi tiết theo từng khoản.
- **Phải thu và Phải trả không bù trừ**: người có khoản Phải thu và khoản Phải trả phải ở **hai danh mục khác nhau** (chuyển danh mục khoản vay); nếu cùng một danh mục thì hợp nhất báo **xung đột**, không tự gộp.
- Phân loại tiền vẫn gắn vào **khoản vay cụ thể** (gốc/lãi) để sổ Công nợ giữ nguyên; giao diện chỉ chọn người trước rồi khoản vay. Không đổi phân loại, báo cáo, snapshot, sổ Công nợ.
- Cơ sở tiền thực thu/chi; dồn tích lãi, dự phòng, xóa nợ cần kế toán viên xác nhận (không làm ở đây).

## User Scenarios & Testing
### User Story 1 - Hợp nhất cấu trúc theo người (P1)
"Hợp nhất hồ sơ nghiệp vụ" (xem trước + xác nhận): mỗi người có khoản vay thành **thành viên** của danh mục nơi khoản vay thuộc về (nhóm của khoản vay hoặc Gốc vay) và mang nghiệp vụ theo chiều đã thiết lập; khoản vay **thôi là thành viên** danh mục (giữ bản ghi, đánh dấu chuyển sang người). Khoản chưa thiết lập chiều: người được thêm vào danh mục, chưa gắn loại. Người có khoản trái chiều trong cùng danh mục: báo xung đột, không đổi.
1. **Given** Kết có Kết 5tr, Kết 10tr (Phải thu), **When** hợp nhất, **Then** Kết là đối tượng của Gốc vay, nghiệp vụ Cho vay, hai khoản là mục con; số liệu, báo cáo, sổ Công nợ không đổi.
2. **Given** chạy lại, **Then** báo không còn gì để làm.

### User Story 2 - Hai màn nhất quán (P1)
Màn **Danh mục** hiện người (kèm các khoản vay con và tổng); màn **Đối tượng** hiện danh mục của người kể cả khi chưa hợp nhất (ghi "qua khoản vay") và báo khi hai màn chưa đồng nhất (kèm nút hợp nhất). Lịch sử của người gồm cả khoản vay của họ.

### User Story 3 - Phân loại: chọn người rồi khoản vay (P1)
Trong hộp phân loại, Gốc vay/Lãi vay liệt kê **người** (thành viên danh mục hoặc có khoản vay); chọn người thì hiện ô **Khoản vay** (chọn bắt buộc khi người có khoản vay); lưu vẫn gắn khoản vay cụ thể.

## Requirements
- **FR-001** (R179): `business-migrate` đổi cấu trúc: người sở hữu khoản vay là thành viên danh mục chứa khoản vay (nhóm hoặc Gốc vay) và mang loại theo chiều thiết lập; khoản vay thôi là thành viên (status REMOVED, lịch sử MIGRATED_TO_PERSON); khoản trái chiều cùng danh mục → CONFLICT; chưa thiết lập chiều → chỉ thêm người; idempotent; BĐS như cũ.
- **FR-002** (R180): nghiệp vụ vay gắn cho **người**, không gắn cho hồ sơ khoản vay; chặn khi khoản vay của người trong danh mục thiết lập chiều khác; sổ nghiệp vụ của người gồm các khoản (số dư, lãi, đối chiếu sổ Công nợ từng khoản).
- **FR-003** (R181): không gỡ người khỏi danh mục khi còn khoản vay thuộc danh mục; lưu trữ danh mục như quy tắc cũ.
- **FR-004** (R182): màn Danh mục: người hiện khoản vay con và tổng gồm các khoản; hàng khoản vay cũ hiện tên người; màn Đối tượng: danh mục của người gồm danh mục khoản vay (đánh dấu "qua khoản vay") và cảnh báo `issues` (`LOAN_AS_MEMBER`, `PERSON_NOT_MEMBER`) kèm nút hợp nhất.
- **FR-005** (R183): lịch sử của người luôn gồm các khoản vay của họ (mọi phạm vi).
- **FR-006** (R184): hộp phân loại: Gốc vay/Lãi vay liệt kê người; ô Khoản vay hiện khi người có khoản vay, chọn bắt buộc; dựng sẵn từ phân loại đã có.
- **FR-007**: không đổi quy tắc tiền, báo cáo, snapshot, sổ Công nợ; dữ liệu thật chỉ đổi khi Thạch bấm hợp nhất.
## Success Criteria
SC-001 sau hợp nhất `objects.issues` rỗng và hai màn liệt kê cùng người với cùng danh mục; SC-002 báo cáo/sổ Công nợ không đổi; SC-003 dữ liệu thật không đổi bởi phiên làm việc.
