# Implementation Plan: Chặn xóa hẳn danh mục còn dữ liệu ngoài giao dịch ngân hàng

**Branch**: `044-category-delete-guard` | **Date**: 2026-10-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/044-category-delete-guard/spec.md`

## Summary

Mở rộng kiểm tra "danh mục đã từng dùng" (một hàm duy nhất, dùng cho cả cờ `deletable` của màn Danh mục và hành động `category-delete`) để xét thêm dòng lịch sử cũ (hiện tại + lịch sử sửa phân loại, mọi lần migrate kể cả đã hủy), lần migrate, quan hệ đối tượng thành viên (hoạt động + đã gỡ/chuyển) và lịch sử chuyển đối tượng; lý do chặn có số lượng và hướng xử lý.

## Technical Context

**Language/Version**: Python 3.13 (stdlib), JavaScript thuần (giao diện)

**Primary Dependencies**: không có (stdlib)

**Storage**: kho sự kiện JSON (`P01Store`), trạng thái `categories`, `legacy_entries`, `legacy_batches`, `category_objects`, `object_moves`

**Testing**: `unittest` (`tests/test_p47_category_delete.py` mới), `node --test tests/js/`

**Target Platform**: máy chủ cục bộ `pcms serve --p01` (:8792)

**Project Type**: web-service + SPA một trang

**Performance Goals**: màn Danh mục không chậm thêm đáng kể — số danh mục nhỏ (≤ vài chục), dòng lịch sử cũ vài trăm; quét tuyến tính mỗi danh mục chấp nhận được (đo trên bản sao dữ liệu thật)

**Constraints**: không đổi tiền/tổng/báo cáo; không gửi lệnh ghi vào dữ liệu thật; một quy tắc cho màn và lệnh

**Scale/Scope**: 1 hàm backend (`cat_in_use_fast` trong `src/pcms/categories.py`), không đổi giao diện ngoài thông báo (nút đã theo `deletable`)

## Nghiên cứu tác động *(bắt buộc nếu đổi nghiệp vụ/cấu trúc)*

Xem bảng "Bối cảnh và bản đồ tác động" trong spec và [research.md](research.md). Đường xóa song song: chỉ có `category-delete` (đã tìm `s['categories']=[` trong mã nguồn — duy nhất ở `categories.py`). Màn liên quan: Danh mục (nút "Xóa hẳn"). Không có màn khác hiển thị `deletable` của danh mục.

## Constitution Check

| Nguyên tắc | Đánh giá |
|---|---|
| I. Dữ liệu tài chính bất khả xâm phạm | Đạt — chỉ thêm điều kiện chặn; thử trên dữ liệu giả, bản sao chỉ đọc |
| II. Không tự quyết số liệu thật | Đạt — không xóa/lưu trữ danh mục thật nào |
| III. Decimal | Không áp dụng (không tính tiền) |
| IV. Lịch sử bất biến | Đạt — mục tiêu chính: không để lịch sử cũ mất khoản mục |
| V. Bằng chứng | Test từng loại tham chiếu + đối chiếu bản sao dữ liệu thật + thử UI dữ liệu giả |
| VII. Danh mục trung tâm | Đạt — không đổi cấu trúc cây/đối tượng; quan hệ thành viên được bảo vệ |
| VIII. Kế toán | Có mục "Tư vấn kế toán" trong spec (khoản mục đã phát sinh chỉ khóa, không xóa) |
| IX. Rà soát tác động, phát hành một lần | Bản đồ tác động trong spec; một lần phát hành; kiểm đồng nhất màn–lệnh (SC-003) |
| VI. Gọn | Sửa một hàm, không thêm màn |

Gate: đạt, không vi phạm. Đánh giá lại sau thiết kế: không đổi.

## Project Structure

### Documentation (this feature)

```text
specs/044-category-delete-guard/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/category-delete.md
└── tasks.md   (/speckit-tasks)
```

### Source Code (repository root)

```text
src/pcms/categories.py        # cat_in_use_fast: thêm kiểm tra + lý do có số lượng
src/pcms/p01.py               # build P47
tests/test_p47_category_delete.py
PRODUCT-SPEC.md, ACCEPTANCE.md, IMPLEMENTATION-STATUS.md
```

**Structure Decision**: dự án đơn hiện có; không thêm module.

## Complexity Tracking

Không có vi phạm cần biện minh.
