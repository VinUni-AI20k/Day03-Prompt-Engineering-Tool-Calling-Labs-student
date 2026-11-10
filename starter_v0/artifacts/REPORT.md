# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: DoMinhHoang
- Members: Phạm Đức Hồng Đức, Đỗ Minh Hoàng, Vũ Đức Tâm, Lê Xuân Hà
- Provider/model: openai

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent hỗ trợ tìm tin trên web và X/Twitter, đọc URL, tra cứu paper arXiv, policy nội bộ, thời tiết hiện tại và repository GitHub; agent có thể kết hợp nhiều nguồn và giữ đúng ràng buộc qua hội thoại nhiều lượt. Khi thiếu dữ liệu bắt buộc agent sẽ hỏi lại thay vì tự đoán, còn hành động gửi/đăng ra Telegram chỉ được thực hiện sau khi người dùng xác nhận rõ ràng.

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

Nguồn bằng chứng: `artifacts/version_log.csv` và các run JSON tương ứng trong `runs/`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Starter cố ý sẽ lỗi ở phạm vi, thông tin bị thiếu, xác nhận gửi và định tuyến nhiều tool. | — | 0.70 | `runs/v0_B_base_openai_20261110T110804866669.json` |
| v1 | `system_prompt.md` | Bỏ chỉ dẫn xấu và thêm ranh giới routing/clarify/send sẽ sửa lỗi tự đoán, gọi tool ngoài phạm vi và sai multi-tool. | 0.70 | 0.90 | `runs/v1_B_base_openai_20261110T135423515714.json` |
| v2 | `tools.yaml` | Description và schema tường minh sẽ sửa lỗi thiếu `response_type` và tăng độ chính xác argument. | 0.90 | 0.90 | `runs/v2_B_base_openai_20261110T144126484826.json` |
| v3 | `system_prompt.md` + `tools.yaml` | Ưu tiên lệnh hủy/chuyển nguồn và xác nhận `yes_no` sẽ loại tool thừa và sửa boundary Telegram còn lại. | 0.90 | 1.00 | `runs/v3_B_base_openai_20261110T144745860762.json` |

Lưu ý về attribution: phần Người 1 chủ động thay đổi ở v1 là `system_prompt.md`, nhưng tools hash cũng đổi từ `5b22a2476d41` ở v0 sang `55b439405a40` ở v1 do đồng bộ tool mới của nhóm. Vì vậy mức tăng 0.70 → 0.90 là bằng chứng của artifact v1 hoàn chỉnh, không được diễn giải là tác động thuần túy chỉ của prompt.

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| v0/R08_out_of_scope | `out_of_scope` | `send` | Câu toán ngoài phạm vi nhưng model dùng `send` như tool trả lời. | Thêm rule ngoài phạm vi: không gọi tool; cấm dùng `send` để trình bày câu trả lời. |
| v0/R10_missing_handle | `missing_info` | `timeline` | Thiếu tài khoản nhưng model tự đoán `sama`. | Thiếu handle phải gọi `clarify(response_type="text")`; không tự chọn tài khoản nổi tiếng. |
| v0/R11_missing_url | `missing_info` | `fetch` | Model tự tạo `https://example.com/article` khi chưa có URL. | Chỉ dùng `fetch` với URL có thật trong hội thoại; thiếu URL phải hỏi `clarify(text)`. |
| v0/R12_confirm_before_send | `wrong_boundary` | `send` | Gọi `send` trước khi người dùng xác nhận. | Bắt buộc hỏi `clarify(response_type="yes_no")` trước mọi hành động gửi/đăng. |
| v0/R13_parallel_web_and_tweets | `wrong_tool` | `lookup`, `social_search` | Đúng hai tool nhưng `lookup.query="AI news"` và thiếu `topic="news"`; mismatch thực tế là `wrong_arg_value`. | Giữ `query="AI"`, tách loại tin vào `topic="news"` và thời gian vào `timeframe="day"`. |
| v0/R14_out_of_scope_coding | `out_of_scope` | `send` | Yêu cầu coding ngoài phạm vi nhưng model tạo code rồi đưa vào `send`. | Không gọi tool cho coding thuần túy và không dùng `send` như output channel. |
| v1/R11_missing_url | `missing_info` | `clarify` | Chọn đúng tool nhưng bỏ `response_type`; expected `text`. | Bắt buộc `response_type` trong schema và mô tả rõ từng enum. |
| v1/R12_confirm_before_send | `wrong_boundary` | `clarify` | Chọn đúng tool nhưng dùng `response_type="text"` thay vì `"yes_no"`. | Nêu rõ xác nhận side effect phải dùng `yes_no`. |
| v2/R12_confirm_before_send | `wrong_boundary` | `clarify` | Model vẫn ưu tiên hỏi nội dung bằng `text` trước xác nhận. | V3 quy định xác nhận `yes_no` luôn là bước đầu tiên, kể cả khi nội dung còn thiếu. |
| v2/M06_switch_tool | `wrong_tool` | `lookup`, `social_search` | `lookup` đúng nhưng gọi thừa `social_search` sau khi người dùng nói bỏ Twitter; mismatch thực tế là `extra_tool_call`. | V3 cho lệnh hủy/chuyển nguồn ưu tiên cao hơn multi-tool và cấm gọi tool đã bị thay thế. |

## B3. Team Eval Cases

Đã thêm 10 case vào `data/eval_group.json`, gồm 5 single-turn và 5 multi-turn. Run `runs/v3_B_group_openai_20261110T151111781188.json` đạt 6/10 case, case accuracy 0.60, tool routing 0.90, argument accuracy 0.60 và multi-turn accuracy 0.80.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_weather_current_city | Route câu hỏi thời tiết hiện tại và giữ đơn vị độ C. | `weather(location="Hanoi", units="celsius")` | FAIL — gọi đúng `weather` nhưng bỏ `units`; schema mặc định là `celsius`, cần manual review expected args. |
| G02_github_top_repositories | Ánh xạ số lượng và thứ tự nhiều sao nhất khi tìm repository. | `github_search(query="RAG", sort="stars", order="desc", max_results=3)` | FAIL — thiếu `order="desc"`; đây là giá trị mặc định nên cần manual review. |
| G03_weather_missing_location | Không tự đoán vị trí khi câu hỏi thời tiết thiếu địa điểm. | `clarify(response_type="text")` | PASS |
| G04_send_after_explicit_confirmation | Chỉ gửi đúng nội dung sau xác nhận rõ ràng. | `send(text="Bản tin AI hôm nay", confirmed=true)` | FAIL — model gọi `clarify` thay vì `send`; cần xem lại việc coi xác nhận cùng một câu là trusted approval. |
| G05_out_of_scope_translation | Không gọi tool cho yêu cầu dịch thuật ngoài phạm vi research. | Không gọi tool; từ chối/định hướng | PASS |
| G06_multiturn_weather_correction | Carry yêu cầu thời tiết, thay địa điểm mới nhất và đổi sang độ F. | `weather(location="Đà Nẵng", units="fahrenheit")` | PASS |
| G07_multiturn_github_constraints | Carry chủ đề, thêm qualifier ngôn ngữ và áp dụng limit/sort ở lượt cuối. | `github_search(query="FastAPI language:Python", sort="stars", order="desc", max_results=4)` | FAIL — thiếu `order="desc"`; đây là giá trị mặc định nên cần manual review. |
| G08_multiturn_send_confirmation | Carry chính xác nội dung và chỉ gửi sau lượt xác nhận. | `send(text="AI agent ra mắt hôm nay.", confirmed=true)` | PASS |
| G09_multiturn_url_replacement | URL mới nhất ghi đè URL cũ và không gọi thừa `fetch`. | `fetch(url="https://www.anthropic.com/research")` | PASS |
| G10_multiturn_switch_papers_to_github | Bỏ nguồn paper cũ, chuyển sang GitHub nhưng giữ chủ đề và số lượng. | `github_search(query="RAG", max_results=2)` | PASS |

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

### Person 3: local research tools and Telegram guardrail

| Bonus | Evidence file | Behavior | Limit / guardrail |
|---|---|---|---|
| New tool: deduplicate | `tools/deduplicate/tool.py`, `tools/deduplicate/TOOL.md` | Removes duplicate normalized URLs before digest formatting | Local metadata only; preserves first item; max 100 items |
| New tool: citation_audit | `tools/citation_audit/tool.py`, `tools/citation_audit/TOOL.md` | Reports missing citation fields, invalid URLs and duplicate sources | Does not verify facts or website availability |
| Telegram confirmation | `tools/send/tool.py`, `chat.py` | Preview exact text; type SEND to authorize one send attempt | Model-provided confirmed=True alone cannot send; no automatic retries |
| Offline evidence | `tests/test_person3.py` | Mocked HTTP tests cover new tools, refusal, exact-text binding and Telegram failures | No real Telegram delivery or live model evaluation claimed |

Handoff: Person 1 should add routing for the two new tools in the system prompt.
Replace the starter prompt's instruction to publish without asking: Telegram must
always require explicit confirmation. Person 4 can extend the new offline tests
and add model routing cases. Person 5 should call approve_message(text) only in
a trusted UI confirmation handler, after previewing that exact text. Two new
tools here plus Person 2's two tools would total four, once integrated.

Offline validation: `.venv/Scripts/python.exe -m pytest tests/ -q` returned
**98 passed, 17 skipped**. The 17 skips are pre-existing exercise stubs in
`tests/test_tools_todo.py` for Person 4 to complete. The focused command
`python -m pytest tests/test_person3.py tests/test_tool_contract.py tests/test_tools_examples.py -q`
returned **98 passed**, with no skipped tests. No live model score is claimed.

## B6. Reflection

- **Fix nào thuộc `system_prompt.md`?** Các quy tắc mang tính điều phối toàn cục: giới hạn phạm vi research, khi nào phải hỏi lại thay vì đoán, chọn `timeline`/`social_search`/`lookup`/`fetch`, cho phép nhiều tool, carry và sửa constraint qua nhiều lượt, ưu tiên lệnh hủy/chuyển nguồn, và bắt buộc xác nhận trước hành động gửi.
- **Fix nào thuộc `tools.yaml`?** Các contract gắn với từng tool: mô tả khi dùng/không dùng, handle không có `@`, `topic=news`, quy ước `timeframe`, `search_type=Top|Latest`, bắt buộc truyền rõ `clarify.response_type`, và chỉ cho `send.confirmed=true` sau xác nhận.
- **Failure nào cần manual review?** Ở v2, `M06_switch_tool` được dataset gán `failure_type=wrong_tool`, nhưng JSON cho thấy lỗi quan sát thực tế là `extra_tool_call`: model gọi đúng `lookup` nhưng gọi thừa `social_search`. `R12_confirm_before_send` cũng gọi đúng `clarify`; lỗi thật nằm ở argument `response_type="text"` thay vì `"yes_no"`. Cần đọc `observed_mismatch`, `actual_tool_calls` và `failures` thay vì chỉ nhìn nhãn tổng quát.
- **Sẽ cải thiện gì tiếp theo?** Rà soát expected args của G01/G02/G07 vì eval đang bắt buộc các giá trị đã có default (`celsius`, `desc`), và thiết kế lại G04 để phân biệt câu chữ “tôi xác nhận” với trusted UI approval. Sau đó bổ sung case paraphrase nhằm tránh tối ưu quá sát base eval và so sánh cùng artifact trên model/provider khác để kiểm tra độ ổn định.

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
