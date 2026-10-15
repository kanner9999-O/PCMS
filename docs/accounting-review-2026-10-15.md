# Rà soát nghiệp vụ kế toán — 15/10/2026

Căn cứ: Constitution nguyên tắc VIII. Rà theo nguyên tắc kế toán phổ biến; **không thay kế toán viên/chuyên viên thuế**. Mỗi mục ghi: hiện trạng → vì sao chưa đúng → đề xuất → cần Thạch quyết định. Chưa sửa gì; chờ Thạch duyệt từng mục.

## Đã đúng nghiệp vụ (giữ nguyên)
Chuỗi số dư liền mạch và đối chiếu sao kê; chứng từ bất biến, sửa bằng phiên bản có lý do (kể cả không xóa giao dịch cho vay nóng trong ngày); tiền vay không là thu nhập; lãi nhận là thu nhập, lãi trả là chi phí, tách vốn gốc/lãi; phải thu và phải trả không bù trừ; BĐS chưa định giá ghi theo giá gốc; chênh lệch chưa thực hiện không gọi là lãi/lỗ; không quy đổi VND/USDT khi chưa có tỷ giá; tiền khách nhận trước là nợ (doanh thu chưa thực hiện); cam kết thanh toán BĐS theo tiến độ chưa đến hạn không ghi thành nợ; giao dịch chưa phân loại là mục treo có cảnh báo; hoàn tiền mua hàng giảm chi phí.

## Cần sửa hoặc cần quyết định (theo mức ưu tiên)

### 1. Chi hộ / tạm ứng đang xử lý như "chi tiêu rồi hoàn chi" — CAO
- Hiện trạng: tiền bạn trả hộ người khác ghi vào Chi tiêu (có thể gắn khoản vay); người đó trả lại thì ghi "hoàn chi" làm giảm chi tiêu ròng (spec 010).
- Vì sao chưa đúng: tiền trả hộ **không phải chi phí của bạn** mà là **khoản phải thu (tạm ứng)**; người đó trả lại là **thu hồi phải thu**. Cách hiện tại làm chi tiêu bị khai cao và tài sản (phải thu) bị khai thấp cho tới khi họ trả; chỉ đúng khi toàn bộ đã hoàn.
- Đề xuất: danh mục "Chi hộ / Tạm ứng" thuộc nhóm phải thu; khi một giao dịch gồm phần bạn chịu và phần chi hộ thì tách phần (phần chịu = Chi tiêu, phần chi hộ = phải thu). "Hoàn chi" chỉ dùng cho tiền hoàn từ chính nhà cung cấp.
- Cần quyết định: có đổi cách xử lý chi hộ như trên không.

### 2. Nợ xấu và "không thu hồi được" chỉ là gom nhóm — CAO
- Hiện trạng: chuyển khoản vay sang danh mục Nợ xấu chỉ đổi nhóm; dư nợ vẫn tính đủ vào tài sản.
- Vì sao chưa đúng: phải thu khó đòi phải **trích lập dự phòng** (giảm giá trị tài sản, ghi chi phí); khi chắc chắn không thu hồi thì **xóa nợ** (ghi chi phí, có căn cứ); nếu sau đó thu lại thì ghi thu nhập khác. Không được chỉ đổi nhóm.
- Đề xuất: nghiệp vụ riêng "Dự phòng / Xóa nợ" gắn khoản vay (có ngày, số tiền, lý do), giảm phải thu hiển thị trong Tổng tài sản; số dự phòng nhập tay có căn cứ.
- Cần quyết định: có làm nghiệp vụ này; mức và căn cứ trích lập do Thạch/kế toán viên quyết.

### 3. Phân loại dài hạn / ngắn hạn theo ý chủ quan — CAO
- Hiện trạng: Long debt do Thạch tự xếp ("2–3 năm hoặc chưa có hướng trả"); khoản vay không có kỳ hạn (R90).
- Vì sao chưa đúng: kế toán phân loại theo **kỳ hạn thỏa thuận** (còn ≤ 12 tháng là ngắn hạn). Khoản **không có kỳ hạn/chưa có hướng trả** không phải dài hạn: coi là đòi theo yêu cầu (ngắn hạn) và cần xem xét khả năng thu hồi (mục 2).
- Đề xuất: thêm ngày đến hạn/kỳ hạn cho khoản vay; gợi ý phân loại ngắn/dài hạn theo kỳ hạn; khoản không kỳ hạn hiển thị nhãn "chưa có kỳ hạn" kèm cảnh báo.
- Cần quyết định: có thêm kỳ hạn (đảo quyết định R90) hay không.

### 4. Danh mục cho vay hiển thị "Chênh −46.000.000" và gộp cho vay với đi vay — CAO (trình bày)
- Hiện trạng: Long debt/Gốc vay hiện "Vào/Ra/Chênh"; ví dụ Mỹ ra 176 triệu, vào 130 triệu, chênh −46 triệu. Cho vay (Mỹ) và đi vay (Mama, Papa) cùng thuộc loại "Gốc vay".
- Vì sao chưa đúng: −46 triệu dễ đọc thành lỗ, trong khi đó là **phải thu 46 triệu (tài sản)**. Tiền ra nghĩa là cho vay (phải thu tăng) hoặc trả nợ (phải trả giảm); tiền vào là thu nợ hoặc nhận vay: nghĩa phụ thuộc hướng khoản.
- Đề xuất: mỗi danh mục vay có **hướng** (phải thu / phải trả) và hiển thị "Dư nợ phải thu" hoặc "Dư nợ phải trả" thay cho "Chênh".
- Cần quyết định: duyệt cách khai hướng ở danh mục.

### 5. Nợ margin đang không tính vào nợ — TRUNG BÌNH–CAO (khi dùng margin)
- Hiện trạng: nợ margin và vị thế sàn "hiển thị riêng, không cộng hay trừ" vào Tổng tài sản.
- Vì sao chưa đúng: nợ margin là **nợ phải trả thật** (vay sàn); bỏ ra ngoài làm tài sản ròng USDT bị khai cao.
- Đề xuất: đưa nợ margin vào nợ USDT (hoặc ít nhất cảnh báo đậm khi có nợ margin); vị thế đang mở giữ hiển thị riêng vì chưa là tài sản/nợ đã ghi nhận.
- Cần quyết định: có tính nợ margin vào nợ không.

### 6. Chi phí mua BĐS nên được vốn hóa — TRUNG BÌNH
- Hiện trạng: vốn đã thanh toán và "chi phí gắn BĐS" tách riêng; giá gốc dùng vốn đã thanh toán ròng.
- Vì sao chưa đúng: phí công chứng, thuế trước bạ, môi giới liên quan trực tiếp đến việc mua là **một phần nguyên giá**; chỉ chi phí sửa chữa/bảo trì/quản lý mới là chi phí kỳ.
- Đề xuất: khi phân loại, phân biệt "chi phí mua (vốn hóa)" và "chi phí vận hành"; giá gốc = vốn đã thanh toán + chi phí mua vốn hóa.
- Cần quyết định: có tách hai loại chi phí này.

### 7. Lịch sử cũ nằm ngoài sao kê (migrate) — TRUNG BÌNH
- Hiện trạng: đếm vào tổng đối tượng/danh mục; có đối chiếu dòng tổng; dòng trùng sao kê tự loại.
- Lưu ý kế toán: với khoản phải thu cũ, chuẩn là ghi **số dư chuyển sang tại ngày cắt** và giữ lịch sử làm chứng từ; replay toàn bộ giao dịch chỉ đúng khi bộ lịch sử đầy đủ (dòng tổng khớp là điều kiện tốt). Các bản ghi này không có chứng từ ngân hàng kèm số dư kiểm chuỗi được.
- Đề xuất: giữ cách hiện tại nhưng hiển thị rõ "dư nợ chuyển sang theo bảng Excel (chưa đối chiếu sao kê)" và cho phép ghi nhận số dư đầu kỳ thay vì từng dòng khi lịch sử không đầy đủ.
- Cần quyết định: có thêm chế độ "số dư chuyển sang".

### 8. Thực thể kế toán: tiền cá nhân và kinh doanh — TRUNG BÌNH (khi làm kinh doanh)
- Hiện trạng: TRX/Energy, cho vay lấy lãi (R29), shop (R28) có thể dùng chung tài khoản cá nhân; chưa có danh mục vốn chủ sở hữu.
- Vì sao cần: tiền cá nhân chuyển vào kinh doanh là **góp vốn**, rút ra là **rút vốn/chia lợi nhuận**, không phải doanh thu hay chi phí; nếu không tách, lợi nhuận kinh doanh sai.
- Đề xuất: khi làm nghiệp vụ kinh doanh có phân vùng riêng và danh mục "Góp vốn / Rút vốn".

### 9. Cơ sở ghi nhận doanh thu TRX và lãi cho vay là cơ sở tiền — THẤP (chấp nhận được, cần ghi rõ)
- Doanh thu TRX theo tiền thực thu (R65) và lãi cho vay theo thực thu (không dồn tích) là **cơ sở tiền**, chấp nhận cho quản lý cá nhân nếu **ghi rõ cơ sở** ở báo cáo. Nếu làm báo cáo kinh doanh hoặc dùng cho thuế, kế toán chuẩn dùng **dồn tích** (doanh thu theo thời gian cung cấp dịch vụ; lãi phải thu theo thời gian) — **cần kế toán viên/thuế xác nhận**.

### 10. Crypto: phí và thưởng — THẤP (chưa phát sinh vì chưa tính lãi/lỗ)
- Khi làm lãi/lỗ: phí mua vốn hóa vào giá vốn, phí bán là chi phí bán; thưởng staking/Earn là thu nhập theo giá trị tại ngày nhận (hiện chỉ ghi số lượng, R66). Cần giá tại ngày nhận khi tính.

### 11. Đợt thanh toán chung cư đến hạn — THẤP
- Cam kết chưa đến hạn không ghi nợ là đúng. Khi đợt đến hạn mà bên bán đã đạt tiến độ, đó trở thành **nợ phải trả đến hạn**; hệ thống mới nhắc "quá hạn". Đề xuất hiển thị "phải trả đến hạn" riêng (không tự cộng vào nợ khi Thạch chưa xác nhận).

## Thứ tự đề xuất xử lý
1) Chi hộ/tạm ứng, 2) nhãn dư nợ phải thu/phải trả theo hướng danh mục, 3) kỳ hạn khoản vay và phân loại ngắn/dài hạn, 4) dự phòng/xóa nợ, 5) nợ margin, 6) vốn hóa chi phí mua BĐS, 7) các mục còn lại khi làm nghiệp vụ liên quan.
