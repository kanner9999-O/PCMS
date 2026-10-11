# PCMS — Nghiệm thu chính thức

Phiên bản 2.2 · 05/10/2026 · Theo [PRODUCT-SPEC](PRODUCT-SPEC.md).

Đây là bộ tiêu chí duy nhất cho kế hoạch bản dùng thử đang review. Đã chuyển từ phỏng vấn rộng sang thiết kế. **N0–N5 dưới đây là đề xuất hiện hành**, thay bảng N0–N3 dự thảo trước; chưa phải mốc được người dùng nghiệm thu hoặc deadline đã cam kết. Không chuyển trạng thái test demo cũ thành nghiệm thu mới.

## 0. Cơ chế đánh giá từ 08/10/2026

### P10 — R06, R45, R46, R50, R55, R56, R58, quản lý danh mục (spec 008)

Tiêu chí chi tiết ở `specs/008-category-management/spec.md` (SC-001…SC-005): tạo và dùng danh mục con không cần sửa mã; tổng từng danh mục khớp tập dòng liệt kê, mỗi giao dịch một lần ở cha; từ tổng mở dòng nguồn ≤2 thao tác; danh mục rỗng không hiện số 0 như đã đối soát; snapshot/báo cáo/công nợ cũ không đổi, snapshot mới đóng băng tên danh mục.

### P09 — R33–R41, R48, R63–R66, TRX/Energy bản đầu (spec 006)

Tiêu chí chi tiết ở `specs/006-trx-energy/spec.md` (SC-001…SC-005): 3 kỳ × 100 USDT → phải thu 300, thu 200 còn 100; thu VND lưu VND + tỷ giá + USDT cấn và không đổi theo lần sau; một giao dịch ngân hàng gắn đúng một lần, không gắn giao dịch đã thuộc khoản vay; báo cáo chỉ tiền thực thu, không lãi/lỗ, không tự quá hạn; hủy giữ lịch sử; dữ liệu cũ không đổi.

### P08 — R47/R53, hoàn thiện hành trình công nợ (spec 005)

Tiêu chí chi tiết ở `specs/005-debt-journey-polish/spec.md` (SC-001…SC-005): báo cáo dòng tiền mở ra kỳ có dữ liệu hoặc cảnh báo chưa có nguồn; Tổng quan công nợ ở đầu màn không bù trừ phải thu/phải trả; khoản hết gốc chưa tất toán hiện lý do; đi lại tài khoản ↔ công nợ ≤2 thao tác; dữ liệu và báo cáo cũ không đổi.

### P07 — R53/A49, tất toán và báo cáo theo kỳ

- Hết gốc còn lãi/thiếu kỳ bảng kê/chưa duyệt/nguồn sai thì không tất toán. Đủ điều kiện, xác nhận có căn cứ thì hoàn thành; không tạo tiền. Mở lại giữ lịch sử, nguồn thay đổi không còn hiện hoàn thành hợp lệ.
- Lọc người/khoản hoàn thành vẫn xem lịch sử/chứng từ. Một người còn khoản hoạt động không bị coi là đã hoàn thành toàn bộ.
- Tuần thứHai–Chủnhật/tháng/quý chọn ngày lấy đúng biên lịch; lãi nhận của cả khoản đã tất toán được tính. Ca2,7 triệu lãi nhận và0,2 triệu chi phí gắn khoản cho chênh2,5 triệu; không gồm gốc/miễn giảm và không nhận vơ đủ chi phí.
- Chỉ phân bổ chi phí có liên kết khoản vay được đưa vào phạm vi; giao dịch tách phần tính đúng một lần, có truy nguồn. Bộ lọc trạng thái danh sách không cắt báo cáo thu lãi lịch sử.
- PO thử chặn tất toán chưa đủ, hoàn thành khoản đủ, lọc xem lại và đối chiếu báo cáo; dữ liệu giả riêng. Snapshot/bản sao tương thích dữ liệu cũ.

### P06 — Bảng kê lãi và quyết định miễn giảm

- A36: dự tính1.500.000, chọn tiền nguồn1.200.000, không giảm thì còn300.000. Duyệt giảm300.000 có lý do/ngày/xác nhận thì còn0; tiền thực nhận vẫn1.200.000, gốc không đổi.
- A37: sau bản duyệtS1, điều chỉnh phải có lý do, tạoS2 và xem lạiS1 nguyên vẹn. Lưu nháp không thay số đã duyệt. Không duyệt lặp cùng nội dung.
- Một tiền lãi có thể phân bổ một phần qua nhiều kỳ, nhưng tổng bản duyệt hiện hành không vượt nguồn. Không lấy tiền khoản khác, sai chiều hoặc gốc làm tiền lãi. Không tự lấy ngày nhận tiền làm kỳ trả. Phần vượt chưa phân bổ, không tăng lãi dự tính.
- Chặn kỳ chồng nhau của cùng khoản và kiểm lại nguồn/điều khoản khi duyệt. Thay phân loại/rate sau duyệt hiện cảnh báo; snapshot cũ giữ nguyên. Kiểm backup/restore và trạng thái cũ thiếu trường mới.
- PO thử chọn tiền nguồn, duyệt chưa miễn giảm, điều chỉnh miễn giảm, xem hai phiên bản trên dữ liệu giả. Không ghi/duyệt dữ liệu thật khi thử. Không coi P06 hoàn thành toàn bộN3 (còn TRX/Energy và các giới hạn khác).

### P05 — Điều khoản lãi và bảng xem trước

- A38–A39: hai cách nhập tương đương; 100 triệu ×10 ngày =500.000; 300 triệu ×10 ngày +200 triệu ×5 ngày =2.000.000; 1,5 triệu ×10 ngày =7.500; 100 triệu ×31 ngày =1.550.000 VND tại đơn giá500.
- Hiện rõ quy ước xem trước gồm ngày đầu/không gồm ngày cuối, gốc trả giảm từ ngày trả, dư gốc cuối ngày và làm tròn tổng một lần. Có xác nhận quy ước; không nhận vơ đây là điều khoản đã chốt của dữ liệu thật.
- Đổi gốc/lãi suất chia đúng đoạn, nhiều phát sinh cùng ngày không cộng lãi lặp. Khoảng bắt đầu sau mốc gốc đầu vẫn tính đủ biến động trước khoảng. Kiểm biên và làm tròn bằng ca số.
- Thiếu thiết lập hoặc lãi suất không được thay bằng0. Số âm/không hữu hạn và dữ liệu gốc không hợp lệ bị chặn. Sổ cũ/backup/bản duyệt ngân hàng giữ nguyên; thay điều khoản có căn cứ và lịch sử.
- Xem trước không ghi sự kiện tài chính; lãi thực thu/chi hiện riêng, không tự gắn vào kỳ hay tự kết luận nợ/quá hạn. PO dùng UI thiết lập lãi và đối chiếu bảng trước phát hành.

### P04 — Công nợ theo người và từng khoản

- Một người có hai khoản cho vay và một khoản đi vay: hiện từng khoản, cộng phải thu/phải trả riêng. Thu gốc cho khoản thứ hai không giảm khoản thứ nhất.
- Gốc đầu 100 triệu, chi thêm 20 triệu, thu gốc 30 triệu: phải thu 90 triệu; thu lãi 1 triệu hiện riêng. Đi vay áp dụng chiều tiền ngược lại. Mỗi số truy về nguồn đã phân bổ.
- Hồ sơ cũ chưa thiết lập không hiện số không như dư nợ đã xác minh. Gốc đầu bằng không phải do người dùng xác nhận cùng ngày và căn cứ. Không tự tạo tiền ngân hàng từ thiết lập công nợ.
- Dữ liệu trước ngày bắt đầu, gốc âm, thiếu nguồn/phân loại không được che giấu. Không gọi lãi đã thu là lãi dự kiến hoặc tự kết luận quá hạn.
- Chỉnh thiết lập/phân bổ giữ lịch sử và snapshot cũ. Kiểm thử dữ liệu giả lập; PO dùng giao diện tạo/thiết lập hồ sơ, xem số dư và truy nguồn trước phát hành.

### P03 — Trạng thái ngân hàng có thể hiểu và hành động

- Tracking09/07, nguồn01/08–29/09: hiển thị khoảng09–31/07 chưa xác minh, kỳ nguồn và ngày cuối nguồn riêng; không đổi opening hoặc tạo tiền bù. Duyệt phải xác nhận khoảng này, snapshot giữ nhãn; chưa phân loại có xác nhận độc lập.
- Đã loại file không bị hướng dẫn nhập lại mù: mở được nguồn và đưa lại vào kiểm tra; blocked có thông báo/đường xử lý.
- Duyệt S1 rồi mở lại không có thay đổi: hiện đã cập nhật, không tạo S2 giống nội dung chỉ vì bấm lại/đổi ghi chú. Điều chỉnh phân loại hoặc nhập nguồn mới thay đổi nội dung thì hiện chưa duyệt và lưu được phiên bản mới với lý do, S1 bất biến.
- Phần tổng quan giữ dữ liệu nguồn đầy đủ không phụ thuộc bộ lọc; tài khoản lưu trữ read-only. Kiểm trên dữ liệu giả lập, không mutate tài khoản người dùng để test.
- Bằng chứng coder tại outputs/p03-handoff.md, PO review riêng; không mặc định có tester thứ hai cho đợt nhỏ này.

### P02 — Điều kiện bàn giao khả năng sử dụng tài khoản

1. Tạo sai tên/số/ngày/số đầu rồi sửa trước khi ghi giao dịch: giá trị mới được lưu sau restart; file chờ được kiểm lại, số tài khoản không mất số 0 đầu, không đổi tài khoản khác.
2. Sau khi có giao dịch/bản duyệt: sửa tên không đổi tiền/nguồn/S1; backend chặn sửa số đầu/mốc/số tài khoản, UI giải thích rõ các trường bị khóa.
3. Tài khoản rỗng: hủy xác nhận xóa không đổi gì; xác nhận xóa ẩn khỏi hoạt động; khôi phục lại đúng thông tin. Tài khoản có nguồn/tiền không thể bị xóa qua UI hoặc API.
4. Lưu trữ tài khoản có lịch sử giữ số, nguồn, phân bổ, snapshot; vẫn tra được, không chỉnh được. API chặn import/classify/transfer/approve khi lưu trữ; khôi phục hoạt động và restart giữ đúng trạng thái, không nhân tiền.
5. PO/QA đi trọn hành trình qua giao diện desktop/mobile: tạo sai→sửa→nhập→phân loại→duyệt→điều chỉnh→lưu trữ→khôi phục; thao tác tìm được không cần console hoặc hướng dẫn đường dẫn kỹ thuật.
6. Các bước nhập/phân loại/duyệt giữ dữ liệu khi chuyển tab; lọc chờ/đã xử lý có số đếm đúng, báo cáo toàn phạm vi; đổi tài khoản không giữ lựa chọn cũ. Ca hồi quy P01 tiếp tục đạt.

Kết quả09/10/2026: 11 ca backend P02 đạt, PO đã thực hiện hành trình UI desktop/mobile như ghi tại [PO-UI-REVIEW](outputs/p02-qa/PO-UI-REVIEW.md); cho cập nhật bản dùng thử phạm vi ngân hàng. Tester không claim kiểm UI độc lập khi công cụ của tester không có browser. Chi tiết và giới hạn nằm tại outputs/p02-qa; không mở rộng kết luận sang toàn bộ sản phẩm hoặc số tài chính thật.

**Kết quả 09/10/2026:** PO cho phát hành bản dùng thử giới hạn P01 trên dữ liệu giả lập riêng, dựa trên QA độc lập và review trải nghiệm. [Báo cáo QA](outputs/p01-qa/REPORT.md) ghi từng ca, bằng chứng và giới hạn; [hiện trạng](IMPLEMENTATION-STATUS.md) ghi quyết định bàn giao. Chưa coi toàn bộ N0–N5 đạt, chưa xác nhận dữ liệu tài chính thật. Có 10 ca backend ban đầu và 1 ca bổ sung nhập sai thứ tự đạt; kiểm UI chính desktop/mobile và phân trang đã thực hiện. Chuyển nội bộ và nút kiểm tra lại nguồn mới có bằng chứng backend, chưa kiểm trọn UI.

Thạch giao PO kiểm soát quy trình và trải nghiệm, tham gia như người dùng. Từ đây PO chốt phạm vi và quyết định bản đủ chất lượng để đưa dùng sau kiểm chứng QA; không bắt Thạch quản lý hoặc duyệt từng đợt phát triển. Các câu bên dưới yêu cầu Thạch xác nhận từng mốc là quy trình lịch sử, được thay bởi cơ chế này. Người dùng vẫn trực tiếp xác nhận sự thật tài chính và approve số liệu của mình. PO/QA chỉ approve trên dữ liệu thử khi kiểm tra. Chưa có mốc nào tự chuyển thành đạt vì thay đổi vai trò.

### P01 — Bài kiểm tra phát hành bắt buộc

| Mã | Thao tác và kết quả cần chứng minh |
|---|---|
| P01-01 | Tài khoản thử đầu 100 triệu; đợt một thu 20/chi 5 → 115 triệu; đợt hai chồng dòng cũ và thêm chi 3 → 112 triệu. Nhập lại không tăng số giao dịch/tiền, liên kết nguồn vẫn còn. |
| P01-02 | Hai dòng cùng ngày/cùng tiền nhưng tham chiếu khác không bị xóa; cùng tham chiếu cùng tài khoản khác tiền báo xung đột. File lỗi không ghi một phần vào lịch sử chính thức. |
| P01-03 | Nguồn lệch số dư không được duyệt. File chưa hỗ trợ báo rõ. Kỳ dữ liệu thể hiện đúng nguồn; không suy có hoặc không có giao dịch ngoài kỳ. |
| P01-04 | Tách chi 22 triệu thành gốc 20/lãi 2: vẫn một giao dịch chi 22; sai tổng hoặc sai hồ sơ bị chặn. Bulk chỉ tác động dòng được chọn; báo cáo gồm toàn đợt dù đang lọc/phân trang. |
| P01-05 | Duyệt còn chưa phân loại cần xác nhận, giữ nhãn chưa rõ. Sửa sau duyệt tạo S2 có lý do; S1 và chứng từ nguồn giữ nguyên, kể cả sau khởi động lại. |
| P01-06 | Tài khoản B không đổi khi import/phân loại A. Chuyển 10 triệu A→B giữ hai nguồn, không thành thu nhập/chi tiêu; thiếu đầu nhận hiện chờ đối ứng; không ghép một dòng hai lần. |
| P01-07 | Backup và restore vào bộ dữ liệu riêng giữ giao dịch, file nguồn, phân bổ, hồ sơ, lịch sử và snapshot; đối chiếu số lượng, số tiền và liên kết. Không ghi đè dữ liệu đang dùng. |
| P01-08 | Trên desktop/mobile: tự đi từ nhập file tới duyệt, đóng/mở lại, tìm giao dịch cũ và sửa phân loại; không cần sửa file dữ liệu hoặc dùng console. Nêu rõ bước bất tiện và lỗi còn lại. |

Tester phải ghi phiên bản hoặc hash mã kiểm tra, dữ liệu thử, bước thực hiện, kỳ vọng/thực tế và bằng chứng từng ca. Test bản mẫu trước đây không thay thế kiểm tra P01 trên ứng dụng lưu bền vững. PO chỉ cho đưa dùng khi không còn lỗi sai tiền, trùng tiền, mất nguồn, thay snapshot cũ hoặc mất dữ liệu; chức năng chưa kiểm phải ghi chưa kiểm.

## 1. Định nghĩa hoàn thành — DoD

Mốc chỉ hoàn thành khi phạm vi được Thạch xác nhận, các tình huống liên quan chạy đạt trên dữ liệu thử có kết quả kỳ vọng, có bằng chứng và giới hạn rõ, không còn lỗi sai tiền/nhân đôi/mất dấu nguồn trong phạm vi, và Thạch xác nhận kết quả sử dụng. Thạch là người dùng hiện tại trực tiếp approve số liệu. “Code xong”, “test qua”, “bàn giao” không đồng nghĩa nghiệm thu.

Ghi phiên bản, bộ dữ liệu, ngày chạy, kết quả từng ca, lỗi còn lại, người và nội dung xác nhận. Dữ liệu giả lập không chứng minh số dư thật đúng.

## 2. Mốc hiện hành — đề xuất cho review thiết kế

| Mốc | Kết quả bàn giao | DoD người dùng kiểm chứng | Ca tham chiếu |
|---|---|---|---|
| N0 — Duyệt thiết kế | Bản mẫu, sơ đồ màn hình, phạm vi/giả định và kế hoạch | Thạch đi qua bốn luồng mẫu, xác nhận hướng thiết kế và phần hoãn; các điểm cần quyết định được ghi rõ | PRODUCT-SPEC mục 8 |
| N1 — Tin được tài khoản | Khai báo không mục đích; import/kiểm tra/phân loại và toàn lịch sử trong tài khoản | File mẫu hợp lệ ra số dư đúng; nhập lại không tăng tiền; file chồng chỉ thêm giao dịch mới; lỗi có vị trí/nguồn; khoản chưa rõ vẫn hiện đúng biến động. Kiểm soát thiếu lịch sử và mốc nguồn | A01–A06, A18 |
| N2 — Duyệt và điều chỉnh | Thạch approve đợt dữ liệu, giữ nhãn chưa rõ; lưu phiên bản và nguồn | Mở lại S1 sau S2 vẫn giữ dữ liệu cũ; S2 có lý do/quyết định và trước/sau; không ghi trùng tiền. Phiên bản lưu bền vững, khởi động lại vẫn đúng | A11–A13, A16–A17, A12 |
| N3 — Công nợ và TRX/Energy | Từng món vay hai chiều, tính lãi ngày, giảm lãi; bảng kê khách Energy/TRX và tiền thanh toán | Trả món mới không giảm món cũ; trả một phần đổi dư gốc; lãi dự tính/thực thu/miễn giảm riêng. Thu chung/thu thiếu/thu nhiều đợt VND hoặc USDT ra đúng nợ; tỷ giá cũ giữ nguyên. Không quản gia hạn | A07–A08, A23–A25, A28–A39 và giới hạn R41 |
| N4 — Tài sản và nơi giữ | BĐS quyền lợi/góp vốn/thế chấp/tiến độ; crypto theo mốc và nơi giữ, đủ nhóm nghiệp vụ đã chọn | Đầu mốc có nguồn; chuyển nội bộ không nhân tài sản; BĐS không cộng trùng nợ/quyền lợi; từng loại spot/futures/margin/staking/Earn có dữ liệu mẫu và ca số kỳ vọng. Không nghiệm thu bằng trang tĩnh | A14–A15, A19–A21, A27/A29, phần tài sản của A10 |
| N5 — Dùng thử trọn luồng | Báo cáo giá hiện tại/tỷ trọng/truy nguồn, hướng dẫn và backup/restore | Thạch tự đi từ dữ liệu đầu vào đến báo cáo/snapshot và điều chỉnh. Tổng khớp chi tiết, phần thiếu hiện rõ, giữ đơn vị tiền. Thử khôi phục vào bộ dữ liệu riêng, số và liên kết khớp. Thạch xác nhận nghiệm thu | A10, A12 và chuỗi N1–N4 |

**Hiện tại:** mới bàn giao thiết kế N0; chưa nghiệm thu N0 hoặc triển khai N1–N5 theo bộ mới. Mỗi mốc cần bằng chứng theo mục 1, không chỉ “code xong”.

**Pending ngoài bản đầu:** shop (A09/A22/A26), cổ phiếu (phần tương ứng A14), khóa sổ tháng. Các đoạn bổ sung bên dưới là lịch sử phát triển tiêu chí, không được đưa phần pending trở lại phạm vi. Bảng N0–N5 tại mục này thay các nhắc “N3 dùng thử cuối” trong ghi chú trước đó.

**Điểm chốt theo mốc:** N1 chính sách lệch/thiếu nguồn; N3 biên ngày/làm tròn và giá vốn/thưởng TRX; N4 giá, FX, futures/margin, quyền lợi chung cư; N5 mẫu số tỷ trọng. Không chặn review N0 vì chưa chốt hết, nhưng phải có quyết định và ca số trước dùng thật ở mốc liên quan.

## 3. Tình huống nghiệm thu đề xuất

Toàn bộ số dưới đây là giả lập. Kỳ vọng chi tiết phải được chốt tại N0.

| Mã / yêu cầu | Cách thử | Kết quả mong đợi |
|---|---|---|
| A01 / R01–R03 | Tạo ngân hàng VND và sàn USDT | Không mục đích bắt buộc; có tracking; import trong tài khoản; giữ nguyên tệ |
| A02 / R03–R04 | Đầu 100 triệu; nhập thu 20, chi 5; nhập lại file; file chồng có thêm chi 3 | Lần đầu 115, nhập lại vẫn 115, thêm dòng mới còn 112; truy được xử lý từng dòng |
| A03 / R04 | Hai giao dịch hợp lệ cùng ngày/cùng tiền, mã nguồn mâu thuẫn và dòng sai số dư | Không xóa nhầm, không âm thầm nhận mâu thuẫn; xử lý đúng chính sách file lỗi đã chốt |
| A04 / R04–R05 | Nhập file mới rồi file cũ, mở lịch sử tracking → hôm nay | Không đặt lại số dư đầu; đúng thứ tự; thấy nguồn tới đâu và phần thiếu; không giả vờ đủ dữ liệu tới hôm nay |
| A05 / R04–R05 | Chuyển 10 triệu giữa tài khoản của mình, hai đầu khác ngày | Đúng tiền/ngày mỗi đầu; không thành thu nhập/chi tiêu; chỉ rõ đầu chưa ghép và phí |
| A06 / R06 | Chi 22 triệu gồm gốc 20/lãi 2, rồi sửa phân loại | Một lần chi 22 trên nguồn; tổng phần khớp; giữ trước/sau; có nơi quản lý danh mục và đối tượng |
| A07 / R07 | Vay A hai món 100/50 triệu, B/C/D 20/30/40; trả 10 gốc món đầu của A | Tổng gốc 230 triệu; A 140 gồm 90/50; B/C/D không đổi; mở được từng giao dịch |
| A08 / R07, R09 | Thêm cho A vay 15 triệu và một khoản vay 100 USDT | Phải thu 15 riêng; nợ VND/USDT riêng; không bù trừ/cộng khác tiền; tách gốc/lãi |
| A09 / R08 | Chi 30 triệu cho nhà cung cấp Shop A | Thấy shop, nhà cung cấp, nguồn và chứng từ; công nợ/tồn kho/lợi nhuận chỉ kiểm theo mức đã chốt |
| A10 / R09, R11 | Xem báo cáo ngày/khoảng ngày và mở số tổng | Thấy thành phần, đơn vị, trạng thái; không coi FX demo là số đã xác nhận; bổ sung ca từng nhóm tài sản sau N0 |
| A11 / R10, R12 | Thạch xem tóm tắt phân loại và approve | Ghi đúng người thao tác và thời điểm duyệt; không dùng tên Dũng mặc định |
| A12 / R04, R12 | Sửa phân loại, mở nguồn, sao lưu/khôi phục vào dữ liệu thử riêng | Không mất nguồn/lịch sử, không nhân đôi; khôi phục khớp số và liên kết; không ghi đè dữ liệu đang dùng để thử |

## 4. Biên bản

**Chưa có mốc N0–N5 hoặc ca nghiệp vụ nào được người dùng nghiệm thu theo bộ mới.** Đây là thiết kế kiểm chứng, không phải kết quả test.

Mẫu: `Mốc / phiên bản / bộ dữ liệu / ca đạt-không đạt / bằng chứng / tồn tại / người xác nhận / ngày / kết luận`. Ghi biên bản và trạng thái trong [IMPLEMENTATION-STATUS](IMPLEMENTATION-STATUS.md), không tạo bảng tiến độ cạnh tranh.

## 5. Bổ sung sau câu trả lời I1 — dự thảo kiểm chứng

| Mã / yêu cầu | Cách thử đề xuất | Kết quả cần chốt trước triển khai |
|---|---|---|
| A13 / R14, R17 | Nhập và phân loại một đợt ba ngày; xem tóm tắt rồi approve; thực hiện đợt tiếp theo | Mỗi lần approve lưu snapshot riêng theo thời điểm duyệt, không phụ thuộc lịch tuần. Có bước xem tóm tắt trước duyệt. Đề xuất hiển thị riêng ngày cuối nguồn, đối chiếu được giao dịch/phân loại/số dư của từng bản; trường snapshot cần chốt. Thạch duyệt; điều chỉnh giữ bản cũ, có quyết định và lý do. Chốt tháng pending, không bắt buộc trong bản thử |
| A14 / R15, R18 | Mở riêng BĐS/coin (cổ phiếu hoãn phase sau); ví dụ giả lập vốn 1 tỷ, giá hiện tại 1,2 tỷ | Hiển thị riêng cả 1 tỷ và 1,2 tỷ; tỷ trọng dùng giá hiện tại. Mẫu số, nguồn/ngày giá, FX và vốn khi bán một phần chờ chốt; truy được thành phần |
| A15 / R16, R19 | Xây bộ mẫu cho mua/bán, chuyển tiền, futures, margin, staking và Earn | Có ca cho từng loại; chốt kết quả kỳ vọng trước triển khai, bao gồm vị thế mở, vay, phí, phần thưởng và nơi giữ khi liên quan. Chưa có mẫu sàn hoặc công thức được xác nhận; không coi tất cả đã hỗ trợ |

N3 cần bao gồm bước khóa sổ và A13–A15 khi chốt phạm vi. Chưa có kết quả chạy hoặc nghiệm thu các ca mới; không suy ra mọi loại nghiệp vụ sàn đã nằm trong lần bàn giao tới.

## 6. Bổ sung 30/09 — approve chưa phân loại và điều chỉnh

| Mã / yêu cầu | Cách thử | Kết quả kỳ vọng |
|---|---|---|
| A16 / R20 | Số dư khớp, còn một khoản chi 10 triệu chưa rõ; Thạch approve | Cho approve, snapshot giữ nhãn và khoản chưa phân loại. Đề xuất báo cáo hiển thị tiền ra chưa rõ 10 triệu, không tự tính thành chi tiêu hoặc đầu tư; cảnh báo các số nghiệp vụ chưa đầy đủ |
| A17 / R21 | Snapshot S1 đã duyệt; xác định khoản 10 triệu là trả gốc và tạo bản điều chỉnh | S1 không đổi; bản mới kèm quyết định, lý do và liên kết bản cũ. Đề xuất xem trước/sau, duyệt lại và không cộng S1 với bản mới |
| A18 / đề xuất đối soát | Số đầu 100, thu 20, chi 5, số cuối nguồn 114 triệu | Hiện số tính 115, lệch 1 triệu, truy vị trí/nguyên nhân; không tạo khoản cân tự động. Đề xuất chỉ lưu nháp và chặn approve cho tới xử lý; quy tắc này chưa được người dùng chốt |

A16–A18 chưa được chạy hoặc nghiệm thu. Chốt tháng là pending theo R22 và không nằm trong điều kiện bắt buộc của N3 hiện tại. Chi tiết cơ chế đối soát còn cần xác nhận.

## 7. Phạm vi nơi giữ tài sản — 30/09/2026

Binance, BingX đều dùng cùng nhóm trade/lưu trữ/Earn theo R23 mới. A15 vẫn cần mẫu thực cho từng sàn và sản phẩm cụ thể. Ví riêng khởi đầu bằng danh sách coin theo ví.

A19 (đề xuất, R23): chuyển coin từ sàn sang ví riêng rồi giữa hai nơi giữ thuộc Thạch; liên kết hai đầu, ghi đúng lượng gửi/nhận và phí theo đồng thực tế, không tạo thu nhập/chi tiêu hoặc tài sản trùng. Số ví, mạng, nguồn và quy tắc chuyển khác mạng còn phải phỏng vấn. Chưa chạy hoặc nghiệm thu.

R24: mọi ca quản lý danh mục cổ phiếu hoãn phase sau. Nếu sao kê hiện tại có dòng liên quan cổ phiếu, cách phân loại tạm vẫn cần làm rõ, không tự bỏ dòng sao kê.

## 8. Khởi tạo theo mốc — dự thảo nghiệm thu

A20 / R25–R26: tại mốc được chọn, khai báo các ví với coin/số lượng; khai báo sàn với các thành phần đầu mốc cần thiết. Kiểm không tính số đầu là thu nhập/mua mới, không đếm trùng Earn/ký quỹ với tổng tài khoản; vốn chưa biết hiển thị chưa xác định, không giả lập bằng giá thị trường. Sau mốc, phát sinh được theo dõi tiếp. Mẫu số, vị thế/nợ đầu mốc và nguồn cần chốt trước chạy ca này. Không yêu cầu lịch sử trước mốc chỉ để bắt đầu theo dõi. Chưa chạy hoặc nghiệm thu.

## 9. BĐS, Shop, Cho vay — ca đề xuất sau xác nhận R27–R29

- A21 / R27: tạo tài sản sở hữu toàn bộ, hai tài sản góp vốn với quyền lợi có nguồn, liên kết một khoản vay thế chấp, một hợp đồng chung cư theo tiến độ. Kiểm vốn đã bỏ vào, phần quyền lợi, giá trị và lịch còn phải trả; không nhân đôi tài sản/nợ. Các loại có thể giao nhau, không tự suy tổng số tài sản. Công thức tổng hợp cần chốt.
- A22 / R28: ví dụ giả lập nhận hàng 100 triệu, trả nhà cung cấp 60, bán phần có giá vốn 30 với doanh thu 45, chi phí 5; không có tồn đầu, trả lại hay thuế trong ví dụ. Phải trả còn 40, tồn hàng theo giá vốn 70, lợi nhuận quản trị trước thuế 10. Tiền khách thực trả theo dõi riêng. Đây là ca đề xuất, chưa chốt phương pháp giá vốn hoặc dữ liệu shop thực.
- A23 / R29: ví dụ giả lập một khoản 100 triệu trọn kỳ tháng, gốc không đổi, lãi đơn 1,5%: lãi kỳ 1,5 triệu. Thu 21,5 triệu với phân bổ được xác nhận 20 gốc/1,5 lãi thì gốc còn 80, lãi thu 1,5, tiền vào 21,5; không coi 21,5 là doanh thu. Lãi kỳ sau, trả giữa kỳ, trả thiếu/quá hạn cần thêm ca sau khi chốt điều khoản. Chưa chạy/ nghiệm thu.

Ca A09 nay phải đáp ứng nhu cầu công nợ và lợi nhuận đã xác nhận, không chỉ gắn nhãn Shop vào tiền chi. Nguồn hàng bán/tồn và phạm vi phải thu khách vẫn cần phỏng vấn.

## 10. Vay nhiều khoản, trả trước một phần và shop tối giản

- A24 / R30: cùng người vay hai khoản 100 triệu, ngày 20 và ngày 30. Thu đủ gốc/lãi khoản ngày 30 theo phân bổ xác nhận: khoản ngày 20 còn nguyên; khoản ngày 30 chỉ tất toán khi mọi nghĩa vụ được xử lý. Không tự FIFO giữa các khoản.
- A25 / R31: khoản gốc 300 triệu, trả 100 triệu gốc và lãi còn phải thu tới mốc trả. Gốc mới 200 triệu, lãi tương lai theo 200; không thu lặp phần lãi đã trả. Ca ngày lẻ chỉ chạy khi quy ước được chốt. Một chuyển khoản chia nhiều món phải khớp tổng nguồn; thiếu tiền không tự tất toán.
- A26 / R32 (thiết kế đề xuất): tồn đầu 0, nhận 10 sản phẩm giá 1 triệu, trả nhà cung cấp 6 triệu; bán 3 sản phẩm doanh thu 4,5 triệu và thu đủ; chi phí 0,5 triệu. Không thuế/hoàn trả trong ví dụ: tồn 7 sản phẩm giá vốn 7 triệu, phải trả 4 triệu, lãi gộp 1,5 triệu, lãi sau chi phí trước thuế 1 triệu. Phải truy được chứng từ và tiền thanh toán. Không nhân đôi khi nhập sao kê đã có giao dịch thanh toán.

Chưa chạy hoặc nghiệm thu A24–A26. Quy ước ngày lẻ, ngày thu, miễn/giảm lãi và chi tiết shop còn cần hoàn thiện trước triển khai.

## 11. Cập nhật phạm vi: shop pending, hoạt động stake tạo sản phẩm

Theo yêu cầu mới, phần shop của N2, A09/A22/A26 và các điều kiện liên quan shop được HOÃN; giữ làm tham khảo, không chặn nghiệm thu bản đầu. Dòng tiền sao kê liên quan shop vẫn được lưu/phân loại trong luồng tài khoản chung; không loại bỏ dữ liệu.

A27 / R33 — dự thảo sau làm rõ sản phẩm: từ một vị thế coin stake có nguồn, ghi quyền lợi từng kỳ; sản phẩm bán/thuê gắn đúng khách và tiền; kiểm không cộng trùng coin gốc, không ghi cùng quyền lợi hai lần, không biến thu hồi cọc thành doanh thu. Mở lại snapshot cũ không đổi khi bổ sung dữ liệu sau. Chưa có mẫu, công thức giá vốn/doanh thu hoặc số kỳ vọng; ca này chưa sẵn sàng triển khai/chạy/nghiệm thu.

## 12. Làm rõ TRX/Energy — thay mô hình sản phẩm chung ở A27

A27 được cụ thể hóa theo R33–R34: không có kho sản phẩm Energy tích lũy theo tháng; lưu đơn thuê và trạng thái ủy quyền thực tế. Thu hồi ủy quyền không phải mua lại TRX và thuê không làm giảm quyền sở hữu coin gốc. Chưa chốt cách đo năng lực/giá và nguồn thực tế.

A28 (đề xuất): đơn giả lập thuê Energy 20 USDT, bán 100 TRX với tổng giá 30 USDT; khách chuyển 50 USDT một lần. Ghi tiền vào 50 đúng một lần, phân bổ thuê 20/bán TRX 30, giảm 100 TRX khi có chứng từ giao; không gọi 50 hoặc 30 là lợi nhuận. Nếu khách trả 40 thì còn phải thu 10, phân bổ từng dòng có căn cứ, không tự giả định đã trả đủ dòng nào. Phí riêng nếu có.

A29 (đề xuất): xác nhận thưởng 10 TRX có thể claim rồi claim 10 vào ví: quyền nhận chuyển sang coin đã nhận, không thành 20 TRX hoặc thu nhập hai lần. Nếu dữ liệu chỉ có claim thì ghi nhận theo nguồn đó, không tự dựng thưởng chưa claim bằng APY. Giá vốn/định giá thưởng cần chốt trước nghiệm thu lợi nhuận.

Các ca chưa chạy/nghiệm thu; không tự thực hiện giao dịch on-chain.

## 13. Hai loại đơn Energy và thu VND/USDT

- A30 / R35: tạo đơn lẻ theo lượng Energy và gói 1 triệu Energy/tháng; giữ riêng kỳ dịch vụ, thực cấp/thu hồi, trạng thái tiền. Chưa chốt ý nghĩa lượng tháng nên chưa thể nghiệm thu quy tắc hạn mức/hoàn tất; không tự quy gói tháng thành kho 1 triệu Energy hoặc hạn mức mỗi ngày.
- A31 / R36 (đề xuất): đơn 100 USDT, thỏa thuận 25.000 VND/USDT, nhận 2.500.000 VND: ngân hàng tăng VND, phải thu giảm 100 USDT, không tăng ví USDT. Kiểm tiền nhận liên kết nguồn đúng một lần. Không có tỷ giá thỏa thuận thì chưa tự phân bổ/tất toán; giá trị danh mục quy đổi sau không sửa khoản đã tất toán. Tỷ giá chỉ là dữ liệu thử, chưa phải quyết định người dùng.

Chưa triển khai/chạy/nghiệm thu A30–A31; trả trước/sau và cơ sở quy đổi còn hỏi tiếp.

## 14. Phí cố định gói tháng và khách trả trước/sau

A32 / R37–R38: cùng gói tháng theo giá/đơn vị được xác nhận, một khách sử dụng và một khách không sử dụng, nếu dịch vụ vẫn cung cấp đúng thỏa thuận thì phí hợp đồng không tự giảm theo lượng đã dùng. Không suy 100 USD = 100 USDT; đơn ghi rõ đơn vị.

A33 / R38 (đề xuất): khách trả trước ghi tiền nhận và dịch vụ còn phải cung cấp; khách trả sau có gói đang chạy nhưng chưa nhận tiền, hạn trả riêng. Chỉ đánh dấu quá hạn sau ngày đến hạn đã thỏa thuận. Không suy thu tiền = hoàn tất dịch vụ hoặc giá trị hợp đồng = lợi nhuận. Snapshot giữ điều khoản đơn, sau khi sửa cấu hình khách không làm thay bản đã duyệt. Chưa chạy/nghiệm thu; ngày tính kỳ, ngày đến hạn và phân bổ doanh thu còn mở.

## 15. Tỷ giá tại từng lần thanh toán — R39

Cập nhật A31: thời điểm quy đổi đã chốt là lúc thanh toán. A34 (đề xuất): nợ 100 USDT, trả 50 USDT tương đương 1.250.000 VND ở tỷ giá 25.000; lần sau 50 USDT tương đương 1.300.000 VND ở 26.000. Còn nợ 0 USDT, ngân hàng nhận tổng 2.550.000 VND, không tăng ví USDT, không tính lại lần trước ở tỷ giá mới. Các tỷ giá là số thử, nguồn nhập/kiểm tỷ giá và quy tắc làm tròn chưa chốt. Chưa chạy/nghiệm thu.

## 16. Thu gộp nhiều kỳ không định kỳ — R40

A35 (đề xuất): ba kỳ dịch vụ đã được xác nhận, mỗi kỳ 100 USDT, chưa thu; bảng kê khách hiện từng kỳ và tổng 300. Nhận 200 USDT một lần, xác nhận phân bổ vào hai kỳ thì còn 100; không ghi nhận tiền về các tháng trước. Không gắn quá hạn chỉ vì người dùng chưa đi thu khi chưa có hạn cam kết. Không tự gia hạn/sinh phí kỳ thứ tư nếu chưa có căn cứ tiếp tục dịch vụ. Không yêu cầu khóa tháng để lập công nợ hoặc thu gộp. Chưa chạy/nghiệm thu.

## 17. Loại gia hạn Energy khỏi phạm vi — R41

Phần quyết định gia hạn/tiếp tục cấp/thu hồi trong các ca đề xuất trước không thuộc nghiệp vụ PCMS. A35 chỉ dựa trên các khoản phí người dùng đã nhập/xác nhận, không tự tạo kỳ thứ tư hoặc đòi hỏi thao tác gia hạn. Vẫn kiểm tổng công nợ, tiền thu, phân bổ và snapshot; thời hạn trên khoản thuê chỉ là thông tin tài chính. Chưa triển khai/chạy/nghiệm thu.

## 18. Lãi ngày và miễn/giảm — R42

A36 (đề xuất): trên cùng khoản/khoảng ngày, lãi dự tính 1,5 triệu, thực thu 1,2 triệu. Không có quyết định miễn thì còn 0,3 triệu chưa thu; có quyết định giảm 0,3 triệu kèm lý do thì phần lãi còn phải thu bằng 0. Gốc không đổi; báo cáo thực thu 1,2 triệu. Không gọi khoản chưa thu là quá hạn nếu chưa có hạn trả, không ghi tiền giảm thành tiền nhận.

A37 (đề xuất): điều chỉnh giảm lãi sau snapshot tạo phiên bản mới và quyết định/lý do, bản cũ giữ nguyên. Giao dịch thu cũ không được ghi lần hai. Ca tính ngày bắt đầu từ giải ngân được xác nhận; số ngày kết thúc/hệ số /30/làm tròn phải chốt trước kiểm công thức. Chưa chạy/nghiệm thu.

## 19. Công thức lãi ngày được xác nhận — R43

A38: nhập 500 VND/triệu/ngày hoặc 1,5%/tháng 30 ngày cho cùng khoản VND phải cho kết quả tương đương, không cộng lãi hai lần. Gốc 100 triệu trong 10 ngày: 500.000 VND; gốc 300 triệu trong 10 ngày rồi 200 triệu trong 5 ngày: 2.000.000 VND tổng lãi dự tính. Số ngày các đoạn được cung cấp rõ trong ca này, không ngầm chốt biên ngày trả.

A39: gốc 1,5 triệu trong 10 ngày: 7.500 VND, không làm tròn gốc xuống 1 triệu. Gốc 100 triệu trong 31 ngày: 1.550.000 VND, không ép thành lãi 30 ngày. Lãi thực thu và miễn giảm vẫn kiểm theo A36; không tự vốn hóa lãi. Biên ngày/nhiều lần trả cùng ngày/làm tròn cần thêm ca sau chốt. Các ca chưa chạy/nghiệm thu; đề xuất /30 chưa chốt trong ghi chú lịch sử trước đã được R43 thay thế.

## 20. Bằng chứng kiểm tra bản mẫu — tách khỏi nghiệm thu sản phẩm

Bản mẫu [index.html](outputs/design-review-v1/index.html) và tập kiểm tra [check.cjs](outputs/design-review-v1/check.cjs) chỉ kiểm tương tác thiết kế. Kết quả được ghi tại IMPLEMENTATION-STATUS sau khi chạy. Các chức năng chưa có: đọc XLSX thật, lưu dữ liệu bền vững, sổ tài chính tích hợp giữa các kịch bản, engine futures/margin và kết nối giá/chuỗi. Không dùng các screenshot hoặc kiểm tra bản mẫu để đánh dấu N1–N5 hoàn thành.

## 21. Review bản mẫu 02 — tiêu chí bổ sung R44–R48

- A40 / R44: chọn từng tài khoản; số dư/mốc đã duyệt và lịch sử 7 ngày thuộc đúng tài khoản. Xem toàn bộ vẫn có dòng cũ. Import/snapshot một tài khoản không đổi tài khoản khác. Bộ lọc không thay số dư đầu.
- A41 / R45: chọn 5 hoặc 10 dòng, áp danh mục; chỉ dòng được chọn thay đổi, số tiền không đổi. Chọn hết phải nói rõ phạm vi đang hiện. Đổi tài khoản không mang lựa chọn cũ. Không cho sửa trực tiếp bản đã duyệt.
- A42 / R46: đợt 50 mã nguồn gồm 20 chi tiêu, 5 cho vay của 3 người và các nhóm còn lại. Tổng nhóm đủ 50, vào 71 triệu/ra 597 triệu, dư cuối 974 triệu từ đầu 1,5 tỷ. Mở mọi nhóm thấy mã/ngày/tiền/đối tượng. Lọc 5 dòng chưa rõ rồi đổi sang chi tiêu, báo cáo vẫn 50, chi tiêu 25, tiền không đổi. Kiểm đếm mã duy nhất và tiền vào/ra riêng; phần tách khoản cần kiểm riêng ở bản vận hành.
- A43 / R47: danh sách 3 người; An 2 món tổng 260 triệu được cấu thành từ lịch sử 4 giao dịch. Thu 10 triệu gốc món A-02, An còn 250 và lịch sử 5 dòng; A-01 còn 200, người khác không đổi. Các số nhập 10000000 hiện 10.000.000 và được tính đúng, không đọc thành 10.
- A44 / R48: danh sách có khách/gói/công nợ. Chưa chọn khách không có biểu mẫu thu không rõ người. Thu cho Minh không đổi nợ Lan/Huy; chuyển khách không mang tiền, nguồn hoặc phân bổ cũ. Lịch sử khoản thu có tên và mã khách, ngày, tiền gốc, tỷ giá, dòng được trả. Mỗi lần thu USDT/VND được đếm một lần.

Ánh xạ mốc: A40–A42 vào N1/N2; A43–A44 vào N3. Kiểm tra bản mẫu không thay nghiệm thu lưu trữ, file thật hoặc sổ tích hợp của các mốc này.

## 22. Review 03 — A45–A49

- **A45:** nhập 50 dòng mới không trộn vào bảng lịch sử cũ; có điểm nối số dư, so từng dòng, lọc 3/6/12 tháng và thông báo phạm vi nguồn. Ca thiếu/lệch nguồn phải hiện chênh lệch; không suy thiếu chỉ vì vài ngày không giao dịch.
- **A46:** Cho vay chọn An/A-02, đổi người xóa món cũ; Mua BĐS chọn Đất B. Thiếu liên kết không được duyệt dưới nhãn đã phân loại; chuyển Chưa phân loại thì được. Liên kết được giữ trong snapshot. Đổi danh mục không giữ đối tượng sai loại.
- **A47:** báo cáo trước duyệt là màn riêng, quay về sửa được, không mất đợt; toàn bộ số dòng/tiền và drill-down vẫn đủ.
- **A48:** từ từng món mở được chứng từ sao kê gốc và thông tin phân bổ. Chứng từ mẫu ghi rõ giả lập, tải phiếu mẫu được. Dòng nhập tay hiện chưa có nguồn, không giả làm sao kê.
- **A49:** lọc người đã hoàn thành; xem lại món/chứng từ; tuần/tháng/quý gồm lãi thu của cả món tất toán. Ví dụ tháng 09: lãi thu 2,7 triệu, phí mẫu 0,2 triệu, chênh 2,5 triệu; không kết luận lãi ròng khi thiếu chi phí. Hết gốc chưa tự tất toán; cần không còn lãi phải thu và xác nhận có căn cứ.

A45–A47 thuộc N1/N2; A48–A49 thuộc N3. Kiểm tra bản mẫu không thay nghiệm thu dữ liệu và sổ vận hành.

## 23. Review 04 — A50–A53

- **A50 (N1):** tạo tài khoản với số dư 123.456.789; sửa tên/định danh vẫn giữ số dư, không có ô sửa số dư sau tạo. Tài khoản mới rỗng; không tự thêm sao kê giả khi nhập.
- **A51 (N1/N2):** tạo Mua BĐS → Đất E, đổi tên Đất F, dùng ngay khi phân loại và gắn tài sản. Ngăn danh mục vòng lặp/tên trùng; bản duyệt không bị đổi theo tên mới. Mẫu quản lý cấu trúc, chưa thay hồ sơ BĐS đầy đủ.
- **A52 (N2):** mở chi tiết Chi tiêu thấy tổng vào/ra/chênh và đơn vị ở đầu danh sách; tổng bằng toàn bộ dòng trong nhóm.
- **A53 (N1/N2):** chưa nạp ngân hàng nhận thì chờ đối ứng; nạp đủ hai bên mới gợi ý cặp chi/thu cùng tiền và nguyên tệ. Xác nhận không thêm/xóa nguồn, không dùng lại dòng đã ghép. Không đổi phân loại của dòng đã ghép nếu chưa hủy liên kết. Sau approve không hủy ghép trực tiếp; snapshot giữ mã cặp. Lệch tiền/khác nguyên tệ chưa tự ghép hoặc tự sinh phí.

### A54 — Truy nguyên số tổng ở mọi danh mục (N1/N4)

- Trước nhập đợt mới: Đất A có 3 giao dịch tổng ra 600 triệu, lần lượt 200/150/250 triệu; mở dòng 150 triệu thấy đúng mã FT-DEMO-DATA-2 và vị trí nguồn.
- Các dòng xuất hiện ở lịch sử tài khoản và danh mục từ cùng nguồn, không cộng thêm tiền khi mở hồ sơ.
- Sau nhập đợt mới: thêm 3 dòng 100 triệu thì tổng nguồn Đất A thành 900 triệu; trạng thái mới chưa duyệt phân biệt với cũ.
- Mọi danh mục có lịch sử, cả rỗng. Danh mục cha gồm các dòng con nhưng đếm mỗi dòng một lần, tách nguyên tệ. Không có nguồn thì báo thiếu thay vì trình bày số vốn nhập tay là đã đối chiếu.

### A55 — Chuẩn nguồn nhiều bank (N1/N2)

Giữ nguyên file và ô nguồn; chuẩn hóa mẫu (44) đủ 163 dòng, tổng vào/ra và số dư khớp từng dòng. Ngày không có giờ phải hiển thị Không có trong nguồn, không giả 00:00 hoặc giờ nhập. Mã tham chiếu giữ nguyên chuỗi. Nhập lặp/chồng kỳ không tăng tiền nhưng giữ liên kết nguồn; cùng mã khác tài khoản không tự gộp; cùng mã cùng tài khoản nhưng khác số tiền phải báo xung đột. Phân loại/tách gốc-lãi không thay dòng nguồn. Xuất phiếu đúng giao dịch, có vị trí nguồn, không chứa giao dịch khách khác và không tự gửi. Ca này mới kiểm tra đọc file; chuẩn lưu trữ/xuất chứng từ chưa triển khai.

### A56 — Bản mẫu 05 theo mô hình đã chốt

Nạp file (44) đủ 163 dòng, tất cả chưa phân loại; nạp lặp không tăng dòng. Mở A9:F9 đúng FT[mã giao dịch đã ẩn], tiền ra 39.000, không có giờ. Phiếu tải chỉ chứa giao dịch đã chọn. Tạo người/hồ sơ, phân bổ đúng loại và chiều; tổng phần sai bị chặn. Long Debt/Bad Debt dùng cùng hồ sơ, đổi thu hồi không đổi gốc. Báo cáo tổng nguyên tiền nguồn, phần phân bổ không tăng số giao dịch gốc. Snapshot S1 giữ nguyên khi tạo S2 có lý do. Kiểm tra nguồn thật không đồng nghĩa phân loại thử là sự thật nghiệp vụ.

### A57 — Giai đoạn và trạng thái

Sau nạp chưa có bảng phân loại; chưa xác nhận nhập liệu thì không approve. Xác nhận nguồn khớp mới sang phân loại, không nhập thay nguồn. Trang 20 dòng. Bulk 3 dòng và lưu riêng 1 dòng tạo đúng 4 Đã phân loại/159 Chưa phân loại, tự rời nhóm chờ. Lọc/trang không cắt báo cáo 163 dòng. Duyệt với phần chưa phân loại cần xác nhận; snapshot không đổi nhãn thành đã phân loại, các ô sửa bị khóa. Kiểm trên desktop/mobile.
