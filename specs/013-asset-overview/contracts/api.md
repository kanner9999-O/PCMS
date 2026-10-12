# Contracts — 013 asset-overview
Action `POST /api/action`: `assets-snapshot {note?}` (không có action sửa/xóa).
`GET /api/state` → `assets` và capability `assets`. UI: nút "Tổng tài sản"; hai khối VND/USDT; mỗi nhóm hiển thị giá trị, cơ sở, tỷ trọng, nút Mở màn nguồn; danh sách cảnh báo; nút "Lưu bản chụp" + ghi chú; danh sách bản chụp với chênh lệch.
Nhãn bắt buộc: ngân hàng "theo dữ liệu nguồn đã ghi đến ngày …"; BĐS "theo giá gốc, chưa định giá" khi dùng giá gốc; "không quy đổi VND ↔ USDT"; tài sản ròng âm: "nợ lớn hơn tài sản".
