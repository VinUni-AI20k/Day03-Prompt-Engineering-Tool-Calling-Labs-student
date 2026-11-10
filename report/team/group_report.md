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
| v0 | baseline | Đo hành vi chưa tối ưu (prompt starter còn chỉ dẫn xấu) | — | 0.70 (14/20) | `runs/v0_B_base_openrouter_20261110T174519840832.json` |
| v1 | system_prompt.md | Bỏ chỉ dẫn đoán/gửi ngay/một bước, thêm rule `clarify` khi thiếu thông tin và xác nhận trước `send` thì R10, R11, R12 sẽ PASS | 0.70 | 0.80 (16/20) | `runs/v1_B_base_openrouter_20261110T180453970452.json` |
| v2 | system_prompt.md | Thêm rule routing theo loại yêu cầu và điều kiện không cần hỏi lại thì hồi quy R01, M02, M06 của v1 sẽ được sửa | 0.80 | 0.90 (18/20) | `runs/v2_B_base_openrouter_20261110T182517635389.json` |
| v3 | system_prompt.md + tools.yaml | Làm rõ khi nào dùng / không dùng ở cả prompt (rule đổi nguồn, rule xác nhận trước `send`) và `tools.yaml` (description, convention args, boundary `send`) thì R12 và M06 sẽ PASS | 0.90 | 0.85 (17/20) | `runs/v3_B_base_openrouter_20261110T184418744227.json` |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `send(text="Nguyên hàm của x^2 là …")` | Câu hỏi toán nằm ngoài phạm vi research agent nhưng model gọi `send` thay vì từ chối (`unexpected_tool_call`). Nguyên nhân: prompt bảo "cứ làm ngay", không có rule phạm vi/từ chối. | Thêm vào prompt: ngoài phạm vi (toán, code, hỏi đáp chung) thì từ chối ngắn gọn, không gọi tool. |
| R14_out_of_scope_coding | out_of_scope | `send(text="Dưới đây là một hàm Python tính Fibonacci …")` | Yêu cầu viết code bị coi như nội dung để gửi, gọi `send` (`unexpected_tool_call`). Cùng nguyên nhân với R08. | Cùng fix với R08 (rule phạm vi), mô tả `send` chỉ dùng khi user yêu cầu gửi/đăng bản tin. |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Câu hỏi không nói rõ tài khoản nhưng model tự chọn Sam Altman (`missing_tool_call: clarify`, thêm `timeline`). Nguyên nhân: prompt bảo "chọn một tài khoản nổi tiếng". | Xoá chỉ dẫn đoán; thêm rule: thiếu handle thì gọi `clarify` (`response_type=text`). |
| R11_missing_url | missing_info | `fetch(url="https://example.com/article")` | Chỉ có "bài viết này" nhưng model tự bịa URL (`missing_tool_call: clarify`, thêm `fetch`). Nguyên nhân: prompt bảo "assume a likely URL". | Xoá chỉ dẫn đoán URL; thêm rule: thiếu URL thì gọi `clarify`. |
| R12_confirm_before_send | wrong_boundary | `send(text="Bản tin này")` | Gọi `send` ngay, không hỏi xác nhận (`missing_tool_call: clarify`, thêm `send`). Nguyên nhân: prompt bảo "cứ gửi luôn"; `send` không mô tả điều kiện xác nhận. Guardrail của code chỉ trả `needs_confirmation`. | Prompt: gửi/đăng thì `clarify(response_type=yes_no)` trước, chỉ `send(confirmed=true)` sau khi user đồng ý; sửa description `send` trong `tools.yaml`. |
| R13_parallel_web_and_tweets | wrong_tool (harness gán; `observed_mismatch` = `wrong_arg_value`) | `lookup(query="AI news", timeframe="day", max_results=5)` + `social_search(query="AI", search_type="Latest", limit=5)` | Chọn đúng cả hai tool (`routing_correct=True`) nhưng `lookup` sai args: `query` là "AI news" thay vì "AI" và thiếu `topic="news"`. Nguyên nhân: `tools.yaml` chưa nêu convention `topic=news` cho tin tức và `query` chỉ chứa từ khoá. | Sửa description/param của `lookup` trong `tools.yaml`: tin tức dùng `topic="news"`, `query` chỉ là từ khoá, không thêm "news". |

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
