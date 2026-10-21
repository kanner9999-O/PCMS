# Implementation Plan: Tách danh mục và đối tượng; tạm dừng nghiệp vụ; đồng nhất các màn

**Branch**: `041-unified-object-model` | **Date**: 2026-10-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/041-unified-object-model/spec.md`

## Summary
Thạch chốt: danh mục và đối tượng tách bạch; **nghiệp vụ tạm dừng** (chỉ lưu thu/chi); bỏ hộp Hồ sơ liên kết; hiển thị tên người; không sửa lắt nhắt từng màn. Cách làm: một cờ tạm dừng nghiệp vụ (mã giữ nguyên, ẩn giao diện), một hàm tạo đối tượng chung, hàm tên hiển thị chung, "đồng bộ danh mục và đối tượng" không gắn nghiệp vụ, cộng bộ test đồng nhất giữa các màn. Quyết định chi tiết ở [research.md](research.md).

## Technical Context
**Language/Version**: Python 3.13 chuẩn thư viện; JavaScript thuần (một file `p01.js`).
**Primary Dependencies**: không (stdlib).
**Storage**: nhật ký sự kiện bất biến trong thư mục dữ liệu; **không thêm trường lưu mới**.
**Testing**: `python -m unittest` (test chấp nhận P-series), test node `tests/js/*.cjs`, QA trình duyệt trên bộ giả.
**Target Platform**: máy cá nhân, máy chủ cục bộ 127.0.0.1.
**Project Type**: ứng dụng web cục bộ (backend Python + giao diện tĩnh).
**Performance Goals**: không đổi.
**Constraints**: Decimal; lịch sử bất biến; không đụng `outputs/p01-user-trial`; đọc dữ liệu thật qua bản sao chỉ đọc.
**Scale/Scope**: hàng trăm giao dịch, vài chục hồ sơ.

## Nghiên cứu tác động
Đã thực hiện: [research.md](research.md) (R1–R7), kịch bản đồng nhất ở [quickstart.md](quickstart.md). `/speckit-analyze` phải sạch lỗi nghiêm trọng trước khi triển khai.

## Constitution Check
- **I/II** dữ liệu thật bất khả xâm phạm, không tự quyết số liệu: PASS — chỉ đọc bản sao; đồng bộ cấu trúc bằng nút xác nhận của Thạch; không đổi số tiền.
- **III** Decimal: PASS — không đổi.
- **IV** lịch sử bất biến: PASS — thành viên khoản vay chuyển `REMOVED` có history; dữ liệu nghiệp vụ giữ nguyên.
- **V** bằng chứng hoàn thành: PASS — test đồng nhất giữa các màn, QA trình duyệt, đối chiếu bản sao dữ liệu thật.
- **VII** danh mục là cấu trúc trung tâm, đối tượng thuộc danh mục: PASS — tách danh mục và loại đối tượng, tên danh mục không mang nghiệp vụ.
- **VIII** nghiệp vụ kế toán: PASS — mục Tư vấn kế toán trong spec; cash basis, một nguồn số dư.
- **IX** rà soát tác động, phát hành một lần: PASS — bản đồ tác động, phỏng vấn gộp đã xong, phát hành một lần.
- **VI** gọn: PASS — dùng lại hàm và dữ liệu hiện có, không viết lại kiến trúc.

## Project Structure

### Documentation (this feature)
```text
specs/041-unified-object-model/
├── spec.md · plan.md · research.md · data-model.md · quickstart.md · tasks.md
└── checklists/requirements.md
```

### Source Code (repository root)
```text
src/pcms/
├── business.py      # cờ business_enabled; migrate chỉ đồng bộ thành viên khi tắt
├── objects.py       # create_profile, disp_name, object_view (ẩn khoản vay/nghiệp vụ khi tắt)
├── categories.py    # dùng create_profile/disp_name; guard nghiệp vụ theo cờ
├── legacy_import.py # nhận type khi tạo đối tượng mới
├── p01.py           # view(): business {enabled:false}; action profile gọi hàm chung
└── web/p01.js|html  # bỏ Hồ sơ liên kết; ẩn UI nghiệp vụ; hộp phân loại/migrate/tạo; tên người
tests/ test_p40_acceptance.py (đồng nhất giữa các màn) + sửa P33/P34/P39 chạy với cờ bật
```

**Structure Decision**: giữ cấu trúc hiện có; không thêm module mới.

## Complexity Tracking
Không có vi phạm Constitution cần biện minh.
