# Feature Specification: Migrate lịch sử cũ từ Excel

**Feature Branch**: `027-legacy-import` · **Created**: 2026-10-15 · **Status**: Draft
**Input**: Thạch có lịch sử giao dịch cũ trong Google Sheets "Long Debt" (mỗi tab một người, ví dụ Mỹ) nằm ngoài sao kê hiện tại; muốn migrate sang đối tượng trong danh mục Long debt, dán từ Sheets, mẫu cột mẫu (R129–R134). Chọn phương án 1: bản ghi "lịch sử cũ" ngoài chuỗi sao kê. Tham chiếu spec 008, 014, 017, 026. Không đổi chuỗi sao kê, mốc, tổng tài sản, Công nợ.

## User Scenarios & Testing
### User Story 1 - Dán, xem trước, ghi lịch sử của một đối tượng (Priority: P1)
Ở màn Danh mục, nút "Migrate lịch sử cũ" mở hộp: chọn danh mục (Long debt), đối tượng (chọn có sẵn hoặc nhập tên mới như Mỹ), dán vùng ô copy từ Google Sheets. Bấm "Xem trước" thấy bảng các dòng sẽ nhập (ngày, nội dung, mã, ra/vào, số dư tham khảo, trạng thái từng dòng), tổng ra/vào và so với dòng tổng. Hết lỗi mới cho "Ghi".

**Independent Test**: dán dữ liệu tab Mỹ (dòng tổng 176.000.000 / 130.000.000 / 46.000.000 và 8 giao dịch) → xem trước 8 dòng, tổng ra 176.000.000, vào 130.000.000, khớp dòng tổng; ghi → đối tượng Mỹ ở Long debt có 8 giao dịch, vào 130.000.000, ra 176.000.000, ròng −46.000.000.

**Acceptance Scenarios**:
1. **Given** dữ liệu hợp lệ, **When** xem trước, **Then** hiện đủ dòng, tổng khớp dòng tổng, nút Ghi bật.
2. **Given** dòng sai (ngày sai, cả ra và vào, số không hợp lệ, thiếu ngày), **When** xem trước, **Then** dòng đó báo lỗi rõ số dòng và nút Ghi bị chặn.
3. **Given** tổng các dòng lệch dòng tổng, **When** xem trước, **Then** cảnh báo nêu chênh lệch; chỉ ghi được khi xác nhận.
4. **Given** đối tượng chưa có, **When** ghi, **Then** tạo đối tượng và gán vào danh mục; đã có thì dùng lại (tự gán nếu chưa thuộc danh mục).
5. **Given** dòng trống, ô trống, định dạng số 30,000,000.00, ngày d/m/yyyy, **When** xem trước, **Then** đọc đúng; dòng tổng không có ngày không bị coi là lỗi.

### User Story 2 - Hiện trong lịch sử và tổng, không đụng sao kê (Priority: P1)
Sau khi ghi, các dòng hiện trong màn Danh mục (tổng của đối tượng và danh mục, lịch sử đối tượng) với nhãn "Lịch sử cũ"; số dư tài khoản, mốc snapshot, kiểm liền mạch, báo cáo duyệt không đổi.

**Acceptance Scenarios**:
1. **Given** đã migrate Mỹ, **When** xem Danh mục, **Then** Mỹ trong Long debt hiện 8 giao dịch, vào/ra đúng; tổng Long debt tăng tương ứng.
2. **Given** mở lịch sử của Mỹ, **When** xem, **Then** dòng sao kê chuẩn, mới nhất trước, nhãn "Lịch sử cũ", số dư tham khảo, ghi chú nguồn (dòng n).
3. **Given** báo cáo tài khoản, tổng tài sản, mốc, Kiểm tra phân loại, **When** xem, **Then** không có thay đổi nào.

### User Story 3 - Tự nhận trùng và hủy (Priority: P2)
**Acceptance Scenarios**:
1. **Given** dòng cũ có mã trùng một giao dịch sao kê (so sau khi bỏ đuôi `\...`), **When** xem trước hoặc sau khi sao kê nhập sau, **Then** dòng đánh dấu "đã có trong sao kê" và không tính vào tổng.
2. **Given** dán lại cùng dữ liệu, **When** xem trước, **Then** các dòng trùng lần migrate trước bị bỏ qua và báo số dòng.
3. **Given** một lần migrate, **When** hủy kèm lý do, **Then** tổng trở lại như trước, bản ghi và bản dán gốc vẫn xem được.

### Edge Cases
- Ánh xạ cột khác mẫu (một cột số tiền có dấu, thiếu số dư): hỗ trợ qua chọn vai trò từng cột.
- Số kiểu Việt "30.000.000": hiểu là ba mươi triệu; số lẻ khác .00 bị lỗi (VND nguyên).
- Dán nhiều tab một lần: không hỗ trợ (mỗi lần một đối tượng); tab "Total" không dán.

## Requirements
- **FR-001** (R129–R131): hành động chỉ đọc xem trước và hành động ghi (ghi chạy lại phân tích phía máy chủ, không tin kết quả xem trước của giao diện); mẫu cột mặc định và ánh xạ vai trò cột (ngày, nội dung, mã, ra, vào, số tiền có dấu, số dư, bỏ qua).
- **FR-002**: phân tích: bỏ dòng rỗng; dòng không ngày chỉ có số = dòng tổng (đối chiếu); ngày d/m/yyyy hoặc yyyy-mm-dd hợp lệ; đúng một trong tiền ra/vào > 0 (hoặc số tiền có dấu ≠ 0); VND nguyên; mỗi dòng báo lỗi kèm số dòng.
- **FR-003** (R132): `cat_parts` cung cấp thêm các dòng lịch sử cũ (loại trừ dòng trùng sao kê và lần migrate đã hủy) cho tổng và lịch sử danh mục/đối tượng; không đưa vào báo cáo theo tài khoản, Kiểm tra phân loại, tổng tài sản, mốc.
- **FR-004** (R133): trùng mã sao kê (chuẩn hóa: bỏ từ `\` trở đi, không phân biệt hoa thường) tính động; trùng lần migrate trước bị bỏ qua khi ghi.
- **FR-005** (R134): hủy cả lần migrate có lý do; lưu bản dán gốc, mã băm, số dòng.
- **FR-006**: giao diện: nút, hộp dán, xem trước, danh sách các lần migrate (hủy), lịch sử có nhãn "Lịch sử cũ"; 375px không tràn ngang.
- **FR-007**: không đổi tiền ở sao kê, snapshot, Công nợ; đọc không ghi.

## Success Criteria
- **SC-001**: ví dụ Mỹ cho đúng 8 dòng, vào 130.000.000, ra 176.000.000, ròng −46.000.000 và khớp dòng tổng.
- **SC-002**: mọi dòng sai bị chặn đúng số dòng; số liệu tài khoản/tổng tài sản/mốc không đổi sau migrate (so sánh trước/sau).
- **SC-003**: dòng trùng mã sao kê không tính hai lần; dữ liệu thật không đổi (SHA256) cho tới khi Thạch tự dán.

## Assumptions
- Mỗi lần dán là một đối tượng và một danh mục; đơn vị VND.
- Đối tượng mới có loại "đối tượng" (spec 026); nghiệp vụ cho vay gắn sau.
- Số dư tài khoản ở cột F chỉ lưu để tham khảo, không kiểm chuỗi.
