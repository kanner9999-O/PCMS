# Plan — 008

Ngày 11/10/2026; phạm vi thiết kế sản phẩm, không triển khai chức năng tài chính.

1. PO đọc yêu cầu gốc, spec 001–007 và mã thể hiện capability P09; lập tổng quan/luồng/UI.
2. Một coder làm HTML độc lập trong docs/product/wireframes, chỉ dữ liệu giả, không API, không tài nguyên ngoài.
3. PO kiểm nhất quán giữa yêu cầu, thiết kế, tasks trước bàn giao; kiểm đường dẫn và dùng thử giao diện.
4. Ghi kết quả cùng giới hạn trong review.md; liên kết từ README. Không sửa tình trạng P08/P09 của Claude trong lượt này.

Constitution: bảo vệ dữ liệu bằng không đọc nội dung/ghi bộ vận hành; không thay quyết định tiền; không phép tính tài chính float; không gọi luồng app; có nhánh riêng, một coder, ngữ cảnh hẹp. Không cần hồi quy backend hoặc restart app vì không sửa app. Không tuyên bố phát hành nghiệp vụ hoặc người dùng đã nghiệm thu bố cục.

Phương tiện: Markdown + Mermaid cho tài liệu; HTML/CSS/JS inline cho bản tương tác. Không thư viện mới. Bản thiết kế tải trực tiếp từ file hoặc server riêng chỉ phục vụ docs/product. Desktop và màn hẹp phải đọc được; không có chức năng lưu thật.
