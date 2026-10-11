# Implementation Plan: Hoàn chi tiêu

**Branch**: `010-expense-refund` | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

## Summary
Cho phép phân loại tiền vào là `expense` (hoàn chi) bằng cách bỏ ràng buộc chiều tiền cho loại Chi tiêu ở `classify` (giữ ràng buộc Thu nhập chỉ cho tiền vào). Dữ liệu không đổi: allocation vẫn `{category:'expense', amount, profile?, node?}`, chiều quyết định bởi dấu của giao dịch nguồn, nên `report()`, snapshot, `loan_cash_report` (đã có nhánh `expense_refunds`) và tổng danh mục (spec 008, đã tách `in/out`) tự đúng. Việc chính là hiển thị: nhãn "Hoàn chi tiêu", chi / hoàn chi / chi ròng ở báo cáo duyệt, màn Danh mục, lịch sử danh mục; thêm trường dẫn xuất `net_spend` cho nhánh Chi tiêu ở backend.

## Technical Context
**Language/Version**: Python 3.13 stdlib + JS thuần · **Storage**: không đổi schema · **Testing**: `tests/test_p12_acceptance.py`, `node tests/js/expense_refund.test.cjs` (hàm nhãn/chi ròng), PO dùng thử UI · **Constraints**: Decimal ở backend, BigInt ở UI cho chi ròng; không đụng `outputs/p01-user-trial`; snapshot/báo cáo cũ nguyên trạng; chỉ `git add` đường dẫn cụ thể; quy trình PR (nhánh → PR → merge).

## Constitution Check
| Nguyên tắc | Đánh giá |
|---|---|
| I Dữ liệu người dùng | Đạt — thử trên bộ giả; SHA256 trước/sau |
| II Không tự quyết số liệu | Đạt — người dùng tự chọn hoàn chi; không tự ghép khoản hoàn với khoản chi |
| III Decimal | Đạt — `net_spend` bằng Decimal; UI dùng BigInt |
| IV Lịch sử bất biến | Đạt — không sửa snapshot; phân loại lại tiền vào đi qua luồng điều chỉnh có sẵn |
| V Bằng chứng | Test + PO dùng thử + hồi quy |
| VI Gọn | Sửa một điều kiện ở backend + thêm trường dẫn xuất; phần còn lại là hiển thị |

## Project Structure
```text
specs/010-expense-refund/{spec,plan,research,data-model,quickstart,tasks}.md, contracts/api.md
src/pcms/p01.py          # classify: bỏ chặn expense với tiền vào; build P12
src/pcms/categories.py   # totals thêm net_spend (nhánh expense); category_history trả root + net_spend
src/pcms/web/p01.js      # nhãn catLabel, hộp thoại, bảng, báo cáo duyệt, snapshot, màn Danh mục, lịch sử
tests/test_p12_acceptance.py, tests/js/expense_refund.test.cjs, cập nhật test cũ nếu khẳng định chặn
```
