# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: ABC
- Members: Nguyễn Hoàng Văn Tiến Mạnh, Nguyễn Thị Thu Hà, Lê Hoàng An
- Provider/model: OpenRouter · `openai/gpt-4o-mini` (artifact `v6`)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent tiếng Việt: tìm **tin tức trên web**, **tweet** (theo tài khoản hoặc theo chủ đề), **bài trên Hacker News**, **đọc và tóm tắt một URL**. Agent **hỏi lại** khi thiếu tài khoản/URL, **xin xác nhận** trước khi đăng lên Telegram, và **từ chối** việc ngoài phạm vi (giải toán, viết code, viết email).

Kết quả eval: base **0.65 → 0.95** (v0 → v6, routing 1.0); bộ eval nhóm tự viết **10/11** (case còn lại cố ý giữ để ghi nhận câu hỏi mơ hồ, xem B6).

**Link dùng thử (deploy):**

> URL: https://suited-reminder-accordingly-blocked.trycloudflare.com
>
> (Cloudflare quick tunnel, chỉ sống trong buổi demo 10/11/2026)

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại user khi thiếu handle/URL, hoặc xin xác nhận (yes/no) trước khi đăng | không |
| timeline | Lấy N tweet mới nhất của một tài khoản X (vd. `sama`, `elonmusk`) | không |
| social_search | Tìm tweet theo chủ đề, sắp xếp Latest hoặc Top | không |
| lookup | Tìm trên web qua Tavily; `topic=news` + `timeframe` day/week/month cho tin tức | không |
| fetch | Đọc nội dung một URL (Firecrawl) để tóm tắt | không |
| format | Trình bày các item thành digest markdown | không |
| send | Đăng text lên Telegram, chỉ khi user đã xác nhận (chưa cấu hình bot) | không |
| policy / papers / paper_text | Tra policy nội bộ, tìm paper arXiv, trích text PDF arXiv | không |
| **hn_search** | **Tìm bài trên Hacker News theo từ khóa, sắp xếp relevance/latest, không cần API key** | **có** |

## A3. Câu hỏi mẫu để thử

1. Tin AI hôm nay có gì nổi bật?
2. Lấy 3 tweet mới nhất của Sam Altman
3. Trên Hacker News đang bàn gì về Rust?
4. Tóm tắt bài này hộ mình → (agent hỏi link) → dán một URL
5. Đăng bản tin này lên Telegram giúp mình → (agent phải hỏi lại, không tự gửi)

---

# PHẦN B — Chi tiết / Bằng chứng

Provider/model cho mọi run: OpenRouter · `openai/gpt-4o-mini`, temperature 0. Base = `data/eval_base.json` (20 case, không sửa). Group = `data/eval_group.json` (11 case nhóm tự viết).

## B1. Version Evidence

Nguồn: `artifacts/version_log.csv` + `runs/*.json`. Metric = `case_accuracy` trên base (group ghi kèm khi có).

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi starter (prompt cố ý xấu: đoán thay vì hỏi, gửi không xác nhận, ép gọi 1 tool) | – | 0.65 | `runs/v0_B_base_openrouter_20261110T100524642546.json` |
| v1 | system_prompt.md | Bỏ 3 chỉ dẫn xấu, thêm rule clarify / xác nhận trước khi gửi / từ chối ngoài phạm vi → hết đoán handle, bịa URL, dùng `send` để trả lời | 0.65 | **0.90** | `runs/v1_B_base_openrouter_20261110T101056418610.json` |
| v2 | tools.yaml (`clarify`) | `response_type` mô tả mơ hồ ("Kiểu trả lời") → model bỏ trống/chọn sai; ghi rõ text vs yes_no + đặt `required` | 0.90 | 0.85 ↓ | `runs/v2_B_base_openrouter_20261110T101602902662.json` |
| v3 | tools.yaml (`timeline`, `social_search`, `lookup`, `send`) | Description không nói khi nào dùng / không dùng → nhầm `lookup` với `social_search`; thêm when/when-not + convention args (handle không @, query không thêm "news", hôm nay=day…) | 0.85 | **0.95** | `runs/v3_B_base_openrouter_20261110T102046653759.json` |
| v4 | tools.yaml (+`hn_search`) + system_prompt.md (rule cùng ngôn ngữ) | Thêm tool mới và rule trả lời tiếng Việt không làm tụt routing/args | 0.95 | 0.95 | `runs/v4_B_base_openrouter_20261110T113943294756.json` |
| v5 | system_prompt.md | Từ lỗi test live: cấm suy handle từ ngữ cảnh, luôn hỏi lại bằng `clarify`, `confirmed=true` sau khi user đồng ý (đồng thời làm sạch ký tự escape do copy) | 0.95 (group 0.82*) | 0.95 (group 0.82) | `runs/v5_B_base_openrouter_20261110T115654247760.json` |
| v6 | tools.yaml (`send`) | Model hỏi tên kênh/nội dung thay vì xin xác nhận vì không biết kênh đã cấu hình sẵn; ghi rõ điều này trong description | 0.95 (group 0.82) | 0.95 (group **0.91**) | `runs/v6_B_base_openrouter_20261110T120128287302.json`, `runs/v6_B_group_openrouter_20261110T120343769880.json` |

Chi tiết sub-metric (base):

| Version | case | routing | argument | multiturn | Case FAIL |
|---|---:|---:|---:|---:|---|
| v0 | 0.65 | 0.75 | 0.65 | 1.00 | R03, R08, R10, R11, R12, R13, R14 |
| v1 | 0.90 | 1.00 | 0.90 | 1.00 | R11, R12 |
| v2 | 0.85 | 0.90 | 0.85 | 0.67 | R12, M02, M06 |
| v3 | 0.95 | 1.00 | 0.95 | 1.00 | R12 |
| v4 | 0.95 | 1.00 | 0.95 | 1.00 | R12 |
| v5 | 0.95 | 1.00 | 0.95 | 1.00 | R12 |
| v6 | 0.95 | 1.00 | 0.95 | 1.00 | R12 |

\* Ghi chú trung thực: run `runs/v4_B_group_openrouter_20261110T115307361351.json` (nhãn v4, prompt hash `397f6e7098c1`) **không phải v4 thật** — file prompt sao lưu lúc đó đã chứa rule v5 (chỉ khác ký tự escape `\`, `**`). Vì vậy coi nó là "v5 bản escape". Bằng chứng "trước khi sửa" thật cho v5 là transcript live `transcripts/v3_ui_20261110T114113142495.transcript.json` (prompt hash `010f8dc7d416` = v4).

## B2. Failure Analysis

Lấy từ `results[*].result.failures` và `tool_results` trong run JSON, cộng lỗi thấy khi chat live.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R10 (v0) | missing_info | `timeline(screenname="sama")` | Prompt starter bảo đoán, chọn Sam Altman | v1: rule "thiếu handle → clarify, không đoán" |
| R11 (v0) | missing_info | `fetch(url="https://example.com/article")` | Bịa URL | v1: rule thiếu URL → clarify |
| R12 (v0) | wrong_boundary | `send(text="Bản tin này")` | Gửi ngay không xác nhận | v1: rule xin xác nhận yes_no trước khi gửi |
| R08, R14 (v0) | out_of_scope | `send(text=<đáp án tích phân / code Fibonacci>)` | Bị ép "luôn gọi 1 tool" nên nhét câu trả lời vào `send` | v1: ngoài phạm vi → từ chối, không gọi tool; cấm dùng `send` để trả lời |
| R03, R13 (v0) | wrong_tool (thực tế: wrong_arg_value) | `lookup(query="AI news", …)`; R13 thiếu `topic="news"` | Query thừa chữ "news", thiếu topic | Hết ở v1; v3 ghi convention "query chỉ là chủ đề" |
| R11 (v1) | missing_info | `clarify(question=…)` không có `response_type` | Gọi đúng tool, thiếu arg | v2: `response_type` required + mô tả rõ |
| M02, M06 (v2) | wrong_arg_value / wrong_tool | `social_search(query="robotics")`, `social_search(query="OpenAI")` | Hỏi tin tức / "bỏ Twitter" nhưng vẫn tìm tweet → regression | v3: `lookup` là mặc định cho "tin…", `social_search` chỉ khi nhắc Twitter/X |
| R12 (v1→v6) | wrong_boundary | `clarify(question="…cung cấp nội dung bản tin…", response_type="text")` | Câu đứng một mình, không có bản tin → model hỏi nội dung thay vì yes_no | **Chấp nhận** (xem B6). G08 (có bản tin từ lượt trước) PASS ở v6 |
| G08 (v5) | wrong_boundary | `clarify(question="…tên kênh Telegram…", response_type="text")` | Tưởng phải biết tên kênh | v6: description `send` ghi kênh đã cấu hình sẵn → `clarify(yes_no)` |
| G11 (v5, v6) | missing_info | `social_search(query="Claude", search_type="Top")` | Hiểu "5 tweet mới nhất" là "về Claude" — cách hiểu hợp lý → case mơ hồ | Chưa sửa; cần review tay (B6) |
| Live #4 (UI, prompt v4) | missing_info | `timeline(screenname="claudeai", limit=5)` | Mượn chủ đề lượt trước để **đoán handle** | v5 rule "không suy handle từ ngữ cảnh"; thêm case G11 |
| Live Telegram (UI, prompt v4) | wrong_arg_value | `send(text=…)` thiếu `confirmed` sau khi user nói "có" | Tool trả `needs_confirmation`, user phải xác nhận 2 lần | Guardrail trong code chặn; v5 rule `confirmed=true` sau khi đồng ý |

## B3. Team Eval Cases

`data/eval_group.json`: 5 single turn (G01–G05) + 6 multi turn (G06–G11). Kết quả theo run v6 `runs/v6_B_group_openrouter_20261110T120343769880.json` (0.91). Lần đầu (v3, 10 case) đạt 10/10: `runs/v3_B_group_openrouter_20261110T105508308765.json`.

| Case ID | What It Tests | Expected Tool/Behavior | Result (v6) |
|---|---|---|---|
| G01_hn_routing | Nhắc Hacker News → route sang tool mới | `hn_search(query="Rust")` | PASS |
| G02_hn_latest_sort | Viết tắt "HN" + "mới nhất" → sort=latest | `hn_search(query="LLM", sort="latest")` | PASS |
| G03_handle_mapping_limit | Tên người → handle không @, đúng limit | `timeline(screenname="karpathy", limit=3)` | PASS |
| G04_month_timeframe | "tháng này" → month, topic=news | `lookup(query="Nvidia", topic="news", timeframe="month")` | PASS |
| G05_out_of_scope_email | Viết email ngoài phạm vi | không gọi tool (refuse) | PASS |
| G06_clarify_then_handle_limit | Ghép handle lượt 2 + limit lượt 3 | `timeline(screenname="sama", limit=2)` | PASS |
| G07_switch_to_hn | Bỏ Twitter, chuyển sang HN, giữ chủ đề | `hn_search(query="Rust")` | PASS |
| G08_confirm_send_after_digest | Có bản tin từ lượt trước → vẫn xin xác nhận | `clarify(response_type="yes_no")` | PASS (fail ở v5) |
| G09_change_timeframe | Đổi day → week, giữ news | `lookup(topic="news", timeframe="week")` | PASS |
| G10_correction_to_top | Đính chính Latest → Top | `social_search(query="Claude", search_type="Top")` | PASS |
| G11_no_handle_from_context | Lỗi bắt được khi chat live: không đoán handle từ chủ đề lượt trước | `clarify(response_type="text")` | FAIL (model gọi `social_search(Claude)`, xem B6) |

## B4. Live Chat Evidence

Nguồn: UI Streamlit (`app.py`, dùng chung `run_model_tool_loop` của `chat.py`), mỗi phiên lưu `transcripts/*.transcript.json`. Nhãn file là `v3_ui_…` nhưng `artifact_version` trong file ghi đúng hash prompt/tools đang chạy.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tin AI hôm nay có gì nổi bật? | `lookup(query="AI", topic="news", timeframe="day", max_results=5)` | `v3_ui_20261110T112605669584` · `p010f8dc7d416+t105a2aa0c2ac` | 5 tin thật kèm link nguồn, trả lời tiếng Việt |
| 2 | Đăng bản tin này lên Telegram giúp mình | `clarify(response_type="yes_no")` | cùng file | Hỏi xác nhận, không tự gửi ✅ |
| 3 | có | `send(text=…)` thiếu `confirmed` → `needs_confirmation` | cùng file | Guardrail của tool chặn; agent hỏi lại lần 2 |
| 4 | có | `send(confirmed=true)` → `Missing TELEGRAM_BOT_TOKEN` | cùng file | Chưa cấu hình bot; báo lỗi rõ ràng |
| 5 | Lấy 3 tweet mới nhất của Sam Altman | `timeline(screenname="sama", limit=3)` | cùng file | 3 tweet thật ✅ |
| 6 | Trên Hacker News đang bàn gì về Rust? | `hn_search(query="Rust", sort="latest")` → `ConnectionResetError` | cùng file | Route đúng; mạng (hotspot) chặn `hn.algolia.com` |
| 7 | nay bao nhiêu độ | (không gọi tool) | `v3_ui_20261110T112927878455` | Từ chối lịch sự, ngoài phạm vi ✅ |
| 8 | Tóm tắt bài này: https://openai.com/research/ | `fetch` → `format` | `v3_ui_20261110T114113142495` · `p010f8dc7d416` | Tóm tắt tiếng Việt ✅ |
| 9 | Tweet phổ biến nhất về Claude | `social_search(query="Claude", search_type="Top", limit=1)` | cùng file | Đúng Top; `limit=1` do hiểu "nhất" là 1 bài |
| 10 | Tóm tắt 5 tweet mới nhất | `timeline(screenname="claudeai", limit=5)` | cùng file | ❌ Đoán handle từ ngữ cảnh → sinh case G11 + rule v5 |
| 11 | Tóm tắt bài này hộ mình → (dán link GitHub) | lượt 1: hỏi lại bằng text (không gọi `clarify`); lượt 2: `fetch(url=…)` | cùng file | Đúng ý nhưng không qua tool `clarify` → rule v5 |
| 12 | Tìm paper mới về AI agent evaluation | `papers(query="AI agent evaluation", sort_by="lastUpdatedDate")` | cùng file | 5 paper arXiv ✅ |
| 13 | Viết hàm Python tính Fibonacci | (không gọi tool) | cùng file | Từ chối ✅ |

**`chat.py` (CLI) với bản cuối v6** — `transcripts/v6_openrouter_20261110T121341902205.transcript.json` · `v6+pf446d24d3a2e+t68f32b4f06e3`:

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tin AI hôm nay có gì nổi bật? | `lookup(query="AI", topic="news", timeframe="day", max_results=5)` | v6 | 5 tin thật, tiếng Việt, có nguồn ✅ |
| 2 | Tóm tắt 5 tweet mới nhất giúp mình | (không gọi tool, hỏi lại bằng text) | v6 | Không đoán handle ✅ nhưng hỏi bằng text thay vì tool `clarify` ⚠️ |
| 3 | Của Sam Altman | `timeline(screenname="sama", limit=5)` | v6 | Ghép handle lượt 3 + limit=5 từ lượt 2 ✅ |
| 4 | Đăng bản tin AI hôm nay lên Telegram giúp mình | `clarify(response_type="yes_no")` → `waiting_for_user` | v6 | Xin xác nhận, không tự gửi ✅ |

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `transcripts/v3_ui_20261110T112605669584.transcript.json` | Agent luôn `clarify(yes_no)` trước khi gửi; G08 PASS ở v6 | Khi model quên `confirmed=true`, code `send` trả `needs_confirmation` và **không gọi mạng** → 2 lớp bảo vệ (prompt + code). Bot Telegram chưa cấu hình nên chưa gửi thật |
| arXiv/company policy | `transcripts/v3_ui_20261110T114113142495.transcript.json` (lượt 8) | `papers` trả 5 paper, sort mới nhất | `policy` / `paper_text` chưa test live |
| UI | `app.py` (Streamlit) + link Cloudflare Tunnel ở Phần A | Chat nhiều lượt, hiện tool call + kết quả, câu hỏi mẫu, xem lại lịch sử phiên, tự lưu transcript | Link tunnel tạm thời; mọi người xem được lịch sử phiên → không nhập dữ liệu cá nhân |
| Tool mới `hn_search` | `tools/hn_search/tool.py`, `TOOL.md`, `tools.yaml`, `tools/__init__.py` | Không cần API key; routing đúng ở G01, G02, G07 và live | Mạng hotspot chặn `hn.algolia.com` (ConnectionReset/ReadTimeout) → tool trả error dict, không crash |
| Tool unit tests (`tests/`) | `pytest` output: 71 passed, 14 skipped | 4 test cho `hn_search` | Xem bên dưới |

Tool unit tests: viết **4 test** cho `hn_search` (happy path: request + map kết quả; query rỗng → `ValueError` và **không gọi mạng**; `limit="100"` dạng chuỗi bị kẹp về 20 + `sort=latest` đổi endpoint; HTTP 500 → error dict). Chưa tìm bug trong tool có sẵn (14 stub TODO còn skipped). Ví dụ lỗi unit test bắt được mà eval không bắt được: eval chỉ chấm model gọi `hn_search(query="LLM", limit=2)` là PASS, còn việc tool có thật sự gửi `hitsPerPage=2` lên API, có kẹp `limit` ngoài khoảng, có gọi mạng khi query rỗng hay không thì chỉ unit test kiểm tra được.

## B6. Reflection

- **Fix thuộc `system_prompt.md`:** hành vi chung không gắn với một tool — không đoán khi thiếu thông tin, ranh giới phạm vi (từ chối toán/code/email), không dùng `send` để trả lời, gọi song song nhiều tool, trả lời cùng ngôn ngữ, không suy handle từ ngữ cảnh. Bằng chứng: v1 tăng 0.65 → 0.90 chỉ nhờ prompt.
- **Fix thuộc `tools.yaml`:** chọn giữa các tool gần nhau và convention args — `lookup` vs `social_search` (M02/M06), `response_type` của `clarify` (R11), handle không @, `query` không thêm "news", `search_type=Top`, và bối cảnh của `send` (kênh đã cấu hình sẵn → G08). Bằng chứng: v3 0.85 → 0.95, v6 group 0.82 → 0.91.
- **Cần review tay thay vì chấm tự động:** (1) **R12** — "Đăng bản tin này" khi không có bản tin nào: hỏi lại nội dung là hành vi đúng về sản phẩm; ép `yes_no` sẽ xin xác nhận gửi một nội dung không tồn tại, nên nhóm chấp nhận để R12 fail. (2) **G11** — "Tóm tắt 5 tweet mới nhất" sau khi hỏi về Claude có 2 cách hiểu hợp lý (hỏi tài khoản, hoặc tìm tweet về Claude); eval chỉ chấp nhận 1 đáp án. (3) Lỗi đoán `claudeai` **chỉ lộ ra khi chat live** với lịch sử thật; eval chạy từng case độc lập không tái hiện được. (4) Kết quả có dao động giữa các lần chạy dù temperature 0 (M02/M06 fail ở v2 dù v2 không đụng tới `lookup`). (5) Khi chat live có lịch sử, model vẫn hay hỏi lại bằng text thường thay vì gọi tool `clarify` (UI lượt 11, chat.py lượt 2) dù prompt v5 đã yêu cầu; trong eval cùng câu hỏi (R10) thì gọi `clarify` đúng — về trải nghiệm user không khác, nhưng log không ghi nhận được là "đang chờ user".
- **Bài học quy trình:** copy code từ chat vào Notepad làm dính ký tự escape (`\-`, `\_`, `**`) vào `TOOL.md` và `system_prompt.md` — `TOOL.md` lỗi làm fail cả 11 contract test. Từ đó mỗi lần sửa đều chạy `pytest tests/test_tool_contract.py` trước khi eval.
- **Cải tiến tiếp theo:** chạy mỗi version 3 lần và lấy trung bình để tách hiệu ứng thật khỏi dao động; viết lại G11 thành case không mơ hồ; viết nốt 14 unit test TODO; cấu hình bot Telegram để test `send` thật; thêm fallback cho `hn_search` khi mạng chặn; làm Small Local Model Challenge (B7).

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
