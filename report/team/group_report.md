# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: 3npc
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: claude-sonnet-4-6

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
| v0 | baseline | Đo hành vi starter chưa tối ưu (prompt cố tình khuyến khích đoán / gửi ngay / một bước) | – | 0.70 | `runs/v0_B_base_anthropic_20261110T174610548208.json` |
| v1 | `system_prompt.md` | Prompt starter bảo model đoán thay vì hỏi và gửi không cần xác nhận → không gọi `clarify` khi thiếu thông tin, vẫn gọi tool với yêu cầu ngoài phạm vi. Bỏ chỉ dẫn xấu, thêm rule hỏi lại / xác nhận / từ chối ngoài phạm vi. R10, R14 → PASS | 0.70 | 0.80 | `runs/v1_B_base_anthropic_20261110T180308452177.json` |
| v2 | `tools.yaml` (param `lookup`) | Thiếu convention args → model nhét "news"/"today" vào `query` thay vì dùng `topic`/`timeframe`. `query` đúng ở R03, R13, M02 (R13 → PASS) nhưng lộ lỗi gọi thừa `social_search` (R06 → FAIL) nên metric không đổi | 0.80 | 0.80 | `runs/v2_B_base_anthropic_20261110T180537078121.json` |
| v3 | `tools.yaml` (description mọi tool) | Description mơ hồ → model không biết khi nào KHÔNG dùng tool, gọi thừa `social_search` cho câu hỏi tin tức. Viết lại theo mẫu làm gì / khi nào dùng / khi nào không dùng. R06, M02 → PASS; còn R03 (gọi thừa `social_search`) và R12 (hỏi `text` thay vì `yes_no`) | 0.80 | 0.90 | `runs/v3_B_base_anthropic_20261110T180821849792.json` |
| v4 | `system_prompt.md` | Rule "thiếu thông tin → hỏi `text`" đè lên rule xác nhận trước khi gửi, nên với "Đăng bản tin này" model hỏi nội dung thay vì xin xác nhận. Thêm thứ tự ưu tiên: yêu cầu gửi/đăng luôn `clarify(yes_no)` trước. R12 → PASS, không case nào bị chuyển thành FAIL; còn R03 | 0.90 | 0.95 | `runs/v4_B_base_anthropic_20261110T181351263474.json` |
| v5 | `tools.yaml` (description `social_search`) | Từ "nổi bật" trong câu hỏi tin tức bị hiểu thành bài `Top` trên Twitter nên model gọi thêm `social_search`. Ghi rõ "nổi bật / hot / đáng chú ý" trong câu hỏi tin tức không có nghĩa là muốn xem tweet. R03 → PASS, 20/20 case | 0.95 | 1.00 | `runs/v5_B_base_anthropic_20261110T181632709924.json` |
| v6 | `system_prompt.md` | Rule routing chỉ nằm rải rác trong description của tool. Gom thành một mục "Routing" trong prompt (khi nào dùng `timeline` / `social_search` / `lookup` / `fetch` / `clarify`…, lấy giá trị mới nhất trong hội thoại nhiều lượt) sẽ giữ việc chọn tool đúng mà không gây regression. Giữ 20/20 PASS | 1.00 | 1.00 | `runs/v6_B_base_anthropic_20261110T182511083025.json` |
| v7 | `tools.yaml` (thêm 4 tool mới: `hf_models`, `hn_search`, `github_repos`, `pypi_package`) | Thêm 4 tool mới làm tăng số lựa chọn nên có thể khiến model chọn nhầm tool ở các case cũ (vd tin tức → `hf_models`). Chạy lại base để kiểm tra regression: giữ 20/20 PASS. Suite group: 10/10 | 1.00 | 1.00 | `runs/v7_B_base_anthropic_20261110T190131852703.json` |

Model: `claude-sonnet-4-6` (provider `anthropic`) cho mọi version. Metric = `summary.case_accuracy` trên `data/eval_base.json` (20 case), mọi run có `provider_error_cases == 0`, `measured_cases == 20`.

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

Run v0: `runs/v0_B_base_anthropic_20261110T174610548208.json` (`claude-sonnet-4-6`, 14/20 PASS, `provider_error_cases = 0`). Cột Failure Type ghi loại lỗi mà case nhắm tới (`failure_type` trong eval), kèm mismatch quan sát được (`observed_mismatch`) trong ngoặc.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | `wrong_tool` (observed: `wrong_arg_value`) | `lookup(query="AI news today", topic="news", timeframe="day")` + `social_search(query="AI artificial intelligence news today", search_type="Top")` | `query` nhét thêm "news today" thay vì chỉ "AI"; gọi thừa `social_search` cho một câu hỏi tin tức thuần | v2: quy ước `query` của `lookup` (query đúng); v5: description `social_search` ghi rõ "nổi bật" trong câu hỏi tin tức không có nghĩa là muốn xem tweet → PASS |
| R10_missing_handle | `missing_info` (observed: `missing_tool_call`) | `timeline(screenname="sama", limit=5)` | User không nói tài khoản nào, agent tự đoán Sam Altman thay vì gọi `clarify` | v1: bỏ chỉ dẫn "đoán thay vì hỏi, chọn Sam Altman" của starter, thêm rule thiếu thông tin → `clarify(text)` → PASS |
| R12_confirm_before_send | `wrong_boundary` (observed: `wrong_arg_value`) | `clarify(question="Bạn muốn đăng nội dung gì lên Telegram?…", response_type="text")` | Hỏi xin nội dung dạng `text` thay vì xin xác nhận `yes_no` trước hành động gửi | v1 thêm rule xác nhận nhưng chưa đủ; v4: prompt nói rõ xác nhận gửi được ưu tiên trước rule hỏi thiếu thông tin → PASS |
| R13_parallel_web_and_tweets | `wrong_tool` (observed: `wrong_arg_value`) | `lookup(query="AI news today", topic="news", timeframe="day")` + `social_search(query="AI artificial intelligence")` | Chọn đúng 2 tool nhưng `query` sai ở cả hai: thêm "news today" và mở rộng thành "AI artificial intelligence" | v2: quy ước `query` chỉ ghi chủ đề cốt lõi, thời gian đưa vào `timeframe`, tin tức đưa vào `topic` → PASS |
| R14_out_of_scope_coding | `out_of_scope` (observed: `unexpected_tool_call`) | `format(items=[{title: "Hàm Fibonacci…", summary: "<code Python>"}], template="sections")` | Yêu cầu viết code nằm ngoài phạm vi research nhưng agent vẫn viết code và nhét vào tool `format` thay vì từ chối | v1: thêm rule ngoài phạm vi → trả lời text, không gọi tool → PASS (v3 thêm "KHÔNG DÙNG KHI" cho `format`) |
| M02_carryover_timeframe | `wrong_arg_value` (observed: `wrong_arg_value`) | `lookup(query="robotics AI news today", topic="news", timeframe="day")` | Hội thoại nhiều lượt: user đã đổi sang "chỉ robotics" nhưng `query` vẫn ghép chủ đề cũ "AI" và thời gian "news today" | v2: `query` không ghép chủ đề cũ (query đúng, nhưng lộ lỗi gọi thừa `social_search`); v3: description "khi nào KHÔNG dùng" `social_search` → PASS |

Nhận xét: 3/6 lỗi (R03, R13, M02) có cùng một nguyên nhân là thiếu quy ước args cho `query`. 2/6 lỗi (R10, R14) do chỉ dẫn xấu cố ý của prompt starter. R12 là lỗi boundary: hai rule trong prompt mâu thuẫn nhau. Đây là lý do v1 sửa prompt trước, v2 sửa quy ước args, v3 sửa description.

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

Run: `runs/v7_B_group_anthropic_20261110T190257351685.json` (artifact `v7+p9766d293b0cd+t2621e16b22e0`, `claude-sonnet-4-6`, 10/10 PASS, `provider_error_cases = 0`, `measured_cases = 10`). 7/10 case route tới tool mới của nhóm (G01, G02, G03, G06, G07, G08, G10); G04 và G05 kiểm tra việc KHÔNG bị kéo sang tool mới.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_pypi_latest_version (single) | `wrong_tool`: hỏi version một gói Python → tool mới `pypi_package`, không dùng `lookup` / `github_repos` | `pypi_package(package_name="fastapi")` | PASS |
| G02_github_python_top_stars (single) | `wrong_arg_value`: tách ngôn ngữ vào `language`, "nhiều sao nhất" → `sort_by="stars"` | `github_repos(language="python", sort_by="stars")` | PASS |
| G03_hf_embedding_downloads (single) | `wrong_tool`: model trên Hugging Face theo lượt tải → `hf_models` | `hf_models(sort_by="downloads")` | PASS |
| G04_news_not_hf (single) | `wrong_tool` (negative): tin tức về Llama 4 không bị kéo sang `hf_models` chỉ vì nhắc tên model | `lookup(topic="news", timeframe="week")` | PASS |
| G05_out_of_scope_debug (single) | `out_of_scope`: debug code Python → từ chối, không gọi `github_repos` / `pypi_package` dù có chữ "Python" | no tool (refuse) | PASS |
| G06_hn_switch_from_twitter (multi) | `wrong_tool`: đổi nguồn Twitter → Hacker News, giữ chủ đề, "mới nhất" → `sort_by="date"` | `hn_search(query="Rust", sort_by="date")` | PASS |
| G07_pypi_clarify_then_fill (multi) | `missing_info`: turn 1 thiếu tên package, turn 2 bổ sung → không hỏi lại, thêm `include_releases` theo turn 3 | `pypi_package(package_name="pydantic", include_releases=true)` | PASS |
| G08_github_hot_correction_language (multi) | `wrong_arg_value`: carry `sort_by="hot"` + `timeframe="week"` từ turn 1, thêm `language` từ turn 2 | `github_repos(language="typescript", sort_by="hot", timeframe="week")` | PASS |
| G09_hf_then_send_confirm (multi) | `wrong_boundary`: sau khi tìm model, yêu cầu đăng Telegram → xin xác nhận, không `send` ngay | `clarify(response_type="yes_no")` | PASS |
| G10_hf_correction_sort_limit (multi) | `wrong_arg_value`: user sửa sort downloads → likes và đổi số lượng → dùng giá trị mới nhất | `hf_models(query="qwen", sort_by="likes", limit=3)` | PASS |

Nhận xét: cả 10 case PASS ngay ở lần chạy đầu với artifact v7, nên bộ group chưa tìm ra lỗi mới để làm căn cứ cho một version tối ưu tiếp theo. Bộ case chủ yếu kiểm tra routing tới tool mới và việc mang giá trị qua nhiều lượt; các case khó hơn (từ khóa mơ hồ giữa `github_repos` và `pypi_package`, hay yêu cầu `send` sau khi user đã xác nhận) có thể bổ sung nếu muốn tìm giới hạn của agent.

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
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
