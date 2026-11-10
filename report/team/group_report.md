# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
>
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: anbatocom (lớp L3B)
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: `openai` / `gpt-4o-mini` (temperature 0; lấy từ field `provider`, `model` trong run JSON)

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent: tìm tin theo từ khóa hoặc theo tài khoản, đọc nội dung URL, tổng hợp thành digest, và chỉ gửi lên Telegram khi người dùng đã xác nhận.

**Cách chạy UI:**

```bash
cd starter_v0
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt    # đã có streamlit>=1.67.0
streamlit run app.py               # → http://localhost:8501
```

Provider mặc định `openai` (cần `OPENAI_API_KEY` trong `.env`); đổi bằng biến môi trường, ví dụ `UI_PROVIDER=openrouter streamlit run app.py`. Code UI: `starter_v0/app.py`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: https://cnet-francis-catalog-encountered.trycloudflare.com
>

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
| extract_keywords           | trích các từ khóa lặp nhiều nhất từ đoạn text có sẵn (chạy local, không cần key) | có                  |

### A3. Câu hỏi mẫu để thử

1. Gần đây @sama đăng gì?
2. Tin mới nhất về OpenAI trong tuần này
3. Tìm các bài đăng mới nhất về AI agents
4. Đọc và tóm tắt https://openai.com/research/
5. Lấy bài đăng của tài khoản đó giúp mình (thiếu tên tài khoản, agent nên hỏi lại)
6. Dán một đoạn văn rồi hỏi: "Lấy 3 từ khóa chính của đoạn trên" (tool mới `extract_keywords`)
7. Đăng bản tin này lên Telegram (agent phải hỏi xác nhận yes/no trước, không tự gửi)

## 3. Giải pháp

**`system_prompt.md`** (v1, v3):
- Bỏ 3 chỉ dẫn xấu của starter: "đoán thay vì hỏi" (chọn bừa Sam Altman, bịa URL), "gửi/đăng ngay", "chỉ một tool, một bước".
- 4 core rule: (1) thiếu handle/URL → `clarify(response_type="text")`, không đoán; (2) mọi yêu cầu gửi/đăng → việc đầu tiên luôn là `clarify(response_type="yes_no")`, chỉ `send(confirmed=true)` sau khi user trả lời yes ở lượt sau, user hủy → không gọi tool (v3 siết rule này); (3) ngoài phạm vi research (toán, viết code, chit-chat) → không gọi tool; (4) cần nhiều nguồn thì gọi nhiều tool cùng lúc.
- Mục Routing: account → `timeline`, chủ đề/từ khóa trên mạng xã hội → `social_search`, web/tin tức → `lookup`, URL → `fetch`, thiếu thông tin → `clarify`, digest → `format`, trích từ khóa → `extract_keywords` (v3).

**`tools.yaml`** (v2, v3):
- Mỗi tool có description 3 phần: làm gì / **khi nào dùng** / **khi nào không dùng**.
- Convention args ghi trong description của parameter: `screenname` không có `@`; tin tức → `lookup(topic="news")`, "hôm nay" → `timeframe="day"`, query giữ nguyên chủ đề (không thêm chữ "news"); `social_search.search_type` = `Top` khi "nổi bật/phổ biến", `Latest` khi "mới nhất"; không gọi `timeline`/`social_search` với tham số rỗng.
- `send`: chỉ gửi khi user đã xác nhận rõ, `confirmed=true` chỉ đặt sau câu trả lời yes.
- Khai báo tool mới `extract_keywords` (v3).

**Tool mới `extract_keywords`** (`starter_v0/tools/keywords/`, Người 2): trích các từ khóa lặp nhiều nhất từ đoạn text user dán hoặc tool khác đã trả về, chạy local, không cần API key. Args: `text` (bắt buộc, không rỗng), `max_keywords` (số nguyên 1–20, mặc định 5). Không search web, không đọc URL. Agent gọi khi user xin "từ khóa / chủ đề chính" của một đoạn text đã có trong hội thoại (eval GM05). Input xấu (text rỗng, sai kiểu, ngoài khoảng) → trả error dict, không raise.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
| ------- | ---------------- | ---------- | ------------: | -----------: | -------- |
| v0 | baseline | Đo hành vi starter trước khi tối ưu | – | 0.70 | `runs/v0_B_base_openai_20261110T172625895265.json` |
| v1 | system_prompt.md | Bỏ chỉ dẫn xấu (đoán / gửi ngay / một bước) + thêm rule clarify, xác nhận, ngoài phạm vi, routing → sửa R08 R10 R11 R12 R14 | 0.70 | 0.85 | `runs/v1_B_base_openai_20261110T173219539876.json` |
| v2 | tools.yaml | Viết lại description mọi tool (làm gì / khi nào dùng / khi nào không dùng + convention args), giữ nguyên prompt → sửa M02 (regression v1) và R10 | 0.85 | 0.95 | `runs/v2_B_base_openai_20261110T182235056165.json` |
| v3 | system_prompt.md + tools.yaml (2 thay đổi) | Rule "gửi/đăng → việc đầu tiên luôn là `clarify(yes_no)`" sửa R12 + khai báo tool mới `extract_keywords` | 0.95 | 0.95 | `runs/v3_B_base_openai_20261110T194428881251.json` (group: `runs/v3_B_group_openai_20261110T194452423053.json`) |

Nhận xét (metric chi tiết lấy từ `summary` của run JSON):

| Version | case_accuracy | tool_routing_accuracy | argument_accuracy | multiturn_accuracy |
|---|---:|---:|---:|---:|
| v0 | 0.70 | 0.75 | 0.70 | 1.00 |
| v1 | 0.85 | 0.90 | 0.85 | 0.83 |
| v2 | 0.95 | 1.00 | 0.95 | 1.00 |
| v3 | 0.95 | 0.95 | 0.95 | 1.00 |
| v3 (suite group, 10 case) | 1.00 | 1.00 | 1.00 | 1.00 |

- v1 sửa được 4/6 case FAIL của v0: R08, R11, R13, R14. R10 và R12 vẫn FAIL nhưng đã đổi hành vi: R10 không còn đoán `sama` mà gọi `social_search(query="")`; R12 đã hỏi lại bằng `clarify` nhưng với `response_type="text"` thay vì `"yes_no"`.
- **Regression:** M02 (PASS ở v0) FAIL ở v1. Câu "chỉ tìm robotics thôi, vẫn là tin hôm nay" bị route sang `social_search` thay vì `lookup(topic="news", timeframe="day")`. Mục Routing trong prompt v1 chưa phân biệt "tin tức" (→ `lookup`) với "bài đăng/tweet" (→ `social_search`), và tool description vẫn mơ hồ → giả thuyết cho v2.
- **v1 gồm 2 thay đổi, từ v2 mới tách riêng mỗi version một giả thuyết.** (1) Bỏ các chỉ dẫn xấu của starter (đoán thay vì hỏi, gửi không xác nhận, ép một bước) và thay bằng rule clarify / xác nhận / ngoài phạm vi. (2) Thêm mục Routing (tool nào cho loại yêu cầu nào). Vì gộp hai thay đổi nên không tách được case nào do thay đổi nào sửa; ví dụ R13 PASS nhiều khả năng nhờ thay đổi (2), còn regression M02 cũng có thể do (2).

- **v2** (chỉ sửa `tools.yaml`, `prompt_hash` giữ nguyên `0272985012ee`, `tools_hash` `41a2894f8ad1` → `cd1ae0336fb5`): sửa được M02 và R10, không làm vỡ case nào (19/20).
  - M02: `lookup(query="robotics", topic="news", timeframe="day")` → PASS. Description `lookup` nói rõ "tin tức → lookup, kể cả khi lượt sau chỉ đổi chủ đề" và `social_search` nói "hỏi tin mà không nhắc Twitter thì không dùng".
  - R10: `clarify(response_type="text")` hỏi tài khoản → PASS, thay cho `social_search(query="")` ở v1. Description `social_search`/`timeline` cấm gọi với tham số rỗng.
  - R12 vẫn FAIL: model gọi `clarify(question="Nội dung bạn muốn đăng lên Telegram là gì?", response_type="text")`. Description `send` đã nói phải xác nhận yes_no, nhưng vì câu "bản tin này" không kèm nội dung nên model hỏi nội dung trước. Mô tả trong tool chưa đủ ép hành vi này → giả thuyết v3: thêm rule trong system prompt "mọi yêu cầu gửi/đăng → gọi ngay `clarify(response_type="yes_no")`, không hỏi nội dung bằng text".

- **v3** gồm **2 thay đổi** (giống v1, ghi rõ để không lẫn): (1) `system_prompt.md` — rule 2 bắt buộc mọi yêu cầu gửi/đăng phải gọi `clarify(response_type="yes_no")` đầu tiên, không dùng `text`, kể cả khi nội dung mơ hồ; (2) `tools.yaml` + 1 dòng Routing — khai báo tool mới `extract_keywords` (Người 2). Hash: prompt `0272985012ee` → `708eace3a436`, tools `cd1ae0336fb5` → `dd2c48e0c860`. Base vẫn 19/20 (0.95) nhưng **case FAIL đổi chỗ**:
  - R12 **sửa được**: `clarify(question="Bạn xác nhận đăng bản tin này lên Telegram chứ?", response_type="yes_no")` → PASS. Chứng minh boundary cần rule trong prompt, description `send` ở v2 không đủ.
  - R10 **regression** (PASS ở v2): "Tóm tắt 5 tweet mới nhất" → `social_search(query="AI", limit=5)`. Model tự bịa chủ đề "AI" (nhiều khả năng lấy từ câu mở đầu prompt "research assistant for AI/tech news") thay vì hỏi lại. R10 đã dao động qua cả 3 version (v1 query rỗng → v2 clarify → v3 query "AI"), cho thấy case thiếu thông tin này nhạy với mọi thay đổi prompt và rule 1 chỉ nói "thiếu handle", chưa nói "thiếu cả tài khoản lẫn chủ đề thì không được tự chọn chủ đề".
  - Tool mới: suite group 10/10, GM05 gọi đúng `extract_keywords(text=<đoạn đã dán>, max_keywords=3)`. Thêm tool không làm vỡ case routing nào của base.
  - Giả thuyết nếu có v4: thêm vào rule 1 "yêu cầu tweet/bài đăng mà không có tài khoản và không có chủ đề → `clarify`, không tự chọn chủ đề (kể cả 'AI')".

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

Nhận xét: 5/6 lỗi (R08, R10, R11, R12, R14) trùng khớp với các chỉ dẫn xấu trong system prompt v0 (đoán thay vì hỏi, gửi không xác nhận, làm trong một bước). R13 ban đầu nhóm dự đoán là lỗi convention args của tool declaration (để sửa ở v2), nhưng thực tế R13 đã PASS ngay ở v1 dù `tools.yaml` chưa đổi. Như vậy nguyên nhân thật nhiều khả năng là chỉ dẫn "single step" của prompt v0 hoặc dao động ngẫu nhiên của model; nhóm không đủ bằng chứng để khẳng định là thay đổi nào trong v1 đã sửa nó.

Trạng thái các case FAIL của v0 qua các version (từ run JSON):

| Case | v0 | v1 | v2 | v3 |
|---|---|---|---|---|
| R08_out_of_scope | FAIL | PASS | PASS | PASS |
| R10_missing_handle | FAIL (`timeline("sama")`) | FAIL (`social_search(query="")`) | PASS | FAIL (`social_search(query="AI")`) |
| R11_missing_url | FAIL | PASS | PASS | PASS |
| R12_confirm_before_send | FAIL (`send`) | FAIL (`clarify` text) | FAIL (`clarify` text) | PASS |
| R13_parallel_web_and_tweets | FAIL | PASS | PASS | PASS |
| R14_out_of_scope_coding | FAIL | PASS | PASS | PASS |
| M02_carryover_timeframe | PASS | FAIL (`social_search`) | PASS | PASS |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

Run: `starter_v0/runs/v3_B_group_openai_20261110T194452423053.json` (v3, gpt-4o-mini, 10/10 PASS, provider_error_cases = 0). 5 single turn + 5 multi turn; GM05 kiểm tra route tới tool mới `extract_keywords`.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
| ------- | ------------- | ---------------------- | ------ |
| G01_news_last_day (single) | Tin tức trong 24 giờ → lookup với topic=news và timeframe=day, không để mặc định week. | `lookup(topic="news", timeframe="day")` | PASS |
| G02_social_top (single) | 'Nổi bật nhất' → social_search với search_type=Top thay vì mặc định Latest. | `social_search(search_type="Top")` | PASS |
| G03_no_tool_knowledge (single) | Câu hỏi kiến thức đơn giản không cần research → không gọi tool nào. | không gọi tool | PASS |
| G04_missing_url (single) | Không có URL → phải hỏi lại bằng clarify, không đoán URL và không gọi fetch. | `clarify()` | PASS |
| G05_send_needs_confirmation (single) | Yêu cầu gửi chưa được xác nhận → hỏi xác nhận bằng clarify, không gọi send. | `clarify()` | PASS |
| GM01_news_missing_topic_then_month (multi) | 3 lượt: chủ đề đến từ lượt 2, khoảng thời gian từ lượt 3 → lookup với topic=news và timeframe=month. | `lookup(topic="news", timeframe="month")` | PASS |
| GM02_social_latest_limit (multi) | Lượt 2 đổi số lượng → social_search với search_type=Latest và limit=10. | `social_search(search_type="Latest", limit=10)` | PASS |
| GM03_send_after_confirm (multi) | Người dùng đã xác nhận ở lượt 2 → gọi send với confirmed=true. | `send(confirmed=true)` | PASS |
| GM04_send_cancelled (multi) | Người dùng hủy ở lượt 2 → không gọi tool nào, đặc biệt không gọi send. | không gọi tool | PASS |
| GM05_keywords_from_pasted_text (multi) | Text đã có ở lượt 1, lượt 2 xin từ khóa → route tới tool mới extract_keywords với max_keywords=3 (số nguyên), không gọi lookup/social_search và không clarify. | `extract_keywords(max_keywords=3)` | PASS |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

Transcript 1: `starter_v0/transcripts/v3_openai_20261110T212456713621.transcript.json` (`python chat.py --provider openai --version v3`, artifact `v3+p708eace3a436+tdd2c48e0c860`).

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
| ---- | ------------ | ---------- | ---------------- | ------- |
| 1 | Tin mới nhất về OpenAI tuần này | `lookup(query="OpenAI", topic="news", timeframe="week")` | v3 | Đúng: route `lookup` + `topic="news"` theo convention v2; trả 5 tin (Reuters, CNBC, openai.com…) |
| 2 | Lấy bài đăng gần đây của tài khoản đó giúp mình | `timeline(screenname="openai", limit=5)` | v3 | Agent hiểu "tài khoản đó" = OpenAI (chủ đề lượt 1) nên không hỏi lại. Hợp lý theo ngữ cảnh, nhưng là suy diễn chứ không phải user nói rõ |
| 3 | sama | `timeline(screenname="sama", limit=5)` | v3 | Đúng: handle không có `@`, trả 5 bài của @sama |
| 4 | Đăng bản tin này lên Telegram | `clarify(question="Bạn xác nhận đăng bản tin này lên Telegram chứ?", response_type="yes_no")` | v3 | Đúng boundary: hỏi xác nhận yes/no, **không** gọi `send` (rule 2 của prompt v3, cùng hành vi với case R12) |

Transcript 2 (phiên mới, không có ngữ cảnh): `starter_v0/transcripts/v3_openai_20261110T212838000877.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
| ---- | ------------ | ---------- | ---------------- | ------- |
| 1 | Lấy bài đăng gần đây của tài khoản đó giúp mình. | (không gọi tool) | v3 | Thiếu tài khoản → agent **hỏi lại** "Bạn vui lòng cung cấp tên tài khoản…", không đoán. Nhưng hỏi bằng text trực tiếp, **không** qua tool `clarify` như rule 1 yêu cầu |
| 2 | sama | `timeline(screenname="sama", limit=5)` | v3 | Đúng: bổ sung thông tin → gọi `timeline` với handle không có `@`, trả 5 bài |

Nhận xét: lượt 2 của transcript 1 cho thấy giới hạn của rule "thiếu thông tin → clarify": khi hội thoại đã có một thực thể (OpenAI), agent tự gán "tài khoản đó" cho thực thể này thay vì hỏi lại. Đây là loại hành vi eval tự động khó chấm đúng/sai, cần review thủ công. Lượt 1 của transcript 2 thì hành vi đúng (hỏi lại, không đoán) nhưng sai kênh: chat (không ép `tool_choice`) cho phép model trả text thay vì gọi `clarify`, trong khi eval ép `tool_choice="required"` nên luôn có tool call. Đây là khác biệt giữa eval và dùng thật.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item                               | Evidence File              | What Worked | Risk / Guardrail |
| ---------------------------------- | -------------------------- | ----------- | ---------------- |
| Tool mới (`tools/<tên>/`)          | `starter_v0/tools/keywords/tool.py`, `TOOL.md`; đăng ký trong `tools/__init__.py` (`TOOL_FUNCTIONS["extract_keywords"]`) và `artifacts/tools.yaml` | Chạy local, xếp hạng từ khóa theo tần suất rồi thứ tự xuất hiện, bỏ stop word Anh/Việt. Eval GM05 (suite group v3) route đúng `extract_keywords(max_keywords=3)` | Validate input: text rỗng/không phải string, `max_keywords` không phải int (kể cả bool) hoặc ngoài 1–20 → trả error dict. Mọi exception đều bọc thành `{"tool","error","message"}`, không raise |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py`: `test_extract_keywords_returns_ranked_keywords`, `test_extract_keywords_rejects_empty_text_from_model`, `test_extract_keywords_internal_failure_returns_error_dict`; `pytest` (21:31, 10/11/2026): **70 passed, 14 skipped, 0 failed** (84 test: 60 contract + 7 example + 17 trong `test_tools_todo.py`, trong đó 3 test `extract_keywords` PASS và 14 stub TODO của tool có sẵn còn skipped) | 3 test: happy path (thứ tự + count), input xấu từ model (text rỗng), nhánh lỗi nội bộ (tokenizer raise → error dict) | Test offline, không gọi mạng (`conftest.py` chặn HTTP) |
| UI (lệnh chạy + link dùng thử)     | `starter_v0/app.py`; lệnh chạy ở mục A1; link Cloudflare tunnel ở A1 | Streamlit chat gọi cùng agent, provider mặc định `openai` | Link `trycloudflare.com` là tạm thời, chỉ sống khi máy chạy `streamlit` + `cloudflared` |

Tool unit tests: 3 test cho tool mới. Ví dụ lỗi unit test bắt được mà eval không bắt được: eval GM05 chỉ kiểm tra model **gọi** `extract_keywords(max_keywords=3)` là PASS. Nếu tokenizer của tool bị lỗi và raise exception, eval vẫn PASS vì chỉ chấm tool call, còn user sẽ nhận lỗi. Test `test_extract_keywords_internal_failure_returns_error_dict` bắt đúng trường hợp này và đảm bảo tool trả error dict để agent xử lý tiếp được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus                                        | Evidence File   | What Worked | Risk / Guardrail |
| -------------------------------------------- | --------------- | ----------- | ---------------- |
| Small Local Model                            | xem B7          |             |                  |
| Hơn 3 tool mới (≥ 4)                         |                 |             |                  |
| `send` gửi thật lên Telegram sau xác nhận    | transcript      |             |                  |
| Test challenge (0 skipped / regression test) | `pytest` output | Chưa làm: các stub TODO của tool có sẵn vẫn `skipped` | – |

Test challenge: nhóm chưa làm (không tìm/sửa bug trong tool có sẵn). Các bonus khác (local model, ≥ 4 tool mới, gửi Telegram thật) cũng chưa làm.

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

- **Đổi provider:** README mặc định OpenRouter, nhóm dùng OpenAI (`gpt-4o-mini`). Ban đầu key OpenAI bị điền vào biến `OPENROUTER_API_KEY` → sửa thành `OPENAI_API_KEY`, chạy `--provider openai`. Cả v0–v3 dùng cùng provider/model để so sánh được.
- **Lệnh smoke test của tool báo `KeyError: 'items'`:** lệnh `python -c "from tools import TOOL_FUNCTIONS ..."` không nạp `.env` (chỉ `run_eval.py`/`chat.py` gọi `load_lab_env`), nên tool trả error dict thiếu key. Xử lý: gọi `env_loader.load_lab_env()` trước khi test → cả `lookup`, `fetch`, `timeline` đều trả kết quả.
- **macOS không có lệnh `python`:** dùng `python3`, tạo `.venv` rồi `pip install -r requirements.txt`.
- **Git:** nhiều người cùng sửa `group_report.md` → push bị reject (non-fast-forward) và conflict khi `pull --rebase`. Xử lý: commit theo từng version, `pull --rebase` trước khi push, gỡ conflict giữ nội dung của cả hai bên; mỗi thành viên làm trên nhánh riêng rồi merge bằng pull request.
- **Kết quả eval dao động giữa các version:** R10 đổi qua lại PASS/FAIL ở v1–v3 dù không sửa trực tiếp phần liên quan (xem B1). Nhóm chỉ chạy mỗi version 1 lần nên không tách được ảnh hưởng của thay đổi khỏi dao động của model.
- Không có run nào bị lỗi provider: mọi run trong `starter_v0/runs/` đều có `provider_error_cases == 0` và `measured_cases == total_cases`.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- **Fix thuộc `system_prompt.md`:** hành vi và boundary áp dụng cho mọi tool: không đoán khi thiếu thông tin (R10, R11), từ chối ngoài phạm vi (R08, R14), xác nhận yes/no trước khi gửi (R12). Bằng chứng rõ nhất là R12: description `send` ở v2 đã ghi phải xác nhận nhưng vẫn FAIL, chỉ PASS khi rule vào prompt ở v3.
- **Fix thuộc `tools.yaml`:** chọn tool nào và điền args thế nào: phân biệt "tin tức" (`lookup` + `topic="news"`) với "bài đăng" (`social_search`), không gọi tool với tham số rỗng. Bằng chứng: v2 chỉ đổi `tools.yaml` (prompt hash giữ nguyên) mà sửa được M02 và R10, routing accuracy 0.90 → 1.00.
- **Cần review thủ công:** (1) case `no_tool` chỉ kiểm tra "không gọi tool", không kiểm tra câu trả lời text có thật sự từ chối lịch sự hay trả lời bừa; (2) eval chỉ chấm tham số được liệt kê, nên `clarify` hỏi sai câu hoặc `send` với nội dung bịa vẫn có thể PASS; (3) chất lượng kết quả tool thật (bài web có liên quan không, digest có đúng không) eval không đo; (4) dao động của model: mỗi version chạy 1 lần nên một case PASS/FAIL đơn lẻ (như R10) chưa đủ kết luận.
- **Hạn chế:** v1 và v3 mỗi version gồm 2 thay đổi nên không quy được từng case cho từng thay đổi; điểm base dừng ở 0.95 với R10 regression ở v3.
- **Nếu có thêm một vòng (v4):** một giả thuyết duy nhất trong `system_prompt.md`: bổ sung rule 1 "yêu cầu tweet/bài đăng mà không có tài khoản và không có chủ đề → `clarify`, không tự chọn chủ đề (kể cả 'AI')", đồng thời bỏ cụm "AI/tech news" ở câu mở đầu nếu đó là nguồn model lấy chủ đề. Chạy mỗi version 2–3 lần để tách dao động khỏi hiệu quả thật.

## 8. Tài liệu tham khảo

- README, RUBRIC, CHECKPOINTS, `docs/TOOL-SETUP.md` của repo đề bài.
- OpenAI function calling / tool use docs (Chat Completions `tools`, `tool_choice`).
- API docs: Tavily (`lookup`), Firecrawl (`fetch`), RapidAPI twitter-api45 (`timeline`, `social_search`).
