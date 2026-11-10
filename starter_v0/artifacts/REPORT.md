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
| v0 | baseline | Baseline trước khi tối ưu | — | case_accuracy=0.35; tool_routing_accuracy=0.5; argument_accuracy=0.35; multiturn_accuracy=0.5 | `runs/v0_B_base_ollama_20261110T095915950610.json` |
| v1 | `artifacts/system_prompt.md` | Quy tắc định tuyến rõ ràng sẽ giảm chọn nhầm tool/args so với v0 | case_accuracy=0.35; tool_routing_accuracy=0.5; argument_accuracy=0.35; multiturn_accuracy=0.5 | case_accuracy=0.6; tool_routing_accuracy=0.65; argument_accuracy=0.6; multiturn_accuracy=0.8333 | `runs/v1_B_base_ollama_20261110T105305856367.json` |
| v2 | `artifacts/tools.yaml` (mô tả tool) | Hướng dẫn rõ nguồn và quy ước tham số sẽ cải thiện routing trên base so với v1 | case_accuracy=0.6; tool_routing_accuracy=0.65; argument_accuracy=0.6; multiturn_accuracy=0.8333 | case_accuracy=0.6; tool_routing_accuracy=0.8; argument_accuracy=0.6; multiturn_accuracy=0.6667 | `runs/v2_B_base_ollama_20261110T112419425370.json` |
| v3 |  |  |  |  |  |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R05_limit_arg | wrong_arg_value | `timeline(screenname=elonmusk)` | Thiếu `limit=10` | Nhấn mạnh trích số lượng trong mọi yêu cầu |
| R06_timeframe_arg | wrong_arg_value | `lookup(query="tin công nghệ", timeframe="week")` | Thiếu `topic=news` | Phân biệt news/general rõ hơn |
| R10_missing_handle | missing_info | `timeline(screenname=TwitterHandle)` | Tự bịa handle thay vì hỏi | Bắt buộc clarify khi chưa biết tài khoản |
| R11_missing_url | missing_info | Không gọi tool | Không hỏi URL còn thiếu | Nêu rõ phải gọi clarify, không được im lặng |
| R12_confirm_before_send | wrong_boundary | `clarify()` | Gọi clarify nhưng thiếu `response_type=yes_no` | Yêu cầu đúng enum và xác nhận trước send |
| R14_out_of_scope_coding | out_of_scope | `format(items=[...], template="bullets")` | Gọi tool và dựng nội dung cho yêu cầu coding ngoài phạm vi | Chặn tool cho yêu cầu không phải research |
| M03_correction_handle | wrong_arg_value | `timeline(screenname=karpathy)` | Bỏ sót `limit=3` từ ngữ cảnh | Mang theo số lượng đã yêu cầu qua các lượt |
| M06_switch_tool | wrong_tool | `social_search(query="OpenAI", search_type="Latest")` | Không chuyển từ social sang web news | Ưu tiên thay đổi ý định mới nhất trong hội thoại |

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
