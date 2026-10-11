# Contracts — 010 expense-refund
`POST /api/action classify`: phần `{category:'expense'}` nay hợp lệ cho cả giao dịch tiền vào; `{category:'income'}` vẫn chỉ cho tiền vào. Thông báo lỗi giữ cho vi phạm còn lại: "Loại thu/chi không khớp chiều tiền." (chỉ Thu nhập + tiền ra).
`GET /api/state` → `categories.roots[expense].totals.net_spend`, `categories.nodes[].totals.net_spend` (nhánh expense).
`POST /api/category-history` → `{…, root, totals:{…, net_spend?}}`.
UI: nhãn "Hoàn chi tiêu"; báo cáo duyệt có dòng "Chi tiêu · chi", "Hoàn chi tiêu", "Chi ròng"; màn Danh mục nhánh Chi tiêu hiện "Chi X · Hoàn chi Y · Chi ròng Z".
