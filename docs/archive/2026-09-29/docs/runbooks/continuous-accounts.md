# Tài khoản, giao dịch liên tục và công nợ

Cập nhật 28/09/2026. Thay cách làm bắt buộc theo tháng bằng nhập và phân loại bất cứ lúc nào. Bộ đang chạy vẫn là dữ liệu giả lập; dữ liệu và thao tác cũ được giữ nguyên.

## Bắt đầu với hai ngân hàng và hai sàn

Vào **Tài khoản & biến động → Khai báo tài khoản**, tạo từng tài khoản với tên riêng, chủ sở hữu, loại ngân hàng/sàn, mục đích, đồng tiền thanh toán, số dư và ngày bắt đầu theo dõi, nguồn xác nhận. Không nhập mật khẩu/API key. Ngày số dư đầu là đầu ngày; các giao dịch từ ngày đó trở đi được cộng tiếp. Không nhập giao dịch đã nằm trong số dư đầu lần nữa.

Bốn tài khoản thật chưa được tự đoán tên hay số dư. Năm tài khoản mẫu cũ được giữ nguyên, không tự đổi thành tài khoản của người dùng. Trong bản demo có thể tạo bốn tài khoản mới bằng số liệu mẫu để trải nghiệm. Đưa dữ liệu thật vào vận hành cần một bộ dữ liệu tách biệt; bản này vẫn có nhãn giả lập và FX mẫu.

Tài khoản sàn có tiền thanh toán chính và danh sách cổ phiếu/crypto gắn nơi giữ. Chọn **Phân bổ / chuyển tài sản** để gắn tài sản danh mục cũ từ “Chưa gắn nơi giữ” sang sàn, với ngày và căn cứ. Thao tác không tăng tổng số lượng hoặc tạo mua/bán. Mua/bán mới ghi số lượng tại tài khoản thực hiện; không được bán vượt số lượng tại nơi giữ. Chuyển nơi giữ chưa bao gồm phí trừ bằng coin; không giả định phí bằng 0 ngoài phần số lượng khai báo.

## Nhập và kiểm tra bất cứ lúc nào

**Nhập dữ liệu** nhận:

- CSV UTF-8: `date,account,amount,description`; thêm `direction` bằng IN/OUT, hoặc `kind` bằng income/expense để chỉ chiều tiền. `account` là mã tài khoản trong dữ liệu xuất/sao lưu, không phải tên tùy ý. Có thể thêm `reference`, `balance`, `opening_balance`.
- XLSX đúng mẫu sao kê đã có: giữ nguyên file, kiểm tra số dư nguồn, rồi chọn tài khoản ngân hàng tương ứng. Chỉ file không có lỗi và được mapping mới ghi được. Mã tham chiếu lặp không tự bị coi là trùng; debit và credit có thể khác nghiệp vụ.

File trùng toàn bộ bị chặn. Dòng tương tự qua hai file được đưa ra review: liên kết với dòng đã có (không ghi tiền lần nữa), hoặc ghi là giao dịch khác và nêu căn cứ. Không tự loại hai giao dịch chỉ vì giống ngày/số tiền. Bản nguồn đã bị sửa/phân loại vẫn được dùng tìm nghi trùng để tránh nhập lại lần nữa.

Khi nguồn cung cấp các số dư liên tiếp, hệ thống kiểm tra tăng/giảm có khớp không. File có dòng không hợp lệ hoặc sai số dư bị giữ tại vùng chờ, không ghi một phần để bỏ qua lỗi. Chưa có đủ mốc nguồn thì ghi rõ chưa chứng minh đầy đủ lịch sử. Có thể lưu nguồn không ghi sổ kèm lý do, rồi nhập bản nguồn đã xác minh.

## Ghi tiền trước, phân loại sau

Chọn **Ghi số tiền → Tiền vào/ra · phân loại sau**. Tiền cập nhật tài khoản, chưa được tính là thu nhập/chi phí. **Giao dịch cần xử lý** giữ những dòng chưa rõ; báo cáo tổng hiển thị tạm tính vì chúng có thể là tiền vay, mua tài sản hoặc chuyển nội bộ.

Chọn **Phân loại / tách khoản**: tối đa ba phần trên giao diện, có loại nghiệp vụ, số tiền, người liên quan, khoản vay, nhãn lãi, tài sản và số lượng nếu mua/bán. Tổng các phần phải bằng số tiền nguồn. Phần không dùng để 0. Phí đã có dòng riêng trên nguồn không cộng lần nữa.

Một dòng đã phân loại có thể chọn **Sổ giao dịch → Nguồn / phân loại → Phân loại lại**. Hệ thống đảo bản trước và thêm bản thay thế, không đổi số tiền nguồn. Phí gắn trực tiếp hoặc giao dịch chuyển/thi hành quyết định có luồng riêng; không phân loại lại bằng cách này.

**Ghép hai đầu chuyển tiền** liên kết hai dòng chưa phân loại, giữ ngày và số thực nhận từng đầu. Cùng đồng tiền phải bằng nhau; phí tách riêng. Khác đồng tiền giữ cả hai số, không suy ra từ FX báo cáo. Chuyển Đầu tư sang Trading vẫn cần quyết định được duyệt. Giữa ngày gửi và ngày nhận đã được liên kết, báo cáo ghi tiền đang chuyển; không coi là thu nhập hay chi phí.

## Công nợ theo người và từng khoản

1. **Công nợ theo người → Người / tổ chức**.
2. Tạo từng khoản: mã/tên, người chịu nợ, mình đi vay hay cho vay, nguyên tệ, ngày bắt đầu, dư gốc đầu, lãi suất tham khảo, điều khoản và đáo hạn, nguồn.
3. Nếu sẽ ghi nhận giao dịch giải ngân, để dư gốc đầu bằng 0. Nếu dùng số dư đầu đã xác nhận, không ghi giải ngân cũ lần nữa.
4. Nhận vay/cho vay bằng giao dịch có mã khoản vay; hoặc phân loại dòng sao kê đã có. Người gửi trên sao kê có thể chuyển hộ; người chịu nợ phải do người dùng xác nhận.
5. Trả 55 triệu gồm 50 triệu gốc + 5 triệu lãi: tách dòng sao kê thành repay 50 triệu và expense 5 triệu, cùng khoản vay, phần thứ hai nhãn “Tiền lãi”. Không nhập thêm thanh toán mới nếu tiền đã có trong sao kê.
6. Nếu thanh toán chưa được nhập từ nguồn nào, có thể dùng nút **Nhận / trả gốc và lãi** trên hồ sơ khoản vay; kiểm tra tổng gốc + lãi và phí riêng.

Báo cáo hiển thị tổng theo nguyên tệ, tổng theo người và từng món; không bù trừ khoản mình nợ với khoản mình cho vay. Phải thu cho vay được tính vào tài sản, không tính vào tiền thanh khoản. Lãi đã xác nhận có thể ghi riêng bằng căn cứ; tiền lãi đã trả/thu trừ khỏi lãi đã xác nhận. Lãi suất mới là điều khoản ghi nhận, chưa có máy tính lãi theo ngày/phạt/ghép lãi. Lãi chưa thu/chi được trình bày riêng, chưa đưa vào tài sản ròng theo tiền thực tế.

## Lịch sử, đối soát và báo cáo

**Tài khoản & biến động**: chọn tài khoản, từ ngày/đến ngày. Thấy số dư đầu, tăng/giảm thực tế, số dư sau mỗi dòng có hiệu lực và số dư cuối. Bản đảo/sửa không làm phình tổng tiền vào/ra; xem đầy đủ qua **Truy vết**. Cùng ngày chưa có giờ nguồn thì thứ tự là thứ tự ghi nguồn/nghiệp vụ, không khẳng định thời điểm trong ngày.

**Đối soát số dư nguồn**: chọn ngày và số dư bank/sàn thực tế; hệ thống hiển thị chênh lệch so với sổ tại ngày đó. Số điền sẵn lấy từ sổ chỉ để thử giao diện, không tự chứng minh nguồn độc lập.

**Báo cáo theo ngày**: thu/chi trong khoảng và số dư/tài sản tại ngày cuối. Không bắt buộc close. **Thiết lập → Ngày xem báo cáo** thay ngày mặc định của dashboard. Ghi giao dịch mới sẽ tự mở rộng ngày xem nếu cần.

**Đối soát & lưu báo cáo** vẫn là thao tác tùy chọn: snapshot cũ không đổi, báo cáo điều chỉnh tạo phiên bản mới. Chưa phân loại/sai lệch/chưa xử lý nguồn thì chưa chốt. Import, phân loại và xem lịch sử không phụ thuộc vào close.

## Giới hạn hiện tại

Một loại tiền thanh toán chính cho mỗi tài khoản và nhiều tài sản lưu ký; chưa có ví phụ đa đồng tiền, margin/futures, thuế, tự tính lãi hay kết nối ngân hàng/sàn. Bộ đọc XLSX chỉ nhận mẫu đã hỗ trợ. Chủ sở hữu hiện là thông tin trên tài khoản, chưa phải hệ thống phân quyền theo pháp nhân. Dữ liệu gốc giữ nguyên; không tự xác nhận bằng chứng thật hoặc đồng nhất người gửi tiền với chủ nợ.
