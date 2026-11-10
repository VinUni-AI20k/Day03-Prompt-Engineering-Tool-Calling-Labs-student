# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team:
- Members:
- Provider/model:

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL: 

## A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

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
|  |  |  |  |

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
| UI |  |  |  |
| Tool unit tests (`tests/`) | `pytest` output |  |  |

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
