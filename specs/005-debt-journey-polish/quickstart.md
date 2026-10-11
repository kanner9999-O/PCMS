# Quickstart — kiểm 005 debt-journey-polish

**Tiền đề**: chỉ dùng bộ giả. Không chạm `outputs/p01-user-trial`, không gọi API ghi vào cổng 8792. Cổng 8799 có thể bị server QA cũ chiếm; dùng 8801.

## 1. Dựng dữ liệu giả và server QA
```bash
cd /Users/nerkan/Documents/Working/PCMS
rm -rf /tmp/pcms-claude-qa
PYTHONPATH=src:tests python3 -c "from pcms.p01 import P01Store; from test_p07_acceptance import seed; seed(P01Store('/tmp/pcms-claude-qa'))"
PYTHONPATH=src python3 -m pcms serve --p01 --data /tmp/pcms-claude-qa --port 8801
```
Bộ giả: 3 người — An (đã hoàn tất), Bình (phải thu 100.000.000), Chi (hết gốc còn lãi); nguồn 01/09–30/09/2026.

## 2. Kiểm tự động
```bash
PYTHONPATH=src:tests python3 -m unittest test_p08_acceptance test_p07_acceptance test_p06_acceptance test_p05_acceptance test_p04_acceptance
node --check src/pcms/web/p01.js
```
Kỳ vọng: test mới (summary khớp tổng người, `completion_blocker`, state không ghi sự kiện, báo cáo không đổi) và hồi quy P04–P07 đều đạt; cú pháp JS đạt.

## 3. Kịch bản PO trên UI (http://127.0.0.1:8801/)
1. Công nợ → đầu màn thấy phải thu 100.000.000 · phải trả 0 · 3 người · 1 hoàn tất / 2 đang hoạt động · 0 cần thiết lập (SC-002).
2. Khoản "Chi · hết gốc còn lãi" thấy lý do chưa hoàn tất và nút tới Bảng kê lãi; khoản "An" chỉ một nhãn trạng thái (SC-003, FR-009).
3. "Báo cáo dòng tiền" ngày 11/10/2026 mở thẳng ngày nguồn mới nhất 30/09/2026 với dòng giải thích; số tháng 09 là 2,7 triệu lãi nhận, 0,2 triệu chi phí gắn khoản, chênh 2,5 triệu, thu gốc 200 triệu riêng (số P07 không đổi) (SC-001, SC-005).
4. Đổi tay sang tháng 11/2026 → có cảnh báo "kỳ này chưa có nguồn" và khoảng nguồn đã ghi; giá trị tự chọn không bị ghi đè.
5. Từ tài khoản → "Khoản vay liên quan" → Công nợ; từ một khoản → "Mở tài khoản" → quay lại (SC-004).

## 4. Phát hành (sau nghiệm thu)
Kiểm SHA256 20 file dữ liệu `outputs/p01-user-trial` trước và sau; restart đúng backend 8792; mở UI chính chỉ đọc. Báo Thạch trước khi restart.
