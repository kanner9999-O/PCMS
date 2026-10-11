# specs/ — đặc tả theo tính năng (Spec Kit)

Migrate ngày 11/10/2026 từ bộ tài liệu cũ. **Nguồn yêu cầu vẫn là `PRODUCT-SPEC.md` (mã Rxx) và `ACCEPTANCE.md` (mã Axx/Pxx).** Mỗi spec ở đây tóm tắt một lát tính năng, trích mã Rxx, và là đơn vị đi qua `/speckit-specify → plan → tasks → implement`. Mâu thuẫn giữa `specs/` và hai file trên → cập nhật hai file trên trước.

| # | Spec | Tương ứng | Trạng thái | Nguồn yêu cầu |
|---|---|---|---|---|
| 001 | [bank-source-history](001-bank-source-history/spec.md) | P01–P03 | Implemented | R01–R06, R09, R10, R14, R17, R20, R21, R44–R46 |
| 002 | [debt-ledger](002-debt-ledger/spec.md) | P04 | Implemented | R07, R29, R30, R58 |
| 003 | [interest-statements](003-interest-statements/spec.md) | P05–P06 | Implemented | R21, R31, R42, R43 |
| 004 | [loan-completion-reporting](004-loan-completion-reporting/spec.md) | P07 | Implemented | R53 |
| 005 | [debt-journey-polish](005-debt-journey-polish/spec.md) | P08 (từ rà hành trình 11/10) | Implemented (chờ restart 8792) | R47, R53 |
| 006 | [trx-energy](006-trx-energy/spec.md) | F07 | Draft (backlog) | R33–R41, R48 |
| 007 | [assets-crypto-realestate](007-assets-crypto-realestate/spec.md) | F05, BĐS | Draft (backlog) | R15, R18, R19, R23, R25–R27 |

**Pending, không mở lại:** Shop (R08, R28, R32), cổ phiếu (R24), chốt tháng (R22).

## Ánh xạ tài liệu cũ → vị trí mới
- `PRODUCT-SPEC.md` §1 (P02–P07) → spec 001–004. §3 R01–R62 → cột "Nguồn yêu cầu" ở trên; file gốc giữ nguyên.
- `ACCEPTANCE.md` → tiêu chí của từng spec (ghi tại mục Success Criteria / Nguồn); mốc N0–N5 giữ ở file gốc.
- `IMPLEMENTATION-STATUS.md`, `outputs/pXX-handoff.md` → lịch sử/bằng chứng, giữ nguyên.
- `docs/archive/` → lịch sử, không phải yêu cầu.
- Quy tắc bất biến (HANDOFF §7) → `.specify/memory/constitution.md`.
