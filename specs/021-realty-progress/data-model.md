# Data model 021
`realty.contracts[]`: `{id, property, price, date, reason, handover_date|null, status, created_at, void_reason?}` — giá hiện tại = ACTIVE có `(date, created_at)` lớn nhất.
`realty.installments[]`: `{id, property, label, due_date, amount, note, status ACTIVE|VOID, created_at, void_reason?}`
`realty.pay_links[]`: `{id, installment, transaction, status ACTIVE|UNLINKED, created_at, unlink_reason?}`; số tiền tính từ giao dịch hiện tại (tổng phần `investment` ra có `profile` = BĐS của đợt).
`view.realty.properties[].progress`: `{contract:{current,history}, handover_date, installments:[{id,label,due_date,amount,note,paid,remaining,status,overdue,overdue_days,over_paid,links:[{id,transaction,date,reference,description,amount,broken}]}], summary:{price,scheduled,paid,remaining,difference,overdue}, linkable:[{transaction,date,reference,description,amount}], today}`; `view.assets.commitments` = `{VND: tổng cam kết}`.
