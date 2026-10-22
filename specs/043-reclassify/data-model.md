# Data model — 043
Không thêm trường cho giao dịch ngân hàng: dùng `classification_history` hiện có (`at, before, after, reason`) + nhật ký sự kiện (`audit.actor`). Thêm `reclassify` vào bản ghi lịch sử: `{part, level, token}`.
Dòng lịch sử cũ: `legacy_entries[].classification_history[] = {at, before:{category,profile}, after:{category,profile}, reason}`; `category`, `profile` của dòng đổi; bản dán gốc (`legacy_batches.source_text`) không đổi.
Xem trước (không lưu): `{source, parts_before, parts_after, part, moved, level, blocks[], needs_membership, effects{categories[],objects[]}, business{loans[],properties[]}, invariants{source_unchanged}, needs_adjustment, token}`.
