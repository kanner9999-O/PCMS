# Contracts — spec 046

Hành động gửi `POST /api/action {action, data}`. Thông báo lỗi bằng tiếng Việt, trả về theo `ValidationError` như hiện có.

| Action | data | Hiệu lực |
|---|---|---|
| `lb-category-set` | category, type (RECEIVABLE/PAYABLE), reason, review_token | Gắn nghiệp vụ. Token lấy từ `/api/lb-category-preview`; trong xem trước còn `blocks` thì chặn. |
| `lb-category-clear` | category, reason | Gỡ nghiệp vụ. Chặn khi nhánh có chi tiết (đã ghi/nháp) hoặc có khoản tạo từ nhánh. |
| `lb-loan-create` | category, person, code?, name, tracking_date, due_date?, rate, broker_name?, broker_rate? | Tạo khoản; chiều lấy từ nghiệp vụ hiệu lực. |
| `lb-loan-edit` | loan, name?, code?, tracking_date?, due_date?, rate?, broker_name?, broker_rate?, reason | Sửa; cần lý do. Kiểm lại nghĩa vụ với mức mới; ngày theo dõi không được sau nguồn đã liên kết. |
| `lb-detail-draft` | source, lines[] | Lưu nháp (không kiểm đủ). |
| `lb-detail-post` | source, lines[], reason? | Ghi phiên bản mới, kiểm đủ và kiểm nghĩa vụ. Xóa nháp. |
| `lb-detail-void` | source, reason | Hủy bản hiện hành (thêm phiên bản VOID); kiểm nghĩa vụ và hoàn tất. |
| `lb-detail-discard` | source | Bỏ nháp. |
| `lb-waiver-add` | loan, date, amount, reason | Thêm miễn giảm. |
| `lb-waiver-cancel` | waiver, reason | Hủy miễn giảm; kiểm nghĩa vụ. |
| `lb-loan-complete` | loan, reason | Đánh dấu hoàn tất khi `can_complete`. |
| `lb-loan-reopen` | loan, reason | Mở lại khoản. |

## Endpoint xem trước (chỉ đọc)

- `POST /api/lb-category-preview {category, type}` → `{category, path, type, scope:[{id,path}], valid:{count,in,out}, missing:{count,in,out}, conflicts:[{source,reference,date,amount,code,message}], non_person:[{profile,name,kind}], blocks:[{code,message}], review_token}`
- `POST /api/lb-detail-preview {source, lines?, as_of?}` → `{source:{id,kind,date,reference,description,account,amount,direction}, groups:[{category,path,person,person_name,amount,business,loans:[{id,code,name,principal,...}]}], current:Version|null, draft, lines, allocated, remaining, impact:[{loan,code, before:{principal,interest_accrued,interest_paid,waived,interest_outstanding}, after:{...}, settlement:'PARTIAL'|'FULL'|null, warnings[]}], blocks:[...], can_post, components:{RECEIVABLE:{IN:[..],OUT:[..]},PAYABLE:{...}}}`
- `POST /api/loan-book {as_of?, category?}` → sổ khoản vay (xem data-model). `sources` (trạng thái từng nguồn trong phạm vi, kèm người/chiều) là nguồn của danh sách "Ghi từ giao dịch nguồn" trên một khoản.

## view()

Thêm các trường:
- `loan_book`: tính tới hôm nay. Trong `sources` chỉ có trạng thái của các nguồn trong phạm vi.
- capability `loan-business`.
- build `P49-2026-10-28`.
- `categories.nodes[].business`: `{type, own, from, from_path}`.
- `categories` ở mỗi đối tượng: `loans` (khoản của người theo chiều của danh mục, lấy từ sổ).
