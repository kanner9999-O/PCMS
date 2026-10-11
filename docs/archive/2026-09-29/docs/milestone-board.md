# PCMS — Bảng nghiệm thu

> **Cập nhật nhập liệu liên tục:** đã bổ sung Tài khoản & biến động, Giao dịch cần xử lý, Công nợ theo người và Báo cáo theo ngày. Không bắt buộc làm theo tháng. Xem [hướng dẫn](runbooks/continuous-accounts.md) và [nghiệm thu](continuous-acceptance.md). Phần mô tả bản thử cũ bên dưới giữ làm lịch sử.


> **Cập nhật phạm vi 28/09/2026:** Thạch giao Codex tự quyết định và hoàn thành sản phẩm cơ bản dùng thử với dữ liệu giả lập. Đã triển khai ứng dụng local theo [quyết định bản thử](product-trial-decisions.md), [hướng dẫn sử dụng](runbooks/product-trial.md) và [nghiệm thu bản thử](product-trial-acceptance.md). Các ràng buộc Sheets-only/no-custom-UI và policy chưa chốt dưới đây thuộc baseline trước yêu cầu mới; chúng không chặn bản thử này. Những yêu cầu về dữ liệu thật/production chưa được coi là hoàn tất.


Cập nhật 28/09/2026. Người duyệt số liệu: **Dũng** (được xác nhận trong trao đổi). Thạch review sản phẩm qua kết quả sử dụng. Chưa có milestone nào được ghi nhận nghiệm thu hoàn thành.

## Quy tắc đã chốt

- Tài khoản giữ loại tiền/tài sản gốc: VND là VND; USDT là USDT.
- Tổng hợp theo USDT là hướng cho giai đoạn sau. Chưa có nguồn tỷ giá, thời điểm và chính sách quy đổi được chốt; chưa tự chuyển VND sang USDT.
- Hai sao kê đang dùng là mẫu lịch sử năm 2024, không đại diện số dư hiện tại hoặc toàn bộ tài sản.

## Bốn milestone của v0.1

| Mốc | Dũng cần thấy để nghiệm thu | Đã bàn giao | Còn thiếu |
|---|---|---|---|
| M0 — Chốt cách vận hành | Có phạm vi, người duyệt, đơn vị báo cáo, ngày bắt đầu, cách xử lý số liệu và quyền truy cập rõ ràng | Đã ghi nhận Dũng duyệt, giữ nguyên đơn vị tài khoản; form thiết lập có các mục còn mở | Phạm vi, opening có bằng chứng, timezone, người vận hành, quyền truy cập/backup, quy tắc close và các policy còn dùng |
| M1 — Biết có gì và ở đâu | Inventory đầy đủ trong phạm vi; tài khoản/tài sản/nợ có người sở hữu, mục đích, chứng từ; Dũng xác nhận | Hai tài khoản từ sao kê, danh sách để xác nhận | Quyền sở hữu, mục đích từng tài khoản; tài sản/nợ và tài khoản khác nếu thuộc scope; xác nhận inventory đầy đủ |
| M2 — Số liệu khớp | Đủ giao dịch, số dư khớp nguồn, không ghi trùng, sai lệch có giải thích, opening được Dũng duyệt | 76 dòng giữ nguyên nguồn; bảng cộng kiểm tra; ba vấn đề cụ thể được gom thành câu hỏi | Hai số dư đầu kỳ và cặp mã giao dịch lặp; phân loại giao dịch; mapping và ghi sổ thực được duyệt |
| M3 — Báo cáo và vận hành tháng | Báo cáo truy được số liệu; chạy review → duyệt → đóng tháng → khôi phục; có hướng dẫn | Workbook review theo milestone; lõi đóng kỳ và khôi phục chạy bằng dữ liệu giả lập | M2 đạt; báo cáo tài chính chính thức, đủ chỉ số có policy, một kỳ vận hành thật và approval |

Workbook hiện là **bàn giao để review**, chưa phải dashboard tài chính chính thức hoặc bằng chứng M0–M3 đã hoàn thành. Điền form không tự ghi sổ, chốt số dư hoặc duyệt milestone.

## Cách nghiệm thu phần vừa bàn giao

1. Mở `Tien_do`: thấy M0–M3, kết quả đã có và việc còn thiếu.
2. Mở `Thiet_lap`: Dũng và cách giữ đơn vị tiền đã được ghi nhận; phần chưa chốt để trống.
3. Mở `Tai_khoan`: kiểm tra hai tài khoản, bổ sung quyền sở hữu và mục đích sử dụng.
4. Mở `Doi_soat`: thấy số nguồn và phép cộng; các khoản lệch vẫn hiển thị, không bị sửa để ép khớp.
5. Mở `Can_xac_nhan`: trả lời các mục có thể xác nhận và ghi nguồn bằng chứng.
6. Mở `Giao_dich`: có 76 dòng và dropdown phân loại; ô vàng là nơi điền. Khoản chưa rõ để nguyên, không đoán.
7. Gửi lại workbook đã điền. Hệ thống nhận câu trả lời để review, kiểm tra số nguồn không bị sửa; Dũng duyệt tài chính ở bước riêng.

## Roadmap sau v0.1

| Mốc | Kết quả đích | Trạng thái DoD |
|---|---|---|
| M4 | Policy và review rủi ro danh mục hoạt động | Cần chốt chi tiết khi bước vào milestone |
| M5 | Kế hoạch phân bổ vốn mỗi tháng và đối chiếu thực hiện | Cần chốt chi tiết |
| M6 | Bảng tài sản toàn diện gồm property/business và nghĩa vụ | Cần chốt chi tiết |
| M7 | Monthly close dưới 30 phút, vẫn đủ kiểm soát | Cần chốt cách đo và số kỳ chứng minh |
| M8 | Nhịp review tuần/tháng/quý/năm vận hành | Cần chốt số chu kỳ nghiệm thu |
| M9 | Kế hoạch vốn 1/3/5 năm với scenarios | Cần chốt phạm vi và cách kiểm định |

M0–M9 là mã chính. Các bước nhập liệu, đối soát, báo cáo, đóng tháng là bằng chứng của M0–M3, không tạo thêm roadmap cạnh tranh. Chi tiết công việc kỹ thuật giữ ở [milestones](milestones.md), người dùng không cần đọc để nghiệm thu.
