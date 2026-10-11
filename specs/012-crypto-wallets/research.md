# Research — 012 crypto-wallets
- **R1 Định danh coin**: khóa `TICKER|MẠNG` (ticker in hoa `[A-Z0-9]{1,20}`, mạng chuẩn hóa in hoa, ≤30, có thể rỗng). Cùng ticker khác mạng hoặc có/không mạng là hai coin khác nhau (R76). Hiển thị "chưa ghi mạng" khi rỗng.
- **R2 Số hiện tại**: với mỗi (nơi giữ, coin, trạng thái) lấy bản ACTIVE có `(date, created_at)` lớn nhất. Số lượng 0 hợp lệ. Hủy bản mới nhất → quay về bản trước (như BĐS 011).
- **R3 Trạng thái**: ví riêng chỉ `HOLDING`; sàn thêm `EARN_LOCKED`, `MARGIN_COLLATERAL`, `OPEN_POSITION`, `MARGIN_DEBT`. Giá trị tài sản chỉ gồm `HOLDING`, `EARN_LOCKED`, `MARGIN_COLLATERAL`; `OPEN_POSITION` và `MARGIN_DEBT` liệt kê riêng, không cộng/trừ (R19). Tổng sàn = tổng các thành phần tài sản; ghi chú người dùng đảm bảo không chồng nhau.
- **R4 Giá và vốn**: giá hiện tại/vốn hiện tại theo coin lấy bản ACTIVE mới nhất theo `(date, created_at)`. Vốn là "tổng vốn bỏ vào tại ngày xác nhận" của coin (không cộng dồn nhiều bản) để tránh mơ hồ khi bán một phần (chưa chốt). Chênh lệch = giá trị − vốn chỉ khi có cả hai, nhãn cố định.
- **R5 Giá trị và tỷ trọng**: `value = số lượng × giá` làm tròn 6 chữ số half-up; tỷ trọng = `value / tổng giá trị có giá` 2 chữ số half-up; mẫu số chỉ gồm coin có giá và nơi giữ đang hoạt động; coin chưa có giá liệt kê `unpriced`. Theo nơi giữ: giá trị mỗi nơi giữ / tổng; theo coin: tổng các nơi giữ.
- **R6 Mốc theo dõi**: `start_date` tùy chọn; xác nhận có `date < start_date` bị chặn.
- **R7 Nơi giữ lưu trữ**: `ARCHIVED` (lý do bắt buộc) loại khỏi tổng và lựa chọn mới, vẫn xem lịch sử.
- **R8 UI**: `cryptoMode` như `realtyMode`; nút "Crypto"; gate theo capability.
- **R9 An toàn**: không có ô nhập khóa riêng/seed; ô nguồn chỉ là mô tả; UI có ghi chú "đừng nhập seed phrase/private key".
