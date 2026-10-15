# Contracts 027
- `POST /api/legacy-preview` `{category, profile?, name?, text, mapping?}` → `{columns, mapping, rows:[{row,date,description,reference,amount,direction,bank_balance,status:'OK'|'MATCHED_BANK'|'DUPLICATE'|'ERROR', message?}], issues:[{row,message}], totals:{in,out}, declared:{in,out}|null, totals_ok, can_import, importable, matched_bank, duplicates}`
- `legacy-import` `{category, profile?, name?, text, mapping?, accept_total_mismatch?}` · `legacy-void` `{batch, reason}`
- `view.categories.legacy`: `[{id, at, category_path, profile_name, rows, active, matched_bank, totals, declared, status, void_reason}]`
