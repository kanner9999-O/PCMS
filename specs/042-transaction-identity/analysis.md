# Phân tích chéo (thủ công, không chạy `/speckit-analyze`) — cập nhật 22/10/2026

| Yêu cầu | Task | Bằng chứng |
|---|---|---|
| R191 / A58 | T02 | `test_ket_case_reproduced…`, `test_resolution_add_membership…`, `test_resolution_reclassify_preview_equals_result…`, `test_correction_guards…`, `test_approved_row_needs_adjustment…`; `assert_screens_consistent` (tổng Danh mục = tổng lịch sử từng đối tượng/danh mục) |
| R192 / A59 bank | T03 | `test_bank_reimport_same_file…`, `test_same_reference_in_another_account…`, `test_bank_import_conflicting_with_scoped_legacy…` |
| R192–R193 / A59 lịch sử | T04 | `test_legacy_scoped_duplicates…`, `test_old_batch_without_account…`, `test_resolution_blocked_when_it_would_move_money…`, P29 `test_bank_duplicates_and_repeat_paste_and_late_statement` (viết lại theo hợp đồng mới) |
| R194 | T04–T06 | snapshot/bản dán gốc không đổi trong test; giới hạn sàn ghi ở review.md |

Phát hiện khi rà bản nháp (đã xử lý): (1) gợi ý điều chỉnh có thể chuyển **lãi sang gốc** → chỉ cho cùng loại gốc; (2) mọi khoản lãi ở Lãi vay hiện là sai lệch → thêm lối "thêm đối tượng vào danh mục" thay vì chuyển tiền; (3) xem trước xác định tài khoản không mô phỏng đúng thứ tự xử lý, có thể ngầm chuyển tiền giữa lần migrate → mô phỏng chính xác và chặn; (4) dòng trùng sao kê bị bỏ khỏi chứng từ → lưu lại, không cộng tiền; (5) bỏ cắt hậu tố có thể cộng hai lần → gần trùng phải đối chiếu; (6) mã chết trong `check_batch`. Không còn yêu cầu không có task.
