# Feature Specification: Định dạng lịch sử giao dịch chuẩn

**Feature Branch**: `017-history-format`
**Created**: 2026-10-12
**Status**: Draft
**Input**: Thạch (12/10/2026): lịch sử ở quản lý danh mục nhìn không rõ, muốn mọi lịch sử danh mục/đối tượng hiển thị giống màn Kiểm tra phân loại; giao PO chốt một định dạng tiêu chuẩn (R94).

**Tham chiếu**: spec 002 (khoản vay), 008/014 (lịch sử danh mục), 011 (BĐS), 015 (màn Kiểm tra). Không đổi số liệu, quy tắc tiền, snapshot; chỉ đổi cách hiển thị (và thêm trường hiển thị vào dữ liệu trả về).

## Định dạng chuẩn (PO chốt)
1. **Đầu**: tên danh mục/đối tượng + kỳ (nếu có) và **tóm tắt**: số giao dịch, vào, ra, ròng (Chi tiêu: chi, hoàn chi, chi ròng; BĐS: vốn đã thanh toán/nhận lại; khoản vay: gốc vào/ra).
2. **Dòng giao dịch kiểu sao kê**: cột ngày + mã tham chiếu; nội dung + nút "Xem nguồn · n liên kết"; số tiền (ra dấu "-" màu ra, vào màu vào); nhãn (danh mục/đối tượng/loại phần) và trạng thái (nháp/"đã duyệt", "đã lưu trữ").
3. **Sắp xếp**: ngày giao dịch mới nhất trước; hòa theo mã tham chiếu.
4. **Giao dịch tách nhiều phần**: dòng ghi phần của danh mục/đối tượng đó và "Phần của giao dịch N VND".
5. **Cuối**: tổng bằng đúng tóm tắt đầu; thông báo nguồn/khoảng trống dữ liệu giữ như cũ.
6. **Trống**: giữ thông báo hiện có (thiếu nguồn / chưa có giao dịch trong kỳ, không phải xác nhận không phát sinh).
7. Mobile 375px: dòng xếp ngày/số tiền, nội dung, nhãn, không tràn ngang.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Lịch sử danh mục theo định dạng chuẩn (Priority: P1)
Từ màn Danh mục (và lịch sử theo tài khoản ở bước duyệt) Thạch mở "Lịch sử" của một danh mục và thấy đúng định dạng chuẩn.

**Independent Test**: danh mục Chi tiêu › Ăn uống có chi 450.000, hoàn chi 300.000, chi tách 60.000 → tóm tắt "Chi 510.000 · Hoàn chi 300.000 · Chi ròng 210.000", ba dòng mới nhất trước, dòng hoàn chi nhãn "Hoàn chi tiêu", dòng tách ghi phần của giao dịch 100.000.

**Acceptance Scenarios**:
1. **Given** danh mục có giao dịch, **When** mở Lịch sử, **Then** có tóm tắt và dòng chuẩn mới nhất trước.
2. **Given** dòng giao dịch, **When** bấm Xem nguồn, **Then** mở dòng sao kê nguồn như các màn khác.
3. **Given** danh mục chuyển nhóm (spec 016) hoặc đã lưu trữ, **When** xem, **Then** nhãn phản ánh danh mục hiệu lực và hiện "đã lưu trữ".

### User Story 2 - Lịch sử khoản vay và BĐS cùng định dạng (Priority: P1)
Chi tiết khoản vay (Công nợ) và Lịch sử BĐS hiển thị giao dịch bằng định dạng chuẩn, mỗi phần gốc/lãi (hoặc vốn/chi phí) một dòng với nhãn rõ.

**Independent Test**: khoản "Kết 10tr" có giải ngân 10tr, trả gốc 3tr, nhận lãi 200.000 → ba dòng kiểu sao kê nhãn "Gốc vay", "Gốc vay", "Lãi vay"; BĐS có vốn và chi phí → nhãn "Vốn", "Chi phí".

**Acceptance Scenarios**:
1. **Given** khoản vay, **When** mở chi tiết, **Then** các giao dịch gốc/lãi hiện dạng chuẩn, kèm cảnh báo "trước mốc" nếu có; các khối thiết lập/lịch sử giữ nguyên.
2. **Given** BĐS, **When** mở Lịch sử, **Then** tóm tắt vốn/chi phí hiện như cũ và dòng giao dịch dạng chuẩn.

### Edge Cases
- Danh mục/đối tượng không có giao dịch: thông báo trống như hiện có.
- Nhiều giao dịch (hàng trăm): danh sách cuộn trong hộp thoại, không tràn ngang.
- Kỳ lọc đang bật (spec 014): tóm tắt và dòng đúng kỳ.

## Requirements *(mandatory)*
- **FR-001** (R94): một thành phần hiển thị dòng giao dịch chuẩn dùng chung màn Kiểm tra phân loại, lịch sử danh mục, chi tiết khoản vay, lịch sử BĐS.
- **FR-002**: lịch sử danh mục và lịch sử BĐS trả thêm cho mỗi dòng `label`, `source_count`, `split`, `tx_amount`; không đổi các trường cũ và các tổng.
- **FR-003**: dòng sắp mới nhất trước (ngày, rồi mã tham chiếu giảm dần).
- **FR-004**: số liệu tổng không đổi so với trước đợt này.
- **FR-005**: giao diện không đổi dữ liệu; "Xem nguồn" mở chi tiết nguồn hiện có.

## Success Criteria
- **SC-001**: bốn nơi hiển thị lịch sử dùng cùng một định dạng (kiểm bằng bước dùng thử trên QA).
- **SC-002**: tổng ở tóm tắt bằng tổng các dòng (kiểm tự động cho lịch sử danh mục/BĐS).
- **SC-003**: 375px không tràn ngang; dữ liệu thật không đổi (SHA256).

## Assumptions
- Sắp mới nhất trước thay cho cũ nhất trước hiện tại (đổi so với bản cũ, PO chốt vì Thạch thường rà việc gần nhất).
- Không thêm lọc/tìm kiếm trong lịch sử đợt này.
