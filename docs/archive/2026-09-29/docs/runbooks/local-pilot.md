# Chạy PCMS local pilot

Phiên bản đầu chạy bằng Python standard library (Python 3.10+), không cần API key, account credentials hoặc cài package. Chỉ nhận SYNTHETIC; chưa dùng dữ liệu thật.

Từ thư mục gốc PCMS:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m pcms demo --output outputs/my-demo-001
PYTHONPATH=src python3 -m pcms verify outputs/my-demo-001/ledger
PYTHONPATH=src python3 -m pcms report outputs/my-demo-001/ledger --as-of 2026-09-30
```

Demo yêu cầu thư mục mới. Muốn chạy lại, chọn tên khác; không xóa hoặc overwrite run cũ. `report.md` là bản đọc cho người dùng, `report.json` là output có traceability; `backup.json` là bundle đã được restore kiểm tra. `ledger/events` chứa lịch sử, `ledger/evidence` giữ nguyên raw inputs. Các outputs bị loại khỏi Git.

## Tình huống đã triển khai

Opening → salary → expense → chuyển giữa hai bank accounts → mua investment có fee → vay/trả gốc/lãi → nhập lại salary → định giá → đối soát → owner giả lập duyệt close → sửa expense 1.000 thành 100 → đối soát lại → duyệt restatement → export/restore.

Kỳ vọng USD giả lập: TNW gốc 414.390, restated 415.290; income 5.000; spending 1.110 → 210; FCF 3.890 → 4.790. Direct debt 209.000; mortgage 200.000 được tính đúng một lần. Business equity 100.000 không cộng thêm cash nội bộ công ty.

## Khi gặp lỗi

- Unbalanced/FK/currency/quantity lỗi: entry không publish, raw và issue được giữ khi đi qua importer.
- Exact duplicate: không double-post, giữ import attempt và issue nonblocking.
- Same source key nhưng payload khác: issue blocking; chưa có chức năng resolve issue trong pilot. Không sửa trực tiếp event để bỏ chặn. Dùng fixture mới trong run mới khi đang phát triển; production resolution phải được triển khai trước live use.
- Close thiếu reconciliation/valuation: bổ sung inputs hợp lệ rồi reconcile lại. Lần reconciliation mới nhất có hiệu lực, không dùng lại kết quả pass cũ khi lần mới fail.
- Correction nửa chừng: chặn report hoàn chỉnh cho đến khi có replacement.
- Checksum mismatch: dừng sử dụng run; giữ bản lỗi để điều tra và restore bundle đã kiểm chứng vào thư mục mới. Không tự cập nhật checksum để hợp thức hóa dữ liệu.

## Giới hạn hiện tại

Đây là vertical slice kỹ thuật cho S0/S1 và kiểm chứng S3/S4, chưa phải hoàn thành M0–M3. Chưa có workbook/Sheets adapter, CSV parser, live config, FX, multi-owner, AI, tax/performance hoặc authenticated approval. Approval strings và file hashes không thay thế phân quyền thực. Các calculations hiện dùng cash-based fixtures, không hỗ trợ accrual/credit-card clearing. Full semantic rules cho từng transaction type và policy-bound approvals cần hoàn thiện trước pilot dữ liệu thật.

Chỉ có một writer. Concurrent writers có thể bị exclusive-create từ chối; caller phải đọc lại và validate lại, không tự retry bypass checks. Cơ chế không phục vụ concurrent multi-user production. Restore kiểm tra file paths/checksums và rebuild snapshots; không phải chứng nhận pháp lý hay độc lập về nguồn chứng từ.
