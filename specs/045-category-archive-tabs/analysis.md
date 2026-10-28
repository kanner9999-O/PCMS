# Specification Analysis Report — spec 045 (`/speckit-analyze`, 28/10/2026)

Lệnh analyze chỉ đọc; báo cáo được lưu thành file này theo yêu cầu của Thạch để PO đối chiếu. Sửa đổi sau báo cáo ghi ở mục "Đã xử lý".

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Coverage | MEDIUM | spec.md Edge Cases ("Đang xem theo kỳ"); tasks.md T009 | Ghi chú tổng phần lưu trữ khi xem theo kỳ có trong T010 nhưng chưa có test | Thêm ca theo kỳ vào T009 |
| C2 | Coverage | MEDIUM | spec.md FR-001 ("tab giữ nguyên khi đổi kỳ"), US1 kịch bản 3 | Giữ tab/ô tìm qua thao tác chỉ kiểm bằng UI (T018), không có test tự động | Chấp nhận: kiểm trong nghiệm thu UI, ghi rõ trong review |
| I1 | Inconsistency | LOW | tasks.md T001; plan.md | R202/A63 đã ghi ở bước plan; T001 còn lại phần liên kết 044 | Tick khi xong liên kết 044 |
| I2 | Inconsistency | LOW | constitution "Quy trình phát triển" bước 3 | README/HANDOFF/manifest: README trong thư mục vận hành có thay đổi dở của người dùng; HANDOFF cũ (P07) | Không sửa README; ghi là còn lệch |
| A1 | Ambiguity | LOW | spec.md FR-003 "số liệu" | Chưa nói số liệu theo kỳ hay toàn bộ | Theo kỳ đang chọn, như tab hoạt động (đã nêu ở Edge Cases) |
| U1 | Underspecification | LOW | spec.md FR-004; tasks.md T015 | Bộ chọn phẳng (đường dẫn) không cần đổi — chỉ ghi trong plan | Giữ; T015 chỉ đổi 2 bộ chọn theo cấp |

**Coverage Summary**

| Requirement | Has Task? | Task IDs | Notes |
|---|---|---|---|
| FR-001 tab | ✅ | T011 | UI; giữ tab kiểm ở T018 |
| FR-002 ghi chú tổng | ✅ | T009, T010, T011 | |
| FR-003 tab lưu trữ | ✅ | T012, T013, T014 | |
| FR-004 không dây chuyền, không mất đường | ✅ | T012, T011, T015 | |
| FR-005 không chọn danh mục lưu trữ | ✅ | T012 | quy tắc sẵn có, thêm test |
| FR-006 dấu vết xóa đối tượng | ✅ | T004, T005, T006 | |
| FR-007 thông báo | ✅ | T007, T008 | |
| FR-008 không đổi tiền/dữ liệu | ✅ | T009, T017 | |
| SC-001…SC-006 | ✅ | T004–T018 | SC-006 kiểm UI ở T018 |

**Constitution Alignment Issues:** không có (I–IX đều có mục; VIII có Tư vấn kế toán).
**Unmapped Tasks:** không (T003, T016–T019 là kiểm chứng/phát hành).
**Metrics:** 8 FR + 6 SC · 19 task · độ phủ 100% · mơ hồ 1 (LOW) · trùng lặp 0 · CRITICAL 0.

**Next Actions:** không có CRITICAL → được chạy `/speckit-implement`. PO áp dụng C1, A1 trước khi implement.

## Đã xử lý (sau báo cáo)
- C1: thêm ca "xem theo kỳ" vào T009.
- A1: FR-003 ghi rõ số liệu theo kỳ đang chọn.
- C2, I2: ghi nhận, kiểm/ghi trong review.
