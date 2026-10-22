# Feature Specification: Sửa phân loại giao dịch (chức năng chung)

**Feature Branch**: `043-reclassify` · **Created**: 2026-10-22 · **Status**: Clarified (Q1 = A) — triển khai
**Input**: Thạch (22/10/2026) yêu cầu chức năng chung "Sửa phân loại" mở rộng từ ca Kết của spec 042: chuyển phần phân loại giữa danh mục, đổi đối tượng, đổi cả hai, hỗ trợ giao dịch chia nhiều phần; không chuyển tiền, không đổi tài khoản nguồn, không gộp giao dịch, không chuyển cả đối tượng cùng lịch sử. Tham chiếu: R84–R86, R136, R141, R169–R171, R185–R194; A58–A59; spec 036, 041, 042; Constitution I–IX.
**Cách làm Spec Kit**: các bước `specify/clarify/plan/tasks/analyze` thực hiện **thủ công** theo cấu trúc mẫu của dự án (không chạy slash command); bằng chứng là các file trong thư mục này và liên kết yêu cầu → task → test.

## Bản đồ tác động *(Constitution IX; tìm trong mã nguồn `origin/main` 5219342)*
- **Đường ghi phân loại duy nhất**: `p01.py` action `classify` (gọi từ hộp Phân loại, bulk, `category-correct-classification` của 042). Spec này **dùng lại** `classify` làm đường ghi; không tạo đường ghi song song. `category-correct-classification` trở thành trường hợp riêng của chức năng chung.
- **Kiểm tra quan hệ** (042): thành viên danh mục hiệu lực sau `cat_eff` (nhóm khoản vay `loan.group`, `object_moves`, `profile_merges`); bảo vệ chống trùng đầu vào giữ nguyên (không chạm `check_batch`, `legacy_preview`).
- **Liên kết nghiệp vụ đọc từ phân loại**: sổ Công nợ `debt_register` (phần `principal/interest` gắn hồ sơ khoản vay; dư nợ âm, trước mốc); bảng kê lãi `interest_settlement` (payments tham chiếu giao dịch, `interest_status` báo lệch); hoàn tất khoản vay `loan_completion.closure_basis` (băm cả allocations); BĐS `realty` (`pay_links` tham chiếu giao dịch; giá gốc từ phần `investment` + chi phí vốn hóa theo cờ `capitalize`); Tổng tài sản đọc Công nợ/BĐS.
- **Giao dịch đặc biệt**: chuyển nội bộ đã ghép (`transfer_match`); phiên điều chỉnh khi đã duyệt (`require_adjustment`); ghi chú bắt buộc (`note_required`); danh mục/đối tượng lưu trữ; lịch sử cũ (`legacy_entries`, có/chưa có tài khoản nguồn) — dòng lịch sử không đi qua `classify`.
- **Màn hình**: hộp Phân loại; lịch sử danh mục/đối tượng/tài khoản (`stmtRowHtml`); mục "Cần đối chiếu" (042); Kiểm tra phân loại; Danh mục; Đối tượng.
- **Số liệu**: tổng danh mục (cây, giao dịch đếm một lần ở cấp cha), tổng đối tượng theo danh mục phân bổ (R191), báo cáo tài khoản, snapshot (bất biến).
- **Spec/quy tắc cũ bị ảnh hưởng**: R191 (042) mở rộng; hành vi hiện tại của hộp Phân loại cho phép đổi gốc↔lãi, đổi khoản vay, bỏ phân loại phần đã liên kết nghiệp vụ — sẽ phải theo quy tắc A/B dưới đây ở **backend** (giao diện và API như nhau).

## Clarifications
### Đã chốt trong yêu cầu (không hỏi lại)
Nguồn bất biến; danh mục là cây; đối tượng hồ sơ chung, phải là thành viên danh mục đích; tên danh mục không quyết định nghiệp vụ; người nhận/chuyển trên sao kê không đổi theo đối tượng; mức A (đổi cách quản lý) cho sửa có xem trước + dấu vết; mức B (đổi bản chất/liên kết công nợ, lãi, tài sản, hợp đồng) không chuyển đơn giản — đi luồng nghiệp vụ hỗ trợ hoặc bị chặn rõ; đổi đối tượng có công nợ không phải chuyển nghĩa vụ nợ; đổi nhóm dài/ngắn hạn không sửa kỳ hạn; đổi gốc→lãi không chỉ thay nhãn; xem trước bắt buộc, mất hiệu lực khi đổi lựa chọn/dữ liệu; backend kiểm lại khi ghi; giao dịch đã duyệt theo phiên điều chỉnh, snapshot giữ nguyên; hoàn tác bằng điều chỉnh mới; chưa cần sửa hàng loạt.

### Câu hỏi còn mở (một lượt) — Session 2026-10-22
- Q1: Thay đổi **mức B** (sửa nhầm gốc↔lãi, gắn nhầm khoản vay của người khác, bỏ/gắn BĐS, đổi vốn hóa) khi **chưa có nghiệp vụ nào tham chiếu** giao dịch (bảng kê lãi, hoàn tất khoản vay, gắn đợt thanh toán BĐS) thì xử lý thế nào? Dữ liệu thật (bản sao chỉ đọc 22/10): 217 giao dịch, 165 đã duyệt; 19 giao dịch có phần nghiệp vụ và **cả 19 đều đã duyệt**; chưa có bảng kê lãi, hoàn tất hay gắn đợt BĐS nào. Phương án: (A) cho phép kể cả đã duyệt — qua phiên điều chỉnh, xem trước tác động dư nợ/lãi/giá gốc trước→sau, xác nhận riêng; (B) chỉ cho phép khi chưa duyệt; (C) chặn tuyệt đối. → A: **Thạch chọn (A)** (22/10/2026).

## Phân định A / B (áp ở backend, giao diện và API như nhau)
| Thay đổi | Mức | Xử lý |
|---|---|---|
| Đổi danh mục trong **cùng loại gốc** (vd Gốc vay › Kết → Gốc vay; Chi tiêu › A → Chi tiêu › B), cùng đối tượng/cùng liên kết | A | Cho phép, xem trước + lý do |
| Đổi đối tượng **không** mang liên kết nghiệp vụ (người/khác ↔ người/khác) | A | Cho phép |
| Đổi loại gốc giữa các loại **không nghiệp vụ** (thu nhập/chi tiêu/chưa phân loại/chuyển nội bộ chờ đối ứng), tuân quy tắc chiều tiền | A | Cho phép |
| Đổi giữa danh mục **vốn hóa / không vốn hóa** cho phần gắn BĐS | B | Cho phép có xem trước tác động + xác nhận riêng (Q1 = A) |
| Đổi/gỡ/gắn **hồ sơ khoản vay hoặc BĐS**; đổi loại gốc liên quan Gốc vay/Lãi vay/Đầu tư BĐS | B | Cho phép có xem trước tác động dư nợ/lãi/giá gốc + xác nhận riêng (Q1 = A); hộp Phân loại cũ không được làm thay đổi mức B nếu không có xác nhận này |
| Giao dịch chuyển nội bộ đã ghép; phần thuộc khoản vay đã hoàn tất; giao dịch có trong bảng kê lãi đã duyệt hoặc đã gắn đợt BĐS | B (tham chiếu) | Chặn, chỉ đường: mở lại/bỏ gắn ở màn tương ứng |
| Khoản vay có nhóm riêng: chọn danh mục khác nhóm | — | Chặn (hiển thị do nhóm quyết định), chỉ đường Công nợ → Chuyển danh mục |

## User Scenarios & Testing
### US1 — Sửa một phần phân loại (P1)
Từ dòng giao dịch (lịch sử danh mục, lịch sử đối tượng, màn phân loại, mục Cần đối chiếu) mở **cùng một** hộp "Sửa phân loại": nguồn chỉ đọc; các phần hiện tại; chọn phần cần sửa; chọn danh mục đích theo cấp → đối tượng hợp lệ của danh mục đó (hiện hồ sơ khoản vay/BĐS liên quan nếu có); lý do; **Xem trước**; **Xác nhận**.
1. Ca Kết (A58): 5 triệu ở Gốc vay › Kết, khoản vay của Kết → đích Gốc vay + Kết: giữ liên kết khoản vay; một giao dịch nguồn; lịch sử Kết tại Gốc vay có 5 triệu; Gốc vay › Kết không còn phần này; tổng Gốc vay và số dư không đổi; không xóa danh mục con.
2. Chuyển giữa hai danh mục cùng bản chất; đổi đối tượng; đổi cả hai.

### US2 — Xem trước đầy đủ và bảo vệ khi ghi (P1)
Xem trước: phân loại trước→sau theo phần; phần tiền được chuyển; tổng danh mục/đối tượng tăng/giảm (giao dịch và phần phân bổ tách biệt, giao dịch đếm một lần ở cấp cha); tổng tiền nguồn và số dư tài khoản không đổi; liên kết nghiệp vụ bị ảnh hưởng hoặc lý do chặn. Đổi lựa chọn → xác nhận cũ mất hiệu lực; ghi lại kiểm mã xem trước, dữ liệu đổi → từ chối, yêu cầu xem trước lại.

### US3 — Giao dịch chia nhiều phần (P1)
Chọn một phần để sửa, các phần khác giữ nguyên; số tiền mỗi phần giữ nguyên (đổi số tiền giữa các phần: dùng hộp Phân loại hiện có, tổng luôn bằng giá trị tuyệt đối giao dịch).

### US4 — Đích không hợp lệ và thay đổi mức B (P1)
Đối tượng chưa thuộc danh mục đích: chặn, đề nghị "Thêm vào danh mục" với xác nhận riêng rồi xem trước lại. Mức B (Q1 = A): cho phép kể cả đã duyệt, qua phiên điều chỉnh, xem trước tác động dư nợ/lãi/giá gốc trước→sau và **xác nhận riêng**; khi giao dịch đã bị nghiệp vụ tham chiếu (bảng kê lãi, khoản vay đã hoàn tất, gắn đợt BĐS, chuyển nội bộ đã ghép) thì luôn chặn kèm đường xử lý. Áp dụng như nhau qua API.

### US5 — Đã duyệt, lịch sử cũ (P2)
Đã duyệt: tự mở phiên điều chỉnh có lý do, snapshot cũ giữ nguyên, bản duyệt mới do người dùng duyệt. Dòng lịch sử cũ: đổi danh mục/đối tượng trong cùng loại gốc, có dấu vết trên dòng, bản dán gốc giữ nguyên; tình trạng tài khoản nguồn (có/chưa) không đổi.

## Requirements
- **FR-001 (R195)** Một chức năng "Sửa phân loại" dùng chung từ mọi màn có dòng giao dịch; ghi qua `classify` (giao dịch ngân hàng) hoặc thao tác dòng lịch sử cũ; không tạo đường ghi song song.
- **FR-002 (R196)** Nguồn bất biến: id, tài khoản, ngày, mã, chiều, số tiền, nội dung, chứng từ; chỉ phân loại thay đổi; dấu vết người/thời điểm/lý do/trước–sau.
- **FR-003 (R197)** Quy tắc A/B ở backend như bảng trên; đối tượng phải là thành viên danh mục hiệu lực; lưu trữ, chiều tiền, ghi chú bắt buộc.
- **FR-004 (R198)** Xem trước tính bằng **mô phỏng đúng thao tác ghi** trên bản sao dữ liệu; mã xem trước băm nội dung; ghi kiểm lại mã.
- **FR-005 (R199)** Giao dịch nhiều phần: sửa đúng phần chọn; tổng các phần bằng giá trị tuyệt đối giao dịch (Decimal); đếm giao dịch một lần ở cấp cha.
- **FR-006 (R200)** Đã duyệt: phiên điều chỉnh, snapshot bất biến; hoàn tác bằng điều chỉnh mới.
- **FR-007** Không sửa hàng loạt; không đổi số tiền giữa các phần trong chức năng này.

## Success Criteria
SC-001 ca Kết và các ca bổ sung đạt trên dữ liệu giả (test + UI). SC-002 xem trước = kết quả (so toàn bộ tổng danh mục/đối tượng/báo cáo). SC-003 mọi đích không hợp lệ và mức B bị chặn như nhau qua UI và API. SC-004 dữ liệu thật không đổi bởi phiên làm việc.

## Tư vấn kế toán (Constitution VIII)
Phân loại là lớp quản lý trên nguồn bất biến; sửa phân loại không phải bút toán chuyển tiền. Thay đổi làm đổi số dư phải thu/phải trả, lãi, giá gốc tài sản là **điều chỉnh nghiệp vụ**: với số đã duyệt/đã dùng cho bảng kê, hoàn tất, thanh toán hợp đồng phải đi qua luồng nghiệp vụ tương ứng (mở lại, bỏ gắn) để không làm sai số đã chốt. Với bản nháp chưa ghi sổ, sửa nhầm là chỉnh bản nháp (xem Q1). Đổi người có công nợ không chuyển nghĩa vụ nợ; đổi nhóm dài/ngắn hạn không đổi kỳ hạn hợp đồng; gốc↔lãi làm đổi dư nợ gốc và lãi nên phải hiện tác động. Thuế: không đưa kết luận.

## Assumptions / giới hạn
Chưa sửa hàng loạt; chưa đổi số tiền giữa các phần trong chức năng này (dùng hộp Phân loại); không xử lý importer sàn (042 B1).
