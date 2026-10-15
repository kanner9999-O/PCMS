# PCMS Constitution

Nguyên tắc dưới đây đã đang áp dụng trong dự án (nguồn: `HANDOFF.md` §1, §4, §7) và được gom lại ở đây để mọi bước Spec Kit tuân theo. Không thêm quy tắc chưa từng được thống nhất.

## Core Principles

### I. Dữ liệu tài chính của người dùng là bất khả xâm phạm (NON-NEGOTIABLE)
`outputs/p01-user-trial` và `private-data/` là dữ liệu vận hành. Không xóa, seed, reset, phân loại lại, duyệt hay gọi API ghi để thử. Mọi thử nghiệm chạy trên thư mục dữ liệu giả riêng (ví dụ `--data /tmp/pcms-claude-qa --port 8799`). Không sửa tay các file JSON để đổi tiền hoặc trạng thái. Không gửi dữ liệu thật ra dịch vụ bên ngoài. Hai thư mục trên luôn nằm trong `.gitignore`.

### II. Không tự quyết định hay xác nhận số liệu tài chính thật
Assistant/agent không duyệt dữ liệu thật, không tự bù tiền, không tự publish file thay người dùng. Phân biệt rõ yêu cầu đã xác nhận, đề xuất và điều chưa chốt; không ghi đề xuất như thể người dùng đã chốt. Biên ngày, làm tròn lãi, FX và định giá là quyết định nghiệp vụ của người dùng khi chưa được chốt trong `PRODUCT-SPEC.md`.

### III. Tiền tính bằng Decimal độ chính xác cao
Không dùng `float` hay `Number` của JavaScript để tính tiền. Gốc lẻ triệu không bị cắt, không vốn hóa lãi. Quy tắc đã xác nhận: 500 VND/triệu/ngày tương đương 1,5%/tháng 30 ngày (R43).

### IV. Lịch sử bất biến, sửa bằng phiên bản mới
Snapshot đã duyệt không bị sửa; điều chỉnh tạo phiên bản mới có lý do, giữ bản cũ. Duyệt ngân hàng và duyệt bảng kê lãi là hai việc khác nhau. Không dùng lại một khoản tiền nguồn ở nhiều bản duyệt hiện hành.

### V. Hoàn thành phải có bằng chứng, không chỉ test xanh
Chỉ báo "xong" khi có mã chạy, test phù hợp và PO đã dùng thử qua UI bằng dữ liệu giả. Số test không phải bằng chứng đủ trải nghiệm. Phần chưa kiểm (mobile, dữ liệu lớn, hành trình đầy đủ) phải được nêu rõ, không im lặng bỏ qua. Không coi một đợt là hoàn thành mốc N0–N5 nếu chưa đối chiếu `ACCEPTANCE.md`.

### VII. Danh mục là cấu trúc trung tâm; đối tượng thuộc danh mục (QUYẾT ĐỊNH CẤU TRÚC, Thạch chốt 15/10/2026)
Mọi tính năng liên quan đến danh mục, hiện tại và về sau, phải theo cách quản lý này (R123–R128, R135, R136):
1. **Cây danh mục**: danh mục gốc → danh mục con nhiều cấp, mỗi danh mục có nhiều danh mục con (ví dụ Cho vay › Cho vay dài hạn, Vay ngắn hạn; Bất động sản › Chung cư, Đất nền).
2. **Đối tượng thuộc danh mục**: mỗi danh mục (ở bất kỳ cấp) có danh sách đối tượng của chính nó; đối tượng là hồ sơ chung, gán được nhiều danh mục, trước mắt chỉ cần tên; loại nghiệp vụ của đối tượng do Thạch quyết định sau.
3. **Chọn theo cấp, tải theo danh mục**: mọi giao diện (phân loại, phiên điều chỉnh, migrate lịch sử cũ, import, lọc, báo cáo...) chọn danh mục theo cấp cha → con; khi đã chọn danh mục thì **chỉ tải và hiển thị đối tượng của chính danh mục đó**, không tải toàn bộ danh mục hay toàn bộ đối tượng của mọi danh mục.
4. **Nghiệp vụ là lớp song song**: nghiệp vụ riêng (vay/cho vay, BĐS, kinh doanh, tách gốc/lãi...) tích hợp sau vào danh mục/đối tượng, không được làm đổi cấu trúc trên hay biến giao diện danh mục thành giao diện nghiệp vụ.
5. Spec mới có liên quan đến danh mục phải nêu tuân thủ nguyên tắc này trong phần kiểm tra Constitution.

### VIII. Nghiệp vụ kế toán là chuẩn cho mọi quyết định business logic (Thạch chốt 15/10/2026)
Thạch không am hiểu nghiệp vụ kế toán và muốn hệ thống vận hành **đúng nghiệp vụ kế toán**. Vì vậy:
1. **Luôn đứng trên nghiệp vụ kế toán để tư vấn.** Mọi quyết định business logic (ghi nhận, phân loại, đo lường, trình bày, công nợ, lãi, vốn, tài sản, doanh thu/chi phí, migrate dữ liệu cũ...) phải có tư vấn kế toán trước khi chốt: phương án đúng kế toán, lý do, hệ quả lên số liệu. Không để Thạch tự chọn công thức/quy tắc sai vì thiếu hiểu biết; câu hỏi phỏng vấn dùng ngôn ngữ dễ hiểu và **phương án đề xuất (Recommended) phải là phương án đúng kế toán**.
2. **Nguyên tắc kế toán áp dụng làm chuẩn** (đã thể hiện ở nhiều quy tắc sẵn có, nay là nguyên tắc chung): ghi nhận theo bản chất kinh tế (không theo hình thức chuyển khoản); tách vốn gốc, lãi, chi phí, hoàn chi, thu hộ/chi hộ; phải thu và phải trả **không bù trừ**; tài sản chưa có giá trị thị trường ghi theo **giá gốc** và nói rõ cơ sở; **thận trọng**: chênh lệch chưa thực hiện không phải lãi/lỗ, lãi chưa thỏa thuận/chưa thu không dồn tích; **nhất quán** phương pháp giữa các kỳ; **trọng yếu**; **chứng từ bất biến, có dấu vết, sửa bằng bút toán/phiên bản mới có lý do**; **đối chiếu** với nguồn (sao kê) và cắt kỳ (cut-off) rõ ràng; không quy đổi tiền tệ khi chưa có tỷ giá và nguồn.
3. **Trong mỗi spec có business logic** có mục "Tư vấn kế toán": phương án, khuyến nghị kế toán, rủi ro/hệ quả, điều cần kế toán viên/thuế xác nhận. Nếu yêu cầu của Thạch trái nguyên tắc kế toán, assistant nói rõ và đề xuất cách đúng; Thạch quyết định cuối cùng và quyết định đó được ghi lại kèm cảnh báo.
4. **Giới hạn trung thực**: assistant tư vấn theo nguyên tắc kế toán phổ biến, không thay kế toán viên/chuyên viên thuế có chứng chỉ; vấn đề thuế, pháp lý, báo cáo nộp cơ quan nhà nước phải được đánh dấu "cần kế toán viên/thuế xác nhận" và không khẳng định thay.

### VI. Gọn và tiết kiệm usage
Một coder với ngữ cảnh gọn cho mỗi đợt vừa phải; không đọc toàn bộ lịch sử, không tạo nhiều agent, không chạy test rộng hoặc lặp khi không có lý do. Không viết lại kiến trúc vô cớ; ghi phát hiện cụ thể rồi mới giao sửa.

## Ràng buộc bổ sung

- Giữ `PRODUCT-SPEC.md` (yêu cầu Rxx) và `ACCEPTANCE.md` (tiêu chí Axx/Pxx, mốc N0–N5) là nguồn sự thật về nghiệp vụ. Spec trong `specs/` mô tả một thay đổi cụ thể và phải trích dẫn mã Rxx/Axx liên quan; không được mâu thuẫn hai file trên. Nếu yêu cầu mới phát sinh, cập nhật `PRODUCT-SPEC.md` trước.
- Lõi `core.py`, `product.py`, `continuous.py` còn phần dùng chung; không xóa khi chưa có quyết định. Đường chạy hiện hành là `--p01` (`src/pcms/p01.py` và các mô-đun cùng nhóm).
- Gate tính năng mới theo capability backend để UI mới không gọi API chưa có của server đang chạy.
- Báo cáo theo phân bổ nguồn, không cộng snapshot; lãi nhận − lãi trả − chi phí là chênh tiền, không gọi là lợi nhuận ròng.
- Ngôn ngữ tài liệu và giao tiếp với người dùng: tiếng Việt.

## Quy trình phát triển

1. Yêu cầu mới → ghi vào `PRODUCT-SPEC.md` và `ACCEPTANCE.md` → `/speckit-specify` → (`/speckit-clarify` chỉ khi có điểm nghiệp vụ thật sự mơ hồ) → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement`.
2. Sau implement bắt buộc có bước **PO nghiệm thu**: dựng dữ liệu giả riêng, đi qua UI theo kịch bản, chạy hồi quy các đợt liên quan, rồi mới phát hành.
3. Phát hành: đối chiếu SHA256 các file dữ liệu vận hành trước và sau; cập nhật `IMPLEMENTATION-STATUS.md`, `HANDOFF.md`, README và manifest.
4. Mỗi tính năng làm trên một nhánh git riêng, commit theo đợt; không commit `outputs/`, `private-data/`, hoặc dữ liệu thật.

## Governance

Constitution này gom các quy tắc đã thống nhất; sửa đổi cần có sự đồng ý của người dùng (Thạch) và ghi lại trong `IMPLEMENTATION-STATUS.md`. Mọi bước plan/analyze phải kiểm tra tuân thủ. Mọi vi phạm phải được ghi chú và biện minh, không im lặng bỏ qua. Hướng dẫn vận hành hằng ngày xem `CLAUDE.md` và `HANDOFF.md`.

**Version**: 1.2.0 | **Ratified**: 2026-10-11 | **Last Amended**: 2026-10-15 (thêm nguyên tắc VII về cấu trúc danh mục và VIII về nghiệp vụ kế toán theo yêu cầu của Thạch)
