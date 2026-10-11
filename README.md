# PCMS — Quản lý tài chính và tài sản cá nhân

**11/10/2026: P03–P07 đã phát hành** — ngân hàng VND, công nợ từng người/từng khoản, lãi dự tính, bảng kê lãi và miễn giảm có duyệt, tất toán có căn cứ, báo cáo dòng tiền tuần/tháng/quý.

**Tiếp quản dự án:** đọc [HANDOFF.md](HANDOFF.md) trước, sau đó đối chiếu yêu cầu trong PRODUCT-SPEC và ACCEPTANCE. Không cần lịch sử chat để bắt đầu.

[Mở PCMS](http://127.0.0.1:8792/) · [Khởi động](Start%20PCMS%20P01.command) · [Trạng thái và bằng chứng](IMPLEMENTATION-STATUS.md).

Bản vận hành hiện tại dùng `--p01` và dữ liệu `outputs/p01-user-trial`. Tên thư mục “trial” không có nghĩa có thể xóa: đã có dữ liệu và nguồn do người dùng nhập. Không dùng bộ này để chạy thử. Chỉ hỗ trợ VND và mẫu XLSX được nhận diện; chưa phải toàn bộ sản phẩm tài sản/đầu tư, chưa xác nhận số dư thực tế đã đầy đủ.

**Bản mẫu thiết kế cũ:**

[Bấm thử bản mẫu PCMS 05](outputs/design-review-v1/index.html) · [Hướng dẫn luồng và sơ đồ màn hình](PRODUCT-SPEC.md#8-thiết-kế-bản-dùng-thử--bản-mẫu-04). Bản 05 dùng sao kê (44) thật; phân loại thử chỉ giữ trong phiên. Bản 04 giả lập có liên kết riêng.

Chỉ có một bộ tài liệu hiện hành, đọc theo thứ tự:

1. [PRODUCT-SPEC — Sản phẩm, yêu cầu và luồng nghiệp vụ](PRODUCT-SPEC.md): đã xác nhận, đề xuất, câu hỏi còn mở.
2. [ACCEPTANCE — Mốc và điều kiện nghiệm thu](ACCEPTANCE.md): kết quả Thạch cần kiểm chứng; mốc N0–N5 đề xuất để review.
3. [IMPLEMENTATION-STATUS — Hiện trạng và quyết định](IMPLEMENTATION-STATUS.md): đã có gì, còn thiếu gì, bằng chứng và sổ phỏng vấn.

README chỉ là chỉ mục. [Bộ tài liệu cũ](docs/archive/2026-09-29/INDEX.md) được lưu lịch sử và **không còn hiệu lực hướng dẫn triển khai**. Mã và cấu hình không thay thế yêu cầu nghiệp vụ.

Bản local có sẵn qua [Start PCMS.command](Start%20PCMS.command), địa chỉ mặc định http://127.0.0.1:8787 khi dịch vụ chạy. Đây là bản thử trước baseline mới, chưa phải sản phẩm đã nghiệm thu. Lần gom tài liệu này không đổi ứng dụng hoặc dữ liệu.
