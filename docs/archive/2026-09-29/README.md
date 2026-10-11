# Personal Capital Management System
**Tình huống sử dụng:** [Use cases](docs/use-cases.md) — v1.1: 20 use case hoạt động, UC-03 gộp vào UC-02; yêu cầu mới về tài khoản, import và lịch sử sao kê (29/09/2026).

**Mô hình nghiệp vụ hiện tại:** [Domain model](docs/domain-model.md) — đối tượng, quan hệ, quy tắc, phần đã có và hướng hoàn thiện (29/09/2026).


> **Cập nhật nhập liệu liên tục:** đã bổ sung Tài khoản & biến động, Giao dịch cần xử lý, Công nợ theo người và Báo cáo theo ngày. Không bắt buộc làm theo tháng. Xem [hướng dẫn](docs/runbooks/continuous-accounts.md) và [nghiệm thu](docs/continuous-acceptance.md). Phần mô tả bản thử cũ bên dưới giữ làm lịch sử.


**28/09/2026 — Đã có ứng dụng dùng thử cơ bản chạy local.** Mở http://127.0.0.1:8787 hoặc nhấp đúp [Start PCMS.command](Start%20PCMS.command). Xem [hướng dẫn 15 phút](docs/runbooks/product-trial.md) và [mốc nghiệm thu bản dùng thử](docs/product-trial-acceptance.md).

Bản mới dùng dữ liệu giả lập cho BĐS, doanh nghiệp, cổ phiếu, crypto, tài khoản và nợ; có 11 màn hình từ giao dịch tới chốt kỳ và kế hoạch vốn. Thạch đã giao Codex tự quyết định phạm vi/chính sách cho bản thử. Các tài liệu baseline bên dưới vẫn giữ giá trị lịch sử và điều kiện chuyển sang số liệu thật; không còn là mô tả đầy đủ giao diện hiện tại.


Cập nhật **2026-09-26 — baseline tài liệu sau product review với Thạch; chuẩn bị triển khai v0.1**.

**Core sản phẩm: tổng hợp và đối soát tài sản, nợ và dòng tiền vào một nơi**, tạo bức tranh tài chính đáng tin để owner quyết định phân bổ vốn và theo dõi kết quả. Dashboard trình bày kết quả, AI phân tích trên kết quả đã kiểm chứng.

## Nghiệm thu theo milestone

Đọc [Bảng milestone dành cho owner](docs/milestone-board.md) trước. Đã xác nhận Dũng duyệt; tài khoản giữ loại tiền gốc, tổng hợp USDT là hướng tương lai. Workbook review đã có trong outputs; chưa phải sổ vận hành hoặc báo cáo đã đóng.

## Đọc theo thứ tự

1. [Product brief](docs/product-brief.md) — sản phẩm là gì, input/output, sáu core features và hành trình người dùng.
2. [Implementation readiness](docs/implementation-readiness.md) — việc có thể bắt đầu, backlog S0–S5 và các quyết định còn mở.
3. [Architecture A–K](docs/architecture.md) — domain, consolidation, audit, close và AI boundary.
4. [Data dictionary](docs/data-dictionary.md) — schema Sheets/PostgreSQL và metric eligibility.
5. [M0–M3 plan](docs/milestones.md) — deliverables, acceptance và release gates.
6. [ADR register](docs/adr-register.md) — lý do chọn thiết kế, tradeoffs và approval dependencies.
7. [AI analysis contract](docs/ai-analysis-contract.md) — ai định nghĩa logic, AI đọc gì và không tự quyết định gì.
8. [Revision history](docs/revision-history.md) — những điểm đã cập nhật sau trao đổi.

## Trạng thái thực tế

Đã bắt đầu triển khai: có Python ledger pilot, JSON entry contract, synthetic fixtures, validation, reconciliation, report, snapshot/restatement và backup/restore. Pilot chạy local, không thay quyết định dùng Sheets làm provisional ledger khi vận hành thật. Đã có workbook review nhập liệu; chưa có workbook vận hành/close hoặc connector. Xem [hướng dẫn chạy](docs/runbooks/local-pilot.md) và [schema mapping / giới hạn](schema/README.md).

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m pcms demo --output outputs/my-demo-001
```

Demo cần thư mục mới, không overwrite run cũ. Tất cả tài sản và approvals trong demo là giả lập. Bản chạy kiểm chứng có [báo cáo demo](outputs/pilot-002/report.md) (output local, không lưu Git). Synthetic development đã bắt đầu; M0–M3 thực tế chưa hoàn thành.

v0.1: Sheets provisional ledger + evidence archive, manual import/review, opening reconciliation, báo cáo cơ bản, decision log và monthly close. Không dùng số liệu crypto trong handoff làm opening balance hoặc performance history. LNW chưa có công thức được owner duyệt; phải hiển thị unavailable khi thiếu policy.

M0–M3 chưa hoàn thành. Chỉ dùng dữ liệu thật và xuất bản báo cáo chính thức khi scope, settings, permissions và các gate tương ứng được xác nhận. Dữ liệu tài chính thật/evidence/backups nằm ở kho private do owner kiểm soát, ngoài Git. Người review sản phẩm không cần học kế toán để duyệt hành trình nghiệp vụ.

## Bank input adapter — 2026-09-28

Đã thêm adapter đọc XLSX theo mẫu sao kê 6 cột được cung cấp: `NGAY / DIEN GIAI / CHI TIET / NO / CO / SO DU`. Adapter chạy bằng Python standard library, giữ VND và chứng từ gốc, tạo staging/issue report riêng; không publish vào synthetic ledger. Bank khác chưa hỗ trợ đến khi có sample.

```sh
PYTHONPATH=src python3 -m pcms bank-stage '/path/to/statement.xlsx'
```

Xem [mapping, validation và DoD adapter](docs/runbooks/bank-statement-v1.md). Mặc định outputs chứa dữ liệu thật nằm trong `private-data/`, không vào Git. Bộ kiểm thử hiện có 40 tests (26 core + 14 bank adapter). Bank statement đủ cấu trúc chưa đồng nghĩa đã reconcile hoặc được duyệt ghi sổ.
