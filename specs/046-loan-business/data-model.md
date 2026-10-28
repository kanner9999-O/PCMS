# Data model — spec 046

Mọi số tiền là chuỗi số nguyên VND, trừ mức lãi (chuỗi Decimal ≥ 0, tối đa 4 chữ số thập phân). Ngày là `YYYY-MM-DD`.

## Nút danh mục (bổ sung)
```
node.business = {type: 'RECEIVABLE'|'PAYABLE', at, reason} | null   # chỉ danh mục người dùng tạo
node.business_history = [{at, action: 'SET'|'CLEAR', type, reason, before}]
```
- **Nghiệp vụ hiệu lực**: `business` của nút gần nhất có giá trị trên chuỗi từ chính nút lên gốc. Gốc hệ thống không mang nghiệp vụ.
- **Bất biến**: không nút nào có `business` khác nghiệp vụ hiệu lực của cha nó.

## Khoản vay `s['loans'][]`
| Trường | Kiểu | Ràng buộc |
|---|---|---|
| id | uuid | |
| code | str | 1–20 ký tự, duy nhất toàn hệ thống (không phân biệt hoa/thường) |
| name | str | 1–100 ký tự |
| person | profile id | kind PERSON, không bị gộp |
| direction | 'RECEIVABLE'/'PAYABLE' | cố định; bằng nghiệp vụ hiệu lực của `category` lúc tạo |
| category | node id | danh mục nơi tạo; người phải là thành viên ACTIVE của một danh mục trong nhánh mang cùng nghiệp vụ hiệu lực |
| tracking_date | date | bắt buộc |
| due_date | date/null | ≥ tracking_date |
| rate | Decimal str | ≥ 0, ≤ 100000 (đồng/triệu/ngày) |
| broker | {name, rate}/null | chỉ RECEIVABLE; tên 1–100 ký tự, rate ≥ 0 |
| status | 'ACTIVE'/'COMPLETED' | |
| created_at, history[] | | history: {at, action CREATE/EDIT/COMPLETE/REOPEN, before, after, reason} |
| completion | {at, reason, as_of}/null | |

## Chi tiết nghiệp vụ `s['loan_details'][]`
```
{source: <transaction id | legacy entry id>, kind: 'BANK'|'LEGACY',
 versions: [{n, at, status: 'POSTED'|'VOID', reason, lines: [Line]}],
 draft: {at, lines: [Line], note} | null}
Line = {category: <khóa danh mục hiệu lực>, person: <profile id>, loan: <loan id>, component: 'principal'|'interest'|'broker', amount}
```
- **Bản hiện hành**: `versions[-1]` nếu có trạng thái POSTED; không có thì nguồn chưa ghi.
- **Nhóm nghiệp vụ của nguồn**: Σ số tiền theo (danh mục hiệu lực, người) của các phần nằm trong danh mục có nghiệp vụ.
- **Ghi (POST)**:
  - Σ dòng theo từng nhóm phải bằng đúng nhóm.
  - Mọi nhóm phải được phủ.
  - `line.loan.person == line.person`, `loan.direction ==` nghiệp vụ hiệu lực của `line.category`.
  - Thành phần hợp chiều tiền:

| Chiều khoản | Tiền vào | Tiền ra |
|---|---|---|
| RECEIVABLE | principal (Thu gốc), interest (Thu lãi) | principal (Giải ngân), broker (Trả phí môi giới, khi khoản có môi giới) |
| PAYABLE | principal (Nhận tiền vay) | principal (Trả gốc), interest (Trả lãi) |

## Miễn giảm `s['loan_waivers'][]`
`{id, loan, date, amount, reason, status 'ACTIVE'|'CANCELLED', at, history[{at, action, reason}]}`

## Sổ khoản vay (chỉ đọc, `loan_book(s, as_of)`)
```
{as_of, today, future: bool,
 loans: [LoanRow], legacy: [<dòng debt_register cũ, giữ nguyên>],
 people: [{person, name, receivable: Block|null, payable: Block|null}],
 by_category: [{category, path, direction, disbursed, repaid, interest_cash, broker_paid, principal, sources}],
 by_account: {account: {in, out}},
 summary: {receivable, payable (gồm cả khoản cũ, tách 'legacy_receivable'/'legacy_payable'), people, loans, transactions, interest_outstanding_receivable, interest_outstanding_payable},
 pending: {count, in, out, items: [PendingItem]}, sources: {<source id>: SourceStatus}}
LoanRow = {id, code, name, person, person_name, direction, category, category_path, rate, broker, tracking_date, due_date, status,
  principal, disbursed, repaid, interest_accrued, interest_paid, waived, interest_outstanding,
  broker_terms, spread_terms, broker_paid, broker_over, overdue, settled, can_complete, complete_blocker,
  caution (còn nguồn chờ cùng người/chiều), events[], segments[], waivers[], sources (số giao dịch)}
SourceStatus = {status: 'POSTED'|'PENDING'|'LEGACY_LINK'|'CONFLICT', reasons[], groups[], amount_in_scope, direction, has_draft, editing}
```
- **Lý do chờ**: NO_PERSON, NOT_PERSON, NO_LOAN, NOT_DETAILED, DRAFT, MISMATCH.
- **Lý do xung đột**: LEGACY_DIRECTION (khoản cũ khác chiều), LEGACY_NO_SETUP.

## Chuyển trạng thái
- **Khoản**: ACTIVE → COMPLETED khi `can_complete` và người dùng xác nhận có lý do; COMPLETED → ACTIVE khi mở lại có lý do.
- **Nguồn**: (không) → nháp → POSTED (v1) → nháp thay thế → POSTED (v2) …; POSTED → VOID khi hủy có lý do.
