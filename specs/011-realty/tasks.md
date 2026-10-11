---
description: "Task list — 011 realty"
---

# Tasks: Bất động sản bản đầu
**Input**: `/specs/011-realty/` · **Tests**: có (`tests/test_p13_acceptance.py`) · Ràng buộc: Decimal, VND nguyên, không đụng `outputs/p01-user-trial`, **chỉ `git add` đường dẫn cụ thể**, quy trình PR.

## Phase 1: Setup
- [X] T001 Baseline hồi quy vào `specs/011-realty/baseline.txt` (unittest P01–P12 + `node --check` + `node tests/js/*.test.cjs`)
- [X] T002 SHA256 `outputs/p01-user-trial/**` vào `/tmp/pcms-011-data-before.sha256`

## Phase 2: Foundational
- [X] T003 Tạo `src/pcms/realty.py`: mixin `Realty` với `realty_state(s)` (setdefault `valuations/mortgages/contributions`), helper `prop(s,id)` (PROPERTY profile), hàm rỗng `change_realty`, `realty_view`, `realty_history`; `src/pcms/p01.py`: thêm mixin, dispatch `realty-*`, `'realty': self.realty_view(s)` và capability `'realty'`, build `P13-…`; `src/pcms/server.py`: route `/api/realty-history`

## Phase 3: US1 — Vốn có nguồn, chi phí, lịch sử (P1) 🎯 MVP
- [X] T004 [US1] `realty_view` (vốn paid/received/net/transactions từ `investment`; chi phí spent/refunded/net từ `expense`; `evidence`; `unclassified`) và `realty_history` (rows CAPITAL/COST, DRAFT/APPROVED, nguồn, `source_notice`) trong `realty.py`
- [X] T005 [US1] Test `tests/test_p13_acceptance.py`: Đất A ba khoản 200/150/250 triệu → paid 600 triệu, 3 dòng lịch sử; giao dịch tách hai phần (một phần gắn BĐS) chỉ tính phần đó; tiền vào Đầu tư BĐS là `received`; Chi tiêu gắn BĐS + hoàn chi → costs net; BĐS rỗng `evidence != HAS_DATA` không có số 0 như đối soát; đọc không ghi sự kiện; `report()`/snapshot không đổi
- [X] T006 [US1] UI `p01.html` (nút `Bất động sản`) và `p01.js`: `realtyMode` (wrapper `render`, capture-click tắt khi chọn mục khác), `renderRealty()` thẻ từng BĐS (vốn, chi phí, nhãn thiếu dữ liệu, nút Lịch sử), `realtyHistory()` dùng `sourceDetail`, nút "+ BĐS" (`object-quick-create` PROPERTY), nhắc chưa phân loại

## Phase 4: US2 — Giá trị hiện tại và chênh lệch (P1)
- [X] T007 [US2] `change_realty` cho `realty-valuation` (value VND nguyên >0, `date` ISO, `source` bắt buộc ≤500, `note` ≤500, property là PROPERTY) và `realty-valuation-void` (lý do bắt buộc, không xóa); `realty_view`: giá trị hiện tại = ACTIVE có ngày mới nhất (hòa → tạo sau), `history`, `gap` = value − (paid − received) kèm nhãn cố định, không có giá trị → `gap=None`
- [X] T008 [US2] Test: giá trị 900 triệu + vốn 600 triệu → gap +300 triệu có nhãn chứa "không phải lãi/lỗ"; không có giá trị → không gap; giá trị mới thay hiện tại, hủy giá trị mới quay về bản trước, bản hủy còn trong history; thiếu ngày/nguồn/giá trị ≤0/không nguyên bị chặn; property không phải BĐS bị chặn; hủy thiếu lý do bị chặn
- [X] T009 [US2] UI: hộp thoại "+ Giá trị hiện tại" (số VND, ngày, nguồn, ghi chú), vốn cạnh giá trị hiện tại (ngày, nguồn), chênh lệch với nhãn, lịch sử giá trị và nút Hủy kèm lý do

## Phase 5: US3 — Thế chấp (P2)
- [X] T010 [US3] `realty-mortgage` (loan là LOAN, `purpose` bắt buộc, chặn nếu loan đã có mortgage ACTIVE) và `realty-mortgage-end` (lý do bắt buộc, `ENDED`); `realty_view.mortgages[]` kèm `loan_name`, `principal` từ `debt_register` (`None` + `issues` khi chưa thiết lập), không đụng `gap`/vốn
- [X] T011 [US3] Test: liên kết hiện dư gốc theo công nợ ("cần thiết lập" khi chưa có gốc đầu); khoản vay thứ hai-BĐS bị chặn khi còn hiệu lực; sau `mortgage-end` liên kết được BĐS khác; loan không phải LOAN bị chặn; thiếu mục đích bị chặn; `gap` và `capital` không đổi khi có thế chấp; tiền vay không vào thu nhập (category totals income không đổi); công nợ (`debts`) không đổi
- [X] T012 [US3] UI: hộp thoại "+ Thế chấp" (chọn khoản vay, mục đích), hiển thị khoản vay/dư gốc/mục đích, nút Kết thúc kèm lý do; ghi chú "không trừ nợ khỏi giá trị"

## Phase 6: US4 — Góp vốn nhiều người (P2)
- [X] T013 [US4] `realty-contribution` (party là PERSON, amount VND nguyên >0, `evidence` bắt buộc, `date` ISO tùy chọn) và `realty-contribution-void` (lý do bắt buộc); `realty_view.contributions` = `{items, total}` (chỉ ACTIVE vào tổng); không có trường phần trăm/quyền lợi
- [X] T014 [US4] Test: A 300 triệu + B 200 triệu → items 2, total 500 triệu; thiếu bằng chứng/party không phải PERSON/amount ≤0 bị chặn; hủy loại khỏi total nhưng còn trong lịch sử; kết quả view không chứa khóa tỷ lệ (`percent`, `share`, `ratio`); vốn của Thạch (từ sao kê) hiển thị riêng, không bị cộng vào `contributions.total`
- [X] T015 [US4] UI: hộp thoại "+ Góp vốn" (chọn người từ hồ sơ người hoặc tạo nhanh người bằng `profile` PERSON có sẵn, số tiền, bằng chứng, ngày), danh sách người góp + tổng, "Vốn của bạn (từ sao kê)" riêng; không cột %

## Phase 7: Polish & nghiệm thu
- [X] T016 `node --check`, `node tests/js/*.test.cjs`, toàn bộ unittest P01–P13; so với baseline
- [X] T017 PO dùng thử UI trên `/tmp/pcms-realty-qa` (8801) theo `quickstart.md` §3; desktop và 375px; ghi lỗi, sửa, kiểm lại
- [X] T018 Đối chiếu SHA256 (T002) phải khớp
- [X] T019 Viết `outputs/p13-handoff.md` (file phải tồn tại trước khi tick); cập nhật `IMPLEMENTATION-STATUS.md`, `HANDOFF.md`, `ACCEPTANCE.md` (P13), `specs/README.md` (hàng 011; ghi chú spec 007 còn lại crypto/chung cư/tổng tài sản) bằng `git update-index --cacheinfo`
- [ ] T020 Push nhánh, mở PR vào `main`, merge; `git fetch origin main:main`; restart 8792, kiểm chỉ đọc, đối chiếu checksum

## Dependencies
Phase 1 → 2 → US1 → US2 → US3 → US4 → Polish. Cùng sửa `realty.py`/`p01.js`/`test_p13_acceptance.py` nên tuần tự. MVP = US1 + US2.
