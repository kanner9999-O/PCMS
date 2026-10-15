# Feature Specification: Hộp migrate chọn danh mục theo cấp

**Feature Branch**: `028-legacy-cascade` · **Created**: 2026-10-15 · **Status**: Draft
**Input**: Thạch: trong giao diện lịch sử cũ, danh mục phải load theo quan hệ cha → con, và đối tượng chỉ của danh mục đã chọn, không tải hết mọi danh mục/đối tượng (R135). Chỉ đổi giao diện hộp migrate (spec 027); không đổi dữ liệu hay backend.

## User Scenarios & Testing
### User Story 1 - Chọn danh mục theo cấp, đối tượng của danh mục đó (Priority: P1)
Hộp chỉ hiện danh sách danh mục gốc ở cấp đầu; chọn một gốc thì hiện tiếp ô danh mục con (nếu có), chọn con thì hiện tiếp cấp dưới (nếu có), dừng khi hết cấp hoặc khi chọn "dùng danh mục này". Ô đối tượng liệt kê **chỉ đối tượng của danh mục đang chọn** và lựa chọn "+ Đối tượng mới".

**Independent Test**: cây Gốc vay › Loans › Long debt (đối tượng Mỹ) và Đầu tư BĐS › Chung cư (A, B): chọn Gốc vay → ô con liệt kê Loans (và các con trực tiếp khác); chọn Loans → ô con Long debt; chọn Long debt → ô đối tượng chỉ gồm đối tượng của Long debt (không có A, B); đổi sang Chung cư → đối tượng chỉ A, B.

**Acceptance Scenarios**:
1. **Given** hộp vừa mở, **When** xem, **Then** chỉ có ô danh mục cấp 1 (các gốc hệ thống có đối tượng và gốc tự tạo); chưa chọn thì ô đối tượng bị khóa.
2. **Given** chọn một danh mục có con, **When** chọn, **Then** hiện thêm ô cấp dưới; đổi danh mục cấp trên thì các ô cấp dưới được dựng lại.
3. **Given** danh mục đã chọn, **When** mở ô đối tượng, **Then** chỉ gồm đối tượng của đúng danh mục đó; danh mục không có đối tượng thì chỉ có "+ Đối tượng mới".
4. **Given** đã chọn đối tượng mới bằng tên, **When** ghi, **Then** đối tượng được tạo và gán vào danh mục sâu nhất đã chọn.
5. **Given** đã xem trước, **When** đổi danh mục hoặc đối tượng, **Then** xem trước bị vô hiệu cho tới khi xem trước lại.
6. **Given** hộp mở, **When** có danh mục "Long debt", **Then** mặc định chọn sẵn đường dẫn tới nó (như trước).

## Requirements
- **FR-001** (R135): danh mục chọn theo cấp từ cây hiện có; cấp sau chỉ hiện con trực tiếp của cấp trước đang chọn; danh mục gửi đi là cấp sâu nhất đã chọn.
- **FR-002** (R135): ô đối tượng chỉ gồm đối tượng đang hoạt động của danh mục đã chọn, kèm "+ Đối tượng mới".
- **FR-003**: giữ nguyên xem trước, ghi, hủy, mọi quy tắc của spec 027; không đổi backend.

## Success Criteria
- **SC-001**: danh sách đối tượng trong hộp bằng đúng danh sách đối tượng của danh mục đã chọn ở mọi cấp (so với màn Danh mục).
- **SC-002**: 375px không tràn ngang; dữ liệu thật không đổi.

## Assumptions
- Cấp 1 gồm các gốc hệ thống nhận đối tượng (Thu nhập, Chi tiêu, Gốc vay, Lãi vay, Đầu tư BĐS) và các gốc tự tạo đang hoạt động.
