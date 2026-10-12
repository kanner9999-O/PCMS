# Research — 015 classification-review
- **R1 Thời điểm phân loại**: `t['classification_history'][-1]['at']` (ISO UTC, `now()`), có cho cả phân loại thường, tách phần và ghép chuyển nội bộ; giao dịch chưa phân loại không có → `None` (xếp cuối). Phần của cùng một giao dịch dùng cùng thời điểm.
- **R2 Nhóm**: tên nhóm = đường dẫn danh mục (`cat_path` nếu có `node`, ngược lại tên gốc hệ thống; `transfer_pending` → "Chuyển nội bộ") + " · " + tên hồ sơ nếu phần có `profile`. `type` = loại gốc (`node.root` hoặc `root_key(category)`) để quyết định hiển thị chi/hoàn chi/chi ròng (`expense`).
- **R3 Dòng**: một dòng cho mỗi (giao dịch, nhóm); số tiền = phần của nhóm; `split=true` khi giao dịch có >1 phần phân loại (UI ghi "Phần của giao dịch X"); nhãn "Hoàn chi tiêu" khi `expense` + tiền vào (theo spec 010); `recent` = phân loại trong 24 giờ trước `now`.
- **R4 Sắp xếp**: nhóm theo `latest` giảm dần, nhóm Chưa phân loại cuối; dòng theo `(classified_at desc, date desc, order desc)`, `None` cuối.
- **R5 Phạm vi**: `all` | `recent` (giao dịch có `classified_at >= now-24h`) | `range` (`start`/`end` bao gồm hai đầu, dùng `cat_period`); chỉ giao dịch trong phạm vi vào tóm tắt và nhóm; kiểm khớp so với chính tập giao dịch trong phạm vi.
- **R6 Kiểm khớp**: như `category_review` — số giao dịch (tập giao dịch khác nhau trong các nhóm so với tập nguồn trong phạm vi), tiền vào, tiền ra (Σ phần so với Σ |signed|); trả `ok` và `difference`.
- **R7 Hiệu năng**: duyệt O(giao dịch × phần); không lưu; trả toàn bộ dòng (vài trăm giao dịch, JSON nhỏ).
- **R8 UI**: `<details open>` mỗi nhóm; nút thu gọn/mở tất cả đặt `open` hàng loạt; dòng dùng `display:grid` 4 cột (ngày+mã / nội dung+Xem nguồn / số tiền / nhãn) co lại một cột ở mobile.
