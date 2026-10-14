# PCMS — Hiện trạng, quyết định và bằng chứng

Cập nhật bàn giao · 11/10/2026. Hiện trạng không bổ sung yêu cầu ngoài [PRODUCT-SPEC](PRODUCT-SPEC.md). Tiêu chí ở [ACCEPTANCE](ACCEPTANCE.md).

## 1. Trạng thái

Điểm bắt đầu tiếp quản: [HANDOFF.md](HANDOFF.md). Các mục bên dưới là lịch sử từng đợt; giới hạn ở đợt cũ có thể đã được đợt mới bổ sung. P07 là bản phát hành hiện tại, không còn việc triển khai P07 đang chạy. Không coi mọi yêu cầu N0–N5 đã hoàn thành.

### P26 Xem trước giao dịch sẽ nhập — 14/10/2026 (đã phát hành, 8792 đã restart)

Làm theo Spec Kit: [specs/024-import-preview](specs/024-import-preview/spec.md) (Thạch yêu cầu; phỏng vấn lại nội dung, cách kiểm đúng, file bị chặn, vị trí; R115–R117). Bước Nhập và kiểm nguồn: file hợp lệ (chờ ghi) có nút **"Xem trước giao dịch sẽ nhập"** cạnh "Xem dòng nguồn". Hộp rộng hiện giao dịch cuối đã ghi làm mốc (kèm số dư), rồi **đúng các giao dịch mới theo thứ tự nối tiếp** (không hiện dòng trùng), mỗi dòng có số dư do hệ thống tính, số dư trong file và dấu ✔/✘; cuối có tổng vào/ra, số dư cuối dự kiến so với số dư cuối file. File bị chặn không có nút; API từ chối. Chỉ đọc. Test: 5 ca P26 + hồi quy = 227 ca Python đạt; trên bản sao dữ liệu thật file (46): 52 dòng mới, 127 trùng ẩn, tất cả ✔, số dư cuối dự kiến 209.995.157 khớp file. Bàn giao: outputs/p26-handoff.md.

### P25 Lịch sử sao kê theo mốc snapshot — 14/10/2026 (đã phát hành, 8792 đã restart)

Làm theo Spec Kit: [specs/023-account-history](specs/023-account-history/spec.md) (Thạch yêu cầu; phỏng vấn lại các chỗ chưa rõ: chỉ mốc gần nhất, nội dung, bộ lọc, vị trí; R111–R114). Trang tài khoản có khối "Lịch sử sao kê": mốc snapshot gần nhất (giao dịch cuối, ngày, số dư), **10 giao dịch cuối của mốc** theo dòng sao kê chuẩn (kèm số dư sau giao dịch), nút "Xem toàn bộ lịch sử sao kê" mở hộp rộng (phạm vi tới mốc hoặc toàn bộ từ ngày đầu, bộ lọc khoảng ngày và chiều vào/ra, phân trang 50, danh sách file sao kê) và, với mỗi file chờ ghi/bị chặn, kết luận **liền mạch và đúng đắn** so với mốc (cách nối, dòng mới/trùng, số dư kỳ vọng/đầu/cuối). Chỉ đọc. Test: 6 ca P25 + hồi quy = 222 ca Python đạt; PO dùng thử QA 8801 (25 giao dịch, 10 dòng cuối, file nối tiếp ✔, file hở ✘, bộ lọc, 375px không tràn ngang). Bàn giao: outputs/p25-handoff.md.

### P24 Nguồn liền mạch theo số dư và mốc snapshot — 14/10/2026 (đã phát hành, 8792 đã restart)

Làm theo Spec Kit: [specs/022-source-continuity](specs/022-source-continuity/spec.md) (Thạch định hướng và trả lời phỏng vấn, R105–R110). Kiểm tra file nguồn theo **chuỗi số dư**, không so ngày: file chứa lại giao dịch cuối đã ghi rồi các dòng mới (kể cả cùng ngày), hoặc không chứa lại nhưng số dư đầu bằng số dư sau giao dịch cuối, đều nối tiếp; chặn khi số dư đầu không nối, có dòng mới nằm trước/xen giữa, phần chồng không kết thúc ở giao dịch cuối, số dư cuối sai hoặc xung đột mã tham chiếu. Bỏ quy tắc "Nguồn mới làm lệch kỳ nguồn đã ghi" và khoảng ngày chưa có nguồn. Bản chốt mốc (đổi chữ từ "duyệt") ghi giao dịch cuối, số dư và số giao dịch; màn tài khoản hiện mốc và số giao dịch nối tiếp sau mốc cần phân loại. Thêm tạo tài khoản từ file sao kê đầu tiên (số tài khoản, số dư đầu, ngày bắt đầu từ file). Test: 7 ca P24 + hồi quy = 216 ca Python đạt (4 test cũ P02/P03 đổi theo R107/R108). Thử trên bản sao dữ liệu thật: file (46) hết lỗi, 52 dòng mới/127 dòng trùng. Bàn giao: outputs/p24-handoff.md.

### P23 Chung cư theo tiến độ — 13/10/2026 (đã phát hành, 8792 đã restart)

Làm theo Spec Kit: [specs/021-realty-progress](specs/021-realty-progress/spec.md) (phỏng vấn Thạch → specify → plan → tasks → implement → nghiệm thu → PR). Theo R101–R104: mỗi BĐS có giá hợp đồng (ngày, lý do, lịch sử, ngày bàn giao dự kiến), lịch thanh toán nhập từng đợt, gắn giao dịch ngân hàng Đầu tư BĐS vào đợt (trả từng phần được, bỏ gắn có lý do), trạng thái đợt, quá hạn (chỉ nhắc), cam kết còn phải thanh toán hiển thị riêng ở màn BĐS và Tổng tài sản (không vào nợ, không trừ giá trị BĐS), khoản vay giữ liên kết thế chấp hiện có. Test: 5 ca P23 + hồi quy = 209 ca Python đạt; PO dùng thử QA 8801 (gắn giao dịch vào đợt, trả quá, dòng cam kết ở Tổng tài sản, 375px không tràn ngang). Chưa làm: tự gắn giao dịch, lãi/phạt chậm trả, gắn giải ngân vay với từng đợt. Bàn giao: outputs/p23-handoff.md.

### P22 Mua/bán/chuyển crypto — 13/10/2026 (đã phát hành, 8792 đã restart)

Làm theo Spec Kit: [specs/020-crypto-movements](specs/020-crypto-movements/spec.md) (phỏng vấn Thạch → specify → plan → tasks → implement → nghiệm thu → PR). Theo R97–R100: số lượng "đang giữ" = mốc xác nhận gần nhất + mua/bán/chuyển có ngày sau mốc; chỉ USDT, không liên kết sao kê VND, chưa tính lãi/lỗ; phí nhập riêng (USDT hoặc coin); chuyển giữa hai nơi giữ (số gửi/nhận, chênh là phí mạng). Cảnh báo "chưa có mốc" và số âm (không vào giá trị), đối chiếu khi xác nhận lại (không tự sửa), hủy giữ bản ghi, tổng tài sản dùng số lượng sổ cái. Test: 7 ca P22 + hồi quy = 204 ca Python đạt; PO dùng thử QA 8801: mua 0.1 BTC giá 60.000 phí 6 USDT → BTC 0,6 và USDT 3.994 (đúng ví dụ spec); chuyển 0,3 BTC nhận 0,2995 hiện cảnh báo chưa có mốc ở ví nhận; hủy giao dịch; chặn dấu phẩy thập phân; 375px không tràn ngang. Chưa làm: lãi/lỗ đã thực hiện, liên kết sao kê VND, tự lấy dữ liệu sàn. Bàn giao: outputs/p22-handoff.md.

### P21 Lãi vay đi cùng khoản vay — 13/10/2026 (đã phát hành, 8792 đã restart)

Làm theo Spec Kit: [specs/019-loan-interest-follows](specs/019-loan-interest-follows/spec.md) (Thạch xác nhận R96). Khi chuyển khoản vay sang danh mục khác, phần lãi vay của khoản cũng hiện dưới danh mục mới (nhãn "Lãi vay" trên dòng); Lãi vay gốc hệ thống không còn đếm khoản đó, tiền không mất chỉ đổi chỗ; dư gốc, công nợ, bảng kê lãi, báo cáo theo loại và snapshot không đổi. Test: 197 ca Python đạt (P18 cập nhật theo R96, thêm 1 ca). Bàn giao: outputs/p21-handoff.md.

### P20 Lịch sử rộng, một dòng một giao dịch — 12/10/2026 (đã phát hành, 8792 đã restart)

Làm theo Spec Kit: [specs/018-history-wide](specs/018-history-wide/spec.md) (Thạch phản hồi sau P19, R95). Hộp lịch sử (danh mục, BĐS, chi tiết khoản vay) rộng tới 1280px; mỗi giao dịch một hàng gồm ngày, mã, nội dung + tài khoản, Xem nguồn, số tiền, nhãn/trạng thái khi khung ≥ 1060px, hẹp hơn tự xếp hai hoặc ba tầng (container query). Màn Kiểm tra dùng cùng lưới. Chỉ đổi hiển thị. Test: 196 ca Python + 7 bộ node đạt; PO dùng thử QA 8801 ở 1500, 768 và 375px (không tràn ngang; 1500px mỗi giao dịch cao đúng một hàng). Bàn giao: outputs/p20-handoff.md.

### P19 Định dạng lịch sử chuẩn — 12/10/2026 (đã phát hành, 8792 đã restart)

Làm theo Spec Kit: [specs/017-history-format](specs/017-history-format/spec.md) (Thạch giao PO chốt định dạng, R94). Lịch sử của danh mục, khoản vay và BĐS dùng cùng một dòng kiểu sao kê như màn Kiểm tra phân loại: tóm tắt đầu, mỗi giao dịch một dòng (ngày + mã, nội dung + Xem nguồn, số tiền ra/vào màu, nhãn + trạng thái), mới nhất trước, tổng cuối. Chỉ đổi hiển thị và thêm trường hiển thị; số liệu không đổi. Test: 4 ca P19 + node `history_format` + hồi quy = 196 ca Python, 7 bộ node đạt (2 kỳ vọng thứ tự cũ ở P10 đổi sang mới nhất trước). PO dùng thử QA 8801. Bàn giao: outputs/p19-handoff.md.

### P18 Quản lý khoản vay và danh mục — 12/10/2026 (chờ phát hành)

Làm theo Spec Kit: [specs/016-loan-category-management](specs/016-loan-category-management/spec.md) (phỏng vấn Thạch → specify → plan → tasks → implement → nghiệm thu). Theo R87–R93: chọn người rồi khoản vay (nhãn "người · ngày · gốc · dư", tạo khoản mới ngay trong ô chọn, không hiện PERSON/LOAN), danh mục con tùy chọn, chặn Thu nhập/Chuyển nội bộ có đối tượng và hồ sơ người gắn trực tiếp, màn Kiểm tra gom theo danh mục + đối tượng (danh mục con là nhãn dòng), chuyển cả khoản vay sang danh mục Gốc vay khác (Loans › Long debt) có lý do và ngày, giữ lịch sử, dư gốc/công nợ/snapshot không đổi, xóa hẳn danh mục chưa từng dùng. Test: 7 ca P18 + node `loan_label` + hồi quy = 192 ca Python, 6 bộ node đạt; PO dùng thử UI trên QA 8801 (desktop + 375px). Chưa làm: chuyển nhóm cho Lãi vay, nhóm cho BĐS. Bàn giao: outputs/p18-handoff.md.

### P17 Kiểm tra phân loại — 12/10/2026 (đã phát hành, 8792 đã restart)

Làm theo Spec Kit: [specs/015-classification-review](specs/015-classification-review/spec.md) (mockup → Thạch chốt → specify → plan → tasks → implement → nghiệm thu → PR). Theo R84–R86: màn chỉ xem mở từ bước Phân loại, gom giao dịch theo danh mục (và "Danh mục · Đối tượng", ví dụ "Gốc vay · Kết"), nhóm "Chưa phân loại" riêng, dòng kiểu sao kê (ngày + mã, nội dung + Xem nguồn, số tiền, nhãn), mở sẵn mọi giao dịch, phạm vi mặc định cả tài khoản (24 giờ qua / khoảng ngày), khoản vừa phân loại lên đầu kèm nhãn "Mới", thanh tóm tắt và kiểm khớp số giao dịch/tiền vào/ra với sao kê. Không sửa dữ liệu, không đổi snapshot/báo cáo. Test: 5 ca P17 + node + hồi quy = 185 ca Python đạt, 5 bộ node đạt; PO dùng thử UI trên QA 8801 (desktop + 375px); 56 file `outputs/p01-user-trial` giữ nguyên SHA256. Chưa làm: nút "đã kiểm", sửa ngay trên màn. Bàn giao: outputs/p17-handoff.md.

### P16 Hoàn thiện Danh mục — 12/10/2026 (đã phát hành, 8792 đã restart)

Làm theo Spec Kit: [specs/014-category-completion](specs/014-category-completion/spec.md) (phỏng vấn Thạch → specify → plan → tasks → analyze → implement → nghiệm thu → PR). Theo R81–R83: tự tạo danh mục gốc mới (loại nhóm thu/chi/đầu tư kế thừa quy tắc, tổng riêng, không trùng tên gốc nào), xem tổng và lịch sử theo kỳ (tháng/quý/tùy chọn), báo cáo duyệt theo danh mục (số giao dịch, số đối tượng, vào/ra/chi ròng, kiểm đối chiếu khớp, mở chi tiết). Không đổi snapshot/báo cáo cũ. Test: 6 ca P16 + node + hồi quy = 117 ca đạt; PO dùng thử UI trên QA 8801 và mobile; 53 file `outputs/p01-user-trial` giữ nguyên SHA256. Chưa làm: gộp danh mục, loại trung tính. Bàn giao: outputs/p16-handoff.md.

### P15 Tổng hợp tài sản bản đầu — 12/10/2026 (đã phát hành, 8792 đã restart)

Làm theo Spec Kit: [specs/013-asset-overview](specs/013-asset-overview/spec.md) (phỏng vấn Thạch → specify → plan → tasks → analyze → implement → nghiệm thu → PR). Theo R77–R80: màn Tổng tài sản với hai khối VND và USDT độc lập (không quy đổi), tài sản/nợ/ròng, tỷ trọng theo nhóm, cơ sở tính (BĐS chưa có giá trị theo giá gốc có nhãn — PO quyết định theo nghiệp vụ kế toán), cảnh báo độ tin cậy, nút mở màn nguồn, bản chụp bất biến có hash và chênh lệch. Không tính đôi (thế chấp chỉ ở nợ, nợ margin/vị thế không cộng trừ), không dồn tích lãi. Test: 6 ca P15 + hồi quy = 111 ca đạt; PO dùng thử UI trên QA 8801 và mobile; 53 file `outputs/p01-user-trial` giữ nguyên SHA256. Chưa làm: quy đổi tiền tệ, cổ phiếu/shop/chung cư tiến độ, biểu đồ diễn biến. Bàn giao: outputs/p15-handoff.md.

### P14 Crypto / ví bản đầu — 12/10/2026 (đã phát hành, 8792 đã restart)

Làm theo Spec Kit: [specs/012-crypto-wallets](specs/012-crypto-wallets/spec.md) (phỏng vấn Thạch → specify → plan → tasks → analyze → implement → nghiệm thu → PR). Theo R74–R76: nơi giữ (ví riêng, Binance, BingX), xác nhận số dư theo ngày (lịch sử, hủy có lý do), tách trạng thái trên sàn (đang giữ, Earn/khóa, ký quỹ, vị thế, nợ margin — vị thế và nợ hiển thị riêng, không cộng trừ), giá USDT nhập tay, giá trị và tỷ trọng theo nơi giữ/coin chỉ trên coin có giá, vốn theo coin với chênh lệch "chưa thực hiện", coin khác mạng tách riêng. Test: 6 ca P14 + hồi quy = 105 ca đạt; PO dùng thử UI trên QA 8801 và 375px; 53 file `outputs/p01-user-trial` giữ nguyên SHA256. Chưa làm: mua/bán/chuyển, giá tự động, tổng tài sản hợp nhất, chung cư tiến độ. Bàn giao: outputs/p14-handoff.md.

### P13 Bất động sản bản đầu — 11/10/2026 (đã phát hành, 8792 đã restart)

Làm theo Spec Kit: [specs/011-realty](specs/011-realty/spec.md) (phỏng vấn Thạch → specify → plan → tasks → analyze → implement → nghiệm thu → PR). Theo R71–R73: màn Bất động sản với vốn đã thanh toán có nguồn (từ phân loại Đầu tư BĐS gắn BĐS, lịch sử truy dòng sao kê), chi phí gắn BĐS, giá trị hiện tại nhập tay (ngày, nguồn, hủy có lý do), vốn cạnh giá trị và chênh lệch "chưa thực hiện", thế chấp (khoản vay + mục đích, không trừ nợ), góp vốn (số tiền từng người, không tỷ lệ). Test: 6 ca P13 + hồi quy = 99 ca đạt; PO dùng thử UI trên QA 8801 và 375px; 53 file `outputs/p01-user-trial` giữ nguyên SHA256. Chưa làm: chung cư theo tiến độ, tổng tài sản/định giá, crypto. Bàn giao: outputs/p13-handoff.md.

### P12 Hoàn chi tiêu — 11/10/2026 (đã phát hành, 8792 đã restart)

Làm theo Spec Kit: [specs/010-expense-refund](specs/010-expense-refund/spec.md) (specify → plan → tasks → analyze → implement → nghiệm thu → PR). Theo R70: tiền vào gán Chi tiêu là hoàn chi, báo cáo/danh mục/lịch sử hiển thị chi, hoàn chi, chi ròng; Thu nhập không tăng. Ví dụ cơm 1.000.000 + 2 × 300.000 → chi ròng 400.000. Test: 6 ca P12 + node + hồi quy = 93 ca đạt; PO dùng thử UI trên QA 8801; 49 file `outputs/p01-user-trial` giữ nguyên SHA256. Bàn giao: outputs/p12-handoff.md.

### P11 Cải thiện màn Phân loại — 11/10/2026 (đã phát hành, 8792 đã restart)

Làm theo Spec Kit: [specs/009-classification-ux](specs/009-classification-ux/spec.md) (specify → plan → tasks → analyze → implement → nghiệm thu) theo 3 phản hồi của Thạch (R67–R69): lý do phân loại tùy chọn; sắp xếp theo số tiền (nhỏ→lớn, lớn→nhỏ, trị tuyệt đối, giữ chọn dòng/bộ lọc); tạo nhanh đối tượng trong dòng phân loại (khoản vay + người mới, BĐS, danh mục con, tự chọn sau khi tạo). Lý do khi duyệt phiên bản mới vẫn bắt buộc (R21). Test: 4 ca P11 + kiểm sắp xếp bằng node + hồi quy = 87 ca đạt (cập nhật 1 dòng test P01 cũ khẳng định lý do bắt buộc); PO dùng thử UI trên QA 8801 và 375px; 41 file `outputs/p01-user-trial` giữ nguyên SHA256. Bàn giao: outputs/p11-handoff.md.

### P10 Quản lý danh mục — 11/10/2026 (đã phát hành, 8792 đã restart)

Làm theo Spec Kit: [specs/008-category-management](specs/008-category-management/spec.md) (specify → clarify → plan → tasks → analyze → implement → nghiệm thu). Thêm màn **Danh mục**: bảy gốc hệ thống + danh mục con tự tạo (≤4 cấp, đổi tên/cha trong cùng gốc, lưu trữ/khôi phục có lịch sử), tổng vào/ra/chênh theo cây (mỗi giao dịch đếm một lần ở cha, danh mục lưu trữ vẫn tính), lịch sử từng danh mục truy về dòng sao kê, chọn danh mục con khi phân loại, bản duyệt đóng băng tên danh mục lúc duyệt. Test: 7 ca P10 (gồm 2.000 giao dịch) + hồi quy P01–P09 = 83 ca đạt; PO dùng thử UI trên QA 8801 và mobile 375px; 29 file `outputs/p01-user-trial` giữ nguyên SHA256. Chưa làm: gốc tự do, tổng đa tiền tệ, đo 10.000 giao dịch. Bàn giao: outputs/p10-handoff.md.

### P09 TRX/Energy bản đầu — 11/10/2026 (đã phát hành, 8792 đã restart)

Làm theo Spec Kit: [specs/006-trx-energy](specs/006-trx-energy/spec.md). Thạch trả lời phỏng vấn, chốt R63–R66 (gói tháng = mức cấp duy trì; công nợ USDT; doanh thu theo tiền thực thu; bán TRX/thưởng chỉ ghi số lượng và tiền). Phạm vi: ghi nhận thủ công khách → đơn (Energy một lần / gói tháng / bán TRX; thu trước-sau, hạn thu tùy chọn) → khoản thu (USDT hoặc VND + tỷ giá nhập tay, tùy chọn gắn giao dịch ngân hàng) → phân bổ → báo cáo tuần/tháng/quý theo ngày nhận; thưởng staking chỉ số lượng; hủy có lý do giữ bản ghi. Mô-đun `src/pcms/trx_energy.py`, lưu trong `state['trx']` (không đổi schema bắt buộc). Chặn ghi tiền hai lần: một giao dịch ngân hàng chỉ gắn trong giới hạn số tiền; giao dịch đã phân bổ vào khoản vay không gắn được. Không lãi/lỗ, không tự quá hạn (chỉ khi có hạn đã qua), không điều khiển Energy/ví. Test: 7 ca P09 + hồi quy P01–P08 (tổng 76 ca) đạt; PO dùng thử UI trên QA 8801: đơn 3 × 100 USDT → thu 200 USDT + 2.500.000 VND @25.000 (=100 USDT, gắn giao dịch ngân hàng) → phân bổ → còn nợ 0; gắn trùng bị chặn; báo cáo tháng 10: 300 USDT, VND thực nhận 2.500.000, thưởng 12,5 TRX; hủy khoản thu hoàn công nợ 100, giữ lịch sử. Mobile 375px không tràn ngang. 27 file `outputs/p01-user-trial` giữ nguyên SHA256. Chưa làm: snapshot/duyệt riêng cho TRX, lãi/lỗ bán TRX, nguồn USDT tự động, kiểm dữ liệu lớn.

### P08 hoàn thiện hành trình công nợ — 11/10/2026 (đã phát hành, 8792 đã restart 11/10/2026)

Làm theo Spec Kit: [specs/005-debt-journey-polish](specs/005-debt-journey-polish/spec.md) (spec → plan → tasks → implement). Nguồn: rà hành trình bằng dữ liệu giả, R47/R53. Chỉ đổi hiển thị/mặc định/liên kết, không đổi quy tắc tiền. Kết quả trên QA 8801 (dữ liệu giả): đầu màn Công nợ có Tổng quan (phải thu 100.000.000, phải trả 0, 3 người, 2 đang hoạt động/1 hoàn tất); khoản "hết gốc còn lãi" hiện lý do chưa hoàn tất kèm nút tới bảng kê lãi; nhãn trạng thái không còn lặp; báo cáo dòng tiền mở ngày nguồn mới nhất 30/09/2026 (hôm nay 11/10 chưa có nguồn) và cảnh báo "Kỳ này chưa có nguồn" khi chọn 11/2026; số tháng 09 không đổi (lãi 2,7 triệu, chi phí 0,2 triệu, chênh 2,5 triệu, thu gốc 200 triệu); liên kết tài khoản ↔ công nợ đi được hai chiều. Test: 5 ca P08 + hồi quy P03–P07 (30 ca) đạt, `node --check` đạt, 7 ca node cho kỳ mặc định/cảnh báo đạt. 27 file `outputs/p01-user-trial` giữ nguyên SHA256 trước/sau. Kiểm mobile 375px (11/10/2026, QA 8801): màn tài khoản, 3 bước nhập/phân loại/duyệt, Công nợ và hộp thoại báo cáo đều không tràn ngang (scrollWidth = 375). Chưa kiểm dữ liệu lớn; các tổng vẫn là NHÁP. Đã restart 8792 (PID mới 6227); UI chính chỉ đọc, 27 file dữ liệu giữ nguyên SHA256.

### P07 đã phát hành11/10/2026 — R53/A49

PO chọn hoàn thiện tất toán có căn cứ và báo cáo tiền thực thu theo tuần/tháng/quý, trước mở rộng sang business khác. Một coder thực hiện; PO đã kiểm nghiệp vụ và dùng UI trước phát hành. Không tự coi hết gốc là hết nợ.

Kết quả thay trạng thái chờ ở trên: PO thử QA8799 chặn khoản Chi hết gốc còn lãi; lọc người đã hoàn thành rồi xem tháng09 vẫn đủ2,7 triệu lãi nhận và0,2 triệu chi phí, chênh2,5 triệu; tách200 triệu thu gốc. Mở lại An có lý do rồi xác nhận hoàn tất lại, giữ cả3 sự kiện lịch sử và chứng từ. Coder chạy19 ca kết hợp trước bổ sung,5 caP07 cuối đạt cùngJS syntax. Bằng chứng outputs/p07-po-review.jpg và outputs/p07-handoff.md. Đã chạy8792 session84652, kiểm UI bộ lọc/báo cáo;20/20 file dữ liệu giữ nguyên SHA256. Không kiểm mobile riêng, chưa hoàn thành toàn bộN3/TRX/Energy.

### P06 đã phát hành 11/10/2026 — R21, R42 và A36–A37

PO giao một coder riêng làm bảng kê lãi theo kỳ với chọn tiền nguồn, miễn giảm có căn cứ và duyệt phiên bản. Không mặc định tiền thu trong kỳ là trả kỳ đó; không tự thay quy ước dự tính thành thỏa thuận thật. PO đã kiểm toàn hành trình trước phát hành; kết quả bên dưới.

Kết quả thay trạng thái chờ ở trên: 8 ca P06 và12 ca hồi quy liên quan đạt, JS syntax đạt. PO đã dùng QA8798 tạo bảng kê1,5 triệu, chủ động chọn tiền1,2 triệu nhận ngoài kỳ, duyệtS1 còn300 nghìn; mở điều chỉnh có lý do, giảm300 nghìn và duyệtS2 còn0; mở lạiS1 giữ nguyên300 nghìn. Gốc và tiền thực thu không đổi. PO phát hiện lỗi token phản hồi khiến duyệt nhầm báo stale; coder sửa review_token và thêm hồi quy luồng HTTP trước khi PO kiểm lại thành công. Ảnh bằng chứng outputs/p06-po-review.jpg, bàn giao outputs/p06-handoff.md.

Đã chạy bản chính8792, session80719; mở UI Công nợ đúng chức năng mới,20/20 file dữ liệu giữ nguyên SHA256 trước/sau. Chưa nghiệm thu mobile riêng, TRX/Energy, quá hạn hoặc toàn bộN3. Số tổng trên trang công nợ vẫn là gốc; lãi duyệt xem riêng trong từng bảng kê.

### P05 đã phát hành — tham chiếu R42–R43, A38–A39

PO chọn điều khoản lãi và bảng xem trước theo dư gốc từng đoạn. Một coder mới triển khai; PO kiểm tài liệu và UI. Biên ngày/làm tròn là quy ước xem trước được nêu rõ và yêu cầu xác nhận, chưa được gọi là thỏa thuận người dùng đã chốt. Chưa triển khai nợ lãi, miễn giảm, quá hạn hoặc duyệt công nợ riêng; không công bố N3 hoàn tất.

12 ca P05/P04/P03 đạt, JS syntax đạt. PO trực tiếp dùng QA8797: dự tính01–11/10 chia120 triệu ×1 ngày và90 triệu ×9 ngày =465.000, tách tiền lãi đã nhận1 triệu; đổi ngày sai xóa kết quả cũ và hiện lỗi; lưu1,5%/tháng hiệu lực03/10 hiện tương đương500 đồng/triệu/ngày, giữ điều khoản01/10. Đã phát hành8792, session78629; UI chính mở được,20/20 file người dùng giữ nguyên checksum. Bàn giao outputs/p05-handoff.md. Chưa kiểm riêng bố cục mobile cho đợt này.

### P04 đã phát hành bản sổ công nợ — 10/10/2026

Một coder mới triển khai sổ phải thu/phải trả theo người và từng khoản, thiết lập gốc đầu có căn cứ, tính biến động gốc từ phân bổ và truy nguồn. PO đã dùng UI QA8796: đối chiếu gốc/lãi/tổng hai chiều, truy dòng sao kê, kiểm xác nhận số đầu bằng không và tạo khoản mới cùng người. 4 ca P04 + 4 ca P03 và JS syntax đạt theo bàn giao coder. PO cho cập nhật bản8792 giữ nguyên dữ liệu. Bằng chứng tại outputs/p04-po-review.md và outputs/p04-handoff.md. Sổ còn ở mức nháp theo dữ liệu; chưa có duyệt công nợ riêng, lãi dự kiến/miễn giảm hoặc quá hạn. Không thêm tester riêng hay sửa dữ liệu thật để thử.

Đã khởi động bản mới8792 và mở mục Công nợ qua UI trên bộ dữ liệu chính; trạng thái trống đúng vì chưa có hồ sơ người. Toàn bộ20 file dữ liệu giữ nguyên SHA256 trước/sau. Session vận hành64770. Lượt phát hành ban đầu bị chờ quyền xem tiến trình; PO đã xử lý khởi động lại sau khi lệnh dừng được cấp quyền.

### P03 đã qua review, cập nhật bản ngân hàng — 10/10/2026

PO đã kiểm ứng dụng QA8795 bằng dữ liệu giả lập: account đã duyệt không đổi hiện Đã cập nhật/Nhập kỳ tiếp theo; account tracking09/07 nguồn01–31/08 hiện khoảng09–31/07; form duyệt có hai xác nhận độc lập cho chưa phân loại và thiếu nguồn. Duyệt xong S1 giữ khoảng thiếu, báo cáo chuyển chỉ xem không tạo bản trùng. Một coder ngữ cảnh gọn triển khai và kiểm targeted, PO review UI, không gọi tester thứ hai. PO cho cập nhật8792 giữ nguyên dữ liệu người dùng. Bằng chứng mã/tests/giới hạn tại outputs/p03-handoff.md. Công nợ chưa thuộc bản này.

Ghi nhận giao việc ban đầu:

PO giao một coder mới với ngữ cảnh riêng ngắn, không tiếp tục coder/tester lịch sử dài. Scope: tổng quan nguồn/độ phủ/trạng thái, hướng dẫn bước tiếp theo đúng, chặn duyệt lặp không thay đổi và xác nhận khoảng nguồn thiếu. Không tự thao tác dữ liệu thật. PO review một lần bản bàn giao; chưa có kết quả P03. Công nợ là đợt sau, chưa đưa vào cùng phạm vi.

### Sửa lỗi ngày theo dõi và nguồn đã loại — P02.1, 09/10/2026

Tech-999 đã lưu đúng mốc09/07/2026 nhưng file01/08–29/09 bị loại vẫn hiện lỗi lịch sử trước khi sửa mốc. Đã tách kết quả hiện tại với lịch sử loại, thêm Đưa lại vào kiểm tra và hướng dẫn khi nhập lại file cùng hash. Hiển thị mốc/kỳ theo DD/MM/YYYY, cảnh báo khoảng09–31/07 chưa có nguồn. Không sửa số dư hoặc tự ghi giao dịch thật. Tester3 ca hồi quy độc lập đạt; coder102 tests đạt. PO mở lại đúng Tech-999 qua UI xác nhận ngày09/07, không còn lỗi mốc hiện tại, nút đưa lại nguồn và cảnh báo khoảng thiếu hiện đúng. Batch thật giữ DISMISSED chờ người dùng chủ động xử lý. Bằng chứng test nằm trong outputs/p02-qa/reopen-regression.log và REPORT.md.

### P02 đã qua kiểm tra, cập nhật bản dùng thử — 09/10/2026

PO đã kiểm trực tiếp trên dữ liệu QA riêng chuỗi tạo sai→sửa→hủy xóa→xóa mềm→khôi phục→nhập→phân loại→duyệt→đổi tên→lưu trữ→xem S1→khôi phục mobile→điều chỉnh→reload. Số dư và nguồn giữ đúng; S1 giữ tên/số tại thời điểm duyệt. [Bằng chứng PO UI](outputs/p02-qa/PO-UI-REVIEW.md). Tester độc lập đạt 11/11 ca backend P02; coder báo 99 kiểm tra hồi quy đạt. [QA](outputs/p02-qa/REPORT.md), [handoff](outputs/p02-implementation-handoff.md), [manifest](outputs/p02-build-manifest.json).

PO cho cập nhật tại URL8792 trên dữ liệu thử cũ, không thay dữ liệu tài chính thật. Tài khoản đã có nguồn/tiền dùng lưu trữ thay xóa; số dư đầu/mốc/số tài khoản đã ghi không được sửa trực tiếp. Vẫn chỉ là phần ngân hàng, không tuyên bố hoàn tất danh mục/đầu tư. Những dòng giao việc dưới đây giữ lịch sử bắt đầu đợt.

Người dùng yêu cầu chủ động hoàn thiện, không hỏi lại tiểu tiết. PO đã giao coder và tester tiếp tục: sửa/xóa mềm/lưu trữ/khôi phục tài khoản, bảo toàn lịch sử, làm rõ các bước thao tác. Phạm vi PRODUCT-SPEC phần P02; tiêu chí ACCEPTANCE phần P02. Coder sở hữu mã ứng dụng, tester sở hữu kiểm tra độc lập, PO sở hữu yêu cầu và review hành trình. Chưa có kết quả nghiệm thu P02; không coi P01 đủ dùng hằng ngày chỉ vì test đạt. Không cần thêm câu trả lời từ người dùng cho đợt này.

### Bàn giao dùng thử P01 — 09/10/2026

PO cho đưa dùng thử phần ngân hàng trên dữ liệu riêng. URL http://127.0.0.1:8792/; launcher `Start PCMS P01.command`; dữ liệu `outputs/p01-user-trial`. Không coi đây là nghiệm thu toàn bộ N0–N5 hoặc xác nhận số tài chính thật. Các đoạn ngày 08/10 và cũ hơn bên dưới là lịch sử tiến độ.

- Coder triển khai, PO không viết mã ứng dụng. [Handoff](outputs/p01-implementation-handoff.md) và [manifest](outputs/p01-build-manifest.json) ghi mã bàn giao, cách chạy và giới hạn. Coder báo 88 kiểm tra hồi quy đạt và kiểm cú pháp JavaScript đạt.
- Tester độc lập kiểm 10 ca backend cùng một ca bổ sung khôi phục nhập sai thứ tự; [báo cáo QA](outputs/p01-qa/REPORT.md), log và hash trong cùng thư mục. UI đã kiểm hai đợt 100→115→112 triệu, lọc không cắt báo cáo, S1/S2, restart, restore sang bộ riêng và giữ lựa chọn sau restart; mobile 390px và phân trang 25 dòng thành 20/5. Chuyển nội bộ được kiểm backend, chưa kiểm toàn luồng UI.
- PO trực tiếp tạo tài khoản mẫu qua UI, nạp/đối soát/ghi file đầu, phân loại chi 5 triệu, reload giữ số dư 115 triệu và 1 dòng chưa rõ. PO kiểm riêng checkbox chọn cả trang, chọn một phần, bỏ chọn; trạng thái đúng sau bản vá. Bản dùng thử để người dùng tiếp tục thao tác chưa có snapshot duyệt.
- Đã sửa trong review: phần phân bổ chưa rõ; khóa sửa giao dịch đã duyệt; đối soát trước ghi; trạng thái nút phân trang/checkbox; mở và tìm lại bản khôi phục; kiểm tra lại file bị chặn sau khi bổ sung nguồn trước. File nguồn không bị sửa.
- Giới hạn: local một người dùng, XLSX mẫu được hỗ trợ/VND; chưa kiểm hiệu năng lịch sử lớn, thiết bị mobile thật hoặc xác nhận phân loại/số dư cá nhân. Các engine công nợ, Energy, tài sản, phân tích đầu tư chưa thuộc bản này. Chi tiết từng ca chưa kiểm được ghi trong báo cáo QA. Nút kiểm tra lại nguồn mới được kiểm backend, chưa chạy lại toàn hành trình UI sau bổ sung cuối.

Việc tiếp theo của PO: tiếp nhận phản hồi sử dụng phần ngân hàng, ưu tiên lỗi theo tác động, sau đó chuẩn bị bức tranh tài chính và công nợ dựa trên nguồn đã tin được. Không yêu cầu người dùng điều phối coder/tester.

**Cập nhật 08/10/2026 — PO đã mở đợt P01:** Thạch giao PO điều phối sản phẩm và trải nghiệm; PO không làm coder. Phạm vi ở PRODUCT-SPEC §7.1, kiểm tra ở ACCEPTANCE §0. Đã giao việc cho hai agent coder và tester độc lập trong task PO. Coder đang triển khai; tester đang chuẩn bị fixture/kiểm tra. Chưa có kết quả nghiệm thu P01. Các đoạn trước ngày này mô tả trạng thái lịch sử, không khôi phục yêu cầu Thạch điều phối từng mốc.

### Giao việc P01

**PO (task hiện tại):** giữ phạm vi, giải quyết quyết định sản phẩm, review trải nghiệm xuyên suốt và quyết định đủ điều kiện đưa dùng. Không tự sửa mã ứng dụng. Mọi phát sinh làm thay đổi tiền hoặc phạm vi báo về PO; không chuyển câu hỏi kỹ thuật cho người dùng.

**Coder — đã nhận, đang triển khai:** đọc PRODUCT-SPEC, ACCEPTANCE §0 và phần hiện trạng này. Rà src/pcms và bản mẫu 05.2; đề xuất phần tái sử dụng và một đường ứng dụng chính, không duy trì thêm bản mẫu cạnh tranh. Triển khai P01 theo §7.1 trên dữ liệu thử riêng, bảo toàn dữ liệu hiện có. Bắt đầu bằng nhập/lưu nguồn và lịch sử liên tục, sau đó phân loại/duyệt/điều chỉnh, cuối cùng backup/restore. Bàn giao cách chạy, phạm vi file thay đổi, bằng chứng kiểm tra, hạn chế và định danh bản bàn giao để QA tái hiện. Không tự mở rộng nghiệp vụ hoặc đánh dấu PO đã nghiệm thu.

**Tester — đã nhận, đang chuẩn bị kiểm độc lập:** chuẩn bị bộ ca P01-01–08 và dữ liệu kỳ vọng độc lập; kiểm ứng dụng coder bàn giao, không chỉ đọc báo cáo coder hoặc chạy lại kiểm tra bản mẫu. Được viết fixture/test/báo cáo, không sửa mã sản phẩm để làm test qua. Ghi lỗi có bước tái hiện, kỳ vọng/thực tế, mức ảnh hưởng và bản được kiểm; kiểm lại lỗi đã sửa. Dùng bộ dữ liệu riêng, không thao tác dữ liệu vận hành. Khi chưa có bản mới, chỉ chuẩn bị ca và rà khoảng trống, không báo PASS.

**Cách phối hợp:** coder sở hữu mã sản phẩm; tester sở hữu bộ kiểm tra/báo cáo; PO sở hữu ba tài liệu hiện hành. Coder và tester không cùng sửa một file. Hiện thư mục chưa là Git repository theo kiểm tra 08/10; không giả định có worktree/commit. Khi có người nhận triển khai, coder phải thiết lập cách cô lập và định danh bản kiểm tra trước thay đổi; việc đó không cho phép ghi đè dữ liệu cũ. Đã khởi chạy /root/coder và /root/tester dưới điều phối PO; không yêu cầu người dùng tạo hoặc quản lý tab.

**Việc tiếp theo:** coder bàn giao bản chạy trên dữ liệu P01 riêng; tester kiểm độc lập; PO review trải nghiệm trước khi đưa người dùng thử. PO theo dõi báo cáo, kiểm soát phạm vi và giải quyết các điểm chặn; người dùng không phải chuyển yêu cầu giữa các vai trò.

**Đã chuyển sang thiết kế bản dùng thử theo yêu cầu “Làm đi” và “tiếp tục đi”.** Bàn giao bản mẫu độc lập tại `outputs/design-review-v1/index.html`, sơ đồ màn hình/giải thích ở PRODUCT-SPEC mục 8, mốc hiện hành N0–N5 ở ACCEPTANCE mục 2. Dừng phỏng vấn rộng; giải quyết điểm mở qua review cụ thể.

Chưa thay ứng dụng vận hành trong `src/`, cấu hình hoặc dữ liệu tài chính. N0 có bản mẫu để review, chưa được Thạch nghiệm thu; N1–N5 chưa triển khai theo baseline 2.0. Không coi quyền tạo mẫu là cho phép giao dịch thật hoặc tự duyệt chính sách còn mở.

## 2. Đối chiếu ứng dụng

“Có” là kết quả đọc mã và hồ sơ bàn giao cũ, không phải chạy lại giao diện trong lần gom tài liệu.

| Phần | Hiện trạng | Khoảng thiếu |
|---|---|---|
| Tài khoản | Có ngân hàng/sàn, nguyên tệ, số dư đầu và mốc | Vẫn bắt buộc pool/mục đích; chưa đạt R02 |
| Import | CSV, XLSX mẫu, kiểm tra và xử lý nghi trùng | Chưa bố cục chung R03; cần rà xử lý toàn lịch sử theo yêu cầu mới |
| Lịch sử | Số dư và biến động theo khoảng ngày | Chưa đầy đủ sao kê hợp nhất tracking → hôm nay/độ phủ nguồn; phần phân loại có thể thành nhiều dòng |
| Phân loại | Chưa rõ, tách phần, thay thế giữ lịch sử | Chưa quản lý danh mục/đối tượng đầy đủ R06 |
| Công nợ | Bên liên quan, từng khoản hai chiều, gốc/lãi, tổng nguyên tệ | Lãi xác nhận thủ công; chưa chốt ngoại lệ, tính lãi tự động |
| Shop A | Có tài sản doanh nghiệp trong demo | Chưa có nghiệp vụ shop/nhà cung cấp/đơn hàng/tồn kho; chưa đáp ứng R08 |
| Tài sản | Có bốn nhóm tài sản, định giá, nơi giữ trong demo | Chưa chứng minh đủ giá vốn/lợi nhuận/quyền sở hữu/nghiệp vụ sàn thực |
| Báo cáo | Có ngày/khoảng ngày, snapshot và FX demo | Chính sách thật chưa chốt; cần chọn lại báo cáo ưu tiên |
| Duyệt/AI | Có quyết định mô phỏng, phân tích quy tắc cố định | Chưa phân quyền thật hoặc LLM; không có bằng chứng Dũng duyệt số thật |
| Lưu trữ | Phiên bản trạng thái, sửa thay thế, backup/restore | Cần kiểm theo phạm vi mới; không tuyên bố sổ kế toán production |

Hai lõi tồn tại: `src/pcms/core.py` là journal pilot cũ; `product.py` và `continuous.py` là app dựa trên trạng thái. Không dùng tài liệu pilot để khẳng định app có kế toán kép hoàn chỉnh.

## 3. Bằng chứng và giới hạn

- Đã rà các nhóm tài liệu yêu cầu, use case v1.1, domain, quyết định demo, roadmap và nghiệm thu; đối chiếu trực tiếp mã tài khoản/lịch sử/công nợ.
- [Biên bản liên tục cũ](docs/archive/2026-09-29/docs/continuous-acceptance.md) ghi 77 tests Python và browser smoke đã qua ngày 28/09. Đây là bằng chứng lịch sử, không chạy lại lần này và không thay thế A01–A12.
- `config/owner-settings.json` ghi Dũng duyệt, giữ nguyên tệ, hướng USDT; scope_approved=false và chưa có milestone được nghiệm thu. File giữ nguyên; trường Dũng nay đã lỗi thời so với R10 mới (Thạch duyệt). Cập nhật cấu hình khi được phép triển khai, không lấy cấu hình cũ làm yêu cầu.
- Hai XLSX thật là mẫu nguồn đã có staging; không lấy số trong mẫu hoặc ảnh nợ làm số dư hiện tại, không import lại lần này.
- Không kiểm kê lại số giao dịch đang dùng vì người dùng có thể tiếp tục thao tác demo. Không đặt lại dữ liệu hoặc tự thay bằng dữ liệu giả lập mới.
- Mã, schema và cấu hình khác PRODUCT-SPEC là khoảng cách triển khai, không phải lý do sửa yêu cầu cho khớp demo.

## 4. Bộ cũ đã được xử lý thế nào?

Tất cả Markdown cũ lưu nguyên nội dung trong [kho lịch sử](docs/archive/2026-09-29/INDEX.md), có manifest đường dẫn và SHA-256. Liên kết trong bản gốc được giữ nguyên nên có thể không chạy từ vị trí lưu trữ. Dùng chỉ mục kho để tra cứu.

| Nguồn cũ | Thay thế / quyết định |
|---|---|
| README, product-brief, implementation-readiness | PRODUCT-SPEC mục 1–3, 6–7; bỏ mặc định Sheets-only/theo tháng |
| UC-01/02/03/07/08 | F01/F06; UC-03 đã gộp UC-02 |
| UC-04/05/06 | F01/F02; nhập, phân loại, chuyển nội bộ |
| UC-09/10/11/12 | F03; công nợ từng người/từng khoản |
| UC-13/14/15/16 | F05; tài sản và báo cáo, hỏi lại độ chi tiết |
| UC-17/18/19 | Phân tích, phân bổ, chốt báo cáo chưa cam kết cho lần tới |
| UC-20/21 | F06, A12; truy vết/sửa/sao lưu |
| domain-model, architecture, data-dictionary | PRODUCT-SPEC mục 4–5; thiết kế chi tiết cũ chỉ tham khảo |
| ai-analysis-contract, adr-register | PRODUCT-SPEC mục 6; quyết định cũ không tự có hiệu lực lại |
| milestones, milestone-board, acceptance cũ | ACCEPTANCE N0–N3 dự thảo; mã cũ giữ lịch sử |
| product-trial-decisions, revision-history | Tách yêu cầu R01–R13 khỏi lựa chọn demo; nhật ký mới bên dưới |
| Bốn runbook và schema README | Tham khảo kỹ thuật lịch sử, không chỉ đạo triển khai mới |
| Trao đổi sau UC v1.1 về danh mục, Shop A, tài liệu rời rạc | R06/R08/R13, F02/F04; không bỏ sót vì chưa có trong doc cũ |
| Handoff ban đầu của Dũng | Giữ tầm nhìn vốn/tài sản; không đưa mọi mong muốn vào scope kế tiếp |

## 5. Nhật ký quyết định hiện hành

| Mã / ngày | Quyết định | Căn cứ / hiệu lực |
|---|---|---|
| D01 / 29/09/2026 | Bộ ba root là tài liệu hiện hành; README dẫn đường; bộ cũ lưu lịch sử | Theo yêu cầu Thạch, có hiệu lực quản lý tài liệu |
| D02 / 29/09/2026 | Dừng triển khai để phỏng vấn | Yêu cầu trực tiếp; chưa gỡ |
| D03 / 29/09/2026 | Chia xác nhận/đề xuất/còn mở; không kế thừa demo thành policy thật | Cách tổ chức của người triển khai, không thay quyết định nghiệp vụ |
| D04 / 29/09/2026 | N0–N3 và A01–A12 là dự thảo phỏng vấn | Chưa cam kết scope hoặc nghiệm thu |

## 6. Sổ phỏng vấn

| Vòng | Trạng thái | Câu trả lời / ảnh hưởng |
|---|---|---|
| I1 — Ưu tiên, shop, người vận hành | Đã trả lời một phần | Thạch nêu luồng bốn bước, trực tiếp tải/đối chiếu/phân loại; đầu ra danh mục, số dư hạng mục, nơi giữ, tỷ trọng. Mức shop và điểm duyệt còn mở |
| I2 — Import/phân loại | Chưa hỏi | Chờ I1 |
| I3 — Công nợ/shop/tài sản | Đã trả lời phần tài sản và sàn | BĐS/coin có vốn và giá hiện tại; cổ phiếu pending phase sau. Binance, BingX và ví riêng đã xác nhận; cần map mua/bán, futures, margin, staking/Earn theo từng nơi. Công nợ/shop và quy tắc chi tiết còn mở |
| I4 — Báo cáo/nghiệm thu | Đã có thông tin ban đầu | Tài khoản duyệt theo mỗi đợt tùy chọn: xem tóm tắt phân loại → approve → snapshot theo thời điểm duyệt, thay mốc tuần cố định. Thạch approve cả khi còn nhãn chưa phân loại; điều chỉnh tạo phiên bản mới với quyết định/lý do, giữ bản cũ. Chốt tháng pending; tỷ trọng theo giá hiện tại. Lệch tiền, nguồn giá/mẫu số/FX còn mở. Chưa được triển khai lại |

Sau mỗi vòng ghi câu trả lời, cập nhật R/F/A liên quan, nêu điều đổi/hoãn. Trước lập trình, trình Thạch phạm vi và mốc cuối để xác nhận. Không cần Thạch đọc architecture hoặc chọn công nghệ.

### I1 — Ghi nhận câu trả lời ngày 29/09/2026

Thạch mô tả: (1) tải sao kê và đối chiếu dữ liệu/số dư với kỳ trước; (2) phân loại nợ, chi tiêu, mua BĐS/cổ phiếu, nhập hàng shop, cho vay; sàn theo chuyển tiền, mua coin, trading; (3) khóa sổ/chốt kỳ; (4) xem danh mục, số dư hạng mục, nơi giữ tiền, tỷ trọng. Đã cập nhật R14–R16, bổ sung nghiệm thu A13–A15. Chưa coi đây là xác nhận toàn bộ F01–F06 hay cho phép code.

Câu hỏi tiếp theo tập trung: kỳ và phạm vi khóa; ý nghĩa số dư/giá trị hạng mục; loại nghiệp vụ sàn. Chi tiết vai trò Dũng, mức shop và mức tự động đối chiếu vẫn để mở cho lượt tiếp theo. Hai ảnh chỉ minh họa quy trình, chưa xác nhận ý nghĩa toàn bộ số liệu.

### I3/I4 — Câu trả lời ngày 30/09/2026

Thạch xác nhận: có thể chốt tuần từng tài khoản, tháng khóa toàn bộ tài khoản và danh mục; từng nhóm BĐS/cổ phiếu/coin có quản lý riêng, thấy cả vốn và giá hiện tại, tỷ trọng theo giá hiện tại; trên sàn dùng mua/bán, futures, margin, staking và Earn. Đã cập nhật R16–R19, F05/F06, A13–A15; không đổi code/dữ liệu và chưa cho phép triển khai lại.

Lượt tiếp theo: điều kiện chốt khi còn lệch/chưa phân loại; cách sửa sau khóa và vai trò Dũng; cách cập nhật giá. Sau đó cần hỏi mẫu số tỷ trọng/FX, vốn sau bán một phần, sàn cụ thể và dữ liệu cho các nghiệp vụ sàn. Không coi yêu cầu mới là demo hiện tại đã hỗ trợ.

### I4 — Làm rõ mốc duyệt tài khoản, 30/09/2026

Thạch điều chỉnh: có thể tải sao kê ba ngày một lần; nhập → phân loại → xem lại báo cáo tóm tắt phân loại → approve → lưu snapshot theo mốc thời gian duyệt. Cập nhật R17/F06/A13; cách diễn đạt chốt tuần ở mục lịch sử phía trên đã được thay thế bằng mốc xử lý tùy chọn. Chưa có chỉ dẫn hủy chốt tháng toàn danh mục, nên giữ yêu cầu đó và hỏi quan hệ hai cấp.

Chưa chốt người bấm approve (Dũng đã được xác nhận trước), phạm vi snapshot, điều kiện chặn, sửa sau duyệt và các mốc nguồn khác nhau. Đề xuất tách thời điểm duyệt khỏi ngày cuối dữ liệu nguồn, không coi duyệt hôm nay là đủ sao kê tới hôm nay. Không sửa code/dữ liệu; tiếp tục phỏng vấn.

### I4 — Quyết định về approve và sửa số liệu, 30/09/2026

Xác nhận mới thay phần tương ứng trong các lượt lịch sử phía trên: Thạch trực tiếp bấm approve; giao dịch chưa phân loại được gắn nhãn/mục riêng và vẫn approve snapshot; chốt tháng pending tới sau sử dụng thử; khi sai giữ snapshot cũ và tạo phiên bản mới với quyết định/lý do điều chỉnh. Đã sửa R10/R17, thêm R20–R22, F06 và A16–A18.

Người dùng yêu cầu phản biện approve chưa phân loại và giải thích các tình huống lệch số dư. Đề xuất: tách trạng thái đối soát/phân loại/duyệt; báo cáo không che khoản chưa rõ; số dư lệch hoặc thiếu bằng chứng chỉ lưu nháp, chờ xử lý trước approve chính thức. Phần chặn lệch là đề xuất, chưa được xác nhận. Cấu hình và code vẫn giữ nguyên; các hành vi demo cũ không được coi là đã đạt yêu cầu mới. Chưa được phép triển khai lại.

### I3 — Sàn, ví và cổ phiếu, 30/09/2026

Thạch dùng Binance, BingX, ví riêng; chưa cập nhật danh mục cổ phiếu, để pending phase sau. Cập nhật R01/R23/R24, F05, A14 và đề xuất A19. Cổ phiếu không là điều kiện nghiệm thu bản thử tới; không suy ra được phép bỏ giao dịch cổ phiếu nếu có trong sao kê.

Cần hỏi: nghiệp vụ dùng trên từng sàn; số ví và mạng, giữ/chuyển hay DeFi; phạm vi bắt đầu tracking (toàn lịch sử hay số dư/vị thế tại mốc có nguồn). Cơ chế import/kết nối chưa chốt. Tiếp tục BA, không sửa code/config/dữ liệu; không tự coi đã phê duyệt các đề xuất nghiệp vụ ở lượt tư vấn trước.

### I3 — Nghiệp vụ hai sàn, ví và mốc bắt đầu, 30/09/2026

Thạch xác nhận Binance và BingX đều trade/lưu trữ/Earn như nhau, dùng hai sàn nhằm giảm rủi ro tập trung. Có nhiều ví, gồm mạng BSC/TRC theo cách gọi người dùng; trước mắt sẽ liệt kê coin từng ví, không muốn tổ chức quy trình theo mạng. Chọn theo dõi từ mốc bắt đầu, chưa chọn ngày cụ thể. Đã cập nhật R23/R25/R26 và A20; cổ phiếu vẫn pending.

Đề xuất tiếp: danh sách trạng thái đầu mốc có coin/số lượng, Earn, ký quỹ/vị thế/nợ nếu có; thiếu vốn không tự suy ra. Ví là nơi giữ đa mạng ở giao diện, mạng/token chỉ làm rõ khi cần định danh/đối soát, không tự mở rộng tích hợp on-chain. Chưa triển khai code hoặc cập nhật dữ liệu thực.

### I3 — BĐS, shop và business cho vay, 30/09/2026

Thạch xác nhận BĐS phần lớn sở hữu toàn bộ, hai mảnh góp vốn, một mảnh thế chấp vay, một chung cư thanh toán tiến độ; chưa suy số tài sản tổng hoặc nhóm loại trừ nhau. Một shop nhỏ nhập hàng theo đợt cần công nợ/lợi nhuận. Có business cho vay lãi 1,5%/tháng. Cập nhật R27–R29, F03/F04, đề xuất mô hình và A21–A23. Chưa có số liệu tài sản/vay thực hoặc công thức lãi được chốt.

Tư vấn theo hướng ba sổ chi tiết cùng dùng giao dịch nguồn; tách gốc/lãi, tiền/hàng/công nợ và giá trị quyền lợi. Câu hỏi kế tiếp ưu tiên cách trả/tính lãi, nguồn vốn cho vay và dữ liệu bán hàng/tồn kho của shop. Không xác nhận tính hợp pháp lãi suất, không tự đặt lãi phạt/lãi kép, không code hay sửa dữ liệu.

### I3 — Thu lãi theo dư gốc còn lại và shop đơn giản, 30/09/2026

Thạch xác nhận: thường trả lãi hằng tháng; mỗi lần vay là khoản riêng, có thể trả món vay sau trước; được trả gốc một phần, trả lãi trên dư gốc trước khi trả tới mốc thanh toán rồi tính tiếp trên dư gốc còn lại. Nguồn cho vay thường tiền riêng. Shop được giao thiết kế đơn giản. Cập nhật R29–R32 và A24–A26, không code.

Đề xuất shop tối giản gồm hàng/nhà cung cấp, nhập theo đợt, bán tổng hợp theo mặt hàng, tiền/công nợ/chi phí và giá vốn bình quân sau mỗi lần nhập; đây là phương án người triển khai đề xuất. Câu hỏi trọng tâm còn lại: tính ngày lẻ và lịch thu lãi. /30 chỉ là phương án minh họa, không tự coi đã được chốt, không tự thay thỏa thuận thực hoặc tính lại khoản cũ.

### I3 — Shop pending; business stake tạo sản phẩm, 30/09/2026

Thạch hoãn shop; chuyển tìm hiểu hoạt động có coin stake, lãi, sản phẩm tạo hằng tháng để bán hoặc cho thuê. Cập nhật R28/R32, F04 pending, R33/F07 và A27 dự thảo; các ca shop hoãn. Không suy rằng lãi và sản phẩm là hai khoản riêng, hoặc sản phẩm là NFT/token/vật phẩm/dịch vụ. Đề xuất sổ stake/quyền lợi/sản phẩm/bán/thuê nối nguồn tiền chung. Cần hỏi bản chất sản phẩm và điều kiện quyền lợi trước chọn cách định giá/tính lợi nhuận. Các câu hỏi ngày lẻ cho vay giữ mở, không bị xóa. Chưa triển khai code hoặc sửa dữ liệu.

### I3 — Xác định mô hình TRX/Energy, 30/09/2026

Thạch xác nhận Energy trên TRON để giảm phí; thưởng stake là coin thêm có thể claim theo ngày, mô tả theo APY năm. Có bán TRX cho khách và thu gộp với tiền thuê Energy. Cập nhật F07/R33/R34, A27–A29. Thay giả thuyết sản phẩm tồn kho hằng tháng bằng đơn dịch vụ tài nguyên; các mô tả lịch sử F07 cũ được thay ngay trong spec.

Đã tra tài liệu TRON chính thức về resource/delegation/reward. Tách sự thật cơ chế khỏi điều khoản dịch vụ người dùng; chưa biết trực tiếp hay trung gian, giá thuê, thời hạn, tiền thu. Đề xuất ghi thưởng/thuê/bán TRX riêng và phân bổ tiền chung, không tính trùng thu nhập hoặc vốn. Không code, không tác động ví/tài sản; shop còn pending, câu hỏi ngày lẻ cho vay còn mở.

### I3 — Vận hành Energy trực tiếp, đơn lẻ/tháng và tiền thu, 30/09/2026

Thạch xác nhận tự stake/cấp Energy từ ví; tính theo số lượng cho một lần hoặc gói 1 triệu Energy/tháng; khách chủ yếu trả USDT, đôi lúc VND. Cập nhật R34–R36 và A30–A31 đề xuất. Không suy ra gói tháng có lượng tiêu thụ cố định hoặc nghĩa vụ cấp bù mỗi ngày. Trả trước/sau chưa được trả lời.

Đề xuất lưu báo giá/đồng thanh toán/tỷ giá thỏa thuận riêng, không tạo USDT giả khi thu VND. Cần hỏi đúng ba điểm còn thiếu: ý nghĩa gói tháng; nhịp thanh toán; cách chốt giá VND. Không code, không kết nối hoặc giao dịch ví; tiếp tục phỏng vấn.

### I3 — Gói Energy thu phí tháng cố định, 30/09/2026

Thạch mô tả gói như data 3G: thuê lượng đã thỏa thuận một tháng, dùng hay không vẫn trả, ví dụ 100 USD. Có khách thu trước, khách quen thu sau. Ghi R37–R38 và A32–A33; không suy USD bằng USDT, không coi đã xác định cơ chế kỹ thuật hạn mức. Quy đổi VND ở câu trước chưa được trả lời.

Đề xuất điều khoản từng khách được sao lưu trên đơn, theo dõi dịch vụ và tiền riêng. Cần hỏi tiếp giá USD hay USDT và cách thỏa thuận VND, để tránh tự chọn tỷ giá. Không triển khai code, không thay cấu hình/data, các vấn đề ngày lẻ cho vay và định giá còn mở.

### I3 — Bổ sung câu 3 về tiền VND, 30/09/2026

Thạch xác nhận lấy USDT nhân tỷ giá lúc thanh toán. Cập nhật R36/R39, A31/A34; thay trạng thái câu hỏi quy đổi còn mở ở lượt trước về mặt thời điểm/công thức. Nguồn tỷ giá và cách làm tròn chưa được xác nhận; đề xuất nhập tỷ giá thực tế từng lần thu. Không tự chọn USD=USDT hoặc nguồn giá trực tuyến. Không code/data changes.

### I3 — Thu gộp Energy theo khả năng vận hành, 30/09/2026

Thạch nói có thể ba tháng mới thu một lần vì không luôn có nguồn lực thu tiền. R40 ghi thu linh hoạt; chưa coi là khách được cam kết hạn nợ ba tháng, không suy hợp đồng tự gia hạn. Đề xuất phí theo kỳ có căn cứ cung cấp, bảng kê gộp theo khách, tiền theo ngày thực nhận, hạn cam kết riêng và chưa thu khác quá hạn. Thêm A35; không code, không gửi nhắc khách hay lập automation.

### I3 — Không quản lý gia hạn Energy, 30/09/2026

Thạch tự quản lý việc hết tháng có tiếp tục cấp/gia hạn; yêu cầu không đưa vào nghiệp vụ. Cập nhật R41, thu hẹp F07 và tiêu chí: không workflow/nhắc gia hạn hay tự sinh phí; chỉ khoản phí người dùng nhập/xác nhận, công nợ, tiền thu và báo cáo. Không diễn giải thành bỏ toàn bộ business Energy. Không hỏi tiếp điều kiện gia hạn; không code/data changes.

### I3 — Lãi tính theo ngày, ưu tiên thực thu, 30/09/2026

Thạch xác nhận tính lãi theo ngày từ ngày cho vay; thực thu có thể thấp hơn dự tính do khách xin giảm và cần ưu tiên thực thu. Ghi R42, A36–A37; không diễn giải thành thu hằng ngày hoặc đã chọn /30. Đề xuất giữ lãi dự tính/thực thu/miễn giảm/còn phải thu riêng, miễn giảm do Thạch xác nhận, không tự xóa chênh lệch. Hệ số ngày, biên ngày trả và làm tròn còn mở. Không code/config/data changes.

### I3 — Chốt 500 VND/triệu/ngày, 30/09/2026

Thạch xác nhận đơn giá 500 đồng/1 triệu/ngày, tương đương 1,5%/30; muốn nhập lãi theo ngày hoặc theo tháng quy ước 30 ngày. Cập nhật công thức đang có, R43 và A38–A39. Công thức luôn nhân số triệu gốc thực tế và số ngày của từng đoạn dư gốc, không chỉ nhân số ngày với 500 cho mọi khoản. Phân biệt lãi suất đầu vào và tiền thực thu. Không coi đây là xác nhận toàn bộ phạm vi hoặc cho phép code; chưa sửa ứng dụng/data.

### D05 — Chuyển từ phỏng vấn sang thiết kế, 05/10/2026

Thạch yêu cầu tránh sa lầy nghiệp vụ, đồng ý bước tiếp theo và giao “Làm đi, sau khi có kết quả thì giải thích chi tiết”; sau đó yêu cầu tiếp tục. Đã làm bản mẫu 9 màn hình bằng dữ liệu giả lập, bốn luồng bấm thử chính, các hồ sơ BĐS và bố cục crypto, sơ đồ màn hình và N0–N5 thay bảng milestone dự thảo cũ. Không tạo bộ yêu cầu thứ hai: mọi mô tả thiết kế nằm trong PRODUCT-SPEC, tiêu chí ở ACCEPTANCE.

Các giả định mẫu được công khai: chặn approve lệch tiền; ngày lãi nhập trực tiếp; tỷ trọng tách phạm vi nguyên tệ; dữ liệu/giá mẫu; các kịch bản vay/Energy độc lập sao kê; chưa hỗ trợ import sàn/engine phái sinh. Shop/cổ phiếu/khóa tháng pending, gia hạn Energy ngoài phạm vi. Tải lại trang đặt lại dữ liệu, chưa là app vận hành.

### Kiểm tra bản mẫu 01 — 05/10/2026

Đã chạy `outputs/design-review-v1/check.cjs` bằng Chrome headless trên file độc lập, ghi kết quả ở [verification.json](outputs/design-review-v1/verification.json). Chín nhóm kiểm tra qua: import lặp không tăng dòng; lệch chặn duyệt theo giả định; approve còn chưa rõ; điều chỉnh cần lý do và giữ S1; lãi/gốc/miễn giảm; hai lần thu VND khác tỷ giá phân bổ đúng; mở các màn tham khảo; không tràn trang 390px/768px qua chín màn; không lỗi JavaScript. Các bảng dày dùng cuộn ngang trong khung nhỏ.

Đã xem ảnh màn tổng quan desktop và tài khoản mobile; các màn còn lại có ảnh bằng chứng trong cùng thư mục. Đây là kiểm tra bản mẫu, không nghiệm thu N1–N5 hoặc chứng minh sổ vận hành đúng. Không test lại app cũ, không thay source/config/private-data. Tập kết quả ghi thời gian chạy theo đồng hồ máy, ngày hồ sơ review dùng 05/10/2026 theo ngữ cảnh hiện tại.

Bản xem đang được phục vụ riêng tại http://127.0.0.1:8789 (chỉ thư mục bản mẫu, không phải app cũ ở 8787). Đã yêu cầu Codex mở tab xem; công cụ trả trạng thái queued. Có thể mở trực tiếp URL hoặc file index.html. Đã chỉnh nhãn khi thu đủ công nợ và bước approve hiển thị hoàn tất; bộ kiểm tra chạy lại sau chỉnh sửa.

### D06 — Review bản mẫu 02, 05/10/2026

Thạch chỉ ra thiếu chọn tài khoản/lịch sử 7 ngày/số dư chốt; thiếu tick phân loại hàng loạt; báo cáo thiếu kiểm đủ số tiền/số giao dịch/đối tượng; thiếu danh sách người vay/lịch sử; thiếu phân cách số và khách Energy/gói/người thanh toán. Đã ghi R44–R48 và A40–A44, cập nhật bản mẫu tại cùng URL/path. Bản 01 lưu trong archive-v1 trước chỉnh.

Bản 02 có 4 tài khoản trạng thái riêng, 50 dòng ngân hàng 1, báo cáo tổng và drill-down, tick nhiều dòng, snapshot lưu cả báo cáo; người vay và khách có danh sách/chi tiết riêng, phiếu thu gắn ID và tên đối tượng. Tất cả ô nhập tiền dùng phân cách nghìn theo tiếng Việt. Dữ liệu các tình huống vẫn độc lập, không tự cho rằng đã nối app vận hành. Chỉ sửa bản mẫu/tài liệu/kiểm thử; không src/config/private-data.

Kiểm tra bản mẫu 02 bằng Chrome đã đạt cả 7 nhóm trong [verification-v2.json](outputs/design-review-v1/verification-v2.json): chọn tài khoản/lịch sử, đối soát 50 dòng, phân loại hàng loạt, snapshot/điều chỉnh, người vay/khoản vay, khách Energy/thu tiền, bố cục 9 màn ở 390/768/1440px. Không phát sinh lỗi JavaScript. Đã xem ảnh desktop người vay và Energy cùng ảnh mobile; các bảng rộng cuộn ngang trong khung. Bộ mẫu ngân hàng 1 có tiền vào 71 triệu, tiền ra 597 triệu, từ số dư 1,5 tỷ còn 974 triệu. Đây là kiểm tra thiết kế tương tác, chưa nghiệm thu chức năng vận hành hoặc nhập sao kê thật.

### D07 — Review bản mẫu 03 · 05/10/2026

Theo 5 phản hồi tiếp theo của Thạch, đã tách dữ liệu cũ/mới và thêm bộ lọc dài hạn; đối chiếu số dư từng dòng; chọn người/món vay hoặc BĐS khi phân loại; báo cáo duyệt riêng; chứng từ liên kết món vay và tải phiếu giả lập; hồ sơ tất toán, xác nhận nghĩa vụ và báo cáo tuần/tháng/quý. R49–R53 và A45–A49 là yêu cầu/tiêu chí tương ứng. Chỉ sửa bản mẫu và tài liệu, không triển khai vào src hoặc dữ liệu thật.

Kiểm tra Chrome bản 03 đã đạt các ca trong `outputs/design-review-v1/verification-v3.json`: tách cũ/mới; các khoảng lịch sử; đối chiếu 50 dòng; gắn An/A-02 và Đất B; chặn thiếu liên kết; báo cáo màn riêng và snapshot; chứng từ và tải phiếu mẫu; báo cáo tháng/tuần/quý; tất toán có xác nhận. Không lỗi JavaScript, không tràn trang tại 390/1440px ở các màn bị ảnh hưởng. Đã xem ảnh báo cáo duyệt. Không coi đây là kiểm thử engine cho vay hay dữ liệu thật.

### D08 — Review bản mẫu 04 · 05/10/2026

Thêm tạo/sửa tài khoản với số dư đầu khóa, cây danh mục, tổng vào/ra đầu chi tiết và màn ghép hai đầu chuyển nội bộ. R54–R57/A50–A53 ghi yêu cầu và giới hạn. Bản 03 được lưu trước khi sửa. Chỉ thay bản mẫu/tài liệu/kiểm tra; không thay src, dữ liệu thật. Tài khoản mới chưa có import file thật; cây danh mục chưa tổng hợp cây đa cấp hoặc tự tạo đầy đủ hồ sơ BĐS; ghép mẫu cùng tiền/cùng nguyên tệ, cần xác nhận.

### D09 — Truy nguyên mọi danh mục · 05/10/2026

Thạch bổ sung mọi danh mục phải có lịch sử; số mua Đất A 600 triệu phải rõ các dòng cấu thành. Đã nối lịch sử danh mục và hồ sơ BĐS vào cùng registry nguồn của tài khoản trong bản mẫu, bổ sung 3 dòng cũ 200/150/250 triệu và chứng từ giả lập. Không còn dùng số vốn nhập tay của bảng BĐS cũ làm số đã đối soát. Khi nạp đợt mới, vốn cập nhật từ các dòng liên kết có trạng thái. R58/A54 ghi quy tắc; khác giá thị trường và giá hợp đồng. Các phần vay/Energy khác vẫn là tình huống độc lập như đã công bố.

Kiểm tra Chrome bản 04 đạt các ca trong `outputs/design-review-v1/verification-v4.json`: khóa số dư đầu, sửa hồ sơ, danh mục con, tổng chi tiết, ghép/khóa chuyển nội bộ, nguồn vốn Đất A 600 triệu/3 dòng và tăng 900 triệu/6 dòng sau import, nhóm cha 7 dòng gồm tài sản con không đếm đôi. Không có lỗi JavaScript; bố cục 390/1440px được kiểm tra. Đã xem ảnh hồ sơ Đất A và ghép nội bộ. Đây là kiểm tra bản mẫu, chưa nghiệm thu app vận hành.

### D10 — Chuẩn hóa nguồn sao kê · 06/10/2026

Đọc nguyên trạng Account statement (44).xlsx bằng openpyxl read-only về hành vi, không lưu sửa file. Kiểm 163 giao dịch A9:F171, tổng vào 956.528.226, ra 951.087.926, số dư đầu 215.875.951/cuối 221.316.251 VND; không chênh từng dòng, không trùng tham chiếu trong file. Nguồn có ngày nhưng không có giờ. Ghi R59/A55 về nguồn bất biến, bản ghi chuẩn, phân bổ phiên bản và phiếu đối chiếu. Không đưa sao kê thật vào bộ dữ liệu giả lập, không xuất/gửi thông tin khách. Chưa triển khai cơ chế lưu file/hash/import đa bank hoặc xuất chứng từ thật.

### D11 — Chấp thuận mô hình, bản mẫu 05 · 06/10/2026

Người dùng chốt mô hình và yêu cầu áp dụng sao kê (44). Tạo phiên bản tập trung luồng nguồn thật với statement-data.js/model-v5.js; bản 04 giữ nguyên dưới archive-v4 và có liên kết xem các luồng chưa nối. Dùng openpyxl chỉ đọc, sao lưu file gốc byte-exact trong nguồn bản mẫu. 163 dòng có source row/ref/raw values, không gán nghiệp vụ tự động. Danh mục/đối tượng/hồ sơ/phân bổ theo nguồn chung; Long/Bad cùng ID; phiếu một giao dịch, snapshot và audit trong phiên. Chưa triển khai app vận hành, upload đa bank, số dư đầu công nợ hoặc nghiệp vụ phi tiền tệ; không gọi đây là N1 hoàn tất.

Kiểm tra Chrome bản 05 đạt: import 163 dòng/idempotency; nguồn A9:F9/ref/không bịa giờ; xuất đúng một giao dịch; chặn sai phân bổ; Long/Bad cùng món; tổng nguồn; S1 bất biến/S2 cần lý do; bố cục 390/1440px. Không lỗi JavaScript. File nguồn sao lưu khớp SHA-256 bản gốc. Kết quả `outputs/design-review-v1/verification-v5.json`.

### D12 — Điều chỉnh UX theo V4 · 06/10/2026

Bản 05.1 gộp tài khoản/phân loại, khôi phục công cụ tài khoản và bộ lọc/chọn hàng loạt, giữ nguồn V5. Bản 05 trước sửa lưu ở archive-v5. Không quay về dữ liệu giả lập, không thay file nguồn hoặc src vận hành. Quy tắc mô hình không đổi.

### D13 — Workflow nhập liệu/phân loại/approve · 06/10/2026

Theo yêu cầu giảm scroll và quản lý trạng thái, bản 05.2 thay bố cục chung dài bằng bước nhập/đối soát có nút xác nhận khóa, sau đó bảng phân loại phân trang 20 dòng. Nhóm chờ/đã phân loại/tất cả, đếm theo dòng gốc; lưu hợp lệ đưa dòng sang nhóm đã xử lý, lưu nháp thiếu vẫn chờ. Approve phần còn chưa phân loại có xác nhận rõ. Chỉ thay bản mẫu và tài liệu; bản 05.1 lưu archive-v5.1.

Kiểm tra Chrome đạt các ca phase/status trong verification-v5.2.json: chặn phân loại/duyệt trước Nhập liệu OK; khóa nguồn; 20 dòng/trang; bulk/lưu đơn chuyển nhóm đúng; toàn đợt 163 dòng; xác nhận phần chưa rõ; khóa sau approve; mobile không tràn. Không lỗi JavaScript. Đã xem ảnh bảng phân loại.
