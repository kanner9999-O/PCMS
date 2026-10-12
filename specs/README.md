# specs/ — đặc tả theo tính năng (Spec Kit)

Migrate ngày 11/10/2026 từ bộ tài liệu cũ. **Nguồn yêu cầu vẫn là `PRODUCT-SPEC.md` (mã Rxx) và `ACCEPTANCE.md` (mã Axx/Pxx).** Mỗi spec ở đây tóm tắt một lát tính năng, trích mã Rxx, và là đơn vị đi qua `/speckit-specify → plan → tasks → implement`. Mâu thuẫn giữa `specs/` và hai file trên → cập nhật hai file trên trước.

| # | Spec | Tương ứng | Trạng thái | Nguồn yêu cầu |
|---|---|---|---|---|
| 001 | [bank-source-history](001-bank-source-history/spec.md) | P01–P03 | Implemented | R01–R06, R09, R10, R14, R17, R20, R21, R44–R46 |
| 002 | [debt-ledger](002-debt-ledger/spec.md) | P04 | Implemented | R07, R29, R30, R58 |
| 003 | [interest-statements](003-interest-statements/spec.md) | P05–P06 | Implemented | R21, R31, R42, R43 |
| 004 | [loan-completion-reporting](004-loan-completion-reporting/spec.md) | P07 | Implemented | R53 |
| 005 | [debt-journey-polish](005-debt-journey-polish/spec.md) | P08 (từ rà hành trình 11/10) | Implemented (đã phát hành) | R47, R53 |
| 006 | [trx-energy](006-trx-energy/spec.md) | P09 (F07 bản đầu) | Implemented (đã phát hành) | R33–R41, R48 |
| 007 | [assets-crypto-realestate](007-assets-crypto-realestate/spec.md) | F05 (BĐS bản đầu đã tách sang 011; còn chung cư tiến độ, crypto, tổng tài sản) | Draft (backlog) | R15, R18, R19, R23, R25–R27 |
| 008 | [category-management](008-category-management/spec.md) | P10 (R06, R55, R56, R58) | Implemented (đã phát hành) | R06, R45, R46, R50, R55, R56, R58 |
| 009 | [classification-ux](009-classification-ux/spec.md) | P11 (R67–R69, màn Phân loại) | Implemented (đã phát hành) | R45, R50, R55, R67–R69 |
| 010 | [expense-refund](010-expense-refund/spec.md) | P12 (R70, hoàn chi tiêu) | Implemented (đã phát hành) | R06, R50, R53, R56, R58, R70 |
| 011 | [realty](011-realty/spec.md) | P13 (R71–R73, Bất động sản bản đầu) | Implemented (đã phát hành) | R18, R27, R58, R71–R73 |
| 012 | [crypto-wallets](012-crypto-wallets/spec.md) | P14 (R74–R76, Crypto / ví bản đầu) | Implemented (đã phát hành) | R01, R15, R18, R19, R25, R26, R74–R76 |
| 013 | [asset-overview](013-asset-overview/spec.md) | P15 (R77–R80, Tổng hợp tài sản bản đầu) | Implemented (đã phát hành) | R09, R15, R18, R19, R42, R77–R80 |
| 014 | [category-completion](014-category-completion/spec.md) | P16 (R81–R83, hoàn thiện Danh mục) | Implemented (đã phát hành) | R46, R55, R56, R58, R81–R83 |
| 015 | [classification-review](015-classification-review/spec.md) | P17 (R84–R86, Kiểm tra phân loại) | Implemented (đã phát hành) | R46, R50, R58, R83, R84–R86 |
| 016 | [loan-category-management](016-loan-category-management/spec.md) | P18 (R87–R93, quản lý khoản vay và danh mục) | Implemented | R84–R93 |
| 017 | [history-format](017-history-format/spec.md) | P19 (R94, định dạng lịch sử chuẩn) | Implemented | R94 |
| 018 | [history-wide](018-history-wide/spec.md) | P20 (R95, lịch sử rộng một dòng) | Implemented | R94, R95 |

**Pending, không mở lại:** Shop (R08, R28, R32), cổ phiếu (R24), chốt tháng (R22).

## Ánh xạ tài liệu cũ → vị trí mới
- `PRODUCT-SPEC.md` §1 (P02–P07) → spec 001–004. §3 R01–R62 → cột "Nguồn yêu cầu" ở trên; file gốc giữ nguyên.
- `ACCEPTANCE.md` → tiêu chí của từng spec (ghi tại mục Success Criteria / Nguồn); mốc N0–N5 giữ ở file gốc.
- `IMPLEMENTATION-STATUS.md`, `outputs/pXX-handoff.md` → lịch sử/bằng chứng, giữ nguyên.
- `docs/archive/` → lịch sử, không phải yêu cầu.
- Quy tắc bất biến (HANDOFF §7) → `.specify/memory/constitution.md`.
