# Plan — Spec 042

Trạng thái: hoàn thiện code + test, **chờ PO nghiệm thu**. Tài liệu này tạo/cập nhật trực tiếp theo cấu trúc Spec Kit; **không chạy slash command** `/speckit-*` trong đợt hoàn thiện (22/10, Claude).

## Kỹ thuật
Python 3.13 stdlib, nhật ký sự kiện bất biến, giao diện `p01.js`. Không thêm trường lưu mới ngoài: `legacy_batches[].account` (+ `account_history`), trạng thái định danh tính động (không lưu).

## Cách làm
1. **R191** — Tổng/lịch sử đối tượng theo danh mục phân bổ chính xác (`cat_target` của phần đã qua `cat_eff`). `classification_issues` liệt kê phần mà đối tượng (người sở hữu khoản vay) không là thành viên; hai lối thoát do người dùng chọn: `category-object-add` (không đổi tiền) hoặc `category-correct-classification` (qua `classify`, giữ guard phiên điều chỉnh). `classification_preview` mô phỏng đúng kết quả: chặn khác loại gốc, chặn đích mà đối tượng không là thành viên, chặn khoản vay có nhóm riêng (vì `cat_eff` sẽ ghi đè node), chặn giao dịch tách nhiều phần.
2. **R192 bank** — `check_batch`: định danh tài khoản + mã đầy đủ chuẩn hóa; chặn mã lặp trong cùng file; cùng mã khác nội dung là xung đột; xung đột với lịch sử cũ đã có tài khoản bị chặn; file trùng hash giữ cách cũ (không ghi thêm).
3. **R192/R193 lịch sử cũ** — nhập mới bắt buộc tài khoản; trạng thái động `ACTIVE / DUPLICATE / MATCHED_BANK / CONFLICT / UNRESOLVED(_MATCH)`; dòng trùng sao kê được lưu làm chứng từ, không cộng tiền; thiếu mã thì không nhập; mã gần trùng (khác hậu tố) phải đối chiếu. Dữ liệu cũ thiếu tài khoản: giữ cách tính tạm như trước (`UNRESOLVED_MATCH` theo mã gốc) và gắn nhãn "tạm tính"; `legacy-account-preview` mô phỏng chính xác thay đổi, **chặn** nếu làm đổi cách tính của lần migrate khác (không tự chuyển tiền giữa đối tượng).
4. **R194** — nguồn, bản dán gốc, snapshot bất biến; sàn chưa có importer sao kê.

## Constitution Check
I/II: không đụng `outputs/p01-user-trial`, `private-data/`; chỉ đọc bản sao để đối chiếu; mọi thay đổi dữ liệu thật là thao tác người dùng. III: Decimal. IV: điều chỉnh qua `classify` có lịch sử, `account_history`, snapshot không đổi. V: 388 test + QA giả. VII/VIII/IX: bản đồ tác động, tư vấn kế toán, kiểm tra đồng nhất giữa màn (test `assert_screens_consistent`). PASS; gate còn lại: PO nghiệm thu.
