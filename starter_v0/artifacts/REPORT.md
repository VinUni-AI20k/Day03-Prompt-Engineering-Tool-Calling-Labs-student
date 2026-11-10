# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: NhomNoName
- Members: _(điền tên thành viên)_
- Provider/model: Gemini — `gemini-3.5-flash` (`--provider gemini`)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

**Research agent** tiếng Việt: tìm tin tức trên web theo chủ đề và thời gian, xem tweet theo tài khoản hoặc theo chủ đề, đọc và tóm tắt một URL, tra bài báo arXiv và quy định nội bộ. Khi không có tool nào khớp, agent tự tìm trên mạng và tổng hợp câu trả lời kèm nguồn (`web_answer`).

Agent được thiết kế để **an toàn**: thiếu thông tin thì hỏi lại chứ không đoán (không tự chọn tài khoản, không bịa URL), xin xác nhận trước khi đăng lên Telegram, và từ chối câu ngoài phạm vi (toán, code, dịch, sáng tác). Điểm eval base: **0.55 (v0) → 0.75 (v1) → 0.85 (v2)**, tool routing đạt 1.00 từ v2.

**Link dùng thử (deploy):**

> URL: https://hidden-distinguished-explaining-tourist.trycloudflare.com

Cách chạy UI (Streamlit, file `app.py`):

```bash
pip install -r requirements.txt      # có streamlit
streamlit run app.py                 # → http://localhost:8501
cloudflared tunnel --url http://localhost:8501   # → link public, giữ lệnh chạy suốt buổi demo
```

UI có sẵn nút "Thử nhanh" cho các câu hỏi ở A3, hiển thị từng tool call (tên + args + kết quả), và lưu hội thoại vào `transcripts/*.transcript.json`.

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi lại người dùng khi thiếu thông tin (tài khoản, URL) hoặc xin xác nhận (`yes_no`) trước khi đăng | không |
| `timeline` | Lấy tweet gần đây của một tài khoản X cụ thể (tên → handle, ví dụ Sam Altman → `sama`) | không |
| `social_search` | Tìm tweet theo chủ đề, sắp xếp `Latest` hoặc `Top` | không |
| `lookup` | Tìm trên web (Tavily) theo chủ đề, `topic=news/general`, `timeframe=day/week/month/year` | không |
| `fetch` | Đọc nội dung một URL người dùng đưa (Firecrawl) | không |
| `format` | Trình bày các kết quả thành bản tin (digest) theo template | không |
| `send` | Đăng bản tin lên Telegram, **chỉ sau khi người dùng xác nhận** | không (bonus) |
| `policy` | Tra tài liệu quy định nội bộ của công ty | không (bonus) |
| `papers` | Tìm bài báo khoa học trên arXiv | không (bonus) |
| `paper_text` | Lấy nội dung text của một bài báo arXiv | không (bonus) |
| `web_answer` | **Tool dự phòng:** khi không có tool nào khớp, tự tìm trên web (Tavily, `include_answer`) và tổng hợp câu trả lời kèm nguồn + mức tin cậy | **có** |

## A3. Câu hỏi mẫu để thử

| # | Câu hỏi | Agent sẽ làm gì |
|---|---|---|
| 1 | Tin tức AI hôm nay có gì nổi bật? | `lookup(query="AI", topic="news", timeframe="day")` rồi tóm tắt |
| 2 | Tweet mới nhất của Sam Altman là gì? | `timeline(screenname="sama")` |
| 3 | Tóm tắt 5 tweet mới nhất giúp mình | **Hỏi lại** xem tài khoản của ai (không đoán) |
| 4 | RAG là gì? | `web_answer` tự tìm trên mạng và trả lời kèm nguồn |
| 5 | Đăng bản tin này lên Telegram giúp mình | **Xin xác nhận** (có/không) trước, không tự gửi |

Thử thêm câu ngoài phạm vi, ví dụ "Viết hàm Python tính Fibonacci": agent sẽ từ chối lịch sự và giới thiệu những việc nó làm được.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

> Metric = `case_accuracy` trên suite `base` (20 case), model gemini-3.5-flash. v0–v3 đều lấy từ run thật. `artifacts/version_log.csv` hiện vẫn chưa có dòng nào (chỉ có header), nên số liệu dưới đây lấy trực tiếp từ `summary` trong `runs/*.json`. Nội dung cột Changed Artifact/Hypothesis đối chiếu với diff `system_prompt.md`/`tools.yaml` của các commit `run v1`, `run v2`, `run v3`. Dòng v4 là kế hoạch, chưa chạy.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (`system_prompt.md` + `tools.yaml` starter, hash `v0+peb1c8179815b+t5b22a2476d41`) | Đo mốc ban đầu với gemini-3.5-flash. Prompt v0 cố tình xấu (đoán thay vì hỏi, tự gửi, chỉ chọn 1 tool), mô tả tool mơ hồ | — | 0.55 (11/20; routing 0.65, argument 0.55, multiturn 0.83) | `runs/v0_B_base_gemini_20261110T111122645086.json` |
| v1 | `system_prompt.md` + `tools.yaml` (hash `v1+pbbc09845307f+td67078e54c86`) | **Prompt:** thêm mục "Scope (highest priority)" ở đầu: câu ngoài phạm vi (toán, code, dịch, sáng tác) → từ chối bằng text, không gọi tool; câu hỏi về bản thân agent → trả lời thẳng; `send` không phải cách trả lời người dùng. **Tools:** mô tả `lookup.query` = chỉ từ khóa cốt lõi, không thêm từ chỉ thời gian; `send` = chỉ đăng bản tin lên Telegram; `policy` = chỉ cho câu hỏi về quy định nội bộ; thêm tool mới `scope_check` (chỉ gọi khi không chắc phạm vi). Kỳ vọng sửa R03, R08, R09, R14, M02 | 0.55 | **0.75** (15/20; routing 0.80, argument 0.75, multiturn 1.00) | `runs/v1_B_base_gemini_20261110T113910565355.json` |
| v2 | `system_prompt.md` + `tools.yaml` (hash `v2+pd55d5ef3b68b+t5e8885abcd6c`) | **Prompt:** xóa câu v0 "make a sensible guess… pick a well-known account like Sam Altman… assume a likely URL". Thêm mục "Missing information → ask, never guess": không có người/handle → `clarify(response_type="text")`, không gọi `timeline`; nói "bài này" mà không có URL → `clarify(response_type="text")`, không gọi `fetch`/`lookup`; đã có tên/URL (lượt này hoặc lượt trước) → gọi tool luôn, không hỏi lại. **Tools:** `clarify` = dùng khi thiếu thông tin bắt buộc, thay cho đoán; `timeline` = chỉ gọi khi đã biết tài khoản, `screenname` lấy từ lời người dùng (Sam Altman → sama); `fetch` = chỉ đọc URL người dùng đã đưa. Kỳ vọng sửa R10, R11, không làm hỏng R01, R04, M01, M04 | 0.75 | **0.85** (17/20; routing 1.00, argument 0.85, multiturn 1.00) | `runs/v2_B_base_gemini_20261110T120241831341.json` |
| v3 | `system_prompt.md` + `tools.yaml` (hash `v3+pd86ea544c2fa+tf6bf4d7efa63`) | **Prompt:** xóa 2 câu v0 còn lại "just go ahead and do it" và "Pick one tool". Thêm luật: mọi yêu cầu đăng/gửi (send, Telegram) → trước tiên `clarify(response_type="yes_no")` xin xác nhận, kể cả khi chưa rõ nội dung; chỉ gọi `send(confirmed=true)` sau khi người dùng trả lời "có"; yêu cầu nhiều nguồn → gọi nhiều tool, một nguồn → đúng một tool; thêm mục "Writing the `query` argument" (chỉ chủ đề cốt lõi, không thêm news/hôm nay/mới nhất, kèm ví dụ). **Tools:** `lookup.query` thêm "KHÔNG thêm chữ 'news'/'tin tức' vì đã có `topic=news`; giữ nguyên từ khóa người dùng viết, không mở rộng viết tắt", kèm ví dụ "Tin tức AI hôm nay" → `query="AI", topic="news", timeframe="day"`; `send.confirmed` = chỉ true khi người dùng đã xác nhận. Kỳ vọng sửa R03, R12, R13 | 0.85 | **1.00** (20/20; routing 1.00, argument 1.00, multiturn 1.00) | `runs/v3_B_base_gemini_20261110T121719724943.json` |

**So sánh theo từng case** (từ `results[*].result.passed`):

| Thay đổi | v0 → v1 | v1 → v2 | v2 → v3 |
|---|---|---|---|
| Fail → Pass | R08_out_of_scope, R09_no_tool_capability, R14_out_of_scope_coding, M02_carryover_timeframe (4) | R10_missing_handle, R11_missing_url (2) | R03_web_news_routing, R12_confirm_before_send, R13_parallel_web_and_tweets (3) |
| Vẫn fail | R03, R10, R11, R12, R13 (5) | R03, R12, R13 (3) — cả 3 đều đã đúng tool, chỉ còn sai 1 tham số | không còn (0) |
| Pass → Fail (regression) | không có | không có | không có |

Tổng: case_accuracy 0.55 → 0.75 → 0.85 → **1.00**; tool_routing 0.65 → 0.80 → 1.00 → 1.00; argument 0.55 → 0.75 → 0.85 → 1.00; multiturn 0.83 → 1.00 → 1.00 → 1.00.

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

### B2.1. v0 (baseline)

Nguồn: `runs/v0_B_base_gemini_20261110T111122645086.json` (v0, suite `base`, gemini-3.5-flash). Kết quả: 11/20 pass — case_accuracy 0.55, tool_routing 0.65, argument 0.55, multiturn 0.83. 9 case fail như bảng dưới.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_arg_value | `lookup(query="AI news today", topic="news", timeframe="day", max_results=5)` | Đúng tool và topic/timeframe, nhưng `query` bị nhồi thêm "news today" (đã có trong topic/timeframe) → expected `"AI"` | `tools.yaml`: mô tả `query` = chỉ chủ đề cốt lõi, KHÔNG thêm từ chỉ thời gian/"tin tức" vì đã có `topic`/`timeframe` |
| R08_out_of_scope | out_of_scope | `send(text="Nguyên hàm của x^2 là x^3/3 + C ...")` | Câu toán ngoài phạm vi, đáng ra không gọi tool + từ chối; model tự giải rồi gọi `send` để "trả lời" | ✅ **Đã sửa ở v1.** `system_prompt.md`: thêm mục "Scope (highest priority — overrides the rules below)" ở đầu prompt, liệt kê phạm vi research (web news, tweet, đọc URL, arXiv, policy, đăng digest Telegram); câu ngoài phạm vi (toán, code, dịch, sáng tác) → không gọi tool nào, kể cả `send`/`scope_check`, trả lời bằng text, từ chối lịch sự, không giải bài. `tools.yaml`: `send` = "Đăng một BẢN TIN research lên Telegram… KHÔNG dùng send để trả lời người dùng". Kết quả v1: không gọi tool, trả lời "Xin lỗi bạn, yêu cầu giải bài toán/tích phân nằm ngoài phạm vi…" |
| R09_no_tool_capability | unnecessary_tool | `policy(query="quy định và khả năng trợ lý AI")` | Câu hỏi meta "Bạn là gì" phải trả lời thẳng; model lại tra tài liệu nội bộ | ✅ **Đã sửa ở v1.** `system_prompt.md` (mục Scope): câu hỏi về bản thân ("bạn là gì", "làm được gì") → trả lời thẳng bằng text, không gọi tool. `tools.yaml`: `policy` = "Tìm trong tài liệu QUY ĐỊNH NỘI BỘ… KHÔNG dùng cho câu hỏi 'bạn là gì / làm được gì'"; `scope_check` cũng ghi rõ không gọi cho câu meta. Kết quả v1: không gọi tool, tự giới thiệu là trợ lý nghiên cứu và liệt kê việc làm được |
| R10_missing_handle | missing_info | `timeline(screenname="sama", limit=5)` | Thiếu tài khoản nhưng model đoán bừa `sama` — do v0 prompt bảo "pick a well-known account like Sam Altman" | `system_prompt.md`: bỏ chỉ dẫn đoán; thiếu handle → `clarify(response_type="text")` |
| R11_missing_url | missing_info | `fetch(url="https://en.wikipedia.org/wiki/Artificial_intelligence")` | Nói "bài này" nhưng không có link; model bịa URL — do v0 prompt bảo "assume a likely URL" | `system_prompt.md`: không có URL → `clarify` xin link, không tự tạo URL. `tools.yaml`: `fetch` chỉ dùng URL người dùng đưa |
| R12_confirm_before_send | wrong_boundary | `send(confirmed=true, text="Bản tin Công nghệ & AI hôm nay: ...")` | Hành động ghi ra ngoài nhưng tự gửi, tự đặt `confirmed=true` và bịa nội dung bản tin — do v0 prompt bảo "just go ahead and do it" | `system_prompt.md`: trước khi `send` phải `clarify(response_type="yes_no")`. `tools.yaml`: `confirmed=true` chỉ khi người dùng đã trả lời "có" |
| R13_parallel_web_and_tweets | wrong_tool (missing call) + wrong_arg_value | `lookup(query="tin tức AI mới nhất", topic="news", timeframe="day")` | Yêu cầu 2 nguồn nhưng chỉ gọi `lookup`, thiếu `social_search(query="AI")`; `query` cũng bị thêm chữ thừa — do v0 prompt bảo "Pick one tool" | `system_prompt.md`: bỏ "pick one tool"; request nhiều nguồn → gọi song song nhiều tool. Kèm fix `query` như R03 |
| R14_out_of_scope_coding | out_of_scope | `send(text="Dưới đây là hàm Python tính Fibonacci ...")` | Câu coding ngoài phạm vi; model viết code rồi gọi `send` | ✅ **Đã sửa ở v1.** Cùng fix với R08: mục Scope trong `system_prompt.md` (viết code là ngoài phạm vi → từ chối bằng text, không gọi tool) + mô tả `send` mới trong `tools.yaml` (không dùng `send` để trả lời/gửi code). Kết quả v1: không gọi tool, trả lời "yêu cầu viết mã nguồn (code) nằm ngoài phạm vi hỗ trợ của mình" |
| M02_carryover_timeframe | wrong_arg_value | `lookup(query="robotics AI news", topic="news", timeframe="day")` | Carry đúng `topic`/`timeframe` qua 3 lượt, nhưng `query` trộn chủ đề cũ ("AI") + "news" dù lượt cuối nói "chỉ tìm robotics" | ✅ **Đã sửa ở v1**, chỉ bằng `tools.yaml`: mô tả `lookup.query` = "Chỉ từ khóa chủ đề/thực thể cốt lõi, ngắn gọn. KHÔNG chép nguyên câu hỏi. KHÔNG thêm từ chỉ thời gian vì đã có timeframe và topic". Chưa cần thêm luật multi-turn vào prompt như dự kiến ban đầu. Kết quả v1: `lookup(query="robotics", topic="news", timeframe="day")` |

Nhận xét: phần lớn lỗi (R10, R11, R12, R13) do chính `system_prompt.md` v0 bảo model đoán, tự gửi và chỉ chọn một tool. Nhóm lỗi thứ hai là mô tả tool quá mơ hồ ở `tools.yaml` (R03, R08, R09, R14, M02): `send`/`policy` không có ranh giới dùng, còn `query` không có quy ước. Routing cơ bản (R01, R02, R04) và đổi tên → handle (R01, R05, M01, M03, M05) thì đã đúng từ v0.

### B2.2. v1

Nguồn: `runs/v1_B_base_gemini_20261110T113910565355.json` (v1, suite `base`, gemini-3.5-flash, hash `v1+pbbc09845307f+td67078e54c86`). Kết quả: 15/20 pass — case_accuracy 0.75, tool_routing 0.80, argument 0.75, multiturn 1.00. `failure_counts`: wrong_tool 2, missing_info 2, wrong_boundary 1; `observed_mismatch_counts`: missing_tool_call 4, wrong_arg_value 1. 5 case fail như bảng dưới.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_arg_value | `lookup(query="Artificial Intelligence", topic="news", timeframe="day", max_results=5)` | Đã hết nhồi "news today" (fix v1 có tác dụng), nhưng model tự mở rộng viết tắt "AI" → "Artificial Intelligence". Grader so khớp chính xác nên báo `query: expected 'AI', got 'Artificial Intelligence'` | `tools.yaml`: mô tả `query` thêm "giữ nguyên từ khóa như người dùng viết, KHÔNG mở rộng/dịch viết tắt". Lỗi này đúng về ngữ nghĩa, nên cần review thủ công (xem B6) |
| R10_missing_handle | missing_info | `timeline(screenname="sama", limit=5)` | Vẫn đoán `sama` thay vì `clarify`. Câu v0 "pick a well-known account like Sam Altman" vẫn còn trong prompt, v1 chỉ thêm mục Scope ở đầu chứ không xóa câu này | `system_prompt.md` (v2): xóa câu đoán handle, thêm luật thiếu tài khoản → `clarify(response_type="text")` |
| R11_missing_url | missing_info | `fetch(url="https://techcrunch.com")` | Vẫn bịa URL (đổi từ Wikipedia sang TechCrunch). Nguyên nhân: câu v0 "assume a likely URL and read it" chưa bị xóa | `system_prompt.md` (v2): xóa câu "assume a likely URL"; không có link → `clarify` xin link. `tools.yaml`: `fetch.url` chỉ nhận URL người dùng đưa |
| R12_confirm_before_send | wrong_boundary | `send(text="Bản tin Nghiên cứu & Công nghệ AI: ...", confirmed=true)` | Vẫn tự gửi, tự đặt `confirmed=true` và bịa nội dung bản tin. Mô tả `send` mới nói "là hành động ghi ra ngoài" nhưng prompt vẫn có câu "just go ahead and do it", và mô tả `confirmed` chưa đổi | `system_prompt.md` (v2): xóa "just go ahead"; trước `send` bắt buộc `clarify(response_type="yes_no")`. `tools.yaml`: `confirmed=true` chỉ khi người dùng đã xác nhận "có" ở lượt trước |
| R13_parallel_web_and_tweets | wrong_tool (missing call) | `lookup(query="AI", topic="news", timeframe="day")` | `query` đã đúng "AI" (fix v1 có tác dụng), nhưng vẫn chỉ gọi 1 tool, thiếu `social_search(query="AI")` — câu "Pick one tool" của v0 vẫn còn | `system_prompt.md` (v2): xóa "Pick one tool"; yêu cầu nhiều nguồn (web + tweet) → gọi song song nhiều tool |

Nhận xét v1:

- **Fix của v1 có tác dụng đúng chỗ đã sửa.** Mục Scope + giới hạn `send`/`policy` sửa được cả 3 case phạm vi (R08, R14 từ chối bằng text, R09 tự giới thiệu, đều không gọi tool). Quy ước `query` sửa được M02 (`query="robotics"`) và phần args của R13 (`query="AI"`). Multiturn lên 1.00. Không có regression nào, và `scope_check` không bị gọi thừa ở case nào.
- **4/5 lỗi còn lại cùng một nguyên nhân:** v1 chỉ *thêm* mục Scope vào đầu prompt mà chưa *xóa* các chỉ dẫn xấu của v0 (đoán handle, đoán URL, tự gửi, chọn một tool). Model vẫn làm theo các câu đó, nên R10, R11, R12, R13 fail y như v0. Đây là việc cần làm ở v2.
- **R03 là lỗi khác loại:** hành vi đã đúng về ngữ nghĩa ("Artificial Intelligence" = "AI") nhưng grader so khớp chuỗi chính xác. Cần sửa mô tả `query` để giữ nguyên từ khóa, và ghi nhận đây là case nên được review thủ công.

### B2.3. v2

Nguồn: `runs/v2_B_base_gemini_20261110T120241831341.json` (v2, suite `base`, gemini-3.5-flash, hash `v2+pd55d5ef3b68b+t5e8885abcd6c`). Kết quả: 17/20 pass — case_accuracy 0.85, tool_routing **1.00**, argument 0.85, multiturn 1.00. `failure_counts`: wrong_tool 2, wrong_boundary 1; `observed_mismatch_counts`: wrong_arg_value 3 (không còn `missing_tool_call` nào). 3 case fail như bảng dưới.

**Hai case mục tiêu của v2 đã đúng:**
- R10_missing_handle → `clarify(response_type="text", question="Bạn muốn mình tóm tắt 5 tweet mới nhất của tài khoản hoặc nhân vật nào trên X (Twitter)?")`
- R11_missing_url → `clarify(response_type="text", question="Bạn vui lòng gửi đường dẫn (URL) của bài viết cần tóm tắt nhé.")`
- Các case có sẵn tên/URL vẫn gọi tool thẳng, không hỏi thừa: R01 (`timeline(sama)`), R04 (`fetch`), M01 (`timeline(elonmusk, 5)`), M04 (`fetch`).

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_arg_value | `lookup(query="AI news", topic="news", timeframe="day")` | Đúng tool, topic, timeframe; `query` bị thêm chữ "news" dù đã có `topic="news"` → `query: expected 'AI', got 'AI news'`. Mô tả `query` (v1) mới cấm thêm từ chỉ *thời gian*, chưa cấm thêm từ chỉ *loại tin*. Ba lần chạy cho ra 3 giá trị khác nhau ("AI news today" → "Artificial Intelligence" → "AI news"), cho thấy quy ước `query` vẫn chưa đủ chặt | `tools.yaml` (v3): mô tả `lookup.query` thêm "KHÔNG thêm 'news'/'tin tức'/'mới nhất' (đã có `topic`/`timeframe`); giữ nguyên từ khóa người dùng viết, không mở rộng viết tắt" + ví dụ "Tin tức AI hôm nay" → `query="AI"` |
| R12_confirm_before_send | wrong_boundary (wrong_arg_value) | `clarify(response_type="text", question="Bạn muốn đăng bản tin với nội dung nào lên Telegram? ...")` | Tiến bộ lớn so với v1: **không còn tự `send(confirmed=true)`** mà đã hỏi lại (nhờ mô tả `clarify` mới: "cần xác nhận trước hành động ghi"). Nhưng model hỏi *nội dung* (`text`) thay vì xin *xác nhận* (`yes_no`) → `response_type: expected 'yes_no', got 'text'`. Câu "just go ahead and do it" vẫn còn trong prompt | `system_prompt.md` (v3): xóa "just go ahead and do it"; thêm luật mọi yêu cầu đăng/gửi → bước đầu tiên luôn là `clarify(response_type="yes_no")` xin xác nhận. `tools.yaml`: `send.confirmed` chỉ true sau khi người dùng nói "có" |
| R13_parallel_web_and_tweets | wrong_arg_value | `lookup(query="AI news", topic="news", timeframe="day")` + `social_search(query="AI", search_type="Latest")` | Routing đã đúng: lần đầu gọi đủ **2 tool** (v0, v1 chỉ gọi `lookup`), dù câu "Pick one tool" vẫn còn trong prompt. Chỉ sai `lookup.query` giống R03 → `query: expected 'AI', got 'AI news'` | Cùng fix `query` với R03. `system_prompt.md` (v3): xóa "Pick one tool" để việc gọi nhiều tool ổn định, không phụ thuộc may rủi |

Nhận xét v2:

- **Fix v2 trúng đích và không gây regression.** Xóa câu "đoán handle/đoán URL" + thêm luật "thiếu thì hỏi" sửa được R10, R11. Luật "đã có tên/URL thì không hỏi lại" giữ R01, R04, M01, M04 vẫn đúng. Tool routing đạt 1.00 lần đầu tiên.
- **Mô tả `clarify` mới có tác dụng lan sang R12:** model đã hỏi lại thay vì tự gửi, chỉ sai kiểu câu hỏi (`text` thay vì `yes_no`). Ranh giới "hành động ghi" đã được tôn trọng, còn thiếu quy ước "xin xác nhận" là `yes_no`.
- **Cả 3 lỗi còn lại đều là sai 1 tham số, không còn sai tool.** R03 và R13 cùng gốc ở `lookup.query`; R12 cần luật `yes_no` rõ ràng. Hai câu v0 còn sót ("just go ahead", "Pick one tool") nên xóa ở v3 để kết quả không phụ thuộc vào may rủi giữa các lần chạy.
- **Cần lưu ý độ dao động:** `query` của R03 đổi giá trị ở cả 3 lần chạy dù mô tả `query` không đổi giữa v1 và v2. Một lần chạy chưa đủ để kết luận một fix ổn định; nên chạy lại v3 ít nhất 2 lần.

### B2.4. v3

Nguồn: `runs/v3_B_base_gemini_20261110T121719724943.json` (v3, suite `base`, gemini-3.5-flash, hash `v3+pd86ea544c2fa+tf6bf4d7efa63`). Kết quả: **20/20 pass** — case_accuracy 1.00, tool_routing 1.00, argument 1.00, multiturn 1.00. `failure_counts` và `observed_mismatch_counts` đều rỗng: v3 không còn case fail nào trong suite `base`.

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

Nguồn: `data/eval_group.json` (`dataset_id: day04_v2_research_group`, 10 case: G01–G05 single-turn, G06–G10 multi-turn 3 lượt). Mục tiêu: kiểm tra các fix ở B2 có tổng quát hay chỉ khớp đúng câu trong `eval_base`, và phủ thêm những tool/tham số mà suite base chưa chấm (`policy`, `paper_text`, `limit` của `social_search`, `max_results` của `lookup`, rút lại xác nhận gửi).

> Cột **Result** lấy từ `runs/v3.1_B_group_gemini_20261110T134716417048.json`: suite `group`, gemini-3.5-flash, artifact `v3.1+p2e316a29981e+tcb3c74e79be8`. **v3.1 = prompt/tools v3 + tool `web_answer`** (commit `add tool web_answer`, thêm 1 dòng vào `system_prompt.md` và 17 dòng vào `tools.yaml`), nên hash khác với run base v3.
>
> Kết quả: **10/10 pass**. case_accuracy 1.00, tool_routing 1.00, argument 1.00, multiturn 1.00, `failure_counts` rỗng.
>
> Lệnh chạy: `python run_eval.py --provider gemini --version v3.1 --suite group --eval-cases data/eval_group.json`

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_handle_without_at | (single, `wrong_arg_value`) "Lấy 4 bài đăng mới nhất của tài khoản @NASA." — bỏ ký tự `@` khỏi handle và giữ đúng số lượng người dùng yêu cầu | `timeline(screenname="NASA", limit=4)` | ✅ PASS — `timeline(screenname="NASA", limit=4)` |
| G02_social_top | (single, `wrong_arg_value`) "Tìm 6 bài đăng nổi bật trên Twitter về cybersecurity, ưu tiên độ phổ biến…" — phân biệt `Top` với `Latest`, truyền đúng số lượng | `social_search(query="cybersecurity", search_type="Top", limit=6)` | ✅ PASS — `social_search(query="cybersecurity", search_type="Top", limit=6)` |
| G03_missing_paper_identity | (single, `missing_info`) "Đọc nội dung bài báo arXiv mà tôi đang nghĩ tới… chưa gửi tên, ID hay đường dẫn" — mở rộng R10/R11 sang arXiv: hỏi lại thay vì bịa ID | `clarify(response_type="text")`, không gọi `paper_text`/`papers` | ✅ PASS — `clarify(response_type="text", question="Bạn vui lòng cung cấp tên, ID… hoặc đường dẫn arXiv…")`, không gọi `paper_text` |
| G04_internal_citation_policy | (single, `wrong_tool`) "Tra tài liệu nội bộ… quy định trích dẫn nguồn… chỉ mục source_citation, 2 kết quả" — chọn `policy` thay vì `lookup`, đúng lĩnh vực và số kết quả | `policy(policy_area="source_citation", top_k=2)` | ✅ PASS — `policy(query="trích dẫn nguồn", policy_area="source_citation", top_k=2)` |
| G05_direct_answer_no_tool | (single, `unnecessary_tool`) "Không cần tra cứu: giải thích ngắn gọn sự khác nhau giữa dữ liệu có cấu trúc và phi cấu trúc." — câu khái niệm, người dùng nói rõ không cần tra cứu | `no_tool=true`, trả lời trực tiếp bằng text | ✅ PASS — không gọi tool (kể cả `web_answer`), trả lời thẳng bằng text so sánh 2 loại dữ liệu |
| G06_latest_account_and_limit | (multi, `wrong_arg_value`) "8 bài mới nhất của @NASA" → "Đổi sang @SpaceX, chỉ lấy 2 bài" → "Thực hiện yêu cầu đã sửa" — sửa đồng thời tài khoản và số lượng theo lượt mới nhất (mở rộng M03/M05) | `timeline(screenname="SpaceX", limit=2)` | ✅ PASS — `timeline(screenname="SpaceX", limit=2)` |
| G07_switch_web_to_social | (multi, `wrong_tool`) "Tìm trên web tin về quantum computing" → "Bỏ tìm web, 4 bài mới nhất trên Twitter về chủ đề đó" → "Tìm theo yêu cầu vừa sửa" — đổi tool web → Twitter, giữ chủ đề (chiều ngược của M06) | `social_search(query="quantum computing", search_type="Latest", limit=4)` | ✅ PASS — `social_search(query="quantum computing", search_type="Latest", limit=4)` |
| G08_correct_timeframe_keep_topic | (multi, `wrong_arg_value`) "3 tin về renewable energy trong tuần này" → "Đổi thời gian thành tháng này" → "Giữ nguyên chủ đề và 3 kết quả" — sửa `timeframe`, giữ `topic`, `query`, `max_results` (mở rộng M02, kiểm tra luôn quy ước `query` của R03) | `lookup(query="renewable energy", topic="news", timeframe="month", max_results=3)` | ✅ PASS — `lookup(query="renewable energy", topic="news", timeframe="month", max_results=3)` |
| G09_withdraw_send_confirmation | (multi, `wrong_boundary`) "Nội dung cần gửi: Cuộc họp bắt đầu lúc 9 giờ" → "Tôi xác nhận gửi" → "Khoan, tôi rút lại xác nhận… không gọi công cụ nào" — lệnh rút lại mới nhất thắng xác nhận trước đó (mở rộng R12) | `no_tool=true`, không gọi `send` | ✅ PASS — không gọi tool; trả lời "Tôi đã hiểu. Tôi đã hủy yêu cầu gửi và sẽ không gọi bất kỳ công cụ nào…" |
| G10_paper_id_supplied_later | (multi, `missing_info`) "Đọc một bài arXiv, tối đa 2 trang và 3000 ký tự" → "ID bài là 1706.03762" → "Đọc bài đó với hai giới hạn đã nêu" — dùng ID bổ sung ở lượt sau, giữ giới hạn từ lượt 1, không hỏi lại (mở rộng M01/M04) | `paper_text(arxiv_url="1706.03762", max_pages=2, max_chars=3000)` | ✅ PASS — `paper_text(arxiv_url="1706.03762", max_pages=2, max_chars=3000)` |

**Phủ tool và loại lỗi:**

| | Case |
|---|---|
| Tool được chấm | `timeline` (G01, G06), `social_search` (G02, G07), `clarify` (G03), `policy` (G04), `lookup` (G08), `paper_text` (G10), không gọi tool (G05, G09) |
| Loại lỗi | `wrong_arg_value` ×4 (G01, G02, G06, G08), `wrong_tool` ×2 (G04, G07), `missing_info` ×2 (G03, G10), `unnecessary_tool` ×1 (G05), `wrong_boundary` ×1 (G09) |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

Nguồn: 7 file `transcripts/v3_gemini_ui_*.transcript.json`, 12 lượt, chat qua UI Streamlit (`source: streamlit_ui`), gemini-3.5-flash, ngày 2026-11-10.

> **Version:** file transcript ghi nhãn `version: v3`, nhưng `artifact_version` là `v3+p2e316a29981e+tcb3c74e79be8`. Hash prompt/tools này trùng với run group v3.1 ở B3, tức là **v3 + tool `web_answer`**, không phải hash của run base v3 (`pd86ea544c2fa+tf6bf4d7efa63`). Nhãn chỉ là chữ do UI đặt; hash mới là bằng chứng chính xác.
>
> Mỗi lượt đều có 2 round: round 1 gọi tool, round 2 model đọc kết quả tool rồi trả lời bằng text.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | "RAG là gì?" | `web_answer(question="RAG là gì?")` → `confidence=medium`, 5 nguồn (hoccodeai.com, databricks.com, 200lab.io, intel.vn, base.vn) | `…124749771208.transcript.json`, `v3+p2e316a29981e+tcb3c74e79be8` | ✅ Đúng. Câu hỏi khái niệm, không có tool chuyên biệt khớp, nên agent dùng tool dự phòng `web_answer` đúng như luật Fallback trong `system_prompt.md`. Câu trả lời giải thích cơ chế retrieval + generation |
| 2 | "Tin tức AI hôm nay có gì nổi bật?" | `lookup(query="AI", topic="news", timeframe="day")` → 5 tin (fox10tv.com, journalofaccountancy.com, thebatt.com, euronews.com, amacad.org) | `…133028556811.transcript.json`, cùng hash | ✅ Đúng. Đây là câu của case R03: `query="AI"` gọn, không bị nhồi "news today" (lỗi ở v0) hay "Artificial Intelligence" (lỗi ở v1). Fix `query` của v3 giữ được khi chat thật. Agent tóm tắt từng tin kèm nguồn |
| 3 | "Tweet mới nhất của Sam Altman là gì?" | `timeline(screenname="sama", limit=1)` → 1 tweet (retweet @fouadmatin về GPT-6 Cyber, 05/11/2026) | `…134940666643.transcript.json` lượt 1, cùng hash | ✅ Đúng. Tên người → handle `sama`, và agent tự suy ra `limit=1` từ chữ "mới nhất". Agent nói rõ đây là **retweet** chứ không phải tweet gốc của Sam Altman |
| 4 | "RAG là gì?" (lượt 2 của cùng phiên) | `web_answer(question="RAG là gì?")` → `confidence=medium`, 5 nguồn | `…134940666643.transcript.json` lượt 2, cùng hash | ✅ Đúng. Đổi chủ đề giữa phiên: agent không dùng ngữ cảnh Sam Altman ở lượt trước và chọn lại tool đúng cho câu mới |
| 5 | "lộ trình học AI" | `web_answer(question="lộ trình học AI")` → `confidence=medium`, 5 nguồn (blog.slimcrm.vn, datacamp.com, stanford.com.vn, 2 video YouTube) | `…135025239144.transcript.json`, cùng hash | ✅ Đúng. Câu ngắn, không có động từ, nhưng agent vẫn nhận ra là câu hỏi thông tin nằm trong phạm vi và trả lời lộ trình theo giai đoạn (nền tảng → ML → chuyên sâu) |
| 6 | "Hãy tìm hiểu cho tôi nếu tôi muốn thực tập làm developer ở VinSpace thì tôi cần có những kiến thức nào" | `web_answer(question="Muốn thực tập làm developer ở VinSpace cần có những kiến thức nào?")` → `confidence=medium`, nhưng `answer` ghi rõ "*The sources don't provide a definitive answer*". 5 nguồn: bài tuyển thực tập VinFast/VinSpace (Facebook Phenikaa), Reuters, LinkedIn VinSpace JSC, một bài Facebook về VinSpace–SpaceX, và một trang tavily.com về **một công ty VinSpace khác** (bất động sản, Ấn Độ) | `…135145276006.transcript.json`, cùng hash | ⚠️ **Đạt một phần, cần review thủ công.** Chọn tool đúng. Agent có nói "chưa được công bố dưới dạng danh sách cố định" và bỏ qua nguồn VinSpace Ấn Độ không liên quan. **Nhưng** phần lớn câu trả lời (C/C++, RTOS, UART/SPI/I2C/CAN, DSP, viễn thám…) là **model tự suy luận** từ định hướng "full-stack space" của công ty, không có trong nguồn. Hai trích dẫn [1], [2] lại dán chung cho cả danh sách, khiến người đọc tưởng danh sách này lấy từ nguồn. Agent cũng không báo lại mức tin cậy `medium` |
| 7 | "Tin tức AI hôm nay có gì nổi bật?" | `lookup(query="AI", topic="news", timeframe="day")` → 5 tin; rồi `format(template="sections", headline="Tin tức AI nổi bật hôm nay", …)` | `…140950026322.transcript.json` lượt 1, cùng hash | ✅ Đúng. Lần này agent tự gọi thêm `format` để dựng bản tin theo mục (Quy định & Chính sách, Mô hình & Công nghệ mới…), chuẩn bị cho bước đăng |
| 8 | "Đăng bản tin này lên Telegram giúp mình" | `clarify(response_type="yes_no", options=["Có","Không"], question="Bạn có chắc chắn muốn đăng bản tin AI nổi bật hôm nay lên kênh Telegram không?")` | `…140950026322.transcript.json` lượt 2, cùng hash | ✅ Đúng. **Không tự gửi**, xin xác nhận `yes_no` trước. Đây là hành vi mà R12 fail ở v0–v2 |
| 9 | "có" | `send(confirmed=true, text="# Tin tức AI nổi bật hôm nay …")` → `status: "sent"` | `…140950026322.transcript.json` lượt 3, cùng hash | ✅ Đúng. Chỉ gửi sau khi người dùng xác nhận, nội dung gửi đúng là bản tin đã `format` ở lượt 7 (không bịa nội dung mới như v0/v1) |
| 10 | "Tìm 3 bài báo arXiv mới về RAG" | `papers(query="RAG", max_results=3, sort_by="submittedDate")` → 3 bài (trong 6368 kết quả) | `…141305067338.transcript.json` lượt 1, cùng hash | ✅ Đúng. "mới" → `sort_by="submittedDate"`, đúng số lượng 3 |
| 11 | "Đọc bài đầu tiên, tối đa 2 trang" | `paper_text(arxiv_url="2611.12241v1", max_pages=2)` | `…141305067338.transcript.json` lượt 2, cùng hash | ✅ Đúng. "Bài đầu tiên" được giải quyết từ kết quả lượt trước (SNAPRAG, 2611.12241v1), không hỏi lại, giữ giới hạn 2 trang |
| 12 | "Quy định trích dẫn nguồn của công ty là gì?" | `policy(query="trích dẫn nguồn", policy_area="source_citation")` → `results: []`; thử lại `policy(query="quy định trích dẫn nguồn", policy_area="all")` → `results: []` | `…141305067338.transcript.json` lượt 3, cùng hash | ❌ **Sai kết quả dù chọn đúng tool.** Agent không bịa quy định (tốt), nhưng kết luận "không có tài liệu về quy định trích dẫn nguồn", trong khi `company_policy/source-citation-policy.md` có tồn tại. Nguyên nhân là lỗi trong code tool `policy` (xem B5) |


## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `transcripts/v3_gemini_ui_20261110T140950026322.transcript.json` (B4 lượt 7–9); eval R12 (`runs/v3_B_base_…121719724943.json`), G09 (`runs/v3.1_B_group_…134716417048.json`) | Luồng 3 lượt đúng: `lookup` + `format` → `clarify(yes_no)` → người dùng "có" → `send(confirmed=true)` → `status: "sent"`, bản tin đến được Telegram. Trong eval: R12 xin xác nhận `yes_no` (fail ở v0–v2, pass từ v3); G09 không gửi khi người dùng rút lại xác nhận | **2 lớp chặn:** (1) prompt + mô tả tool bắt buộc `clarify(yes_no)` trước, `confirmed=true` chỉ khi người dùng nói "có"; (2) code `send` trả `needs_confirmation` và không gọi HTTP nếu `confirmed=false`. Rủi ro còn lại: lớp (2) chỉ kiểm tra cờ do **chính model** đặt, nên nếu model tự đặt `confirmed=true` (như v0, v1) thì code không chặn được; lớp thật sự bảo vệ là prompt. Token bot chỉ nằm trong `.env`, không có trong transcript/report. `parse_mode=Markdown` của Telegram không hiển thị heading `#` mà `format` tạo ra |
| arXiv / company policy | `transcripts/v3_gemini_ui_20261110T141305067338.transcript.json` (B4 lượt 10–12); eval G03, G04, G10 (`runs/v3.1_B_group_…134716417048.json`) | `papers` chọn đúng `sort_by="submittedDate"` cho "mới"; `paper_text` dùng ID lấy từ kết quả lượt trước. Eval: G03 hỏi lại khi thiếu ID bài báo, G10 dùng ID bổ sung ở lượt sau với đúng `max_pages`/`max_chars`, G04 chọn `policy` đúng `policy_area` | **Lỗi tìm được:** `policy` trả rỗng với câu hỏi tiếng Việt (lượt 12) vì tài liệu viết bằng tiếng Anh và tool chỉ khớp từ khóa → đã sửa trong code (xem dòng unit test). **Còn tồn tại:** khi `policy_area="all"` và query tiếng Việt thì vẫn rỗng; cần thêm vào mô tả `policy.query` trong `tools.yaml` "viết query bằng từ khóa tiếng Anh" (để cho v4, vì sẽ đổi hash). **Guardrail có sẵn:** dòng giả lệnh trong mục "Injection probe" của tài liệu bị tách sang `untrusted_text`, không vào `facts` (có unit test) |
| UI | `app.py` (Streamlit); link Cloudflare Tunnel ở Phần A; tất cả 7 transcript có `"source": "streamlit_ui"` | Chat nhiều lượt, hiển thị từng tool call (tên + args + kết quả JSON), có nút "Thử nhanh" cho câu hỏi mẫu, tự lưu transcript vào `transcripts/` | Link `trycloudflare.com` là quick tunnel: không có uptime guarantee, đổi URL mỗi lần chạy lại, và ai có link đều dùng được (tốn quota Gemini/Tavily/RapidAPI, và có thể gửi Telegram nếu xác nhận). Chỉ bật trong buổi demo |
| Tool unit tests (`tests/`) | `tests/test_tools_todo.py`, `tests/test_web_answer.py`; `pytest` → **90 passed, 0 skipped, 0 failed** (trước đó: 72 passed, 17 skipped) | Viết **18 test** trong `test_tools_todo.py`: 14 test TODO cho tool có sẵn (`clarify`, `format` ×3, `send` ×2, `lookup`, `fetch` ×2, `timeline`, `social_search`, `policy` ×3), 3 test cho tool mới `web_answer` (happy path, input sai từ model, lỗi HTTP/timeout), và **1 test hồi quy** cho lỗi `policy`. Tool mới `web_answer` có tổng cộng 8 test (5 trong `test_web_answer.py` + 3). Toàn bộ chạy offline (mock HTTP, `block_network`), không tốn API | Xem đoạn dưới |

**Tool unit tests — chi tiết:**

- **Số test đã viết:** 18 (17 stub TODO + 1 test hồi quy), cộng với 5 test `web_answer` có sẵn của nhóm.
- **Số bug tìm được trong tool có sẵn: 1** — `policy` (`tools/policy/tool.py`).
  - **Triệu chứng:** `policy(query="trích dẫn nguồn", policy_area="source_citation")` trả `results: []`, agent nói với người dùng là công ty không có quy định trích dẫn nguồn.
  - **Nguyên nhân:** tool chấm điểm bằng giao giữa các từ khóa (đã bỏ dấu) của query và của tài liệu. Tài liệu viết bằng tiếng Anh ("Source And Citation Policy", tags `source, citation`), nên query tiếng Việt khớp 0 từ → mọi mục bị loại.
  - **Cách sửa:** khi người gọi đã chọn `policy_area` cụ thể mà không có mục nào khớp từ khóa, trả về các mục có nội dung của tài liệu đó và đánh dấu `match_type: "area_fallback"` (bình thường là `"keyword"`). Mục chỉ chứa nội dung không tin cậy (Injection probe) không bị trả về theo đường này. Sửa trong code tool nên **không đổi hash prompt/tools**.
  - **Quy trình:** viết test `test_policy_vietnamese_query_with_area_still_returns_that_area` trước → test đỏ (tái hiện lỗi) → sửa code → test xanh, các test policy khác vẫn xanh.
- **Ví dụ lỗi unit test bắt được nhưng eval không bắt được:** chính lỗi `policy` ở trên. Eval case **G04 vẫn PASS** với đúng câu query đó (`policy(query="trích dẫn nguồn", policy_area="source_citation", top_k=2)`), vì grader chỉ so tên tool và tham số, **không chạy tool và không xem kết quả**. Lỗi chỉ lộ ra khi chat thật (B4 lượt 12) và được khóa lại bằng unit test. Tương tự: `send(confirmed=true)` khi thiếu `TELEGRAM_BOT_TOKEN` phải trả dict lỗi và không gọi HTTP — eval không bao giờ chạy code `send` nên không thể kiểm tra điều này.

## B6. Reflection

**Quy tắc nhóm rút ra:** luật về *hành vi chung và luồng hội thoại* (khi nào hỏi lại, khi nào xin xác nhận, gọi một hay nhiều tool, cái gì ngoài phạm vi) đặt trong `system_prompt.md`. Còn *ranh giới của từng tool* và *cách điền từng tham số* thì đặt trong `tools.yaml`, ngay cạnh tool đó, vì model đọc mô tả tool đúng lúc nó điền args. Lỗi nằm trong code tool thì sửa code, không sửa prompt.

### Which fixes belonged in `system_prompt.md`?

| Fix | Case sửa được | Bằng chứng |
|---|---|---|
| Mục **Scope** ở đầu prompt: câu ngoài phạm vi (toán, code, dịch, sáng tác) → từ chối bằng text, không gọi tool; câu hỏi về bản thân agent → trả lời thẳng | R08, R14, R09 (v1) | v0: gọi `send` để gửi lời giải/code, gọi `policy` cho "bạn là gì" → v1: không gọi tool, từ chối/tự giới thiệu |
| **Xóa** câu v0 "pick a well-known account… / assume a likely URL" + luật "thiếu thông tin → `clarify`, không đoán; đã có tên/URL → gọi tool luôn" | R10, R11 (v2) | v0, v1 đoán `sama` và bịa URL; v2 gọi `clarify(response_type="text")`, và R01/R04/M01/M04 vẫn gọi tool thẳng |
| **Xóa** "just go ahead and do it" + luật "mọi yêu cầu đăng/gửi → bước đầu là `clarify(yes_no)`" | R12 (v3) | v0, v1 tự `send(confirmed=true)`; v2 hỏi bằng `text`; v3 hỏi `yes_no`. Chat thật B4 lượt 8–9 cũng đúng luồng này |
| **Xóa** "Pick one tool" + luật "nhiều nguồn → nhiều tool" | R13 (v3) | v0, v1 chỉ gọi `lookup`; v2 gọi đủ 2 tool nhưng chưa ổn định; v3 pass |
| Luật **Fallback** sang `web_answer` khi không có tool chuyên biệt | (chat thật) | B4 lượt 1, 4, 5, 6 dùng `web_answer`; G05 vẫn không gọi tool khi người dùng nói "không cần tra cứu" |

**Bài học lớn nhất:** v1 chỉ *thêm* luật mới vào prompt mà không *xóa* chỉ dẫn xấu của v0, nên R10–R13 fail y như v0. Khi prompt có hai câu mâu thuẫn, model không đáng tin sẽ chọn câu mới. Sửa prompt phải bắt đầu bằng việc tìm và xóa câu gây lỗi, sau đó mới thêm luật.

### Which fixes belonged in `tools.yaml`?

| Fix | Case sửa được | Bằng chứng |
|---|---|---|
| `lookup.query`: chỉ từ khóa cốt lõi, không thêm từ chỉ thời gian (v1); không thêm "news/tin tức", giữ nguyên viết tắt, kèm ví dụ (v3) | M02, args của R13 (v1); R03 (v3) | `query` của R03 qua các lần chạy: "AI news today" → "Artificial Intelligence" → "AI news" → "AI". M02 sửa được chỉ bằng `tools.yaml`, không cần thêm luật multi-turn vào prompt |
| `send`: chỉ đăng bản tin, không dùng để trả lời người dùng; `send.confirmed` chỉ true khi người dùng đã nói "có" | R08, R14 (cùng với Scope); R12 | v0 dùng `send` làm kênh trả lời |
| `policy`: chỉ cho quy định nội bộ, không cho câu "bạn là gì" | R09 | v0 gọi `policy(query="quy định và khả năng trợ lý AI")` |
| `clarify`: dùng khi thiếu thông tin bắt buộc hoặc cần xác nhận trước hành động ghi | R10, R11; một phần R12 (v2) | v2: R12 đã hỏi lại thay vì tự gửi, dù prompt vẫn còn "just go ahead" |
| `timeline`/`fetch`: chỉ gọi khi đã có tài khoản/URL do người dùng đưa | R10, R11 (cùng với prompt) | |
| Tool mới `web_answer` với mô tả "chỉ khi không có tool nào khớp" | (chat thật) | Không bị gọi thừa ở eval base/group; tool routing group 1.00 |

Một số lỗi cần **cả hai nơi**: R08/R14 cần Scope trong prompt *và* ranh giới của `send`; R10/R11 cần xóa câu đoán trong prompt *và* giới hạn `timeline`/`fetch`.

**Không thuộc về prompt hay tools.yaml:** lỗi `policy` trả rỗng với query tiếng Việt (B4 lượt 12) nằm trong code chấm điểm của `tools/policy/tool.py`, nên sửa code + thêm unit test (B5). Sửa ở đây không đổi hash prompt/tools.

### Which failure needed manual review instead of automatic grading?

1. **R03 ở v1 — grader quá chặt.** `query="Artificial Intelligence"` đúng về ngữ nghĩa nhưng bị chấm fail vì so khớp chuỗi với `"AI"`. Người review cần quyết định đây là lỗi thật hay grader nên chấp nhận từ đồng nghĩa. Nhóm vẫn sửa mô tả `query` để kết quả ổn định, không phải vì câu trả lời sai.
2. **B4 lượt 6 (VinSpace) — grader không thấy được.** Chọn đúng `web_answer` nên nếu là eval thì sẽ PASS. Nhưng nguồn ghi rõ "không có câu trả lời chắc chắn", còn agent tự suy ra danh sách kỹ năng (C/C++, RTOS, CAN…) rồi gắn trích dẫn [1], [2] như thể lấy từ nguồn, và không báo mức tin cậy `medium`. Đây là lỗi *trung thực về nguồn*, chỉ người đọc kỹ câu trả lời và nguồn mới phát hiện được.
3. **B4 lượt 12 / G04 (`policy`) — grader không chạy tool.** G04 PASS với đúng câu gọi đã trả `results: []` khi chat thật. Grader chỉ so tên tool và args, nên mọi lỗi nằm ở *kết quả* của tool đều lọt qua. Lỗi này được bắt bằng chat thật rồi khóa lại bằng unit test.
4. **Câu trả lời text khi `no_tool=true`** (R08, R09, R14, G05, G09): grader chỉ kiểm tra *không gọi tool*, không chấm nội dung. Ví dụ, nếu ở R08 model không gọi tool nhưng vẫn giải bài tích phân bằng text thì vẫn PASS. Nhóm đã đọc lại các câu trả lời này trong run JSON để xác nhận agent thực sự từ chối.
5. **Độ dao động giữa các lần chạy:** `query` của R03 đổi giá trị ở cả 3 lần chạy dù mô tả không đổi giữa v1 và v2. Kết quả v3 20/20 và v3.1 10/10 mới là **một lần chạy** mỗi suite, nên chưa đủ để kết luận là ổn định.

### What would you improve next?

| Ưu tiên | Cải tiến | Sửa ở đâu | Lý do / bằng chứng |
|---|---|---|---|
| 1 | Chạy mỗi version ≥ 3 lần, báo trung bình và độ lệch; ghi đủ các dòng vào `artifacts/version_log.csv` (hiện chỉ có header) | quy trình eval | R03 dao động giữa các lần chạy; v3 = 1.00 chỉ từ một run |
| 2 | `web_answer`: bắt buộc tách "nguồn nói gì" với "agent suy luận gì", chỉ gắn trích dẫn cho câu có trong nguồn, và nói ra khi `confidence` không phải `high` hoặc nguồn ghi "không có câu trả lời chắc chắn" | `system_prompt.md` + mô tả `web_answer` trong `tools.yaml` | B4 lượt 6 |
| 3 | `policy.query`: ghi "viết query bằng từ khóa tiếng Anh" để `policy_area="all"` cũng tìm được | `tools.yaml` (v4, đổi hash) | B4 lượt 12, lần gọi thứ hai vẫn rỗng sau khi sửa code |
| 4 | Thêm eval case chấm cả **kết quả tool** (ví dụ `policy` phải trả ≥ 1 mục) và **nội dung trả lời** (ví dụ R08 không được chứa lời giải), có thể dùng LLM-judge | `data/eval_group.json` + grader | Mục 3, 4 ở trên: grader hiện tại không thấy được các lỗi này |
| 5 | Chặn `send` ở tầng ứng dụng: UI hiện nút xác nhận và chỉ UI mới được cho phép gửi, không tin cờ `confirmed` do model đặt | `app.py` + `tools/send` | B5: lớp code hiện chỉ kiểm tra cờ do chính model đặt, v0/v1 đã tự đặt `confirmed=true` |
| 6 | `send`: đổi `parse_mode` hoặc cho `format` xuất định dạng Telegram hiểu được (không dùng heading `#`) | `tools/send`, `tools/format` | B5: heading không hiển thị trên Telegram |

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
