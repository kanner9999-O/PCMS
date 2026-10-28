# Feature Specification: Chặn xóa hẳn danh mục còn dữ liệu ngoài giao dịch ngân hàng

**Feature Branch**: `044-category-delete-guard`

**Created**: 2026-10-28

**Status**: Draft

**Input**: User description: "Chặn \"Xóa hẳn\" danh mục khi danh mục còn dòng lịch sử cũ (kể cả lần migrate đã hủy, kể cả dòng đã sửa phân loại đi, kể cả lần migrate ghi danh mục này) hoặc còn đối tượng thành viên đang hoạt động; chỉ cho Lưu trữ kèm lý do cụ thể; backend và giao diện như nhau. Kỳ vọng dữ liệu thật: Property và Hot Debt chỉ lưu trữ; Bianance và Long Debt vẫn xóa hẳn được." (Thạch chốt 28/10/2026)

## Bối cảnh và bản đồ tác động *(nguyên tắc IX)*

Quy tắc hiện hành: R93 — "Xóa hẳn danh mục chưa từng dùng (kể cả lịch sử); danh mục đã dùng chỉ lưu trữ". Kiểm tra "đã dùng" hiện chỉ xét: danh mục con, khoản vay từng gắn nhóm, phần phân loại và lịch sử phân loại của giao dịch ngân hàng, bản đã duyệt. **Bỏ sót** các nơi khác cũng lưu danh mục:

| Nơi lưu danh mục | Hiện có được xét khi xóa? | Hệ quả nếu xóa |
|---|---|---|
| Dòng lịch sử cũ (danh mục hiện tại) | Không | Dòng trỏ danh mục không tồn tại; tiền mồ côi khỏi mọi tổng |
| Lịch sử sửa phân loại của dòng lịch sử cũ (spec 043) | Không | Dấu vết trước–sau mất nhãn |
| Lần migrate (danh mục ghi trên lần dán, cả lần đã hủy) | Không | Bản dán gốc mất ngữ cảnh danh mục |
| Đối tượng thành viên đang hoạt động (và lớp nghiệp vụ gắn cặp đối tượng–danh mục) | Không | Quan hệ thành viên/nghiệp vụ trỏ danh mục không tồn tại |
| Quan hệ thành viên đã gỡ/chuyển, lịch sử chuyển đối tượng | Không | Lịch sử đối tượng mất nhãn danh mục |
| Giao dịch ngân hàng, lịch sử phân loại, bản duyệt, khoản vay, danh mục con | Có | — |

Màn chịu tác động: Danh mục (nút "Xóa hẳn" theo cờ "xóa được"), hành động xóa danh mục (API). Không đổi: tiền, tổng, báo cáo, Lưu trữ/Khôi phục, Đối tượng, Công nợ, BĐS. Dữ liệu thật (đọc bản sao 28/10/2026): 8 danh mục con, 4 đang hiện "Xóa hẳn": Bianance, Long Debt (không dữ liệu), Hot Debt (2 đối tượng), Property (20 giao dịch hiển thị từ 36 dòng lịch sử cũ, 5 đối tượng).

## Clarifications

### Session 2026-10-28
- Q: Danh mục còn dữ liệu ngoài giao dịch ngân hàng có được xóa hẳn? → A: Không; chặn khi còn dòng lịch sử cũ (mọi trường hợp nêu trên) hoặc còn đối tượng thành viên đang hoạt động; chỉ lưu trữ, báo lý do (Thạch chốt 28/10/2026).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Không thể xóa mất danh mục đang chứa lịch sử cũ (Priority: P1)

Thạch mở màn Danh mục; danh mục có dòng lịch sử cũ (như Property) không hiện nút "Xóa hẳn", chỉ có "Lưu trữ". Nếu gọi xóa bằng đường khác vẫn bị từ chối với lý do nói rõ còn bao nhiêu dòng lịch sử cũ.

**Why this priority**: Ngăn mất/mồ côi dữ liệu tài chính thật (nguyên tắc I).

**Independent Test**: Trên dữ liệu giả, nhập lịch sử cũ vào một danh mục rồi thử xóa hẳn.

**Acceptance Scenarios**:

1. **Given** danh mục có dòng lịch sử cũ đang hiệu lực, **When** xem màn Danh mục, **Then** không có nút "Xóa hẳn"; **When** gửi lệnh xóa, **Then** bị từ chối với lý do "còn N dòng lịch sử cũ … chỉ có thể lưu trữ", danh mục và dòng giữ nguyên.
2. **Given** lần migrate vào danh mục đã bị hủy, **When** thử xóa, **Then** vẫn bị từ chối (bản dán gốc và dòng của lần đã hủy vẫn được lưu để truy nguyên).
3. **Given** dòng lịch sử cũ từng ở danh mục này rồi được "Sửa phân loại" sang danh mục khác, **When** thử xóa danh mục cũ, **Then** bị từ chối (đã từng dùng).
4. **Given** danh mục bị chặn xóa, **When** bấm Lưu trữ (đủ điều kiện lưu trữ hiện hành), **Then** lưu trữ thành công, tổng không đổi.

---

### User Story 2 - Không xóa danh mục còn đối tượng thành viên (Priority: P1)

Danh mục còn đối tượng thành viên đang hoạt động (như Hot Debt) không xóa hẳn được; lý do nêu số đối tượng và hướng xử lý (gỡ/chuyển đối tượng hoặc lưu trữ).

**Why this priority**: Đối tượng thuộc danh mục là cấu trúc trung tâm (nguyên tắc VII); xóa danh mục làm quan hệ thành viên và nghiệp vụ gắn cặp bị treo.

**Independent Test**: Tạo danh mục, thêm một đối tượng, thử xóa; gỡ đối tượng rồi thử lại.

**Acceptance Scenarios**:

1. **Given** danh mục có đối tượng thành viên đang hoạt động, **When** thử xóa, **Then** bị từ chối, nút ẩn, lý do nêu số đối tượng.
2. **Given** danh mục từng có đối tượng nhưng đã gỡ/chuyển hết, **When** thử xóa, **Then** bị từ chối vì danh mục đã từng được dùng (lịch sử thành viên), chỉ lưu trữ.

---

### User Story 3 - Danh mục thật sự chưa dùng vẫn xóa được (Priority: P2)

Danh mục mới tạo, chưa có giao dịch, lịch sử cũ, đối tượng (như Bianance, Long Debt) vẫn có nút "Xóa hẳn" và xóa được, có lý do và bản ghi đã xóa.

**Why this priority**: Giữ khả năng dọn danh mục tạo nhầm (việc dọn trong giai đoạn migrate).

**Independent Test**: Tạo danh mục trống, xóa hẳn.

**Acceptance Scenarios**:

1. **Given** danh mục chưa từng dùng ở bất kỳ nơi nào, **When** xóa hẳn với lý do, **Then** thành công và có bản ghi đã xóa.

### Edge Cases

- Danh mục cha không có dữ liệu nhưng danh mục con có: đã bị chặn (còn danh mục con) — giữ nguyên.
- Lý do xóa bị chặn có nhiều nguyên nhân: báo nguyên nhân quan trọng nhất trước (danh mục con → khoản vay → giao dịch → lịch sử cũ → đối tượng đang hoạt động → lịch sử thành viên).
- Danh mục đã lưu trữ: quy tắc xóa hẳn giống danh mục đang hoạt động.
- Danh mục gốc hệ thống: không thuộc phạm vi (không xóa được như hiện hành).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001** (R201): Danh mục chỉ được xóa hẳn khi chưa từng được dùng ở **bất kỳ** nơi nào lưu danh mục: ngoài các điều kiện hiện hành, thêm dòng lịch sử cũ (danh mục hiện tại hoặc trong lịch sử sửa phân loại, thuộc lần migrate đang hiệu lực hay đã hủy), lần migrate ghi danh mục này, quan hệ đối tượng thành viên (đang hoạt động hoặc đã gỡ/chuyển) và lịch sử chuyển đối tượng.
- **FR-002** (R201): Khi bị chặn, thông báo nêu lý do cụ thể kèm số lượng (ví dụ "Còn 36 dòng lịch sử cũ …", "Còn 5 đối tượng thành viên …") và hướng xử lý: Lưu trữ.
- **FR-003** (R201): Màn Danh mục và lệnh xóa dùng **cùng một** quy tắc: nút "Xóa hẳn" chỉ hiện khi lệnh xóa sẽ thành công.
- **FR-004**: Không thay đổi tiền, tổng, báo cáo, điều kiện Lưu trữ/Khôi phục, hay dữ liệu thật đang có; không tự xóa danh mục nào.

### Key Entities

- **Danh mục con**: nút cây danh mục; có trạng thái hoạt động/lưu trữ; "đã từng dùng" khi bất kỳ bản ghi nào ở bảng tác động tham chiếu nó.
- **Dòng lịch sử cũ / lần migrate**: dữ liệu chuyển từ bảng tính, gắn danh mục và đối tượng; lần migrate có thể bị hủy nhưng vẫn lưu.
- **Quan hệ đối tượng–danh mục**: thành viên (hoạt động/đã gỡ/đã chuyển) và lớp nghiệp vụ gắn cặp.

## Tư vấn kế toán *(nguyên tắc VIII)*

- **Phương án đúng kế toán (đề xuất, Thạch đã chọn)**: tài khoản/danh mục đã từng có phát sinh — kể cả phát sinh trong sổ cũ chuyển sang — không được xóa mà chỉ khóa (lưu trữ), để chứng từ và sổ chi tiết vẫn truy được về khoản mục gốc (nguyên tắc chứng từ bất biến, có dấu vết; đối chiếu).
- **Hệ quả**: số danh mục "rác" có thể còn lại ở trạng thái lưu trữ; đổi lại, không có khoản tiền nào bị tách khỏi tổng hoặc mất khoản mục.
- **Rủi ro nếu không sửa**: xóa Property làm 36 dòng lịch sử cũ không còn thuộc khoản mục nào, lệch tổng đầu tư BĐS so với sổ cũ.
- Không có vấn đề thuế/pháp lý cần kế toán viên xác nhận.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 0 trường hợp xóa hẳn thành công đối với danh mục có bất kỳ bản ghi nào trong bảng tác động (kiểm bằng test cho từng loại bản ghi).
- **SC-002**: Trên bản sao chỉ đọc dữ liệu thật: Property và Hot Debt không còn "Xóa hẳn"; Bianance và Long Debt vẫn còn; mọi tổng danh mục/đối tượng/công nợ/báo cáo giống hệt bản trước.
- **SC-003**: 100% danh mục hiện nút "Xóa hẳn" thì lệnh xóa thành công, và ngược lại (đồng nhất màn – lệnh).
- **SC-004**: Mỗi lần bị chặn, Thạch thấy lý do kèm số lượng và hướng xử lý ngay trong một thông báo.

## Assumptions

- "Từng có đối tượng thành viên rồi gỡ/chuyển" được coi là đã dùng, theo R93 "chưa từng dùng (kể cả lịch sử)"; đã đối chiếu bản sao chỉ đọc dữ liệu thật 28/10/2026: Bianance và Long Debt không có tham chiếu nào (giữ nút xóa); Property có 36 dòng lịch sử cũ, 7 lần migrate (3 đã hủy), 5 thành viên hoạt động + 1 đã gỡ; Hot Debt 2 thành viên hoạt động; chưa có lịch sử chuyển đối tượng.
- Phát hành theo quy trình hiện hành (PR → merge khi test xanh → kiểm `main` sạch → cập nhật app `:8792`), không gửi lệnh ghi vào dữ liệu thật.
- Tham chiếu: spec 016 (quản lý danh mục khoản vay, R93), 041 (đối tượng hợp nhất), 042 (định danh giao dịch, lịch sử cũ), 043 (sửa phân loại dòng lịch sử cũ).
