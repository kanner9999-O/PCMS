# Plan 028
**Constitution (nguyên tắc VII)**: tuân thủ: chọn danh mục theo cấp, chỉ tải đối tượng của danh mục đã chọn.
Chỉ `web/p01.js` (`legacyWizard`): thay ô danh mục phẳng bằng chuỗi ô theo cấp (`legacyCascade`), thay ô đối tượng bằng danh sách `membersOf` của danh mục đã chọn; không đổi API. Kiểm tra trên QA 8801 với cây nhiều cấp; test JS thuần cho hàm dựng chuỗi cấp.
