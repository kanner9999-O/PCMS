# Phân tích chéo (thủ công, không chạy `/speckit-analyze`) — cập nhật 22/10/2026

| Yêu cầu | Task | Bằng chứng |
|---|---|---|
| R191 / A58 | T02 | `test_ket_case_reproduced…`, `test_resolution_add_membership…`, `test_resolution_reclassify_preview_equals_result…`, `test_correction_guards…`, `test_approved_row_needs_adjustment…`; `assert_screens_consistent` (tổng Danh mục = tổng lịch sử từng đối tượng/danh mục) |
| R192 / A59 bank | T03 | `test_bank_reimport_same_file…`, `test_same_reference_in_another_account…`, `test_bank_import_conflicting_with_scoped_legacy…` |
| R192–R193 / A59 lịch sử | T04 | `test_legacy_scoped_duplicates…`, `test_old_batch_without_account…`, `test_resolution_blocked_when_it_would_move_money…`, P29 `test_bank_duplicates_and_repeat_paste_and_late_statement` (viết lại theo hợp đồng mới) |
| R194 | T04–T06 | snapshot/bản dán gốc không đổi trong test; giới hạn sàn ghi ở review.md |

Phát hiện khi rà bản nháp (đã xử lý): (1) gợi ý điều chỉnh có thể chuyển **lãi sang gốc** → chỉ cho cùng loại gốc; (2) mọi khoản lãi ở Lãi vay hiện là sai lệch → thêm lối "thêm đối tượng vào danh mục" thay vì chuyển tiền; (3) xem trước xác định tài khoản không mô phỏng đúng thứ tự xử lý, có thể ngầm chuyển tiền giữa lần migrate → mô phỏng chính xác và chặn; (4) dòng trùng sao kê bị bỏ khỏi chứng từ → lưu lại, không cộng tiền; (5) bỏ cắt hậu tố có thể cộng hai lần → gần trùng phải đối chiếu; (6) mã chết trong `check_batch`. Không còn yêu cầu không có task.

## Vòng 2 (sau PO review 22/10)
| Lỗi P1 | Sửa | Test hồi quy |
|---|---|---|
| Gần trùng phụ thuộc thứ tự nhập | `check_batch` + `NEAR_DUPLICATE` + preview lịch sử so cả lịch sử cùng tài khoản | `test_near_duplicate_legacy_first_then_bank_is_blocked_in_check_and_publish`, `…bank_first_then_legacy…`, `…in_other_account_is_not_flagged`, `…between_two_legacy_pastes_and_resolution` |
| Tạo mới quan hệ phân loại không hợp lệ | `classify` kiểm thành viên danh mục hiệu lực, bỏ ngoại lệ | `test_new_classification_blocked_when_owner_not_member_of_effective_category` (LOAN, PROPERTY), `test_loan_group_and_object_move_use_effective_category`, `test_unchanged_old_part_can_be_resaved_but_not_moved_to_another_invalid_place` |
Test cũ bị ảnh hưởng (theo hợp đồng mới, không chỉ đổi kỳ vọng): P18 (`object_rules`, `review_one_group`, `archive_blocked`: thêm bước "thêm đối tượng vào danh mục" + khẳng định bị chặn trước đó), P28 (`legacy_rules_without_members…` đảo thành "bị chặn, dữ liệu cũ giữ nguyên/xem được"), P19, P40 (thêm thành viên trước khi phân loại). P01–P17 dựng dữ liệu kiểu cũ bằng cờ nội bộ.
Phát hiện thêm: tổng của lần migrate **đã hủy** trong danh sách bị hiện 0 (P43 hiện tổng bản dán) — vòng 1 tôi chỉ so số dòng nên báo nhầm "giống hệt"; đã khôi phục cách hiện cũ + test `test_void_batch_keeps_reference_totals_but_counts_nothing`.

## Vòng 3 (sau PO review vòng 2)
| Lỗi | Sửa | Test hồi quy |
|---|---|---|
| Gần trùng trong cùng file sao kê không kiểm | `check_batch` kiểm `file_bases` (mã gốc) bên cạnh `file_refs` | `test_same_file_near_duplicate_blocks_import_and_publish_in_both_orders`, `test_same_file_exact_duplicate_blocks_import_and_publish`, `test_suffix_variants_in_different_accounts_are_kept_separate` |
| Cùng lần dán lịch sử: lặp y hệt bị tự bỏ qua; khác hậu tố không kiểm | `legacy_preview` dùng `paste_refs`/`paste_bases`; bỏ việc đưa dòng của lần dán vào tập "trùng lần trước" | `test_same_paste_exact_and_near_duplicates_block_preview_and_import` |
Đối chiếu bản sao dữ liệu thật: không file nào có mã gốc lặp khác hậu tố; kết quả kiểm tra các file đang chờ (44), (45), (5) giống hệt P43; tổng các màn giống hệt.
