# Data Model — 011 realty (`state['realty']`)
| Thực thể | Trường |
|---|---|
| valuation | `id`, `property` (PROPERTY profile), `value` (VND nguyên >0), `date` (ISO), `source` (1–500, bắt buộc), `note` (≤500), `status` ACTIVE\|VOID, `void_reason`, `created_at` |
| mortgage | `id`, `property`, `loan` (LOAN profile), `purpose` (1–500, bắt buộc), `note`, `status` ACTIVE\|ENDED, `end_reason`, `created_at` |
| contribution | `id`, `property`, `party` (PERSON profile), `amount` (VND nguyên >0), `date` (ISO, tùy chọn), `evidence` (1–500, bắt buộc), `note`, `status` ACTIVE\|VOID, `void_reason`, `created_at` |
Ràng buộc: tối đa một mortgage ACTIVE cho mỗi `loan`; không xóa bản ghi; `view['realty']` dẫn xuất (không lưu).
`view['realty'].properties[]`: `{id,name,capital:{paid,received,net,transactions},costs:{spent,refunded,net},valuation:{current,history[]},gap:{amount,label}|null,mortgages[],contributions:{items[],total},evidence}`; `view['realty'].unclassified`.
