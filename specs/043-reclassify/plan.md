# Plan — 043 Sửa phân loại giao dịch
Thực hiện thủ công theo mẫu Spec Kit (không chạy slash command). Chi tiết quyết định: [research.md](research.md); dữ liệu: [data-model.md](data-model.md); kiểm chứng: [quickstart.md](quickstart.md).
- Mixin mới `src/pcms/reclassify.py`: `reclass_signature/level`, `reclass_reference_blocks`, `reclassify_preview`, `change_reclassify` (`transaction-reclassify`), legacy row edit. Nối vào `P01Store`, `change`, `server.py` (`/api/reclassify-preview`).
- `p01.py classify`: khi sửa phân loại đã có, mức B cần `business_ack`; tham chiếu nghiệp vụ chặn (dùng chung hàm R3).
- `categories.py`: `category-correct-classification` (042) đi qua chức năng chung.
- `web/p01.js`: hộp "Sửa phân loại", nút trên dòng lịch sử, màn phân loại, mục Cần đối chiếu.
- Test `tests/test_p45_reclassify.py`; sửa test cũ chỉ khi hợp đồng đổi (B cần xác nhận).
Constitution: I/II (dữ liệu thật không đụng, chỉ dữ liệu giả), III Decimal, IV lịch sử/snapshot bất biến, V bằng chứng, VII danh mục–đối tượng, VIII tư vấn kế toán trong spec, IX bản đồ tác động + một lượt hỏi. PASS.
