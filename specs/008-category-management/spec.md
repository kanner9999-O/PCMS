# Feature Specification: Quản lý danh mục và lịch sử từng danh mục

**Feature Branch**: `008-category-management`
**Created**: 2026-10-11
**Status**: Clarified 11/10/2026 (PO quyết định các điểm còn mở; chờ plan)
**Input**: Thạch hỏi "phần quản lý danh mục đang ở đâu" (11/10/2026). Hiện danh mục là danh sách cố định trong mã; chưa có nơi thêm/sửa danh mục, chưa có màn xem lịch sử và tổng từng danh mục. Nguồn yêu cầu: R06, R45, R46, R50, R55, R56, R58 · Tiêu chí: ACCEPTANCE A06, A41, A46, A51, A54 · Spec liên quan: 001 (phân loại), 002 (đối tượng khoản vay).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Quản lý cây danh mục (Priority: P1)
Thạch có một nơi để xem toàn bộ cây danh mục, tạo danh mục con dưới một gốc hệ thống, sửa tên, mô tả, danh mục cha (trong cùng gốc) và lưu trữ danh mục không dùng nữa; các danh mục nghiệp vụ gốc (Thu nhập, Chi tiêu, Gốc vay, Lãi vay, Đầu tư BĐS, Chuyển nội bộ) giữ tên và cấp cha, chỉ sửa mô tả (R55).

**Why this priority**: là phần R06 còn thiếu; phân loại hiện bị khóa vào danh sách cứng nên không thêm được việc/đối tượng mới như Đất E.

**Independent Test**: tạo "Mua BĐS → Đất E", đổi tên thành "Đất F", dùng ngay khi phân loại một giao dịch; thử tạo trùng tên, đặt danh mục làm cha của chính con nó (vòng lặp) — đều bị chặn kèm lý do.

**Acceptance Scenarios**:
1. **Given** danh mục gốc "Đầu tư BĐS", **When** tạo con "Đất E", **Then** "Đất E" chọn được khi phân loại và gắn tên tài sản.
2. **Given** danh mục đã dùng trong bản duyệt, **When** đổi tên, **Then** snapshot cũ giữ tên lúc duyệt, màn hiện hành hiện tên mới.
3. **Given** hai danh mục cùng cấp, **When** đặt tên trùng hoặc tạo vòng cha-con, **Then** bị chặn.
4. **Given** danh mục có giao dịch, **When** Thạch muốn bỏ, **Then** chỉ lưu trữ (ẩn khỏi lựa chọn mới), không xóa lịch sử.

### User Story 2 - Lịch sử và tổng từng danh mục truy nguyên được (Priority: P1)
Mở một danh mục thấy tổng tiền vào, tổng tiền ra, chênh vào–ra, nguyên tệ, số giao dịch, và danh sách giao dịch cấu thành (kể cả của danh mục con) với mã nguồn, ngày, tài khoản, nội dung, đối tượng, trạng thái, vào/ra; mở được dòng nguồn trong sao kê (R56, R58).

**Why this priority**: yêu cầu chung của Thạch — mọi số tổng phải truy về đúng tập dòng gốc.

**Independent Test**: danh mục cha có hai con: tổng cha = tổng các dòng của cả cây, mỗi dòng đếm một lần; tách riêng nguyên tệ; danh mục chưa có giao dịch hiển thị lịch sử rỗng và "thiếu dữ liệu", không số 0 giả.

**Acceptance Scenarios**:
1. **Given** danh mục cha có con, **When** xem cha, **Then** thấy giao dịch của cả con, mỗi dòng một lần, kèm tổng vào/ra/chênh riêng từng nguyên tệ.
2. **Given** giao dịch tách thành nhiều phần ở nhiều danh mục, **When** xem từng danh mục, **Then** chỉ tính phần thuộc danh mục đó, tổng các phần khớp tiền nguồn.
3. **Given** danh mục chưa có giao dịch, **When** mở, **Then** lịch sử rỗng và nêu rõ chưa có nguồn, không tạo giao dịch giả.

### User Story 3 - Dùng danh mục khi phân loại và kiểm toàn đợt (Priority: P2)
Danh sách danh mục khi phân loại lấy từ cây; phân loại hàng loạt và từng dòng vẫn chỉ đổi dòng được chọn; báo cáo duyệt đếm mỗi giao dịch đúng một lần ở nhóm trực tiếp (R45, R46, R50).

**Independent Test**: chọn 5 dòng, áp một danh mục con: chỉ 5 dòng đổi, tiền nguồn không đổi; báo cáo toàn đợt không trùng/thiếu.

### Edge Cases
- Đổi danh mục của giao dịch đã duyệt → qua điều chỉnh có lý do, không sửa snapshot (R21).
- Danh mục lưu trữ đang gắn giao dịch cũ vẫn hiển thị trong lịch sử, không chọn được cho dòng mới.
- Chuyển danh mục con sang cha khác: lịch sử các giao dịch đã duyệt giữ đường dẫn cũ trong snapshot.
- Danh mục cổ phiếu (R24) và Shop pending: không tạo sẵn; Thạch có thể tạo nhóm con dưới gốc phù hợp nhưng chúng không có nghiệp vụ riêng.

## Clarifications

### Session 2026-10-11 (PO chốt khi rà checklist `category.md`; không có điểm nào cần Thạch trả lời thêm)
- Q: Người dùng có tạo được danh mục gốc mới không? → A: Không ở đợt này. Bảy danh mục gốc hệ thống (Thu nhập, Chi tiêu, Gốc vay, Lãi vay, Đầu tư BĐS, Chuyển nội bộ, Chưa phân loại) cố định; mọi danh mục người dùng tạo là con (trực tiếp hoặc gián tiếp) của một gốc để kế thừa quy tắc chiều tiền và liên kết đối tượng. Đây là cách hiểu R55 "gốc/con" an toàn cho tiền; nếu Thạch cần gốc tự do thì mở đợt sau.
- Q: Danh mục đã lưu trữ có tính vào tổng của cha không? → A: Có. Lịch sử không bao giờ bị loại khỏi tổng; mục lưu trữ hiện nhãn "(đã lưu trữ)" trong danh sách con.
- Q: Độ sâu tối đa và giới hạn tên? → A: Tối đa 4 cấp kể cả gốc; tên 1–100 ký tự sau khi cắt khoảng trắng, mô tả ≤ 500 ký tự; trùng tên chỉ xét giữa các danh mục cùng cha, không phân biệt hoa thường (so sánh sau chuẩn hóa Unicode NFC), tính cả danh mục đã lưu trữ.
- Q: Lưu trữ, khôi phục và đổi cha tác động thế nào? → A: Lưu trữ cần lý do; khôi phục được; lưu trữ cha không tự lưu trữ con nhưng chặn nếu còn con hoạt động. Đổi tên/cha có lịch sử (thời điểm, giá trị trước/sau, lý do tùy chọn); màn hiện hành dùng tên/cha mới, snapshot cũ giữ nguyên.
- Q: Sửa nhầm thì quay lại thế nào? → A: Không có "hoàn tác"; sửa lại bằng một thay đổi mới, lịch sử giữ cả hai.
- Q: Danh mục cũ (khóa cố định) chuyển sang cây thế nào? → A: Khóa cũ trở thành bảy gốc hệ thống; mọi phân loại hiện có giữ nguyên (không gắn danh mục con); không đổi dữ liệu đã ghi.
- Q: Liên kết đối tượng kế thừa thế nào? → A: Gốc quyết định đối tượng bắt buộc như hiện nay: Gốc vay/Lãi vay → khoản vay; Đầu tư BĐS → hồ sơ BĐS; các gốc còn lại không bắt buộc. Danh mục con chỉ là nhóm quản lý thêm, không thay đối tượng.
- Q: Đổi cha sang gốc khác và gốc nào có nhóm con? → A: Chỉ đổi cha trong cùng một gốc. Chỉ các gốc dùng được khi phân loại (Thu nhập, Chi tiêu, Gốc vay, Lãi vay, Đầu tư BĐS) cho tạo nhóm con; Chuyển nội bộ và Chưa phân loại không có nhóm con.
- Q: Quy mô và thiết bị? → A: Tới 200 danh mục và 10.000 giao dịch vẫn dùng được; màn hình điện thoại 375px không tràn ngang.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Hệ thống MUST cho tạo danh mục con dưới một gốc hệ thống (độ sâu tối đa 4 cấp kể cả gốc), sửa tên, mô tả, danh mục cha, lưu trữ và khôi phục danh mục tự tạo; MUST ngăn tên trùng giữa các danh mục cùng cha và vòng lặp cha-con; tên 1–100 ký tự, mô tả ≤ 500 (R55).
- **FR-002**: Danh mục nghiệp vụ gốc MUST giữ tên và cấp cha; chỉ sửa mô tả (R55).
- **FR-003**: Danh mục MUST có lịch sử thay đổi (tên, cha, trạng thái; thời điểm, giá trị trước/sau, lý do — bắt buộc khi lưu trữ); snapshot đã duyệt MUST giữ tên và đường dẫn tại thời điểm duyệt (R21).
- **FR-004**: Quy tắc nghiệp vụ liên kết đối tượng (khoản vay, tài sản) MUST kế thừa nhóm gốc của danh mục; đổi danh mục MUST xóa liên kết không còn phù hợp (R50).
- **FR-005**: Mỗi danh mục MUST có màn lịch sử (trạng thái dòng: Nháp = chưa vào bản duyệt nào, Đã duyệt = nằm trong ít nhất một snapshot; đối tượng = người/khoản vay/BĐS gắn với phần phân loại, trống nếu không có) gồm các giao dịch cấu thành (kể cả của con) với mã nguồn, ngày, tài khoản, nội dung, đối tượng, trạng thái, vào/ra theo nguyên tệ và lối mở dòng nguồn (R58).
- **FR-006**: Tổng của danh mục MUST gồm tổng vào, tổng ra, chênh vào–ra, số giao dịch theo từng nguyên tệ; MUST truy được về đúng tập dòng gốc; MUST NOT đếm đôi khi xem nhóm cha; hoàn tiền MUST NOT bị ẩn do bù trừ; tổng của cha MUST gồm cả danh mục đã lưu trữ (nhãn "đã lưu trữ") (R56, R58).
- **FR-007**: Danh mục chưa có giao dịch MUST hiển thị lịch sử rỗng kèm trạng thái thiếu dữ liệu ("chưa có nguồn" khi chưa tài khoản nào ghi nguồn; "chưa có giao dịch trong các kỳ nguồn đã ghi" kèm các kỳ đó khi đã có nguồn), MUST NOT tạo giao dịch giả hoặc mặc định bằng không (R58).
- **FR-008**: Lựa chọn danh mục khi phân loại MUST lấy từ cây hiện hành, loại danh mục đã lưu trữ khỏi lựa chọn mới; phân loại không được đổi tiền nguồn (R06, R45).
- **FR-009**: Thay đổi này MUST NOT sửa dữ liệu tài chính đã ghi, MUST NOT đổi kết quả báo cáo, snapshot hay công nợ đã có; dữ liệu cũ dùng danh mục cố định MUST tiếp tục hiển thị đúng sau khi chuyển sang cây.

### Key Entities
- **Danh mục**: tên, mô tả, danh mục cha, loại (gốc hệ thống / tự tạo), trạng thái (hoạt động/lưu trữ), lịch sử thay đổi.
- **Phần phân loại của giao dịch**: khóa gốc hệ thống (hiện có), tham chiếu danh mục con tùy chọn (mới), đối tượng (hồ sơ khoản vay/BĐS) và tiền của phần.
- **Tổng danh mục**: dẫn xuất từ các phần phân loại, theo nguyên tệ.

## Success Criteria *(mandatory)*
- **SC-001**: Tạo, đổi tên và dùng một danh mục mới khi phân loại trong tối đa 3 thao tác, không cần sửa mã.
- **SC-002**: Với mọi danh mục, tổng hiển thị bằng đúng tổng các dòng liệt kê (đối chiếu khớp 100% trên bộ dữ liệu giả); mỗi giao dịch đếm một lần ở danh mục cha.
- **SC-003**: Từ một số tổng bất kỳ mở được dòng sao kê nguồn trong tối đa 2 thao tác.
- **SC-004**: 0 thay đổi ở snapshot, báo cáo và công nợ đã có sau khi chuyển danh mục cố định sang cây (đối chiếu số trước/sau và checksum dữ liệu vận hành).
- **SC-005**: Danh mục rỗng luôn hiển thị trạng thái thiếu dữ liệu, không bao giờ hiển thị 0 như đã đối soát.

## Assumptions
- Danh mục cổ phiếu và Shop vẫn pending (R24, R28): không tạo sẵn.
- Đối tượng tài sản đầy đủ (vốn, định giá) thuộc spec 007; ở đây danh mục con của "Đầu tư BĐS" chỉ là đối tượng chọn được khi phân loại (R55).
- Lưu trữ thay cho xóa vì mọi danh mục đã có giao dịch phải giữ lịch sử.
- Báo cáo đợt (R46) tiếp tục đếm mỗi giao dịch ở nhóm trực tiếp; tổng gộp cây nhiều cấp chỉ hiện ở màn danh mục.
