---
description: "Task list — 012 crypto-wallets"
---

# Tasks: Crypto / ví bản đầu
**Input**: `/specs/012-crypto-wallets/` · **Tests**: có (`tests/test_p14_acceptance.py`) · Ràng buộc: Decimal, không đụng `outputs/p01-user-trial`, **chỉ `git add` đường dẫn cụ thể**, quy trình PR.

## Phase 1: Setup
- [X] T001 Baseline hồi quy vào `specs/012-crypto-wallets/baseline.txt` (unittest P01–P13 + `node --check` + `node tests/js/*.test.cjs`)
- [X] T002 SHA256 `outputs/p01-user-trial/**` vào `/tmp/pcms-012-data-before.sha256`

## Phase 2: Foundational
- [X] T003 Tạo `src/pcms/crypto_ledger.py`: mixin `CryptoLedger`, hằng `BUCKETS`/`ASSET_BUCKETS`/`WALLET_BUCKETS`, `crypto_state(s)` (setdefault `places/balances/prices/capitals`), helper `coin_key(ticker,network)`, chuẩn hóa ticker (`[A-Z0-9]{1,20}`) và mạng (≤30, in hoa), kiểm số thập phân (`quantity` ≤18 dp, `price`/`amount` ≤12 dp), hàm rỗng `change_crypto`, `crypto_view`; `p01.py`: mixin, dispatch `crypto-*`, `'crypto': self.crypto_view(s)`, capability `'crypto'`, build `P14-…`

## Phase 3: US1 — Nơi giữ và xác nhận số dư (P1) 🎯 MVP
- [X] T004 [US1] `change_crypto`: `crypto-place` (tên duy nhất casefold, `kind` WALLET|EXCHANGE, `start_date` ISO tùy chọn), `crypto-place-archive` (lý do bắt buộc), `crypto-balance` (nơi giữ ACTIVE, ví chỉ HOLDING, sàn đủ 5 trạng thái, số lượng ≥0, nguồn bắt buộc, ngày không trước `start_date`), `crypto-balance-void` (lý do bắt buộc)
- [X] T005 [US1] `crypto_view` phần nơi giữ: component hiện tại theo (nơi giữ, coin, trạng thái) = bản ACTIVE `(date, created_at)` mới nhất, `history` đủ cả bản hủy, `positions` (OPEN_POSITION) và `debts` (MARGIN_DEBT) riêng, coin định danh theo ticker+mạng (khác mạng tách riêng, hiển thị "chưa ghi mạng")
- [X] T006 [US1] Test `tests/test_p14_acceptance.py`: BTC 0,5 → 0,6 → hủy → quay về 0,5 và history 2 bản; số lượng 0 hợp lệ; thiếu nguồn/ngày xấu/số âm/>18 chữ số thập phân/ticker sai bị chặn; ví riêng chỉ HOLDING; sàn nhận 5 trạng thái; ngày trước mốc bị chặn; USDT TRC20 và ERC20 tách riêng, "chưa ghi mạng" tách khỏi có mạng; nơi giữ lưu trữ không nhận xác nhận mới và bị loại khỏi tổng; không seed/khóa trong view; đọc không ghi sự kiện
- [X] T007 [US1] UI `p01.html` (nút `Crypto`) và `p01.js`: `cryptoMode` (wrapper `render`, capture-click tắt khi chọn mục khác), `renderCrypto()` khung + từng nơi giữ (thành phần, lịch sử, nút Hủy kèm lý do), hộp thoại `+ Nơi giữ`, `+ Xác nhận số dư` (chọn nơi giữ, ticker, mạng, trạng thái theo loại nơi giữ, số lượng, ngày, nguồn), lưu trữ nơi giữ, ghi chú "không nhập seed phrase / private key"

## Phase 4: US2 — Tách trạng thái trên sàn (P1)
- [X] T008 [US2] `crypto_view`: `asset_value` chỉ từ HOLDING/EARN_LOCKED/MARGIN_COLLATERAL có giá; `positions` và `debts` không vào giá trị, không trừ; tổng nơi giữ = tổng thành phần tài sản (kèm `components_note`)
- [X] T009 [US2] Test: BingX BTC giữ 0,2 + ký quỹ 0,1 + vị thế 5 + nợ margin 0,05, giá 60.000 → `asset_value` = 18.000 (0,3 × 60.000), vị thế/nợ ở khu riêng và không ảnh hưởng giá trị; đổi vị thế/nợ không đổi `asset_value`
- [X] T010 [US2] UI: khu "Vị thế đang mở & nợ margin (hiển thị riêng, không cộng vào giá trị)" từng sàn; nhãn thành phần; ghi chú người dùng đảm bảo không chồng nhau

## Phase 5: US3 — Giá, giá trị USDT, tỷ trọng (P1)
- [X] T011 [US3] `crypto-price` (+ void): giá USDT >0 ≤12 dp, ngày, nguồn bắt buộc; `crypto_view`: giá hiện tại theo coin, `value = qty × price` làm tròn 6 dp half-up, `coins[]` gộp các nơi giữ hoạt động, `totals` (giá trị tổng, `unpriced[]`, `denominator` nêu mẫu số), `weight` 2 dp half-up theo nơi giữ và theo coin chỉ trên coin có giá
- [X] T012 [US3] Test: BTC 0,5 @ 60.000 và ETH 10 @ 2.500 → 30.000, 25.000, tổng 55.000, tỷ trọng 54,55 / 45,45; XYZ không giá → `unpriced`, không vào mẫu số; tỷ trọng theo nơi giữ đúng và cộng ≈100; giá mới thay cũ, hủy giá mới quay về; giá 0/âm/>12 dp/thiếu ngày/nguồn bị chặn; số lượng 18 chữ số thập phân giữ đúng
- [X] T013 [US3] UI: tổng quan giá trị USDT + bảng tỷ trọng theo nơi giữ và theo coin (chỉ coin có giá, nêu mẫu số), danh sách "chưa có giá", hộp thoại `+ Giá hiện tại` (coin chọn từ coin đã có hoặc nhập mới, giá, ngày, nguồn) hiển thị ngày giá, nhãn "nhập tay"

## Phase 6: US4 — Vốn và mốc theo dõi (P2)
- [X] T014 [US4] `crypto-capital` (+ void): USDT >0 ≤12 dp, ngày, nguồn bắt buộc; `crypto_view`: vốn hiện tại theo coin = bản ACTIVE mới nhất (không cộng dồn), `gap = value − capital` chỉ khi có cả hai kèm nhãn "chưa thực hiện, không phải lãi/lỗ", thiếu vốn → `capital=None`
- [X] T015 [US4] Test: BTC vốn 25.000 + giá trị 30.000 → gap +5.000 có nhãn; ETH chưa vốn → `capital=None`, `gap=None`; vốn mới thay vốn cũ (không cộng dồn), hủy quay về; coin không giá có vốn → không gap; view không chứa khóa `profit`/`loss`/`pnl`
- [X] T016 [US4] UI: hộp thoại `+ Vốn`; hiển thị vốn cạnh giá trị từng coin, "vốn chưa xác định", chênh lệch có nhãn

## Phase 7: Polish & nghiệm thu
- [X] T017 `node --check`, `node tests/js/*.test.cjs`, toàn bộ unittest P01–P14; so với baseline; test bất biến: dữ liệu ngân hàng/snapshot/công nợ/danh mục/BĐS không đổi khi dùng crypto
- [X] T018 PO dùng thử UI trên `/tmp/pcms-crypto-qa` (8801) theo `quickstart.md` §3; desktop và 375px; ghi lỗi, sửa, kiểm lại
- [X] T019 Đối chiếu SHA256 (T002) phải khớp
- [ ] T020 Viết `outputs/p14-handoff.md` (file phải tồn tại trước khi tick); cập nhật `IMPLEMENTATION-STATUS.md`, `HANDOFF.md`, `ACCEPTANCE.md` (P14), `specs/README.md` (hàng 012; 007 còn chung cư tiến độ, tổng tài sản) bằng `git update-index --cacheinfo`
- [ ] T021 Push nhánh, mở PR vào `main`, merge; `git fetch origin main:main`; restart 8792, kiểm chỉ đọc, đối chiếu checksum

## Dependencies
Phase 1 → 2 → US1 → US2 → US3 → US4 → Polish. Cùng sửa `crypto_ledger.py`/`p01.js`/`test_p14_acceptance.py` nên tuần tự. MVP = US1 + US3.
