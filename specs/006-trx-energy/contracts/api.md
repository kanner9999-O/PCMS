# Contracts — 006 trx-energy

Actions qua `POST /api/action` `{action, data}` (có CSRF token, request_id như hiện hành):
`trx-customer {name,note}` · `trx-order {customer,terms,evidence,lines[]}` · `trx-order-void {order,reason}` · `trx-receipt {customer,date,currency,received,rate?,bank_transaction?,evidence,allocations?[]}` · `trx-allocate {receipt,allocations[]}` · `trx-receipt-void {receipt,reason}` · `trx-reward {date,trx_amount,note}`.
Lỗi nghiệp vụ → `ValidationError` tiếng Việt (HTTP 400 như hiện hành).
`GET /api/state` thêm `trx` (dẫn xuất) và `capabilities` có `trx-energy`.
`POST /api/trx-report {date, period: week|month|quarter}` → `{start,end,period,received_usdt,by_type{ENERGY_ONCE,ENERGY_MONTHLY,TRX_SALE,UNALLOCATED},received_vnd,trx_sold,trx_rewards,entries[]}`.
UI: nút "TRX / Energy" ở sidebar; màn danh sách khách (còn nợ, chờ phân bổ), đơn/dòng, khoản thu, báo cáo; mọi nhãn tiền ghi rõ USDT/VND.
