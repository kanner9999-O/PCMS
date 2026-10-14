# Feature Specification: Xem trước giao dịch sẽ nhập

**Feature Branch**: `024-import-preview` · **Created**: 2026-10-14 · **Status**: Draft
**Input**: Thạch chỉ thấy "52 mới / 127 trùng" nhưng không nhìn được 52 giao dịch mới nối vào chuỗi như thế nào; muốn xem trước để kiểm đúng/sai (R115–R117). Tham chiếu spec 022 (nối tiếp theo số dư), 017 (dòng sao kê chuẩn), 023. Chỉ đọc.

## User Scenarios & Testing
### User Story 1 - Xem trước giao dịch mới nối vào chuỗi (Priority: P1)
Với file chờ ghi, Thạch bấm "Xem trước giao dịch sẽ nhập" cạnh "Xem dòng nguồn" và thấy giao dịch cuối đã ghi (mốc), rồi mọi giao dịch mới theo thứ tự nối tiếp, mỗi dòng có số dư tính, số dư file, ✔/✘; cuối có tổng vào/ra và số dư cuối dự kiến.

**Independent Test**: tài khoản đã ghi (44) giả lập (giao dịch cuối R4, số dư 1.011.000); file (46) giả lập thêm N1, N2, N3 → preview: dòng mốc R4, rồi N1 (số dư tính 953.000 = file ✔), N2 (853.000 ✔), N3 (843.000 ✔); tổng ra 168.000; số dư cuối dự kiến 843.000 = cuối file ✔; 3 dòng trùng không hiện.

**Acceptance Scenarios**:
1. **Given** file chờ ghi có dòng mới, **When** xem trước, **Then** hiện mốc rồi đúng các dòng mới theo thứ tự file, không hiện dòng trùng.
2. **Given** số dư tính khác số dư trong file ở một dòng, **When** xem trước, **Then** dòng đó ✘ và đỏ (và tổng kết cảnh báo).
3. **Given** file không có dòng mới (chỉ trùng), **When** xem trước, **Then** hiện "không có giao dịch mới".
4. **Given** tài khoản chưa có giao dịch (file đầu tiên), **When** xem trước, **Then** mốc là số dư đầu tài khoản và mọi dòng của file là mới.
5. **Given** file bị chặn hoặc đã ghi/loại, **When** mở trạng thái file, **Then** không có nút xem trước; gọi trực tiếp bị từ chối kèm lý do.

### Edge Cases
- Nhiều dòng (hàng trăm): danh sách cuộn trong hộp rộng; số dòng mới hiển thị ở tiêu đề.
- Dòng cùng ngày giao dịch cuối: vẫn là dòng mới (spec 022).

## Requirements
- **FR-001** (R115): hành động chỉ đọc trả preview cho file STAGED: mốc (giao dịch cuối đã ghi hoặc số dư đầu tài khoản), các dòng mới theo thứ tự file, số dư tính, số dư file, trạng thái khớp từng dòng, tổng vào/ra, số dư cuối dự kiến, số dư cuối file, số dòng trùng ẩn.
- **FR-002** (R116): giao diện hiển thị mốc rồi các dòng theo dòng sao kê chuẩn với số dư tính/số dư file và ✔/✘, tổng kết cuối.
- **FR-003** (R117): file BLOCKED/PUBLISHED/DISMISSED: không có nút; API từ chối.
- **FR-004**: không đổi dữ liệu; nút "Ghi toàn đợt" vẫn như cũ.

## Success Criteria
- **SC-001**: số dòng preview bằng số dòng mới mà bước kiểm tra báo; số dư cuối dự kiến bằng số dư cuối sau khi ghi.
- **SC-002**: lệch số dư ở bất kỳ dòng nào đều hiện ✘; dữ liệu thật không đổi.

## Assumptions
- Số dư tính của dòng đầu = số dư sau giao dịch mốc (hoặc số dư đầu tài khoản); mỗi dòng sau = trước ± số tiền.
