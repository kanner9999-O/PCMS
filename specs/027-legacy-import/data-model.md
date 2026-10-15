# Data model 027
`legacy_batches[]`: `{id, at, source_text, sha256, category (id danh mục hoặc khóa gốc), profile, mapping, rows, totals{in,out}, declared{in,out}|null, accepted_mismatch, status ACTIVE|VOID, void_reason?, voided_at?}`
`legacy_entries[]`: `{id, batch, row, date, description, reference, amount, direction IN|OUT, bank_balance|null, category, profile}`
Tổng/lịch sử: mỗi dòng sinh một "giao dịch giả" (account=None, signed_amount, allocations 1 phần gắn danh mục và đối tượng, `legacy=True`) trong `cat_parts` trừ khi lần migrate đã hủy hoặc mã (chuẩn hóa) trùng một giao dịch sao kê.
