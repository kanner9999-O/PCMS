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
| 019 | [loan-interest-follows](019-loan-interest-follows/spec.md) | P21 (R96, lãi đi cùng khoản vay) | Implemented | R93, R96 |
| 020 | [crypto-movements](020-crypto-movements/spec.md) | P22 (R97–R100, mua/bán/chuyển crypto) | Implemented | R19, R74–R76, R97–R100 |
| 021 | [realty-progress](021-realty-progress/spec.md) | P23 (R101–R104, chung cư theo tiến độ) | Implemented | R71–R73, R101–R104 |
| 022 | [source-continuity](022-source-continuity/spec.md) | P24 (R105–R110, nguồn liền mạch theo số dư, mốc snapshot) | Implemented | R59, R105–R110 |
| 023 | [account-history](023-account-history/spec.md) | P25 (R111–R114, lịch sử sao kê theo mốc) | Implemented | R105–R114 |
| 024 | [import-preview](024-import-preview/spec.md) | P26 (R115–R117, xem trước giao dịch sẽ nhập) | Implemented | R105–R117 |
| 025 | [classify-objects](025-classify-objects/spec.md) | P27 (R118–R122, phân loại danh mục → con → đối tượng) | Implemented | R54–R58, R87–R93, R118–R122 |
| 026 | [category-objects](026-category-objects/spec.md) | P28 (R123–R128, danh mục có đối tượng riêng) | Implemented | R87–R93, R118–R128 |
| 027 | [legacy-import](027-legacy-import/spec.md) | P29 (R129–R134, migrate lịch sử cũ từ Excel) | Implemented | R123–R134 |
| 028 | [legacy-cascade](028-legacy-cascade/spec.md) | P30 (R135–R136, chọn danh mục theo cấp; quyết định cấu trúc) | Implemented | R123–R136 |
| 029 | [object-unique](029-object-unique/spec.md) | P31 (R138–R140, tên đối tượng duy nhất, gộp trùng) | Implemented | R125, R138–R140 |
| 030 | [note-capitalized-costs](030-note-capitalized-costs/spec.md) | P32 (R141–R145, ghi chú, vốn hóa chi phí mua BĐS, chi không chứng từ) | Implemented | R71–R73, R141–R145 |
| 031 | [loan-business-objects](031-loan-business-objects/spec.md) | P33 (R146–R153, nghiệp vụ gắn đối tượng trong danh mục, Cho vay trước) | Implemented | R84–R86, R136–R145, R146–R153 |
| 032 | [default-group](032-default-group/spec.md) | P34 (R154–R157, nhóm mặc định cho danh mục, phương án A) | Implemented | R136, R146–R157 |
| 033 | [object-management](033-object-management/spec.md) | P35 (R158–R163, màn quản lý đối tượng) | Implemented | R136, R158–R163 |
| 034 | [category-cleanup](034-category-cleanup/spec.md) | P36 (R164–R165, dọn danh mục con chưa dùng) | Implemented | R136, R164–R165 |
| 035 | [object-suggest](035-object-suggest/spec.md) | P37 (R166–R168, thêm đối tượng theo loại, gợi ý tìm kiếm) | Implemented | R136, R166–R168 |
| 036 | [classify-cascade](036-classify-cascade/spec.md) | P38 (R169–R171, phân loại theo cây danh mục cha con) | Implemented | R84–R86, R136, R169–R171 |
| 037 | [legacy-shortcut](037-legacy-shortcut/spec.md) | P39 (R172–R173, migrate lịch sử cũ từ đối tượng của danh mục, chống ghi nhầm) | Implemented | R84–R86, R136, R172–R173 |
| 038 | [transaction-note-inline](038-transaction-note-inline/spec.md) | P40 (R174–R176, ghi chú sửa tại dòng lịch sử, cột Ghi chú khi migrate) | Implemented | R141–R145, R174–R176 |

**Pending, không mở lại:** Shop (R08, R28, R32), cổ phiếu (R24), chốt tháng (R22).

## Ánh xạ tài liệu cũ → vị trí mới
- `PRODUCT-SPEC.md` §1 (P02–P07) → spec 001–004. §3 R01–R62 → cột "Nguồn yêu cầu" ở trên; file gốc giữ nguyên.
- `ACCEPTANCE.md` → tiêu chí của từng spec (ghi tại mục Success Criteria / Nguồn); mốc N0–N5 giữ ở file gốc.
- `IMPLEMENTATION-STATUS.md`, `outputs/pXX-handoff.md` → lịch sử/bằng chứng, giữ nguyên.
- `docs/archive/` → lịch sử, không phải yêu cầu.
- Quy tắc bất biến (HANDOFF §7) → `.specify/memory/constitution.md`.
