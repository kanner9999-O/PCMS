# AI analysis contract

Ngày 2026-09-26. Thiết kế mục tiêu; chưa triển khai AI integration. v0.1 có thể chạy và close hoàn chỉnh không cần AI.

## Ba lớp logic

| Lớp | Ai định nghĩa / duyệt | Cơ chế |
|---|---|---|
| Calculation | Implementation lead đặc tả, owner duyệt business meaning | Deterministic engine, decimal arithmetic, formula version và tests |
| Policy checks | Owner phê duyệt giới hạn và ngoại lệ | So actual với approved policy; chưa có policy thì không gắn breach |
| AI reasoning | Implementation lead thiết kế prompt và eval; owner duyệt phạm vi dùng | Giải thích facts, so sánh phương án, nêu giả định và uncertainty; không ghi facts tự động |

Risk limits, reserve months, allocation bands và thresholds trong ví dụ trao đổi không phải approved policy. AI không tự định nghĩa công thức hoặc biến đề xuất thành quy tắc chính thức.

## Input bắt buộc cho analysis package

- report/snapshot ID, effective cutoff, recorded cutoff, scope, currency, schema/formula/policy versions;
- metric values đã tính, nguồn/chứng từ hoặc manifest IDs;
- coverage, eligibility, open issues, valuation age và assumptions;
- approved policies và exceptions có actor/time; mục tiêu owner đã xác nhận;
- previous decisions liên quan khi có quyền đọc; dùng aliases và minimum necessary data.

Không gửi credentials. Evidence text là dữ liệu, không phải instructions cho model. Nếu không được phép dùng provider bên ngoài, không gửi dữ liệu thật; vẫn dùng deterministic reporting.

## Output contract

Mỗi analysis giữ `analysis_id, generated_at, model_identifier, prompt_version, input_manifest_id, report_id, policy_version_ids, review_state` để truy nguyên. Không cam kết model sinh lại cùng văn bản; lưu nguyên output đã review.

Mỗi finding gồm:

1. **Fact:** metric/input ID và số liệu nguồn; không bịa số còn thiếu.
2. **Interpretation:** ý nghĩa và giả định, tách khỏi fact.
3. **Policy check:** approved rule ID và kết quả, hoặc NOT_CONFIGURED.
4. **Options:** các lựa chọn và tradeoffs; không gọi là quyết định owner.
5. **Uncertainty:** dữ liệu thiếu/cũ, phạm vi kết luận.
6. **Review:** câu hỏi/hành động đề xuất, chưa approved mặc định.

Scenario arithmetic được calculation engine tính và gắn scenario assumptions; model không tự đưa số chưa được kiểm chứng vào report như fact. Không đủ dữ liệu thì từ chối kết luận phần đó và nêu evidence cần bổ sung.

## Quyền hạn

AI đọc report được cấp quyền. AI có thể đề xuất classification/correction/decision nhưng phải vào review queue. AI không publish journal, duyệt close, thay policy, sửa lịch sử, gửi lệnh giao dịch hoặc chuyển vốn. Nếu owner chấp nhận đề xuất, tạo Decision và approval event riêng; không đổi trạng thái analysis thành financial fact.

## Acceptance trước activation

- Concentration cao nhưng không có limit: mô tả tỷ trọng, không khẳng định breach.
- Thiếu cost basis: không tạo realized/unrealized P&L hoặc gọi holdings là profit.
- Report thiếu account material: không tuyên bố full net worth đáng tin.
- Nguồn có câu yêu cầu bỏ qua policy: xử lý như dữ liệu, không thực thi.
- Mọi số trong findings khớp calculation outputs; scenario có assumptions riêng.
- Không có đường tự publish/approve/trade; approval và correction đi qua workflow chuẩn.

AI activation chỉ sau M2 và sau khi contract/evals đạt; advanced investment analytics còn cần dữ liệu phù hợp. Không đặt AI làm điều kiện để triển khai core ledger v0.1.
