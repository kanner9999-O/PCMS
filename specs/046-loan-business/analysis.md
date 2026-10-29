# Specification Analysis Report — spec 046

Lần chạy `/speckit-analyze` ngày 28/10/2026, sau `/speckit-tasks`.

- Đầu vào: `spec.md`, `plan.md`, `tasks.md`, `research.md`, `data-model.md`, `contracts/actions.md`, `.specify/memory/constitution.md` (v1.3.0).
- Lệnh chuẩn bị: `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks`, trả về FEATURE_DIR `specs/046-loan-business` và AVAILABLE_DOCS gồm research, data-model, contracts, quickstart, tasks.

Bước analyze chỉ đọc, không sửa file. Các sửa đổi được làm sau đó và ghi ở mục "Xử lý sau analyze".

## Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Constitution | CRITICAL | tasks.md T030 (Phase 9); constitution IX.3 và "Quy trình phát triển" mục 1 | Cập nhật PRODUCT-SPEC/ACCEPTANCE (R203–R212, A64, R186 thay một phần) đang xếp **cuối**, trong khi constitution bắt buộc làm **trước** khi sửa mã. | Đưa việc cập nhật tài liệu lõi lên Phase 1 (trước mọi task mã). IMPLEMENTATION-STATUS vẫn để cuối. |
| U1 | Underspecification | HIGH | research.md D6; spec FR-005 ("gỡ thành viên"); tasks T015 | Dấu vân tay tính trên `cat_parts`, mà gỡ thành viên (`category-object-remove`) **không đổi phần tiền**. Vì vậy bất biến chung không bắt được việc gỡ Kết khỏi Hot Debt khi Kết còn chi tiết đã ghi hoặc còn khoản vay tạo ở đó, và đường này sẽ lọt. | Thêm vào dấu vân tay **quan hệ thành viên** của các cặp (danh mục, người) đang có trong bản đã ghi, nháp và khoản vay. Ghi rõ điều này trong D6 và T006, và có test ở T015. |
| U2 | Underspecification | MEDIUM | spec FR-002 (lưu trữ giữ chi tiết); tasks T007 | Chưa có test nào chứng minh lưu trữ danh mục nghiệp vụ vẫn giữ chi tiết đã ghi, và chi tiết đó vẫn được tính vào sổ. | Thêm ca này vào T007. |
| G1 | Coverage gap | MEDIUM | plan Performance Goals; tasks T031 | Mục tiêu "chậm thêm ≤ 20%" chưa có task đo. | Thêm bước đo `view()` P48 và P49 trên bản sao vào T031. |
| U3 | Underspecification | MEDIUM | spec luồng 4 ("Ghi từ giao dịch nguồn"); contracts | Chưa nói backend cung cấp danh sách nguồn ứng viên cho một khoản bằng cách nào. | Lấy từ `loan_book.sources`, lọc theo người và chiều của khoản. Ghi điều này trong contracts và đưa vào T025. |
| I1 | Inconsistency | LOW | data-model (rate ≤ 100000) và spec FR-003 (≥ 0) | Data-model có trần 100000; spec không nói. | Coi là giới hạn kỹ thuật chặn nhập sai, không phải quy tắc nghiệp vụ. Ghi vào Assumptions của spec. |
| A1 | Ambiguity | LOW | spec Assumptions ("ngày xem mặc định hôm nay") | Với khoản đã hoàn tất, chưa rõ "tới ngày xem" tính đến đâu. | Không đổi kết quả: dư gốc bằng 0 thì cơ sở bằng 0, nên lãi không tăng. Không cần sửa. |
| D1 | Duplication | LOW | spec FR-010 và Clarifications (chặn trả vượt) | Cùng một quy tắc được nêu ở hai chỗ. | Giữ cả hai: Clarifications ghi nguồn gốc quyết định, FR là yêu cầu kiểm được. |

## Coverage Summary

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| FR-001 gắn nghiệp vụ, kế thừa, xem trước | ✓ | T005, T007, T008, T011, T012 | |
| FR-002 gỡ, đổi cha, lưu trữ, xóa | ✓ | T006, T007, T009, T010 | U2 |
| FR-003 khoản vay | ✓ | T013, T014 | |
| FR-004 chi tiết, nháp, phiên bản | ✓ | T015, T016, T018, T019 | |
| FR-005 trạng thái, chặn đường song song, chỉ Người | ✓ | T006, T015, T017 | U1 |
| FR-006 lãi theo ngày, làm tròn | ✓ | T003, T004 | |
| FR-007 xem trước tất toán, lối vào từ khoản | ✓ | T016, T020, T028 | U3 |
| FR-008 miễn giảm | ✓ | T020, T021 | |
| FR-009 hoàn tất | ✓ | T020, T021 | |
| FR-010 chặn trả vượt | ✓ | T020, T021 | |
| FR-011 môi giới | ✓ | T022, T023 | |
| FR-012 một sổ | ✓ | T024, T025, T026 | |
| FR-013 báo cáo, đếm | ✓ | T024, T025, T028 | |
| FR-014 chưa đầy đủ, không chặn duyệt | ✓ | T024, T028 | |
| FR-015 không đổi nguồn/snapshot | ✓ | T024, T031 | |
| FR-016 BĐS và nghiệp vụ cặp vẫn tạm dừng | ✓ | T030 (tài liệu), test hồi quy spec 041 có sẵn | |
| SC-001 … SC-006 | ✓ | T003, T020, T024, T015, T031, T032 | SC-006 là QA giao diện (T032) |

## Constitution Alignment Issues

- **C1 (CRITICAL)**: IX.3 "Cập nhật tài liệu lõi trước". Phải xử lý trước implement.
- Các nguyên tắc I–VIII không có xung đột. Spec có mục Tư vấn kế toán (VIII), Bản đồ ảnh hưởng (IX.1), quy tắc cũ bị thay (IX.3).

## Unmapped Tasks

Không có. T001 và T002 là setup; T029–T033 là polish/bằng chứng.

## Metrics

- Total Requirements: 16 FR + 6 SC = 22
- Total Tasks: 33
- Coverage: 100% (yêu cầu có ít nhất 1 task)
- Ambiguity Count: 1
- Duplication Count: 1
- Critical Issues Count: 1

## Next Actions

1. Xử lý C1 và U1 trước `/speckit-implement`, vì một lỗi là CRITICAL, một lỗi là HIGH.
2. Xử lý U2, G1, U3, I1 bằng cách sửa tasks/research/contracts/spec. Không cần chạy lại specify hay plan.

## Xử lý sau analyze (28/10/2026)

Đây là bước sửa của người triển khai, không phải output của analyze. Brief yêu cầu tự hoàn thiện nên các sửa dưới đây đã được áp dụng:

- **C1**: tách T030 thành:
  - **T000**, đặt ở Phase 1: PRODUCT-SPEC R203–R212, R186 thay một phần, ghi các R cũ bị thay thế; ACCEPTANCE A64;
  - **T030**, để cuối: chỉ còn IMPLEMENTATION-STATUS P49.
- **U1**: research D6 và T006 thêm thành phần thứ tư của dấu vân tay: quan hệ thành viên ACTIVE của mọi cặp (danh mục, người) có trong bản đã ghi, nháp hoặc khoản vay. T015 thêm test gỡ thành viên.
- **U2**: T007 thêm ca lưu trữ danh mục nghiệp vụ vẫn tính chi tiết đã ghi.
- **G1**: T031 thêm bước đo thời gian `view()`.
- **U3**: contracts ghi rằng `loan_book.sources` là nguồn của danh sách "Ghi từ giao dịch nguồn".
- **I1**: Assumptions của spec ghi trần 100.000 đ/triệu/ngày là giới hạn chặn nhập sai.


## Chạy lại `/speckit-analyze` — vòng sửa theo PO review 28/10 (29/10/2026)

Đã chạy thật bộ lệnh đang cài (`.specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks` → FEATURE_DIR `specs/046-loan-business`; không có `.specify/extensions.yml` nên không có hook). Phạm vi: Phase 10 (T034–T041), FR-003/004/005 sửa đổi. Kết quả của analyze (chỉ đọc):

| ID | Loại | Mức | Vị trí | Phát hiện | Đề xuất |
|---|---|---|---|---|---|
| R1 | Hiến chương IX | HIGH | spec.md, Bản đồ ảnh hưởng | Chưa phản ánh trường khoản vay mới trên phần phân loại và các đường ghi/màn bị ảnh hưởng | Bổ sung bản đồ ảnh hưởng cho vòng sửa |
| R2 | Không nhất quán | MEDIUM | tasks.md T013 | Còn "sửa mức lãi cho ra số lãi mới", trái FR-003 mới | Ghi chú thay bởi T037 |
| R3 | Độ phủ | MEDIUM | spec.md SC | Chưa có tiêu chí đo được cho P1/P2 | Thêm SC-007, SC-008 |
| R4 | Thiếu đặc tả | LOW | data-model.md | Mã chờ cho khoản đã chọn bị lệch chưa đặt tên | Thêm LOAN_MISMATCH |
| R5 | Văn phong | LOW | spec.md US3 3b/3c | Đánh số không liền | Giữ để truy vết |

Độ phủ: FR-003 → T036, T037, T040; FR-004 → T038; FR-005 → T038–T040; T034 test đỏ; T035 tài liệu; T041 bằng chứng. 0 CRITICAL, 1 HIGH, 0 mơ hồ, 0 trùng lặp. Hiến chương: I, II, IV, VIII đạt. IX: quyết định P2 do Thạch đã chốt trong brief nên không phỏng vấn lại.

**Xử lý sau analyze (người triển khai, không phải output của analyze)**: R1 bổ sung mục "Bổ sung bản đồ ảnh hưởng — vòng sửa 29/10" trong spec.md; R2 sửa tasks.md T013; R3 thêm SC-007/SC-008; R4 thêm LOAN_MISMATCH vào data-model.md. R5 giữ nguyên.
