# PCMS — Dùng thử sản phẩm cơ bản

Ngày bàn giao: 28/09/2026. Theo yêu cầu mới của Thạch, Codex tự chọn thiết kế và chính sách để hoàn thành một sản phẩm dùng thử bằng **toàn bộ dữ liệu giả lập**. Không cần bổ sung dữ liệu thật để trải nghiệm.

## Mở sản phẩm

Mở http://127.0.0.1:8787 khi ứng dụng đang chạy. Khi cần mở lại, nhấp đúp **Start PCMS.command** trong thư mục PCMS; giữ cửa sổ chạy ứng dụng mở trong lúc sử dụng. Cần Python 3.10 trở lên (máy hiện tại đã có).

Dữ liệu được lưu sau mỗi thao tác. Đóng tab hoặc tải lại không làm mất dữ liệu. Bản sao lưu nằm trong mục **Thiết lập & sao lưu**; tải một bản trước khi thử khôi phục.

## Những gì có sẵn

- 5 tài khoản: chi tiêu VND, dự phòng VND, chứng khoán VND, đầu tư USDT và Trading USDT.
- 8 tài sản: hai bất động sản (có đồng sở hữu), một doanh nghiệp, hai cổ phiếu, ba crypto.
- Hai khoản nợ cá nhân, gồm nợ bảo đảm bằng bất động sản.
- 24 giao dịch từ tháng 7 đến tháng 9/2026; hai báo cáo lịch sử giả lập.
- Báo cáo ngày 28/09/2026: tài sản ròng ban đầu **745.960 USDT**, tiền **124.600 USDT**, nợ **69.400 USDT**. Đây là số mẫu, không phải tài sản của Thạch hay Dũng.

## Một vòng thử khoảng 15 phút

1. **Tổng quan:** xem tổng tài sản ròng, tiền ở đâu và cảnh báo tỷ trọng crypto.
2. **Tài sản & khoản nợ:** mở Riverside; xem giá trị tài sản và nợ, cập nhật định giá. Thử xem doanh nghiệp và tài sản đồng sở hữu.
3. **+ Giao dịch:** nhập chi phí 1.000.000 VND từ tài khoản Chi tiêu. Tổng tiền và tài sản ròng giảm 40 USDT theo tỷ giá mẫu. Vào Sổ giao dịch → Sửa để thử bản thay thế.
4. **Phân bổ & quyết định:** đề xuất 1.000 USDT từ Đầu tư sang Trading → Duyệt thử → Thực hiện. Tổng tài sản không đổi, hai tài khoản đổi số dư.
5. **Nhập dữ liệu:** chọn Nạp 2 giao dịch mẫu. Ghi sổ một dòng, bỏ qua dòng kia có lý do. Nhập lại cùng file bị chặn trùng.
6. **Rủi ro & kịch bản:** thay mức giảm giá. Xem tài sản ròng trong kịch bản, không thay đổi sổ thực tế.
7. **Kế hoạch 1/3/5 năm:** thay góp vốn và mức tăng trưởng giả định, lưu thành quyết định review nếu muốn.
8. **Đối soát & chốt kỳ:** thử nhập số dư sai để thấy chốt kỳ bị chặn. Dùng nguồn giả lập cho tất cả → Chốt báo cáo. Sửa giao dịch, đối soát và chốt lại: tạo phiên bản mới, giữ báo cáo cũ.
9. **Thiết lập & sao lưu:** tải báo cáo CSV để mở bằng Excel; tải bản sao lưu. Khôi phục yêu cầu nhập KHOI PHUC và tạo phiên bản mới.

## Các quy tắc Codex chọn cho bản thử

- Kỳ thao tác 01/07–28/09/2026, không tự nhận dữ liệu ngoài kỳ. Ngày hiện tại của máy không thay ngày báo cáo mẫu.
- VND, USD, USDT giữ nguyên ở tài khoản. Báo cáo tổng dùng USDT, với tỷ giá giả lập cố định 25.000 VND = 1 USDT và 1 USD = 1 USDT; không lấy giá thị trường.
- Giá trị tài sản = số lượng × giá × tỷ lệ sở hữu. Nợ cá nhân chỉ trừ một lần. Giá doanh nghiệp là giá vốn chủ sở hữu toàn doanh nghiệp; tiền/nợ bên trong doanh nghiệp không cộng/trừ lần nữa.
- Tài sản ròng thanh khoản mẫu = tiền + cổ phiếu + crypto − toàn bộ nợ cá nhân. Đây là giả định thận trọng, không phải tiền có thể rút ngay.
- Thu trừ chi hoạt động không bao gồm chuyển nội bộ, mua/bán tài sản, vay/trả gốc. Phí được ghi chi; trả gốc trình bày riêng. Không có dữ liệu giá vốn đủ để tính lợi suất nên không hiển thị lợi nhuận đầu tư.
- Ngưỡng review: tài sản riêng lẻ 35%, crypto 35%, dự phòng 20.000 USDT. Có thể điều chỉnh trong giao diện; không tự bán hay chuyển vốn.
- Dũng là **vai trò duyệt mô phỏng**. Một người dùng tại máy có thể đóng cả vai trò đề xuất và duyệt để trải nghiệm; không phải xác thực hay chữ ký của Dũng thật.
- Bổ sung tài sản/nợ là mở rộng phạm vi số dư đã có từ 28/09; không tự tạo thu/chi. Mua cổ phiếu/crypto mới: tạo tài sản số lượng 0 rồi ghi mua. Vay mới: tạo dư nợ 0 rồi ghi vay.
- Sửa sai hiện hỗ trợ số tiền/nội dung, giữ loại/ngày/tài khoản gốc. Giao dịch thực thi quyết định không dùng nút sửa thông thường.
- Đối soát tự động bằng nguồn giả lập chỉ là thao tác trải nghiệm, không phải bằng chứng ngân hàng.

## Ranh giới của bản cơ bản

Đây là ứng dụng local một người dùng; không kết nối tài khoản thật, không giao dịch thật, không có giá trực tiếp. Bộ review dùng quy tắc tính toán minh bạch; chưa tích hợp AI ngôn ngữ. Chưa có phân quyền nhiều người, thuế, kế toán doanh nghiệp đầy đủ, hiệu suất theo giá vốn hay tự động hóa lịch review.

CSV giả lập có thể đi từ nhập → review → ghi sổ. Adapter XLSX mẫu bank giữ nguyên nguồn trong vùng chờ, chưa tự mapping/ghi sổ. Hai sao kê thật đã gửi trước đó không được đưa vào bộ dữ liệu này.

Các thay đổi thử nghiệm không đồng nghĩa với nghiệm thu số liệu thật hoặc đáp ứng production. Mốc đóng kỳ dưới 30 phút và nhịp vận hành nhiều kỳ chưa được chứng minh bằng sử dụng thực tế.
