# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: **DNH**
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: **openrouter / openai/gpt-4o-mini** (lấy từ run JSON v0–v3)

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

```bash
cd starter_v0
pip install -r requirements.txt   # SDK provider; UI dùng stdlib http.server (không thêm package)
python -m ui --provider openrouter --version v3
# mở http://127.0.0.1:8787
```

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel:
> `cloudflared tunnel --url http://127.0.0.1:8787`
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

- **v1 (`system_prompt.md`)**: bỏ chỉ dẫn xấu starter (đoán handle/URL, gửi luôn, một bước); thêm rule `clarify` khi thiếu info, confirm trước `send`, từ chối out-of-scope không gọi tool. Metric 0.65 → 0.85.
- **v2 (`tools.yaml`)**: viết lại mọi description (khi nào dùng/không dùng); bắt buộc `clarify.response_type`; `send` chỉ khi `confirmed=true` sau xác nhận; convention args (`lookup` query ngắn + `topic`/`timeframe`, handle không `@`, `social_search` vs `timeline`). Metric 0.85 → 0.95.
- **v3 (`system_prompt.md`)**: turn đầu của send/post/đăng chỉ được `clarify(response_type="yes_no")`, không hỏi nội dung bằng `text` trước confirm. Metric 0.95 → **1.0** (20/20).
- **Tool mới**: do Đạt phụ trách — chưa merge vào báo cáo này tại thời điểm Nghị chốt v0–v3.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi starter trước khi tối ưu |  | 0.65 | `starter_v0/runs/v0_B_base_openrouter_20261110T181324961249.json` |
| v1 | system_prompt.md | Bỏ đoán/gửi luôn → giảm missing_info, wrong_boundary, out_of_scope | 0.65 | 0.85 | `starter_v0/runs/v1_B_base_openrouter_20261110T184102136031.json` |
| v2 | tools.yaml | Siết declaration (clarify.response_type + send boundary + routing/args) → hết R10–R12 | 0.85 | 0.95 | `starter_v0/runs/v2_B_base_openrouter_20261110T185301286980.json` |
| v3 | system_prompt.md | Turn đầu send/đăng phải clarify yes_no (không text) → R12 PASS | 0.95 | 1.0 | `starter_v0/runs/v3_B_base_openrouter_20261110T185429875666.json` |

Hash/`artifact_version` đầy đủ: `starter_v0/artifacts/version_log.csv`. Mọi run trên có `provider_error_cases=0`, `measured_cases=total_cases=20`.

### B2. Failure Analysis

Nguồn FAIL ban đầu: `starter_v0/runs/v0_B_base_openrouter_20261110T181324961249.json` (v0, `case_accuracy=0.65`, `provider_error_cases=0`, `measured_cases=20/20`).  
Cột **Failure Type** = `result.failure_type`; chi tiết = `result.observed_mismatch` + `result.failures`.  
Cột **Fix** ghi version đã xử lý theo run thật sau đó (v1/v2/v3 đều PASS các case dưới; v3 = 20/20).

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_tool (`observed_mismatch`: wrong_arg_value) | `lookup(query="AI news", topic="news", timeframe="day")` | Expect `query="AI"`; actual `query="AI news"` | v1 prompt + v2 `tools.yaml` convention query ngắn / topic+timeframe → PASS từ v1 |
| R08_out_of_scope | out_of_scope (`observed_mismatch`: unexpected_tool_call) | `send(text=...)` | Expect `no_tool`; actual gọi `send` trả lời tích phân | v1 scope rule → PASS từ v1 |
| R10_missing_handle | missing_info (`observed_mismatch`: missing_tool_call) | `timeline(screenname="sama")` | Expect `clarify`; đoán handle | v1 bắt clarify; v2 bắt `response_type="text"` → PASS từ v2 |
| R11_missing_url | missing_info (`observed_mismatch`: missing_tool_call) | `fetch(url="https://example.com/article")` | Expect `clarify`; bịa URL | v1 + v2 (như R10) → PASS từ v2 |
| R12_confirm_before_send | wrong_boundary (`observed_mismatch`: missing_tool_call) | `send(text="Bản tin này")` | Expect `clarify(yes_no)`; gửi luôn | v1 dừng send; v2 vẫn còn sai `text`; v3 ép yes_no turn đầu → PASS ở v3 |
| R13_parallel_web_and_tweets | wrong_tool (`observed_mismatch`: wrong_arg_value) | `lookup(...)` + `timeline(sama)` | Sai args; thiếu `social_search` | v1/v2 routing social_search vs timeline → PASS từ v1 |
| R14_out_of_scope_coding | out_of_scope (`observed_mismatch`: unexpected_tool_call) | `send(text=...Fibonacci...)` | Expect `no_tool` | v1 scope rule → PASS từ v1 |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
