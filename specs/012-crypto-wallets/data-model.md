# Data Model — 012 crypto-wallets (`state['crypto']`)
| Thực thể | Trường |
|---|---|
| place | `id`, `name` (1–100, duy nhất casefold), `kind` WALLET\|EXCHANGE, `start_date` (ISO\|null), `note` (≤500), `status` ACTIVE\|ARCHIVED, `archive_reason`, `created_at` |
| balance | `id`, `place`, `ticker`, `network`, `bucket` ∈ HOLDING\|EARN_LOCKED\|MARGIN_COLLATERAL\|OPEN_POSITION\|MARGIN_DEBT (WALLET chỉ HOLDING), `quantity` (Decimal ≥0, ≤18 dp), `date` (≥ `start_date` nếu có), `source` (1–500), `status` ACTIVE\|VOID, `void_reason`, `created_at` |
| price | `id`, `ticker`, `network`, `price` (USDT >0, ≤12 dp), `date`, `source`, `status`, `void_reason`, `created_at` |
| capital | `id`, `ticker`, `network`, `amount` (USDT >0, ≤12 dp), `date`, `source`, `status`, `void_reason`, `created_at` |
`view['crypto']`: `{places[{…, components[], positions[], debts[], asset_value, weight, history[]}], coins[{key,ticker,network,quantity,price,value,weight,capital,gap}], totals{value,priced,unpriced[],denominator}, prices[], capitals[], buckets{…labels}, gap_label}`. Dẫn xuất, không lưu.
