# Tasks — Spec 042
- [x] T01 Specify/clarify/plan và bản đồ tác động; PO đồng ý plan (Codex).
- [x] T02 Tổng/lịch sử theo danh mục phân bổ; cảnh báo; xem trước điều chỉnh khớp kết quả; lối "thêm đối tượng vào danh mục"; chặn khác loại gốc/khoản vay có nhóm/tách phần (`categories.py`).
- [x] T03 Bank identity: tài khoản + mã đầy đủ, mã lặp trong file, xung đột nội dung, xung đột lịch sử cũ (`p01.py check_batch`).
- [x] T04 Lịch sử cũ: tài khoản bắt buộc, trạng thái định danh, lưu dòng trùng sao kê làm chứng từ, gần trùng hậu tố, xác định tài khoản có xem trước chính xác và chặn ảnh hưởng lần migrate khác; UI "Cần đối chiếu", nhãn "tạm tính" (`legacy_import.py`, `p01.js`, `server.py`).
- [x] T05 Tests dữ liệu giả (`tests/test_p44_identity.py` 11 ca + cập nhật fixture P29/P31/P33/P36/P37/P38/P40) và đối chiếu bản sao dữ liệu thật.
- [x] T05b Sửa hai lỗi P1 của PO review 22/10 + test hồi quy (`test_p44_identity.py` thêm 8 ca).
- [x] T05c Sửa lỗi gần trùng/lặp trong cùng file sao kê và cùng lần dán (PO review vòng 2) + test import/publish.
- [ ] T06 PO (Codex) nghiệm thu UI trên QA `http://localhost:8803`; chưa merge/phát hành.
