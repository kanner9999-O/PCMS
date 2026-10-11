# Data Model — 006 trx-energy (state['trx'])

| Thực thể | Trường (ràng buộc) |
|---|---|
| customer | `id`, `name` (bắt buộc, ≤100, duy nhất không phân biệt hoa thường), `note` (≤500), `created_at`, `status` ACTIVE |
| order | `id`, `customer`, `terms` `{mode: PREPAID\|POSTPAID, due_date: ISO\|null}`, `evidence` (≤500, bắt buộc), `lines[]`, `status` ACTIVE\|VOID, `void_reason`, `created_at` |
| line | `id`, `type` ENERGY_ONCE\|ENERGY_MONTHLY\|TRX_SALE, `amount_usdt` (>0, 6 dp), `quantity` (>0; ENERGY: lượng Energy, TRX_SALE: số TRX), `service_start`/`service_end` (ISO, bắt buộc cho ENERGY_MONTHLY, end ≥ start), `plan` (tên gói, ≤100, ENERGY_MONTHLY), `note` |
| receipt | `id`, `customer`, `date` (ISO), `currency` USDT\|VND, `received` (>0), `rate` (VND/USDT, bắt buộc >0 nếu VND), `usdt_equivalent`, `bank_transaction`\|null, `evidence` (≤500, bắt buộc), `allocations[{line, amount_usdt, at}]`, `status` ACTIVE\|VOID, `void_reason` |
| reward | `id`, `date`, `trx_amount` (>0), `note`, `status` ACTIVE\|VOID |

Dẫn xuất (`view['trx']`): theo khách `billed`, `allocated`, `outstanding`, `unallocated`, `overdue` (chỉ khi có hạn); theo dòng `paid`, `outstanding`, `status` UNPAID\|PARTIAL\|PAID; tổng `billed/allocated/outstanding/unallocated`; `trx_sold_quantity`, `reward_quantity`.
Bất biến: `Σ allocations ≤ usdt_equivalent` mỗi khoản thu; `Σ allocations vào dòng ≤ amount_usdt`; outstanding = billed − allocated ≥ 0.
