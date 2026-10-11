# Data Model — 010 expense-refund
Không đổi schema. Dẫn xuất mới:
- `category_view().roots[expense].totals.net_spend` và `nodes[root=='expense'].totals.net_spend` = `out − in` (chuỗi Decimal, có thể âm). Các root/nút khác không có khóa này.
- `category_history(d)` trả thêm `root` (khóa gốc của danh mục) và, khi `root == 'expense'`, `totals.net_spend`.
Quy ước chiều: phần phân loại `expense` + giao dịch tiền ra = chi; + tiền vào = hoàn chi. Bất biến: Thu nhập chỉ tính phần `income`; `Σ in/out` của gốc không đổi so với trước.
