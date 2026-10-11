# PCMS — Bức tranh sản phẩm

Bản thiết kế 1 · 11/10/2026 · **Đề xuất bố cục, chưa được người dùng xác nhận.**

**[Mở bản thiết kế tương tác](wireframes/index.html)** · [Luồng nghiệp vụ](journeys.md) · [Bản đồ màn hình](ui-map.md) · [Theo dõi đợt thiết kế](../../specs/008-product-map/tasks.md)

## Sản phẩm để làm gì?
PCMS giúp một người quản lý tiền, tài sản và nghĩa vụ của mình từ nguồn có thể kiểm chứng. Người dùng biết tiền ở đâu, vào/ra vì việc gì, còn phải thu/trả bao nhiêu và hoạt động nào tạo tiền. Đích dài hạn là hiểu danh mục và có căn cứ tự quyết định điều chỉnh; chưa có cơ sở tự đưa khuyến nghị mua/bán hoặc tỷ trọng tối ưu.

Thói quen sử dụng mong muốn: mở tổng quan để biết việc cần xử lý; nhập nguồn khi có; phân loại gắn đúng việc; xem sổ và báo cáo; từ bất kỳ số tổng nào mở được nguồn cấu thành. Không phải dùng nhiều sổ rời rồi tự cộng lại.

## Sáu khu vực người dùng nhìn thấy
| Khu vực | Câu hỏi nó trả lời | Đường đi chính |
|---|---|---|
| Tổng quan | Tôi đang có dữ liệu gì, còn thiếu gì, tiền nằm ở đâu? | Việc cần xử lý → tài khoản/khoản nợ; số tổng → danh sách cấu thành |
| Tài khoản | Nguồn tiền có khớp, đã xử lý tới đâu? | Hồ sơ → nhập/kiểm → phân loại → tóm tắt → duyệt/điều chỉnh |
| Công nợ | Ai nợ tôi, tôi nợ ai, gốc/lãi còn bao nhiêu? | Người → từng món → gốc/lãi/bảng kê → nguồn → hoàn tất |
| TRX / Energy | Khách mua gì, trả bao nhiêu, còn thiếu bao nhiêu? | Khách → đơn → thu tiền/phân bổ → công nợ/báo cáo |
| Tài sản | Tôi sở hữu gì, vốn đã bỏ và giá trị hiện tại có căn cứ gì? | Crypto theo coin/nơi giữ; BĐS theo hồ sơ → nguồn vốn/định giá |
| Báo cáo xuyên suốt | Tiền thực vào/ra và tỷ trọng có ý nghĩa gì? | Chọn kỳ/phạm vi/đơn vị → số tổng → giao dịch; chưa đủ nguồn thì cảnh báo |

Bản HTML dùng tab “Bản đồ hành trình” để giải thích thiết kế; tab này không phải phân hệ tài chính bắt buộc trong sản phẩm cuối. Báo cáo hiện trong từng khu vực; một trung tâm báo cáo hợp nhất là thiết kế đích.

## Điều không được nhập nhằng
- Tài khoản là **nơi giữ**, danh mục là **ý nghĩa nghiệp vụ**, hồ sơ là **đối tượng cụ thể**. Cùng một nguồn có thể được nhìn qua cả ba, không phát sinh thêm tiền.
- 22 triệu tiền vào được chia 20 triệu thu gốc + 2 triệu lãi: ngân hàng tăng 22 triệu; khoản phải thu gốc giảm 20 triệu; tiền lãi nhận 2 triệu. Không gọi 22 triệu là doanh thu và không tính việc thu gốc là tài sản mới.
- VND, USDT, số lượng TRX giữ riêng. 2,5 triệu VND @25.000 được cấn 100 USDT là hai biểu diễn của cùng khoản thu; không cộng chúng như hai khoản tiền.
- Gốc còn lại, lãi dự tính, bảng kê đã duyệt, lãi thực thu là các số khác nhau. Hết gốc chưa chứng minh đã tất toán.
- Tổng theo dữ liệu nháp, snapshot đã duyệt và khoảng thiếu nguồn phải có nhãn khác nhau. Chưa phân loại vẫn có thể được duyệt với xác nhận rõ.
- Số dư đầu không là thu nhập. Thiếu giá vốn/nguồn không thay bằng số 0. Giá trị tài sản không lấy từ giá trị danh nghĩa futures.

## Hiện trạng tại mốc kiểm tra 11/10/2026
Đọc repository tới commit `7d0b756`. Đây là đối chiếu tài liệu/mã, không phải nghiệm thu lại ứng dụng.

| Khả năng | Hiện trạng mã | Bằng chứng/giới hạn | Nguồn |
|---|---|---|---|
| Ngân hàng VND, nhập nguồn, phân loại, duyệt/điều chỉnh, tài khoản | P01–P03 có mã | Có hồ sơ nghiệm thu cũ; parser giới hạn mẫu nhận diện | R01–R06, R17–R21, R49–R62; spec 001 |
| Công nợ, gốc/lãi, bảng kê, tất toán, báo cáo | P04–P08 có mã | P04–P07 có hồ sơ; P08 báo đã phát hành nhưng file bàn giao/ảnh được tasks dẫn chiếu chưa tìm thấy ở lần audit | R07, R29–R31, R42–R43, R47, R52–R53; specs 002–005 |
| TRX/Energy ghi nhận thủ công | P09 có mã | Báo đã phát hành; thiếu outputs/p09-handoff.md theo task. Chưa xác nhận lại nghiệm thu | R33–R41, R48, R63–R66; spec 006 |
| Crypto/ví/sàn, BĐS đầy đủ | Backlog | Có thiết kế cũ; chưa coi là khả năng app hiện hành | R15–R19, R23, R25–R27, R58; spec 007 |
| Tổng tài sản ròng, quy đổi và tỷ trọng thống nhất | Thiết kế đích | FX, định giá, mẫu số và nhiều trường nghiệp vụ còn mở; không đưa tổng giả như số đã xác nhận | R09, R15, R18–R19 |
| Hỗ trợ quyết định phân bổ danh mục | Tầm nhìn | Cần nền dữ liệu/định giá trước; chưa có thuật toán hoặc tiêu chí đầu tư được chốt | R11, R15, R18 |
| Shop, cổ phiếu, chốt tháng | Pending | Không tự đưa vào đợt hiện tại | R22, R24, R32 |

## Những quyết định còn mở
Nguồn/ngày định giá; FX dùng cho tổng hợp; cách tính vốn khi bán một phần; mẫu số tỷ trọng và xử lý nợ; trường futures/margin/Earn; quyền lợi BĐS góp vốn. Các màn vẫn có thể được review về cấu trúc mà chưa cần người dùng trả lời toàn bộ điểm này. Chỉ hỏi khi chuẩn bị triển khai nghiệp vụ phụ thuộc nó.

## Thứ tự hoàn thiện do PO đề xuất
1. Khép bằng chứng còn thiếu P08/P09 và kiểm hành trình nối ngân hàng–công nợ–Energy.
2. Nhận feedback trên bản đồ này; sửa bố cục/hành trình nếu lệch ý tưởng người dùng.
3. Triển khai tài sản theo từng lát có nguồn: khởi tạo nơi giữ/coin và hồ sơ BĐS; làm rõ nghiệp vụ liên quan ngay trước triển khai.
4. Tổng quan hợp nhất, tỷ trọng và phân tích khi chính sách và độ phủ dữ liệu đủ. Không chốt “toàn bộ sản phẩm xong” chỉ vì đủ màn hình.

## Vai trò tài liệu này
PRODUCT-SPEC và ACCEPTANCE vẫn là căn cứ. Bộ docs/product diễn giải chúng thành trải nghiệm; specs/ là từng lát triển khai. Mỗi thay đổi màn hình phải xét ảnh hưởng tới hành trình, cập nhật thiết kế nếu cần, rồi nghiệm thu luồng. Mã có trước nhưng không phù hợp thiết kế mới phải được lập task, không tự ghi thành đã có.
