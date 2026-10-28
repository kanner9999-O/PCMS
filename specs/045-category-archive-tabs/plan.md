# Implementation Plan: Tách danh mục lưu trữ và vá dấu vết xóa

**Branch**: `045-category-archive-tabs` | **Date**: 2026-10-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/045-category-archive-tabs/spec.md`

## Summary

Backend: `category_view` bổ sung cho mỗi gốc/danh mục phần tổng thuộc danh mục lưu trữ bên dưới (`archived_share`), và cho mỗi danh mục: lý do không xóa được (`delete_block`), lý do không khôi phục được (`restore_block`), thời điểm/lý do lưu trữ từ lịch sử. Xóa hẳn đối tượng (2 đường) giữ dấu vết thành viên trong `object_deleted[].memberships`; `cat_in_use_fast` đọc dấu vết này; thông báo chặn xóa viết lại theo nguyên nhân + hướng dẫn Lưu trữ. Giao diện: màn Danh mục có tab "Đang sử dụng"/"Đã lưu trữ (N)", ghi chú tổng, tìm theo tên, khôi phục/xóa có lý do; bộ chọn danh mục theo cấp không làm mất danh mục hoạt động dưới cha lưu trữ.

## Technical Context

**Language/Version**: Python 3.13 (stdlib), JavaScript thuần

**Primary Dependencies**: không

**Storage**: kho sự kiện JSON; thêm trường `memberships` vào bản ghi `object_deleted` (bản ghi mới), không đổi bản ghi cũ

**Testing**: `unittest` (`tests/test_p48_category_archive.py`), `node --test tests/js/`, thử UI dữ liệu giả

**Target Platform**: `pcms serve --p01`

**Project Type**: web-service + SPA

**Performance Goals**: dựng màn Danh mục không chậm đáng kể (đo trước/sau trên bản sao dữ liệu thật)

**Constraints**: không đổi cách tính tổng; một quy tắc xóa cho nút/lệnh/dọn; không dây chuyền lưu trữ/khôi phục; không cây thứ hai (tab lưu trữ là danh sách phẳng có đường dẫn, đọc từ cùng `nodes`)

**Scale/Scope**: `src/pcms/categories.py`, `src/pcms/objects.py`, `src/pcms/web/p01.js` (+css), test mới, tài liệu

## Nghiên cứu tác động *(bắt buộc nếu đổi nghiệp vụ/cấu trúc)*

Bản đồ ở spec. Đường xóa đối tượng tìm bằng `s['category_objects']=[` : `objects.py` (`object-delete`) và `categories.py` (`category-object-delete`) — cả hai sửa. Bộ chọn danh mục trong giao diện (tìm `status==='ACTIVE'`): `cascChildren` (phân loại, Sửa phân loại), `levelOptions` (migrate lịch sử cũ), `nodeSelect`, `objCategoryOptions`, `objMoveForm`, `catEdit`, `loanRegroup` — các bộ chọn phẳng liệt kê từng danh mục hoạt động theo đường dẫn nên không mất mục; hai bộ chọn theo cấp (`cascChildren`, `levelOptions`) cần cho đi qua cha lưu trữ còn con hoạt động. Hệ thống đã chặn chọn danh mục lưu trữ khi ghi (`classify`, `cat_target_root`, `cat_parent_ok`, xem trước Sửa phân loại).

## Constitution Check

| Nguyên tắc | Đánh giá |
|---|---|
| I, II | Đạt — không sửa dữ liệu thật; thử trên dữ liệu giả, đối chiếu bản sao chỉ đọc |
| III | Tổng phần lưu trữ tính bằng Decimal cùng vòng tính tổng hiện có |
| IV | Đạt — vá mất dấu vết khi xóa đối tượng |
| V | Test backend + UI dữ liệu giả + đối chiếu dữ liệu thật |
| VII | Đạt — giữ một cây, tab chỉ là cách hiển thị; đối tượng vẫn thuộc danh mục |
| VIII | Có Tư vấn kế toán (trình bày công bố phần khoản mục đã khóa) |
| IX | Bản đồ tác động; một lần phát hành; kiểm đồng nhất tổng tab ↔ gốc (SC-003) và nút ↔ lệnh ↔ dọn (SC-004) |
| VI | Không thêm màn mới; dùng chung dữ liệu `categories` |

Gate đạt. Đánh giá lại sau thiết kế: đạt.

## Project Structure

### Documentation (this feature)

```text
specs/045-category-archive-tabs/
├── spec.md, plan.md, research.md, data-model.md, quickstart.md
├── contracts/category-view.md
├── analysis.md   (kết quả /speckit-analyze)
├── tasks.md, review.md
```

### Source Code (repository root)

```text
src/pcms/categories.py   # category_view (archived_share, delete_block, restore_block, archived_at/reason), cat_in_use_fast, category-object-delete
src/pcms/objects.py      # object-delete giữ dấu vết; helper obj_delete_trace
src/pcms/web/p01.js|css  # tab, ghi chú tổng, danh sách lưu trữ, bộ chọn theo cấp
tests/test_p48_category_archive.py
```

**Structure Decision**: dự án hiện có.

## Complexity Tracking

Không có vi phạm.
