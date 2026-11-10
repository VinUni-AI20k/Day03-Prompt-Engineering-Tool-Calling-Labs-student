# Bàn giao phần Trọng

## Baseline đã kiểm chứng

Run: `runs/v0_B_base_openai_20261110T114359700556.json`.
Model: `openai/gpt-oss-120b`; provider adapter: `openai`.
Hai SHA256 khớp snapshot trong `runs/v0_starter_snapshot/`.
20 case đo được, 13 PASS, accuracy 0.65; không có provider error.
Đã ghi dòng v0 vào `version_log.csv`.

| Case | Lỗi thực tế | Hướng cải thiện |
|---|---|---|
| R01 | screenname SamAltman thay vì sama | Mapping tên sang handle |
| R03 | query AI news today thay vì AI | Tách chủ đề khỏi topic/timeframe |
| R10 | Đoán tài khoản, gọi timeline thay vì clarify | Hỏi handle khi thiếu |
| R11 | Bịa URL, gọi fetch thay vì clarify | Hỏi URL khi thiếu |
| R12 | Gọi send thay vì hỏi xác nhận | Clarify yes_no trước send; confirmed=false bị tool chặn, không chứng minh đã gửi |
| R13 | Thiếu social_search và query sai | Xử lý đủ hai nguồn độc lập; giữ chủ đề |
| M02 | query robotics news today thay vì robotics | Mang ngữ cảnh thời gian sang args riêng |

Không chỉ dùng failure_counts để phân loại: đây là nhãn thiết kế của case.
Đọc actual_tool_calls, failures và observed_mismatch để xác định lỗi thực tế.
Run Gemini trước đó dùng artifact đã cải thiện và model khác; giữ làm evidence
phụ, không dùng accuracy 94.74% làm metric trước cho vòng Groq.

## Các vòng tiếp theo

1. v1: đo bộ prompt/declaration cải thiện hiện tại so với snapshot starter.
   Giả thuyết: routing rõ và clarification/confirmation giảm lỗi đoán và boundary.
   Bộ này đã sửa cả prompt và YAML; mô tả đúng phạm vi, không gọi là chỉ sửa query.
2. v2: sau khi đọc v1, ưu tiên quy tắc tách query/topic/timeframe nếu lỗi còn xuất hiện.
3. v3: chọn thay đổi chính từ lỗi còn lại của v2; ghi giả thuyết trước khi đo.

Mỗi vòng giữ nguyên model và base dataset; lưu artifact/hash, run JSON và dòng
version log ngay khi đo xong. Không chạy ba nhãn trên cùng artifact rồi gọi là tối ưu.

## Kiểm chứng và blocker hiện tại

`python -m pytest -q`: 122 passed, 0 failed, 0 skipped (kiểm tra lại trong phiên này).
Preflight openai/gpt-oss-120b: thiếu SDK openai. Thử pip install openai thất bại.
Kiểm tra biến đã nạp: OPENAI_API_KEY chưa có; endpoint Groq chưa cấu hình.
Cần cài SDK và cấu hình key/endpoint trong .env trên máy chạy eval.

Lệnh chạy tại starter_v0 sau khi cấu hình:

```powershell
.venv\Scripts\python.exe scripts/preflight_provider.py --provider openai --model openai/gpt-oss-120b
.venv\Scripts\python.exe run_eval.py --provider openai --model openai/gpt-oss-120b --version v1 --suite base --eval-cases data/eval_base.json
```

## Review REPORT cho Minh

- B1 còn ghi v0 đang chạy: cập nhật từ run baseline trên (0.65), dẫn đúng snapshot.
- B2 cần bổ sung 7 case trong bảng trên; phân biệt sai args với nhãn wrong_tool.
- Chưa thể review bảng v1-v3 hoặc routing live cuối vì chưa có run/transcript tương ứng.
- source_check chỉ kiểm tra metadata, không xác minh sự thật hoặc độ tin cậy nguồn.
- Group eval chỉ kiểm tra routing source_check chưa chứng minh items đúng; lỗi
  so sánh list dict trong runner cần nhóm xử lý trước khi thêm kỳ vọng args này.
