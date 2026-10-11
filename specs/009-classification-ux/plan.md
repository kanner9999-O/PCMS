# Implementation Plan: Cải thiện màn Phân loại giao dịch

**Branch**: `009-classification-ux` | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

## Summary
Ba thay đổi ở màn Phân loại: (1) lý do phân loại và lý do mở phiên điều chỉnh thành tùy chọn (backend + UI); (2) sắp xếp danh sách theo ngày / số tiền tăng / số tiền giảm (chỉ phía UI, so sánh bằng BigInt trên chuỗi VND); (3) "Tạo nhanh" đối tượng ngay trong từng dòng của hộp thoại phân loại bằng một action backend nguyên tử `object-quick-create` (khoản vay + người mới, BĐS, hoặc danh mục con) rồi tự chọn đối tượng vừa tạo. Không đổi quy tắc tiền, phân bổ, snapshot.

## Technical Context
**Language/Version**: Python 3.13 stdlib + JS thuần · **Storage**: không đổi schema; dùng lại `profiles` và `categories`, thêm bản ghi audit như hành động hiện có · **Testing**: `tests/test_p11_acceptance.py` (backend), `tests/js/classification_sort.test.cjs` (so sánh sắp xếp), PO dùng thử UI · **Constraints**: Decimal/BigInt, không đụng `outputs/p01-user-trial`, gate UI theo capability `quick-object`, chỉ `git add` đường dẫn cụ thể (có phiên khác sửa `docs/product`, `specs/008-product-map`, `README.md`).

## Constitution Check
| Nguyên tắc | Đánh giá |
|---|---|
| I Dữ liệu người dùng | Đạt — thử trên bộ giả; SHA256 trước/sau |
| II Không tự quyết số liệu | Đạt — không tự phân loại, không ghi tiền; khoản vay tạo nhanh chưa thiết lập gốc → "cần thiết lập" |
| III Decimal | Đạt — sắp xếp bằng BigInt trên chuỗi, không dùng Number để so sánh tiền |
| IV Lịch sử bất biến | Đạt — chỉ thêm; lý do rỗng vẫn ghi lịch sử trước/sau; duyệt phiên bản mới vẫn đòi lý do (R21) |
| V Bằng chứng | Có test + PO dùng thử + hồi quy |
| VI Gọn | Không mô-đun mới lớn: một hàm trong `categories.py`, sửa nhỏ `p01.py`, `p01.js` |

## Project Structure
```text
specs/009-classification-ux/{spec,plan,research,data-model,quickstart,tasks}.md, contracts/api.md
src/pcms/p01.py            # reason tùy chọn (classify, begin-adjustment); dispatch object-quick-create; capability quick-object
src/pcms/categories.py     # change_quick_object (LOAN/PROPERTY/CATEGORY, nguyên tử)
src/pcms/web/p01.js        # sắp xếp, lý do tùy chọn, tạo nhanh trong dòng, đồng bộ đối tượng theo danh mục
tests/test_p11_acceptance.py, tests/js/classification_sort.test.cjs
```
