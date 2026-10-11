# Implementation Plan: Bất động sản bản đầu

**Branch**: `011-realty` | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

## Summary
Mô-đun `realty.py` (mixin `Realty`) thêm sổ phụ cho BĐS lưu trong `state['realty']` (giá trị hiện tại, liên kết thế chấp, khoản góp vốn — append-only, hủy có lý do) và các dẫn xuất chỉ-đọc: vốn/chi phí tính từ phần phân loại có sẵn (Đầu tư BĐS và Chi tiêu gắn hồ sơ BĐS), lịch sử truy nguyên theo BĐS, dư gốc khoản vay thế chấp lấy từ `debt_register`. UI: màn "Bất động sản" với thẻ từng BĐS (vốn cạnh giá trị hiện tại, chênh lệch có nhãn, thế chấp, góp vốn), các hộp thoại ghi nhận và lịch sử. Không đổi phân loại, snapshot, công nợ.

## Technical Context
**Language/Version**: Python 3.13 stdlib + JS thuần · **Storage**: khóa mới `state['realty']` tạo bằng `setdefault` (không đổi schema bắt buộc) · **Testing**: `tests/test_p13_acceptance.py`, PO dùng thử UI · **Constraints**: Decimal ở backend; VND nguyên dương; không đụng `outputs/p01-user-trial`; gate UI theo capability `realty`; quy trình nhánh → PR → merge; chỉ `git add` đường dẫn cụ thể.

## Constitution Check
| Nguyên tắc | Đánh giá |
|---|---|
| I Dữ liệu người dùng | Đạt — thử trên bộ giả; SHA256 trước/sau |
| II Không tự quyết số liệu | Đạt — giá trị, góp vốn do Thạch nhập; không suy quyền lợi/tỷ lệ; chênh lệch có nhãn, không gọi lãi/lỗ; không trừ nợ |
| III Decimal | Đạt — tổng/chênh lệch bằng Decimal ở backend |
| IV Lịch sử bất biến | Đạt — chỉ thêm, hủy có lý do |
| V Bằng chứng | Test + PO dùng thử + hồi quy |
| VI Gọn | Một mô-đun mới, sửa tối thiểu `p01.py`/`server.py`/`p01.js` |

## Project Structure
```text
specs/011-realty/{spec,plan,research,data-model,quickstart,tasks}.md, contracts/api.md
src/pcms/realty.py          # mới: Realty mixin (change_realty, realty_view, realty_history)
src/pcms/p01.py             # mixin, dispatch realty-*, view['realty'], capability realty
src/pcms/server.py          # /api/realty-history
src/pcms/web/p01.html,p01.js
tests/test_p13_acceptance.py
```
