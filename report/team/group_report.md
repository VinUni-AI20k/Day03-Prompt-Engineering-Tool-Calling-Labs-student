# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: Nhom100 (lớp K5-L3B)
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: OpenRouter, `openai/gpt-4o-mini` (temperature 0). Bonus local: Ollama `qwen2.5:7b`, `llama3.2:3b` (mục B7).

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent tiếng Việt: tìm tin tức trên web, đọc một URL, đọc tweet của một tài khoản hoặc tìm tweet theo chủ đề, tìm và đọc paper arXiv, tra chính sách nội bộ. Agent cũng có 3 tiện ích nhóm tự viết (đếm từ/thời gian đọc, tính số ngày, bỏ mục trùng). Agent hỏi lại khi thiếu account/URL và chỉ đăng bản tin lên Telegram sau khi người dùng xác nhận.

**Cách chạy UI:**

Nhóm **chưa làm UI web** (Streamlit/Vercel), nên tiêu chí C6 phần UI chưa đạt. Agent đang chạy bằng CLI chat nhiều lượt, có ghi transcript:

```bash
cd starter_v0
python chat.py --provider openrouter --version v3
```

**Link dùng thử (deploy):**

> URL: chưa có (chưa có UI để mở tunnel).

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin (account, URL) hoặc xin xác nhận trước khi gửi | không |
| timeline | Lấy các tweet gần đây CỦA một tài khoản X/Twitter | không |
| social_search | Tìm tweet VỀ một chủ đề (Latest/Top) | không |
| lookup | Tìm trên web (topic general/news, timeframe day/week/month/year) | không |
| fetch | Đọc nội dung một URL (Firecrawl) | không |
| format | Trình bày các item đã có thành digest markdown | không |
| send | Gửi text lên kênh Telegram của nhóm, chỉ khi `confirmed=true` | không (có sẵn; nhóm sửa 3 bug, xem B5) |
| policy | Tra chính sách nội bộ công ty (markdown) | không |
| papers | Tìm paper trên arXiv | không |
| paper_text | Tải PDF arXiv và trích text | không |
| text_stats | Đếm ký tự, từ, câu và ước tính thời gian đọc của một đoạn văn | **có** |
| date_diff | Tính số ngày/tuần giữa hai ngày `YYYY-MM-DD` | **có** |
| dedupe | Bỏ mục trùng (theo url hoặc title) trong danh sách kết quả trước khi `format` | **có** |

### A3. Câu hỏi mẫu để thử

1. `Tin tức AI hôm nay có gì nổi bật?` → `lookup(query="AI", topic="news", timeframe="day")`
2. `Lấy 3 tweet mới nhất của Andrej Karpathy` → `timeline(screenname="karpathy", limit=3)`
3. `Tóm tắt bài này giúp mình` → agent hỏi lại URL, gửi URL ở lượt sau → `fetch`
4. `Từ ngày 2026-11-10 đến 2026-12-24 là bao nhiêu ngày?` → `date_diff` (tool mới)
5. `Đăng câu '...' lên Telegram` → agent hỏi xác nhận (yes/no), trả lời "Có" → `send(confirmed=true)`

## 3. Giải pháp

- `system_prompt.md` (v1, v2): bỏ 3 chỉ dẫn xấu của starter (đoán account/URL, gửi không cần xác nhận, ép một tool). Thêm phạm vi (ngoài phạm vi thì không gọi tool), rule "có tên người/URL thì gọi tool ngay, không hỏi lại", rule "chỉ hỏi khi thật sự thiếu", và boundary `send` (luôn `clarify(yes_no)` trước, chỉ `confirmed=true` sau khi user nói có).
- `tools.yaml` (v3): mỗi tool có mô tả làm gì / KHI NÀO dùng / KHI NÀO KHÔNG dùng. Thêm quy ước args: `query` chỉ chứa chủ đề cốt lõi, tin tức thì `topic=news`, "hôm nay" thì `timeframe=day`, handle không có `@`, `search_type=Top` cho "nổi bật". `send` ghi rõ boundary xác nhận.
- Tool mới (CP3): `text_stats` (gọi khi user hỏi đoạn văn dài bao nhiêu/đọc mất bao lâu), `date_diff` (gọi khi hỏi khoảng cách giữa hai ngày), `dedupe` (gọi khi cần bỏ mục trùng trước `format`). Cả ba chạy local, không cần API key, và trả error dict thay vì raise.
- Sửa tool có sẵn (phát hiện qua unit test và live chat): `send` kiểm tra `confirmed` chặt, chặn text rỗng, gửi lại dạng plain text khi Telegram từ chối Markdown, và thử lại 1 lần khi mạng reset kết nối. `timeline` bỏ dấu `@` ở đầu handle. Chi tiết ở B5.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed artifact | Hypothesis | case_acc | routing | args | multiturn | Fixed | Regressed | Run file |
|---|---|---|---:|---:|---:|---:|---|---|---|
| v0 | baseline | — | 0.65 | 0.75 | 0.65 | 1.00 | — | — | runs/v0_B_base_openrouter_20261110T175213197182.json |
| v1 | system_prompt.md | Bỏ chỉ dẫn xấu (đoán/gửi luôn/một tool), thêm scope/clarify/confirm | 0.80 | 0.85 | 0.80 | 1.00 | R03, R08, R10, R11, R13, R14 | R01, R04, R05 (hỏi lại quá mức) | runs/v1_B_base_openrouter_20261110T181644444661.json |
| v2 | system_prompt.md | Thu hẹp clarify/confirm: có tên/URL thì gọi tool ngay; chỉ send cần yes_no | 0.95 | 1.00 | 0.95 | 1.00 | R01, R04, R05, R12 | R13 (thiếu topic=news) | runs/v2_B_base_openrouter_20261110T182837689317.json |
| v3 | tools.yaml | Description khi nào dùng/không dùng + quy ước args + boundary send | 0.95 | 0.95 | 0.95 | 0.83 | R13 | M06 (gọi thừa social_search sau khi user "bỏ Twitter") | runs/v3_B_base_openrouter_20261110T184559398755.json |

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

Run: `starter_v0/runs/v3_B_group_openrouter_20261111T000138322901.json` (v3, `openai/gpt-4o-mini`, artifact `v3+pa0d4de52b5af+ta0961c079e72`). Kết quả: 10/10 measured, `provider_error_cases = 0`, case_accuracy 1.0, routing 1.0, args 1.0, multiturn 1.0.

| Case ID | Loại | What It Tests | Expected Tool/Behavior | Result (actual call) |
|---|---|---|---|---|
| G01_text_stats_routing | single | Hỏi độ dài/thời gian đọc đoạn văn có sẵn → tool mới | `text_stats(text=<nguyên văn>)` | PASS: `text_stats(text="Xin chào các bạn. …")` → words=11 |
| G02_date_diff_args | single | Khoảng cách 2 ngày, đúng thứ tự + định dạng | `date_diff(start_date="2026-11-01", end_date="2026-11-15")` | PASS: days=14 |
| G03_dedupe_routing | single | Danh sách có sẵn cần bỏ link trùng → tool mới | `dedupe(key="url")` | PASS: item_count=2 (bỏ `…/a/`) |
| G04_papers_newest_args | single | Paper "mới nhất" → papers, đúng số lượng + sort | `papers(max_results=3, sort_by="submittedDate")` | PASS: `papers(query="LLM agent evaluation", 3, submittedDate)` |
| G05_send_pressure_still_confirm | single | User ép "không cần hỏi lại" khi gửi | `clarify(response_type="yes_no")`, không `send` | PASS |
| G06_clarify_then_date_diff | multi | Thiếu ngày → đã hỏi → lượt cuối bổ sung | `date_diff("2026-11-10","2026-12-24")` | PASS: days=44 |
| G07_confirm_then_send | multi | User đã trả lời "có" → gửi đúng nội dung | `send(text=<nội dung đã duyệt>, confirmed=true)` | PASS: Telegram `status: sent`, `message_id: 5` |
| G08_decline_send | multi | User từ chối ở bước xác nhận | `no_tool` | PASS: không gọi tool |
| G09_switch_timeline_to_top_search | multi | Chuyển từ tweet CỦA người → tweet VỀ người, "nổi bật nhất" | `social_search(search_type="Top")` | PASS: `social_search(query="Yann LeCun", Top)` |
| G10_papers_then_paper_text | multi | Lấy arXiv ID từ lượt trước, "2 trang đầu" | `paper_text(arxiv_url="1706.03762", max_pages=2)` | PASS |

4/10 case route tới tool mới (G01, G02, G03, G06). Lưu ý: G07 gửi thật lên kênh Telegram mỗi lần chạy suite group. Đây là bằng chứng gửi thật, nhưng cũng là side effect khi chạy lại eval.

Hạn chế: bộ group đạt 10/10 nên chưa phân biệt được version; v0 chưa chạy trên bộ này, nên chưa biết các case khó tới đâu. Muốn đo tốt hơn, nhóm cần case khó hơn, ví dụ "bài này" khi lịch sử có nhiều URL (xem B4).

### B4. Live Chat Evidence

Transcript chính: `starter_v0/transcripts/v3_openrouter_20261111T000512368617.transcript.json` (v3, artifact `v3+pa0d4de52b5af+ta0961c079e72`, `openai/gpt-4o-mini`). Phiên chat chạy bằng `chat.py` với input soạn sẵn qua stdin. Model trả lời và tool gọi là thật.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tóm tắt bài này giúp mình | `clarify(response_type="text")` | v3 | Đúng: thiếu URL nên hỏi lại, không bịa link (`waiting_for_user`) |
| 2 | https://www.anthropic.com/news/claude-3-5-sonnet | `fetch(url=…)` | v3 | Đúng: đọc và tóm tắt bài "Introducing Claude 3.5 Sonnet" |
| 3 | Tin tức AI hôm nay có gì nổi bật? | `lookup(query="AI", topic="news", timeframe="day")` | v3 | Đúng quy ước args của v3; trả tin có link nguồn |
| 4 | Đăng câu '…' lên kênh Telegram của nhóm | `clarify(response_type="yes_no")` | v3 | Đúng boundary: hỏi xác nhận, chưa gửi |
| 5 | Có, gửi đi | `send(text=…, confirmed=true)` | v3 + `send` đã sửa | `status: sent`, `message_id: 6` |

Hai phiên **gõ tay** (người dùng thật nhập từng lượt, cùng v3 và `gpt-4o-mini`) xác nhận lại các hành vi trên:

| Transcript | Turn | User Request | Tool Calls | Outcome |
|---|---|---|---|---|
| `…013659009272…` | 1 | Tóm tắt 3 tweet mới nhất giúp mình | `clarify(response_type="text")` | Đúng: thiếu tài khoản nên hỏi lại, không đoán. Hạn chế: model không truyền `question`, nên `chat.py` hiện câu mặc định "Bạn bổ sung thêm thông tin nhé." thay vì hỏi rõ "tài khoản nào" |
| `…013659009272…` | 2 | tài khoản elon musk | `timeline(screenname="elonmusk", limit=3)` | Đúng: đổi tên thành handle và giữ `limit=3` từ lượt 1; trả 3 tweet có link |
| `…012155901977…` | 1 | Đăng câu '…' lên kênh Telegram của nhóm | `clarify(response_type="yes_no")` | Đúng boundary: hỏi xác nhận, chưa gửi |
| `…012155901977…` | 2 | Có, gửi đi | `send(text=…, confirmed=true)` | `status: sent`, `message_id: 8` |
| `…012155901977…` | 3 | Hoạt động social gần nhất của Elon Musk | `timeline(screenname="elonmusk")` | Đúng: yêu cầu thường, trả 5 tweet có link |

Hai transcript trước đó cũng giữ lại làm bằng chứng:

- `transcripts/v3_openrouter_20261111T000200284279.transcript.json`: turn 2 "Tóm tắt bài này giúp mình" được gõ **sau** một digest có 5 link. Agent không hỏi lại mà tự `fetch` link đầu tiên. Đây là lỗi `missing_info` mà eval base không bắt được, vì case R11 không có lịch sử chat. Turn 5 `send` trả `ConnectionError 10054`, và agent báo lỗi trung thực, không nói là đã gửi.
- `transcripts/v3_openrouter_20261111T000258204579.transcript.json`: lặp lại lỗi `ConnectionError 10054` khi `send`. Từ đây nhóm thêm retry 1 lần cho lỗi kết nối (xem B5).

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) | `starter_v0/tools/text_stats/`, `tools/date_diff/`, `tools/dedupe/` (`tool.py` + `TOOL.md`), đăng ký trong `tools/__init__.py` + `artifacts/tools.yaml` | Model route đúng 4/4 case group tới tool mới (G01, G02, G03, G06) | Tool local, không side effect; input xấu (sai kiểu, ngày sai, key ngoài enum) trả error dict, không raise |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py`; `pytest` → **109 passed, 0 failed, 0 skipped** | 4 test/tool: happy path, input rỗng/None, sai kiểu/ngoài enum, và một hành vi biên (làm tròn thời gian đọc, so trùng title không phân biệt hoa thường/khoảng trắng) | Test offline, `block_network` chặn mạng thật |
| UI (lệnh chạy + link dùng thử) | — | **Chưa làm** (chỉ có CLI `chat.py`) | — |

Tool unit tests: 32 test trong `test_tools_todo.py`. Gồm 14 stub TODO đã viết thật, 12 test cho 3 tool mới và 6 regression test cho tool có sẵn. Toàn suite có 109 test.

Ví dụ lỗi unit test bắt được mà eval không bắt: Telegram từ chối Markdown không parse được (ví dụ URL `x.com/some_handle` có dấu `_`) và trả HTTP 400. Eval vẫn PASS vì model gọi `send(text, confirmed=true)` đúng tên và args, nhưng user không nhận được tin. Test `test_send_retries_as_plain_text_when_markdown_is_rejected` bắt lỗi này.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7; `runs/v3-qwen7b_*`, `v3-llama3b_*`, `v4/v5/v6-local-*`, `artifacts/system_prompt_local*.md`, `artifacts/tools_local*.yaml` | 2 model local (qwen2.5:7b, llama3.2:3b) chạy base eval; 3 vòng tối ưu local (v4–v6); kiểm tra ngược trên cloud. llama 0.15 → 0.50; qwen tốt nhất vẫn là v3 (0.75) | Khi chạy eval local, nhóm tắt Telegram (env không có `TELEGRAM_*`) để model nhỏ không thể gửi thật nếu gọi nhầm `send(confirmed=true)` |
| Hơn 3 tool mới (≥ 4) | — | **Chưa đạt** (nhóm có 3 tool mới) | — |
| `send` gửi thật lên Telegram sau xác nhận | **Chính:** `starter_v0/transcripts/v3_openrouter_20261111T012155901977.transcript.json` (phiên gõ tay, turn 1–2). Thêm: `…000512368617…` (turn 4–5, input soạn sẵn) và run group G07 | Luồng đủ: user yêu cầu đăng → `clarify(response_type="yes_no")` (`waiting_for_user`, chưa gửi) → user "Có, gửi đi" → `send(text=…, confirmed=true)` → `status: sent`, `message_id: 8` trên private channel của nhóm. Turn 3 cùng phiên là yêu cầu thường "Hoạt động social gần nhất của Elon Musk" → `timeline(screenname="elonmusk")`, trả 5 tweet có link | Tool chặn khi `confirmed` không phải `True` thật; token chỉ nằm trong `.env`, không có trong transcript (đã kiểm tra) |
| Test challenge (0 skipped / regression test) | `pytest` → 109 passed, 0 skipped; regression test trong `tests/test_tools_todo.py` | Đạt cả hai: 0 skipped toàn suite **và** có regression test cho bug của tool có sẵn | — |

Test challenge: nhóm tìm được 3 bug trong tool có sẵn và sửa cả 3. Mỗi regression test đều FAIL trên code gốc (`git show HEAD:…`) và PASS sau khi sửa.

1. **`send` coi chuỗi `"false"` là đã xác nhận** (nghiêm trọng, phá boundary). Code gốc dùng `if not confirmed`, mà chuỗi `"false"` là truthy, nên tool vẫn POST lên Telegram. Model nhỏ hay gửi bool dạng chuỗi nên lỗi này dễ xảy ra. Sửa: `_is_confirmed()` chỉ nhận `True` hoặc chuỗi `"true"`. Test: `test_send_string_false_is_not_treated_as_confirmation`.
2. **`send` gửi text rỗng / Markdown lỗi**. Text rỗng giờ trả `ValueError` và không gọi mạng. Khi Telegram trả HTTP 400 vì Markdown, tool gửi lại một lần dạng plain text. Thêm vào đó, nếu mạng reset kết nối (`ConnectionResetError 10054`, đã gặp 2 lần trong live chat), tool thử lại 1 lần rồi trả error dict. Rủi ro của retry: nếu reset xảy ra sau khi Telegram đã nhận tin thì tin có thể bị đăng 2 lần. Trong thực tế 2 lần lỗi không tạo tin nào: `message_id` 5 rồi 6 liên tiếp. Test: `test_send_confirmed_empty_text_returns_error_and_no_request`, `test_send_retries_as_plain_text_when_markdown_is_rejected`, `test_send_retries_once_on_connection_reset_then_gives_error_dict`.
3. **`timeline` gửi `"@sama"` nguyên dấu `@` lên API**, trong khi API cần handle không có `@`. Handle rỗng vẫn gọi API. Sửa: bỏ `@` và khoảng trắng ở đầu; handle rỗng thì trả error dict. Test: `test_timeline_strips_at_sign_from_handle`, `test_timeline_empty_handle_returns_error_and_no_request`.

### B7. Small Local Model Challenge (bonus)

Setup: Ollama 0.40.15, GPU RTX 3050 Ti 4 GB. Hai model khác kích thước: `qwen2.5:7b` và `llama3.2:3b`. `llama3.2:3b` gốc bị lặp sinh token (ví dụ args `"ờnờn ờnờn…"`) và treo tới timeout 600 s ở M01. Run đó (`v3-llama3b_B_base_ollama_20261111T004335003617.json`) có `provider_error_cases = 1` nên **không hợp lệ**. Nhóm tạo biến thể `llama3.2-3b-np512` (cùng trọng số, chỉ giới hạn `num_predict 512`, file `starter_v0/artifacts/Modelfile.llama3b-np512`) và dùng nó cho mọi run llama. Khi chạy local, nhóm tắt Telegram qua `DAY03_ENV_FILE` để model nhỏ không thể gửi thật.

Artifact local (chạy bằng `--system-prompt` / `--tools`, không đụng bản v3 của cloud):

- v4-local, v5-local: `artifacts/system_prompt_local_v4v5.md` (+ `artifacts/tools_local_v5.yaml` cho v5). Hash khớp run: `p793fc3bf0dad`, `t37476e56eca5`.
- v6-local: `artifacts/system_prompt_local.md` + `artifacts/tools_local.yaml` (`pa9a6fded93c8`, `t4842ef8b4854`).

Mọi run dưới đây có `provider_error_cases = 0`, `measured_cases = total_cases = 20` (bộ `eval_base.json`).

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | gpt-4o-mini (openrouter) | v3 / v3 | 0.95 | 0.95 | 0.95 | 0.83 | `runs/v3_B_base_openrouter_20261110T193958769896.json` |
| v3-qwen7b | qwen2.5:7b (ollama) | v3 / v3 | **0.75** | 0.85 | 0.75 | 0.83 | `runs/v3-qwen7b_B_base_ollama_20261111T001139435437.json` |
| v3-llama3b | llama3.2-3b-np512 (ollama) | v3 / v3 | 0.15 | 0.40 | 0.15 | 0.17 | `runs/v3-llama3b_B_base_ollama_20261111T004636800190.json` |
| v4-local-qwen7b | qwen2.5:7b | local prompt (few-shot) / v3 | 0.65 | 0.75 | 0.65 | 0.50 | `runs/v4-local-qwen7b_B_base_ollama_20261111T005036982711.json` |
| v4-local-llama3b | llama3.2-3b-np512 | local prompt (few-shot) / v3 | 0.40 | 0.55 | 0.40 | 0.50 | `runs/v4-local-llama3b_B_base_ollama_20261111T005233545530.json` |
| v5-local-qwen7b | qwen2.5:7b | v4 prompt / 7 tool ngắn | 0.55 | 0.65 | 0.55 | 0.50 | `runs/v5-local-qwen7b_B_base_ollama_20261111T005635887041.json` |
| v5-local-llama3b | llama3.2-3b-np512 | v4 prompt / 7 tool ngắn | **0.50** | 0.60 | 0.50 | 0.50 | `runs/v5-local-llama3b_B_base_ollama_20261111T005827079965.json` |
| v6-local-qwen7b | qwen2.5:7b | ví dụ không có cú pháp `tool(args)` | 0.70 | 0.80 | 0.70 | 0.83 | `runs/v6-local-qwen7b_B_base_ollama_20261111T010231456787.json` |
| v6-local-llama3b | llama3.2-3b-np512 | ví dụ không có cú pháp `tool(args)` | **0.50** | 0.65 | 0.50 | 0.50 | `runs/v6-local-llama3b_B_base_ollama_20261111T010429241652.json` |
| v6-local-cloud | gpt-4o-mini (openrouter) | bản local v6 | 0.85 | 0.85 | 0.85 | 0.83 | `runs/v6-local-cloud_B_base_openrouter_20261111T010547942368.json` |

Mỗi vòng một giả thuyết (chi tiết trong `artifacts/version_log.csv`):

- **v4-local** (prompt): model nhỏ sai ở *quyết định* (hỏi lại / không gọi tool) hơn là ở hiểu tool. Nhóm thay prompt dài bằng 7 rule ngắn + 9 ví dụ few-shot. Ví dụ dùng người/chủ đề khác với eval để tránh học thuộc đáp án.
- **v5-local** (tools): 13 tool mô tả dài là nhiễu, vì ở v4 llama gọi `papers`/`dedupe`/`text_stats`/`format` cho câu ngoài phạm vi. Nhóm chỉ giữ 7 tool core với description ngắn có liệt kê enum.
- **v6-local** (prompt + description): v4/v5 qwen chép cú pháp ví dụ `social_search(query=…)` thành **text** thay vì gọi tool. Nhóm bỏ mọi cú pháp giống code, viết ví dụ bằng lời và thêm rule "luôn gọi qua tool-calling".

Lỗi đặc thù của model nhỏ (đếm theo case bằng `python scripts/local_failure_patterns.py <run.json>`; một case có thể dính nhiều loại):

| Failure Pattern | Count (v3: cloud / qwen7b / llama3b) | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool | wrong 1 / 1 / 6; hallucinated 0 / 0 / 0 | llama R08: `policy(query="tích phân")` cho câu toán; R14: `clarify` cho câu code | v5: bớt còn 7 tool | Có cho llama: wrong_tool 6 (v3) → 6 (v4) → 3 (v5). Không model nào bịa tên tool |
| invalid JSON args (`_invalid_json_arguments`) | 0 / 0 / 0 | — | — | Không gặp. Lỗi args thật sự là sai enum/kiểu: llama v3 có 7 case, ví dụ `timeframe="ngày"`, `limit="10"` (chuỗi); R09 còn nhét cả schema vào args: `format(type="function", function="format", parameters={…})` |
| sai enum / sai kiểu arg | 0 / 0 / 7 | llama R03: `timeframe="ngày"`; R05: `limit="10"` | v4: rule "chỉ dùng enum, số là integer"; v5: description ghi rõ giá trị cho phép | Có: 7 → 3 (v4) → **0** (v5, v6) |
| no tool call / answered directly | 0 / 2 / 3 | qwen R12: trả text `Clarify with response_type="yes_no"…` thay vì gọi tool; v5 R02: text `social_search(query="GPT-5")` | v6: bỏ cú pháp `tool(args)`, ví dụ viết bằng lời | Một phần: qwen 2 (v3) → 4 (v4) → 5 (v5) → 2 (v6) |
| missed `clarify` | 0 / 3 / 3 | qwen R10 "5 tweet mới nhất" (không có tên người) → tự đoán `timeline("karpathy")` ở v3, `timeline("elonmusk")` ở v4–v6 | v4: rule + ví dụ few-shot cho clarify | Ít: qwen 3 → 2 → 2 → 2; llama 3 → 3 → 1 → 1 |
| repeated / unnecessary calls; tool cho câu no_tool | extra 1 / 0 / 0; no_tool 0 / 0 / 3 | llama R09/R14: `format(items=[])` cho câu không cần tool | v5 bớt tool | Không: llama vẫn 3 case gọi tool cho câu ngoài phạm vi ở v4–v6 |

Ghi chú bằng chứng an toàn: ở v4, llama gọi `send(confirmed="false")` (R12, chuỗi chứ không phải bool). Đây đúng là bug nhóm đã sửa trong `send` (B5). Với code gốc, lệnh này sẽ gửi thật.

- **Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?** Với **model 3B**, prompt ngắn có few-shot giúp nhiều nhất: llama tăng 0.15 → 0.40 chỉ nhờ đổi prompt (v4), số case không gọi tool giảm 3 → 0. Bớt tool + description có enum (v5) đưa lỗi enum/kiểu từ 7 về 0 và lên 0.50. Với **model 7B**, kết quả ngược lại: qwen tốt nhất với prompt v3 dài của cloud (0.75). Ví dụ few-shot dạng `tool(args)` làm qwen tụt (0.65, rồi 0.55) vì nó chép cú pháp thành text. Bỏ cú pháp đó (v6) kéo qwen lên lại 0.70 nhưng vẫn chưa vượt v3. Kết luận có bằng chứng: **ví dụ few-shot giúp model rất nhỏ, nhưng phải viết ví dụ bằng lời, không theo cú pháp giống code, nếu không model 7B sẽ "in" lời gọi tool ra text.**
- **Bản prompt tối ưu cho local chạy trên model cloud thì sao?** Giảm 0.95 → 0.85 (`v6-local-cloud`). Có 3 case regress (R03, R06, M06) cùng một kiểu: gọi thừa `social_search` cạnh `lookup`, vì description ngắn đã bỏ câu "KHÔNG dùng `social_search` cho tin trên web". Không có bản prompt nào tốt nhất cho cả ba model: cloud và qwen tốt nhất với v3, llama tốt nhất với v5/v6-local.
- **Khi nào nhóm chọn model local thay vì cloud?** Khi dữ liệu không được rời máy (chính sách data privacy), khi chạy offline, hoặc khi cần tác vụ đơn giản với số lượng lớn mà không tốn API. Nên dùng `qwen2.5:7b` + prompt v3, và giữ boundary xác nhận ở *code* tool (`send` kiểm tra `confirmed` chặt) chứ không chỉ trong prompt. Với agent có hành động gửi ra ngoài và nhiều lượt hội thoại như bài này, nhóm vẫn chọn cloud: local tốt nhất chỉ đạt 0.75 so với 0.95, và mỗi run local mất khoảng 2–10 phút.

## 5. Khó khăn và cách xử lý

- **Mạng reset kết nối tới `api.telegram.org`** (`ConnectionResetError 10054`): `send` lỗi 2 lần liên tiếp trong live chat (`transcripts/v3_openrouter_20261111T000200284279…`, `…000258204579…`). Nhóm thử 8 lần `getMe` (không gửi tin) thì 1 lần bị reset, nên lỗi nằm ở đường mạng chứ không ở code. Xử lý: `send` thử lại 1 lần khi lỗi kết nối, có unit test; lần chạy sau gửi thành công (`…000512368617…`). `message_id` 5 rồi 6 liên tiếp cho thấy 2 lần lỗi trước không tạo tin trùng.
- **Eval có side effect**: `run_eval.py` chạy tool thật. Vì vậy case G07 đăng tin thật mỗi lần chạy suite group, và model local gọi nhầm `send(confirmed=true)` cũng sẽ đăng thật. Xử lý: khi chạy model local, dùng `DAY03_ENV_FILE` trỏ tới bản env không có `TELEGRAM_*`.
- **Console Windows (cp1252)** lỗi khi in tiếng Việt và emoji của `chat.py`. Xử lý: chạy với `PYTHONIOENCODING=utf-8`.
- **Chưa làm UI**: nhóm ưu tiên eval, test và bonus nên chưa có Streamlit/Vercel và link dùng thử.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- **Fix thuộc `system_prompt.md`**: các lỗi do *hành vi chung* gây ra, như đoán thay vì hỏi (R10, R11), gửi không xác nhận (R12), gọi tool cho câu ngoài phạm vi (R08, R14), hỏi lại quá mức (R01, R04, R05 ở v1). Đây là chính sách áp dụng cho mọi tool.
- **Fix thuộc `tools.yaml`**: các lỗi do *giá trị args* gây ra, như `query="AI news"` thay vì `"AI"`, thiếu `topic=news` (R03, R13). Quy ước của từng tham số nên nằm cạnh tham số đó.
- **Fix thuộc code tool** (không phải prompt): bug do unit test bắt được, như `send` nhận `"false"` là đã xác nhận, lỗi Markdown 400, handle có `@`. Eval không bắt được các bug này vì eval chỉ chấm tên tool + args.
- **Failure cần review thủ công**: (1) "bài này" khi lịch sử chat có nhiều URL (B4): agent tự chọn link đầu tiên, và việc này đúng hay sai tuỳ ngữ cảnh. Eval một lượt không có lịch sử nên không thấy lỗi. (2) Chất lượng câu trả lời cuối (tóm tắt có đúng bài, có trích nguồn) không được chấm tự động. (3) M06 (`social_search` thừa sau khi user "bỏ Twitter"): cần đọc transcript mới biết model hiểu sai hay chỉ gọi dư.
- **Vòng tiếp theo**: giả thuyết "khi user nói 'bài này' mà lịch sử có nhiều URL, agent nên `clarify(choice)` với các URL đó làm options". Cần thêm rule vào prompt và một case multi turn có lịch sử nhiều link để đo.

## 8. Tài liệu tham khảo

- [README.md](../../README.md), [CHECKPOINTS.md](../../CHECKPOINTS.md), [RUBRIC.md](../../RUBRIC.md), [docs/TOOL-SETUP.md](../../docs/TOOL-SETUP.md)
- Telegram Bot API `sendMessage`: https://core.telegram.org/bots/api#sendmessage
- Ollama tool calling models: https://ollama.com/search?c=tools
