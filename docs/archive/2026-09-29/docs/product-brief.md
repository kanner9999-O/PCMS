# PCMS — Product brief

> **Cập nhật nhập liệu liên tục:** đã bổ sung Tài khoản & biến động, Giao dịch cần xử lý, Công nợ theo người và Báo cáo theo ngày. Không bắt buộc làm theo tháng. Xem [hướng dẫn](runbooks/continuous-accounts.md) và [nghiệm thu](continuous-acceptance.md). Phần mô tả bản thử cũ bên dưới giữ làm lịch sử.


> **Cập nhật phạm vi 28/09/2026:** Thạch giao Codex tự quyết định và hoàn thành sản phẩm cơ bản dùng thử với dữ liệu giả lập. Đã triển khai ứng dụng local theo [quyết định bản thử](product-trial-decisions.md), [hướng dẫn sử dụng](runbooks/product-trial.md) và [nghiệm thu bản thử](product-trial-acceptance.md). Các ràng buộc Sheets-only/no-custom-UI và policy chưa chốt dưới đây thuộc baseline trước yêu cầu mới; chúng không chặn bản thử này. Những yêu cầu về dữ liệu thật/production chưa được coi là hoàn tất.


Cập nhật 2026-09-26 sau trao đổi với Thạch. Đây là baseline để chuẩn bị triển khai, không xác nhận dữ liệu hoặc policy tài chính thực.

## Sản phẩm chính xác là gì?

PCMS là sổ tài chính tổng hợp cho người có nhiều loại tài sản. Core là **gom và đối soát tài sản + nợ + dòng tiền vào một nơi**, tạo bức tranh đáng tin để owner quyết định sử dụng vốn và theo dõi kết quả.

Người dùng mục tiêu ban đầu: owner có tài khoản ngân hàng, financial investments, bất động sản, phần vốn doanh nghiệp và các nghĩa vụ nợ; hiện dữ liệu phân tán. Hành trình chính: cập nhật và review hàng tháng. Daily/weekly chủ yếu xử lý ngoại lệ ở giai đoạn sau.

Dashboard trình bày kết quả; AI giải thích kết quả. Cả hai không thay thế ledger và bằng chứng. v0.1 vận hành bằng Sheets, manual imports và review. Không xây custom frontend, tự động giao dịch, tax filing hoặc risk engine nâng cao trong v0.1.

## Input → xử lý → output

| Input từ người dùng/nguồn được chọn | Hệ thống xử lý | Output |
|---|---|---|
| Chủ thể, accounts, quyền sở hữu | Xác định phạm vi, IDs và nơi giữ tài sản | Wealth map |
| Statements, transaction CSV, balance observations | Giữ raw, chuẩn hóa, kiểm tra trùng và đối soát | Ledger accepted và issue queue |
| Property/business valuations, prices, FX | Kiểm tra scope, phương pháp, thời điểm và độ cũ | Giá trị tài sản có provenance |
| Nợ, dư nợ và lịch nghĩa vụ | Xác định trách nhiệm, tránh trừ/cộng trùng | Debt breakdown và nghĩa vụ sắp tới |
| Income, spending, đầu tư và transfers | Phân loại dòng tiền; không coi loan proceeds là income | Báo cáo thu/chi và cash-flow bridge |
| Policy, mục tiêu, quyết định owner | Versioning, kiểm tra điều kiện, lưu approval | Review checklist, kế hoạch vốn và decision history |

Input không gồm passwords, OTP hoặc private keys. Không giả định đã kết nối tự động. Dữ liệu nguồn, định giá và policy thiếu phải được đánh dấu; không biến unknown thành zero.

## Bốn khu vực người dùng

1. **Tài sản của tôi:** có gì, ở đâu, thuộc ai, nợ bao nhiêu.
2. **Tình hình tài chính:** net worth, thu chi, thanh khoản, coverage và issues.
3. **Kế hoạch sử dụng vốn:** tiền có thể phân bổ, nhu cầu sắp tới, quyết định được duyệt.
4. **Review và lịch sử:** chốt tháng, so sánh kỳ, truy nguyên thay đổi, review quyết định.

Đây là cách tổ chức nghiệp vụ/operational Sheets, chưa phải cam kết thiết kế bốn màn hình app. Người dùng nhập thu nhập, chi tiêu, mua bán, chuyển tiền, vay/trả nợ; không cần nhập debit/credit. Implementation lead chuyển các hành động đó thành postings và giải thích các lựa chọn có ý nghĩa nghiệp vụ để owner duyệt.

## Sáu core features và workflow

| Feature | Input và luồng | Kết quả / ngoại lệ | Phạm vi v0.1 |
|---|---|---|---|
| Wealth Map | Chọn scope → khai báo entities/accounts/assets/debt → xác nhận ownership → owner review | Inventory đầy đủ; thiếu quyền sở hữu/nghĩa vụ thì mở issue | Có, bao gồm property/business metadata và equity |
| Ledger & Data Quality | Nhập evidence → raw → normalize → validate → reconcile → publish | Accepted ledger; trùng/mismatch được giữ để review, không tự cộng | Có, import có kiểm soát |
| Financial Control | Accepted inputs → chọn valuation/FX → eligibility → compute → report | TNW/flows/debt/allocation; metric chưa đủ dữ liệu/policy trả unavailable | Có, metric gates riêng |
| Investment & Risk | Kiểm tra lịch sử → tính metrics → đối chiếu approved policy → owner review | Performance/risk report, không tự sell khi breach | Allocation cơ bản; performance và risk engine defer |
| Capital Allocation | Xác định vốn khả dụng → đề xuất routing → owner approve → Decision Log → thực hiện bên ngoài → nhập kết quả | Kế hoạch và actual; chuyển investment sang trading cần decision | Pools + manual decision log; advanced routing defer |
| Governance & Reporting | Reconcile cuối kỳ → kiểm tra issues → owner approve → freeze snapshot → export → review kỳ sau | Closed history; lỗi kỳ cũ tạo approved restatement | Có, manual close và backup |

Luồng chính: **cập nhật → xử lý sai lệch → xem báo cáo → quyết định → thực hiện bên ngoài → theo dõi lại**. Closed snapshot chỉ xuất bản sau approval; bản draft phải phân biệt với bản chính thức. Sai sót phát hiện sau close không sửa trực tiếp bản cũ.

## Ví dụ nghiệm thu sản phẩm

Một owner nhập sao kê, danh mục và nghĩa vụ tại cutoff. Hệ thống phát hiện transfer nội bộ và không gọi đó là income. Khoản mua cổ phiếu được tách khỏi chi sinh hoạt. Property equity không bị trừ mortgage lần hai. Người dùng nhìn thấy net worth kèm coverage và có thể đi từ một con số về evidence. Khi thiếu policy liquidity, LNW hiển thị lý do unavailable. Owner duyệt close và xem lại nguyên bản tháng đó sau khi tháng sau có dữ liệu mới.

## Ai quyết định gì?

| Vai trò | Trách nhiệm |
|---|---|
| Product reviewer — Thạch trong cuộc trao đổi này | Làm rõ core, input/output, hành trình và tính dễ hiểu; không mặc nhiên là asset owner |
| Financial owner — cần xác nhận người có thẩm quyền | Xác nhận scope, ownership, policies, exceptions, close và quyết định vốn |
| Implementation lead | Đề xuất domain/schema, công thức, validation; triển khai và kiểm thử |
| Custodian | Thu thập chứng từ, nhập và xử lý issues theo quyền được giao |
| AI analyst | Phân tích trên báo cáo và policy có nguồn, đề xuất để review |

Người định hình sản phẩm không cần học kế toán trước. Cần xác định câu hỏi người dùng muốn trả lời; implementation lead chịu trách nhiệm làm rõ phương án kỹ thuật/nghiệp vụ. Quy tắc thuế, pháp lý hoặc kế toán chuyên biệt được xác minh với chuyên gia khi đưa vào scope.

## Tiêu chí thành công của v0.1

- Owner biết tài sản, nơi giữ, nợ và dòng tiền trong phạm vi đã xác nhận.
- Mỗi chỉ số có nguồn, cutoff và trạng thái dữ liệu/policy.
- Nhập trùng không làm giàu lên; chuyển nội bộ không tạo thu nhập; nợ không trừ hai lần.
- Có thể sửa sai và khôi phục mà không mất báo cáo cũ.
- Review và đóng một kỳ hoàn chỉnh; đo thời gian thực tế, chưa cam kết mục tiêu dưới 30 phút.

Xem [architecture](architecture.md) cho thiết kế, [readiness](implementation-readiness.md) cho bước triển khai và [AI contract](ai-analysis-contract.md) cho giới hạn phân tích.
