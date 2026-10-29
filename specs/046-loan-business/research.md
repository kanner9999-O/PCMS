# Research — spec 046

## 1. Điểm nối trong mã (tìm bằng grep, nhánh `origin/main` 589f449)

| Khái niệm | Nơi tạo/sửa | Nơi hiển thị | Nơi tính số |
|---|---|---|---|
| Phân loại tiền | `p01.change('classify')`, `reclassify.reclass_apply`, `categories.change_category('category-correct-classification')`, `legacy_import` (migrate, void) | Lịch sử giao dịch, Kiểm tra phân loại | `categories.cat_parts` (giao dịch + `legacy_items`, qua `cat_eff`) |
| Đối tượng trong danh mục | `category-object-add/remove/move/merge/delete`, `object-*` | Danh mục, Đối tượng | `category_view` (oacc), `object_view` |
| Khoản vay kiểu cũ | `profile` (kind LOAN), `loan-setup`, `interest-terms`, `loan-regroup` | Công nợ (`debt_register`), Tổng tài sản | `debt_register`, `interest_preview`, `closure_preview` |
| Nghiệp vụ cặp (spec 031) | `business-*` (bị chặn từ `business_enabled=False`) | ẩn | `business_view` (ẩn) |
| Phải thu/Phải trả tổng | — | Tổng tài sản | `assets.asset_core` → `debt_register.people` |
| Xóa hẳn danh mục | `category-delete`, `category-cleanup` | nút Xóa hẳn | `cat_in_use_fast` (R201, R202) |
| Đổi cha danh mục | `category-edit` (parent) | Danh mục | — |
| Mức B sửa phân loại | `reclassify_preview` | hộp Sửa phân loại | `reclass_signature`, `reclass_snapshot` (đọc `debt_register`) |
| Snapshot | `approve` | Lịch sử duyệt | `report()` → `financial_content` |

**Kết luận**:
- Mọi đường đổi phần tiền đều đi qua `change()`.
- Mọi phép tính đọc phần tiền đều đi qua `cat_parts`, và `cat_eff` áp dụng việc chuyển hoặc gộp đối tượng.
- Vì vậy chỉ cần một dấu vân tay nghiệp vụ tính trên `cat_parts`, so trước và sau `change()`, là bao được mọi đường sửa song song (FR-005, SC-005).

## 2. Quyết định

### D1 — Chi tiết nghiệp vụ lưu ngoài giao dịch
- **Decision**: lưu ở `s['loan_details']`, không lưu trong `transaction.allocations`.
- **Rationale**:
  - `approve` lưu `report()` gồm cả allocations, và `financial_changed` so nội dung đó. Nếu chi tiết nằm trong allocations thì mỗi lần hoàn thiện chi tiết sẽ đòi mở phiên điều chỉnh và tạo bản duyệt mới. Điều này trái FR-014/FR-015, vì người dùng được chốt sao kê trước khi chi tiết nghiệp vụ xong.
  - Dòng lịch sử cũ không có allocations thật.
- **Alternatives**: thêm trường `loan`/`component` vào allocation. Bị loại vì đổi snapshot và vì nháp/bản hiện hành khó giữ song song.

### D2 — Khoản vay kiểu mới ở `s['loans']`
- **Decision**: lưu ở `s['loans']`, không dùng hồ sơ `kind='LOAN'`.
- **Rationale**:
  - Hồ sơ trong `profiles` bị ràng buộc tên duy nhất toàn hệ thống (R138), nên hai người không thể cùng có khoản tên "Vay tháng 10".
  - Hồ sơ LOAN còn được xử lý ở nhiều nơi: `part_owner`, `cat_eff` nhóm khoản, gộp, đối tượng… Đi qua những nơi đó dễ gây lệch.
  - Khoản mới không xuất hiện như một đối tượng, đúng spec 041.
- **Alternatives**: dùng lại hồ sơ LOAN. Bị loại vì các lý do trên.

### D3 — Một sổ `loan_book`
- **Decision**: `loan_book` gồm khoản mới (động cơ mới) và khoản cũ (dòng lấy từ `debt_register`, không tính lại).
- **Rationale**: FR-012, mọi màn dùng một nguồn. Khoản cũ giữ đúng số cũ (SC-004). Không có phần tiền nào được tính ở cả hai nhánh:
  - liên kết cũ là phần có hồ sơ LOAN;
  - chi tiết mới gắn với phần có hồ sơ PERSON;
  - một phần tiền chỉ có một hồ sơ.
- **Alternatives**: chuyển khoản cũ sang động cơ mới. Bị loại vì làm đổi số cũ, và brief cấm tự ghi lại.

### D4 — Động cơ lãi theo đoạn sự kiện
- **Decision**: duyệt các ngày có sự kiện theo thứ tự.
  - Đoạn giữa hai ngày sự kiện có cơ sở = dư cuối.
  - Ngày có sự kiện D có cơ sở = dư cuối D−1 + giải ngân D.
  - Dư cuối D = dư cuối D−1 + giải ngân D − trả gốc D.
  - Lãi thô = Σ cơ sở × mức / 1.000.000 × số ngày, Decimal prec 80.
  - Tổng tới ngày xem làm tròn `quantize(1, ROUND_HALF_UP)`.
  - Môi giới dùng cùng cơ sở.
- **Rationale**: khớp ví dụ 6 ngày (300.000) và ví dụ trả 40 triệu. Chi phí tính theo số sự kiện, không theo số ngày.
- **Alternatives**: dùng `interest_preview` cũ. Bị loại vì quy ước cũ là "dư cuối ngày, ngày kết thúc không tính", cho ra 5 ngày (250.000). Hàm cũ giữ nguyên cho bảng kê cũ.

### D5 — Kiểm tra nghĩa vụ
- **Decision**: sau khi áp phiên bản hoặc miễn giảm ứng viên, duyệt từng ngày có sự kiện của khoản và kiểm:
  - dư cuối không âm;
  - lũy kế lãi đã thu/trả + miễn giảm ≤ round(lãi lũy kế tới ngày đó);
  - ngày ≥ ngày theo dõi;
  - khoản chưa hoàn tất.
- **Rationale**: lũy kế thu/trả và miễn giảm chỉ tăng ở ngày có sự kiện, và lãi lũy kế không giảm theo thời gian, nên kiểm tại các ngày có sự kiện là đủ.
- Trả môi giới vượt phần theo điều khoản chỉ cảnh báo.

### D6 — Bất biến chung bọc `change()`
- **Decision**: `lb_fingerprint(s)` gồm ba phần:
  1. Với mỗi nguồn có bản đã ghi: tập (khóa danh mục, người, số tiền, nghiệp vụ hiệu lực) của các phần thuộc danh mục có nghiệp vụ.
  2. Với nguồn chỉ có nháp: nghiệp vụ hiệu lực của các danh mục trong nháp.
  3. Với mỗi khoản: nghiệp vụ hiệu lực của danh mục nơi tạo.
  4. Quan hệ thành viên ACTIVE của mọi cặp (danh mục, người) có trong (1)–(3). Lý do: gỡ thành viên không đổi phần tiền nên (1) không bắt được (analyze U1).
- Hành động không phải `lb-*` làm đổi phần (1), (3) hoặc (4), hoặc đổi nghiệp vụ ở phần (2), thì bị chặn.
- Hành động `lb-category-*` có kiểm tra riêng (xem FR-002), kèm thông báo cụ thể.
- **Rationale**: một chỗ, không bỏ sót đường song song (classify, reclassify, object-move/merge/remove, legacy-void, category-edit…). Bỏ qua khi không có `loans`/`loan_details`, nên không tốn thêm chi phí cho dữ liệu hiện có.
- **Alternatives**: chặn ở từng hành động. Bị loại vì dễ sót (đúng bài học của spec 044/045).

### D7 — Hồ sơ trong danh mục có nghiệp vụ
- **Decision**: phần tiền mới chỉ nhận hồ sơ PERSON. Hồ sơ LOAN kiểu cũ còn nguyên trên giao dịch thì vẫn hợp lệ (quy tắc "unchanged" sẵn có).

### D8 — Xác định nguồn
- **Decision**: id giao dịch ngân hàng, hoặc id dòng lịch sử cũ (lấy qua `legacy_items`, chỉ dòng đang hiệu lực).
- Dòng thuộc lần migrate đã hủy thì không nhận chi tiết. Nếu dòng đó đã có bản đã ghi, bất biến D6 chặn việc hủy migrate.

### D9 — Mã khoản
- **Decision**: gợi ý `CV-0001` / `ĐV-0001` theo số kế tiếp của từng chiều; duy nhất toàn hệ thống, so không phân biệt hoa/thường.

### D10 — Chặn hoàn tất khi còn nguồn chờ
- **Decision**: phạm vi chặn là các nguồn chờ có phần tiền thuộc cùng người và cùng chiều, cùng các nháp có dòng gắn khoản này.

## 3. Rủi ro

- **Tốc độ `view()`**:
  - `loan_book` duyệt `cat_parts` một lần.
  - Dấu vân tay chỉ tính khi có dữ liệu nghiệp vụ.
  - Đo lại ở bước QA.
- **Đã có dữ liệu vay kiểu cũ trong Hot Debt**: theo bản sao, 4 phần Chi tiêu có `node` nhưng không có hồ sơ LOAN, nên không có xung đột. 16 liên kết cũ nằm ở gốc hệ thống, ngoài phạm vi gắn nghiệp vụ.
