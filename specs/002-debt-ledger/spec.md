# Feature Specification: Sổ công nợ truy được nguồn (P04)

**Feature Branch**: `002-debt-ledger` (baseline, đã phát hành trên `main`)
**Created**: 2026-10-11 (migrate từ PRODUCT-SPEC §1 P04, §5 F03)
**Status**: Implemented (P04, 10/10/2026)
**Nguồn yêu cầu**: R07, R29, R30, R47 (một phần), R58 · Bàn giao: `outputs/p04-handoff.md`, `outputs/p04-po-review.md`

## User Scenarios & Testing

### User Story 1 - Xem phải thu / phải trả theo người và từng khoản (Priority: P1)
Thạch tạo người và từng khoản vay/cho vay, thiết lập chiều, ngày bắt đầu và gốc đầu có căn cứ (kể cả xác nhận bằng 0); xem dư gốc từng khoản, không bù trừ hai chiều.

**Independent Test**: cho vay 100 triệu rồi thu gốc 40 triệu → dư 60 triệu; đi vay đảo chiều đúng; hồ sơ chưa thiết lập hiện "cần thiết lập", không mặc định dư nợ.

**Acceptance Scenarios**:
1. **Given** khoản cho vay, **When** phân bổ chi gốc, **Then** phải thu tăng; thu gốc → giảm.
2. **Given** khoản đi vay, **When** nhận gốc, **Then** phải trả tăng; trả gốc → giảm.
3. **Given** giao dịch trước mốc dư đầu, **When** tính, **Then** không cộng trùng.

### User Story 2 - Truy từ khoản tới dòng sao kê (Priority: P1)
Mở khoản → danh sách giao dịch cấu thành → dòng nguồn trong file sao kê.

**Independent Test**: truy dòng giao dịch đúng mã/nguồn; cảnh báo gốc âm hoặc dữ liệu thiếu.

### User Story 3 - Lãi thực nhận/thực trả hiện riêng (Priority: P2)
Lãi thu/chi đã phân bổ hiển thị riêng, không đổi gốc.

### Edge Cases
- Không tự phân bổ tiền theo thứ tự khoản vay (R30).
- Thiết lập/điều chỉnh có lịch sử; không viết lại snapshot đã duyệt.
- Sổ ở mức NHÁP: không phải xác nhận công nợ thực tế khi nguồn/phân loại còn thiếu.

## Requirements

### Functional Requirements
- **FR-001**: Mỗi lần vay MUST là khoản riêng; không gộp mất chi tiết (R30).
- **FR-002**: Dư gốc MUST = gốc đầu có căn cứ ± giao dịch đã phân bổ rõ vào đúng khoản/chiều.
- **FR-003**: MUST hỗ trợ cả hai chiều (mình vay / mình cho vay) và không bù trừ (R07).
- **FR-004**: Khoản thiếu thiết lập MUST hiện "cần thiết lập"; không đoán dư nợ.
- **FR-005**: MUST truy được từ khoản tới giao dịch và dòng nguồn (R58).
- **FR-006**: Số tiền dùng Decimal; không dùng float/Number (constitution III).

### Key Entities
Người (PERSON) · Khoản (LOAN: chiều, gốc đầu, ngày hiệu lực, căn cứ) · Phân bổ gốc/lãi · Lịch sử thiết lập.

## Success Criteria
- **SC-001**: 4 ca P04 + 4 ca P03 đạt; PO đối chiếu gốc/lãi/tổng hai chiều trên QA (IMPLEMENTATION-STATUS §P04).

## Assumptions & Known limits
- R47 (tổng nợ từng người + tổng quan) chưa đạt đầy đủ — được xử lý bởi spec 005. Chưa có quá hạn (cần hạn cam kết). Giới hạn VND.
