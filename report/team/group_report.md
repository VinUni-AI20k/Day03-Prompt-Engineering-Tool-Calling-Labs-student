# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: model `gpt-4o-mini` cho mọi version. v0 gọi qua OpenRouter (`openai/gpt-4o-mini`); từ v1 gọi trực tiếp qua provider `openai` (`gpt-4o-mini`), cùng model nên metric so sánh được.

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

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (starter chưa sửa) | Đo hành vi chưa tối ưu trước khi sửa | – | case 0.65 · routing 0.75 · args 0.65 · multiturn 1.00 | [v0_B_base_openrouter_20261110T174226406183.json](../../starter_v0/runs/v0_B_base_openrouter_20261110T174226406183.json) |
| v1 | `system_prompt.md` | Prompt starter dặn đoán account/URL, gửi không cần xác nhận và ép gọi đúng 1 tool → gây 5/7 FAIL (R08, R10, R11, R12, R14). Bỏ các chỉ dẫn này, thêm rule `clarify` khi thiếu info, xác nhận `yes_no` trước `send`, từ chối ngoài phạm vi, cho phép nhiều tool/lượt thì các case đó PASS. | case 0.65 · routing 0.75 · args 0.65 · multiturn 1.00 | case 0.95 · routing 1.00 · args 0.95 · multiturn 1.00 | [v1_B_base_openai_20261110T182945282365.json](../../starter_v0/runs/v1_B_base_openai_20261110T182945282365.json) |
| v2 | `tools.yaml` | R12 FAIL vì description `send`/`clarify` không nói rõ yêu cầu gửi/đăng luôn cần `clarify(response_type="yes_no")` kể cả khi nội dung chưa rõ. Viết rõ boundary này (kèm viết lại description mọi tool theo làm gì / khi nào dùng / không dùng) thì R12 PASS. **Kết quả: giả thuyết không đúng.** R12 vẫn FAIL: agent vẫn hỏi nội dung bằng `text`. M06 bị regression: user nói "Bỏ Twitter, chuyển sang web" nhưng agent gọi thêm `social_search` bên cạnh `lookup` (v1 chỉ gọi `lookup`). | case 0.95 · routing 1.00 · args 0.95 · multiturn 1.00 | case 0.90 · routing 0.95 · args 0.90 · multiturn 0.83 | [v2_B_base_openai_20261110T190148454639.json](../../starter_v0/runs/v2_B_base_openai_20261110T190148454639.json) |
| v3 |  |  |  |  |  |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

Run v0: [`v0_B_base_openrouter_20261110T174226406183.json`](../../starter_v0/runs/v0_B_base_openrouter_20261110T174226406183.json) · artifact `v0+peb1c8179815b+te69bc53ed884` · 20/20 case đo được, `provider_error_cases = 0` → run hợp lệ. 13/20 PASS, 7 FAIL.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | `wrong_tool` (observed: `wrong_arg_value`) | `lookup(query="AI news", topic="news", timeframe="day")` | Chọn đúng tool và đúng `topic`/`timeframe`, nhưng nhét chữ "news" vào `query` (expected `"AI"`). Description của `lookup` không nói `query` chỉ chứa từ khoá cốt lõi. | `tools.yaml`: mô tả `query` = chủ đề cốt lõi, không thêm "news/tin tức" vì đã có `topic=news`. **Kết quả:** đã PASS ở v1 dù chưa sửa `tools.yaml`. Có thể nhờ prompt mới bỏ câu ép gọi một tool và có routing rõ hơn. |
| R08_out_of_scope | `out_of_scope` (observed: `unexpected_tool_call`) | `send(text="Nguyên hàm của x^2 là x³/3 + C ...")` | Câu toán ngoài phạm vi research nhưng agent vẫn gọi tool, lại còn gọi `send` không có xác nhận. Nguyên nhân: prompt ép "Always finish in a single step. Pick one tool". | `system_prompt.md`: bỏ câu ép gọi tool; thêm rule: yêu cầu ngoài phạm vi research → từ chối lịch sự, không gọi tool. **Kết quả:** PASS ở v1. |
| R10_missing_handle | `missing_info` (observed: `missing_tool_call`) | `timeline(screenname="sama")` | Không rõ tài khoản nào nhưng agent tự đoán Sam Altman thay vì hỏi lại. Nguyên nhân: prompt dặn "pick a well-known account like Sam Altman". | `system_prompt.md`: bỏ chỉ dẫn đoán account; thêm rule: thiếu handle → `clarify(response_type="text")`. **Kết quả:** PASS ở v1. |
| R11_missing_url | `missing_info` (observed: `missing_tool_call`) | `fetch(url="https://example.com/article")` | "Bài viết này" không có URL nhưng agent bịa URL. Nguyên nhân: prompt dặn "assume a likely URL and read it". | `system_prompt.md`: bỏ chỉ dẫn đoán URL; thêm rule: thiếu URL → `clarify`. **Kết quả:** PASS ở v1. |
| R12_confirm_before_send | `wrong_boundary` (observed: `missing_tool_call`) | `send(text="Bản tin này")` | Gửi lên Telegram ngay, không xin xác nhận, nội dung còn rỗng nghĩa. Nguyên nhân: prompt dặn "just go ahead and do it"; description `send` không nêu boundary `confirmed`. | `system_prompt.md`: trước khi gửi phải `clarify(response_type="yes_no")`; `tools.yaml`: `send` chỉ gọi với `confirmed=true` sau khi user đồng ý. **Kết quả:** v1 vẫn FAIL. Agent không còn gửi ngay, nhưng gọi `clarify(response_type="text")` để hỏi nội dung, thay vì `yes_no` để xác nhận. Chuyển sang giả thuyết v2. |
| R13_parallel_web_and_tweets | `wrong_tool` (observed: `wrong_arg_value`) | `lookup(query="AI news", timeframe="day")` + `social_search(query="AI", search_type="Latest")` | Routing đúng cả 2 tool, nhưng `lookup` thiếu `topic="news"` và `query` thừa "news". Không có convention "tin/tin tức/hôm nay → `topic=news`". | `tools.yaml`: nêu rõ convention `topic=news` cho tin tức, `timeframe=day` cho "hôm nay"; cùng fix `query` như R03. **Kết quả:** đã PASS ở v1 dù chưa sửa `tools.yaml` (cùng nhận định với R03). |
| R14_out_of_scope_coding | `out_of_scope` (observed: `unexpected_tool_call`) | `send(text="...def fibonacci(n)...")` | Viết code ngoài phạm vi và dùng `send` để trả lời. Cùng nguyên nhân với R08. | Cùng fix với R08. **Kết quả:** PASS ở v1. |

**Gom nhóm nguyên nhân (định hướng cho v1–v3):**

1. **5/7 case FAIL** (R08, R10, R11, R12, R14) do các chỉ dẫn xấu cố ý trong `system_prompt.md`: đoán thay vì hỏi, gửi không cần xác nhận, ép gọi đúng một tool. Đây là giả thuyết mạnh nhất cho **v1**: sửa `system_prompt.md`.
2. **2/7 case FAIL** (R03, R13) là lỗi convention args của `lookup` (`query` thừa "news", thiếu `topic=news`). Dự đoán ban đầu: cần sửa `tools.yaml`. **Thực tế:** cả hai đã PASS ở v1 nhờ sửa prompt, nên v2 không cần nhắm vào 2 case này.
3. `multiturn_accuracy = 1.0`: cả 6 case multi-turn (M01–M06) đều PASS ở v0. Cần theo dõi để v1–v3 không làm tụt chỉ số này (regression).
4. **Sau v1 còn R12.** Agent hiểu "bản tin này" là thiếu nội dung nên hỏi bằng `text` thay vì xin xác nhận `yes_no`. Giả thuyết cho **v2**: description `send`/`clarify` trong `tools.yaml` chưa nói rõ yêu cầu gửi/đăng luôn cần bước `clarify(response_type="yes_no")`, kể cả khi nội dung chưa rõ; viết rõ boundary này thì R12 PASS.

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
