# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: `ollama` (`qwen2.5:3b`)

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi starter chưa tối ưu trước khi sửa (`ollama` / `qwen2.5:3b`) | — | 0.40 (8/20) | `starter_v0/runs/v0_B_base_ollama_20261110T184359142341.json` |
| v1 | `system_prompt.md` | Gỡ chỉ dẫn bẫy của starter + thêm rule routing, map handle và ranh giới out-of-scope/clarify | 0.40 (8/20) | 0.45 (9/20) | `starter_v0/runs/v1_B_base_ollama_20261110T185037706863.json` |
| v2 | `tools.yaml` | Viết lại description ngắn gọn (DÙNG KHI / KHÔNG DÙNG KHI) và quy ước tham số trong `tools.yaml` | 0.45 (9/20) | 0.70 (14/20) | `starter_v0/runs/v2_B_base_ollama_20261110T191308230206.json` |
| v3 | `system_prompt.md` | Siết rule `http(s)://` → `fetch`, cấm gọi `clarify` với coding/toán, thêm ví dụ gọi `clarify` và truyền `limit` | 0.70 (14/20) | 0.80 (16/20) | `starter_v0/runs/v3_B_base_ollama_20261110T192354388698.json` |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON (`v0_B_base_ollama_20261110T184359142341.json`).

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `R01_user_tweets_routing` | `wrong_tool` | `timeline(screenname="samaltman")` | `screenname: expected 'sama', got 'samaltman'` | Thêm bảng map tên người nổi tiếng sang handle Twitter (`Sam Altman` → `sama`, `Andrej Karpathy` → `karpathy`, `Elon Musk` → `elonmusk`) |
| `R03_web_news_routing` | `wrong_tool` | `papers(query="AI", sort_by="lastUpdatedDate", max_results=5)` | `missing tool call lookup; extra tool call papers` | Phân biệt rõ rule routing: tin tức web → `lookup(topic="news")`, chỉ dùng `papers` cho bài báo khoa học arXiv |
| `R06_timeframe_arg` | `wrong_arg_value` | `lookup(topic="tech", query="tin công nghệ trong tuần này", timeframe="week")` | `topic: expected 'news', got 'tech'` (API 400 Bad Request) | Ghi rõ enum `topic` chỉ nhận `general` hoặc `news`; `query` chỉ chứa từ khóa ngắn |
| `R08_out_of_scope` | `out_of_scope` | `clarify(question="giải giúp mình bài toán tích phân: nguyên hàm của x^2 là gì?")` | `expected no tool call` | Bổ sung rule từ chối thẳng không gọi tool với câu hỏi ngoài phạm vi research (toán, lập trình...) |
| `R10_missing_handle` | `missing_info` | `timeline(screenname="twitter")` | `missing tool call clarify; extra tool call timeline` | Gỡ chỉ dẫn ép đoán bừa trong `system_prompt.md`; bắt buộc gọi `clarify(response_type="text")` khi thiếu handle |
| `R11_missing_url` | `missing_info` | `lookup(query="bài viết", timeframe="day", topic="general")` | `missing tool call clarify; extra tool call lookup` | Gỡ chỉ dẫn ép đoán URL trong `system_prompt.md`; bắt buộc gọi `clarify(response_type="text")` khi nói "bài này" mà thiếu link |
| `R12_confirm_before_send` | `wrong_boundary` | `send(text="Đây là bản tin mới nhất từ nguồn tin cậy.", confirmed=true)` | `missing tool call clarify; extra tool call send` | Gỡ chỉ dẫn tự gửi trong `system_prompt.md`; yêu cầu gọi `clarify(response_type="yes_no")` xác nhận trước khi `send` |
| `R13_parallel_web_and_tweets` | `wrong_tool` | `social_search(Latest, 3)` + `social_search(Top, 3)` | `missing tool call lookup; extra tool call social_search` | Gỡ chỉ dẫn ép chọn 1 tool trong `system_prompt.md`; hướng dẫn gọi song song `lookup` + `social_search` khi cần cả web và Twitter |
| `R14_out_of_scope_coding` | `out_of_scope` | `clarify(question="Viết giúp mình một hàm Python tính Fibonacci bằng recursion.")` | `expected no tool call` | Bổ sung rule từ chối thẳng không gọi tool với yêu cầu viết code ngoài phạm vi research |
| `M02_carryover_timeframe` | `wrong_arg_value` | `lookup(query="robotics today", timeframe="day")` | `query: expected 'robotics', got 'robotics today'; topic: expected 'news', got None` | Quy ước `lookup.query` chỉ giữ từ khóa chủ đề (`"robotics"`), giữ `topic="news"` khi user nói "vẫn là tin hôm nay" |
| `M03_correction_handle` | `wrong_arg_value` | `social_search(query="Andrej Karpathy", search_type="Latest", limit=3)` | `missing tool call timeline; extra tool call social_search` | Nhấn mạnh tweet *của một người cụ thể* → luôn dùng `timeline` + map handle (`Andrej Karpathy` → `karpathy`), không dùng `social_search` |
| `M06_switch_tool` | `wrong_tool` | `social_search(query="OpenAI", search_type="Latest", limit=5)` | `missing tool call lookup; extra tool call social_search` | Nhấn mạnh tuân theo chỉ dẫn đổi nguồn ở lượt mới nhất ("Bỏ Twitter, chuyển sang tìm trên web tin tức" → chuyển sang `lookup`) |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/hackernews/`) | `starter_v0/tools/hackernews/tool.py`, `TOOL.md`, `tools/__init__.py`, `artifacts/tools.yaml` | Tìm kiếm thảo luận công nghệ trên Hacker News qua Algolia API (không cần API key), hỗ trợ `sort_by=relevance|date` và `limit` | Clamp `limit` (1–20), fallback `sort_by` ngoài enum, bắt `ValueError`/`HTTPError` trả về error dict thay vì raise |
| Unit test tool mới (3 test) | `starter_v0/tests/test_tools_todo.py` (`pytest -v`: 70 passed, 14 skipped, 0 failed) | Pass cả 3 test: happy path (`search_by_date` + fallback `hn_url`), input xấu (query rỗng, enum sai, `limit` dạng chuỗi), và HTTP 503 trả error dict | Eval chỉ kiểm tra model có gọi đúng `hackernews(query=...)` hay không, không bắt được bug bên trong code tool (ví dụ quên truyền `hitsPerPage` hoặc crash khi `hit["url"]` là `None`); unit test bắt được ngay offline |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

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
