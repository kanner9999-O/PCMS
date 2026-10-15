# Implementation Plan: Nghiệp vụ gắn đối tượng trong danh mục (cho vay trước)

**Branch**: `031-loan-business-objects` | **Spec**: [spec.md](spec.md)

## Technical Context
Python 3.13 stdlib; module mới `src/pcms/business.py` (mixin `Business`) gắn vào `P01Store`; dữ liệu nằm trong `category_objects[].business` (không bảng mới) + `business_migrations`. UI trong `p01.js/css`. Test `tests/test_p33_acceptance.py`.

## Constitution Check
I/II: không đụng dữ liệu thật, hợp nhất chỉ chạy khi Thạch bấm; QA trên `/tmp/pcms-031-qa`. III: Decimal. IV: đổi loại có ngày hiệu lực + lịch sử. VII: nghiệp vụ gắn đối tượng trong danh mục, giao diện chọn theo cấp. VIII: mục Tư vấn kế toán trong spec. Pass.

## Design
- `ROLE_BY_ROOT`, `BUSINESS_TYPES={LOAN_LENT,LOAN_BORROWED,PROPERTY}` với gốc tương thích.
- Hành động: `business-set`, `business-clear`, `business-migrate` (dispatch trong `P01Store.change` theo tiền tố `business-`).
- `business_view(s)`: vai trò danh mục, sổ cho vay theo cặp (qua `cat_parts` + `cat_eff`), cảnh báo, xem trước hợp nhất.
- Chặn hẳn: hook kiểm tra vào `category-object-remove|move|merge`, `category-archive`.
- Nới `classify`: LOAN luôn nhận ở principal/interest, PROPERTY ở investment.
- UI: chip vai trò, chip nghiệp vụ, hộp thoại, panel sổ cho vay, nút hợp nhất.
