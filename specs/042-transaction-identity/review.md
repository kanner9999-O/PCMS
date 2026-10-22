# Review — Spec 042 (cập nhật 22/10/2026, Claude) — **CHỜ PO NGHIỆM THU, CHƯA MERGE, CHƯA PHÁT HÀNH**

## 0. Hiện trạng khi tiếp quản và xử lý ngay
- Bản nháp của coder Codex nằm **chưa commit trong thư mục vận hành** `PCMS/`. Server thật `:8792` (backend P43 nạp 21/10 19:37) đọc `src/pcms/web/p01.js` từ đĩa mỗi lần tải trang ⇒ **giao diện nháp đang được phục vụ cho app thật**, gọi API mà backend đang chạy không có.
- Đã xử lý (không restart, không đụng dữ liệu): sao lưu bản nháp (`git diff` + file mới) → tạo worktree `../PCMS-042` nhánh `042-transaction-identity-impl` từ P43 và áp bản nháp vào đó → trả 7 file nháp trong `PCMS/` về HEAD P43. Kiểm chứng: SHA256 `p01.js` do `:8792` phục vụ = SHA256 `HEAD:src/pcms/web/p01.js` (`51dab7d4…`). Giữ nguyên các thay đổi cũ không thuộc đợt này (`README.md`, `specs/README.md`, `docs/product/`, `specs/008-product-map/`). Nhánh `codex/042-transaction-identity` vẫn trỏ P43 (không có mã nháp).

## 1. Đã sửa so với bản nháp
| Vấn đề trong review cũ / phát hiện mới | Xử lý |
|---|---|
| Điều chỉnh khi `loan.group` có giá trị: `cat_eff` ghi đè node mới ⇒ xem trước ≠ kết quả | `classification_preview` mô phỏng `cat_eff` trên phần mới, chặn nếu đích khác; test `test_correction_guards…` |
| Gợi ý điều chỉnh có thể chuyển **lãi sang gốc**; mọi khoản ở Lãi vay hiện là sai lệch | Chỉ cho đích **cùng loại gốc**; thêm lối "Thêm [đối tượng] vào [danh mục]" (không đổi tiền); UI gom theo (danh mục, đối tượng) |
| Xem trước xác định tài khoản với nhiều batch cùng định danh có thể khác kết quả, ngầm chọn batch đứng trước | Mô phỏng chính xác trạng thái trước/sau toàn bộ dòng; **chặn** khi làm đổi cách tính của lần migrate khác; test `test_resolution_blocked…`, `test_old_batch_without_account…` (tổng sau = xem trước) |
| Dòng trùng sao kê mới không lưu ⇒ mất truy nguyên chứng từ | Lưu `OK` + `MATCHED_BANK`; trạng thái động quyết định không cộng tiền |
| Bỏ cắt hậu tố mã có thể cộng hai lần (`FT…\BNK` vs `FT…`) | Gần trùng khác hậu tố cùng tài khoản ⇒ lỗi cần đối chiếu (nhập lịch sử và xác định tài khoản) |
| Cảnh báo tạm tính/xung đột trên các màn | Mục "Cần đối chiếu" ở Danh mục; nhãn "Lịch sử cũ · tạm tính" trong mọi lịch sử; tổng lịch sử cũ ở danh sách migrate tách `matched_bank / duplicates / conflicts / unresolved` |
| Test cũ theo hợp đồng cũ | Fixture thêm `account` (hợp đồng R193); P29 viết lại theo R192; P33 đổi kỳ vọng 4→2 **kèm** khẳng định nguồn gốc (K1 ở Gốc vay › Kết, K4 ở Lãi vay là sai lệch quan hệ) và lịch sử = tổng |
| Mã chết trong `check_batch`, hàm không dùng | Bỏ `legacy_bank_refs`, `norm_ref_c`, nhánh `'id' not in old` |

## 2. Bằng chứng kiểm thử
- `cd ../PCMS-042/tests && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../src python3 -m unittest discover -s . -p "test_*.py"` → **Ran 388 tests, OK**. Node: 9/9 `tests/js/*.cjs` OK.
- `tests/test_p44_identity.py` (11 ca mới): tái hiện ca Kết; hai lối giải quyết (thêm thành viên / điều chỉnh) với tiền, nguồn, tổng danh mục không đổi; xem trước = kết quả; chặn khác loại gốc, không thành viên, khoản vay có nhóm, tách phần; giao dịch đã duyệt cần phiên điều chỉnh, snapshot không đổi; nhập lặp nguyên file không thêm giao dịch; mã lặp trong file; cùng mã khác nội dung; cùng mã khác tài khoản giữ riêng; lịch sử trùng xuyên đối tượng; lịch sử khác tài khoản; thiếu mã; lịch sử cũ thiếu tài khoản (tạm tính, xem trước = kết quả, bản dán gốc giữ nguyên); chặn khi ảnh hưởng lần migrate khác; xung đột bank với lịch sử có tài khoản. `assert_screens_consistent`: tổng mỗi đối tượng ở mỗi danh mục = tổng lịch sử của đối tượng tại danh mục đó.
- **Đối chiếu bản sao chỉ đọc của dữ liệu thật** (P43 vs mã này): tổng danh mục gốc/con, báo cáo tài khoản, sổ Công nợ, danh sách migrate **giống hệt**; chỉ tổng theo đối tượng đổi theo R191 (Kết ở Gốc vay 5→4 giao dịch: FT26267843740784 nằm ở Gốc vay › Kết; lãi của Trang, Thái, Tiến, Anh Tự ở Lãi vay không còn cộng vào người ở Gốc vay). 9 dòng sẽ hiện ở "Cần đối chiếu". 0 dòng lịch sử thật thiếu mã; 0 cặp lịch sử–sao kê gần trùng hậu tố.
- **Dữ liệu thật**: SHA256 `outputs/p01-user-trial` (146 file) và `private-data/` trước/sau phiên: xem mục 5.

## 3. QA cho PO
- Bộ giả: `/tmp/pcms-042-qa` — server **`http://localhost:8803`** (chạy từ `../PCMS-042`). Không dùng dữ liệu thật.
- Dựng lại: `specs/042-transaction-identity/qa_seed.py`; chạy `old` bằng mã P43 (`PYTHONPATH=../PCMS/src:../PCMS/tests`) rồi `new` bằng mã 042; khởi động `PYTHONPATH=src python3 -m pcms serve --p01 --data /tmp/pcms-042-qa --port 8803`.
- Kịch bản:
  1. **Ca Kết**: Danh mục → "Cần đối chiếu": `Gốc vay › Kết · Kết: 1 giao dịch, 5.000.000` (FT26267843740784). Thử "Thêm Kết vào Gốc vay › Kết" **hoặc** mở "Từng giao dịch" → "Điều chỉnh nơi phân loại" → Gốc vay → Xem trước → Xác nhận. Kiểm: Kết ở Gốc vay 10tr/2 → 15tr/3; tổng Gốc vay không đổi; một giao dịch nguồn.
  2. **Lãi**: `Lãi vay · Kết` chỉ có lối "Thêm Kết vào Lãi vay" (không gợi ý chuyển sang Gốc vay).
  3. **Nhập lặp**: tải lại `sao-ke-thang-9.xlsx` (hoặc file giống hệt) → "File đã có trong lịch sử nhập; không ghi thêm tiền". File `sao-ke-sai-noi-dung.xlsx` đang BLOCKED: "tham chiếu K3 xung đột với dữ liệu đã có".
  4. **Khác tài khoản**: `sao-ke-tai-khoan-khac.xlsx` (tài khoản 000456, cùng mã) STAGED 6 dòng mới, 0 trùng.
  5. **Lịch sử cũ thiếu tài khoản**: "Xuân Mai QA · chưa xác định tài khoản" → Xác định tài khoản → chọn QA vay → Xem trước (trước = sau −1.050.000.000) → Xác nhận; lịch sử hiện nhãn "tạm tính" trước khi xác định.
  6. Migrate lịch sử mới: hộp có ô "Tài khoản nguồn" bắt buộc; dán lại cùng dữ liệu cho đối tượng khác → dòng "Trùng lần migrate trước".
- Tôi đã chạy 1, 2, 5 trên bản sao `/tmp/pcms-042-qa-try` (đã tắt); `/tmp/pcms-042-qa` để nguyên trạng ban đầu cho PO.

## 4. Giới hạn còn lại
- **Sàn (crypto)**: chưa có bộ nhập sao kê sàn tương đương ngân hàng; định danh/chống trùng ở đây chỉ áp cho sao kê ngân hàng và lịch sử dán. Không tuyên bố hoàn thành bank/sàn.
- Dòng lịch sử **thiếu mã** không nhập được (dữ liệu thật hiện 0 dòng như vậy).
- Gần trùng khác hậu tố chỉ kiểm với giao dịch **sao kê** cùng tài khoản (không kiểm giữa hai lần dán lịch sử).
- Khoản vay có nhóm riêng: không điều chỉnh từng giao dịch; dùng Công nợ → Chuyển danh mục.
- Giao dịch tách nhiều phần: điều chỉnh ở màn phân loại.
- Dữ liệu thật: 7 lần migrate chưa có tài khoản ⇒ số đang là "tạm tính" cho tới khi Thạch xác định tài khoản; 9 dòng sai lệch quan hệ chờ Thạch chọn cách xử lý.
- Phát hành cần: merge, khởi động lại `:8792` (thư mục vận hành), PO xác nhận. Chưa làm.

## 5. Bảo vệ dữ liệu
Không sửa/phân loại/gộp/xóa/duyệt/nhập vào `outputs/p01-user-trial`, `private-data/`. Đối chiếu chỉ trên bản sao trong scratchpad. Hash trước phiên: `outputs` 146 file `d5794465…`, `private-data` `fa45318c…`; **sau phiên: giống hệt** (146 file, cùng hai hash). Không có thay đổi mới từ người dùng trong phiên.

## 6. File thay đổi (worktree `../PCMS-042`, nhánh `042-transaction-identity-impl`)
`src/pcms/categories.py`, `src/pcms/legacy_import.py`, `src/pcms/p01.py`, `src/pcms/server.py`, `src/pcms/web/p01.js`, `PRODUCT-SPEC.md` (R191–R194), `ACCEPTANCE.md` (A58–A59), `tests/test_p44_identity.py` (mới), `tests/test_p29,p31,p33,p36,p37,p38,p40_acceptance.py`, `specs/042-transaction-identity/*`, `docs/transaction-classification-pending.md`. Script dựng QA: `specs/042-transaction-identity/qa_seed.py`.
