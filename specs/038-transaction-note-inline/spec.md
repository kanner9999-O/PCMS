# Feature Specification: Ghi chú giao dịch — sửa ngay trên dòng lịch sử và nhập từ migrate

**Feature Branch**: `038-transaction-note-inline` · **Created**: 2026-10-21 · **Status**: Draft
**Input**: Thạch: mỗi giao dịch cần trường "Note" (mục đích hoặc lưu ý). Migrate dữ liệu cũ có cột thông tin đó thì nhập thành note. Khi hiển thị dòng giao dịch (lịch sử) cần có cách bổ sung note. Ví dụ: nội dung ngân hàng ghi "uống rượu" nhưng mục đích thật là tiền môi giới. Tham chiếu spec 030 (R141–R145), 027, 028, 033; Constitution I, II, IV.

## Hiện trạng và phản biện
Trường `note` (≤1000) và `voucher` đã có cho giao dịch ngân hàng từ spec 030, nhưng chỉ nhập được trong hộp phân loại; **lịch sử cũ (migrate)** không có note và **dòng lịch sử** chưa sửa được note tại chỗ. Spec này bù hai chỗ đó, không đổi dữ liệu nguồn.

## Tư vấn kế toán (Constitution VIII)
Nội dung ngân hàng (diễn giải gốc) là **bằng chứng, không sửa**; note là lớp diễn giải của chủ tài khoản, ghi **mục đích thực** để truy vết. Note không đổi số tiền, phân loại, báo cáo, snapshot; mọi lần sửa có lịch sử (thời điểm, trước, sau). Danh mục yêu cầu ghi chú (chi không chứng từ) không được để trống. Mục đích có thể liên quan thuế/chứng từ: cần kế toán viên xác nhận khi dùng note làm căn cứ hạch toán.

## User Scenarios & Testing
### User Story 1 - Bổ sung / sửa note ngay trên dòng lịch sử (P1)
Mỗi dòng giao dịch trong các lịch sử (danh mục, đối tượng, tài khoản, kiểm tra phân loại…) có nút "+ Ghi chú" (hoặc "Sửa ghi chú" nếu đã có) mở ô nhập ngay tại dòng; lưu thì dòng cập nhật tại chỗ, không cần đóng lịch sử; áp cho cả giao dịch ngân hàng và dòng lịch sử cũ.
1. **Given** dòng "chuyen tien a tuan uong ruou", **When** ghi "Tiền môi giới", **Then** dòng hiện ✎ Tiền môi giới, nội dung ngân hàng giữ nguyên.
2. **Given** giao dịch đã duyệt, **When** sửa note, **Then** lưu được không cần phiên điều chỉnh; snapshot không đổi.
3. **Given** danh mục yêu cầu ghi chú, **When** xóa note, **Then** bị chặn.

### User Story 2 - Nhập note từ cột khi migrate lịch sử cũ (P1)
Trong "Tùy chỉnh cột" có vai trò mới **Ghi chú**; cột chọn làm Ghi chú nhập thành note của từng dòng lịch sử cũ, hiện ở bản xem trước và ở mọi lịch sử; mặc định không chọn cột nào làm note.
1. **Given** cột G chọn "Ghi chú", **When** ghi, **Then** mỗi dòng có note từ ô tương ứng (≤1000 ký tự, bỏ trống thì không có note).

## Requirements
- **FR-001** (R174): vai trò cột `note` trong migrate; `legacy_entries[].note`; dòng lịch sử cũ trả `note` ở mọi lịch sử.
- **FR-002** (R175): `transaction-note` nhận cả mã dòng lịch sử cũ; ghi `note_history` trên dòng; vẫn tuân thủ danh mục yêu cầu ghi chú; không đổi số tiền, phân loại, snapshot, bản dán gốc.
- **FR-003** (R176): giao diện sửa note tại dòng ở mọi lịch sử có mã giao dịch; cập nhật tại chỗ.
- **FR-004**: không đụng dữ liệu thật ngoài thao tác của Thạch.
## Success Criteria
SC-001 ghi note cho một giao dịch ≤ 2 thao tác từ dòng lịch sử; SC-002 số tiền/phân loại/báo cáo/snapshot không đổi; SC-003 dữ liệu thật không đổi bởi phiên làm việc.
