# Implementation Plan: Crypto / ví bản đầu

**Branch**: `012-crypto-wallets` | **Date**: 2026-10-12 | **Spec**: [spec.md](spec.md)

## Summary
Mô-đun `crypto_ledger.py` (mixin `CryptoLedger`) lưu sổ phụ `state['crypto']` (nơi giữ, xác nhận số dư, giá, vốn — chỉ thêm, hủy có lý do) và dẫn xuất chỉ-đọc `crypto_view`: số hiện tại theo (nơi giữ, coin, trạng thái), giá trị USDT, tỷ trọng theo nơi giữ và coin, vốn và chênh lệch có nhãn. Không đụng giao dịch ngân hàng, phân loại, snapshot, công nợ. UI: màn "Crypto" (tổng quan + tỷ trọng, từng nơi giữ với thành phần, khu vị thế/nợ margin riêng, giá/vốn từng coin) và hộp thoại ghi nhận.

## Technical Context
**Language/Version**: Python 3.13 stdlib + JS thuần · **Storage**: khóa mới `state['crypto']` (`setdefault`, không đổi schema bắt buộc) · **Testing**: `tests/test_p14_acceptance.py`, PO dùng thử UI · **Constraints**: Decimal ở backend (số lượng ≤18 chữ số thập phân, giá ≤12); giá trị làm tròn 6 chữ số, tỷ trọng 2 chữ số half-up; không đụng `outputs/p01-user-trial`; gate UI theo capability `crypto`; quy trình nhánh → PR → merge; chỉ `git add` đường dẫn cụ thể.

## Constitution Check
| Nguyên tắc | Đánh giá |
|---|---|
| I Dữ liệu người dùng | Đạt — thử trên bộ giả; SHA256 trước/sau |
| II Không tự quyết số liệu | Đạt — số lượng, giá, vốn do Thạch nhập; không giá tự động; không lãi/lỗ khi thiếu vốn; vị thế/nợ không cộng trừ |
| III Decimal | Đạt — mọi phép tính ở backend bằng Decimal |
| IV Lịch sử bất biến | Đạt — chỉ thêm, hủy có lý do |
| V Bằng chứng | Test + PO dùng thử + hồi quy |
| VI Gọn | Một mô-đun mới, sửa tối thiểu `p01.py`/`p01.js`/`p01.html` |

## Project Structure
```text
specs/012-crypto-wallets/{spec,plan,research,data-model,quickstart,tasks}.md, contracts/api.md
src/pcms/crypto_ledger.py   # mới: CryptoLedger (change_crypto, crypto_view)
src/pcms/p01.py             # mixin, dispatch crypto-*, view['crypto'], capability crypto
src/pcms/web/p01.html,p01.js
tests/test_p14_acceptance.py
```
(Không cần route server mới: lịch sử nằm trong `view['crypto']`, dữ liệu nhỏ.)
