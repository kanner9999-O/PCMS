# Ghi nhận trao đổi ngày 22/10/2026 — chờ xử lý

## Cập nhật sau yêu cầu triển khai cả hai nội dung
Người dùng đã cho phép triển khai cả hai nội dung. Trạng thái mới: đang triển khai tại `specs/042-transaction-identity`, nhánh `codex/042-transaction-identity`; chưa nghiệm thu, chưa phát hành. Các ghi nhận bên dưới là lịch sử trước yêu cầu này. Điểm tiếp quản cụ thể nằm trong `specs/042-transaction-identity/review.md`.

- Người dùng yêu cầu tạm ghi nhận, chưa triển khai quy tắc: định danh giao dịch duy nhất trong từng tài khoản ngân hàng/sàn ngay đầu vào; danh mục và đối tượng chỉ phân loại giao dịch đó. Không coi ghi nhận này là cho phép thay đổi dữ liệu hoặc thiết kế đã hoàn tất.
- Vấn đề đang thảo luận: FT26267843740784 là một bản ghi nguồn 5.000.000 VND, nhưng phân loại còn trỏ danh mục con Gốc vay/Kết và hồ sơ khoản vay Kết; đối tượng người Kết lại là thành viên Gốc vay. Cách tổng hợp theo nơi thuộc về của khoản vay đưa số tiền vào đối tượng ở danh mục cha, trong khi tổng danh mục vẫn theo node của phần phân loại. Đây là sự không nhất quán giữa phân loại giao dịch và quan hệ đối tượng–danh mục, không phải hai giao dịch nguồn cần gộp.
- Chưa quyết định chuyển phân loại về danh mục cha hay giữ danh mục con và đặt đối tượng tại đó. Chưa sửa mã hoặc dữ liệu vận hành.
