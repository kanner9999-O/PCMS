# Review — Spec 045 (28/10/2026, Claude)
Trạng thái: **đã triển khai · đã nghiệm thu (PO/người dùng đại diện theo CLAUDE.md, dữ liệu giả) · phát hành: xem mục 5.** PO độc lập kiểm lại trên QA `:8807`.

## 1. Quy trình Spec Kit (đã gọi lệnh)
`/speckit-specify` → `/speckit-clarify` (không có điểm nghiệp vụ cần hỏi) → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` (báo cáo lưu ở [analysis.md](analysis.md): 0 CRITICAL, 2 MEDIUM, 4 LOW; C1, A1 sửa trước implement) → `/speckit-implement` (test backend viết trước: 5/5 ca mới thất bại trước khi sửa). Không có hook (`.specify/extensions.yml` không tồn tại). Truy nguyên: yêu cầu mới R202/A63; sửa lỗi review 044 ghi ở bảng "Truy nguyên" của spec và liên kết từ `specs/044-category-delete-guard/review.md` mục 6 (không sửa nội dung cũ của 044).

## 2. Đã triển khai
- `objects.py`: `obj_delete_trace`; `object-delete` giữ `memberships` trong bản ghi xóa. `categories.py`: `category-object-delete` dùng cùng helper; `cat_in_use_fast` đọc dấu vết đối tượng đã xóa, thông báo mới (nguyên nhân + "Lưu trữ để ẩn khỏi danh sách đang sử dụng" / "Giữ lưu trữ hoặc khôi phục"; khoản vay đang gắn: chuyển khoản vay trước); `category_view`: `archived_share` (gốc/cha), `delete_block`, `restore_block`, `archived_at`, `archive_reason`.
- `p01.js|css`: tab "Đang sử dụng" (mặc định) / "Đã lưu trữ (N)"; ghi chú tổng "gồm X giao dịch … thuộc K danh mục đã lưu trữ" + nút xem; tab lưu trữ: tìm (không dấu), đường dẫn, số liệu theo kỳ, thời điểm/lý do (hoặc "không có dữ liệu"), đối tượng, Lịch sử, Khôi phục hoặc lý do, Xóa hẳn hoặc lý do; danh mục cha lưu trữ còn con hoạt động hiện làm ngữ cảnh; bộ chọn theo cấp (`cascChildren`, `levelOptions`) đi qua được cha đó; mô tả hộp Xóa hẳn/Dọn danh mục đúng điều kiện.
- Test cũ đổi theo hợp đồng mới: `test_p47_category_delete` (2 đoạn chữ thông báo), `tests/js/classify_cascade.test.cjs` (lấy thêm `catPassable`, thêm ca cha lưu trữ – con hoạt động).

## 3. Kiểm thử
- `test_p48_category_archive.py`: 12 tests (5 ca 045 + 7 kế thừa P18). Toàn bộ: **447 tests OK**; node **9/9**.
- Bản sao chỉ đọc dữ liệu thật, P47 → P48: tổng danh mục/đối tượng, cờ xóa hẳn, Công nợ, báo cáo, Đối tượng, BĐS **giống hệt**; 3 danh mục lưu trữ (Kết, Bianance, Anh Tự) có thời điểm 28/10/2026 và lý do "Thừa"; Kết, Anh Tự: "đã từng được dùng để phân loại giao dịch… Giữ lưu trữ hoặc khôi phục"; Bianance xóa hẳn được; `archived_share` rỗng (hiện không có tiền trong danh mục lưu trữ). `view()` 1,11–1,20s (P47) → 1,17–1,20s (P48).

## 4. Nghiệm thu UI (dữ liệu giả `PCMS-QA/p48-qa`, :8811)
| Ca (A63) | Kết quả |
|---|---|
| Mở Danh mục: tab Đang sử dụng được chọn; 5 danh mục lưu trữ không có trong cây; nhãn "Đã lưu trữ (5)" | Đạt |
| Chi tiêu: tổng 1.750.000 không đổi; ghi chú "1 giao dịch (chi 600.000) thuộc 1 danh mục đã lưu trữ" + nút mở tab (lần đầu đếm 4 vì tính cả danh mục lưu trữ không có tiền — đã sửa chỉ đếm danh mục có tiền) | Đạt sau sửa |
| Tìm "cu qa" (không dấu) → "Chi tiêu › Cũ QA" và "Đầu tư BĐS › Nhà › Cũ QA" | Đạt |
| Con QA: "Chưa khôi phục được: Danh mục cha «Chi tiêu › Cha QA» đang lưu trữ" ; khôi phục Cha QA không khôi phục Con QA | Đạt |
| Khôi phục "Chi tiêu › Cũ QA": số tab 5→4, tổng Chi tiêu không đổi, hiện lại ở tab Đang sử dụng, ghi chú biến mất | Đạt |
| Xóa hẳn "Trống QA" (chưa dùng) từ tab lưu trữ: 4→3, có bản ghi xóa | Đạt |
| Đổi kỳ "Tháng này" khi đang ở tab lưu trữ: tab giữ nguyên | Đạt |
| "Có đối tượng QA" (đối tượng đã bị xóa hẳn): không có nút Xóa hẳn; lý do "từng có đối tượng thành viên (đã gỡ, chuyển hoặc xóa đối tượng)… Lưu trữ để ẩn" | Đạt |
| Lịch sử từ tab lưu trữ mở đúng; Sửa phân loại: cấp con của Chi tiêu không có danh mục lưu trữ | Đạt |
| Thông báo có "danh mục con" bị gượng ("Nếu không dùng nữa: Giữ lưu trữ…") | Đã sửa câu |

Chưa kiểm được bằng UI: trạng thái cha lưu trữ – con hoạt động (hệ thống chặn mọi đường tạo ra; dữ liệu thật 0 trường hợp) — kiểm bằng test JS bộ chọn và test backend các đường chặn.

## 5. Phát hành
PR #46 → `main` `9fda79a`. Kiểm `main` sạch: 447 OK, node 9/9. App `:8792`: build `P48-2026-10-28`, `p01.js` = `main` (`0c0a3e0d…`); tab lưu trữ có Kết, Bianance, Anh Tự; Xóa hẳn: Bianance, Long Debt. Hash dữ liệu thật trước = sau (`outputs/p01-user-trial` 161 file `a1ec41f0`, `private-data` 30 file `4421df5d`); không gửi lệnh ghi nào vào app thật.

**QA cho PO**: `http://localhost:8807`, dữ liệu giả `/Users/nerkan/Documents/Working/PCMS-QA/p48-po`, dựng lại được bằng `PCMS-QA/seed_p48.py` (chạy từ thư mục PCMS: `PYTHONPATH=src:tests python3 ../PCMS-QA/seed_p48.py ../PCMS-QA/p48-po`). Có sẵn: 5 danh mục lưu trữ (Chi tiêu › Cũ QA có 600.000; Nhà › Cũ QA trùng tên; Cha QA › Con QA; Trống QA), "Có đối tượng QA" + "Đối tượng tạm QA" để PO tự tái hiện P2 (xóa hẳn đối tượng rồi thử xóa danh mục), Hot QA/Property QA (044), QA-L1 (043).

## 6. Hướng dẫn sử dụng ngắn
- Danh mục → tab **Đang sử dụng** (mặc định) để làm việc; tab **Đã lưu trữ (N)** để tìm, xem lịch sử, khôi phục hoặc xóa hẳn danh mục chưa từng dùng.
- Khi tổng có phần thuộc danh mục đã lưu trữ, dòng vàng dưới tổng cho biết số giao dịch/tiền và nút **Xem danh mục đã lưu trữ**.
- Danh mục đã dùng: chỉ lưu trữ; lý do ghi ngay trên dòng. Khôi phục danh mục con cần khôi phục cha trước (không tự dây chuyền).

## 7. Giới hạn / còn lệch
- Đối tượng xóa trước bản này (dữ liệu thật: 0) không có dấu vết thành viên.
- Thanh công cụ (Gốc mới, Migrate, Danh mục mẫu, Dọn) vẫn hiện ở cả hai tab.
- README trong thư mục vận hành có thay đổi dở của người dùng nên không sửa; HANDOFF.md còn ghi bản P07.
