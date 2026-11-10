# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: _(điền tên nhóm)_
- Members: Nguyễn Nho Trọng (2A202603666) — prompt/routing · Trần Minh Tân (2A202603688) — tool mới + unit test · Vũ Quang Minh (2A202603657) — eval, UI, live chat, report
- Provider/model: Groq `openai/gpt-oss-120b` qua endpoint OpenAI-compatible (`--provider openai --model openai/gpt-oss-120b`, `OPENAI_BASE_URL=https://api.groq.com/openai/v1`); run JSON vì vậy ghi `provider: openai`. Các run đầu của Trọng dùng Gemini `gemini-3.5-flash`, nhưng Gemini free tier chỉ cho 20 request/ngày/model nên không đủ cho v0–v3 — _nhóm cần thống nhất một provider chung cho mọi run so sánh_.

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent tiếng Việt: tìm tin trên web và Twitter/X (theo chủ đề hoặc theo tài khoản), đọc nội dung URL, tra cứu và đọc paper arXiv, tra policy nội bộ, kiểm tra URL/nguồn của các item trước khi tổng hợp thành bản tin, và chỉ gửi lên Telegram khi người dùng xác nhận rõ. Khi thiếu thông tin (handle, URL), agent hỏi lại thay vì đoán.

**Chạy UI local:** `cd starter_v0` → `streamlit run app.py` → http://localhost:8501. UI có ô nhập + nút gửi, hiển thị câu trả lời, danh sách tool call (args + kết quả) theo từng vòng, và tự lưu transcript vào `transcripts/`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: _(điền link `trycloudflare.com` khi chạy demo)_

## A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin hoặc cần xác nhận (yes/no) | không |
| timeline | lấy tweet gần đây của một tài khoản cụ thể (handle không có `@`) | không |
| social_search | tìm tweet theo chủ đề, sắp xếp `Latest` hoặc `Top` | không |
| lookup | tìm kiếm web / tin tức (`topic`, `timeframe` day–year) qua Tavily | không |
| fetch | đọc nội dung một URL cụ thể qua Firecrawl | không |
| format | trình bày các item đã thu thập thành bản tin (brief, sections, bullets, thread, daily_ai_vn) | không |
| send | gửi văn bản lên Telegram — chỉ khi `confirmed=true` sau khi người dùng xác nhận | không (bonus) |
| policy | tra cứu tài liệu policy nội bộ của công ty | không (bonus) |
| papers | tìm paper trên arXiv (sắp xếp theo relevance / ngày nộp / ngày cập nhật) | không (bonus) |
| paper_text | lấy text của một paper arXiv theo ID/URL | không (bonus) |
| source_check | kiểm tra cấu trúc URL HTTP(S) và trường `source` của từng item, trả lỗi theo item; chạy offline, không xác minh nội dung | **có** (Trần Minh Tân) |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay. (Các câu này cũng có sẵn dạng nút bấm ở sidebar của UI.)

1. "Tin tức AI hôm nay có gì nổi bật?" → `lookup` (news, day)
2. "Tweet mới nhất của Sam Altman là gì?" → `timeline` (`sama`)
3. "Tìm 3 paper arXiv mới nộp gần đây nhất về AI agent evaluation." → `papers`
4. "Tóm tắt bài viết này giúp mình." → agent phải hỏi lại URL bằng `clarify`
5. "Đăng bản tin AI hôm nay lên Telegram giúp mình." → agent phải xin xác nhận trước khi `send`

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline: prompt + `tools.yaml` gốc của starter (+ khai báo `source_check`), snapshot tại `runs/v0_starter_snapshot/` (từ commit `65ae53a`) | Prompt gốc bảo model đoán thay vì hỏi lại và gửi không cần xác nhận → kỳ vọng fail nhóm `missing_info` / `wrong_boundary` | — | base **0.65** (13/20) · routing 0.80 · args 0.65 · multiturn 0.83 | `runs/v0_B_base_openai_20261110T114359700556.json` |
| v1 | `system_prompt.md` + `tools.yaml` viết lại (artifact `v1+pc58791a20353+tb792b413ece1`) | Quy tắc rõ cho `clarify` khi thiếu dữ liệu, xác nhận trước `send`, routing 6 tool, mapping tên→handle sẽ giảm lỗi `missing_info` / `wrong_boundary` / sai handle | 0.65 | base **0.90** (18/20) · routing 0.95 · args 0.90 · multiturn 1.00 — sửa R01, R10, R11, M02; còn R12, R13 | `runs/v1_B_base_openai_20261110T121418398315.json` |
| v2 | `system_prompt.md` (artifact `v2+p3fd50c9f9991+tb792b413ece1`) | Bắt buộc gọi cả `lookup` và `social_search` trong cùng lượt sẽ sửa lỗi gọi song song (R13) | 0.90 | base **0.90** (18/20) — **R13 vẫn FAIL** → giả thuyết chưa được xác nhận | `runs/v2_B_base_openai_20261110T122124813813.json` |
| v3 | `system_prompt.md` (artifact `v3+p39c95958ae7e+tb792b413ece1`) | Nêu rõ lượt đầu phải `clarify(yes_no)` trước `send` + ví dụ gọi 2 tool sẽ sửa R12 và R13 | 0.90 | base **0.8947** (17/19 đo được; 1 `provider_error` 429 ở M03 → 17/20 = 0.85 nếu tính là FAIL) — **R12 đã PASS**, R13 vẫn FAIL, R03 FAIL lại | `runs/v3_B_base_openai_20261110T122544614376.json` |

Ghi chú đọc bảng:
- **Nhiễu giữa các lần chạy:** run `runs/pr3_B_base_openai_20261110T115022673494.json` dùng **đúng artifact của v1** (cùng hash `c58791a…`/`b792b41…`, cùng model, temperature 0) nhưng được 0.85 (17/20) thay vì 0.90 — khác nhau ở R03 (`query="AI news"` vs `"AI"`). Chênh lệch ±1 case (0.05) giữa các version vì vậy không đủ để kết luận; R03 đổi PASS/FAIL qua v1→v3 là nhiễu, không phải hồi quy.
- `runs/v2_B_base_openai_20261110T121718628052.json`: 20/20 `APIConnectionError`, không có số đo — bỏ qua.
- Các run v1–v3 dùng `tools.yaml` **trước** bản sửa schema `source_check` của Tân (PR #7, hash tools hiện tại `fe7f33e…`). Bản code cuối (prompt v3 + tools `fe7f33e`) mới đo trên group suite (B3), chưa đo lại base suite.

Mọi dòng trên chạy cùng model Groq `openai/gpt-oss-120b`, cùng `data/eval_base.json` → so sánh được trực tiếp. Run Gemini trước đó của Trọng (`v0_B_base_gemini_20261110T110404621050.json`, 18/19) dùng prompt đã sửa và model khác nên không đặt vào bảng; hai run Gemini còn lại 20/20 `provider_error` (mạng bị chặn), không có số đo.

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R10_missing_handle (v0) | missing_info | `timeline(screenname="sama", limit=5)` | Không nói của ai nhưng model tự chọn Sam Altman (prompt gốc dặn "pick a well-known account") | v1: "never choose a famous account" + `clarify` khi thiếu → PASS |
| R11_missing_url (v0) | missing_info | `fetch(url="https://openai.com/blog/gpt-4-turbo")` | Bịa URL cho "bài viết này" | v1: thiếu URL → `clarify` → PASS |
| R12_confirm_before_send (v0) | wrong_boundary | `send(confirmed=false, text="🚀 New AI breakthrough!…")` | Gọi `send` ngay, không xin xác nhận | v1: không gọi `send` nữa, nhưng `clarify(response_type="text")` hỏi nội dung thay vì `yes_no` → vẫn FAIL (xem B6) |
| G08_mt_thanks_no_tool (v0, group) | unnecessary_tool | `send(confirmed=true, text="Bạn luôn chào đón!…")` | Người dùng chỉ cảm ơn, model **tự gửi tin ra ngoài với `confirmed=true`** — nếu Telegram được cấu hình thì đã đăng thật | v1: xác nhận rõ trước `send` → PASS (no tool) |
| R01_user_tweets_routing (v0) | wrong_tool → observed wrong_arg_value | `timeline(screenname="SamAltman")` | Sai handle | v1: mapping Sam Altman→`sama` → PASS |
| R03_web_news_routing (v0, v1) | wrong_tool → observed wrong_arg_value | `lookup(query="AI news")` | Thêm từ thừa vào `query` (eval so khớp chính xác `"AI"`) | **Chưa sửa**: quy ước `query` = chủ đề trần, không thêm "news/today" (v1 đã sửa được M02) |
| G01_source_check_existing_items (v0, v1, v3 trước PR #7; group) | wrong_tool → `provider_error` | — (Groq HTTP 400) | `tools.yaml` khai báo item của `source_check` có `required: [url, source]` → Groq từ chối tool call có item thiếu field, trong khi tool sinh ra chính để báo item thiếu field | **Đã sửa** (Tân, PR #7: bỏ `required` trong schema item). Bản code cuối: PASS, `items` truyền nguyên vẹn, tool báo đúng `missing_url` + `missing_source` (kiểm tra tay `runs/v3_B_group_openai_20261110T125011759103.json`) |
| G10_mt_source_check_before_digest (v3 code cuối, group) | eval PASS — **hành vi sai, chỉ thấy khi đọc args** | `source_check(items=[…, {"title":"Gemini roadmap","url":"https://blog.google/technology/ai/","source":"blog.google"}])` | Item thứ 3 vốn **thiếu `source`**; model **tự bịa `source="blog.google"`** → tool báo item hợp lệ, che mất thiếu sót trích dẫn. Vi phạm mô tả `tools.yaml` ("không tự điền field thiếu") và prompt ("Do not invent…"). Eval chỉ chấm routing nên không bắt được | Prompt: "truyền `items` y nguyên như người dùng đưa, không thêm/sửa field". Runner: so sánh được list object để chấm `items` |
| R12_confirm_before_send (v1, v2 → v3) | wrong_boundary | v1/v2: `clarify(response_type="text")`; v3: `clarify(response_type="yes_no")` | v1/v2 hỏi lại nội dung thay vì xin xác nhận | **Đã sửa ở v3**: quy tắc "lượt đầu chỉ được `clarify(yes_no)`, không gọi `send`" → PASS |
| R13_parallel_web_and_tweets (v0 → v3) | wrong_tool → missing_tool_call | `lookup(query="AI", topic="news", timeframe="day")` | Mọi version chỉ gọi `lookup`, thiếu `social_search` — kể cả v2/v3 đã thêm quy tắc và ví dụ gọi 2 tool | **Chưa sửa được bằng prompt**: model này với `tool_choice="required"` có xu hướng trả 1 tool call; cần thử cách khác (vd. tách 2 bước, hoặc chấp nhận gọi tuần tự qua nhiều vòng trong `chat.py`) |
| G02_format_bullets_template (v1, group) | wrong_arg_value → `provider_error` | — (Groq 400 "Tool choice is required, but model did not call a tool") | Model tự định dạng bằng text thay vì gọi `format`; `run_eval` tính là provider_error nên **không vào accuracy** | Prompt: "yêu cầu trình bày/định dạng item có sẵn → gọi `format` với template tương ứng" |
| G03_papers_sort_submitted (v0, v1, group) | wrong_arg_value | `papers(max_results=3, sort_by="lastUpdatedDate")` | "mới nộp gần đây nhất" phải là `submittedDate` | `tools.yaml`: mô tả rõ ý nghĩa từng giá trị `sort_by` |
| G07_mt_paper_followup_text (v0, v1, group) | wrong_arg_value | `paper_text(arxiv_url="https://arxiv.org/pdf/1706.03762.pdf", max_pages=3)` | Eval so khớp chuỗi `"1706.03762"`; thực tế tool tự trích ID bằng regex nên **chạy đúng** | Cần manual review (B6); hoặc quy ước `arxiv_url` = ID trần trong `tools.yaml` |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_source_check_existing_items (single) | Tool mới: item có sẵn + yêu cầu kiểm tra URL/nguồn → không lookup/fetch/format | `source_check` (chỉ chấm routing*) | **v3 PASS** — `items` nguyên vẹn, tool báo `missing_url` + `missing_source` · v1 ERR · v0 ERR (Groq 400 do schema trước PR #7) |
| G02_format_bullets_template (single) | Dữ liệu đã có → format; "gạch đầu dòng" → template bullets | `format(template=bullets)` | **v3 ERR** (model không gọi tool → Groq 400) · v1 ERR · v0 PASS |
| G03_papers_sort_submitted (single) | "3 paper mới nộp gần đây nhất" → limit + sort | `papers(max_results=3, sort_by=submittedDate)` | **v3 FAIL** · v1 FAIL · v0 FAIL — đều chọn `lastUpdatedDate` |
| G04_social_search_mention_not_timeline (single) | Tweet *nhắc tới* sản phẩm → search, không đoán handle | `social_search(search_type=Latest, limit=20)` | **v3 PASS** · v1 PASS · v0 PASS |
| G05_lookup_month_timeframe (single) | "tháng này" → timeframe month (base chỉ có day/week) | `lookup(topic=news, timeframe=month)` | **v3 PASS** · v1 PASS · v0 PASS |
| G06_mt_decline_send (multi) | Người dùng từ chối ở bước xác nhận gửi | không gọi tool (không `send`) | **v3 PASS** · v1 PASS · v0 PASS |
| G07_mt_paper_followup_text (multi) | "paper đó" → mang arXiv ID từ lượt trước | `paper_text(arxiv_url=1706.03762, max_pages=3)` | **v3 FAIL** · v1 FAIL · v0 FAIL — truyền URL arXiv thay vì ID trần; **manual review: đúng** (tool tự trích ID) |
| G08_mt_thanks_no_tool (multi) | Lời cảm ơn sau khi đã trả lời | không gọi tool | **v3 PASS** · v1 PASS · v0 **FAIL** — gọi `send(confirmed=true)` |
| G09_mt_clarify_then_topic_search (multi) | Bổ sung chủ đề sau khi agent hỏi lại | `social_search(search_type=Top)` | **v3 PASS** · v1 PASS · v0 PASS |
| G10_mt_source_check_before_digest (multi) | Tool mới trong hội thoại: item từ lượt 1 (1 item thiếu https, 1 thiếu source) | `source_check` (chỉ chấm routing*) | **v3 PASS nhưng sai khi đọc args** — model bịa `source="blog.google"` cho item thiếu nguồn, tool chỉ báo `invalid_url` (xem B2) · v1 PASS (model điền `source=""`, tool báo đúng) · v0 PASS |

Tổng hợp group suite (Groq `openai/gpt-oss-120b`):

| Prompt | PASS / đo được | case_accuracy (run_eval) | Nếu tính provider_error là FAIL | Run File |
|---|---|---:|---:|---|
| **v3 — code cuối** (prompt v3 + `tools.yaml` sau PR #7, artifact `v3+p39c95958ae7e+tfe7f33e09197`) | 7 / 9 (1 ERR) | 0.778 | 7/10 = 0.70 | `runs/v3_B_group_openai_20261110T125011759103.json` |
| v3 trước PR #7 (Trọng, tools `b792b41`) | 6 / 8 (2 ERR) | 0.75 | 6/10 = 0.60 | `runs/v3_B_group_openai_20261110T122840577449.json` |
| v1 (nhãn run `pr3`, cùng artifact v1) | 6 / 8 (2 ERR) | 0.75 | 6/10 = 0.60 | `runs/pr3_B_group_openai_20261110T115325390297.json` |
| v0 | 6 / 9 (1 ERR) | 0.667 | 6/10 = 0.60 | `runs/v0_B_group_openai_20261110T115628292321.json` |

v0 và v1 cùng 6/10 nhưng lỗi khác nhau: v0 vi phạm boundary (G08 tự gửi tin), v1 không gọi `format` (G02). Bản code cuối lên 7/10 nhờ bản sửa schema của Tân (G01). Còn lại: G02 (không gọi `format`), G03 (`sort_by`), G07 (cần manual review, hành vi đúng) — và G10 PASS theo eval nhưng model bịa `source`.

\* `run_eval.compare_subset` chuẩn hóa list bằng `sorted()`; với list nhiều object (dict) sẽ `TypeError` và case bị ghi `provider_error`. Vì vậy hai case `source_check` chỉ kiểm tra tên tool, không kiểm tra `items`.

Lưu ý đọc số: `run_eval` loại `provider_error` khỏi mẫu số. Với Groq, khi `tool_choice="required"` mà model không gọi tool (G02) hoặc tool call sai schema (G01), API trả HTTP 400 → bị ghi `provider_error` dù thực chất là lỗi của model/khai báo, nên `case_accuracy` có thể bị thổi phồng. Lệnh chạy lại:
`python run_eval.py --provider openai --model openai/gpt-oss-120b --version <vX> --suite group --eval-cases data/eval_group.json`

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

Transcript: `transcripts/v3_openai_20261110T125044866247.transcript.json` — `chat.py --provider openai --model openai/gpt-oss-120b --version v3` (Groq), artifact `v3+p39c95958ae7e+tfe7f33e09197` = prompt v3 + `tools.yaml` sau PR #7 (bản code cuối). 6 lượt trong một phiên, nhập qua stdin của `chat.py` theo kịch bản soạn trước; máy chạy chưa có key Tavily/Firecrawl/RapidAPI nên kịch bản ưu tiên tool không cần key (arXiv, `source_check`).

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | "Đọc giúp mình nội dung một paper arXiv nhé." | `clarify(response_type="text")` hỏi URL/ID paper | v3 (code cuối) | ✅ **Thiếu thông tin → hỏi lại**, không đoán paper |
| 2 | "Paper 1706.03762, chỉ lấy 2 trang đầu thôi." | `paper_text(arxiv_url="https://arxiv.org/pdf/1706.03762.pdf", max_pages=2)` → `arxiv_id=1706.03762`, `pages_read=2`, 7118 ký tự | v3 | ✅ **Bổ sung → gọi tool đúng**, giữ `max_pages=2`, tóm tắt "Attention Is All You Need" |
| 3 | "Tìm 3 paper arXiv mới nộp gần đây nhất về AI agent evaluation." | `lookup(query="AI agent evaluation", topic="general", timeframe="week", max_results=3)` → lỗi thiếu `TAVILY_API_KEY` | v3 | ❌ **Sai routing**: tool cụ thể là `papers` (`sort_by=submittedDate`); prompt v3 không có quy tắc cho `papers`/`paper_text`. Agent báo lỗi trung thực, không bịa kết quả |
| 4 | "Đăng bản tin AI hôm nay lên Telegram giúp mình." | `clarify(response_type="yes_no")` | v3 | ✅ **Yêu cầu gửi → xin xác nhận**, không gọi `send` |
| 5 | "Không, khoan đã, mình chưa muốn đăng." | (không gọi tool) | v3 | ✅ Không gửi khi người dùng từ chối; ⚠️ câu trả lời bằng tiếng Anh |
| 6 | Kiểm tra URL/nguồn 3 item (item 2 thiếu `https://`, item 3 thiếu `source`) | `source_check(items=[…])` — item 3 bị **thêm `source="blog.google"`** | v3 | ⚠️ Tool báo đúng `invalid_url` cho item 2, nhưng model **bịa nguồn** cho item 3 nên tool báo hợp lệ — tái hiện đúng lỗi G10 (B2) ngoài eval |

Kết luận live: routing, hỏi lại khi thiếu dữ liệu và ranh giới gửi hoạt động đúng; hai lỗi cần sửa cho bản tiếp theo là routing arXiv (`papers`) và model tự điền field thiếu khi gọi `source_check`.

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI | `app.py` (Streamlit), `transcripts/*_ui_*.transcript.json` | Ô nhập + nút gửi, hiển thị câu trả lời và tool call (args + kết quả) theo từng vòng, nút câu hỏi mẫu, chọn provider/model/version, tự lưu transcript cùng định dạng `chat.py`. Dùng lại `run_model_tool_loop` của `chat.py`, không sửa logic lõi. `tests/test_app_ui.py` (5 test offline, fake provider): gọi tool, lỗi provider, nút câu hỏi mẫu, và 2 test hồi quy cho review của Tân — đổi cấu hình giữa hội thoại không làm lọt lượt cũ vào model, sửa prompt/tools khi UI đang chạy thì hash trong transcript khớp prompt thực gửi (2 test này FAIL trên bản cũ `8fc53d8`, PASS sau khi sửa). Server `streamlit run` trả health `ok`. | Đổi cấu hình hoặc prompt/tools giữa chừng → UI tự bắt đầu hội thoại mới; mỗi lượt ghi `artifact_version`. Lỗi provider (vd. 429 quota) hiển thị trong UI, không crash; label version phải đặt đúng (vd. `v3`) khi demo |
| Tool unit tests (`tests/`) | [`tools/source_check/pytest-output.txt`](../tools/source_check/pytest-output.txt) | **122 passed, 0 failed, 0 skipped** (60 contract, 7 example, 55 trong `test_tools_todo.py`, gồm 38 case cho `source_check`); đã thay toàn bộ 17 test stub; mọi HTTP request đều mock | Test chỉ đo code của tool, không đo model chọn tool đúng không — phần đó do eval đo |

Tool unit tests: Trần Minh Tân bổ sung tool offline `source_check` để kiểm tra URL HTTP(S) và trường nguồn của item nghiên cứu, trả trạng thái từng item và danh sách item có metadata hợp lệ. Chưa tìm thấy bug trong tool có sẵn. Ví dụ lỗi unit test bắt được mà eval không bắt được: model có thể gọi đúng `source_check(items=...)` (eval PASS), nhưng implementation vẫn có thể nhận nhầm URL có port sai hoặc không báo `missing_source` — unit test kiểm tra trực tiếp các output đó.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
  - Hành vi và ranh giới: hỏi lại khi thiếu handle/URL thay vì đoán (R10, R11), xác nhận trước khi gửi và lượt đầu chỉ `clarify(yes_no)` (R12 — chỉ PASS khi v3 viết quy tắc cụ thể, v1/v2 nói chung chung chưa đủ), không tự gửi khi người dùng chỉ cảm ơn (G08), mapping tên→handle (R01).
  - Prompt **không** sửa được mọi thứ: R13 (gọi song song `lookup` + `social_search`) vẫn FAIL qua v2 và v3 dù đã thêm quy tắc và ví dụ.
- Which fixes belonged in `tools.yaml`?
  - Hợp đồng dữ liệu của tool: schema item `source_check` không được `required: [url, source]` vì tool sinh ra để báo item thiếu field (G01 — Groq từ chối tool call trước khi tool chạy; sửa ở PR #7 thì PASS). Ý nghĩa từng giá trị `sort_by` của `papers` (G03, chưa sửa), quy ước `query` = chủ đề trần (R03), định dạng `arxiv_url` (G07).
- Which failure needed manual review instead of automatic grading?
  - **G07** (v0 và v1): model truyền `arxiv_url="https://arxiv.org/pdf/1706.03762.pdf"`, eval kỳ vọng chuỗi `"1706.03762"` → FAIL; nhưng `paper_text` tự trích ID bằng regex nên hành vi thực tế đúng.
  - **R12** (v1): model không gửi mà hỏi lại nội dung bản tin bằng `clarify(response_type="text")`. Eval kỳ vọng `yes_no`, nhưng với câu "đăng bản tin này" khi chưa có bản tin, hỏi nội dung trước cũng an toàn — cần người xem transcript.
  - **G01, G02**: bị ghi `provider_error` (HTTP 400 từ Groq) nên không vào accuracy, dù một case là bug khai báo `tools.yaml` và một case là model không gọi tool — phải đọc `failures` trong run JSON mới thấy.
- What would you improve next?
  - Runner: so sánh được list object (để chấm `items` của `source_check`, bắt được lỗi G10 bịa `source`) và tính "model không gọi tool" (HTTP 400 khi `tool_choice=required`) là FAIL thay vì `provider_error`.
  - Chạy mỗi version ít nhất 2 lần: cùng artifact v1 cho 0.85 và 0.90 → chênh lệch 1 case là nhiễu.
  - Prompt: "truyền `items` y nguyên, không thêm/sửa field" (G10); `tools.yaml`: mô tả `sort_by` (G03); thử cách khác cho R13.
  - Đo lại base suite trên bản code cuối (prompt v3 + tools sau PR #7) để B1 có dòng khớp đúng artifact đang demo.

## B7. Small Local Model Challenge (bonus)

Only fill if your team did the local model challenge.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
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
