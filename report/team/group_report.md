# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: G2026
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: `openrouter` / `openai/gpt-4o-mini`

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent: tìm tin AI trên web (Tavily), bài đăng X/Twitter, Hacker News, Wikipedia và paper arXiv; đọc nội dung một URL; tổng hợp thành digest Markdown; hỏi lại khi thiếu thông tin (tài khoản/URL) và chỉ gửi Telegram sau khi người dùng xác nhận.

UI hiển thị cả tool call + args + kết quả tool trong khung mở rộng, nên người thử thấy được agent đã gọi gì.

**Cách chạy UI:**

```powershell
cd starter_v0
.\.venv\Scripts\Activate.ps1          # Windows (macOS/Linux: source .venv/bin/activate)
streamlit run app.py --server.port 8501
# → http://localhost:8501
```

Dependency `streamlit>=1.40` đã thêm vào `starter_v0/requirements.txt`. Cần `OPENROUTER_API_KEY` (và `TAVILY_API_KEY`, `FIRECRAWL_API_KEY`, `RAPIDAPI_KEY` cho tool tương ứng) trong `starter_v0/.env`; UI tự ẩn tool thiếu key để agent chuyển sang nguồn còn dùng được (kèm cảnh báo ở sidebar) thay vì hiện lỗi `RuntimeError`.

**Link dùng thử (deploy):**

Cloudflare Tunnel trỏ vào UI local:

```powershell
cloudflared tunnel --url http://127.0.0.1:8501
```

> URL: https://terminals-shots-loc-degrees.trycloudflare.com
>
> Link `trycloudflare.com` là **tạm thời**, sống theo phiên `cloudflared` (tắt lệnh/tắt máy là mất) **và** chỉ hoạt động khi Streamlit đang chạy ở cổng 8501 (nếu UI tắt, link trả 502 Bad gateway). Nhóm giữ cả `streamlit` và `cloudflared` chạy trong suốt buổi showdown. Nếu link chết, chạy lại 2 lệnh trên và cập nhật URL mới vào đây.

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin (`text` / `yes_no` / `choice`) | không |
| timeline | bài đăng gần đây của một tài khoản X (`screenname`, không có `@`) | không |
| social_search | tìm bài đăng X theo từ khóa, `search_type` = `Top` \| `Latest` | không |
| lookup | tìm web (Tavily) với `topic` = `general` \| `news` và `timeframe` = `day` \| `week` \| `month` \| `year` | không |
| fetch | đọc nội dung một URL cụ thể (Firecrawl) | không |
| format | trình bày các item đã thu thập thành digest Markdown | không |
| send | gửi text lên Telegram channel, chỉ khi `confirmed=true` | không |
| policy | tìm trong company policy nội bộ (source citation, data privacy, …) | không |
| papers | tìm paper trên arXiv theo từ khóa | không |
| paper_text | tải PDF arXiv và trích plain text | không |
| wiki | tra cứu nền tảng bách khoa (Wikipedia) về một thực thể trước khi tìm tin | có |
| hackernews | bài đăng/thảo luận công nghệ trên Hacker News kèm điểm + bình luận | có |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1. "OpenAI là công ty gì? Trả lời gọn trong 2 câu." → `wiki(query="OpenAI", sentences=2)`
2. "Trên Hacker News có bài nào mới nhất về MCP không? Lấy 3 bài." → `hackernews(query="MCP", sort="date", limit=3)`
3. "Tin tức AI hôm nay có gì nổi bật? Tóm tắt giúp mình 3 tin chính." → `lookup(query="AI", topic="news", timeframe="day", max_results=3)`
4. "Tóm tắt 5 tweet mới nhất giúp mình" → agent hỏi lại account (không tự đoán handle).
5. "Đăng bản tin này lên Telegram giúp mình" → `clarify(response_type="yes_no")` trước, không tự `send`.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

- **Tool mới `wiki`** (`starter_v0/tools/wiki/`): tra Wikipedia REST để lấy 1–2 câu nền tảng về một thực thể cụ thể (người/tổ chức/sản phẩm/khái niệm), trả `summary` + `url` canonical + `items` đưa thẳng vào `format`. Agent nên gọi khi người dùng hỏi "X là gì/là ai" hoặc cần bối cảnh trước khi tìm tin; **không** gọi cho tin mới (`lookup`), bài cộng đồng (`social_search`), paper (`papers`). Không cần API key; đã khai báo trong `tools.yaml` và đăng ký ở `TOOL_FUNCTIONS`.
- **Tool mới `hackernews`** (`starter_v0/tools/hackernews/`): tìm story trên Hacker News qua Algolia HN Search (không cần API key), trả `items` có `title/url/source/summary` + `points`/`comments` (tín hiệu cộng đồng), `hn_url`, và `text` đã bỏ HTML cho Ask HN; bài không có link ngoài thì fallback về `news.ycombinator.com/item?id=...`. Agent gọi khi người dùng nói rõ Hacker News/HN, "dân dev bàn gì", "Show HN", hoặc cần thêm nguồn cộng đồng kỹ thuật; **không** gọi cho tin báo chí (`lookup`), tweet (`social_search`), paper (`papers`), hay URL cụ thể (`fetch`).

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (không sửa) | Đo hành vi chưa tối ưu: prompt bảo đoán thay vì hỏi, gửi không cần xác nhận | — | 0.75 | `starter_v0/runs/v0_B_base_openrouter_20261110T172631463565.json` |
| v1 | `artifacts/system_prompt.md` | Bỏ chỉ dẫn đoán (Sam Altman, URL giả) + thêm rule `clarify(response_type="text")` khi thiếu account/URL | 0.75 | 0.90 | `starter_v0/runs/v1_B_base_openrouter_20261110T175622978277.json` |
| v2 | `artifacts/system_prompt.md` | Thêm Scope + Sending boundary (`clarify(yes_no)`, `confirmed=true`) + Plan the turn | 0.90 | 1.00 | `starter_v0/runs/v2_B_base_openrouter_20261110T180239635864.json` |
| v3 | `artifacts/tools.yaml` | Viết lại description 12 tool (when/when-not + convention args) + nhắc `clarify` luôn đặt `response_type` | 1.00 | 1.00 | `starter_v0/runs/v3_B_base_openrouter_20261110T183447099371.json` |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `send(text="Nguyên hàm của x^2 …")` | Gọi `send` cho câu toán ngoài phạm vi research/news/social | v2: thêm Scope; v3: `send` ghi rõ "không dùng để trả lời câu hỏi" |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Tự đoán handle Sam Altman thay vì hỏi lại | v1: bỏ chỉ dẫn đoán + rule `clarify(response_type="text")` |
| R11_missing_url | missing_info | `fetch(url="https://example.com/article")` | Bịa URL khi user nói "bài này" mà không có link | v1: rule `clarify` xin link |
| R12_confirm_before_send | wrong_boundary | `send(text="Bản tin này")` | Gửi ngay, không xin xác nhận trước | v2: Sending boundary → `clarify(response_type="yes_no")` |
| R13_parallel_web_and_tweets | wrong_tool (observed `wrong_arg_value`) | `lookup(query="AI news", timeframe="day")` thiếu `topic`; `social_search(...)` | Query lẫn từ khóa "news" + thiếu `topic="news"`; `social_search` khi đó lỗi vì thiếu RAPIDAPI | v3: mô tả `lookup` rõ `query` chỉ chủ đề, `topic` bắt buộc; đã thêm RAPIDAPI |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_wiki_definition_routing | Hỏi định nghĩa 1 thực thể → `wiki`, không phải `lookup`/`fetch`; đòi 2 câu | `wiki(query="OpenAI", sentences=2)` | PASS — model gọi `wiki(query="OpenAI", lang="vi", sentences=2)` |
| G02_hackernews_newest_arg | Nguồn Hacker News + "mới nhất" + "3 bài" → đúng tool và đúng 2 arg | `hackernews(sort="date", limit=3)` | PASS — `hackernews(query="MCP", sort="date", limit=3)` |
| G03_translation_out_of_scope | Dịch thuật ngoài phạm vi research/news/social → không gọi tool nào | `no_tool` (refuse) | PASS — 0 tool call |
| G04_wiki_multiturn_lang | 3 lượt: giữ entity, sentences, rồi đổi `lang` sang tiếng Việt | `wiki(query="Anthropic", sentences=2, lang="vi")` | PASS — đúng cả 3 arg |
| G05_hackernews_sort_correction | 3 lượt: sửa `sort` relevance → date, giữ `limit=3` | `hackernews(sort="date", limit=3)` | PASS — `query="MCP"`, sort=date, limit=3 |
| G06_switch_news_to_wiki | 3 lượt: đổi ý từ tin tức (lookup) sang định nghĩa (wiki), còn 1 câu | `wiki(query="OpenAI", sentences=1)` | PASS — `wiki(query="OpenAI", lang="vi", sentences=1)` |

Batch 1: **6/10 case (3 single + 3 multi)**, 6/6 PASS. 4 case còn lại cho `date_calc`/`cite_format` do thành viên khác thêm, giữ tổng **5 single + 5 multi**. 5 case (`G01/G02/G04/G05/G06`) route tới 2 tool mới, vượt yêu cầu "≥ 1 case".

Run: `starter_v0/runs/v3_B_group_openrouter_20261110T192049745700.json` — `total_cases=6`, `measured_cases=6`, `provider_error_cases=0`, `case_accuracy=1.0`, `tool_routing_accuracy=1.0`, `argument_accuracy=1.0`, `multiturn_accuracy=1.0`; mọi tool call chạy thật không lỗi (`tool_results` không có `error`). Artifact version `v3+p661c801ecb6f+t82fdfe0351db`: hash `t…` khác run v3 base vì `tools.yaml` đã thêm `wiki`/`hackernews` ở CP3 — đây là chủ ý, không sửa lại hash v0–v3.

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tin tức AI hôm nay, tóm tắt 3 tin chính | `lookup(query="AI", topic="news", timeframe="day", max_results=3)` | `transcripts/v3_openrouter_20261110T232722798444.transcript.json` | 3 tin + link nguồn |
| 2 | Tóm tắt 5 tweet mới nhất | không gọi tool — agent hỏi lại account | cùng transcript | hỏi lại đúng hướng (không đoán handle) |
| 3 | Của Sam Altman nhé | `timeline(screenname="sama", limit=5)` | cùng transcript | 5 tweet kèm metrics — RAPIDAPI chạy thật |
| 4 | Đăng bản tin AI vừa tóm tắt lên Telegram | `clarify(response_type="yes_no")` | cùng transcript | chờ user xác nhận, không tự gửi |

> Ghi chú trung thực: lượt 2 agent hỏi lại bằng text thay vì gọi `clarify`; bằng chứng boundary của tool `clarify` nằm ở lượt 4.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) | `starter_v0/tools/wiki/` + `starter_v0/tools/hackernews/` (mỗi tool có `tool.py` + `TOOL.md`) | `wiki`: tóm tắt bách khoa 1 thực thể (Wikipedia REST, en/vi, không key), `summary` N câu ≤ 1200 ký tự + `url` canonical + `items` cho `format`. `hackernews`: story/thảo luận HN (Algolia, không key), `items` có `points`/`comments`/`text` (Ask HN đã bỏ HTML), fallback URL về item page khi bài không có link ngoài | Nội dung Wikipedia/HN là untrusted: `wiki` trả `trust_boundary`, HN chỉ là tín hiệu chứ không phải fact; validate `lang`/`sentences` và `sort`/`limit` **trước** khi gọi mạng; timeout 30s; mọi lỗi trả error dict |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py` (`test_wiki_*`, `test_hackernews_*`), `pytest -q -rs` -> 93 passed, 0 skipped, 0 failed | 7 test offline (wiki 3 + hackernews 4): happy path (assert cả request: URL/UA/timeout/params, và mapping), đổi endpoint theo `sort`, input xấu từ model (rỗng, sai kiểu, ngoài enum/khoảng), nhánh lỗi HTTP 429 -> `HTTPError` dict | `fake_http` + `block_network` chặn mạng thật; test input xấu assert `calls == []` để bắt regression "gọi API oan khi args sai" |
| UI (lệnh chạy + link dùng thử) | `starter_v0/app.py`, `requirements.txt`, link ở A1 | Streamlit UI: chat nhiều lượt, render tool call/args/result trong expander; đã kiểm thử headless bằng `AppTest` (1 lượt "OpenAI là gì?" → `wiki` trả lời, 0 exception); health `/_stcore/health` = 200; link public qua Cloudflare Tunnel trả 200 | Key chỉ hiện cảnh báo thiếu, không hiển thị giá trị; link tunnel tạm thời, tắt sau showdown; mỗi lượt chat tốn credit API nên chỉ chia sẻ trong buổi demo |

Tool unit tests: 7 test cho 2 tool mới (`wiki` 3, `hackernews` 4), chạy offline, mock toàn bộ HTTP. Toàn suite: 93 passed, 0 skipped, 0 failed — 21 test trong `test_tools_todo.py` gồm 7 test tool mới + 14 stub cũ (clarify, format, send, lookup, fetch, timeline, social_search, policy) đã thay bằng test thật. Ví dụ lỗi mà unit test bắt được nhưng eval không bắt được: `test_wiki_bad_model_input_returns_error_dict_before_any_network_call` chứng minh `lang="xx"` / `sentences="3"` bị chặn *trước khi* phát request (`calls == []`); tương tự `test_hackernews_bad_model_input_returns_error_dict_before_any_network_call` chặn `sort="top"` / `limit=50`. Eval chỉ thấy model chọn tool/args gì, không thấy được tool có gọi mạng oan, nuốt lỗi hay raise hay không.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `starter_v0/tests/test_tools_todo.py`, `pytest -q -rs` output | 93 passed, 0 skipped, 0 failed: 14 stub của tool có sẵn (clarify 1, format 3, send 2, lookup 1, fetch 2, timeline 1, social_search 1, policy 3) đã thay bằng test offline mock HTTP, assert cả request gửi đi lẫn mapping kết quả | `fake_http` + `block_network` chặn mạng thật, mỗi test một hành vi; test input xấu assert `calls == []` |

Test challenge: không phát hiện bug trong các tool có sẵn (hành vi khớp mô tả ở `TOOL.md` và example test), nên nhóm chọn hướng "0 skipped" của challenge: thay 14 stub bằng test thật, `pytest -q -rs` -> 93 passed, 0 skipped, 0 failed.

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
