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
| v0 | baseline: prompt + `tools.yaml` gốc của starter (+ khai báo `source_check`), snapshot tại `runs/v0_starter_snapshot/` (từ commit `65ae53a`) | Prompt gốc bảo model đoán thay vì hỏi lại và gửi không cần xác nhận → kỳ vọng fail nhóm `missing_info` / `wrong_boundary` | — | _đang chạy (Groq)_ | _chờ run_ |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_source_check_existing_items (single) | Tool mới: item có sẵn + yêu cầu kiểm tra URL/nguồn → không lookup/fetch/format | `source_check` (chỉ chấm routing*) | _chờ run_ |
| G02_format_bullets_template (single) | Dữ liệu đã có → format; "gạch đầu dòng" → template bullets | `format(template=bullets)` | _chờ run_ |
| G03_papers_sort_submitted (single) | "3 paper mới nộp gần đây nhất" → limit + sort | `papers(max_results=3, sort_by=submittedDate)` | _chờ run_ |
| G04_social_search_mention_not_timeline (single) | Tweet *nhắc tới* sản phẩm → search, không đoán handle | `social_search(search_type=Latest, limit=20)` | _chờ run_ |
| G05_lookup_month_timeframe (single) | "tháng này" → timeframe month (base chỉ có day/week) | `lookup(topic=news, timeframe=month)` | _chờ run_ |
| G06_mt_decline_send (multi) | Người dùng từ chối ở bước xác nhận gửi | không gọi tool (không `send`) | _chờ run_ |
| G07_mt_paper_followup_text (multi) | "paper đó" → mang arXiv ID từ lượt trước | `paper_text(arxiv_url=1706.03762, max_pages=3)` | _chờ run_ |
| G08_mt_thanks_no_tool (multi) | Lời cảm ơn sau khi đã trả lời | không gọi tool | _chờ run_ |
| G09_mt_clarify_then_topic_search (multi) | Bổ sung chủ đề sau khi agent hỏi lại | `social_search(search_type=Top)` | _chờ run_ |
| G10_mt_source_check_before_digest (multi) | Tool mới trong hội thoại: item từ lượt 1 (1 item thiếu https, 1 thiếu source) | `source_check` (chỉ chấm routing*) | _chờ run_ |

\* `run_eval.compare_subset` chuẩn hóa list bằng `sorted()`; với list nhiều object (dict) sẽ `TypeError` và case bị ghi `provider_error`. Vì vậy hai case `source_check` chỉ kiểm tra tên tool, không kiểm tra `items`.

Kết quả: đang chạy trên Groq `openai/gpt-oss-120b` (key Gemini free tier của Minh đã hết quota 20 request/ngày/model trong ngày 10/11/2026). Lệnh chạy:
`python run_eval.py --provider openai --model openai/gpt-oss-120b --version <vX> --suite group --eval-cases data/eval_group.json`

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI | `app.py` (Streamlit), `transcripts/*_ui_*.transcript.json` | Ô nhập + nút gửi, hiển thị câu trả lời và tool call (args + kết quả) theo từng vòng, nút câu hỏi mẫu, chọn provider/model/version, tự lưu transcript cùng định dạng `chat.py`. Dùng lại `run_model_tool_loop` của `chat.py`, không sửa logic lõi. Smoke test offline bằng `streamlit.testing` (fake provider): gọi tool, lỗi provider, nút câu hỏi mẫu đều đạt; server `streamlit run` trả health `ok`. | Lỗi provider (vd. 429 quota) hiển thị trong UI, không crash; label version phải đặt đúng (vd. `v3`) khi demo vì transcript lưu kèm hash prompt/tools |
| Tool unit tests (`tests/`) | [`tools/source_check/pytest-output.txt`](../tools/source_check/pytest-output.txt) | **122 passed, 0 failed, 0 skipped** (60 contract, 7 example, 55 trong `test_tools_todo.py`, gồm 38 case cho `source_check`); đã thay toàn bộ 17 test stub; mọi HTTP request đều mock | Test chỉ đo code của tool, không đo model chọn tool đúng không — phần đó do eval đo |

Tool unit tests: Trần Minh Tân bổ sung tool offline `source_check` để kiểm tra URL HTTP(S) và trường nguồn của item nghiên cứu, trả trạng thái từng item và danh sách item có metadata hợp lệ. Chưa tìm thấy bug trong tool có sẵn. Ví dụ lỗi unit test bắt được mà eval không bắt được: model có thể gọi đúng `source_check(items=...)` (eval PASS), nhưng implementation vẫn có thể nhận nhầm URL có port sai hoặc không báo `missing_source` — unit test kiểm tra trực tiếp các output đó.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?

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
