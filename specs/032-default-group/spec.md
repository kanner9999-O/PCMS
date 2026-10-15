# Feature Specification: Nhóm mặc định cho danh mục

**Feature Branch**: `032-default-group` · **Created**: 2026-10-15 · **Status**: Draft
**Input**: Thạch (15/10/2026): thêm "nhóm mặc định" cho danh mục — chỉ tổng hợp tiền vào/ra, không gắn vai trò hay nghiệp vụ, vẫn đưa vào báo cáo; mọi danh mục hiện có thuộc nhóm này; nghiệp vụ gắn cho đối tượng ở mọi danh mục. Chọn **phương án A**: nhóm là nhãn tổ chức, không đổi phân loại gốc của giao dịch, báo cáo, snapshot. Sửa lệch của spec 031 (nghiệp vụ buộc theo loại gốc). Tham chiếu spec 026, 031; Constitution VII, VIII; R136, R146–R153.

## Tư vấn kế toán (Constitution VIII)
- **Phương án A (khuyến nghị)**: nhóm mặc định là lớp tổ chức/tổng hợp dòng tiền; **không sửa phân loại gốc** của giao dịch đã ghi (lịch sử bất biến) nên báo cáo và snapshot đã duyệt không đổi.
- **Rủi ro cần hiển thị, không chặn**: danh mục có loại ghi nhận Chi tiêu/Thu nhập vẫn được cộng vào báo cáo Chi tiêu/Thu nhập. Cho vay hoặc mua BĐS đặt trong đó làm chi tiêu/thu nhập trên báo cáo lệch bản chất (cho vay là tăng phải thu, mua BĐS là tăng tài sản). Hệ thống cảnh báo rõ ở cặp nghiệp vụ; tách khỏi báo cáo chi tiêu (phương án B) là bước riêng, cần xem trước chênh lệch và xác nhận của Thạch.
- Các chặn mâu thuẫn thật vẫn giữ (chiều khoản vay, loại hồ sơ, đổi loại khi đã có giao dịch).
- Cần kế toán viên xác nhận khi chuyển sang phương án B (báo cáo kỳ cũ).

## User Scenarios & Testing
### User Story 1 - Mọi danh mục thuộc nhóm mặc định (Priority: P1)
Mỗi danh mục (gốc hệ thống và do người dùng tạo) mang nhóm "Mặc định": chỉ tổng hợp tiền vào/ra và đưa vào báo cáo. Danh mục tạo mới tự thuộc nhóm này. Danh mục hiện có được xem là nhóm mặc định mà không sửa giao dịch hay snapshot.

**Acceptance Scenarios**:
1. **Given** dữ liệu cũ, **When** mở màn Danh mục, **Then** mọi danh mục hiện nhóm "Mặc định" và tổng tiền không đổi.
2. **Given** tạo danh mục mới, **Then** nhóm là Mặc định.
3. **Given** báo cáo/snapshot cũ, **Then** không đổi.

### User Story 2 - Nghiệp vụ gắn đối tượng ở mọi danh mục (Priority: P1)
Đối tượng trong danh mục bất kỳ (kể cả Long Debt, Property thuộc Nhóm chi) gắn được Cho vay/Đi vay/BĐS; bỏ chặn theo loại gốc.

**Acceptance Scenarios**:
1. **Given** Mỹ trong danh mục loại chi, **When** gắn Cho vay, **Then** lưu được và sổ cho vay chạy.
2. **Given** khoản vay thiết lập Phải thu, **When** gắn Đi vay, **Then** vẫn bị chặn.
3. **Given** cặp nghiệp vụ nằm trong danh mục có loại ghi nhận Chi tiêu/Thu nhập, **Then** hiện cảnh báo "đang tính vào Chi tiêu/Thu nhập".

## Requirements
- **FR-001** (R154): mỗi danh mục có `group` = `default` ("Nhóm mặc định", chỉ tổng hợp tiền vào/ra, chưa gắn nghiệp vụ); thiếu trường = mặc định; danh mục mới tự đặt mặc định; hiển thị ở màn Danh mục và `view`.
- **FR-002** (R155): nhóm không đổi phân loại gốc, báo cáo, snapshot, tổng danh mục.
- **FR-003** (R156): `business-set` không chặn theo loại gốc; giữ chặn loại hồ sơ/chiều/đổi loại khi có giao dịch.
- **FR-004** (R157): cảnh báo `IN_EXPENSE_REPORT` / `IN_INCOME_REPORT` cho cặp nghiệp vụ nằm trong danh mục loại Chi tiêu/Thu nhập (không chặn).
- **FR-005**: không đổi quy tắc tiền; không đụng dữ liệu thật.

## Success Criteria
- **SC-001**: Mọi danh mục hiện có hiển thị nhóm mặc định; tổng tiền các danh mục không đổi.
- **SC-002**: Mỹ trong danh mục Nhóm chi gắn Cho vay được và có cảnh báo.
- **SC-003**: Dữ liệu thật `outputs/p01-user-trial` không đổi.
