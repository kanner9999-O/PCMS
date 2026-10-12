# Implementation Plan: Quản lý khoản vay và danh mục (016)

**Spec**: [spec.md](spec.md) · **Branch**: `016-loan-category-management`
**Ngôn ngữ/ràng buộc**: Python 3.13 stdlib + JS thuần như các đợt trước; Decimal; sự kiện/sao lưu cũ; không đụng `outputs/p01-user-trial`.

## Constitution Check
Không đổi quy tắc tiền, không bù trừ, snapshot bất biến (không viết lại), mọi thay đổi có lý do và lịch sử, đọc không ghi, thử trên dữ liệu giả. Đạt.

## Cấu trúc (file chạm tới)
- `src/pcms/categories.py`: `cat_eff`, `cat_parts` dùng hiệu lực, `loan_options`, hành động `loan-regroup`, `category-delete`, chặn lưu trữ, `deletable`/`loans`/`deleted` trong `category_view`, gom nhóm mới trong `classification_review`.
- `src/pcms/p01.py`: dispatch `loan-regroup`/`category-delete`, chặn đối tượng ở loại không phép, `view()` thêm `loan_options`, build `P18-…`, capability `loan-category`.
- `src/pcms/web/p01.js`: ô chọn người → khoản vay (và BĐS), bỏ chữ loại hồ sơ, tạo nhanh khoản vay theo người, nút "Chuyển danh mục" ở khoản vay, nút "Xóa" ở danh mục, nhãn dòng ở màn Kiểm tra.
- Test: `tests/test_p18_acceptance.py`, `tests/js/loan_label.test.cjs`.

## Giai đoạn
0 Research → 1 Data model/contracts/quickstart → 2 Backend → 3 UI → 4 nghiệm thu, PR.
