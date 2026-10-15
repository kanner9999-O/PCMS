# Feature Specification: Ghi chú giao dịch, chi phí mua BĐS vốn hóa, chi không chứng từ

**Feature Branch**: `030-note-capitalized-costs` · **Created**: 2026-10-15 · **Status**: Draft
**Input**: Thạch hỏi cách quản lý giao dịch có mục đích riêng (phí công chứng, tiền "bôi trơn" giấy tờ) theo nghiệp vụ kế toán; chọn đề xuất: ghi chú + số chứng từ, danh mục con vốn hóa cho chi phí mua BĐS, danh mục riêng cho chi không chứng từ (R141–R145). Tham chiếu spec 009, 011, 013, 026. Tuân Constitution VII và VIII.

## Tư vấn kế toán (Constitution VIII)
- **Phương án và khuyến nghị**: ba lớp thông tin cho mỗi giao dịch: danh mục (bản chất, quyết định cách ghi nhận), đối tượng (của ai/cái gì), ghi chú (vì sao, chi tiết). Chỉ mục đích làm đổi cách ghi nhận mới thành danh mục. Chi phí trực tiếp liên quan đến việc mua BĐS (công chứng, thuế trước bạ, môi giới) được **vốn hóa vào nguyên giá**; chi phí sửa chữa/vận hành là chi phí kỳ. Khoản chi không có chứng từ hợp lệ không được vốn hóa và không là chi phí hợp lệ về thuế: ghi **trung thực**, tách riêng, kèm ghi chú.
- **Hệ quả lên số liệu**: giá gốc BĐS tăng đúng bằng chi phí mua vốn hóa ròng (hoàn chi trừ đi); chênh lệch chưa thực hiện tính trên giá gốc mới; chi phí vận hành vẫn ở "Chi phí gắn BĐS". Chi không chứng từ không ảnh hưởng giá gốc.
- **Cần kế toán viên/thuế/luật xác nhận**: tính hợp lệ về thuế và pháp lý của các khoản không chứng từ (đặc biệt khoản chi cho người có chức vụ để giải quyết giấy tờ có thể là vi phạm pháp luật); mức và điều kiện vốn hóa theo quy định thuế hiện hành.

## User Scenarios & Testing
### User Story 1 - Ghi chú và số chứng từ cho giao dịch (Priority: P1)
Trong hộp phân loại (một giao dịch) có ô "Ghi chú / diễn giải" và "Số chứng từ (tùy chọn)"; lưu cùng phân loại. Ghi chú hiện dưới nội dung ở mọi lịch sử (danh mục, đối tượng, tài khoản) và màn Kiểm tra; sửa được riêng không cần phiên điều chỉnh.

**Acceptance Scenarios**:
1. **Given** giao dịch, **When** phân loại kèm ghi chú và số chứng từ, **Then** lưu bền, hiện ở các lịch sử và có lịch sử thay đổi.
2. **Given** giao dịch đã duyệt, **When** sửa riêng ghi chú, **Then** lưu không cần phiên điều chỉnh và không đổi số tiền, phân loại, snapshot.
3. **Given** phân loại hàng loạt kèm ghi chú, **When** lưu, **Then** ghi chú áp cho mọi dòng chọn; bỏ trống thì không đổi.

### User Story 2 - Danh mục mẫu chi phí mua BĐS vốn hóa; giá gốc đúng (Priority: P1)
Nút "Danh mục mẫu" tạo "Chi phí mua BĐS (vốn hóa)" (Công chứng, Thuế trước bạ, Môi giới, Khác). Chi phí phân loại vào đây và gắn BĐS cộng vào giá gốc.

**Independent Test**: BĐS Đất A vốn đã thanh toán ròng 600.000.000; chi công chứng 5.000.000 (vốn hóa) và chi sửa hàng rào 3.000.000 (chi phí thường), hoàn công chứng 1.000.000 → vốn ròng 600.000.000, chi phí mua vốn hóa ròng 4.000.000, **giá gốc 604.000.000**, chi phí gắn BĐS thường 3.000.000; giá trị hiện tại 900.000.000 → chênh lệch chưa thực hiện 296.000.000; Tổng tài sản BĐS theo giá gốc 604.000.000.

**Acceptance Scenarios**:
1. **Given** hai danh mục mẫu chưa có, **When** bấm tạo, **Then** tạo đủ danh mục và con; tạo lại báo đã có.
2. **Given** chi phí vốn hóa gắn BĐS, **When** xem màn BĐS, **Then** hiện "Chi phí mua vốn hóa" và "Giá gốc ghi sổ" riêng; chi phí thường tách riêng, không đếm kép.
3. **Given** BĐS chưa định giá, **When** xem Tổng tài sản, **Then** giá trị theo giá gốc mới kèm cơ sở "vốn thanh toán ròng + chi phí mua vốn hóa".
4. **Given** dữ liệu đã phân loại trước đó, **When** triển khai, **Then** không đổi (chỉ phân loại mới/ sửa mới vào danh mục vốn hóa mới đổi giá gốc).

### User Story 3 - Chi khác không chứng từ (Priority: P1)
Danh mục mẫu "Chi khác không chứng từ": hiển thị riêng, không vốn hóa, ghi chú bắt buộc khi phân loại.

**Acceptance Scenarios**:
1. **Given** phân loại vào danh mục này thiếu ghi chú, **When** lưu, **Then** bị chặn với lý do.
2. **Given** có ghi chú, **When** lưu, **Then** lưu được; không ảnh hưởng giá gốc BĐS.
3. **Given** xem Danh mục/lịch sử, **When** mở, **Then** hiện riêng cùng ghi chú.

## Requirements
- **FR-001** (R141): trường `note` (≤ 1000) và `voucher` (≤ 100) trên giao dịch, có `note_history`; `classify` nhận `note`/`voucher` tùy chọn (áp cho mọi dòng chọn; vắng = không đổi); hành động `transaction-note` sửa riêng không cần phiên điều chỉnh; hiển thị ở lịch sử danh mục, đối tượng, tài khoản, màn Kiểm tra.
- **FR-002** (R142, R145): hành động `category-template` tạo danh mục mẫu (idempotent) kèm cờ `capitalize` (lan xuống con) hoặc `note_required`.
- **FR-003** (R143): phần chi/hoàn thuộc danh mục có cờ `capitalize`, gắn BĐS → chi phí mua vốn hóa; giá gốc = vốn ròng + chi phí mua vốn hóa ròng; chênh lệch chưa thực hiện và Tổng tài sản (cơ sở giá gốc) dùng giá gốc; chi phí còn lại giữ ở "Chi phí gắn BĐS".
- **FR-004** (R144): danh mục có `note_required` đòi ghi chú không rỗng khi phân loại (và khi sửa ghi chú không cho xóa).
- **FR-005**: không đổi tiền, snapshot, sao kê; dữ liệu cũ không đổi.

## Success Criteria
- **SC-001**: ví dụ Đất A cho đúng: vốn ròng 600.000.000; chi phí mua vốn hóa ròng 4.000.000; giá gốc 604.000.000; chi phí thường 3.000.000; chênh lệch 296.000.000.
- **SC-002**: chi không chứng từ thiếu ghi chú bị chặn 100%; không đổi giá gốc.
- **SC-003**: ghi chú hiện đúng ở mọi lịch sử; dữ liệu thật không đổi (SHA256); 375px không tràn ngang.

## Assumptions
- Cờ vốn hóa chỉ áp dụng khi phần chi gắn hồ sơ BĐS; không gắn BĐS thì chỉ là chi tiêu thường.
- Ghi chú áp cho cả giao dịch (không riêng từng phần tách).
