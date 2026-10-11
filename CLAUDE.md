# Tiếp quản PCMS

Đọc `HANDOFF.md` trước. Đây là điểm bàn giao hiện hành ngày11/10/2026, trỏ tới yêu cầu, mã vận hành, dữ liệu cần bảo vệ và bằng chứng nghiệm thu.

Người dùng muốn assistant giữ vai trò PO + người dùng đại diện: tự ưu tiên theo tài liệu, giao coder khi cần, tự dùng thử/nghiệm thu. Người dùng chỉ sử dụng và phản hồi, không điều phối kỹ thuật. Không tự tạo quyết định tài chính hoặc duyệt dữ liệu thật thay người dùng.

`PRODUCT-SPEC.md` là yêu cầu, `ACCEPTANCE.md` là tiêu chí, `IMPLEMENTATION-STATUS.md` là lịch sử kết quả. Không coi đề xuất/chưa chốt trong tài liệu là xác nhận của người dùng. Bảo vệ `outputs/p01-user-trial`; chỉ kiểm thử trên bộ giả riêng.

## Spec Kit (từ 11/10/2026)

Dự án dùng Spec Kit (`specify-cli`, tích hợp `claude`). Nguyên tắc ở `.specify/memory/constitution.md`. Tính năng mới đi theo `/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement`, sau đó PO nghiệm thu bằng dữ liệu giả như trong HANDOFF.md. Spec trong `specs/` phải trích mã Rxx/Axx và không thay `PRODUCT-SPEC.md`/`ACCEPTANCE.md`.
