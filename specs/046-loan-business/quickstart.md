# Quickstart / kịch bản kiểm — spec 046

## Chuẩn bị (chỉ dữ liệu giả)

```bash
cd /Users/nerkan/Documents/Working/PCMS-wt-046
PYTHONPATH=src python3 /Users/nerkan/Documents/Working/PCMS-QA/seed_p49.py /Users/nerkan/Documents/Working/PCMS-QA/p49-po
PYTHONPATH=src python3 -m pcms serve --p01 --data /Users/nerkan/Documents/Working/PCMS-QA/p49-po --port 8809
```

Script seed tạo bộ dữ liệu giả mô phỏng cấu trúc thật:
- Danh mục Hot Debt (nhóm chi) › Ngắn hạn.
- Long Debt.
- Vay bạn.
- Thành viên Kết và Tươi.
- Hồ sơ khoản kiểu cũ "Khoản Kết" Phải thu, có liên kết ở gốc Gốc vay.
- Một dòng lịch sử cũ trong Hot Debt.
- Một BĐS nằm trong Hot Debt (để thấy xung đột "không phải Người").
- Các giao dịch của bảng ví dụ trong spec. Tất cả đã phân loại danh mục, chưa có chi tiết nghiệp vụ.

## Kịch bản

1. **Kế thừa và xung đột**
   - Gắn Đi vay cho Hot Debt › Ngắn hạn, rồi gắn Cho vay cho Hot Debt → bị chặn, nêu "Hot Debt › Ngắn hạn (Đi vay)".
   - Gỡ ở Ngắn hạn rồi gắn Cho vay cho Hot Debt → xem trước có: thiếu (các giao dịch ví dụ), xung đột (BĐS không phải Người) → xác nhận.
   - Ngắn hạn hiện "kế thừa".
2. **Nhiều khoản**: ở Công nợ tạo CV-0001 (500, môi giới Long 200), CV-0002 (600) cho Kết; ở Vay bạn tạo ĐV-0001 (0).
3. **Ghi chi tiết theo ví dụ (bước 1–7)**:
   - So từng số với bảng trong spec.
   - Ở bước 4, trước khi ghi, thử Thu gốc 110.000.000 → bị chặn.
   - Ở bước 6, lưu nháp còn thiếu → sổ không đổi.
4. **Đang sửa**: với giao dịch bước 4, lưu nháp thay thế → Công nợ vẫn hiện số cũ → ghi → số mới. Lịch sử có 2 phiên bản.
5. **Chặn đường song song**:
   - Sửa phân loại giao dịch bước 1 sang Chi tiêu → bị chặn.
   - Chuyển Kết sang danh mục khác → bị chặn.
   - Gỡ nghiệp vụ Hot Debt → bị chặn.
   - Xóa hẳn Hot Debt → bị chặn.
6. **Chưa đầy đủ**:
   - Bước 8 (Tươi) → băng "Chưa đầy đủ: 1 giao dịch, vào 5.000.000" → Mở danh sách chờ.
   - Hoàn tất khoản của Tươi bị chặn (Tươi chưa có khoản: tạo rồi thử).
7. **Hoàn tất**:
   - CV-0001 sau bước 6: không hoàn tất được (còn thiếu 30.000).
   - Miễn giảm 30.000 → hoàn tất.
   - Mở lại.
8. **Đồng nhất giữa các màn**: so Phải thu/Phải trả giữa Công nợ và Tổng tài sản; số giao dịch và khoản của Kết giữa Công nợ, Danh mục (thành viên Kết) và Đối tượng.
9. **Snapshot**:
   - Duyệt tài khoản khi còn nguồn chờ → được.
   - Ghi chi tiết sau đó → snapshot không đổi, không bị yêu cầu điều chỉnh.

## Kịch bản vòng sửa 29/10 (PO review P1, P2)

- **P1**: ghi một chi tiết cho CV-0001 → Sửa khoản: ô mức lãi / mức môi giới bị khóa, kèm lý do; API `lb-loan-edit` đổi `rate` bị chặn; lãi các ngày đã qua không đổi; hủy chi tiết hoặc mở lại khoản vẫn khóa; khoản chỉ có nháp sửa được.
- **P2**: phân loại L9 (chưa phân loại) vào Hot Debt: thiếu người hoặc thiếu khoản → không lưu; tách 2 phần cho 2 khoản → lưu, "Chờ chi tiết"; đóng hộp Chi tiết → sổ không đổi; Sửa phân loại, Migrate lịch sử, phân loại hàng loạt cùng quy tắc; phần cũ (L1–L8, FT900) vẫn trong danh sách chờ.

## Lệnh test

```bash
cd tests && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../src python3 -m unittest test_p49_loan_business -v
cd tests && PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=../src python3 -m unittest discover -s . -p "test_*.py"
node --test tests/js/
```

## Bất biến dữ liệu thật

Trên bản sao trong scratchpad: `view()` của P48 và P49 cho cùng báo cáo tài khoản, cùng `debt_register`, cùng tổng danh mục và cùng `asset_core`. Phần `loan_book` là phần mới: chỉ có dòng kiểu cũ và không có nguồn chờ, vì chưa danh mục nào mang nghiệp vụ.
