# Báo cáo cá nhân — NguyenBaQuangHuy-2A202603926

## 1. Thông tin thành viên

- Họ tên: Nguyễn Bá Quang Huy
- MSSV: 2A202603926
- Email: quanghuynguyenba@gmail.com
- GitHub: quanghuynguyenba@gmail.com (branch làm việc quanh `system_prompt.md`)

## 2. Phần việc phụ trách

Trong nhóm mình phụ trách cải tiến `starter_v0/artifacts/system_prompt.md` cho **v1**. Cụ thể:

- Bỏ chỉ dẫn xấu cố ý của starter (đoán thay vì hỏi, gửi không xác nhận, ép một bước).
- Thêm rule clarify khi thiếu thông tin, xác nhận trước khi `send`, routing tool, và multi-turn chỉ xử lý lượt mới nhất.
- Phối hợp tester (Vũ) đọc fail log / phản hồi rủi ro credentials để chốt bản prompt cuối trước khi ghi dòng v1 vào `artifacts/version_log.csv`.

## 3. Đóng góp cụ thể

**Hai bước sửa prompt**

1. `ba02a75` (`update system prompt`): thay toàn bộ starter xấu bằng rule clarify + routing + confirm trước khi `send`. Agent không còn được đoán handle/URL hay tự gửi.
2. `425911f` (`fix system prompt`): bỏ rule xin platform/credentials ngay trong chat (Vũ báo rủi ro lộ token). Thu hẹp xác nhận còn `clarify(response_type=yes_no)` rồi `send(confirmed=true)`. Siết multi-turn: chỉ hành động theo message mới nhất, không gọi lại tool cũ trừ khi user yêu cầu lại.

**Giả thuyết v1** (khớp dòng v1 trong `artifacts/version_log.csv`):

> Bỏ chỉ dẫn xấu + thêm rule clarify / xác nhận send / routing / chỉ xử lý lượt mới nhất sẽ giảm lỗi `missing_info`, `wrong_boundary`, `out_of_scope`.

**Kết quả đo được**

| Suite | Metric | Run |
|---|---|---|
| Base | v0 **0.65** → v1 **0.90** (18/20) | `runs/v1_B_base_openrouter_20261110T185510918902.json` |
| Group | **7/9** (case_accuracy 0.7778) | `runs/v1_B_group_openrouter_20261110T185542663317.json` |

Cả hai run đều `provider_error_cases = 0`, `measured_cases = total_cases`.

**Phân tích FAIL còn lại sau v1**

Base (2 FAIL):

- `R10_missing_handle`: đã gọi `clarify` đúng hướng (hỏi handle), nhưng thiếu `response_type=text`.
- `R12_confirm_before_send`: đã gọi `clarify`, nhưng thiếu `response_type=yes_no` (còn hỏi nội dung thay vì yes/no).

Group (2 FAIL):

- `G01_timeframe_month`: expected `timeframe=month`, got `day` — prompt chỉ map “hôm nay” → `day`, chưa cover “tháng này”.
- `GM03_switch_to_twitter_top`: gọi thừa `lookup` cùng `social_search` (`extra_tool_call`) dù lượt mới nhất chỉ cần Twitter.

Routing/clarify đã đúng hướng nhờ prompt. Phần FAIL còn lại chủ yếu thuộc arg contract / mô tả trong `tools.yaml` — Vũ báo lại và Nguyên dùng làm giả thuyết cho v2/v3.

## 4. Bằng chứng

- File/commit/PR:
  - `ba02a75`: bản đầu cập nhật `system_prompt.md`
  - `425911f`: bản cuối v1 — bỏ xin credentials, siết confirm + multi-turn
  - Dòng v1 trong `artifacts/version_log.csv` (author `quanghuynguyenba`, prompt_hash `8c876c84e53c`)
  - Run: `runs/v1_B_base_openrouter_20261110T185510918902.json`, `runs/v1_B_group_openrouter_20261110T185542663317.json` (Vũ chạy lại trên prompt cuối và thay bản nháp)
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  Mình dùng Cursor để đọc starter prompt, so sánh với yêu cầu lab (bỏ chỉ dẫn xấu, thêm routing/confirm), và chỉnh lại sau feedback tester. Tự kiểm bằng cách đối chiếu `summary` trong run JSON với `version_log`, đọc `failures` / `actual_tool_calls` của từng case FAIL, và chỉ giữ run có `provider_error_cases = 0`.

## 5. Tự đánh giá

- **Học được:** starter “xấu có chủ đích” phá routing như thế nào; rule ngắn + boundary rõ (đừng đoán, đừng gửi chưa xác nhận) quan trọng hơn prompt dài.
- **Làm tốt:** nhảy base +0.25 chỉ bằng prompt; sửa nhanh rủi ro xin credentials sau khi tester báo.
- **Chưa tốt:** chưa siết `response_type` và mapping “tháng này → month” ngay trong prompt (để lại cho `tools.yaml`).
- **Rút ra:** prompt chịu trách nhiệm behavior/boundary; schema và required args nên nằm ở `tools.yaml`.
