# Review — Spec 043 "Sửa phân loại" (22/10/2026, Claude)
Trạng thái: **đã triển khai · đã nghiệm thu (người dùng đại diện/PO theo CLAUDE.md, trên dữ liệu giả) · phát hành: xem mục 6.** Không có PO độc lập (Codex) trong đợt này.

## 1. Quy trình Spec Kit
specify (bản đồ tác động) → clarify (1 câu, Thạch chọn A) → plan/research/data-model/quickstart → tasks → analysis → implement → test → dùng thử → nghiệm thu → phát hành. Các bước làm **thủ công** theo mẫu dự án, không chạy slash command; bằng chứng là các file trong thư mục này.

## 2. Đã triển khai
- `src/pcms/reclassify.py` (mới): mức A/B theo chữ ký nghiệp vụ, chặn tham chiếu nghiệp vụ, xem trước mô phỏng `classify` trên bản sao (đặt phiên điều chỉnh trong bản sao), tác động danh mục/đối tượng/Công nợ/BĐS/nguồn, `review_token`, ghi (`transaction-reclassify`) và sửa dòng lịch sử cũ.
- `p01.py classify`: mức B cần `business_ack`; tham chiếu nghiệp vụ chặn (UI/API như nhau). `server.py`: `/api/reclassify-preview`.
- `web/p01.js|css`: hộp "Sửa phân loại" (nguồn chỉ đọc, chọn phần, danh mục theo cấp, đối tượng thành viên, khoản vay của người, thêm thành viên có xác nhận riêng, lý do, xem trước, xác nhận mức B, tự mở phiên điều chỉnh); nút trên mọi dòng lịch sử, màn phân loại (giao dịch đã phân loại), mục Cần đối chiếu (thay hộp điều chỉnh riêng của 042).

## 3. Nghiệm thu (dữ liệu giả `/tmp/pcms-043-qa`, bản thử `/tmp/pcms-043-qa-try`)
| Ca | Kết quả |
|---|---|
| Ca Kết từ lịch sử Gốc vay › Kết (đã duyệt) | Đạt: khoản vay Kết 5tr giữ nguyên; Gốc vay › Kết 0 giao dịch; Kết ở Gốc vay ra 10tr→15tr, 2→3 giao dịch; tổng Gốc vay 15tr không đổi; số dư 1.006.600.000 không đổi; snapshot 1 giữ nguyên; tự mở phiên điều chỉnh; danh mục con còn |
| Mức B: K3 thu gốc → Lãi vay | Đạt: xem trước "Kết 10tr: dư nợ gốc 7.000.000 → 10.000.000; lãi thu 200.000 → 3.200.000"; không tick xác nhận → từ chối; tick → ghi; Công nợ khớp xem trước |
| Nhiều phần: X1 phần 2 Đi lại·Mỹ → Ăn uống·Tươi | Đạt: phần 1 giữ nguyên 400.000; phần 2 600.000 đổi; tổng 1.000.000 |
| Đích chưa là thành viên | Đạt: Tươi không có trong danh sách Đi lại; "Thêm đối tượng có sẵn" có xác nhận riêng → chọn được; đổi lựa chọn sau xem trước → nút xác nhận tắt, kết quả xóa |
| Dòng lịch sử cũ (Nhà · Đất A → Đất B) | Đạt: mức B có xác nhận; bản dán gốc giữ nguyên; dấu vết trên dòng |
| Màn phân loại | Giao dịch đã phân loại có nút "Sửa phân loại" (7/7), mở đúng hộp |
| **Lỗi phát hiện khi dùng thử** | Mã xem trước tên `token` bị server ghi đè bằng mã phiên → bước ghi luôn báo "dữ liệu đã thay đổi" qua giao diện (test gọi thẳng backend không bắt được). Đã đổi thành `review_token` + test `test_review_token_survives_server_envelope`; chạy lại toàn bộ ca UI trên bản thử mới: đạt. |

## 4. Kiểm thử tự động
`cd tests && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../src python3 -m unittest discover -s . -p "test_*.py"` → **417 tests OK**; node 9/9 OK. `test_p45_reclassify.py`: 17 tests (10 ca 043 + 7 kế thừa P18).
Đối chiếu bản sao chỉ đọc dữ liệu thật (P44 vs P45): tổng danh mục gốc/con, tổng đối tượng, Công nợ, báo cáo, lịch sử cũ **giống hệt**. Xem trước (không ghi) ca Kết thật: mức A, không bị chặn, Gốc vay › Kết → Gốc vay, nguồn không đổi.

## 5. Hướng dẫn sử dụng ngắn
1. Ở dòng giao dịch (lịch sử danh mục/đối tượng/tài khoản, màn phân loại, mục Cần đối chiếu) bấm **Sửa phân loại**.
2. Chọn phần cần sửa (nếu giao dịch chia nhiều phần), chọn danh mục đích theo cấp, chọn đối tượng (và khoản vay nếu người đó có nhiều khoản). Đối tượng chưa thuộc danh mục: **+ Thêm đối tượng có sẵn vào danh mục này…** rồi xác nhận.
3. Nhập lý do → **Xem trước**: kiểm tra trước → sau, tổng danh mục/đối tượng, "tổng tiền và số dư không đổi"; nếu có khối "Ảnh hưởng nghiệp vụ" thì đọc kỹ và tick xác nhận.
4. **Xác nhận sửa**. Giao dịch đã duyệt: hệ thống tự mở phiên điều chỉnh; duyệt lại bản mới ở bước Xem toàn đợt và duyệt như thường.
5. Muốn hoàn tác: sửa lại về chỗ cũ (lần sửa mới có dấu vết). Đổi số tiền giữa các phần: nút **Chia lại số tiền giữa các phần…** (hộp Phân loại).

## 6. Giới hạn
Chưa sửa hàng loạt; chưa đổi số tiền giữa các phần ngay trong hộp này; dòng lịch sử cũ chỉ đổi trong cùng loại gốc; người có nhiều khoản vay phải chọn khoản; importer sàn vẫn chưa có (042 B1).

## 7. Review vòng 2 (23/10/2026) — hai lỗi được báo, đã sửa
| Mức | Lỗi | Nguyên nhân | Sửa | Bằng chứng |
|---|---|---|---|---|
| P1 | API `classify` cũ đổi thu gốc → thu lãi chỉ bằng `business_ack=true` (không xem trước, mã xem trước, lý do) | Quyền đổi mức B là một cờ trong dữ liệu client gửi | Quyền mức B là đối tượng nội bộ `RECLASS_GRANT`, chỉ "Sửa phân loại" cấp sau khi kiểm lý do, mã xem trước, xác nhận; JSON/API không tạo ra được; mọi cờ client gửi bị bỏ qua | `test_old_classify_api_cannot_make_business_change_with_any_flag` (5 tổ hợp cờ qua JSON); thử HTTP thật trên bộ giả: 3/3 bị từ chối, K3 không đổi |
| P2 | Dòng lịch sử cũ chuyển vào danh mục bắt buộc ghi chú thành công khi không có ghi chú | Đường sửa dòng lịch sử cũ không kiểm cờ `note_required` | Xem trước chặn `NOTE_REQUIRED`; bước ghi kiểm lại; hộp có ô **Ghi chú giao dịch** (gợi ý "bắt buộc với danh mục này"), ghi chú nằm trong mã xem trước; dấu vết ghi chú trước/sau | `test_legacy_row_into_note_required_category_needs_note`, `test_bank_transaction_into_note_required_category_needs_note`; thử UI: thiếu ghi chú → chặn, nhập ghi chú → xem trước lại → ghi đúng |
| Rà soát tác động (nguyên tắc IX) | Cùng lỗ hổng ở **nhập lịch sử cũ** vào danh mục bắt buộc ghi chú | `legacy_preview` không kiểm ghi chú từng dòng | Dòng thiếu ghi chú là dòng lỗi, không nhập được | `test_legacy_import_into_note_required_category_needs_note_per_row`; P38 đổi theo quy tắc (trước đây nhập được dòng thiếu ghi chú — đúng trạng thái sai) |

Test cũ dựng dữ liệu bằng `classify` mức B nay dùng `RECLASS_GRANT` trong tiến trình (tương đương đi qua "Sửa phân loại"). Kết quả: **421 tests OK**, node 9/9. Dữ liệu thật (đọc bản sao): chưa có danh mục bắt buộc ghi chú → 0 dòng bị ảnh hưởng. Build `P46-2026-10-23`.
Giới hạn thêm: hộp Phân loại cũ ("Chia lại số tiền giữa các phần…") không đổi được mức B; đổi nghiệp vụ dùng "Sửa phân loại" từng phần.
