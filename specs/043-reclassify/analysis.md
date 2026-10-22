# Phân tích chéo (thủ công, không chạy `/speckit-analyze`) — 22/10/2026
| Yêu cầu | Task | Test / nghiệm thu |
|---|---|---|
| R195 chức năng chung, một đường ghi | T03, T05 | `test_ket_case…`, UI: mở từ lịch sử danh mục, màn phân loại, mục Cần đối chiếu |
| R196 nguồn bất biến, dấu vết, hoàn tác | T03 | `test_ket_case…` (id/tài khoản/ngày/mã/tiền/nội dung/chứng từ), `test_stale_preview…` (hoàn tác bằng sửa mới) |
| R197 A/B, thành viên, tham chiếu | T03, T04 | `test_move_between…`, `test_invalid_targets…`, `test_business_change…`, `test_business_references…`; P06/P07/P23 cập nhật (bảng kê, hoàn tất, đợt BĐS) |
| R198 xem trước = kết quả, mã xem trước | T03, T05 | `assert_preview_matches`, `test_stale_preview…`, `test_review_token_survives_server_envelope` |
| R199 nhiều phần | T03 | `test_split_transaction…` |
| R200 đã duyệt, lịch sử cũ | T03 | `test_approved_needs_adjustment…`, `test_legacy_row…` |
Test cũ đổi theo hợp đồng mới (mức B cần xác nhận; tham chiếu bị chặn): helper `classify` của P13/P18 gửi `business_ack` (tương đương đã xác nhận ở "Sửa phân loại"); gọi thô `act('classify')` vẫn nghiêm; P06 (2 ca bảng kê), P07 (hoàn tất), P23 (đợt BĐS) chuyển sang "mở lại/bỏ gắn rồi mới sửa"; P11, P44 thêm xác nhận ở chỗ đổi mức B có chủ đích. Không còn yêu cầu thiếu task/test.
