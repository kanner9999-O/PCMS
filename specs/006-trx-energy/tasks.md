---
description: "Task list — 006 trx-energy (bản đầu)"
---

# Tasks: TRX/Energy bản đầu
**Input**: `/specs/006-trx-energy/` · **Tests**: có (`tests/test_p09_acceptance.py`) · Ràng buộc: Decimal, không đụng `outputs/p01-user-trial`, gate UI theo capability `trx-energy`.

## Phase 1: Setup
- [X] T001 Ghi baseline hồi quy vào `specs/006-trx-energy/baseline.txt` (`unittest` P01–P08 + `node --check`)
- [X] T002 Lưu SHA256 `outputs/p01-user-trial/**` vào `/tmp/pcms-006-data-before.sha256`

## Phase 2: Foundational
- [X] T003 Tạo `src/pcms/trx_energy.py`: mixin `TrxEnergy` với `change_trx(s,action,d)` (dispatch 7 action ở `contracts/api.md`), helper `trx_state(s)` = `s.setdefault('trx',{customers:[],orders:[],receipts:[],rewards:[]})`, `usdt(x)` làm tròn half-up 6 dp
- [X] T004 Trong `src/pcms/p01.py`: thêm `TrxEnergy` vào bases của `P01Store`, dispatch `trx-*` trong `change()`, thêm `trx` và `'trx-energy'` vào `view()`/capabilities, `build` `P09-…`

## Phase 3: US1 — Khách, đơn, công nợ (P1) 🎯 MVP
- [X] T005 [US1] `trx-customer` (tên duy nhất không phân biệt hoa thường, ≤100) và `trx-order` (kiểm lines theo `data-model.md`: type, amount_usdt>0, quantity>0, ENERGY_MONTHLY cần plan+service_start/end, terms PREPAID|POSTPAID, due_date ISO hoặc null, evidence bắt buộc) trong `trx_energy.py`
- [X] T006 [US1] `trx_view(s)` trong `trx_energy.py`: theo khách/dòng/tổng (billed, allocated, outstanding, unallocated, status dòng, overdue chỉ khi có due_date và hôm nay giờ VN > hạn và còn nợ)
- [X] T007 [P] [US1] Test trong `tests/test_p09_acceptance.py`: ba kỳ × 100 USDT → billed 300; khách trùng tên bị chặn; dòng thiếu service_end bị chặn; không có hạn → overdue false

## Phase 4: US2 — Khoản thu, phân bổ, VND quy đổi (P1)
- [X] T008 [US2] `trx-receipt` (USDT hoặc VND+rate, evidence, allocations tùy chọn, ràng buộc R2/R3/R4 ở research), `trx-allocate` (append-only), `trx-receipt-void`, `trx-order-void` (không void khi còn phân bổ hiệu lực) trong `trx_energy.py`
- [X] T009 [P] [US2] Test: thu 200 phân bổ 2 dòng → outstanding 100; thu VND 25.000.000 @25.000 = 1.000 USDT; đổi tỷ giá lần sau không đổi lần trước; vượt phân bổ bị chặn; gắn bank_transaction lần hai quá số tiền bị chặn; void khoản thu hoàn số liệu và giải phóng giao dịch ngân hàng; state ngân hàng/giao dịch không đổi

## Phase 5: US3 — Báo cáo thực thu và thưởng (P2)
- [X] T010 [US3] `trx-reward` và `trx_report(d,s)` (tuần Hai–CN/tháng/quý theo ngày nhận; by_type, received_vnd, trx_sold, trx_rewards, entries) trong `trx_energy.py`; thêm route `/api/trx-report` trong `src/pcms/server.py`
- [X] T011 [P] [US3] Test báo cáo: tổng theo kỳ, tách loại, VND riêng, không có khóa lãi/lỗ, void loại khỏi báo cáo

## Phase 6: UI (US1–US3)
- [X] T012 Thêm nút `TRX / Energy` vào `src/pcms/web/p01.html` (sidebar) và `trxMode` trong `src/pcms/web/p01.js` (wrapper `render`, capture-click đặt `trxMode=false` khi chọn tài khoản/Công nợ/Hồ sơ)
- [X] T013 `renderTrx()` trong `p01.js`: tổng quan (billed/đã phân bổ/còn nợ/chờ phân bổ, USDT), danh sách khách → đơn → dòng (trạng thái chip, hạn, quá hạn nếu có), nút + khách / + đơn / + khoản thu / + thưởng / Báo cáo; dùng `fmt`, `esc`, `modal`, `act`, `field`; không cộng tiền bằng `Number`
- [X] T014 Hộp thoại đơn (nhiều dòng), khoản thu (USDT|VND, tỷ giá, giao dịch ngân hàng chọn từ danh sách giao dịch tiền vào chưa dùng hết, phân bổ), phân bổ bổ sung, void kèm lý do, báo cáo kỳ (mặc định kỳ chứa ngày nhận gần nhất như 005)

## Phase 7: Polish & nghiệm thu
- [X] T015 `node --check src/pcms/web/p01.js`; chạy toàn bộ `unittest` P01–P09; so với baseline
- [X] T016 PO dùng thử UI theo `quickstart.md` §3 trên `/tmp/pcms-trx-qa` cổng 8801 (desktop + mobile 375px không tràn ngang)
- [X] T017 Đối chiếu SHA256 dữ liệu vận hành (T002) — phải khớp
- [X] T018 Viết `outputs/p09-handoff.md`; cập nhật `IMPLEMENTATION-STATUS.md`, `HANDOFF.md`, `README.md`, `ACCEPTANCE.md` (P09), `specs/README.md` (006 Implemented)
- [X] T019 Restart 8792, kiểm chỉ đọc, đối chiếu checksum, commit/merge `main`/push

## Dependencies
Phase 1 → 2 → US1 → US2 → US3 → UI → Polish. Cùng sửa `trx_energy.py` và `p01.js` nên tuần tự; test [P] khác file nhưng cùng `test_p09_acceptance.py` → tuần tự trong thực tế. MVP = US1+US2.
