# Implementation Plan: TRX/Energy bản đầu

**Branch**: `006-trx-energy` | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

## Summary
Thêm sổ ghi nhận thủ công cho kinh doanh TRX/Energy: khách → đơn (Energy một lần / gói tháng / bán TRX) → khoản thu (USDT hoặc VND quy đổi, tùy chọn gắn giao dịch ngân hàng) → phân bổ → báo cáo theo tiền thực thu; thưởng staking ghi số lượng. Làm thành mô-đun `trx_energy.py` (mixin của `P01Store`) lưu trong khóa `trx` của state sự kiện hiện có, UI trong `p01.js`. Tái dùng cơ chế sự kiện/audit/backup đã có; không tích hợp blockchain, không đụng dữ liệu ngân hàng.

## Technical Context
**Language/Version**: Python 3.13 stdlib + JS thuần (như 005) · **Storage**: sự kiện JSON hiện có; thêm khóa `state['trx']` (tạo bằng `setdefault`, state cũ vẫn hợp lệ — không đổi schema bắt buộc) · **Testing**: `unittest` `tests/test_p09_acceptance.py`, `node --check`, PO dùng thử UI trên bộ giả · **Platform**: web cục bộ một người dùng · **Constraints**: Decimal; USDT 6 chữ số thập phân, VND nguyên; không ghi tiền hai lần (gắn giao dịch ngân hàng chỉ một lần/số tiền); không tự quá hạn; gate UI theo `view.capabilities` có `trx-energy`.

## Constitution Check
| Nguyên tắc | Đánh giá |
|---|---|
| I Dữ liệu người dùng | Đạt — chỉ thử trên bộ giả; SHA256 trước/sau |
| II Không tự quyết số liệu | Đạt — tỷ giá/giá/số lượng do Thạch nhập; không tự suy lãi/lỗ (R66), không tự quá hạn (R40) |
| III Decimal | Đạt — mọi cộng/quy đổi bằng Decimal ở backend |
| IV Lịch sử bất biến | Đạt — chỉ thêm; sửa sai bằng void có lý do, giữ bản ghi |
| V Bằng chứng | Có test + PO dùng thử + hồi quy |
| VI Gọn | Một mô-đun mới, không kiến trúc mới |

## Project Structure
```text
specs/006-trx-energy/{spec,plan,research,data-model,quickstart,tasks}.md, contracts/api.md
src/pcms/trx_energy.py        # mới: TrxEnergy mixin (change_trx, trx_view, trx_report)
src/pcms/p01.py               # thêm mixin, dispatch, view['trx'], capability
src/pcms/server.py            # /api/trx-report
src/pcms/web/p01.html,p01.js  # nút TRX / Energy + màn + hộp thoại
tests/test_p09_acceptance.py
```
**Structure Decision**: mixin cùng kiểu `InterestSettlement`/`LoanCompletion`.
