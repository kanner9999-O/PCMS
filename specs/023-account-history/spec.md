# Feature Specification: Lịch sử sao kê theo mốc snapshot

**Feature Branch**: `023-account-history` · **Created**: 2026-10-14 · **Status**: Draft
**Input**: Thạch muốn xem trong giao diện tài khoản lịch sử sao kê tới mốc snapshot gần nhất, lấy được toàn bộ lịch sử có bộ lọc, dùng mốc làm tham chiếu để thấy file mới có liền mạch và đúng không, mặc định 10 giao dịch cuối của mốc (R111–R114). Tham chiếu spec 017 (dòng sao kê chuẩn), 022 (nguồn liền mạch, mốc). Chỉ đọc, không đổi dữ liệu.

## User Scenarios & Testing
### User Story 1 - Mốc gần nhất và 10 giao dịch cuối (Priority: P1)
Mở tài khoản, thấy khối "Lịch sử sao kê": mốc snapshot gần nhất (giao dịch cuối, ngày, số dư, thời điểm chốt) và **10 giao dịch cuối cùng tới mốc** theo dòng sao kê chuẩn (mới nhất trước), kèm tổng quan số giao dịch/số file.

**Independent Test**: tài khoản đã chốt mốc ở giao dịch R4 (4 giao dịch) → khối hiện mốc R4, đủ 4 dòng (ít hơn 10); tài khoản 25 giao dịch đến mốc → hiện 10 dòng cuối, nút xem thêm.

**Acceptance Scenarios**:
1. **Given** đã có mốc, **When** mở tài khoản, **Then** thấy mốc và 10 giao dịch cuối tới mốc, mỗi dòng có ngày + mã, nội dung + Xem nguồn, số tiền, số dư sau giao dịch, nhãn phân loại, file nguồn.
2. **Given** chưa có mốc, **When** mở, **Then** hiện "Chưa chốt mốc" và dùng giao dịch cuối đã ghi làm tham chiếu.
3. **Given** có giao dịch sau mốc (file nối tiếp đã ghi), **When** xem phạm vi mặc định, **Then** chúng không nằm trong 10 dòng của mốc nhưng được nhắc "n giao dịch nối tiếp sau mốc".

### User Story 2 - Danh sách file sao kê và toàn bộ lịch sử có lọc (Priority: P1)
Một hộp "Toàn bộ lịch sử sao kê" liệt kê mọi file đã ghi tới mốc (kỳ, số dòng, trạng thái, mới/trùng) và danh sách giao dịch từ ngày đầu theo dõi tới hiện tại (hoặc tới mốc) có phân trang và bộ lọc: khoảng ngày và chiều vào/ra (Thạch chọn hai bộ lọc này); kèm tổng vào/ra của kết quả lọc.

**Independent Test**: bộ lọc "chiều ra + khoảng ngày" chỉ trả đúng các dòng ra trong khoảng, tổng ra = Σ dòng.

**Acceptance Scenarios**:
1. **Given** phạm vi "tới mốc" hoặc "toàn bộ", **When** chuyển, **Then** toàn bộ giao dịch từ đầu theo dõi (kể cả sau mốc, đánh dấu "sau mốc") hiện được.
2. **Given** bộ lọc không hợp lệ (ngày sai, kết thúc trước bắt đầu, chiều lạ), **When** áp dụng, **Then** bị chặn kèm lý do.
3. **Given** danh sách dài, **When** cuộn, **Then** phân trang theo trang (mặc định 10 ở khối nhanh, 50 ở hộp đầy đủ).

### User Story 3 - File mới so với mốc: liền mạch và đúng đắn (Priority: P1)
Với mỗi file đang chờ ghi hoặc bị chặn, khối hiển thị tham chiếu (giao dịch cuối, số dư kỳ vọng) và kết quả: nối vào giao dịch cuối hoặc khớp số dư đầu, số dòng mới/trùng, số dư cuối có khớp, có xung đột/lỗi nào, kèm 10 giao dịch cuối của mốc làm đối chiếu.

**Independent Test**: file (46) giả lập chồng (44) → "Liền mạch: chứa lại giao dịch cuối R4; 3 dòng mới, 3 trùng; số dư cuối khớp"; file hở số dư → "Không liền mạch: số dư đầu … khác … " với lý do.

**Acceptance Scenarios**:
1. **Given** file nối tiếp hợp lệ, **When** xem, **Then** nhãn "Liền mạch và đúng" kèm cách nối (chứa lại giao dịch cuối / số dư đầu khớp).
2. **Given** file không liền mạch hoặc lỗi, **When** xem, **Then** nhãn "Không liền mạch/không đúng" kèm các lý do hiện có và số liệu so sánh.

### Edge Cases
- Tài khoản chưa có giao dịch: thông báo trống, hướng dẫn nhập file đầu.
- File bị loại khỏi đợt: liệt kê với trạng thái "đã loại", không tính vào lịch sử.
- Giao dịch có nhiều nguồn (file chồng): hiện file đầu tiên và số liên kết nguồn.

## Requirements
- **FR-001** (R111, R114): trả mốc gần nhất (hoặc giao dịch cuối nếu chưa chốt), danh sách file, và giao dịch tới mốc mới nhất trước, phân trang (mặc định 10).
- **FR-002** (R112): phạm vi `milestone` (tới mốc) và `all` (từ đầu theo dõi, giao dịch sau mốc đánh dấu); bộ lọc khoảng ngày và chiều tiền; trả tổng vào/ra và tổng số dòng của kết quả lọc.
- **FR-003** (R113): với mỗi file STAGED/BLOCKED trả cách nối (`CONTAINS_TAIL`/`OPENING_MATCH`/`NONE`), kết luận liền mạch + đúng, số dòng mới/trùng, số dư kỳ vọng/đầu/cuối file, số dư cuối khớp hay không, lý do.
- **FR-004**: chỉ đọc; không đổi dữ liệu, mốc, snapshot.
- **FR-005**: giao diện dùng dòng sao kê chuẩn (spec 017), hộp rộng cho toàn bộ lịch sử, 375px không tràn ngang.

## Success Criteria
- **SC-001**: mở tài khoản thấy mốc và đúng 10 (hoặc ít hơn nếu ít giao dịch) giao dịch cuối của mốc, không cần thao tác thêm.
- **SC-002**: mọi bộ lọc cho kết quả khớp tính tay (tổng vào/ra = Σ dòng; số dòng đúng); toàn bộ lịch sử bằng đúng số giao dịch đã ghi.
- **SC-003**: kết luận liền mạch/đúng đắn của file khớp quy tắc spec 022; dữ liệu thật không đổi.

## Assumptions
- Tham chiếu để nối file mới là giao dịch cuối đã ghi (trùng giao dịch mốc khi chưa có giao dịch sau mốc); hiển thị cả hai.
- Sắp mới nhất trước theo thứ tự ghi (thứ tự chuỗi số dư).
