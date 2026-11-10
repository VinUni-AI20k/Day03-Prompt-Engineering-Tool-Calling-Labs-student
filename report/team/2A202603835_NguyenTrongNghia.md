# Báo cáo cá nhân — NguyenTrongNghia-2A202603835

## 1. Thông tin thành viên

- Họ tên: Nguyễn Trọng Nghĩa
- MSSV: 2A202603835
- Email: nghiatrongnguyen2304@gmail.com

## 2. Phần việc phụ trách

- **CP4 — Eval nhóm 10 case**: viết bộ eval của nhóm trong `starter_v0/data/eval_group.json`, chạy `--suite group` bằng provider thật và điền bảng B3 trong `report/team/group_report.md`.

## 3. Đóng góp cụ thể

### 3.1. Thiết kế 10 case (5 single turn + 5 multi turn)

Giữ case G01 (route tới `github_search`) đã có từ nhánh CP3 và viết thêm 9 case. Mỗi case có `failure_type`, `expect` và `metadata.what_it_tests`.

| Case | Loại | Lỗi muốn đo | Expect |
|---|---|---|---|
| G01_github_repository_routing | single | `wrong_tool` | `github_search(query, language="Python", sort="stars", limit=3)` |
| G02_deduplicate_by_url | single | `wrong_tool` | `deduplicate_sources(strategy="url")` |
| G03_policy_area_data_privacy | single | `wrong_arg_value` | `policy(policy_area="data_privacy")` |
| G04_send_pressure_skip_confirm | single | `wrong_boundary` | `clarify(response_type="yes_no")` dù user ép "không cần hỏi lại" |
| G05_github_missing_topic | single | `missing_info` | `clarify(response_type="text")` |
| G06_filter_by_date_range | multi | `wrong_tool` | `filter_by_date(start_date="2026-11-01", end_date="2026-11-10", date_field="published")` |
| G07_compare_sources_fields | multi | `wrong_arg_value` | `compare_sources(fields=["title","published"])` |
| G08_github_language_correction | multi | `wrong_arg_value` | `github_search(language="TypeScript", sort="stars", limit=5)` |
| G09_send_after_confirmation | multi | `wrong_boundary` | `send(confirmed=true)` sau khi user đã đồng ý |
| G10_papers_clarify_then_fill | multi | `missing_info` | `papers(query="diffusion models", max_results=3)` |

Nguyên tắc khi viết case:

- **Phủ tool mới của CP3**: cả 4 tool mới (`github_search`, `deduplicate_sources`, `filter_by_date`, `compare_sources`) đều có ít nhất một case route tới. Đây là điều kiện của C5 và của bonus "≥ 4 tool mới".
- **Phủ phần base chưa đo**: base eval chỉ có một case boundary (R12). Mình thêm G04 (user gây áp lực bỏ bước xác nhận) và G09 (hoàn tất luồng: đã xác nhận thì phải gửi, không hỏi lại).
- **Chỉ kiểm tra arg suy ra được chắc chắn**: `run_eval.py` so sánh args chính xác (chỉ bỏ qua hoa/thường) và coi tool call thừa là FAIL. Vì vậy mình không assert `query` tự do khi user không nói rõ, để case không fail vì cách diễn đạt khác.
- **Multi turn mô phỏng hội thoại thật**: có lượt `assistant` hỏi lại (G09, G10) để kiểm tra agent dùng ngữ cảnh lượt trước; có lượt user sửa lại yêu cầu (G08).

### 3.2. Kiểm tra trước khi chạy

- Kiểm tra schema bằng chính hàm của `run_eval.py` (`load_cases`, `validate_case_failure_types`, `validate_expected_tools`), và kiểm tra mọi arg trong `expect` đều có trong `parameters` của `tools.yaml`.
- `pytest` sau khi thêm case: 97 passed, 14 skipped, 0 failed (contract test vẫn xanh).

### 3.3. Chạy eval nhóm

```bash
python run_eval.py --provider openai --version v3 --suite group --eval-cases data/eval_group.json
```

- Model: OpenAI `gpt-4o-mini`.
- Kết quả: `total_cases=10`, `measured_cases=10`, `provider_error_cases=0` → run hợp lệ.
- `case_accuracy`, `tool_routing_accuracy`, `argument_accuracy`, `multiturn_accuracy` đều = 1.00 (10/10 PASS).
- Mình đọc `tool_results` trong run JSON để xác nhận args thật (không chỉ nhìn PASS/FAIL).

### 3.4. Điền bảng B3

Điền đủ 10 dòng trong B3 của `group_report.md`, kèm link run và ghi chú về hash.

## 4. Bằng chứng

- File/commit/PR:
  - [`starter_v0/data/eval_group.json`](../../starter_v0/data/eval_group.json)
  - [Run group v3](../../starter_v0/runs/v3_B_group_openai_20261110T193821499328.json)
  - [Bảng B3 trong group report](group_report.md)
  - Nhánh `feat/check-point-4`; commit: (bổ sung hash sau khi commit)
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Dùng Claude Code để đọc logic chấm trong `run_eval.py`, soạn nháp các case và điền B3.
  - Tự kiểm tra: validate schema bằng code của `run_eval.py`; chạy `pytest`; chạy eval bằng API thật; đối chiếu từng `actual_tool_calls` và `tool_results` trong run JSON với `expect`.

## 5. Tự đánh giá

- **Làm được**: đủ 10 case đúng cấu trúc 5 + 5, phủ cả 4 tool mới và luồng xác nhận trước khi gửi; run hợp lệ, có bằng chứng trong repo.
- **Hạn chế**:
  - 10/10 PASS nghĩa là bộ case chưa bắt được lỗi nào của bản v3 hiện tại, nên chưa giúp tìm giả thuyết tối ưu mới. Nếu có thêm thời gian sẽ viết case khó hơn (ví dụ yêu cầu mơ hồ giữa `lookup` và `papers`, hoặc vừa cần lọc ngày vừa cần loại trùng).
  - Case chỉ kiểm tra tool và args, không chấm nội dung câu trả lời cuối.
  - G09 PASS nhưng `send` trả lỗi `Missing TELEGRAM_BOT_TOKEN` vì `.env` chưa cấu hình Telegram; run không chứng minh có gửi tin thật.
  - `prompt_hash` của run (`0d8d6477582f`) khác dòng v3 trong `version_log.csv` (`cf429f209691`) chỉ do file được checkout với CRLF trên Windows; nội dung prompt giống v3. `tools_hash` khác vì `tools.yaml` đã thêm 4 tool mới của CP3 sau khi chạy v3.
- **Bài học**: unit test đo code của tool, còn eval đo lựa chọn của model. Eval case nên chỉ kiểm tra những gì user nói rõ; kiểm tra quá chặt thì case fail vì diễn đạt, không phải vì agent sai.
