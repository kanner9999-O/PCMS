# Feature Specification: Tách danh mục lưu trữ và vá dấu vết xóa (tiếp nối spec 044)

**Feature Branch**: `045-category-archive-tabs`

**Created**: 2026-10-28

**Status**: Draft

**Input**: Yêu cầu của Thạch ngày 28/10/2026 (tách danh mục lưu trữ khỏi màn làm việc; vá P2 và thông báo trong `docs/po-review-044-2026-10-28.md`).

## Truy nguyên

| Mục | Nguồn | Quan hệ |
|---|---|---|
| US1, US2 — tab Đang sử dụng / Đã lưu trữ | Yêu cầu mới 28/10/2026 | Mới: R202, A63 |
| US3 — xóa đối tượng không xóa dấu vết thành viên | PO review 044, P2 | Sửa lỗi của R201/FR-001 (spec 044); spec 044 giữ nguyên lịch sử, chỉ thêm liên kết "sửa ở 045" |
| US4 — thông báo chặn xóa | PO review 044, ghi chú UX | Sửa thông báo của R201/FR-002 (spec 044) |
| Quy tắc gốc | R93, R123–R128 (nguyên tắc VII), R201 | Không đổi quy tắc: đã dùng → chỉ lưu trữ |

## Bản đồ tác động *(nguyên tắc IX; tìm theo mã nguồn và bản sao chỉ đọc dữ liệu thật)*

| Khu vực | Hiện trạng | Tác động |
|---|---|---|
| Màn Danh mục (cây theo gốc, mọi nút kể cả đã lưu trữ trộn chung) | Danh mục lưu trữ hiện xen trong cây với nhãn "đã lưu trữ" | Tách 2 tab; tab hoạt động chỉ hiện mục đang dùng; tổng ghi rõ phần thuộc danh mục lưu trữ |
| Tổng danh mục gốc/cha | Đã gồm giao dịch thuộc danh mục lưu trữ | Không đổi cách tính; thêm ghi chú và lối xem |
| Bộ chọn danh mục (phân loại, Sửa phân loại, migrate lịch sử cũ, thêm/chuyển đối tượng, đổi cha, nhóm khoản vay) | Chỉ liệt kê danh mục đang hoạt động; hệ thống từ chối danh mục lưu trữ khi ghi | Không đổi; bảo đảm danh mục hoạt động dưới cha đã lưu trữ (nếu có) vẫn chọn được |
| Lưu trữ/khôi phục | Lưu trữ cha bị chặn khi còn con hoạt động; khôi phục con bị chặn khi cha đang lưu trữ; tạo/đổi cha vào danh mục lưu trữ bị chặn | Không đổi, không dây chuyền |
| Xóa hẳn danh mục: nút, lệnh xóa, dọn danh mục | Cùng một quy tắc "đã từng dùng" (spec 044) | Thêm dấu vết thành viên của đối tượng đã xóa; sửa lời thông báo |
| Xóa hẳn đối tượng (2 đường: màn Đối tượng, trong danh mục) | Xóa luôn quan hệ thành viên, bản ghi xóa không giữ danh mục | Giữ dấu vết thành viên trong bản ghi xóa |
| Lịch sử danh mục, báo cáo, Công nợ, BĐS, snapshot | — | Không đổi |
| Dữ liệu thật (28/10) | 8 danh mục con/gốc riêng, 3 đã lưu trữ (Kết, Bianance, Anh Tự — lý do "Thừa"); không có con hoạt động dưới cha lưu trữ; chưa từng xóa đối tượng | Không sửa dữ liệu; sau phát hành 3 mục trên chuyển sang tab Đã lưu trữ |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Màn danh mục chỉ tập trung vào danh mục đang dùng (Priority: P1)

Thạch mở Danh mục: tab **Đang sử dụng** mở mặc định, chỉ có danh mục hoạt động; tab **Đã lưu trữ (N)** cho biết còn N danh mục lưu trữ. Tổng của gốc/cha vẫn như trước; ngay dưới tổng ghi rõ "gồm X giao dịch thuộc K danh mục đã lưu trữ" và có lối mở tab lưu trữ để đối chiếu.

**Why this priority**: mục tiêu chính của yêu cầu — màn làm việc gọn mà số không "lệch" trong mắt người dùng.

**Independent Test**: lưu trữ một danh mục có giao dịch trên dữ liệu giả; so tổng gốc trước/sau và đối chiếu với tab lưu trữ.

**Acceptance Scenarios**:

1. **Given** có danh mục đã lưu trữ, **When** mở Danh mục, **Then** tab Đang sử dụng được chọn, không có danh mục lưu trữ như mục làm việc, nhãn tab lưu trữ có số lượng đúng.
2. **Given** danh mục lưu trữ có giao dịch, **When** xem tổng của gốc chứa nó, **Then** tổng bằng đúng tổng trước khi lưu trữ, có ghi chú số giao dịch/tiền thuộc danh mục lưu trữ và nút xem chi tiết.
3. **Given** đang ở tab Đã lưu trữ hoặc đang gõ tìm, **When** chuyển tab qua lại hoặc sau một thao tác, **Then** tab đang chọn và dữ liệu không mất (danh sách tải lại đúng).

---

### User Story 2 - Quản lý riêng danh mục đã lưu trữ (Priority: P1)

Trong tab **Đã lưu trữ**: tìm theo tên; mỗi dòng có đường dẫn cha → con, số liệu, thời điểm và lý do lưu trữ (nếu có trong lịch sử; nếu không có thì ghi "không có dữ liệu"), nút Lịch sử, nút **Khôi phục**. "Xóa hẳn" chỉ hiện khi hệ thống xác nhận chưa từng dùng; nếu không, ghi rõ vì sao chỉ có thể giữ lưu trữ.

**Why this priority**: lưu trữ chỉ có ích khi vẫn tìm, xem và khôi phục được.

**Independent Test**: lưu trữ 2 danh mục trùng tên ở hai cha khác nhau, tìm theo tên, phân biệt bằng đường dẫn, khôi phục một cái.

**Acceptance Scenarios**:

1. **Given** hai danh mục lưu trữ trùng tên, **When** tìm tên đó, **Then** thấy cả hai với đường dẫn khác nhau.
2. **Given** danh mục lưu trữ có cha đang hoạt động, **When** Khôi phục, **Then** về tab Đang sử dụng đúng vị trí cũ, số lượng hai tab cập nhật, tổng không đổi.
3. **Given** danh mục lưu trữ có cha cũng đang lưu trữ, **When** xem dòng đó, **Then** nút Khôi phục báo cần khôi phục cha trước (nêu tên cha); không tự khôi phục dây chuyền.
4. **Given** danh mục lưu trữ chưa từng dùng, **When** Xóa hẳn với lý do, **Then** xóa được, có bản ghi đã xóa; **Given** từng dùng, **Then** không có nút xóa, có lý do.

---

### User Story 3 - Xóa đối tượng không mở khóa xóa danh mục (Priority: P1)

Danh mục từng có đối tượng thành viên vẫn được coi là đã dùng sau khi đối tượng đó bị xóa hẳn (kể cả gỡ khỏi danh mục rồi mới xóa). Đối tượng chưa dùng vẫn xóa được như trước.

**Why this priority**: lỗi làm sai quy tắc R93/R201 và mất dấu vết quan hệ (nguyên tắc IV).

**Independent Test**: tạo danh mục + đối tượng, xóa hẳn đối tượng, kiểm tra nút/lệnh/dọn danh mục.

**Acceptance Scenarios**:

1. **Given** danh mục có một đối tượng chưa dùng, **When** xóa hẳn đối tượng (ở màn Đối tượng hoặc trong danh mục), **Then** xóa thành công; bản ghi xóa lưu danh mục và lịch sử thành viên; danh mục vẫn không xóa được (nút ẩn, lệnh từ chối, không có trong danh sách dọn).
2. **Given** gỡ đối tượng khỏi danh mục rồi mới xóa hẳn đối tượng, **Then** như trên.
3. **Given** danh mục chưa từng có đối tượng/giao dịch, **Then** vẫn xóa hẳn và dọn được.

---

### User Story 4 - Thông báo không hướng dẫn thao tác vô ích (Priority: P2)

Khi bị chặn xóa vì đã từng dùng, thông báo nêu nguyên nhân cụ thể và hướng dẫn "Lưu trữ để ẩn khỏi danh sách đang sử dụng"; không gợi ý gỡ/chuyển đối tượng như cách mở quyền xóa. Áp dụng cho xóa đơn và mô tả dọn danh mục.

**Acceptance Scenarios**:

1. **Given** danh mục có đối tượng thành viên, **When** thử xóa, **Then** thông báo nêu số đối tượng và hướng dẫn Lưu trữ, không có "gỡ hoặc chuyển đối tượng".

### Edge Cases

- Cha lưu trữ nhưng con hoạt động: hệ thống hiện chặn mọi đường tạo ra trạng thái này; nếu vẫn tồn tại (dữ liệu cũ), con hoạt động vẫn hiện ở tab Đang sử dụng dưới cha hiển thị dạng ngữ cảnh "đã lưu trữ" (không có thao tác làm việc), và vẫn chọn được khi phân loại.
- Con lưu trữ, cha hoạt động: cha ở tab Đang sử dụng (tổng gồm con, có ghi chú); con ở tab Đã lưu trữ.
- Danh mục gốc riêng (không có cha) bị lưu trữ: thuộc tab Đã lưu trữ cùng danh mục con của nó.
- Đang xem theo kỳ: hai tab và ghi chú tổng dùng số liệu của kỳ đó.
- Tab Đã lưu trữ trống: thông báo "Chưa có danh mục nào được lưu trữ".
- Xóa hẳn đối tượng đã từng dùng: vẫn bị chặn như hiện hành.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001** (R202): Màn Danh mục có hai tab: "Đang sử dụng" (mặc định, chỉ danh mục hoạt động, giữ cây cha → con theo gốc) và "Đã lưu trữ (N)". Tab đang chọn giữ nguyên sau thao tác và khi đổi kỳ.
- **FR-002** (R202): Tổng gốc/cha không đổi cách tính (gồm giao dịch thuộc danh mục lưu trữ). Khi tổng có phần thuộc danh mục lưu trữ, ghi rõ số giao dịch và tiền của phần đó kèm lối mở tab Đã lưu trữ.
- **FR-003** (R202): Tab Đã lưu trữ: tìm theo tên; mỗi dòng có đường dẫn đầy đủ, số liệu (theo kỳ đang chọn), thời điểm và lý do lưu trữ lấy từ lịch sử (không có thì ghi rõ không có dữ liệu), Lịch sử, Khôi phục (hoặc lý do không khôi phục được, ví dụ cha đang lưu trữ), Xóa hẳn chỉ khi hệ thống cho phép, nếu không thì nêu lý do.
- **FR-004** (R202): Không tự lưu trữ/khôi phục dây chuyền; danh mục hoạt động không bị mất đường truy cập vì cha bị lưu trữ (màn và bộ chọn).
- **FR-005** (R202): Danh mục lưu trữ không chọn được cho phân loại mới, migrate, thêm đối tượng (giữ quy tắc hiện hành ở cả màn và hệ thống).
- **FR-006** (sửa R201 FR-001): Xóa hẳn đối tượng (mọi đường) giữ lại dấu vết danh mục và lịch sử thành viên trong bản ghi xóa; kiểm tra "danh mục đã từng dùng" đọc dấu vết này. Nút, lệnh xóa và dọn danh mục dùng cùng quy tắc.
- **FR-007** (sửa R201 FR-002): Thông báo chặn xóa nêu nguyên nhân và hướng dẫn Lưu trữ; không gợi ý thao tác không mở được quyền xóa. Mô tả hộp Dọn danh mục nêu đúng điều kiện.
- **FR-008**: Không đổi tiền, tổng, báo cáo, snapshot; không sửa dữ liệu thật.

### Key Entities

- **Danh mục** (hoạt động / lưu trữ; lịch sử gồm lần lưu trữ có thời điểm và lý do).
- **Quan hệ thành viên đối tượng–danh mục** và **bản ghi đối tượng đã xóa** (nay mang dấu vết thành viên).

## Tư vấn kế toán *(nguyên tắc VIII)*

- Ẩn khoản mục khỏi màn làm việc là trình bày, không phải xóa sổ: số dư/tổng vẫn phải gồm phát sinh của khoản mục đã khóa, và trình bày phải công bố phần đó (minh bạch, đối chiếu được) — đề xuất ghi chú tổng và lối xem chi tiết.
- Khoản mục đã có phát sinh hoặc đã từng gắn đối tượng chỉ được khóa (lưu trữ), không xóa; dấu vết quan hệ phải còn khi xóa đối tượng (chứng từ/dấu vết bất biến).
- Không có vấn đề thuế/pháp lý cần kế toán viên xác nhận.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Mở màn Danh mục, 0 danh mục lưu trữ xuất hiện như mục làm việc trong tab mặc định; số trên tab lưu trữ đúng 100%.
- **SC-002**: Tổng mọi gốc/cha/đối tượng, Công nợ, báo cáo trước/sau phát hành và trước/sau lưu trữ/khôi phục giống hệt (kiểm trên dữ liệu giả và bản sao chỉ đọc dữ liệu thật).
- **SC-003**: Với mọi gốc, tổng = tổng các mục hiển thị trong tab hoạt động + phần ghi chú "thuộc danh mục lưu trữ" (đối chiếu được).
- **SC-004**: 0 trường hợp danh mục từng có đối tượng trở nên xóa được sau khi xóa đối tượng; 100% danh mục hiện "Xóa hẳn" thì lệnh xóa thành công và có trong danh sách dọn khi là danh mục con.
- **SC-005**: 0 thông báo chặn xóa gợi ý gỡ/chuyển đối tượng.
- **SC-006**: Tìm một danh mục lưu trữ theo tên và khôi phục trong ≤ 3 thao tác.

## Assumptions

- "Lý do/thời điểm lưu trữ" lấy từ lịch sử danh mục (đã ghi từ trước); không suy diễn khi thiếu.
- Đối tượng đã xóa từ trước bản này không có dấu vết thành viên (dữ liệu thật: 0 lần xóa đối tượng) — không khôi phục ngược.
- Phát hành theo quy trình hiện hành; QA riêng dữ liệu giả ở `PCMS-QA` (ngoài repo).
- Tham chiếu: spec 016/034 (dọn danh mục), 041 (đối tượng), 044 (chặn xóa).
