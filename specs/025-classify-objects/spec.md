# Feature Specification: Phân loại theo danh mục, danh mục con, đối tượng

**Feature Branch**: `025-classify-objects` · **Created**: 2026-10-14 · **Status**: Draft
**Input**: Thạch muốn phiên phân loại/điều chỉnh chỉ còn: danh mục cha → danh mục con → đối tượng (hiện hết nếu danh mục có đối tượng), tách khỏi nghiệp vụ tài chính; mỗi danh mục tự khai loại đối tượng; popup có nút ✕ góc trên phải (R118–R122). Tham chiếu spec 008, 009, 014, 016. Không đổi dữ liệu đã phân loại, không đổi quy tắc tiền.

## User Scenarios & Testing
### User Story 1 - Khai báo loại đối tượng cho danh mục (Priority: P1)
Ở màn Danh mục, mỗi danh mục (gốc hệ thống, gốc tự tạo, con) có nút "Đối tượng": chọn Không có / Người / Khoản vay / BĐS (con có thêm "Kế thừa từ cha"). Mặc định mọi danh mục hệ thống là Không có; con kế thừa từ cha.

**Independent Test**: khai "Gốc vay" = Người; danh mục con "Cho vay" (do Thạch tạo) kế thừa Người; đặt riêng con "Vay" = Khoản vay → "Vay" là Khoản vay, các con của "Gốc vay" khác vẫn Người; về Kế thừa thì lại Người.

**Acceptance Scenarios**:
1. **Given** danh mục, **When** đặt loại đối tượng, **Then** lưu kèm lịch sử và hiển thị loại hiệu lực (kể cả kế thừa) ở màn Danh mục.
2. **Given** con không tự đặt, **When** cha đổi loại, **Then** con đổi theo.
3. **Given** loại không hợp lệ hoặc gốc "Chưa phân loại", **When** đặt, **Then** bị chặn.

### User Story 2 - Phân loại: danh mục → danh mục con → đối tượng (Priority: P1)
Hộp phân loại gồm: Danh mục (loại), Danh mục con (nếu có), Đối tượng (chỉ hiện nếu danh mục/danh mục con đã khai loại đối tượng; liệt kê **tất cả** đối tượng loại đó, kèm "+ Tạo nhanh"). Không còn bước chọn người rồi khoản vay; không còn nút "+ Tách thêm phần" (giao dịch đã tách vẫn sửa được).

**Independent Test**: "Gốc vay" khai Người; phân loại giao dịch 500tr → Gốc vay → danh sách người (Kết, Tươi, Thái) → chọn Kết → lưu được không cần khoản vay; danh mục chưa khai (Chi tiêu) → không hiện ô đối tượng.

**Acceptance Scenarios**:
1. **Given** danh mục đã khai Người, **When** mở hộp phân loại và chọn danh mục đó, **Then** thấy ô Đối tượng liệt kê mọi người; chọn danh mục con có loại khác thì đổi danh sách theo.
2. **Given** danh mục chưa khai, **When** chọn, **Then** không có ô Đối tượng.
3. **Given** đối tượng không đúng loại danh mục đã khai, **When** lưu, **Then** bị chặn kèm lý do.
4. **Given** danh mục chưa khai nhưng giao dịch đã phân loại cũ có đối tượng (ví dụ Gốc vay gắn khoản vay), **When** mở sửa, **Then** đối tượng cũ vẫn hiện (nhãn "giữ như cũ") và không bị mất khi lưu.
5. **Given** tạo nhanh đối tượng (người/khoản vay/BĐS) hoặc danh mục con ngay trong hộp, **When** lưu, **Then** tạo xong và được chọn.
6. **Given** giao dịch chưa tách, **When** mở hộp, **Then** không có nút "+ Tách thêm phần"; giao dịch đã tách hiện các phần như cũ.

### User Story 3 - Nút ✕ góc trên phải (Priority: P2)
Mọi popup (review, lịch sử, preview, phân loại, biểu mẫu) có nút ✕ ở góc trên bên phải đóng popup; màn Kiểm tra phân loại có "✕ Đóng" ở góc trên phải (giữ "← Quay lại").

**Acceptance Scenarios**:
1. **Given** popup đang mở, **When** bấm ✕, **Then** đóng như nút Đóng/Hủy, không lưu.
2. **Given** màn Kiểm tra phân loại, **When** bấm "✕ Đóng", **Then** quay về bước Phân loại.

### Edge Cases
- Danh mục lưu trữ/xóa không ảnh hưởng loại đối tượng của danh mục khác.
- Đối tượng người đã gắn Gốc vay mới không tự cập nhật Công nợ (tạm tách); giao dịch cũ gắn khoản vay vẫn chạy.
- Phân loại hàng loạt: một loại, một đối tượng áp cho mọi dòng (nếu danh mục có đối tượng).

## Requirements
- **FR-001** (R119): hành động đặt loại đối tượng cho danh mục gốc hệ thống (trừ Chưa phân loại), gốc tự tạo, danh mục con; con kế thừa; có lịch sử; hiển thị loại khai báo và loại hiệu lực.
- **FR-002** (R118, R120): hộp phân loại danh mục → con → đối tượng (liệt kê hết đối tượng đúng loại hiệu lực, tạo nhanh được người/khoản vay/BĐS/danh mục con).
- **FR-003** (R120): kiểm tra khi lưu: đối tượng không bắt buộc; nếu có phải đúng loại hiệu lực; danh mục chưa khai loại → quy tắc cũ (Gốc/Lãi: khoản vay; Đầu tư: BĐS; Chi tiêu: khoản vay hoặc BĐS; còn lại không); dữ liệu đã lưu không đổi.
- **FR-004** (R121): ẩn "+ Tách thêm phần" khi giao dịch chưa tách; backend không đổi.
- **FR-005** (R122): nút ✕ trên mọi popup và màn Kiểm tra phân loại.
- **FR-006**: không đổi tiền, snapshot, báo cáo; đọc không ghi.

## Success Criteria
- **SC-001**: phân loại một giao dịch vào (danh mục, đối tượng) ≤ 3 lựa chọn, không cần khoản vay.
- **SC-002**: kế thừa/đặt riêng loại đối tượng cho đúng ở mọi cấp; đối tượng sai loại bị chặn 100%.
- **SC-003**: dữ liệu thật không đổi (SHA256); 375px không tràn ngang.

## Assumptions
- Đối tượng hiện hết = mọi hồ sơ đúng loại (người / khoản vay / BĐS).
- Giao dịch gắn người trong Gốc vay chưa vào Công nợ cho tới khi tích hợp nghiệp vụ.
