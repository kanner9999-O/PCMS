# Feature Specification: Nguồn liền mạch theo số dư và mốc snapshot

**Feature Branch**: `022-source-continuity` · **Created**: 2026-10-14 · **Status**: Draft
**Input**: Thạch gặp lỗi "Nguồn mới làm lệch kỳ nguồn đã ghi" khi nạp file (46) chồng lên (44) và bổ sung 3 giao dịch cuối ngày 29/09. Thạch định hướng: chuỗi giao dịch liền mạch theo số dư là trọng tâm; mốc snapshot theo lần tải file + phân loại + chốt; chặn cả số dư lệch lẫn file không nối; tạo tài khoản từ file đầu tiên (R105–R110). Tham chiếu spec 001 (nguồn), 003, 009. Không đổi quy tắc tiền, không sửa giao dịch đã ghi, không đổi bản duyệt cũ.

## User Scenarios & Testing
### User Story 1 - Nạp file nối tiếp theo số dư, không quan tâm ngày (Priority: P1)
Thạch tải file (46) chứa lại các giao dịch đã có từ 15/08 rồi 3 giao dịch mới cuối ngày 29/09 và các giao dịch sau đó. Hệ thống nhận ra giao dịch cuối đã ghi (số dư 221.316.251), coi các dòng sau nó là giao dịch mới, kể cả cùng ngày 29/09, và cho ghi.

**Independent Test**: tài khoản đã ghi file A (đến giao dịch cuối, số dư S); file B chứa lại vài dòng của A, giao dịch cuối của A, rồi thêm 3 dòng cùng ngày giao dịch cuối và các dòng ngày sau → ghi được, thêm đúng các dòng mới, số dư cuối khớp file B; trước đây bị chặn.

**Acceptance Scenarios**:
1. **Given** file chứa giao dịch cuối đã ghi rồi các dòng mới, **When** kiểm tra, **Then** sẵn sàng ghi; dòng trùng liên kết nguồn, dòng sau là mới; không có lỗi "lệch kỳ nguồn".
2. **Given** file không chứa giao dịch cuối nhưng số dư đầu = số dư sau giao dịch cuối, **When** kiểm tra, **Then** sẵn sàng ghi toàn bộ dòng là mới.
3. **Given** file chỉ gồm giao dịch đã có, **When** kiểm tra, **Then** không có dòng mới, không lỗi.

### User Story 2 - Chặn khi không liền mạch (Priority: P1)
**Acceptance Scenarios**:
1. **Given** số dư đầu file khác số dư sau giao dịch cuối (và file không chồng lên dữ liệu), **When** kiểm tra, **Then** bị chặn kèm thông báo nêu giao dịch cuối, số dư kỳ vọng và số dư file.
2. **Given** file chồng lên dữ liệu nhưng có dòng mới nằm trước hoặc xen giữa các dòng đã có, hoặc phần chồng không kết thúc ở giao dịch cuối đã ghi mà vẫn có dòng mới, **When** kiểm tra, **Then** bị chặn "không nối liền mạch".
3. **Given** một dòng cùng mã tham chiếu nhưng khác nội dung/số tiền/số dư, **When** kiểm tra, **Then** bị chặn (giữ như cũ).
4. **Given** số dư cuối file khác số dư tính từ giao dịch cuối cộng các dòng mới, **When** kiểm tra, **Then** bị chặn.
5. **Given** tài khoản chưa có giao dịch, **When** số dư đầu file khác số dư đầu tài khoản, **Then** bị chặn.

### User Story 3 - Mốc snapshot ghi giao dịch cuối và số dư (Priority: P1)
Khi Thạch chốt mốc, bản chụp ghi giao dịch cuối (mã tham chiếu, ngày), số dư sau nó, số giao dịch đã và chưa phân loại. Màn tài khoản cho biết mốc gần nhất và bao nhiêu giao dịch nối tiếp sau mốc cần phân loại.

**Acceptance Scenarios**:
1. **Given** đã chốt mốc, **When** ghi file nối tiếp, **Then** màn hiện "n giao dịch nối tiếp sau mốc" và số chưa phân loại trong đó.
2. **Given** mốc cũ, **When** file mới được ghi, **Then** mốc cũ giữ nguyên số liệu; mốc mới nối tiếp mốc cũ.

### User Story 4 - Tạo tài khoản từ file sao kê đầu tiên (Priority: P2)
Thạch chọn file sao kê khi thêm tài khoản; hệ thống lấy số tài khoản, số dư đầu (số dư đầu của file), ngày bắt đầu (ngày đầu kỳ file) và nạp file chờ ghi.

**Acceptance Scenarios**:
1. **Given** file hợp lệ chưa có tài khoản cùng số, **When** tạo từ file, **Then** có tài khoản mới (tên do Thạch đặt, mặc định theo số tài khoản) và file ở trạng thái sẵn sàng ghi.
2. **Given** số tài khoản đã tồn tại hoặc file lỗi, **When** tạo, **Then** bị chặn và không tạo tài khoản dở dang.

### Edge Cases
- Tài khoản tạo tay: file đầu phải có số dư đầu bằng số dư đầu đã khai.
- Giao dịch cuối có nhiều dòng trùng thứ tự: dùng thứ tự ghi (giao dịch ghi sau cùng là giao dịch cuối).
- Dữ liệu cũ đã ghi theo kỳ: giữ nguyên; chuỗi số dư hiện có là điểm bắt đầu.

## Requirements
- **FR-001** (R107): kiểm tra file theo chuỗi số dư: xác định giao dịch cuối, phần chồng, các dòng mới; không dùng ngày để so kỳ.
- **FR-002** (R108): chặn khi số dư đầu không nối, khi dòng mới nằm trước/giữa phần chồng, khi phần chồng không kết thúc ở giao dịch cuối mà vẫn có dòng mới, khi số dư cuối không khớp, khi sổ cái khác số dư giao dịch cuối đã ghi.
- **FR-003**: bỏ cảnh báo khoảng ngày chưa có nguồn và yêu cầu xác nhận khoảng đó (`coverage_gaps` rỗng, không còn bắt xác nhận).
- **FR-004** (R106): bản chốt mốc ghi `milestone` (giao dịch cuối, ngày, mã, số dư, số giao dịch, số đã/chưa phân loại); `readiness` trả mốc gần nhất và số giao dịch nối tiếp sau mốc.
- **FR-005** (R109): hành động tạo tài khoản từ file (số tài khoản, số dư đầu, ngày bắt đầu từ file; tên; nạp file chờ ghi) trong một bước nguyên tử.
- **FR-006**: giao diện đổi chữ "duyệt" thành "chốt mốc" ở các nút/bước chính; hiện mốc và giao dịch nối tiếp; nút tạo tài khoản từ file.
- **FR-007**: không đổi giao dịch đã ghi, bản duyệt cũ, quy tắc tiền; dữ liệu thật không đổi cho tới khi Thạch tự thao tác.

## Success Criteria
- **SC-001**: kịch bản file 44 → 46 (mô phỏng bằng dữ liệu giả) ghi được đúng số dòng mới (gồm các dòng cùng ngày cuối) và số dư cuối khớp.
- **SC-002**: mọi kịch bản không liền mạch (số dư lệch, hở, xen giữa, chồng sai chỗ, số dư cuối sai) đều bị chặn với thông báo nêu rõ.
- **SC-003**: dữ liệu `outputs/p01-user-trial` không đổi (SHA256) trong kiểm thử.

## Assumptions
- Thứ tự ghi giao dịch trong tài khoản (`order`) là thứ tự chuỗi số dư; chỉ cho nối tiếp về phía sau.
- Backfill file cũ hơn mốc đầu tài khoản không còn được hỗ trợ (bị chặn vì không nối tiếp).
