# PCMS — Bàn giao tiếp quản cho Claude

Cập nhật11/10/2026 sau phát hànhP07. Đây là tóm tắt trạng thái có bằng chứng, không thay đặc tả. Không có triển khai đang chạy cần chờ agent cũ; chưa bắt đầu đợt tiếp theo. Không cần kế thừa công cụ/session/chat của Codex.

## 1. Vai trò và cách làm đã thống nhất

- Chủ sản phẩm sử dụng/duyệt trong app là **Thạch**. Người dùng muốn chỉ dùng sản phẩm và feedback. Assistant chịu trách nhiệm PO + người dùng đại diện: ưu tiên, giao coder, kiểm trải nghiệm/nghiệm thu và phát hành. Không buộc người dùng chọn tiểu tiết triển khai; không tự quyết định hoặc ký xác nhận dữ liệu tài chính thật thay họ.
- Bám tài liệu đã thống nhất. Phân biệt yêu cầu đã xác nhận với đề xuất/chưa chốt và bằng chứng mới chỉ ở bản mẫu.
- Tiết kiệm usage: một coder với ngữ cảnh gọn cho đợt vừa phải, PO tự review. Không đọc toàn bộ lịch sử, không tạo nhiều agent hoặc chạy rộng/lặp tests không có lý do. Người dùng đã phản ánh chi phí usage cao.
- Chỉ báo hoàn thành khi có mã chạy, kiểm tra phù hợp và PO dùng thử. Chưa nghiệm thu tổng thể thì nói rõ; không lấy số tests làm bằng chứng đủ trải nghiệm.

## 2. Nguồn sự thật và thứ tự đọc

1. `PRODUCT-SPEC.md`: yêu cầu hiện hành; Rxx là mã tham chiếu. P03–P07 ở đầu là quyết định triển khai; đọc mục nghiệp vụ liên quan khi làm tiếp.
2. `ACCEPTANCE.md`: tiêu chí Axx, Pxx và mốc N0–N5. Không đánh đồng một đợtP với toàn bộ mốcN.
3. `IMPLEMENTATION-STATUS.md`: kết quả mới nhất ở đầu, bên dưới giữ lịch sử. Các giới hạn P04/P05 cũ đã được P06/P07 bổ sung; không đọc chúng như giới hạn hiện tại.
4. `outputs/p07-handoff.md`, rồi p06/p05/p04 nếu cần chi tiết mô-đun. `outputs/p06-po-review.jpg`, `outputs/p07-po-review.jpg` là ảnh **dữ liệu giả lập**.

`outputs/design-review-v1` là bản mẫu thiết kế, không phải app vận hành. `docs/archive` là lịch sử, không phải yêu cầu mới. README đã cập nhật tớiP07.

## 2b. Quy trình Spec Kit (từ 11/10/2026)

Tính năng mới đi theo `/speckit-specify → plan → tasks → implement` trong `specs/NNN-…` (index: `specs/README.md`; quy tắc: `.specify/memory/constitution.md`), sau đó PO nghiệm thu bằng dữ liệu giả. P01–P07 đã migrate thành spec 001–004; TRX/Energy (006) và tài sản/crypto/BĐS (007) là backlog Draft. P08 = spec 005 (hành trình công nợ): đã code và kiểm xong trên QA 8801, đã phát hành, 8792 đã restart. Script Spec Kit chạy bằng `bash`, không dùng `sh`. Mã trên GitHub kanner9999-O/PCMS (outputs/ và private-data/ không đẩy lên).

P32 (spec 030, Ghi chú giao dịch; danh mục mẫu chi phí mua BĐS vốn hóa và chi khác không chứng từ; giá gốc BĐS gồm chi phí mua vốn hóa) hoàn thành 15/10/2026.

P31 (spec 029, Tên đối tượng duy nhất toàn hệ thống và gộp đối tượng trùng) hoàn thành 15/10/2026. Dữ liệu thật hiện có hai cặp trùng (Xuân Mai, Hòa Sơn: BĐS + đối tượng) chờ Thạch bấm Gộp.

P30 (spec 028, Hộp migrate chọn danh mục theo cấp, đối tượng của danh mục đã chọn) hoàn thành 15/10/2026. **Quyết định cấu trúc**: cách quản lý danh mục (cây cha-con, đối tượng thuộc danh mục, chọn theo cấp, nghiệp vụ là lớp song song) áp dụng cho mọi tính năng danh mục về sau — xem Constitution nguyên tắc VII.

P29 (spec 027, Migrate lịch sử cũ từ Google Sheets vào đối tượng của danh mục, ngoài chuỗi sao kê) hoàn thành 15/10/2026.

P28 (spec 026, Danh mục có đối tượng riêng: cây danh mục, đối tượng từng danh mục, thêm/đổi tên/gỡ/xóa/chuyển, lịch sử) hoàn thành 14/10/2026; thay khai báo "loại đối tượng" của P27.

P27 (spec 025, Phân loại theo danh mục → con → đối tượng; mỗi danh mục khai loại đối tượng; ✕ ở popup) hoàn thành 14/10/2026. Lưu ý: giao dịch gắn người trong Gốc vay/Lãi vay chưa vào Công nợ cho tới khi tích hợp nghiệp vụ.

P26 (spec 024, Xem trước giao dịch sẽ nhập: mốc + các giao dịch mới nối tiếp với số dư tính/file và ✔/✘) hoàn thành 14/10/2026.

P25 (spec 023, Lịch sử sao kê theo mốc snapshot: mốc + 10 giao dịch cuối, toàn bộ lịch sử có lọc, đối chiếu file mới với mốc) hoàn thành 14/10/2026.

P24 (spec 022, Nguồn liền mạch theo số dư và mốc snapshot: kiểm file theo chuỗi số dư, chốt mốc ghi giao dịch cuối, tạo tài khoản từ file) hoàn thành 14/10/2026. Hướng đi: tập trung nhập nguồn, snapshot, phân loại danh mục; nghiệp vụ (cho vay, BĐS, TRX, crypto, kinh doanh) tích hợp sau.

P23 (spec 021, Chung cư theo tiến độ: giá hợp đồng có lịch sử, lịch đợt, gắn giao dịch vào đợt, cam kết chưa thanh toán hiển thị riêng) hoàn thành 13/10/2026. Backlog tài sản còn: quy đổi tiền tệ, cổ phiếu/shop (pending).

P22 (spec 020, Mua/bán/chuyển crypto: số lượng sổ cái = mốc xác nhận + giao dịch sau mốc, USDT) hoàn thành 13/10/2026. Backlog tài sản còn: chung cư theo tiến độ, quy đổi tiền tệ, cổ phiếu/shop (pending).

P21 (spec 019, Lãi vay đi cùng khoản vay khi chuyển danh mục) hoàn thành 13/10/2026.

P20 (spec 018, Lịch sử rộng, một dòng một giao dịch) hoàn thành 12/10/2026.

P19 (spec 017, Định dạng lịch sử chuẩn: lịch sử danh mục/khoản vay/BĐS dùng dòng kiểu sao kê như màn Kiểm tra) hoàn thành 12/10/2026.

P18 (spec 016, Quản lý khoản vay và danh mục: chọn người→khoản vay, chuyển cả khoản vay sang danh mục khác, xóa danh mục chưa dùng, Kiểm tra gom theo gốc + đối tượng) hoàn thành 12/10/2026.

P17 (spec 015, Kiểm tra phân loại: màn chỉ xem gom giao dịch theo danh mục/đối tượng, kiểu sao kê, kiểm khớp với sao kê) đã phát hành 12/10/2026.

P16 (spec 014, Hoàn thiện Danh mục: gốc tự tạo theo loại, xem theo kỳ, báo cáo duyệt theo danh mục) đã phát hành 12/10/2026.

P15 (spec 013, Tổng hợp tài sản bản đầu: hai khối VND/USDT không quy đổi, bản chụp bất biến) đã phát hành 12/10/2026. Backlog còn: chung cư theo tiến độ, mua/bán/chuyển crypto, quy đổi tiền tệ nếu Thạch cần, cổ phiếu/shop (pending).

P14 (spec 012, Crypto / ví bản đầu: xác nhận số dư theo ngày, giá nhập tay, tỷ trọng, tách trạng thái sàn) đã phát hành 12/10/2026. Backlog tài sản còn: chung cư theo tiến độ, tổng tài sản hợp nhất, mua/bán/chuyển crypto (spec 007).

P13 (spec 011, Bất động sản bản đầu: vốn có nguồn, giá trị nhập tay, thế chấp, góp vốn) đã phát hành 11/10/2026. Backlog tài sản còn: chung cư theo tiến độ, tổng tài sản/định giá, crypto (spec 007).

P12 (spec 010, hoàn chi tiêu: tiền vào gán Chi tiêu là hoàn chi, hiển thị chi/hoàn chi/chi ròng) đã phát hành 11/10/2026. Quy trình từ P12: nhánh → PR vào main → merge.

P11 (spec 009, cải thiện màn Phân loại: lý do tùy chọn, sắp xếp theo số tiền, tạo nhanh đối tượng) đã phát hành 11/10/2026.

P10 (spec 008, quản lý danh mục) đã phát hành 11/10/2026: màn Danh mục, danh mục con, tổng/lịch sử truy nguồn (xem IMPLEMENTATION-STATUS). Spec 008 trùng số với `specs/008-product-map` do một phiên khác tạo song song; không gộp, cần đổi số một trong hai khi dọn dẹp.

P09 (spec 006, TRX/Energy bản đầu) đã phát hành 11/10/2026: xem IMPLEMENTATION-STATUS. Việc tiếp theo trong backlog: tài sản/crypto/BĐS (spec 007, cần phỏng vấn công thức định giá), snapshot riêng cho TRX nếu Thạch cần.

## 3. Bản vận hành và mã

Thư mục dự án: `/Users/nerkan/Documents/Working/PCMS`.

```sh
cd /Users/nerkan/Documents/Working/PCMS
PYTHONPATH=src python3 -m pcms serve --p01 --data outputs/p01-user-trial --port 8792
```

Mở `http://127.0.0.1:8792/`; hoặc chạy `Start PCMS P01.command`. TênP01 của launcher không có nghĩa bản còn ở tính năngP01. Ngày bàn giao đã thấy Python PID57764 nghe8792; PID có thể thay đổi, không dùng lại mù. Kiểm cổng trước khi start. Session84652 chỉ thuộc Codex, Claude không cần nó.

- `src/pcms/p01.py`: trạng thái ngân hàng, phân bổ, snapshot, công nợ gốc, điều khoản/lãi dự tính.
- `src/pcms/interest_settlement.py`: bảng kê lãi, phân bổ tiền, miễn giảm, duyệt/điều chỉnh.
- `src/pcms/loan_completion.py`: tất toán/mở lại và báo cáo dòng tiền.
- `src/pcms/server.py`, `__main__.py`: HTTP/khởi động; `bank_statement.py`: đọc sao kê.
- `src/pcms/web/p01.js`, `p01.html`, `p01.css`: UI hiện hành.
- `product.py`/`core.py` có phần dùng chung; không xóa. App cũ không chạy `--p01`, thường8787, không phải đích phát hành này.

Thư mục **chưa là Git repository** khi kiểm bàn giao; không có commit/branch/remote để cung cấp. Mã lưu trực tiếp trên đĩa. `outputs/handoff-2026-10-11-manifest.json` lưu SHA256 mã/tài liệu/tests và file dữ liệu để đối chiếu, không thay bản sao lưu.

## 4. Dữ liệu cần bảo vệ

`outputs/p01-user-trial` đang là bộ vận hành, có dữ liệu giả ban đầu **và nguồn người dùng đã nhập**. Không xóa/seed/reset/reclassify/approve để thử. P07 phát hành đã kiểm20/20 file không đổi checksum. Khi tiếp quản phải đọc trạng thái hiện tại, vì người dùng có thể tiếp tục nhập sau bàn giao.

Lần PO xem gần nhất có tài khoản mẫu, Tech-999, Tech-99999 và chưa có hồ sơ người/công nợ thực. Tech-999 bắt đầu09/07/2026; sao kê01/08–29/09 trước đó bị loại, có nút đưa lại kiểm tra. Khoảng09–31/07 chưa có nguồn; không tự bù tiền hoặc tự publish file. Đây là quan sát cũ, không phải lệnh sửa trạng thái.

Dữ liệu lưu sự kiện JSON kèm kiểm chứng và snapshot bất biến. Dùng chức năng backup/restore; restore tạo bộ riêng. Không sửa tay các JSON để đổi tiền hoặc trạng thái. Không gửi dữ liệu thật ra dịch vụ ngoài.

Các QA `/tmp/pcms-p0x-po-qa` có thể bị dọn; nguồn seed nằm trong tests, không phụ thuộc /tmp để tiếp tục. Kiểm checksum trước/sau phát hành; manifest chứa hash, không chứa nội dung giao dịch.

Khi tạo manifest bàn giao, bộ vận hành hiện có27 file, khác20 file tại lần phát hànhP07. Không sửa hoặc khôi phục chúng về trạng thái cũ; lượt bàn giao chỉ đọc và ghi hash hiện tại. Cần coi dữ liệu hiện tại là trạng thái mới nhất, không lấy các con số quan sát cũ trong chat để ghi đè.

## 5. Đã phát hành và đã kiểm

| Đợt | Khả năng | Bằng chứng |
|---|---|---|
| P01–P03 | VND/mẫu XLSX hỗ trợ; kiểm nguồn/trùng/lệch; phân loại/tách khoản; chuyển nội bộ; snapshot ngân hàng; backup/restore; sửa/xóa rỗng/lưu trữ tài khoản; ngày theo dõi, phục hồi nguồn đã loại, thiếu kỳ nguồn, chặn duyệt trùng | outputs/p01-implementation-handoff.md; p02-implementation-handoff.md; p02-1-source-recovery-handoff.md; p03-handoff.md |
| P04 | Người và từng khoản phải thu/phải trả; gốc đầu có căn cứ; không bù trừ; legacy thiếu setup cảnh báo; truy nguồn | outputs/p04-handoff.md; p04-po-review.md |
| P05 | Lãi suất VND/triệu/ngày hoặc %/30ngày; ngày hiệu lực/audit; xem trước từng đoạn gốc; lãi thực thu riêng | outputs/p05-handoff.md |
| P06 | Kỳ lãi không chồng; chủ động chọn một phần tiền nguồn đúng khoản/chiều; chống dùng trùng; miễn giảm có lý do/ngày/xác nhận; snapshot lãi và điều chỉnh bất biến | outputs/p06-handoff.md; p06-po-review.jpg |
| P07 | Tất toán cần đủ gốc/lãi/kỳ đã duyệt/căn cứ; mở lại có lý do; nguồn đổi cần kiểm lại; lọc người/khoản; tuần/tháng/quý gồm khoản đã tất toán; tách gốc/lãi/chi phí/hoàn chi phí | outputs/p07-handoff.md; p07-po-review.jpg |

PO đã trực tiếp kiểmP06:1,5 triệu dự tính, tiền nhận1,2 triệu ngoài kỳ được chọn rõ; S1 còn300nghìn; S2 miễn300nghìn còn0; S1 nguyên vẹn. Lỗi token phát hiện qua UI đã sửa trước phát hành.

PO kiểmP07: chặn khoản hết gốc còn lãi; mở lại và tất toán lại khoản đủ; lịch sử còn; báo cáo tháng09 lãi2,7 triệu, chi phí0,2 triệu, chênh2,5 triệu và thu gốc200 triệu riêng; lọc người hoàn thành không cắt báo cáo.

Tests: P06 cuối8 ca +12 hồi quy trước đó đạt. P07 chạy19 ca kết hợp trước hai bổ sung, sau đó5 caP07 cuối đạt; không cộng số lượt chạy thành số ca độc lập. JS syntax đạt. Không chạy lại toàn bộ bộ tests ở lượt bàn giao vì không sửa mã. Chưa kiểm mobile riêngP03–P07, dữ liệu lớn hoặc toàn bộ hành trình sản phẩm.

## 6. Chạy kiểm thử và dựng QA

Từ gốc dự án, ví dụ kiểm đúng vùng thay đổi:

```sh
PYTHONPATH=src:tests python3 -m unittest test_p07_acceptance
PYTHONPATH=src:tests python3 -m unittest test_p06_acceptance test_p05_acceptance test_p04_acceptance
node --check src/pcms/web/p01.js
```

Node có thể không nằm trongPATH; lần trước dùng runtime Node cục bộ của Codex. Claude có thể dùng Node sẵn trên máy, không cần phụ thuộc plugin. `tests/test_p07_acceptance.py` có `seed(store)` tạo dữ liệu giả; chỉ gọi trên thư mục mới riêng với `P01Store`. Ví dụ server QA dùng `--data /tmp/pcms-claude-qa --port 8799`, kiểm cổng trước.

UI thử qua browser với dữ liệu giả; không dùng API ghi vào8792 để tránh thao tác người dùng. Backend và static JS cùng workspace: gate tính năng mới theo capability backend, tránh UI mới gọi API chưa có của server đang chạy. Sau kiểm, restart đúng backend để phát hành và verify bản chính read-only.

## 7. Quy tắc và bẫy cần giữ

- 500VND/triệu/ngày tương đương1,5%/tháng30ngày đã xác nhận (R43). Gốc lẻ triệu không cắt; không vốn hóa lãi.
- Biên ngày/làm tròn ban đầu chưa chốt chung. P05 dùng quy ước xem trước: dư gốc cuối ngày, gồm ngày đầu/không gồm ngày cuối, round tổng một lần half-up. P06 buộc xác nhận căn cứ áp dụng riêng cho bảng kê; không nói người dùng đã chốt toàn cục.
- Tất toánP07 bao phủ tới hết ngày hoàn tất, tức end-exclusive ngày kế. Hết gốc không tự đủ. Lãi0 phải có điều khoản/bảng kê, không suy từ thiếu dữ liệu.
- Duyệt bank và duyệt bảng kê là khác nhau. Snapshot cũ giữ nguyên. Phân bổ đang nháp vẫn có thể dùng cho báo cáo hiện hành; không gọi tổng đó đã đối soát đủ thực tế.
- Tiền thu theo ngày giao dịch không tự gắn kỳ lãi; chọn tiền ngoài kỳ được nhưng phải rõ ngày. Không dùng lại tiền ở các bản duyệt hiện hành; bản cũ bị thay thế không giữ thêm reservation. Sửa nguồn không được gây kẹt sửa hoặc chuyển tiền sang khoản khác khi còn reservation cũ.
- HTTP response có CSRF `token`; review phải dùng `review_token`. Lỗi đụng tên đã có regression.
- Decimal precision cao cho số tiền; không chuyển sangfloat hoặc dùngJS Number để tính tiền chính xác.
- Báo cáoP07 theo phân bổ nguồn, không cộng snapshot; lãi nhận−lãi trả−chi phí gắn khoản+hoàn chi phí là chênh tiền, không phải lợi nhuận ròng. Lọc trạng thái không loại khoản tất toán khỏi báo cáo.

## 8. Còn thiếu và việc nên làm tiếp

**Chưa hoàn thành toàn bộ sản phẩm/N3–N5.** Còn TRX/Energy, crypto và tài sản/BĐS, định giá/FX/tỷ trọng/phân tích đầu tư và tổng quan tài chính. Shop/cổ phiếu/khóa sổ tháng đang pending theo tài liệu, không tự mở lại phạm vi. Không quản gia hạn/cấp/cắt Energy (R41). Không có kết nối giao dịch tự động với ngân hàng/sàn.

Ưu tiên PO đã thông báo gần nhất: rà một hành trình xuyên suốt ngân hàng→phân loại→công nợ→bảng kê→báo cáo→điều chỉnh/khôi phục để tìm chỗ khó dùng/thiếu liên kết, rồi mới mở rộng TRX/Energy theo yêu cầu hiện hành. Đây là hướng tiếp theo, chưa có code/test cho đợt mới.

Đối chiếu các tiêu chí còn chưa chứng minh đủ, không chỉ thêm tính năng: R47 tổng quan người, R53 phạm vi chi phí, các yêu cầu danh mục/lịch sử ở R44–R59. Kiểm mobile riêng và vận hành với nhiều khoản/dữ liệu lớn còn thiếu. Không kết luận số dư cá nhân đã đầy đủ chỉ vì tests giả đạt.

Lưu ý UX đang có: gốc tổng và lãi duyệt nằm khác màn; một số dialog nhiều bước, thời gian lịch sử còn ISO UTC, nguồn có mã dài. Đây là điểm cần tự đánh giá qua dùng thử, không phải lỗi tài chính đã xác nhận. Ghi phát hiện cụ thể rồi mới giao sửa, không rewrite kiến trúc vô cớ.

## 9. Lời nhắn để bắt đầu trong Claude

“Đọc CLAUDE.md và HANDOFF.md trong dự án này. Tiếp quản vai trò PO + người dùng đại diện, đối chiếu PRODUCT-SPEC.md và ACCEPTANCE.md. Bản hiện hành là P07. Tự rà hành trình xuyên suốt bằng dữ liệu giả, ưu tiên và giao triển khai phần còn thiếu; tôi chỉ dùng và feedback. Bảo vệ outputs/p01-user-trial, không tự duyệt dữ liệu thật. Báo cáo kết quả cụ thể, giữ ngữ cảnh và số lượt kiểm tra gọn.”
