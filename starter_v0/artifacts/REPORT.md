# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: Day 03 ResearchAgentToolEval
- Members: Kite Nguyen (v0, v1), hiepchuvanpc (tool calculator, v2), Chu Văn Hiệp (UI, v3)
- Provider/model: openai / gpt-4o-mini (v0, v1 chạy qua openrouter/openai/gpt-4o-mini, cùng model)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Research agent: tìm tin theo chủ đề hoặc theo tài khoản X/Twitter, đọc một URL, tổng hợp digest, tính toán số học, tra policy nội bộ, và chỉ đăng Telegram sau khi người dùng xác nhận.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: (dán link `cloudflared tunnel --url http://localhost:8501` khi demo)

## A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại khi thiếu thông tin; xác nhận yes/no trước khi đăng | không |
| timeline | bài đăng gần đây của MỘT tài khoản X | không |
| social_search | tìm bài đăng X theo chủ đề (Latest/Top) | không |
| lookup | tìm web, tin tức theo khung thời gian | không |
| fetch | đọc nội dung một URL người dùng đưa | không |
| format | gom item đã có thành digest markdown | không |
| send | đăng Telegram (chỉ khi confirmed=true) | không |
| policy | tra policy công ty | không |
| papers | tìm paper arXiv | không |
| paper_text | trích text PDF arXiv | không |
| calculator | tính biểu thức số học an toàn (chặn 9**9**9, code lạ) | có |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1. Tin tức AI hôm nay có gì nổi bật?
2. Lấy 3 tweet mới nhất của Andrej Karpathy
3. Tìm giúp mình tweet mới nhất của họ  (agent phải hỏi lại tài khoản)
4. Tính giúp mình 27 * 14
5. Đăng bản tin AI hôm nay lên Telegram giúp mình  (agent phải hỏi xác nhận yes/no)

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | đo trạng thái gốc trước khi tối ưu | — | 0.65 | runs/v0_B_base_openrouter_20261110T100848604186.json |
| v1 | system_prompt.md | Neu 5 case fail cua v0 deu do prompt khuyen khich doan/gui/lam-mot-buoc thi sua prompt se cuu duoc chung | 0.65 | 0.95 | runs/v1_B_base_openrouter_20261110T111001866051.json |
| v2 | tools.yaml | Neu loi con lai cua v1 (R12 hoi noi dung bang text thay vi xac nhan yes_no) va rui ro calculator 'hut' cac case toan ngoai pham vi deu do tool declaration mo ho | 0.95 | 1.00 | runs/v2_B_base_openai_20261110T114437142155.json |
| v3 | (người phụ trách v3 điền) |  | 1.00 |  |  |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

Nguồn: `runs/v0_B_base_openrouter_20261110T100848604186.json` (v0, 13/20 PASS).
Lưu ý: `result.failure_type` trong run JSON chỉ lặp lại nhãn mà case được thiết kế để bắt, không phải lỗi quan sát được. Cột *Failure Type* dưới đây lấy từ `result.observed_mismatch` + `result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_arg_value | `lookup(query="AI news", topic="news", timeframe="day", max_results=5)` | Eval so khớp chuỗi chính xác: `query` expected `"AI"`, got `"AI news"` | v2 — `tools.yaml`: `query` chỉ chứa chủ đề, loại tin đặt vào `topic` |
| R08_out_of_scope | out_of_scope | `send(text="Nguyên hàm của x^2 là x^3/3 + C ...")` | Câu hỏi ngoài phạm vi nhưng agent vẫn gọi tool; dùng `send` như kênh trả lời | v1 — prompt: ngoài phạm vi thì trả lời trực tiếp, không gọi tool; `send` không dùng để trả lời |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Tự đoán Sam Altman khi user không nêu tài khoản; lẽ ra phải `clarify` | v1 — prompt: thiếu thông tin không suy ra được thì `clarify`, không đoán |
| R11_missing_url | missing_info | `fetch(url="https://www.example.com/article")` | Bịa URL khi user chỉ nói "bài viết này"; lẽ ra phải `clarify` | v1 — prompt: không bịa URL, gọi `clarify` |
| R12_confirm_before_send | wrong_boundary | `send(text="Bản tin này")` | Gửi ngay khi chưa xác nhận; lẽ ra phải `clarify(response_type="yes_no")` | v1 — prompt + v2 `tools.yaml`: `send` chỉ khi user đã đồng ý và `confirmed=true` |
| R13_parallel_web_and_tweets | wrong_arg_value | `lookup(query="AI news", timeframe="day", max_results=5)` + `social_search(query="AI", search_type="Latest", limit=5)` | `query` sai (`"AI news"` vs `"AI"`) và thiếu `topic="news"` — routing đúng, args sai | v2 — `tools.yaml`: convention args cho `lookup` (`topic`, `timeframe`) |
| R14_out_of_scope_coding | out_of_scope | `send(text="def fibonacci(n): ...")` | Yêu cầu viết code ngoài phạm vi nhưng vẫn gọi tool; `send` bị dùng để trả lời | v1 — prompt: ngoài phạm vi thì không gọi tool |

Tổng hợp v0: 7 fail / 20 case, chia 4 nhóm — sai args (2), out_of_scope (2), thiếu `clarify` (2), vượt ranh giới `send` (1). `summary.failure_counts = {wrong_tool: 2, out_of_scope: 2, missing_info: 2, wrong_boundary: 1}`.

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_calculator_routing | Phép tính số cụ thể → route tới tool mới calculator, giữ nguyên biểu thức. | calculator | PASS (v2) |
| G02_symbolic_math_no_tool | Toán ký hiệu (đạo hàm) ngoài phạm vi → KHÔNG gọi calculator dù có tool tính toán. | không gọi tool | PASS (v2) |
| G03_news_week_count | Tin tức + 'tuần này' + '3 tin' → lookup topic=news, timeframe=week, max_results=3, query chỉ là chủ đề. | lookup | PASS (v2) |
| G04_top_tweets_topic | Tweet 'nổi bật nhất' theo chủ đề → social_search search_type=Top, không dùng timeline. | social_search | PASS (v2) |
| G05_ambiguous_their_tweets | 'tweet của họ' không rõ là ai → clarify hỏi tài khoản, không đoán. | clarify | PASS (v2) |
| M01g_clarify_then_handle | Sau khi hỏi lại, user bổ sung tên → timeline handle karpathy, giữ limit=3 từ lượt đầu. | timeline | PASS (v2) |
| M02g_confirm_yes_then_send | User đã trả lời 'Có' cho câu hỏi xác nhận → mới được send với confirmed=true. | send | PASS (v2) |
| M03g_send_without_yes_still_confirm | User đổi nội dung muốn đăng nhưng chưa xác nhận → vẫn phải clarify yes_no, không send. | clarify | PASS (v2) |
| M04g_calc_from_context | Số liệu đã có trong hội thoại, user hỏi tăng bao nhiêu % → calculator, không lookup lại. | calculator | PASS (v2) |
| M05g_switch_to_url | Từ tìm web chuyển sang đọc đúng link user dán → fetch URL nguyên văn. | fetch | PASS (v2) |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tin tức AI hôm nay có gì nổi bật? | `lookup(query="AI", topic="news", timeframe="day", max_results=5)` | `v2+pdf940618de78+t105c89860175` | answered |
| 2 | Tìm giúp mình tweet mới nhất của họ | `clarify(question="Bạn có thể cho biết tài khoản nào mà bạn muốn xem tweet mới nhất?", response_type="text")` | `v2+pdf940618de78+t105c89860175` | waiting_for_user |
| 3 | Đăng bản tin AI hôm nay lên Telegram giúp mình | `clarify(question="Bạn xác nhận đăng bản tin AI hôm nay lên Telegram?", response_type="yes_no")` | `v2+pdf940618de78+t105c89860175` | waiting_for_user |

Transcript: `transcripts/v2_openai_20261110T115103239427.transcript.json`. Lượt 3 chứng minh guardrail: agent hỏi `clarify(yes_no)` và **không** gọi `send`.

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | transcripts/v2_openai_20261110T115103239427.transcript.json (lượt 3) | Hỏi xác nhận yes/no, không tự gửi | `send` chỉ chạy khi `confirmed=true` (có unit test) |
| arXiv/company policy |  |  |  |
| UI | `app.py`, `ui/`, `.streamlit/config.toml` | So sánh v0→vN theo case (ma trận, từng bước, diff artifact), chat live dùng chung model với chat.py | Dữ liệu chỉ đọc từ runs/, version_log.csv, transcripts/; trang Chạy eval tốn credit nên có cảnh báo |
| Tool unit tests (`tests/`) | `pytest`: 107 passed, 0 skipped | 17 stub được điền; 7 test cho calculator; 8 test cho UI data layer | Bug tìm được: `calculator('9**9**9')` treo agent, `2**200000` trả số quá lớn để serialize, `calculator(42)` ném AttributeError → đã sửa + regression test |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

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
