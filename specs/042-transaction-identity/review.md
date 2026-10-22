# Review — Spec 042 (cập nhật 22/10/2026, Claude) — **ĐÃ PHÁT HÀNH P44 (22/10/2026), PO đạt có giới hạn**

> Vòng 2 (sau `docs/po-review-042-2026-10-22.md`) và vòng 3 (sau `docs/po-review-042-r2-2026-10-22.md`) ở cuối tài liệu.

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


---
## Vòng 2 — sửa hai lỗi P1 của PO review (22/10/2026)

### Đã sửa
1. **Gần trùng phụ thuộc thứ tự nhập** — nay chặn ở mọi thứ tự trong **cùng tài khoản**: lịch sử trước rồi sao kê (kiểm ở staging, kiểm lại và ghi: `check_batch` gọi chung), sao kê trước rồi lịch sử (`legacy_preview`), hai lần dán lịch sử, và dữ liệu đã lỡ có (trạng thái `NEAR_DUPLICATE`: không cộng, đếm vào "xung đột", xác định tài khoản bị chặn). Khác tài khoản: không coi là gần trùng. Không tự gộp hậu tố.
2. **Tạo mới quan hệ phân loại không hợp lệ** — `classify` (đường ghi duy nhất của phân loại: giao diện, API, điều chỉnh) kiểm đối tượng sở hữu (người của khoản vay; hồ sơ khác là chính nó) là **thành viên danh mục hiệu lực** sau `cat_eff` (nhóm khoản vay, chuyển đối tượng, gộp hồ sơ). Bỏ ngoại lệ native/legacy/kept cho LOAN/PROPERTY. Phần **y hệt** đã có trên chính giao dịch được giữ nguyên (dữ liệu cũ xem được, có thể lưu kèm ghi chú), sửa qua mục "Cần đối chiếu". Giao diện phân loại chỉ liệt kê thành viên (bỏ phần P42 liệt kê thêm người có khoản vay).
3. Phát hiện thêm khi đối chiếu lại: vòng 1 tôi báo "danh sách migrate giống hệt" nhưng chỉ so số dòng; thực tế tổng của **lần migrate đã hủy** bị hiện 0. Đã khôi phục cách hiện như P43 (tổng bản dán để tham chiếu, không tính) + test.

### Bằng chứng
- `cd ../PCMS-042/tests && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../src python3 -m unittest discover -s . -p "test_*.py"` → **Ran 396 tests, OK**; node 9/9 OK.
- `test_p44_identity.py`: 26 tests (19 ca riêng 042 + 7 ca kế thừa P18). Ca mới vòng 2: gần trùng lịch sử→sao kê (kiểm + ghi bị từ chối, không giao dịch nào được ghi), sao kê→lịch sử, khác tài khoản không gắn cờ / cùng tài khoản vẫn chặn, hai lần dán lịch sử + xác định tài khoản bị chặn + `NEAR_DUPLICATE` không cộng; phân loại mới bị chặn khi người không thuộc danh mục (ca PO tái hiện X1 → Gốc vay › Kết; ngay sau đó X1 không có trong "Cần đối chiếu" vì không được ghi), BĐS chưa thuộc Đầu tư BĐS, nhóm khoản vay đưa danh mục hiệu lực sang Long debt, chuyển đối tượng A→B, phần cũ y hệt lưu lại được nhưng không chuyển sang chỗ sai khác; lần migrate đã hủy.
- Test cũ cập nhật theo hợp đồng mới (P18, P19, P28, P40) — mỗi chỗ đều có khẳng định **bị chặn trước** rồi mới thêm thành viên; P01–P17 và bước dựng P18 tạo dữ liệu kiểu cũ bằng cờ nội bộ `require_membership=False` (mặc định bật, không có đường bật/tắt từ giao diện/API).
- Đối chiếu bản sao chỉ đọc dữ liệu thật (P43 vs mã vòng 2): tổng gốc/con danh mục, báo cáo tài khoản, sổ Công nợ, **danh sách migrate (kể cả tổng)** giống hệt; 9 dòng "Cần đối chiếu".
- QA trình duyệt trên bản sao riêng (đã tắt): phân loại X1 → Gốc vay › Kết không có Kết trong danh sách; gọi thẳng API bị chặn với thông báo "Kết chưa là thành viên danh mục Gốc vay › Kết…"; file `sao-ke-gan-trung.xlsx` BLOCKED "gần trùng … khác hậu tố"; xem trước lịch sử dán `FT26267843740784\BNK` vào QA vay báo gần trùng.

### QA mới cho PO (bộ sạch, riêng)
- **`http://localhost:8805`**, dữ liệu `/tmp/pcms-042-qa-r2` (giả), dựng bằng `specs/042-transaction-identity/qa_seed.py` (đổi đường dẫn dữ liệu sang `-r2`). Bộ `:8803` của PO giữ nguyên trạng PO đã thao tác.
- Kịch bản vòng 2 (bổ sung vào mục 3 ở trên):
  7. **P1 gần trùng, lịch sử trước**: tài khoản "QA tài khoản gần trùng" có lịch sử "Gần Trùng QA" mã `FT26267843740784\BNK`; file `sao-ke-gan-trung.xlsx` của tài khoản đó đang **BLOCKED** (dòng 9 gần trùng). Thử "Ghi toàn đợt": bị từ chối.
  8. **P1 gần trùng, sao kê trước**: Migrate lịch sử cũ → tài khoản QA vay → dán `20/09/2026⇥Cho Ket vay 5tr⇥FT26267843740784\BNK⇥5,000,000⇥⇥1` → Xem trước báo gần trùng, không ghi được.
  9. **P1 quan hệ**: phân loại `X1` → Gốc vay › Kết: không có đối tượng Kết để chọn; thêm Kết vào Gốc vay › Kết (màn Danh mục) rồi mới phân loại được.

### Giới hạn (không đổi so với vòng 1) + mới
- Sàn chưa có importer sao kê; định danh/chống trùng chỉ cho sao kê ngân hàng và lịch sử dán.
- ~~Gần trùng trong cùng một file sao kê chưa kiểm~~ → đã sửa ở vòng 3.
- Với dữ liệu thật sau phát hành: phân loại mới tiền lãi vào Lãi vay sẽ cần người (Kết, Thái…) là thành viên Lãi vay trước — dùng nút "Thêm … vào Lãi vay" ở mục Cần đối chiếu.

### Commit vòng 2: xem `git log` nhánh `042-transaction-identity-impl` (sau `8379d78`).


---
## Vòng 3 — gần trùng / lặp trong cùng file sao kê và cùng lần dán lịch sử (22/10/2026)

### Đã sửa
- **Cùng file sao kê** (`p01.py check_batch`): mỗi dòng của file được đưa vào tập kiểm tra; dòng sau có mã lặp y hệt hoặc chỉ khác hậu tố với dòng trước ⇒ lỗi nêu rõ dòng nào trùng dòng nào; file BLOCKED; "Ghi toàn đợt" bị từ chối; **0 giao dịch được ghi**; không phụ thuộc thứ tự hai dòng; số dư hợp lệ vẫn chặn. Không tự gộp, không xóa.
- **Cùng lần dán lịch sử** (`legacy_import.py legacy_preview`): trước đây dòng lặp y hệt trong cùng lần dán được đánh "Trùng lần migrate trước" và tự bỏ qua — tức tự gộp; nay là lỗi cần đối chiếu. Mã chỉ khác hậu tố trong cùng lần dán cũng là lỗi. Hai đường nhập (sao kê, dán lịch sử) cùng một hành vi.
- Khác tài khoản: không gắn cờ ở cả hai đường.

### Bằng chứng
- Toàn bộ suite: **Ran 400 tests, OK**; node 9/9 OK. `test_p44_identity`: 30 tests (4 ca mới vòng 3).
- Ca mới: file mới hai mã `FTQA` / `FTQA\BNK`, số dư từng dòng hợp lệ, **cả hai thứ tự**: import → BLOCKED với thông báo "gần trùng … trong cùng file", `check_batch` báo lỗi, `publish` bị từ chối, số giao dịch của tài khoản vẫn 0; mã lặp y hệt trong file: BLOCKED + publish từ chối + 0 giao dịch; hai biến thể hậu tố ở **hai tài khoản khác nhau**: STAGED, publish được, mỗi tài khoản 1 giao dịch; cùng lần dán lịch sử: lặp y hệt, khác hậu tố (cả hai thứ tự) ⇒ xem trước có lỗi, `can_import=False`, `duplicates=0`, import bị từ chối, số dòng lịch sử không tăng; khác tài khoản ⇒ nhập được.
- QA API (xem trước, không ghi) trên `:8806`: lần dán `FT8`+`FT8` ⇒ "Mã lặp trong cùng lần dán (trùng dòng 1)"; `FT8\X`+`FT8` ⇒ "Mã gần trùng dòng 1 (FT8\X) trong cùng lần dán".
- Bản sao chỉ đọc dữ liệu thật: 0 file có mã gốc lặp khác hậu tố; kiểm tra lại các file đang chờ (44), (45), (5) cho kết quả **giống hệt** P43 (không có file nào bị chặn thêm); tổng danh mục/báo cáo/Công nợ/danh sách migrate giống hệt.
- Hash `outputs/p01-user-trial` (146 file) và `private-data/` giống hệt trước phiên.

### QA vòng 3 cho PO (bộ sạch, riêng)
- **`http://localhost:8806`**, dữ liệu giả `/tmp/pcms-042-qa-r3` (dựng bằng `qa_seed.py`, đường dẫn `-r3`). `:8803` (PO vòng 1) và `:8805` (vòng 2) giữ nguyên.
- Thêm kịch bản:
  10. Tài khoản "QA cùng file": `sao-ke-cung-file-gan-trung.xlsx` **BLOCKED** — "Dòng 10: mã FTQA\BNK gần trùng dòng 9 (FTQA) trong cùng file"; Ghi toàn đợt bị từ chối.
  11. Migrate lịch sử cũ, tài khoản QA vay, dán hai dòng cùng mã `FT8` (hoặc `FT8\X` rồi `FT8`): Xem trước báo lỗi, không ghi được.

### Commit vòng 3: nhánh `042-transaction-identity-impl`, sau `ea5706c`. T06 vẫn chờ PO.


---
## Nghiệm thu PO vòng 3 và phát hành
- PO: **đạt có giới hạn** cho phạm vi ngân hàng/lịch sử dán và sửa sai lệch phân loại (`docs/po-review-042-r3-2026-10-22.md`). Không xác nhận importer sàn (backlog B1). Ghi chú không chặn: số dòng ứng viên trên file bị chặn (backlog B2).
- Phát hành đúng mã đã nghiệm thu: commit `39c4881` (mã) + một commit chỉ tài liệu (tasks/review/IMPLEMENTATION-STATUS, ba biên bản PO). Không sửa mã sau nghiệm thu.
- Bằng chứng sau phát hành: ghi ở `IMPLEMENTATION-STATUS.md` mục P44 (commit sau merge).

### Bằng chứng phát hành (22/10/2026)
- PR #39 merge → `main` = `facc5a6`; `git diff 39c4881 facc5a6 -- src tests` rỗng (mã/test đúng bản PO nghiệm thu).
- Kiểm `main` từ worktree sạch: **400 tests OK**, 9/9 test node OK; build `P44-2026-10-22`.
- Thư mục vận hành `PCMS/`: `git merge --ff-only origin/main` (không đụng `README.md`, `specs/README.md`, `docs/product/`, `specs/008-product-map/` đang sửa dở; ba biên bản PO chưa theo dõi được thay bằng bản giống hệt trong `main`).
- Khởi động lại `:8792` (cùng lệnh, cùng thư mục dữ liệu). `/api/state`: build `P44-2026-10-22`, có capability `transaction-identity`; `p01.js` phục vụ = `main` (SHA256 `9e0fe8ed…`). Mở màn Danh mục (chỉ xem): có mục "Cần đối chiếu" với **9** dòng; **6** lần migrate đang hoạt động chưa có tài khoản (+1 lần đã hủy); màn Đối tượng 14 đối tượng.
- Dữ liệu thật: SHA256 `outputs/p01-user-trial` (146 file `d5794465…`) và `private-data/` (`fa45318c…`) trước/sau phát hành **giống hệt**. Không phân loại, gộp, xác định tài khoản hay sửa dữ liệu thật nào; các việc đó chờ Thạch.
- Đã tắt các server QA giả `:8803`, `:8805`, `:8806` (dữ liệu giả ở `/tmp/pcms-042-qa*` còn giữ, dựng lại bằng `qa_seed.py`).
