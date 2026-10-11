# Implementation Plan: Quản lý danh mục và lịch sử từng danh mục

**Branch**: `008-category-management` | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

## Summary
Thêm cây danh mục: bảy gốc hệ thống cố định (khóa hiện có) + danh mục con do người dùng tạo (≤4 cấp, lưu trữ/khôi phục, lịch sử thay đổi). Phần phân loại của giao dịch nhận thêm tham chiếu `node` tùy chọn tới một danh mục con (cùng gốc với `category`). Mới: màn "Danh mục" (cây + tổng vào/ra/chênh theo cây, đếm giao dịch một lần) và lịch sử từng danh mục truy về dòng sao kê. Snapshot mới đóng băng tên/đường dẫn danh mục tại lúc duyệt. Không đổi dữ liệu và báo cáo đã có.

## Technical Context
**Language/Version**: Python 3.13 stdlib + JS thuần (như 005/006) · **Storage**: khóa mới `state['categories']` (danh sách nút) và `state['category_roots']` (mô tả gốc) tạo bằng `setdefault`; allocation thêm `node` chỉ khi có (allocation cũ giữ nguyên nên test/snapshot cũ không đổi) · **Testing**: `unittest` `tests/test_p10_acceptance.py`, `node --check`, PO dùng thử UI trên bộ giả · **Platform**: web cục bộ · **Constraints**: Decimal; không đụng `outputs/p01-user-trial`; gate UI theo capability `category-tree`; ≤200 danh mục, ≤10.000 giao dịch; 375px không tràn ngang.

## Constitution Check
| Nguyên tắc | Đánh giá |
|---|---|
| I Dữ liệu người dùng | Đạt — chỉ thử trên bộ giả; SHA256 trước/sau |
| II Không tự quyết số liệu | Đạt — chỉ tổ chức/hiển thị, không số liệu mới |
| III Decimal | Đạt — tổng tính ở backend bằng Decimal |
| IV Lịch sử bất biến | Đạt — chỉ thêm; lưu trữ thay xóa; snapshot đóng băng tên |
| V Bằng chứng | Có test + PO dùng thử + hồi quy |
| VI Gọn | Một mô-đun mới `categories.py`, sửa tối thiểu nơi khác |

## Project Structure
```text
specs/008-category-management/{spec,plan,research,data-model,quickstart,tasks}.md, contracts/api.md
src/pcms/categories.py          # mới: mixin Categories (change_category, category_view, category_history)
src/pcms/p01.py                 # mixin, dispatch category-*, classify nhận node, snapshot đóng băng cây, view['categories'], capability
src/pcms/server.py              # /api/category-history
src/pcms/web/p01.html,p01.js    # nút Danh mục, màn cây + lịch sử, chọn danh mục con khi phân loại
tests/test_p10_acceptance.py
```
**Structure Decision**: mixin như `TrxEnergy`; không đổi `report()` (báo cáo đợt tiếp tục đếm theo khóa gốc, R46).
