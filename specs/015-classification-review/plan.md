# Implementation Plan: Màn Kiểm tra phân loại

**Branch**: `015-classification-review` | **Date**: 2026-10-12 | **Spec**: [spec.md](spec.md)

## Summary
Thêm `classification_review({account, scope, start, end})` vào `categories.py` (tái dùng `cat_parts/cat_keys/cat_path/root_key` và logic kiểm khớp của `category_review`): gom phần phân loại của tài khoản thành nhóm "Danh mục" hoặc "Danh mục · Đối tượng", tính số giao dịch và tổng vào/ra/chi ròng từng nhóm, liệt kê **mọi** dòng giao dịch kiểu sao kê, sắp theo thời điểm phân loại mới nhất (lấy từ `classification_history[-1].at`), cùng tóm tắt và kiểm khớp. Route `POST /api/classification-review`. UI: nút "Kiểm tra phân loại" ở bước Phân loại mở màn chỉ xem (`checkMode`) với phạm vi (cả tài khoản mặc định / 24 giờ qua / khoảng ngày), thanh tóm tắt, các nhóm mở sẵn (`<details open>`), thu gọn/mở tất cả, nút quay lại. Không ghi dữ liệu.

## Technical Context
**Language/Version**: Python 3.13 stdlib + JS thuần · **Storage**: không đổi · **Testing**: `tests/test_p17_acceptance.py`, `tests/js/classification_check.test.cjs` (hàm nhãn dòng), PO dùng thử UI · **Constraints**: Decimal ở backend; không đổi snapshot/báo cáo; không đụng `outputs/p01-user-trial`; quy trình nhánh → PR → merge; chỉ `git add` đường dẫn cụ thể.

## Constitution Check
| Nguyên tắc | Đánh giá |
|---|---|
| I Dữ liệu người dùng | Đạt — thử trên bộ giả; SHA256 trước/sau |
| II Không tự quyết số liệu | Đạt — chỉ hiển thị phân loại đã có |
| III Decimal | Đạt — tổng bằng Decimal |
| IV Lịch sử bất biến | Đạt — chỉ đọc |
| V Bằng chứng | Test + PO dùng thử + hồi quy |
| VI Gọn | Một hàm backend, một route, một màn |

## Project Structure
```text
specs/015-classification-review/{spec,plan,research,data-model,quickstart,tasks}.md, contracts/api.md
src/pcms/categories.py   # classification_review
src/pcms/p01.py          # build P17
src/pcms/server.py       # /api/classification-review
src/pcms/web/p01.js      # nút + màn Kiểm tra phân loại
tests/test_p17_acceptance.py, tests/js/classification_check.test.cjs
```
