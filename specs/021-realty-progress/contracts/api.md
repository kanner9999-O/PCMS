# Contracts 021 (qua `POST /api/action`)
- `realty-contract` `{property, price, date, reason, handover_date?}` · `realty-contract-void` `{contract, reason}`
- `realty-installment` `{property, label, due_date, amount, note?}` · `realty-installment-void` `{installment, reason}` (chặn khi còn giao dịch gắn)
- `realty-pay-link` `{installment, transaction}` · `realty-pay-unlink` `{link, reason}`
Lỗi tiếng Việt: không phải BĐS, số không nguyên/≤0, ngày sai, thiếu tên/lý do, giao dịch không phải Đầu tư BĐS ra của BĐS này, đã gắn đợt khác, đợt đã hủy.
