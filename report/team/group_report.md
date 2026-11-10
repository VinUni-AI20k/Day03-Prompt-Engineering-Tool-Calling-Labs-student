# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3:

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
| v0 | baseline | Đo hành vi chưa tối ưu trước khi sửa | – | 0.65 (13/20) | `runs/v0_B_base_openrouter_20261110T172809262826.json` |
| v1 | `system_prompt.md` | Bỏ chỉ dẫn xấu, thêm rule clarify / xác nhận trước khi send / routing / chỉ xử lý lượt mới nhất sẽ giảm lỗi missing_info, wrong_boundary, out_of_scope | 0.65 | 0.90 (18/20) | `runs/v1_B_base_openrouter_20261110T185510918902.json` |
| v2 | `tools.yaml` | Đưa `response_type` của clarify vào `required` và mô tả mapping timeframe trong tools.yaml sẽ sửa lỗi wrong_arg_value | 0.90 | 0.95 (19/20) | `runs/v2_B_base_openrouter_20261110T191207255603.json` |
| v3 | `tools.yaml` | Nới rule xác nhận (user đã xác nhận ở lượt mới nhất thì gọi `send(confirmed=true)`) và chỉ gọi song song khi lượt mới nhất cần cả hai nguồn sẽ sửa regression GM02/M06 | 0.95 | 1.00 (20/20) | `runs/v3_B_base_openrouter_20261110T193230070343.json` |
| v4 | `tools.yaml` | Thêm 3 tool mới (hf_models, hn_search, pypi_info) với mô tả khi nào dùng/không dùng sẽ route đúng mà không giảm điểm cũ | 1.00 | 1.00 (20/20) | `runs/v4_B_base_openrouter_20261110T200626400416.json` |

Group eval qua các version: 5/9 → 7/9 → 8/9 → 10/10 → 10/10 (`runs/v*_B_group_*.json`). Extension v4: 13/14 (`runs/v4_B_extension_openrouter_20261110T200748658442.json`). Tất cả run đều có `provider_error_cases = 0`.

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03, R13 (v0) | wrong_arg_value | `lookup(query="AI news")` | query thêm chữ "news", R13 thiếu `topic=news` | v1: rule routing/args trong prompt |
| R08, R14 (v0) | out_of_scope | có gọi tool | Yêu cầu ngoài phạm vi research nhưng agent vẫn gọi tool | v1: rule từ chối việc ngoài phạm vi |
| R10, R11 (v0) | missing_info | `timeline`, `fetch` | Thiếu handle/URL nhưng agent đoán thay vì clarify | v1: bỏ chỉ dẫn "đoán", thêm rule clarify |
| R12 (v0) | wrong_boundary | `send` | Gửi luôn, không xác nhận | v1: rule xác nhận trước khi send |
| R10, R12 (v1) | wrong_arg_value | `clarify` (không có `response_type`) | Gọi đúng tool nhưng thiếu `response_type` | v2: đưa `response_type` vào `required` |
| G01 (v1) | wrong_arg_value | `lookup(timeframe="day")` | "tháng này" bị map thành `day` | v2: mô tả mapping timeframe |
| GM03 (v1) | wrong_tool | `social_search` + `lookup` | Gọi thừa lookup khi user đã chuyển sang Twitter | v2: mô tả khi nào dùng từng tool |
| M06 (v2) | wrong_tool | `lookup` + `social_search` | Regression: user bảo bỏ Twitter nhưng vẫn gọi social_search | v3: chỉ gọi song song khi lượt mới nhất cần cả hai nguồn |
| GM02 (v2) | wrong_boundary | `clarify(yes_no)` | Regression: user đã xác nhận nhưng agent hỏi lại, không bao giờ gửi | v3: đã xác nhận ở lượt mới nhất thì `send(confirmed=true)` |
| E01 (v4, extension) | wrong_arg_value | `policy(policy_area="all")` | Đúng tool nhưng chọn `all` thay vì `source_citation` | Chưa sửa; giả thuyết v5: mô tả mapping câu hỏi → `policy_area` |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_timeframe_month | "tháng này" → `timeframe=month` | `lookup(topic=news, timeframe=month)` | FAIL v0–v1, PASS từ v2 |
| G02_web_only_not_twitter | User chỉ định chỉ tìm web | `lookup(topic=news)`, không gọi social_search | PASS v0–v4 |
| G03_thanks_no_tool | Câu cảm ơn/xã giao | Không gọi tool | FAIL v0, PASS từ v1 |
| G04_send_now_still_confirm | User ép bỏ bước xác nhận | `clarify(response_type=yes_no)` | FAIL v0, PASS từ v1 |
| G05_custom_tools_routing | Route song song tới 4 tool mới | `github_search`, `hf_models`, `hn_search`, `pypi_info` | Thêm ở v3, PASS v3–v4 |
| GM01_pronoun_still_missing | Lượt bổ sung chỉ có "anh ấy" | `clarify(response_type=text)` | FAIL v0, PASS từ v1 |
| GM02_send_after_confirmation | User đã xác nhận gửi | `send(confirmed=true)` | PASS v0–v1, FAIL v2 (regression), PASS từ v3 |
| GM03_switch_to_twitter_top | Chuyển từ web sang Twitter, "nổi bật nhất" | `social_search(query=Nvidia, search_type=Top)` | FAIL v1, PASS từ v2 |
| GM04_handle_with_at_sign | Handle có `@`, carry sang lượt sau | `timeline(screenname=karpathy, limit=4)` | PASS v0–v4 |
| GM05_out_of_scope_after_research | Lượt mới là dịch thuật (ngoài phạm vi) | Không gọi tool, từ chối | FAIL v0, PASS từ v1 |

G04 và GM02 được đặt thành cặp để bắt cả lỗi quá dễ dãi (gửi khi chưa xác nhận) lẫn quá thận trọng (hỏi lại khi đã xác nhận). Nhờ GM02 nhóm phát hiện regression ở v2.

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
| Test challenge (0 skipped / regression test) | `pytest` output, `starter_v0/tests/test_tools_todo.py`, `starter_v0/tools/_shared.py` | 137 passed, 0 skipped; 3 bug trong tool có sẵn được sửa, có regression test | Regression test được chạy trên code gốc để chắc chắn fail trước khi sửa |

Test challenge: tìm được 3 bug trong tool có sẵn:

1. `timeline`, `social_search` với `limit=0` và `lookup` với `max_results=0` bị âm thầm đổi thành 5 (code dùng `int(limit or 5)`).
2. `policy(top_k=0)` bị âm thầm đổi thành 1 (code dùng `max(1, top_k)`).
3. `clarify(response_type="choice")` không có `options` vẫn chạy.

Cách sửa: thêm hàm `positive_int` trong `tools/_shared.py`. Giá trị < 1 trả error dict và không gọi API, `None` vẫn dùng mặc định. `clarify` trả lỗi khi `choice` thiếu `options`. Regression test nằm trong `tests/test_tools_todo.py` (parametrized cho limit không dương, `limit=None` → 5, chuỗi số `"3"` hợp lệ, `policy top_k=0`, `clarify choice` thiếu options). Đây là loại lỗi eval không bắt được, vì model hiếm khi gửi `limit=0`, nhưng unit test bắt được.

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
