# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
>
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: `openai` / `gpt-4o-mini` (temperature 0; lấy từ field `provider`, `model` trong run JSON)

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent: tìm tin theo từ khóa hoặc theo tài khoản, đọc nội dung URL, tổng hợp thành digest, và chỉ gửi lên Telegram khi người dùng đã xác nhận.

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

| Tên tool                   | Làm được gì                                             | Tool mới nhóm thêm? |
| -------------------------- | ------------------------------------------------------- | ------------------- |
| clarify                    | hỏi lại người dùng khi thiếu thông tin                  | không               |
| timeline                   | lấy bài đăng gần đây của một tài khoản                  | không               |
| social_search              | tìm bài đăng theo từ khóa (Latest hoặc Top)             | không               |
| lookup                     | tìm trên web (general hoặc news, theo khoảng thời gian) | không               |
| fetch                      | đọc nội dung một URL                                    | không               |
| format                     | trình bày các item đã có thành markdown digest          | không               |
| send                       | gửi text lên Telegram, chỉ khi người dùng đã xác nhận   | không               |
| policy                     | tìm trong tài liệu policy nội bộ                        | không               |
| papers                     | tìm paper trên arXiv                                    | không               |
| paper_text                 | tải PDF arXiv và trích text                             | không               |
| (chờ tên tool của Người 2) | (chờ mô tả)                                             | có                  |

### A3. Câu hỏi mẫu để thử

1. Gần đây @sama đăng gì?
2. Tin mới nhất về OpenAI trong tuần này
3. Tìm các bài đăng mới nhất về AI agents
4. Đọc và tóm tắt https://openai.com/research/
5. Lấy bài đăng của tài khoản đó giúp mình (thiếu tên tài khoản, agent nên hỏi lại)

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
| ------- | ---------------- | ---------- | ------------: | -----------: | -------- |
| v0 | baseline | Đo hành vi starter trước khi tối ưu | – | 0.70 | `runs/v0_B_base_openai_20261110T172625895265.json` |
| v1 | system_prompt.md | Bỏ chỉ dẫn xấu (đoán / gửi ngay / một bước) + thêm rule clarify, xác nhận, ngoài phạm vi, routing → sửa R08 R10 R11 R12 R14 | 0.70 | 0.85 | `runs/v1_B_base_openai_20261110T173219539876.json` |
| v2 | tools.yaml | Viết lại description mọi tool (làm gì / khi nào dùng / khi nào không dùng + convention args), giữ nguyên prompt → sửa M02 (regression v1) và R10 | 0.85 | 0.95 | `runs/v2_B_base_openai_20261110T182235056165.json` |
| v3      |                  |            |               |              |          |

Nhận xét (metric chi tiết lấy từ `summary` của run JSON):

| Version | case_accuracy | tool_routing_accuracy | argument_accuracy | multiturn_accuracy |
|---|---:|---:|---:|---:|
| v0 | 0.70 | 0.75 | 0.70 | 1.00 |
| v1 | 0.85 | 0.90 | 0.85 | 0.83 |
| v2 | 0.95 | 1.00 | 0.95 | 1.00 |

- v1 sửa được 4/6 case FAIL của v0: R08, R11, R13, R14. R10 và R12 vẫn FAIL nhưng đã đổi hành vi: R10 không còn đoán `sama` mà gọi `social_search(query="")`; R12 đã hỏi lại bằng `clarify` nhưng với `response_type="text"` thay vì `"yes_no"`.
- **Regression:** M02 (PASS ở v0) FAIL ở v1. Câu "chỉ tìm robotics thôi, vẫn là tin hôm nay" bị route sang `social_search` thay vì `lookup(topic="news", timeframe="day")`. Mục Routing trong prompt v1 chưa phân biệt "tin tức" (→ `lookup`) với "bài đăng/tweet" (→ `social_search`), và tool description vẫn mơ hồ → giả thuyết cho v2.
- **v1 gồm 2 thay đổi, từ v2 mới tách riêng mỗi version một giả thuyết.** (1) Bỏ các chỉ dẫn xấu của starter (đoán thay vì hỏi, gửi không xác nhận, ép một bước) và thay bằng rule clarify / xác nhận / ngoài phạm vi. (2) Thêm mục Routing (tool nào cho loại yêu cầu nào). Vì gộp hai thay đổi nên không tách được case nào do thay đổi nào sửa; ví dụ R13 PASS nhiều khả năng nhờ thay đổi (2), còn regression M02 cũng có thể do (2).

- **v2** (chỉ sửa `tools.yaml`, `prompt_hash` giữ nguyên `0272985012ee`, `tools_hash` `41a2894f8ad1` → `cd1ae0336fb5`): sửa được M02 và R10, không làm vỡ case nào (19/20).
  - M02: `lookup(query="robotics", topic="news", timeframe="day")` → PASS. Description `lookup` nói rõ "tin tức → lookup, kể cả khi lượt sau chỉ đổi chủ đề" và `social_search` nói "hỏi tin mà không nhắc Twitter thì không dùng".
  - R10: `clarify(response_type="text")` hỏi tài khoản → PASS, thay cho `social_search(query="")` ở v1. Description `social_search`/`timeline` cấm gọi với tham số rỗng.
  - R12 vẫn FAIL: model gọi `clarify(question="Nội dung bạn muốn đăng lên Telegram là gì?", response_type="text")`. Description `send` đã nói phải xác nhận yes_no, nhưng vì câu "bản tin này" không kèm nội dung nên model hỏi nội dung trước. Mô tả trong tool chưa đủ ép hành vi này → giả thuyết v3: thêm rule trong system prompt "mọi yêu cầu gửi/đăng → gọi ngay `clarify(response_type="yes_no")`, không hỏi nội dung bằng text".

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

Run v0: `starter_v0/runs/v0_B_base_openai_20261110T172625895265.json` (gpt-4o-mini, 14/20 PASS, provider_error_cases = 0).

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `send(text="Nguyên hàm của x^2 là …")` | Câu toán ngoài phạm vi nhưng model vẫn gọi tool, lại còn gọi `send` vì prompt v0 bảo "gửi luôn" | v1: rule ngoài phạm vi → không gọi tool; bỏ chỉ dẫn "send ngay" |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Không có handle → model tự đoán `sama` đúng như prompt v0 xúi ("pick Sam Altman") | v1: bỏ chỉ dẫn đoán; thiếu handle → `clarify(response_type="text")` |
| R11_missing_url | missing_info | `fetch(url="https://example.com/article")` | Nói "bài này" nhưng không có link → model bịa URL | v1: không bịa URL; thiếu link → `clarify` |
| R12_confirm_before_send | wrong_boundary | `send(text="Bản tin này đã được đăng…")` | Gửi ngay không xác nhận (tool chặn vì `confirmed` = false) | v1: hành động gửi → `clarify(response_type="yes_no")` trước (v1 đã hỏi lại nhưng dùng `response_type="text"`, vẫn FAIL). *Kế hoạch, chưa làm:* description `send` nêu rõ chỉ `confirmed=true` sau khi user đồng ý |
| R13_parallel_web_and_tweets | wrong_tool (observed: wrong_arg_value) | `lookup(query="AI news", timeframe="day")`, `social_search(query="AI")` | Route đúng 2 tool nhưng `lookup` thiếu `topic="news"` và query bị thêm chữ "news" | v1 (gián tiếp nhờ rule routing "news → lookup"): run v1 gọi `lookup(query="AI", topic="news", timeframe="day")` → PASS |
| R14_out_of_scope_coding | out_of_scope | `send(text="def fibonacci…")` | Yêu cầu viết code ngoài phạm vi nhưng model vẫn gọi `send` | v1: rule ngoài phạm vi |

Nhận xét: 5/6 lỗi do chính các chỉ dẫn xấu trong system prompt v0 (đoán thay vì hỏi, gửi không xác nhận, làm trong một bước). Lỗi còn lại (R13) là do tool declaration không nói rõ convention args.

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
| ------- | ------------- | ---------------------- | ------ |
|         |               |                        |        |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
| ---- | ------------ | ---------- | ---------------- | ------- |
|      |              |            |                  |         |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item                               | Evidence File              | What Worked | Risk / Guardrail |
| ---------------------------------- | -------------------------- | ----------- | ---------------- |
| Tool mới (`tools/<tên>/`)          |                            |             |                  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |             |                  |
| UI (lệnh chạy + link dùng thử)     |                            |             |                  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus                                        | Evidence File   | What Worked | Risk / Guardrail |
| -------------------------------------------- | --------------- | ----------- | ---------------- |
| Small Local Model                            | xem B7          |             |                  |
| Hơn 3 tool mới (≥ 4)                         |                 |             |                  |
| `send` gửi thật lên Telegram sau xác nhận    | transcript      |             |                  |
| Test challenge (0 skipped / regression test) | `pytest` output |             |                  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version    | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
| ---------- | ---------------- | ------------ | ------------- | ------------ | -------- | --------- | -------- |
| v3         | (cloud)          | v3           |               |              |          |           |          |
| v3-<model> | (ollama)         | v3           |               |              |          |           |          |
| v3-<model> | (ollama)         | v3           |               |              |          |           |          |
| v4-local   |                  |              |               |              |          |           |          |
| v5-local   |                  |              |               |              |          |           |          |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern                               | Count | Example Case | Fix Tried | Helped? |
| --------------------------------------------- | ----- | ------------ | --------- | ------- |
| wrong / hallucinated tool                     |       |              |           |         |
| invalid JSON args (`_invalid_json_arguments`) |       |              |           |         |
| no tool call / answered directly              |       |              |           |         |
| missed `clarify`                              |       |              |           |         |
| repeated / unnecessary calls                  |       |              |           |         |

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
