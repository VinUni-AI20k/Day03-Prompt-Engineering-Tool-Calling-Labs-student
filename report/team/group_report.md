# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3:

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
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

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed artifact | Hypothesis | case_acc | routing | args | multiturn | Fixed | Regressed | Run file |
|---|---|---|---:|---:|---:|---:|---|---|---|
| v0 | baseline | — | 0.65 | 0.75 | 0.65 | 1.00 | — | — | runs/v0_B_base_openrouter_20261110T175213197182.json |
| v1 | system_prompt.md | Bỏ chỉ dẫn xấu (đoán/gửi luôn/một tool), thêm scope/clarify/confirm | 0.80 | 0.85 | 0.80 | 1.00 | R03, R08, R10, R11, R13, R14 | R01, R04, R05 (hỏi lại quá mức) | runs/v1_B_base_openrouter_20261110T181644444661.json |
| v2 | system_prompt.md | Thu hẹp clarify/confirm: có tên/URL thì gọi tool ngay; chỉ send cần yes_no | 0.95 | 1.00 | 0.95 | 1.00 | R01, R04, R05, R12 | R13 (thiếu topic=news) | runs/v2_B_base_openrouter_20261110T182837689317.json |
| v3 | tools.yaml | Description khi nào dùng/không dùng + quy ước args + boundary send | 0.95 | — | 0.95 | 0.83 | R13 | M06 (gọi thừa social_search sau khi user "bỏ Twitter") | runs/v3_B_base_openrouter_20261110T184559398755.json |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_tool (observed: wrong_arg_value) | `lookup(query="AI news", topic=news, timeframe=day)` | Routing đúng nhưng `query` thêm chữ "news" thay vì chỉ "AI" | v2: tools.yaml quy ước `query` chỉ chứa chủ đề cốt lõi |
| R08_out_of_scope | out_of_scope | `send(text="Nguyên hàm của x^2 là x^3/3 + C…")` | Câu toán ngoài phạm vi nhưng vẫn gọi tool `send` | v1: bỏ "Pick one tool", thêm phạm vi, ngoài phạm vi thì không gọi tool |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Không có account, model đoán Sam Altman theo prompt gốc | v1: bỏ chỉ dẫn đoán account; thiếu handle → `clarify` |
| R11_missing_url | missing_info | `fetch(url="https://example.com/article")` | Bịa URL theo prompt gốc "assume a likely URL" | v1: bỏ chỉ dẫn đó; thiếu URL → `clarify` |
| R12_confirm_before_send | wrong_boundary | `send(text="Bản tin này đã được đăng lên Telegram.")` | Gửi ngay khi chưa xác nhận | v1: trước `send` phải `clarify(response_type=yes_no)` |
| R13_parallel_web_and_tweets | wrong_tool (observed: wrong_arg_value) | `lookup(query="AI", timeframe=day)` + `social_search(query="AI")` | Gọi đủ 2 tool nhưng thiếu `topic=news` | v2: quy ước "tin tức" → `topic=news` |
| R14_out_of_scope_coding | out_of_scope | `send(text="def fibonacci(n): …")` | Yêu cầu code ngoài phạm vi nhưng vẫn gọi `send` | v1: giống R08 |

Run v0: `starter_v0/runs/v0_B_base_openrouter_20261110T175213197182.json` — case_accuracy 0.65 (13/20), routing 0.75, args 0.65, multiturn 1.0, provider_error_cases 0.

Nhận xét: 5/7 lỗi (R08, R10, R11, R12, R14) đến từ chỉ dẫn xấu cố ý trong `system_prompt.md` gốc (đoán thay vì hỏi, gửi không xác nhận, ép gọi một tool). 2/7 lỗi (R03, R13) là sai giá trị args do `tools.yaml` thiếu quy ước `query`/`topic`.
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
