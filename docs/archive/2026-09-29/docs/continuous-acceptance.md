# Nghiệm thu nhập liệu liên tục

Ngày 28/09/2026. Triển khai tiếp trong bản dùng thử; không tự nghiệm thu thay người dùng hoặc xác nhận số liệu thật.

| Mốc | Kết quả đã triển khai | Cách thử |
|---|---|---|
| C1 — Tài khoản | Tạo ngân hàng/sàn, chủ sở hữu, nguyên tệ, mốc số dư; lịch sử có số dư sau từng dòng | Tạo tài khoản từ 2024, nhập thêm giao dịch 2026/2027; chọn khoảng ngày bất kỳ |
| C2 — Dữ liệu liên tục | CSV và XLSX mẫu; nguồn giữ nguyên, mapping, kiểm tra số dư, review nghi trùng qua file chồng kỳ | Nhập cùng file bị chặn; file khác chứa cùng giao dịch cần liên kết hoặc giải thích distinct; file sai số dư không ghi |
| C3 — Phân loại | Chưa rõ vẫn có số dư; tách tối đa ba phần trên UI; phân loại lại giữ lịch sử | Nhận 50 triệu chưa rõ rồi gắn khoản vay; trả 22 triệu tách 20 gốc/2 lãi; tiền không bị ghi hai lần |
| C4 — Công nợ | Mình vay/cho vay, tổng nguyên tệ, theo người, từng món, hạn trả, lãi xác nhận | Tạo bốn người, người A hai khoản; trả một khoản không làm giảm khoản khác |
| C5 — Truy vết và báo cáo | Nguồn, bản gốc/thay thế, lịch sử có hiệu lực, ghép chuyển khác ngày, báo cáo khoảng ngày | Chuyển giữa hai tài khoản không thành thu nhập; tiền đang chuyển có trong báo cáo giữa hai ngày |

Kiểm tra: 77 tests Python qua, gồm 61 kiểm tra có sẵn và 16 kiểm tra mới. Kiểm thử trình duyệt trên dữ liệu riêng: tạo tài khoản/người/khoản vay, ghi chưa phân loại, tách gốc/lãi, nhập CSV, ghép chuyển, báo cáo ngày, reload và desktop/mobile. Backup bản dữ liệu đang dùng được lưu trước khi nâng cấp; snapshots và lịch sử cũ không bị viết lại.

Cách dùng: [Hướng dẫn tài khoản & công nợ](runbooks/continuous-accounts.md). Danh sách giới hạn và nghĩa của số dư/lãi được ghi ở cuối hướng dẫn.
