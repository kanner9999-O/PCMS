# Data model 020
`crypto.movements[]`: `{id, kind: BUY|SELL|TRANSFER, status: ACTIVE|VOID, date, source, created_at, void_reason?, voided_at?}`
- BUY/SELL: `place, ticker, network, quantity, price, quote_ticker (mặc định USDT), quote_network (mặc định ""), quote = quantity×price làm tròn 6 chữ số (half-up), fee ("0" mặc định), fee_ticker (ticker coin hoặc quote_ticker)`
- TRANSFER: `from_place, to_place, ticker, network, quantity (gửi), received (nhận ≤ gửi)`

Số lượng sổ cái (HOLDING) = số mốc `crypto.balances` ACTIVE mới nhất + Σ delta(giao dịch ACTIVE, ngày > ngày mốc). Delta: BUY coin +quantity (− phí nếu bằng coin), quote −quote (− phí nếu bằng quote); SELL coin −quantity (− phí nếu bằng coin), quote +quote (− phí nếu bằng quote); TRANSFER nơi gửi −quantity, nơi nhận +received.

`view.crypto` thêm: `movements` (mới nhất trước), `ledger_warnings` `[{place, coin, code: NO_BASE|NEGATIVE}]`; mỗi `components[]` HOLDING thêm `confirmed_quantity`, `ledger_moves`, `warnings`; mỗi nơi giữ thêm `reconciliations` `[{ticker, network, date, expected, confirmed, difference}]`.
