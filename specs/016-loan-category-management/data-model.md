# Data model: 016

**Hồ sơ LOAN** (hiện có) thêm: `group`: id danh mục (`root=='principal'`) hoặc `null` (= Gốc vay); `group_history`: danh sách `{at, effective_date, from, to, reason}` (`from/to` là id hoặc `null`).

**`s['category_deleted']`**: danh sách `{id, name, path, root, reason, at}`.

**Danh mục node** (view): thêm `deletable` (bool), `loans` (số khoản vay đang gắn).

**`view().loan_options`**: danh sách `{id, party, party_name, name, date, gross, current, direction, setup(bool), group, group_path}`; `date` = ngày hiệu lực thiết lập hoặc ngày giao dịch gốc đầu tiên (hoặc `null`); `gross` = gốc đầu mốc + gốc phát sinh theo chiều của khoản kể từ mốc (hoặc `null` khi chưa thiết lập); `current` = dư gốc hiện tại (hoặc `null`).

**Quy tắc**: phần `principal` có `profile` là LOAN có `group` → danh mục hiệu lực = `group`; còn lại giữ `node` của phần. Các thao tác mới không đổi `allocations`, `classification_history`, snapshot.
