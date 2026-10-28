# Truy vết yêu cầu → task → test → bằng chứng QA — spec 046

**Test**: tất cả nằm trong `tests/test_p49_loan_business.py`, trừ các test có ghi `js:`, nằm trong `tests/js/loan_business.test.cjs`.

**QA**: kịch bản QA trong `quickstart.md`, chạy trên giao diện với bộ dữ liệu giả `PCMS-QA/p49-claude` (cổng 8810, ngày 28/10/2026). Nhật ký chi tiết ở `review.md` §3.

| Yêu cầu | Task | Test tự động | Bằng chứng QA (giao diện) |
|---|---|---|---|
| FR-001 / R203: gắn nghiệp vụ, kế thừa, xem trước, chặn xung đột | T005, T007, T008, T011, T012 | `US1CategoryBusiness.test_inheritance_and_child_different_blocked`, `test_parent_blocked_when_child_has_other_business_and_names_branch`, `test_no_inference_from_name_and_no_system_root`, `test_preview_counts_missing_and_conflicts_and_token` | QA-1: chặn "Hot Debt › Ngắn hạn (Đi vay)". Xem trước: thiếu 7 giao dịch (vào 115.510.000, ra 112.120.000), xung đột 1 (BĐS). Con hiện "kế thừa từ Hot Debt". Danh mục tên "Cho vay" không có nghiệp vụ. |
| FR-002 / R203: gỡ, đổi cha, lưu trữ, xóa hẳn | T006, T009, T010 | `test_clear_blocked_with_details_or_loans_and_move_blocked`, `test_clear_blocked_by_draft_and_delete_blocked_archive_keeps`, `test_child_move_under_other_business_parent_blocked_without_details` | QA-5: gỡ nghiệp vụ Hot Debt bị chặn ("5 giao dịch đã ghi"). |
| FR-003 / R204: khoản vay (mã, chiều, lãi, môi giới) | T013, T014 | `US2Loans.*` (3 test) | QA-2: CV-0001 / CV-0002 / ĐV-0001. Ô môi giới ẩn với khoản Đi vay. |
| FR-004 / R205: chi tiết, nháp, phiên bản, hủy | T015, T016, T018, T019 | `US3Details.test_split_two_loans_principal_and_interest_posts`, `test_incomplete_blocks_post_but_draft_saved_and_book_unchanged`, `test_replacement_keeps_current_until_posted_and_void_needs_reason`, `test_wrong_component_or_other_person_loan_blocked` | QA-3: L7 nháp còn thiếu 360.000 → sổ không đổi; ghi đủ 4 dòng (2 khoản, cả gốc và lãi). QA-9: hủy rồi ghi lại → phiên bản POSTED, VOID, POSTED. |
| FR-005 / R205: trạng thái chờ, chặn đường song song, chỉ hồ sơ Người | T006, T015, T017 | `test_pending_reasons`, `test_new_parts_only_person_in_business_category`, `test_parallel_paths_blocked_after_post`, `test_legacy_link_valid_not_double_and_legacy_row_detail` | QA-5: Sửa phân loại, chuyển đối tượng, gỡ thành viên đều bị chặn kèm hướng dẫn. Nhãn "Chờ chi tiết nghiệp vụ" hiện trên dòng giao dịch. |
| FR-006 / R206: lãi theo ngày, làm tròn | T003, T004 | `InterestEngine.*` (5 test), `US4InterestSettlement.test_example_numbers` | QA-3: L1 hiện lãi ngày đầu 50.000; L4 hiện 300.000. |
| FR-007 / R207: xem trước tất toán, lối vào từ khoản vay | T016, T020, T028 | `test_over_principal_and_over_interest_blocked` (PARTIAL), `test_full_settlement_label_and_cancel_waiver` (FULL) | QA-3: "Tất toán một phần" ở L4; "Tất toán toàn bộ gốc" ở L7. Nút "Ghi từ giao dịch nguồn" có trên mỗi khoản. |
| FR-008 / R207: miễn giảm | T020, T021 | `test_full_flow_completion_with_waiver`, `test_void_that_breaks_obligation_blocked` | QA-7: miễn giảm 30.000 → lãi còn thiếu về 0. |
| FR-009 / R207: hoàn tất, mở lại | T020, T021 | `test_full_flow_completion_with_waiver`, `test_pending_in_same_person_direction_blocks_completion` | QA-7: CV-0001 chỉ hoàn tất được sau khi miễn giảm. |
| FR-010 / R208: chặn trả vượt | T020, T021 | `test_over_principal_and_over_interest_blocked` | QA-3: thu gốc 110.000.000 bị chặn. QA-9: Tươi trả 3.000.000 lãi vượt 45.000 → bị chặn. |
| FR-011 / R209: môi giới theo điều khoản | T022, T023 | `US5Broker.*` (2 test) | QA-3 và QA-7: môi giới theo điều khoản 120.000 → 192.000; đã trả 120.000; không có số 60.000/90.000 nào. |
| FR-012 / R210: một sổ | T024, T025, T026 | `US6OneBook.test_consistency_across_screens_and_counts` | QA-8: Tổng tài sản (Phải thu 3.000.000 = khoản cũ + 0; Phải trả 50.000.000) = Công nợ = Danh mục = Đối tượng. |
| FR-013 / R211: báo cáo, số đếm | T024, T025, T028 | như trên (1 người, 3 khoản, 6 giao dịch; Hot Debt: 5 giao dịch) | QA-8: thẻ "1 người · 3 khoản · 6 giao dịch"; bảng "Theo danh mục". |
| FR-014 / R211: chưa đầy đủ, duyệt không bị chặn | T024, T028 | `test_pending_banner_and_caution`, `test_approve_with_pending_and_snapshot_unchanged`, `test_default_view_date_never_hides_recorded_events` | QA-6: băng "Chưa đầy đủ: 3 giao dịch · vào 7.000.000 · ra 2.000.000". QA-9: duyệt sao kê khi còn 3 nguồn chờ → được. |
| FR-015 / R212: nguồn, snapshot, khoản cũ không đổi | T024, T031 | `test_approve_with_pending_and_snapshot_unchanged`, `test_no_business_data_means_no_change` | QA-9: snapshot và tổng báo cáo giống trước/sau, không mở phiên điều chỉnh. T031: bản sao dữ liệu thật, P48 so với P49 giống hệt ở 11 nhóm số liệu. |
| FR-016: BĐS và nghiệp vụ cặp vẫn tạm dừng | T000, T030 | hồi quy spec 041 (`test_p43_*`) vẫn xanh | — |
| UI thuần (thành phần theo chiều, số còn phải phân bổ) | T029 | js: `loan_business.test.cjs` | — |
