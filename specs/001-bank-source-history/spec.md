# Feature Specification: Lịch sử ngân hàng, nguồn và phân loại (P01–P03)

**Feature Branch**: `001-bank-source-history` (baseline, đã phát hành trên `main`)
**Created**: 2026-10-11 (migrate từ PRODUCT-SPEC §1 P01–P03, §3, §5 F01/F02/F06, §7.1)
**Status**: Implemented (P03, phát hành 10/10/2026)
**Nguồn yêu cầu**: R01–R06, R09, R10, R12, R14, R17, R20, R21, R44–R46, R58–R62 · Tiêu chí: ACCEPTANCE §0 (P01), P02, P03 · Bàn giao: `outputs/p01-implementation-handoff.md`, `p02-implementation-handoff.md`, `p02-1-source-recovery-handoff.md`, `p03-handoff.md`

> Spec baseline mô tả hành vi **đã có**, để các spec sau tham chiếu. Không thay `PRODUCT-SPEC.md` (nguồn yêu cầu) hay `ACCEPTANCE.md` (nguồn nghiệm thu).

## User Scenarios & Testing

### User Story 1 - Nhập sao kê và có lịch sử liên tục (Priority: P1)
Thạch tải sao kê XLSX (VND) của một tài khoản ngân hàng; hệ thống kiểm nguồn, phát hiện trùng/lệch số dư, ghi vào lịch sử liên tục từ ngày bắt đầu theo dõi tới nguồn mới nhất.

**Independent Test**: nạp hai file nối tiếp (100→115→112 triệu), nạp lặp không tăng dòng, file lệch bị chặn kèm lý do.

**Acceptance Scenarios**:
1. **Given** tài khoản có mốc theo dõi, **When** nạp file hợp lệ, **Then** số dư và kỳ nguồn cập nhật, file gốc không bị sửa.
2. **Given** file nạp lại cùng nội dung, **When** nạp, **Then** không tăng dòng và có đường xử lý rõ.
3. **Given** khoảng trước nguồn chưa kiểm chứng, **When** xem tổng quan, **Then** hiển thị khoảng thiếu, không suy "không có giao dịch".

### User Story 2 - Phân loại, tách khoản, chuyển nội bộ (Priority: P1)
Phân loại một hoặc nhiều giao dịch (checkbox), tách một giao dịch thành nhiều phần, ghép chuyển nội bộ; dòng chưa phân loại vẫn nằm trong báo cáo.

**Independent Test**: chọn cả trang/một phần/bỏ chọn; tổng phần tách = tiền nguồn; bộ lọc UI không cắt phạm vi báo cáo.

### User Story 3 - Duyệt, snapshot, điều chỉnh (Priority: P1)
Xem tóm tắt toàn đợt → duyệt (kể cả còn chưa phân loại, có nhãn) → snapshot bất biến; sai sót tạo phiên bản điều chỉnh có lý do, giữ bản cũ.

**Independent Test**: duyệt S1, tạo S2 có lý do, S1 giữ nguyên; duyệt lặp không đổi nội dung tài chính bị chặn; khoảng nguồn thiếu cần xác nhận riêng và lưu vào snapshot.

### User Story 4 - Quản lý tài khoản và khôi phục (Priority: P2)
Sửa tên/thông tin trước khi có lịch sử, xóa mềm tài khoản rỗng, lưu trữ tài khoản có lịch sử, khôi phục; backup/restore sang bộ dữ liệu riêng; đưa lại nguồn đã loại vào kiểm tra.

**Independent Test**: tạo sai → sửa → xóa → khôi phục → nhập → phân loại → duyệt → lưu trữ → khôi phục → reload, số dư và nguồn giữ đúng.

### Edge Cases
- Tài khoản đã duyệt không đổi → "Đã cập nhật / Nhập kỳ tiếp theo", không yêu cầu duyệt lặp.
- Nguồn bắt đầu sau mốc theo dõi → cảnh báo khoảng thiếu (ví dụ 09–31/07).
- Tài khoản lưu trữ không nhận nhập/phân loại/duyệt cho tới khi khôi phục (backend chặn).

## Requirements

### Functional Requirements
- **FR-001**: Hệ thống MUST ghi sao kê vào lịch sử liên tục theo từng tài khoản, nhập/phân loại bất kỳ lúc nào, không bắt buộc theo tháng (R04, R05, R14).
- **FR-002**: MUST kiểm nguồn, trùng, lệch số dư trước khi ghi và không sửa file gốc (R03, R04).
- **FR-003**: MUST cho phân loại/tách/chuyển nội bộ; chưa phân loại để mục riêng, vẫn được duyệt có nhãn (R06, R20).
- **FR-004**: Báo cáo duyệt MUST gồm toàn bộ giao dịch của tài khoản, độc lập bộ lọc; đối chiếu số mã giao dịch gốc, tiền vào/ra riêng (R46).
- **FR-005**: Snapshot MUST bất biến; điều chỉnh tạo phiên bản mới có lý do (R17, R21).
- **FR-006**: MUST nêu độ phủ nguồn: mốc theo dõi, kỳ đã ghi, khoảng thiếu, file chờ/chặn/đã loại, chưa phân loại; không coi thời gian sau nguồn cuối là đã đối soát (R05, R44).
- **FR-007**: VND giữ VND, USDT giữ USDT; không tự quy đổi (R09).
- **FR-008**: Người duyệt là Thạch; MUST NOT tự duyệt thay (R10).
- **FR-009**: Dữ liệu lưu dạng sự kiện kèm kiểm chứng; backup/restore tạo bộ dữ liệu riêng (R12, constitution I).

### Key Entities
Tài khoản · Đợt nhập (batch) · Giao dịch · Phân bổ phân loại · Snapshot/phiên bản duyệt · Sự kiện kiểm chứng.

## Success Criteria
- **SC-001**: Số dư chuỗi hai đợt khớp và reload giữ nguyên (đã kiểm P01/P02).
- **SC-002**: Tester độc lập 11/11 ca P02; PO kiểm chuỗi UI P02/P03 (xem IMPLEMENTATION-STATUS).

## Assumptions & Known limits
- Chỉ XLSX mẫu hỗ trợ, VND, local một người dùng. Chưa kiểm dữ liệu lớn hoặc mobile thật. Danh mục/đối tượng đầy đủ (R06, R58) chưa được chứng minh trọn vẹn. Sàn/ví crypto chưa có (xem spec 007).
