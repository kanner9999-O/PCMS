# Contracts — 012 crypto-wallets
Actions `POST /api/action`: `crypto-place {name,kind,start_date?,note?}` · `crypto-place-archive {place,reason}` · `crypto-balance {place,ticker,network?,bucket,quantity,date,source}` · `crypto-balance-void {balance,reason}` · `crypto-price {ticker,network?,price,date,source}` · `crypto-price-void {price,reason}` · `crypto-capital {ticker,network?,amount,date,source}` · `crypto-capital-void {capital,reason}`.
`GET /api/state` → `crypto` và capability `crypto`. Lỗi → `ValidationError` tiếng Việt.
UI: nút "Crypto"; nhãn bắt buộc: giá "nhập tay", chênh lệch "chưa thực hiện, không phải lãi/lỗ", vị thế/nợ "hiển thị riêng, không cộng vào giá trị".
