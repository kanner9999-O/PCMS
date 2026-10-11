# Implementation Plan: Hoàn thiện hành trình công nợ

**Branch**: `005-debt-journey-polish` | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

## Summary

Bốn cải thiện hiển thị trên màn Công nợ và báo cáo dòng tiền khoản vay: (1) kỳ mặc định và cảnh báo "chưa có nguồn" của báo cáo; (2) khối tổng quan công nợ ở đầu màn; (3) gợi ý việc kế tiếp cho khoản hết gốc chưa tất toán được và bỏ nhãn trạng thái lặp; (4) liên kết giữa màn tài khoản và công nợ. Cách làm: chủ yếu ở UI (`p01.js`), cộng một trường dẫn xuất chỉ-đọc `completion_blocker` trong `debt_register` tái dùng đúng kiểm tra `closure_preview`. Không thêm hành động ghi, không đổi tính tiền.

## Technical Context

**Language/Version**: Python 3.13 (backend, stdlib), JavaScript thuần trong `src/pcms/web/p01.js` (không framework, không bước build)
**Primary Dependencies**: không có; `pyproject.toml` không khai báo thư viện ngoài
**Storage**: dữ liệu sự kiện JSON + snapshot trong thư mục `--data`; **không thay đổi lược đồ lưu trữ** ở đợt này
**Testing**: `unittest` (`PYTHONPATH=src:tests python3 -m unittest test_pXX_acceptance`); `node --check src/pcms/web/p01.js`; PO duyệt UI bằng bộ giả `seed()` của `tests/test_p07_acceptance.py`
**Target Platform**: máy cá nhân macOS, trình duyệt, server `python3 -m pcms serve --p01`
**Project Type**: ứng dụng web cục bộ một người dùng
**Performance Goals**: không đổi; dữ liệu vài trăm giao dịch
**Constraints**: số tiền dùng Decimal; không đụng `outputs/p01-user-trial`; gate tính năng UI theo `view.capabilities`; kết quả báo cáo/snapshot cũ phải y hệt
**Scale/Scope**: 1 màn (Công nợ), 1 hộp thoại (báo cáo dòng tiền), 1 điểm vào ở màn tài khoản

## Constitution Check

| Nguyên tắc | Đánh giá |
|---|---|
| I. Bảo vệ dữ liệu người dùng | Đạt — chỉ test trên bộ giả (`/tmp/pcms-claude-qa`, cổng 8801); đối chiếu SHA256 trước/sau phát hành |
| II. Không tự quyết định số liệu tài chính | Đạt — không tự tất toán/duyệt; chỉ hiển thị lý do |
| III. Decimal | Đạt — tổng cộng bằng `Decimal` ở backend hoặc cộng chuỗi qua `fmt` đã có; không dùng Number để cộng tiền (xem research R2) |
| IV. Lịch sử bất biến | Đạt — không ghi sự kiện mới |
| V. Bằng chứng | Có kế hoạch: test backend + PO dùng thử UI + hồi quy P04–P07 (xem quickstart) |
| VI. Gọn | Đạt — một đợt nhỏ, không tạo module mới |

Không có vi phạm cần biện minh.

## Project Structure

### Documentation (this feature)

```text
specs/005-debt-journey-polish/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/ui-and-state.md
├── checklists/requirements.md
└── tasks.md            # do /speckit-tasks tạo
```

### Source Code (repository root)

```text
src/pcms/p01.py                  # thêm completion_blocker + debt_summary vào debt_register (chỉ đọc)
src/pcms/loan_completion.py      # thêm completion_blocker(s, profile) tái dùng closure_preview
src/pcms/web/p01.js              # tổng quan đầu màn, gợi ý khoản, kỳ mặc định, liên kết
tests/test_p08_acceptance.py     # test mới (tên theo quy ước test_pXX)
```

**Structure Decision**: giữ cấu trúc hiện có; không tách mô-đun mới. Tổng hợp số tiền làm ở backend (`debt_summary`) để dùng Decimal chung với phần còn lại, UI chỉ hiển thị.

## Complexity Tracking

Không có.
