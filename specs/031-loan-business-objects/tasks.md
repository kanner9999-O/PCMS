# Tasks: 031 loan-business-objects
- [ ] T001 Tạo `src/pcms/business.py`: hằng số, `business-set|clear|migrate`, `business_view`, kiểm tra chặn.
- [ ] T002 Nối vào `P01Store`, `change()`, `view()` (khóa `business`), build `P33-2026-10-15`, capability `business-objects`.
- [ ] T003 Chặn hẳn trong `categories.py` cho remove/move/merge/archive; nới `classify` cho LOAN/PROPERTY.
- [ ] T004 UI: chip vai trò, chip nghiệp vụ, hộp thoại gắn, panel sổ cho vay, nút hợp nhất xem trước.
- [ ] T005 Test `tests/test_p33_acceptance.py` (US1–US4, SC-001..003) trên dữ liệu giả.
- [ ] T006 Cập nhật PRODUCT-SPEC (R146–R153), IMPLEMENTATION-STATUS, specs/README, handoff.
- [ ] T007 QA trình duyệt trên `/tmp/pcms-031-qa`, kiểm checksum `outputs/p01-user-trial`, PR.
