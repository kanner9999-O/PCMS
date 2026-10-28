# Review — Spec 044 "Chặn xóa hẳn danh mục còn dữ liệu" (28/10/2026, Claude)
Trạng thái: **đã triển khai · đã nghiệm thu (PO/người dùng đại diện theo CLAUDE.md, dữ liệu giả) · phát hành: xem mục 4.**

## 1. Quy trình Spec Kit (đã gọi lệnh)
`/speckit-specify` → `/speckit-clarify` (không cần câu hỏi; giả định đã đối chiếu dữ liệu thật) → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` (0 CRITICAL; sửa C1 thêm ca danh mục đã lưu trữ, I2 ghi chú README) → `/speckit-implement` (test trước: 3 test thất bại trước khi sửa, đạt sau khi sửa). Không có hook (`.specify/extensions.yml` không tồn tại).

## 2. Kiểm thử
- `test_p47_category_delete.py`: 12 tests (5 ca 044 + 7 kế thừa P18): lịch sử cũ chặn + lưu trữ vẫn được + danh mục đã lưu trữ cùng quy tắc; lần migrate đã hủy; dòng đã sửa phân loại đi; thành viên hoạt động; lịch sử thành viên đã gỡ; chuyển đối tượng; danh mục trống (hoạt động/lưu trữ) xóa được; nút = lệnh cho mọi danh mục.
- Toàn bộ: **435 tests OK**; node 9/9.
- Bản sao chỉ đọc dữ liệu thật, P46 → P47: tổng danh mục/đối tượng, Công nợ, báo cáo, Đối tượng, BĐS **giống hệt**; "Xóa hẳn": Property true→**false**, Hot Debt true→**false**, Bianance true→true, Long Debt true→true, các danh mục khác false→false. Thời gian dựng màn 1,32s → 1,34s.

## 3. Nghiệm thu UI (dữ liệu giả `/tmp/pcms-044-qa`, :8810)
| Ca | Kết quả |
|---|---|
| Màn Danh mục: Kết, Ăn uống, Đi lại, Nhà, Hot QA, Property QA không có "Xóa hẳn", có "Lưu trữ"; Trống QA có "Xóa hẳn" | Đạt |
| Lệnh xóa qua HTTP: Property QA "Còn 1 dòng lịch sử cũ…", Hot QA "Còn 1 đối tượng thành viên…", Ăn uống/Kết "đã từng được dùng để phân loại" | Đạt |
| Xóa Trống QA bằng nút + lý do → biến mất, có bản ghi đã xóa | Đạt |
| Lưu trữ Property QA → ARCHIVED, tổng danh mục và tổng Đầu tư BĐS không đổi, vẫn không xóa được | Đạt |

## 4. Phát hành
PR #44 → `main` `5819a2e`. Kiểm `main` sạch: 435 OK, node 9/9. App `:8792`: build `P47-2026-10-28`, `p01.js` = `main` (`bebea48c…`); "Xóa hẳn" trên app thật: Bianance, Long Debt = có; Property, Hot Debt, các danh mục khác = không. Hash dữ liệu thật trước = sau (`outputs/p01-user-trial` 158 file `664c9a16`, `private-data` 30 file `4421df5d`); không gửi lệnh ghi nào vào app thật.

## 5. Giới hạn / còn lệch
- Không tự xóa/lưu trữ danh mục thật nào; Bianance, Long Debt vẫn xóa được khi Thạch muốn.
- README trong thư mục vận hành có thay đổi dở của người dùng nên không sửa; HANDOFF.md còn ghi bản P07 (cũ từ trước, ngoài phạm vi).

## 6. Sau phát hành (liên kết, không sửa nội dung trên)
PO review `docs/po-review-044-2026-10-28.md` phát hiện: (P2) xóa hẳn đối tượng làm mất dấu vết thành viên → danh mục từng dùng trở nên xóa được; (UX) thông báo gợi ý gỡ/chuyển đối tượng. Cả hai sửa ở [spec 045](../045-category-archive-tabs/spec.md) (FR-006, FR-007), phát hành cùng R202.
