# Tiếp quản PCMS

Đọc `HANDOFF.md` trước. Đây là điểm bàn giao hiện hành ngày11/10/2026, trỏ tới yêu cầu, mã vận hành, dữ liệu cần bảo vệ và bằng chứng nghiệm thu.

Người dùng muốn assistant giữ vai trò PO + người dùng đại diện: tự ưu tiên theo tài liệu, giao coder khi cần, tự dùng thử/nghiệm thu. Người dùng chỉ sử dụng và phản hồi, không điều phối kỹ thuật. Không tự tạo quyết định tài chính hoặc duyệt dữ liệu thật thay người dùng.

`PRODUCT-SPEC.md` là yêu cầu, `ACCEPTANCE.md` là tiêu chí, `IMPLEMENTATION-STATUS.md` là lịch sử kết quả. Không coi đề xuất/chưa chốt trong tài liệu là xác nhận của người dùng. Bảo vệ `outputs/p01-user-trial`; chỉ kiểm thử trên bộ giả riêng.

## Spec Kit (từ 11/10/2026)

Dự án dùng Spec Kit (`specify-cli`, tích hợp `claude`). Nguyên tắc ở `.specify/memory/constitution.md`. Tính năng mới đi theo `/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement`, sau đó PO nghiệm thu bằng dữ liệu giả như trong HANDOFF.md. Spec trong `specs/` phải trích mã Rxx/Axx và không thay `PRODUCT-SPEC.md`/`ACCEPTANCE.md`.

## Quyết định cấu trúc về danh mục (từ 15/10/2026)

Mọi tính năng liên quan danh mục phải theo `.specify/memory/constitution.md` nguyên tắc VII: cây danh mục cha → con nhiều cấp; đối tượng thuộc danh mục; giao diện chọn theo cấp và chỉ tải đối tượng của danh mục đã chọn; nghiệp vụ riêng là lớp song song tích hợp sau.

## Nghiệp vụ kế toán là chuẩn (từ 15/10/2026)

Thạch không am hiểu kế toán và muốn vận hành đúng nghiệp vụ kế toán. Mọi quyết định business logic phải kèm tư vấn kế toán (phương án đúng kế toán làm đề xuất, nêu lý do và hệ quả); mỗi spec có business logic có mục "Tư vấn kế toán"; vấn đề thuế/pháp lý đánh dấu cần kế toán viên xác nhận. Chi tiết: `.specify/memory/constitution.md` nguyên tắc VIII.
