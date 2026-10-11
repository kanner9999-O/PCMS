# Quyết định triển khai bản dùng thử cơ bản

28/09/2026. Căn cứ: Thạch yêu cầu hoàn thành sản phẩm có thể dùng thử; Codex tự đề xuất, tự quyết định và đóng vai owner, dùng dữ liệu giả lập cho BĐS, doanh nghiệp, cổ phiếu, crypto. Đây là quyền triển khai bản thử, không phải xác nhận số liệu thật hay chữ ký của Dũng.

| Quyết định | Chọn cho bản thử | Hệ quả |
|---|---|---|
| PT-001 — Giao diện | Web local tiếng Việt, 11 màn hình | Thay Sheets-only/no-custom-UI của baseline cho phạm vi demo; dùng Python chuẩn, không dịch vụ ngoài |
| PT-002 — Dữ liệu | Bộ dữ liệu riêng tại private-data/product-demo | Không dùng hai sao kê thật; giữ nguyên khu staging cũ |
| PT-003 — Policy | Nguyên tệ VND/USD/USDT; báo cáo USDT theo FX mẫu; giới hạn và cách tính được ghi trong hướng dẫn | Số liệu dùng để trải nghiệm, không diễn giải là chính sách tài chính thật |
| PT-004 — Vai trò | Một người local, nhãn Dũng · vai trò thử nghiệm | Có thể đi trọn luồng duyệt mà không gửi thông báo hay giả mạo duyệt thật |
| PT-005 — Lưu trữ | Mỗi thao tác ghi thêm một phiên bản trạng thái, nối checksum; snapshot đóng kỳ riêng | Không ghi đè bản đã chốt; sửa tạo đảo và thay thế; restore giữ lịch sử lưu trữ trước |
| PT-006 — Lõi sản phẩm | Projection tiền/số lượng/nợ riêng phục vụ demo, song song ledger journal pilot đã có | Chưa thay journal pilot bằng production ledger; không khẳng định UI demo đáp ứng full double-entry contract |
| PT-007 — Review | Quy tắc minh bạch + stress test + kế hoạch vốn 1/3/5 năm | Chưa tích hợp LLM; không gọi tính toán quy tắc là AI đã triển khai |
| PT-008 — Nhập | CSV giả lập review từng dòng; XLSX mẫu chỉ staging | Chặn file trùng và chốt kỳ khi file lỗi còn mở; không tự suy đoán mapping bank |
| PT-009 — Vận hành | Loopback, một máy, snapshot và export/restore | Chưa nhiều người/phân quyền/triển khai internet. Checksum phát hiện thay đổi ngoài ý muốn, không chống người có quyền sửa cả dữ liệu và checksum |

Luồng chính: nhập hoặc tạo giao dịch → kiểm tra → ghi sổ giả lập → xem tài sản/dòng tiền → review kịch bản → ghi quyết định → duyệt thử → thực hiện → đối soát → chốt kỳ → sao lưu. Tất cả tiền chỉ di chuyển trong sổ giả lập.

Dữ liệu tài sản/nợ thêm mới có ngày vào phạm vi; không làm thay đổi projection trước ngày đó. Định giá cập nhật tách khỏi giao dịch. Sửa giao dịch dùng bản đảo/thay thế; báo cáo cũ giữ nguyên, bản chốt lại tham chiếu bản trước. Policy và tỷ giá tại close được giữ cùng snapshot mới.

## 28/09/2026 — Nhập liệu liên tục và công nợ

Yêu cầu tiếp theo của Thạch: tài khoản là nơi giữ tiền/tài sản; nhập và phân loại bất cứ lúc nào, không ép chọn tháng. Triển khai được giao trực tiếp sau khi thống nhất hướng làm.

- PT-010: Luồng tài khoản → nguồn → số tiền → phân loại → báo cáo. Chốt kỳ là tùy chọn, không là điều kiện nhập liệu.
- PT-011: Tách bên liên quan khỏi tài khoản và tên người chuyển trên sao kê; một người có nhiều khoản vay. Gốc/lãi/phí tách riêng. Không bù trừ vay và cho vay.
- PT-012: Số tiền đã xác nhận nhưng chưa phân loại vẫn vào số dư; báo cáo tài chính đánh dấu tạm tính. Thay phân loại giữ tiền không đổi, ghi phiên bản đảo/thay thế.
- PT-013: Review nghi trùng ở cấp dòng giữa các file; không tự bỏ giao dịch chỉ vì cùng ngày/số tiền. Liên kết nguồn trùng phải được xác nhận; giao dịch distinct cần căn cứ.
- PT-014: Hai đầu chuyển giữ ngày và nguyên tệ thực tế; tiền đang chuyển được theo dõi giữa hai mốc. Số dư đầu và các khoản mở rộng phạm vi không tự thành thu nhập.
- PT-015: Giữ nguyên dữ liệu đã dùng; không đổi tên/số dư mẫu thành bốn tài khoản thật, không đoán nơi lưu ký hoặc chủ nợ. Người dùng tự khai báo bằng dữ liệu mẫu để trải nghiệm.

Hướng dẫn và giới hạn: runbooks/continuous-accounts.md. Bằng chứng nghiệm thu: continuous-acceptance.md.
