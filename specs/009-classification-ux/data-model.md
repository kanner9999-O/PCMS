# Data Model — 009 classification-ux
Không đổi schema. Dùng lại `profiles` (`PERSON|LOAN|PROPERTY`, `party`) và `categories` (spec 008).
- `classification_history[].reason`: chuỗi, có thể rỗng (≤500).
- `account.adjustment_reason`: chuỗi, có thể rỗng khi mở phiên điều chỉnh (≤500).
- Action `object-quick-create`: LOAN → thêm tối đa 2 `profiles` (PERSON mới nếu có `party_name`; LOAN); PROPERTY → 1 `profile`; CATEGORY → 1 nút `categories`. Audit `object-quick-create` kèm chi tiết. Bất biến: không đổi `transactions`, `allocations`, `snapshots`, `debt_setup`.
