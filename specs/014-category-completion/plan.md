# Implementation Plan: Hoàn thiện Danh mục

**Branch**: `014-category-completion` | **Date**: 2026-10-12 | **Spec**: [spec.md](spec.md)

## Summary
Mở rộng mô-đun `categories.py` (spec 008): (1) **gốc tự tạo** = nút danh mục `parent=None` có `root` = loại (`income`/`expense`/`investment`), tổng riêng và không cộng vào gốc hệ thống; (2) **kỳ**: `category_view`/`category_history` nhận `start`/`end` (và `account` cho lịch sử) + route `/api/category-view`; (3) **báo cáo duyệt theo danh mục** `category_review(account)` dựng cây từng gốc (hệ thống, tự tạo, Chưa phân loại) với số giao dịch, số đối tượng, vào/ra, chi ròng và khối kiểm đối chiếu đủ/khớp + route `/api/category-review`. UI: nút "+ Gốc mới", bộ lọc kỳ, khối "Theo danh mục" trong bước xem toàn đợt. Không đổi `report()`, snapshot hay schema allocation (allocation vẫn `category`=loại + `node`).

## Technical Context
**Language/Version**: Python 3.13 stdlib + JS thuần · **Storage**: không đổi schema; nút `categories[]` cho phép `parent=None` (gốc tự tạo) · **Testing**: `tests/test_p16_acceptance.py`, `tests/js/category_period.test.cjs` (tính kỳ), PO dùng thử UI · **Constraints**: Decimal; không đổi snapshot/báo cáo cũ; không đụng `outputs/p01-user-trial`; quy trình nhánh → PR → merge; chỉ `git add` đường dẫn cụ thể.

## Constitution Check
| Nguyên tắc | Đánh giá |
|---|---|
| I Dữ liệu người dùng | Đạt — thử trên bộ giả; SHA256 trước/sau |
| II Không tự quyết số liệu | Đạt — chỉ tổ chức và hiển thị; báo cáo nêu rõ khớp/không khớp |
| III Decimal | Đạt — tổng bằng Decimal ở backend |
| IV Lịch sử bất biến | Đạt — nút không xóa; snapshot đóng băng cây gồm gốc tự tạo |
| V Bằng chứng | Test + PO dùng thử + hồi quy |
| VI Gọn | Mở rộng một mô-đun có sẵn; thêm 2 route |

## Project Structure
```text
specs/014-category-completion/{spec,plan,research,data-model,quickstart,tasks}.md, contracts/api.md
src/pcms/categories.py   # gốc tự tạo, kỳ, category_review
src/pcms/p01.py          # build P16; (snapshot đã gọi cat_path nên tự đúng)
src/pcms/server.py       # /api/category-view, /api/category-review
src/pcms/web/p01.js      # + Gốc mới, bộ lọc kỳ, khối báo cáo theo danh mục
tests/test_p16_acceptance.py, tests/js/category_period.test.cjs
```
