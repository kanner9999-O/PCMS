# Data Model: 041

Không thêm trường lưu mới; chỉ thay đổi cách đọc/ghi và một cờ cấu hình lúc chạy.

| Thực thể | Trường | Thay đổi |
|---|---|---|
| Hồ sơ (profile) | `id, kind∈{PERSON,PROPERTY,OBJECT,LOAN}, name, party, status, merged_into` | Không đổi cấu trúc. Tạo qua `create_profile` (tên 1–100, duy nhất toàn hệ thống kể cả `ARCHIVED`). LOAN không tạo từ giao diện đối tượng. |
| Thành viên danh mục (`category_objects`) | `category, profile, status, history, business, business_history` | `business*` giữ nguyên nhưng **tạm dừng**: không đọc/ghi qua giao diện. Thành viên là hồ sơ LOAN → chuyển `REMOVED` với history `MIGRATED_TO_PERSON` khi đồng bộ. |
| Cờ cấu hình | `P01Store.business_enabled` (mặc định `False`) | Tắt: `view()['business']={enabled:false}`; `business-set/clear` bị từ chối; guard danh mục bỏ qua. |
| `view()['objects']` | `rows, issues, types, counts` | Bỏ `loans` và `business` khỏi từng hàng khi tắt; `issues` còn `LOAN_AS_MEMBER` và `PERSON_NOT_MEMBER` (cảnh báo lệch + nút đồng bộ). |
| Đầu ra đọc | tên hiển thị | `disp_name(s,pid)`: LOAN → tên người; khác → tên hồ sơ. |

Quy tắc: tên đối tượng duy nhất (chuẩn hóa NFC, khoảng trắng, hoa/thường); đổi loại và lưu trữ/xóa theo spec 033 (không đổi). Không đổi Decimal, báo cáo, snapshot.
