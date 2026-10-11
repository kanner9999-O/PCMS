# Nhập mẫu bank statement v1

Ngày 2026-09-28. Adapter `vn-account-statement-v1` hỗ trợ đúng cấu trúc XLSX người dùng cung cấp. Tên ngân hàng chưa được xác nhận qua metadata độc lập; không suy ra bank identity từ nội dung chuyển tiền. Bank/format khác sẽ bổ sung adapter khi có mẫu.

## Cách chạy

```sh
PYTHONPATH=src python3 -m pcms bank-stage '/path/to/statement.xlsx'
```

Mặc định tạo batch mới trong `private-data/bank-staging/`, đã loại khỏi Git. Có thể truyền nhiều files và `--output` tới thư mục private phù hợp. Mỗi lần nhập giữ bản gốc XLSX với SHA-256, JSON staging có toàn bộ dữ liệu nguyên trạng/chuẩn hóa, issues và manifest. Không sửa file nguồn. Không import tài khoản thật vào synthetic ledger USD.

## Nhận diện và mapping

| Nguồn | Field chuẩn hóa | Quy tắc |
|---|---|---|
| B1, D1 | period_start, period_end | DD/MM/YYYY → ISO date; không đoán timezone hoặc giờ |
| B2, B3 | account_reference, account_name | Account giữ dạng text để không mất zero đầu |
| B4 | currency | Phiên bản này chỉ VND, không quy đổi sang USD |
| D3, D4 | reported_opening_balance, reported_closing_balance | Giữ nguyên, không âm thầm thay bằng số suy luận |
| A8:F8 | Header signature | NGAY / DIEN GIAI / CHI TIET / NO / CO / SO DU |
| A9:A… | effective_date | Ngày giao dịch, precision DATE |
| B9:B… | description | Văn bản nguồn; không coi là instruction hoặc tự động classification |
| C9:C… | bank_reference | Không phải khóa unique cho mỗi movement |
| D9:D… | debit | Tiền ra từ tài khoản ngân hàng; chưa phải expense |
| E9:E… | credit | Tiền vào tài khoản ngân hàng; chưa phải income |
| F9:F… | reported_balance | Số dư sau từng movement để kiểm tra liên tiếp |

Raw numeric XML hoặc string `1,000` được chuyển thành decimal text `1000`, không qua float. Blank debit/credit là zero nếu phía kia dương; blank balance không được coi là zero. Formula cells không được evaluate hoặc chấp nhận thay cho raw facts. Chỉ hỗ trợ integer VND trong mẫu này.

## Validation và dedup

- Tính `signed_amount = credit − debit`.
- Kiểm tra từng bước: previous balance + signed amount = reported balance.
- Kiểm tra cả kỳ: reported opening + total credits − total debits = reported closing.
- Kiểm tra ngày trong kỳ, thứ tự ngày, trường thiếu, extra columns, số tiền lỗi và closing row.
- Nếu header opening bằng balance sau giao dịch đầu: chỉ lưu `opening_balance_hypothesis`, `hypothesis_applied=false`; vẫn giữ lỗi đối soát và mọi giao dịch.
- Mã bank trùng: giữ tất cả legs và mở issue; không tự gộp debit/credit thành transfer hoặc reversal.
- `raw_record_id` ổn định theo file hash + sheet + row; fingerprint chứa account/reference/date/debit/credit/balance/description để hỗ trợ overlap review sau này. Batch có thể được nhập lại, nhưng staging không publish nên không double-post. Cross-file economic dedup và owner-approved journal mapping chưa triển khai.

## Trạng thái và phạm vi nghiệm thu

`REJECTED_FORMAT`: sai mẫu hoặc header lỗi. `BLOCKED_RECONCILIATION`: đã đọc được nhưng có vấn đề cần review. `AWAITING_CLASSIFICATION`: kiểm tra số liệu qua, vẫn chưa biết bản chất kinh tế. Mọi trường hợp luôn là `STAGING_ONLY`.

DoD adapter cho mẫu này: đọc đủ dòng, giữ source/cell provenance, mapping tiền ra/vào đúng, phát hiện balance mismatch và repeated refs, giữ raw, không tự phân loại hoặc publish. Synthetic test fixtures không chứa tài khoản hoặc mô tả thật. Đối chiếu read-only bằng reader độc lập trên mẫu được cấp.

Đây là tiến độ của mốc nhập liệu/S2; chưa hoàn thành workbook nhập liệu, M1 inventory hay M2 opening reconciliation. Để M2 đạt cần owner xác nhận số dư đầu kỳ/bổ sung evidence, giải thích repeated refs, mapping account/entity, phân loại các movements và journal/currency support.

## Workbook review

Bản review dành cho người dùng có Tien_do, Thiet_lap, Tai_khoan, Doi_soat, Can_xac_nhan và Giao_dich. Điền ô vàng rồi gửi lại. Người dùng không cần chạy lệnh dưới đây; đây là hướng dẫn operator.

```sh
PYTHONPATH=src python3 -m pcms review-package private-data/bank-staging/BATCH_ID --output outputs/NEW_PACKAGE.json
PYTHONPATH=src python3 -m pcms review-return private-data/bank-staging/BATCH_ID /path/to/completed-review.xlsx
```

Operator tạo workbook bằng scripts/workbook/build-review.mjs với bundled artifact-tool và verified package. Builder hiện thiết kế cho hai sample đã cấp, cần điều chỉnh trước khi mở rộng dataset. Review receiver kiểm tra source IDs, số tiền, ngày, tài khoản, mô tả và bank refs so với archived source; các answers chỉ là proposals. Tên Dũng trong ô reviewer không phải authentication/approval. Form trả lời không sửa financial history; proposal được lưu append-only vào batch mới. Import lại statement giống hệt không tăng số dòng trong cùng review package. Overlap giữa các statements khác nhau chưa tự gộp.
