# Research — 006 trx-energy (quyết định kỹ thuật, 11/10/2026)

- **R1 Lưu trữ**: khóa `trx` trong state sự kiện (`customers, orders, receipts, rewards`), tạo bằng `setdefault` khi ghi. Lý do: backup/restore, kiểm chứng hash, audit chạy sẵn; không cần file mới. Loại: file riêng (mất kiểm chứng chung).
- **R2 Tiền**: số tiền lưu chuỗi Decimal. USDT làm tròn 6 chữ số (half-up); VND nguyên đồng. `usdt_equivalent = VND_nhận / tỷ_giá` (tỷ giá = VND mỗi USDT, do người dùng nhập), làm tròn half-up 6 chữ số, lưu cùng tỷ giá và thời điểm; không tính lại khi giá đổi (R39).
- **R3 Phân bổ**: append-only. Mỗi khoản thu có `allocations[{line, amount}]`; tổng phân bổ ≤ `usdt_equivalent`; tổng phân bổ vào một dòng ≤ số tiền dòng (thừa → để "chờ phân bổ"); dòng phải cùng khách. Không có tự động "cũ nhất trước" ở backend (R30/R40: Thạch chọn).
- **R4 Gắn giao dịch ngân hàng**: `bank_transaction` tùy chọn; phải là giao dịch đã ghi, tiền vào, VND; tổng `vnd_received` các khoản thu gắn cùng giao dịch ≤ số tiền giao dịch (chống ghi hai lần). Không sửa giao dịch ngân hàng.
- **R5 Hủy**: `void` đơn/khoản thu cần lý do; bản ghi giữ, loại khỏi tổng. Đơn có phân bổ còn hiệu lực không void được (phải void khoản thu trước). Khoản thu void giải phóng tiền ngân hàng đã gắn.
- **R6 Quá hạn**: chỉ khi đơn có `due_date` và hôm nay (giờ VN) > hạn và còn nợ; không có hạn → không gắn quá hạn.
- **R7 Báo cáo**: theo ngày nhận khoản thu (tuần Hai–CN, tháng, quý như `loan_cash_report`): USDT cấn tách theo loại dòng (Energy một lần / gói tháng / bán TRX / chờ phân bổ), VND thực nhận riêng, số TRX bán, số TRX thưởng; không lãi/lỗ (R66).
- **R8 UI mode**: `trxMode` như `debtMode`; nút trong sidebar; gate theo capability.
