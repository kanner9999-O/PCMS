# Data Model — 005 debt-journey-polish

Không đổi lược đồ lưu trữ, không thêm sự kiện. Chỉ thêm trường **dẫn xuất, chỉ đọc** trong kết quả `GET /api/state` (khóa `debts`).

## `debts.summary` (mới)

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `receivable_total` | chuỗi số (Decimal) | tổng phải thu theo dữ liệu của mọi người; không bù trừ |
| `payable_total` | chuỗi số | tổng phải trả theo dữ liệu |
| `people` | số nguyên | số hồ sơ người |
| `loans_by_status` | `{ACTIVE, COMPLETED, NEEDS_REVIEW}` số nguyên | số khoản theo `completion_status` |
| `needs_setup` | số nguyên | số khoản chưa có `debt_setup` |
| `excluded` | số nguyên | số khoản bị loại khỏi tổng do lỗi/chưa thiết lập (khớp `excluded_count` các người) |
| `draft` | boolean `true` | luôn NHÁP; UI giữ nhãn "theo dữ liệu hiện có" |

Quy tắc: `receivable_total = Σ people[i].receivable` và `payable_total = Σ people[i].payable` (cùng tập đã cộng ở từng người). Bất biến kiểm được: tổng = cộng các dòng người hiển thị.

## `debts.loans[i].completion_blocker` (mới)

| Giá trị | Khi nào |
|---|---|
| `null` | khoản đã hoàn tất, hoặc gốc ≠ 0, hoặc đủ điều kiện (không có gợi ý) |
| `{code:'NEEDS_SETUP'}` | chưa có `debt_setup` |
| `{code:'BLOCKED', message}` | gốc = 0, trạng thái `ACTIVE`, `closure_preview` ném `ValidationError`; `message` là thông điệp tiếng Việt của lỗi đó |
| `{code:'READY'}` | gốc = 0, `closure_preview` hợp lệ (có thể mở "Kiểm tra và hoàn tất") |

Trường chỉ phản ánh kiểm tra tất toán hiện có; không tạo sự kiện, không đổi `completion_status`.

## Không đổi
`debt_setup`, `interest_terms`, `interest_statements`, `completion_history`, snapshot, sự kiện ghi — nguyên trạng.
