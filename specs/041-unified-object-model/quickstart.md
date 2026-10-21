# Quickstart: kiểm tra 041 (kịch bản chạy được)

Chuẩn bị: bộ giả trong test (`tests/test_p18_acceptance.py`: người Kết có hai khoản vay; thêm một người có khoản chưa thiết lập, một khoản số dư âm, BĐS ở hai danh mục, BĐS chưa thuộc danh mục). Không dùng `outputs/p01-user-trial`.

1. **Nghiệp vụ ẩn**: gắn sẵn nghiệp vụ (bật cờ trong test) rồi tắt cờ; `view()['business']` chỉ `{enabled:false}`; `business-set` bị từ chối; dữ liệu `business` còn trong state.
2. **Một đường tạo**: `object-create`, `category-object-add`(tên), `object-quick-create`, `legacy-import`(tên mới + `type`), `profile` đều ra đối tượng có loại và cùng quy tắc tên; tên trùng (kể cả lưu trữ) bị chặn ở mọi lối.
3. **Tên người**: `classification_review` và `category_history` không chứa nhóm/nhãn bắt đầu bằng "Khoản "; nhóm là "Gốc vay · Kết".
4. **Phân loại**: người một khoản vay → lưu gắn đúng khoản, không hỏi; người nhiều khoản → có ô chọn.
5. **Đồng bộ**: trước đồng bộ `objects.issues` có `LOAN_AS_MEMBER`/`PERSON_NOT_MEMBER`; sau `business-migrate` rỗng; hai màn cùng tập (người, danh mục) và cùng số giao dịch; báo cáo, `debt_register`, snapshot giống hệt.
6. **Giao diện** (QA trình duyệt trên bộ giả): không còn nút Hồ sơ liên kết, không còn chip/khối Nghiệp vụ; hộp Thêm đối tượng, migrate hỏi loại.
7. **Dữ liệu thật**: đối chiếu bản sao chỉ đọc; checksum `outputs/p01-user-trial` không đổi.
