# Phân tích chéo spec–plan–tasks (/speckit-analyze, chỉ đọc) — 21/10/2026

| Yêu cầu | Task phủ | Ghi chú |
|---|---|---|
| FR-001 tạm dừng nghiệp vụ | T002, T003, T004 | cờ + ẩn dữ liệu trả về + ẩn UI; test T010/T011 |
| FR-002 bỏ Hồ sơ liên kết | T006 | chỉ UI; backend `profile` giữ cho Công nợ/test |
| FR-003 một hàm tạo | T001, T005, T006 | 5 lối được liệt kê ở research R2 |
| FR-004 tên người | T007, T008 | `disp_name`; ô khoản vay chỉ khi >1 |
| FR-005 đồng bộ | T009 | không gắn nghiệp vụ, không xử lý BĐS |
| FR-006 màn Đối tượng | T003, T004 | `issues` + nút đồng bộ |
| FR-007 test đồng nhất | T010, T011 | quickstart 1–5 |
| FR-008 không đổi tiền/dữ liệu thật | T013 | bản sao chỉ đọc, checksum |

Kết quả: không có lỗi nghiêm trọng. Constitution I–IX đạt (plan.md). Không còn yêu cầu không có task; không còn task không gắn yêu cầu (T012–T014 là hoàn thiện). Nhắc: spec "Assumptions" ghi Công nợ/BĐS/Tổng tài sản đóng băng (không đổi); nếu Thạch muốn ẩn chúng là quyết định riêng. Có thể triển khai.
