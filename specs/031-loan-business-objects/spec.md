# Feature Specification: Nghiệp vụ gắn đối tượng trong danh mục (cho vay trước)

**Feature Branch**: `031-loan-business-objects` · **Created**: 2026-10-15 · **Status**: Draft
**Input**: Thạch chốt (15/10/2026): tách "quản lý danh mục" (dòng tiền gộp) khỏi "quản lý nghiệp vụ" (quy tắc kế toán có trạng thái). Nghiệp vụ gắn vào **cặp (đối tượng, danh mục)**; danh mục mang vai trò dòng tiền trung tính; đối tượng chỉ mang loại nghiệp vụ và tham số; không bắt chọn vai trò từng giao dịch; danh mục thường (chi tiêu, thu nhập) không cần đối tượng/nghiệp vụ; hợp nhất hồ sơ đối tượng + nghiệp vụ làm một lượt; **Cho vay làm trước**; mâu thuẫn vai trò thì **chặn hẳn**. Tham chiếu spec 016, 019, 026, 029, 030; Constitution VII, VIII; R136–R145.

## Tư vấn kế toán (Constitution VIII)
- **Mô hình ba lớp** (khuyến nghị): (1) sổ giao dịch nguồn không đổi; (2) danh mục là tổng hợp dòng tiền, mang vai trò trung tính; (3) nghiệp vụ là lớp ghi nhận kế toán có trạng thái, gắn vào đối tượng. Đây là cách sổ chi tiết kế toán vận hành: tài khoản tổng hợp (danh mục) + sổ chi tiết theo đối tượng (nghiệp vụ). Số liệu nghiệp vụ chỉ **đọc** từ phân loại, không tạo/sửa tiền.
- **Cho vay / đi vay**: tách **Phải thu (cho vay)** và **Phải trả (đi vay)**, không bù trừ kể cả cùng một người. Gốc và lãi tách riêng: lãi không làm đổi dư nợ gốc. Giải ngân làm tăng dư nợ; thu/trả gốc làm giảm; thu quá gốc là bất thường phải cảnh báo, không tự cắt.
- **Cơ sở ghi nhận**: bản này theo **tiền thực thu/chi (cash basis)**, ghi nhãn rõ; **không** dồn tích lãi, không trích dự phòng, không xóa nợ.
- **Đổi loại nghiệp vụ** sau khi đã có dữ liệu: có ngày hiệu lực + lý do + lịch sử, không sửa số cũ (bất biến, nguyên tắc IV). Không cho đổi chiều (cho vay ↔ đi vay) của cặp đã có giao dịch phát sinh trước ngày hiệu lực mà không ghi lịch sử.
- **Cần kế toán viên/thuế xác nhận**: dồn tích lãi, dự phòng nợ khó đòi, xóa nợ, lãi phạt, lãi suất theo kỳ, xử lý thuế thu nhập từ lãi cho vay. Bản này không tính các khoản đó.

## User Scenarios & Testing
### User Story 1 - Gắn nghiệp vụ cho đối tượng trong danh mục (Priority: P1)
Trong màn Danh mục, mỗi đối tượng thuộc danh mục có nút "Nghiệp vụ". Chọn loại (Cho vay / Đi vay / Bất động sản), tham số (lãi suất thỏa thuận ghi nhận, ngày đáo hạn, ghi chú), ngày hiệu lực. Chỉ hiện loại hợp với vai trò của danh mục.

**Acceptance Scenarios**:
1. **Given** đối tượng Mỹ trong danh mục con của Gốc vay, **When** gắn "Cho vay", **Then** lưu cho cặp (Mỹ, danh mục đó); chip "Cho vay" hiện cạnh Mỹ.
2. **Given** đối tượng trong danh mục Chi tiêu, **When** gắn nghiệp vụ, **Then** bị chặn: "Danh mục này chỉ là dòng tiền thường".
3. **Given** Mama có cặp "Cho vay" ở danh mục A và "Đi vay" ở danh mục B, **When** xem, **Then** hai sổ riêng, không bù trừ.
4. **Given** khoản vay (hồ sơ LOAN) có thiết lập chiều Phải thu, **When** gắn "Đi vay", **Then** bị chặn vì mâu thuẫn chiều.
5. **Given** đối tượng đã có giao dịch, **When** đổi loại, **Then** yêu cầu ngày hiệu lực và lý do, giữ lịch sử.

### User Story 2 - Sổ nghiệp vụ cho vay theo cặp (Priority: P1)
Panel "Nghiệp vụ cho vay" liệt kê từng cặp: chiều, giải ngân/nhận vay, thu/trả gốc, dư nợ gốc, lãi thu/trả, số giao dịch, cảnh báo, bấm xem lịch sử chuẩn.

**Independent Test**: Mỹ (Cho vay): giải ngân 500.000.000, thu gốc 200.000.000 + 100.000.000, lãi thu 6.000.000 → dư nợ 200.000.000, lãi thu 6.000.000. Cùng giao dịch hiển thị ở danh mục dòng tiền (ra 500tr, vào 306tr) mà không đổi con số danh mục.

**Acceptance Scenarios**:
1. **Given** thu gốc vượt giải ngân, **Then** dư nợ âm bị gắn cảnh báo "Thu quá gốc", không tự điều chỉnh.
2. **Given** lãi và gốc phân loại cho cùng một đối tượng, **Then** lãi hiển thị riêng, không đổi dư nợ gốc.
3. **Given** khoản vay có thiết lập ở màn Công nợ, **Then** sổ cặp hiển thị dư nợ cùng đối chiếu với sổ Công nợ; lệch thì cảnh báo.

### User Story 3 - Hợp nhất hồ sơ (Priority: P1)
Nút "Hợp nhất hồ sơ nghiệp vụ" (xem trước → xác nhận): mọi khoản vay (LOAN) thành đối tượng trong danh mục Gốc vay (nhóm hiện có hoặc gốc), kèm loại nghiệp vụ suy từ thiết lập chiều; khoản chưa thiết lập chiều được đưa vào danh mục nhưng **chưa gắn loại** (không đoán). BĐS thành đối tượng của Đầu tư BĐS, nghiệp vụ Bất động sản. Idempotent, có bản ghi, không đổi phân loại hay số liệu hiện có.

**Acceptance Scenarios**:
1. **Given** 2 khoản vay đã thiết lập (1 phải thu, 1 phải trả) và 1 chưa thiết lập, **When** xem trước, **Then** liệt kê 3 dòng với kết quả dự kiến, dòng chưa thiết lập ghi "cần thiết lập chiều trước".
2. **When** xác nhận, **Then** tạo đối tượng đúng; chạy lại không tạo trùng.
3. **Then** báo cáo, snapshot, tổng danh mục, sổ Công nợ không đổi.

### User Story 4 - Chặn mâu thuẫn vai trò (Priority: P1)
Các thao tác làm cặp mang nghiệp vụ sai vai trò bị chặn: gắn sai loại, chuyển đối tượng sang danh mục khác vai trò, gỡ khi đã có giao dịch, lưu trữ danh mục còn cặp nghiệp vụ, gộp hồ sơ khác chiều.

## Requirements
- **FR-001** (R146): vai trò danh mục suy từ gốc: Thu nhập, Chi tiêu (dòng tiền thường); Gốc vay, Lãi vay (vai trò cho vay/đi vay); Đầu tư BĐS (vai trò BĐS); Chuyển nội bộ, Chưa phân loại (không nhận đối tượng). Hiển thị vai trò ở màn Danh mục và `view`.
- **FR-002** (R147): nghiệp vụ gắn vào mục `category_objects` (cặp đối tượng–danh mục): `business={type,effective_date,params,history}`. Loại: `LOAN_LENT` (Cho vay, vai trò Gốc vay), `LOAN_BORROWED` (Đi vay, Gốc vay), `PROPERTY` (Bất động sản, Đầu tư BĐS). Tham số: `interest_note` (số, % thỏa thuận, chỉ ghi nhận), `maturity` (ngày), `note` (≤ 500).
- **FR-003** (R148, chặn hẳn): `business-set` chặn khi danh mục không phải vai trò tương ứng, khi hồ sơ LOAN mâu thuẫn chiều thiết lập (RECEIVABLE ↔ LOAN_LENT, PAYABLE ↔ LOAN_BORROWED), khi hồ sơ PROPERTY gắn loại cho vay hoặc hồ sơ LOAN gắn BĐS, khi đối tượng không thuộc danh mục.
- **FR-004** (R149): đổi/gỡ nghiệp vụ cần `effective_date` và `reason`; ghi `history`; loại theo ngày dùng ngày hiệu lực; không sửa số cũ. Đổi chiều khi đã có giao dịch phải có ngày hiệu lực không sớm hơn giao dịch gần nhất đã phân loại cho cặp.
- **FR-005** (R150): sổ cho vay theo cặp (chỉ đọc): giải ngân/nhận vay, thu/trả gốc, dư nợ gốc theo chiều, lãi thu/trả (phân loại `interest` cùng đối tượng, ghép vào cặp duy nhất của đối tượng; đối tượng có hai cặp cho vay khác nhau thì lãi hiển thị "cần chỉ định cặp" và không cộng bừa), số giao dịch, cảnh báo (`NEGATIVE_BALANCE`, `REGISTER_MISMATCH`, `UNDIRECTED_INTEREST`, `NO_DIRECTION`). Ghi nhãn "tiền thực thu/chi, chưa dồn tích".
- **FR-006** (R151): `business-migrate` hợp nhất hồ sơ (xem trước + xác nhận), idempotent, có bản ghi `business_migrations`, không đổi phân loại/snapshot/Công nợ.
- **FR-007** (R152, chặn hẳn): gỡ đối tượng khỏi danh mục, lưu trữ danh mục, chuyển danh mục, gộp đối tượng bị chặn khi liên quan cặp đang mang nghiệp vụ mâu thuẫn hoặc đã có giao dịch (nêu cách xử lý: gỡ nghiệp vụ có hiệu lực/lý do trước).
- **FR-008** (R153): phân loại khoản vay/BĐS vào danh mục gốc tương ứng không bị chặn bởi việc hợp nhất (hồ sơ LOAN luôn nhận ở Gốc vay/Lãi vay, PROPERTY ở Đầu tư BĐS).
- **FR-009**: Giao diện: chip vai trò ở danh mục gốc, chip nghiệp vụ ở đối tượng, hộp thoại nghiệp vụ, panel sổ cho vay, nút hợp nhất có xem trước; bấm mã giao dịch mở lịch sử chuẩn của đối tượng.
- **FR-010**: Không đổi quy tắc tiền, snapshot, báo cáo, Công nợ; không dồn tích, dự phòng, xóa nợ.

## Success Criteria
- **SC-001**: Đối tượng cho vay hiển thị đúng dư nợ gốc và lãi theo ví dụ User Story 2, khớp tổng ở danh mục.
- **SC-002**: Mọi trường hợp mâu thuẫn FR-003/FR-007 bị chặn với lý do tiếng Việt cụ thể.
- **SC-003**: Hợp nhất hai lần liên tiếp cho kết quả như một lần; số báo cáo/tổng danh mục không đổi.
- **SC-004**: Dữ liệu thật trong `outputs/p01-user-trial` không đổi (checksum baseline).

## Assumptions
- Vai trò danh mục suy từ gốc hệ thống; vai trò do người dùng tự định nghĩa (giá vốn, doanh thu…) thuộc đợt Bán hàng sau.
- Crypto, bán hàng làm sau (thứ tự Thạch: Cho vay → BĐS → crypto → bán hàng); bản này đưa BĐS vào mức gắn loại và hợp nhất, chưa thêm sổ mới.
- Lãi suất thỏa thuận chỉ ghi nhận, không tính lãi (cần kế toán xác nhận trước khi dồn tích).
