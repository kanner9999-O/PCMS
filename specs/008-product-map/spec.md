# 008 — Bản đồ sản phẩm và trải nghiệm PCMS

Ngày: 11/10/2026. Nhánh: `008-product-map`. Trạng thái: đang thực hiện thiết kế; chưa được người dùng xác nhận bố cục.

## Yêu cầu đầu vào
Người dùng yêu cầu triển khai tổng quan sản phẩm, luồng nghiệp vụ, UI tổng thể vì chưa hình dung sản phẩm đang làm có giống mong muốn không. Đây là tài liệu thiết kế và bản tương tác độc lập, không phải phát hành chức năng tài chính mới.

Nguồn nghiệp vụ: PRODUCT-SPEC R01–R07, R09–R12, R15–R27, R33–R43, R47–R66; ACCEPTANCE N0–N5 và A54–A57. Chi tiết nguồn được ánh xạ trong docs/product/overview.md. Không thay quy tắc tiền hoặc tự chốt điểm mở.

## Specify — tình huống nghiệm thu
- US1/P1: mở bản đồ → hiểu PCMS giúp làm gì, có những phân hệ nào và phần nào chưa có.
- US2/P1: bấm qua 6 màn → thấy bố cục, việc chính, đường đi và trạng thái dữ liệu; có ví dụ truy từ 22 triệu nhận vào tới 20 triệu gốc + 2 triệu lãi trên cùng nguồn giả.
- US3/P1: đọc luồng → biết cách bắt đầu, nhập thiếu/sai, sửa sau duyệt và tiếp tục sử dụng; không hiểu duyệt đồng nghĩa mọi giao dịch đã phân loại.
- US4/P2: người tiếp quản tìm từ README tới thiết kế rồi yêu cầu Rxx/spec; thấy rõ thiết kế đích khác hiện trạng mã và bằng chứng nghiệm thu.

## Clarify
Không phỏng vấn lại. Dùng câu trả lời đã lưu. Chưa chốt FX, mẫu số tỷ trọng, giá vốn bán một phần, định giá: giữ trạng thái mở, không cần chốt để vẽ cấu trúc màn hình. Bố cục/điều hướng mới là đề xuất PO chờ feedback, không đánh dấu người dùng đã duyệt.

## Tiêu chí
SC1: đủ overview, journeys, ui-map và wireframe HTML độc lập.
SC2: các màn có nhãn dữ liệu giả/thiết kế; phần tài sản không trình bày tổng/tỷ trọng chưa có căn cứ.
SC3: đường truy nguyên hoạt động; các phép minh họa nhất quán, không nhân đôi nguồn.
SC4: có ma trận nguồn và trạng thái, có phân biệt mã đã có với nghiệm thu còn thiếu bằng chứng.
SC5: liên kết nội bộ hợp lệ, kiểm cú pháp và dùng thử bản thiết kế; không sửa src/tests/dữ liệu vận hành.
