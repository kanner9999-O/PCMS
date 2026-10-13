# Contracts 020 (qua `POST /api/action`)
- `crypto-trade` `{kind:'BUY'|'SELL', place, ticker, network?, quantity, price, date, source, fee?, fee_ticker?, quote_ticker?, quote_network?}`
- `crypto-transfer` `{from_place, to_place, ticker, network?, quantity, received, date, source}`
- `crypto-movement-void` `{movement, reason}`
Lỗi (thông báo tiếng Việt): nơi giữ lưu trữ/không có, ngày trước mốc theo dõi, số không hợp lệ, mua/bán coin cùng đồng định giá, phí khác coin/đồng định giá, cùng nơi giữ khi chuyển, số nhận > số gửi, thiếu nguồn/ngày, hủy bản đã hủy.
