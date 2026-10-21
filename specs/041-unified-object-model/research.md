# Research: 041 — kết quả tìm kiếm mã nguồn và quyết định (Constitution IX)

## Khái niệm bị đổi: nghiệp vụ tạm dừng; tách danh mục/đối tượng; một đường tạo đối tượng; tên người
Kết quả tìm bằng `grep` trên `src/pcms` và `src/pcms/web` (21/10/2026), đối chiếu bản sao chỉ đọc của dữ liệu thật.

### R1. Nơi nghiệp vụ xuất hiện
- Backend: `business.py` (`change_business`, `business_view`, `business_migration_rows`, `change_business_migrate`, guard `biz_guard_*`), nối vào `p01.py` (`change`, `view()['business']`), `categories.py` (`category_view` gắn `business`, `loans`, `party_name`; `change_category` gọi `biz_guard_remove/merge/archive`), `objects.py` (`object_view` dùng `business`, `issues`).
- UI `p01.js`: `bizForm`, `bizMigrateForm`, `bizPanelHtml`, wrapper `renderCategories` thêm chip/nút/khối Nghiệp vụ, `objBizName`, nhãn cảnh báo `bizIssue`, màn Đối tượng hiện nghiệp vụ và khoản vay.
- **Quyết định**: thêm cờ `business_enabled` (mặc định tắt). Tắt: `view()['business']` chỉ trả `{enabled:false}`; mọi thành phần UI ẩn khi `!view.business.enabled`; `business-set/clear` bị từ chối "nghiệp vụ tạm dừng"; guard của danh mục (`biz_guard_*`) chỉ chạy khi bật; dữ liệu `business`/`business_history` giữ nguyên. **Lý do**: Thạch chưa quyết định nghiệp vụ; không xóa mã để bật lại sau. **Phương án bị loại**: xóa mã nghiệp vụ (mất công, khó khôi phục).

### R2. Đường tạo đối tượng song song (5)
`objects.py: object-create`; `p01.py: action=='profile'` (hộp Hồ sơ liên kết); `categories.py: change_quick_object` (PERSON/PROPERTY/LOAN/CATEGORY; gọi từ phân loại và nút Thêm BĐS ở `realty-add`); `categories.py: category-object-add` với `name` (tạo loại OBJECT); `legacy_import.py: legacy-import` (tạo OBJECT). Quy tắc kiểm tra khác nhau (tên, loại, danh mục).
- **Quyết định**: một hàm `create_profile(s,name,kind,category=None)` trong `objects.py` (tên 1–100, `require_free_name`, loại ∈ {PERSON,PROPERTY,OBJECT}, tùy chọn thành viên danh mục) mà **mọi lối** gọi. `profile`: giữ cho test và tạo LOAN (cần cho sổ Công nợ), nhánh PERSON/PROPERTY gọi hàm chung. Bỏ **UI** hộp Hồ sơ liên kết. `legacy-import` nhận `type` (mặc định OBJECT khi thiếu để tương thích test; giao diện luôn gửi loại).

### R3. Nguồn số liệu trùng nhau
`debt_register` (p01.py) dùng bởi Công nợ, Tổng tài sản (`assets.py`), `loan_completion.py`, `realty.py`, `objects.py`; `business_view` tính lại riêng (ra 105.000.000 so với 0 của Công nợ). **Quyết định**: ẩn sổ nghiệp vụ (R1) loại nguồn thứ hai khỏi giao diện; sổ Công nợ là nguồn duy nhất. Khi nghiệp vụ được bật lại sau này, sổ nghiệp vụ phải đọc từ `debt_register` (ghi vào spec tương lai).

### R4. Nơi hiển thị tên khoản vay
`categories.py: classification_review` (`profiles` map → `obj`), `category_history` (nhãn), `category_view` (`objs`), `p01.js: objectOptions`, `membersOf`. **Quyết định**: hàm `disp_name(s,profile_id)` trả tên người cho hồ sơ LOAN, tên hồ sơ cho loại khác; dùng ở `classification_review`, `category_history`, `category_view` (LOAN → tên người, kind 'PERSON' nhãn Người); UI hộp phân loại tự xác định khoản vay khi chỉ có một, hiện ô chọn khi có nhiều.

### R5. Đồng bộ danh mục–đối tượng
Cấu trúc thật: 6 người, mỗi người đúng một khoản vay; 6 khoản là thành viên Gốc vay; Kết, Tươi thuộc Hot Debt (OBJECT/PERSON); BĐS: Xuân Mai ở 2 danh mục, Kỳ Sơn không danh mục. **Quyết định**: `business-migrate` (giữ tên action) khi nghiệp vụ tắt chỉ làm: thêm người vào danh mục chứa khoản vay (`ADD_ONLY`), đánh dấu thành viên khoản vay `REMOVED/MIGRATED_TO_PERSON`; không gắn loại, không xử lý BĐS. UI nhãn "Đồng bộ danh mục và đối tượng".

### R6. Kiểm tra đồng nhất giữa các màn
Cần test so: tập (người, danh mục) ở `category_view` và `object_view`; số giao dịch; nhóm ở `classification_review` và nhãn lịch sử; không còn chuỗi "Khoản " trong nhóm. Dữ liệu giả mô phỏng cấu trúc thật (người một khoản vay, khoản chưa thiết lập, khoản số dư âm).

### R7. Spec/quy tắc cũ bị ảnh hưởng
R146–R153, R156–R157, R179–R182: chuyển **Pending** trong `PRODUCT-SPEC.md`; R84–R86 và R136 giữ; spec 031/032/033/035/037/040 ghi chú "bị thay thế một phần bởi 041".

## Rủi ro
- Test cũ P33/P34/P39 kiểm nghiệp vụ: chạy với `business_enabled=True` trong `setUp`.
- Ẩn UI sai điều kiện làm hiện lẫn: kiểm bằng test dữ liệu trả về + QA trình duyệt.
