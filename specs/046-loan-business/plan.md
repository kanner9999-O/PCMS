# Implementation Plan: Nghiệp vụ Cho vay / Đi vay gắn vào danh mục

**Branch**: `046-loan-business` | **Date**: 2026-10-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/046-loan-business/spec.md`

## Summary

Thêm một lớp nghiệp vụ vay chạy song song với cây danh mục, gồm:
- nghiệp vụ gắn vào danh mục và kế thừa xuống nhánh;
- khoản vay kiểu mới, mỗi khoản thuộc một người;
- chi tiết nghiệp vụ cho từng nguồn, có phiên bản và nháp;
- miễn giảm và hoàn tất;
- **một sổ khoản vay** (`loan_book`) tính dư gốc và lãi theo ngày bằng Decimal.

Mọi màn đọc từ cùng một sổ. Một **kiểm tra bất biến chung** bọc quanh `change()` chặn mọi đường sửa làm lệch chi tiết đã ghi, nên không phải vá từng đường riêng. Các đường này gồm: phân loại, sửa phân loại, chuyển/gộp/gỡ đối tượng, đổi cha, gỡ nghiệp vụ, hủy migrate.

Giữ nguyên: khoản kiểu cũ, bảng kê cũ, báo cáo tài khoản, snapshot.

## Technical Context

**Language/Version**: Python 3.13 (stdlib), JavaScript thuần (`src/pcms/web/p01.js`).

**Primary Dependencies**: không thêm thư viện. Dùng `decimal` (prec 80, `ROUND_HALF_UP`) và `datetime.date`.

**Storage**: JSON event-sourced (`P01Store`). Thêm khóa trạng thái `loans`, `loan_details`, `loan_waivers`. Thêm trường `business` và `business_history` trên nút danh mục.

**Testing**:
- `unittest`: `tests/test_p49_loan_business.py` và hồi quy toàn bộ suite.
- `node --test tests/js/` cho các hàm thuần của giao diện.

**Target Platform**: máy chủ cục bộ `python -m pcms serve --p01`, dùng qua trình duyệt trên máy Thạch.

**Project Type**: ứng dụng web cục bộ, một tiến trình.

**Performance Goals**: `view()` trên dữ liệu thật (khoảng 220 giao dịch, 6 khoản) chậm thêm không quá 20% so với P48 (khoảng 1,2 giây). Sổ tính theo đoạn sự kiện, không lặp từng ngày.

**Constraints**:
- Không ghi vào `outputs/p01-user-trial` hoặc `private-data`.
- Không đổi `report()`, vì snapshot so sánh trên nó.
- Tiền dùng Decimal; lưu dạng chuỗi số nguyên VND.

**Scale/Scope**:
- 1 module mới, khoảng 6 module phải sửa.
- 3 màn phải sửa: Danh mục, Công nợ, hộp Phân loại.
- Các màn chỉ đọc: Đối tượng, Tổng tài sản, tóm tắt tài khoản.

## Nghiên cứu tác động *(bắt buộc nếu đổi nghiệp vụ/cấu trúc)*

- [research.md](research.md): các điểm nối trong mã, quyết định kỹ thuật, các phương án bị loại.
- [quickstart.md](quickstart.md): kịch bản kiểm tra đồng nhất giữa các màn, chạy trên dữ liệu giả mô phỏng cấu trúc thật (Hot Debt có Kết/Tươi, khoản kiểu cũ ở gốc Gốc vay, dòng lịch sử cũ).
- Chạy `/speckit-analyze` trước `/speckit-implement`; kết quả lưu ở [analysis.md](analysis.md).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Nguyên tắc | Đánh giá | Ghi chú |
|---|---|---|
| I. Dữ liệu thật bất khả xâm phạm | ĐẠT | Chỉ đọc bản sao trong scratchpad. QA chạy trên `PCMS-QA/p49-po`. So hash trước/sau khi phát hành. |
| II. Không tự quyết số liệu thật | ĐẠT | Không có thao tác tự động: gắn nghiệp vụ, tạo khoản, ghi chi tiết đều do người dùng xác nhận. Chưa phát hành trước khi có review độc lập. |
| III. Decimal | ĐẠT | Lãi tính chính xác, chỉ làm tròn một lần trên tổng lũy kế (nửa lên). Gốc lẻ không bị cắt, không vốn hóa lãi. R43 (500 đ/triệu/ngày) vẫn đúng, như một mức lãi. |
| IV. Lịch sử bất biến | ĐẠT | Chi tiết có phiên bản. Hủy, sửa, miễn giảm, hoàn tất đều cần lý do và có lịch sử. Snapshot không đổi vì chi tiết lưu ngoài giao dịch. |
| V. Bằng chứng | ĐẠT (kế hoạch) | Test theo bảng ví dụ, QA qua giao diện. QA của người triển khai tách khỏi nghiệm thu của PO. |
| VI. Gọn | ĐẠT | Một module mới. Một kiểm tra bất biến chung thay vì vá nhiều đường. Không viết lại khoản cũ. |
| VII. Danh mục trung tâm | ĐẠT | Nghiệp vụ là lớp song song trên danh mục. Cây danh mục, cách chọn theo cấp và tải theo danh mục giữ nguyên. Người vẫn là thành viên danh mục. |
| VIII. Kế toán | ĐẠT | Spec có mục "Tư vấn kế toán": không bù trừ, thận trọng với lãi chưa thu, miễn giảm không phải tiền thu, phần thuế cần kế toán viên. |
| IX. Rà soát tác động | ĐẠT | Bản đồ ảnh hưởng nằm ở spec và research. Quy tắc cũ bị thay được ghi vào PRODUCT-SPEC. Phát hành một lần, kèm test đồng nhất giữa các màn. |

Kiểm lại sau Phase 1: không phát sinh vi phạm.

## Thiết kế chính

1. **Nghiệp vụ danh mục** (`categories.py` và phần mới trong `loan_business.py`)
   - Lưu tại `node['business']={'type':'RECEIVABLE'|'PAYABLE', at, reason}`.
   - `lb_effective(s,node_id)` lấy nghiệp vụ hiệu lực bằng cách đi lên chuỗi cha.
   - Hành động `lb-category-set` / `lb-category-clear`, có xem trước qua `/api/lb-category-preview` kèm `review_token`.
2. **Khoản vay** (`s['loans']`)
   - Hành động `lb-loan-create` / `lb-loan-edit`.
   - Người phải là thành viên ACTIVE của một danh mục trong nhánh có nghiệp vụ; chiều khoản lấy theo nghiệp vụ đó.
3. **Chi tiết nghiệp vụ** (`s['loan_details']`)
   - Mỗi bản ghi có `versions` (POSTED/VOID) và `draft`.
   - Hành động `lb-detail-draft` / `lb-detail-post` / `lb-detail-void` / `lb-detail-discard`.
   - Nguồn là giao dịch ngân hàng hoặc dòng lịch sử cũ, lấy qua `cat_parts`, nên các lần chuyển hoặc gộp đối tượng (`cat_eff`) được tính đúng.
4. **Sổ khoản vay** `loan_book(s, as_of)`
   - Khoản kiểu mới tính bằng động cơ lãi theo ngày.
   - Khoản kiểu cũ lấy nguyên dòng từ `debt_register`.
   - Cho ra: tổng theo chiều, theo người (hai khối), theo danh mục, theo tài khoản; danh sách chờ; các số đếm.
   - `asset_core`, `category_view`, `object_view` và màn Công nợ đều đọc từ sổ này.
5. **Kiểm tra bất biến chung**
   - Bọc `P01Store.change`. Với mọi hành động không phải `lb-*`, so dấu vân tay nghiệp vụ trước và sau.
   - Với bản đã ghi: nhóm (danh mục, người, số tiền, nghiệp vụ hiệu lực) phải giữ nguyên.
   - Với nháp và khoản vay: nghiệp vụ hiệu lực phải giữ nguyên.
   - Lệch thì báo `ValidationError` kèm hướng dẫn.
6. **Ràng buộc phân loại mới**: phần tiền mới trong danh mục có nghiệp vụ chỉ nhận hồ sơ Người, không nhận hồ sơ khoản kiểu cũ. Áp dụng ở `classify`, xem trước Sửa phân loại và dòng lịch sử cũ.
7. **Xóa hẳn danh mục**: `cat_in_use_fast` thêm lý do chặn "đã gắn nghiệp vụ / có khoản vay / có chi tiết nghiệp vụ" (bổ sung R201).
8. **Giao diện**
   - Danh mục: dòng Nghiệp vụ, nút gắn/gỡ, hộp xem trước.
   - Hộp Phân loại: sau khi lưu thì mở bộ Chi tiết nghiệp vụ.
   - Bộ Chi tiết nghiệp vụ dùng chung cho mọi lối vào.
   - Công nợ: khối mới, danh sách chờ, các hộp khoản vay, miễn giảm, hoàn tất.
   - Đối tượng: hiện hai chiều.
   - Tóm tắt tài khoản: thêm dòng nghiệp vụ.
   - Capability `loan-business` dùng để bật phần giao diện mới.

## Vòng sửa theo PO review 28/10 (29/10/2026)

Nguồn: `docs/po-review-046-2026-10-28.md` (P1, P2). Không mở spec mới; sửa trong worktree `PCMS-wt-046`, nhánh `046-loan-business`.

- **P1 — khóa điều khoản**: `lb_terms_locked(s, loan)` (loan_business.py) trả lý do khi khoản đã từng có phát sinh được ghi. `lb-loan-edit` chặn đổi `rate` và điều khoản môi giới (có/không, mức) khi khóa; tên môi giới vẫn đổi được. `loan_book.loans[]` thêm `terms_locked`, `terms_lock_reason`; form "Sửa thông tin" khóa ô mức lãi / môi giới và ghi lý do. Không thêm tính năng ngày hiệu lực.
- **P2 — người + khoản khi phân loại**:
  - Phần phân loại thêm trường `loan`. Một hàm kiểm chung `lb_new_part_issue(s, part)` (danh mục hiệu lực có nghiệp vụ → cần Người + khoản đúng người, đúng chiều, chưa hoàn tất; phần có `loan` mà danh mục không có nghiệp vụ → lỗi).
  - Gọi ở `classify` (một dòng và hàng loạt; phần giữ y nguyên phần cũ được miễn), `reclassify_preview` (block `LOAN_BUSINESS`; payload giữ `loan`), `reclass_apply` cho dòng lịch sử cũ, `legacy_preview`/`legacy-import` (lưu `loan` vào lần migrate và từng dòng).
  - Lưới an toàn: `lb_fingerprint` thêm tập phần tiền lỗi; `lb_guard` chặn khi xuất hiện phần lỗi **mới** (phần mới/đổi, hoặc phần có khoản trở nên lệch người/chiều/không còn nghiệp vụ). Phần y nguyên trở thành thuộc nghiệp vụ (gắn nghiệp vụ, chuyển nhánh) được giữ và vào danh sách chờ — ngoại lệ lịch sử.
  - Nhóm chi tiết nghiệp vụ đổi khóa thành (danh mục, người, khoản|null). Dòng phải đúng khoản của nhóm; nhóm null (phần cũ) nhận khoản bất kỳ của người đó cùng chiều.
  - Giao diện: ô "Khoản vay" (lọc theo người, chiều, chưa hoàn tất) trong hộp Phân loại (cả hàng loạt), Sửa phân loại, Migrate lịch sử cũ; nút "+ Tách thêm phần" hiện khi có nghiệp vụ để chia nhiều khoản; thiếu khoản thì không gửi và hộp giữ nguyên.
- **Test trước**: `ReviewP1RetroactiveTerms`, `ReviewP2PersonAndLoanRequired` trong `tests/test_p49_loan_business.py`, chạy đỏ trước khi sửa (`evidence/review-r1-red.txt`). Sửa test cũ `test_edit_needs_reason_history_and_rate_correction_changes_interest` (coi tính lại lãi lịch sử là đúng) và `test_over_paying_broker_warns_not_blocks` (dùng sửa mức môi giới sau khi ghi).
- **Rủi ro**: hiệu năng bất biến mới (duyệt mọi phần tiền mỗi thao tác khi có nghiệp vụ) — dữ liệu thật hiện chưa gắn nghiệp vụ nên đường nhanh bỏ qua; đo lại P48/P49 trên bản sao.

## Project Structure

### Documentation (this feature)

```text
specs/046-loan-business/
├── spec.md, plan.md, research.md, data-model.md, quickstart.md
├── contracts/actions.md      # hành động, endpoint xem trước, hình dạng loan_book
├── analysis.md               # kết quả /speckit-analyze
├── tasks.md                  # /speckit-tasks
├── traceability.md           # yêu cầu → task → test → bằng chứng QA
└── review.md                 # QA của người triển khai, giới hạn, hướng dẫn
```

### Source Code (repository root)

```text
src/pcms/
├── loan_business.py     # MỚI: nghiệp vụ danh mục, khoản vay, chi tiết, sổ, lãi, miễn giảm, hoàn tất, bất biến
├── p01.py               # mixin; change() bọc bất biến; classify (chỉ Người); view; build P49
├── categories.py        # cat_in_use_fast; category_view (business, khoản vay của thành viên)
├── reclassify.py        # block NOT_PERSON / LOAN_DETAIL trong xem trước
├── assets.py            # Phải thu/Phải trả lấy từ loan_book
├── objects.py           # object_view hai chiều; obj_in_use tính cả khoản vay
├── server.py            # /api/lb-category-preview, /api/lb-detail-preview, /api/loan-book
└── web/p01.js, p01.css  # giao diện
tests/
├── test_p49_loan_business.py     # MỚI
└── js/loan_business.test.cjs     # MỚI (hàm thuần: nhãn thành phần, số còn phải phân bổ)
```

**Structure Decision**: giữ nguyên cấu trúc một dự án hiện có. Thêm một mixin mới vào `P01Store`, giống cách các spec trước đã làm (Reclassify, Objects…).

## Complexity Tracking

Không có vi phạm Constitution cần biện minh.
