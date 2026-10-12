# Implementation Plan: Tổng hợp tài sản bản đầu

**Branch**: `013-asset-overview` | **Date**: 2026-10-12 | **Spec**: [spec.md](spec.md)

## Summary
Mô-đun `assets.py` (mixin `AssetOverview`) tính **dẫn xuất chỉ-đọc** `asset_view` từ các phân hệ sẵn có (số dư ngân hàng `report`, `debt_register`, `realty_view`, `crypto_view`, `trx_view`) thành hai khối VND và USDT (tài sản theo nhóm, nợ theo nhóm, ròng, tỷ trọng, cơ sở, cảnh báo, lối tới màn nguồn) và lưu **bản chụp bất biến** vào `state['asset_snapshots']` bằng action `assets-snapshot` (kèm hash). Không nhập số liệu mới, không đổi phân hệ nguồn. UI: màn "Tổng tài sản" với hai khối, cảnh báo, nút Lưu bản chụp, danh sách bản chụp và chênh lệch.

## Technical Context
**Language/Version**: Python 3.13 stdlib + JS thuần · **Storage**: khóa mới `state['asset_snapshots']` (`setdefault`) · **Testing**: `tests/test_p15_acceptance.py`, PO dùng thử UI · **Constraints**: Decimal; không quy đổi tiền tệ; không đụng `outputs/p01-user-trial`; gate UI theo capability `assets`; quy trình nhánh → PR → merge; chỉ `git add` đường dẫn cụ thể.

## Constitution Check
| Nguyên tắc | Đánh giá |
|---|---|
| I Dữ liệu người dùng | Đạt — thử trên bộ giả; SHA256 trước/sau |
| II Không tự quyết số liệu | Đạt — chỉ hợp nhất số đã nhập; cơ sở tính BĐS ghi rõ; không giá/tỷ giá mới |
| III Decimal | Đạt — tổng/tỷ trọng bằng Decimal ở backend |
| IV Lịch sử bất biến | Đạt — bản chụp có hash, không sửa/xóa |
| V Bằng chứng | Test + PO dùng thử + hồi quy |
| VI Gọn | Một mô-đun mới, không route mới (view trong `/api/state`) |

## Project Structure
```text
specs/013-asset-overview/{spec,plan,research,data-model,quickstart,tasks}.md, contracts/api.md
src/pcms/assets.py        # mới: AssetOverview (asset_view, change_assets)
src/pcms/p01.py           # mixin, dispatch assets-*, view['assets'], capability assets
src/pcms/web/p01.html,p01.js
tests/test_p15_acceptance.py
```
