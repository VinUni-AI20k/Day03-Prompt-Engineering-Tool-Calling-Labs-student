# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: OpenAI `gpt-4o-mini` (`--provider openai`, temperature 0)

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
| v0 | baseline | Đo hành vi của prompt và tools starter chưa sửa | — | 0.65 | [`runs/v0_B_base_openai_20261110T181546506674.json`](../../starter_v0/runs/v0_B_base_openai_20261110T181546506674.json) |
| v1 | `system_prompt.md` | 5/7 case FAIL ở v0 (R08, R10, R11, R12, R14) do prompt dặn đoán handle, bịa URL, gửi ngay. Thay bằng rule hỏi lại bằng `clarify`, xác nhận trước khi gửi, không gọi tool khi ngoài phạm vi sẽ sửa các case này. | 0.65 | 0.80 | [`runs/v1_B_base_openai_20261110T184119766103.json`](../../starter_v0/runs/v1_B_base_openai_20261110T184119766103.json) |
| v2 | `tools.yaml` | Sau v1, R11, R12, R13 đã chọn đúng tool nhưng sai tham số (thiếu `response_type`, `text` thay vì `yes_no`, thiếu `topic="news"`) vì description tham số quá mơ hồ. Viết lại description mọi tool (làm gì, khi nào dùng, khi nào không) và ghi rõ convention từng tham số sẽ sửa các case này. | 0.80 | 0.90 | [`runs/v2_B_base_openai_20261110T184931003075.json`](../../starter_v0/runs/v2_B_base_openai_20261110T184931003075.json) |
| v3 | `system_prompt.md` | M06 FAIL từ v1 (gọi thừa `social_search` dù user đã bỏ Twitter) do rule "nhiều nguồn → gọi đủ tool" quá rộng. Thu hẹp rule (chỉ khi user yêu cầu rõ nhiều nguồn) và thêm rule "lượt sau ghi đè lượt trước" sẽ sửa M06 mà không làm hỏng R13. | 0.90 | 0.90 | [`runs/v3_B_base_openai_20261110T185149151645.json`](../../starter_v0/runs/v3_B_base_openai_20261110T185149151645.json) |

Metric = `case_accuracy` trên bộ base 20 case, provider openai `gpt-4o-mini`. Hash từng version nằm trong [`version_log.csv`](../../starter_v0/artifacts/version_log.csv). Mỗi version chỉ đổi một artifact: v1 và v3 chỉ đổi `prompt_hash`, v2 chỉ đổi `tools_hash`.

| Chỉ số | v0 | v1 | v2 | v3 |
|---|---:|---:|---:|---:|
| `case_accuracy` | 0.65 | 0.80 | 0.90 | 0.90 |
| `tool_routing_accuracy` | 0.75 | 0.95 | 0.95 | 0.95 |
| `argument_accuracy` | 0.65 | 0.80 | 0.90 | 0.90 |
| `multiturn_accuracy` | 1.00 | 0.83 | 0.83 | 1.00 |
| Case FAIL | R03, R08, R10, R11, R12, R13, R14 | R11, R12, R13, M06 | R12, M06 | R10, R12 |

**Kết quả v1 so với v0** (`prompt_hash` f0c107a9d7a1 → c396dd255888, `tools_hash` giữ nguyên 41a2894f8ad1):
- Được sửa: R08, R10, R14 (đúng giả thuyết). R03 cũng PASS (`query` từ "AI news" thành "AI") dù v1 không nhắm vào case này, nên có thể chỉ là dao động của model.
- Giả thuyết đúng một phần: R11 và R12 đã gọi `clarify` (routing đúng, `tool_routing_accuracy` 0.75 → 0.95) nhưng vẫn sai tham số. R11 bỏ trống `response_type`; R12 dùng `response_type="text"` để hỏi nội dung bản tin thay vì `yes_no` để xác nhận.
- Vẫn FAIL như dự kiến: R13 (`lookup` thiếu `topic="news"`), dành cho v2.
- Lỗi mới (regression): M06. User đã nói "Bỏ Twitter" nhưng model vẫn gọi thêm `social_search`. Khả năng cao do rule mới "Nhiều nguồn → gọi đủ các tool" khiến model gọi thừa.
- R08 và R14 PASS vì không gọi tool, nhưng model vẫn giải toán và viết code thay vì từ chối. Eval chỉ chấm việc có gọi tool hay không, nên phần này cần review thủ công.

**Kết quả v2 so với v1** (`tools_hash` 41a2894f8ad1 → 8ee23b5594df, `prompt_hash` giữ nguyên c396dd255888):
- Được sửa: R11 (giờ truyền `response_type="text"`) và R13 (`lookup` có `topic="news"`). Đúng giả thuyết.
- Vẫn FAIL: R12. Dù cả prompt lẫn description của `response_type` đều nói gửi/đăng thì dùng `yes_no`, model vẫn hỏi nội dung bản tin bằng `text`. User nói "bản tin này" mà không đưa nội dung, nên model ưu tiên hỏi thông tin còn thiếu. Hành vi này an toàn (không gửi gì) nhưng khác với điều eval mong đợi.
- Vẫn FAIL: M06 (gọi thừa `social_search`). v2 không nhắm vào case này, để dành cho v3.

**Kết quả v3 so với v2** (`prompt_hash` c396dd255888 → 83c2d72ee7b1, `tools_hash` giữ nguyên 8ee23b5594df):
- Được sửa: M06 (chỉ gọi `lookup`, `multiturn_accuracy` trở lại 1.0). R13 vẫn PASS. Đúng giả thuyết.
- Lỗi mới (regression): R10 ("Tóm tắt 5 tweet mới nhất giúp mình", không nói tài khoản). Model gọi `social_search(query="")` thay vì `clarify`. Kiểm tra thêm bằng cách gọi model 5 lần cho câu này (không chạy tool): prompt v2 cho `clarify` 5/5 lần, prompt v3 cho `social_search` 5/5 lần. Vậy lỗi ổn định và do thay đổi của v3, không phải dao động. Giả thuyết: các ví dụ mới trong rule ("tìm thêm tweet", "chỉ xem trên Twitter") khiến model gắn chữ "tweet" với `social_search`.
- `case_accuracy` giữ nguyên 0.90 vì sửa được 1 case và hỏng 1 case. v3 xác nhận được giả thuyết về M06 nhưng tạo ra lỗi mới.

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

Run v0: [`starter_v0/runs/v0_B_base_openai_20261110T181546506674.json`](../../starter_v0/runs/v0_B_base_openai_20261110T181546506674.json) (`v0+pf0c107a9d7a1+t41a2894f8ad1`, openai `gpt-4o-mini`). Run hợp lệ: 20/20 case được đo, 0 lỗi provider. Kết quả: 13/20 PASS, `case_accuracy` = 0.65, `tool_routing_accuracy` = 0.75, `argument_accuracy` = 0.65, `multiturn_accuracy` = 1.0.

Cột Failure Type ghi loại lỗi thực tế quan sát được. Nếu khác nhãn `failure_type` ghi sẵn trong eval thì ghi cả hai.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | `wrong_arg_value` (eval gắn nhãn `wrong_tool`) | `lookup(query="AI news", topic="news", timeframe="day")` | Chọn đúng tool, đúng `topic` và `timeframe`, nhưng thêm chữ "news" vào `query` (eval mong `query="AI"`). Description của `query` chỉ ghi "Truy vấn", không nói phần "tin tức/hôm nay" đã nằm trong `topic`/`timeframe`. | v2 (`tools.yaml`): mô tả `lookup.query` chỉ chứa từ khóa chủ đề; "tin tức", "hôm nay" thể hiện bằng `topic`/`timeframe`, không lặp lại trong query. |
| R08_out_of_scope | `out_of_scope` | `send(text="Nguyên hàm của x^2 là …")` | Câu toán ngoài phạm vi research. Model tự giải rồi gọi `send` để gửi đáp án, dù user không yêu cầu gửi. Nguyên nhân: prompt starter dặn "call a tool right away" và gặp yêu cầu gửi/đăng thì "just go ahead". Code `send` trả `needs_confirmation` nên không gửi thật. | v1 (`system_prompt.md`): bỏ các chỉ dẫn ép gọi tool và gửi ngay; thêm rule phạm vi: câu ngoài research (toán, code…) thì không gọi tool, từ chối ngắn gọn và nói agent làm được gì. |
| R10_missing_handle | `missing_info` | `timeline(screenname="sama")` | User không nói tài khoản nào nhưng model đoán là Sam Altman, đúng như prompt starter dặn ("pick a well-known account like Sam Altman"). | v1: bỏ chỉ dẫn đoán; thêm rule: thiếu tài khoản thì gọi `clarify(response_type="text")` để hỏi. |
| R11_missing_url | `missing_info` | `fetch(url="https://example.com/article")` | User nói "bài viết này" nhưng không đưa link. Model bịa URL `example.com` theo chỉ dẫn "assume a likely URL". | v1: bỏ chỉ dẫn bịa URL; thêm rule: không có URL thì gọi `clarify(response_type="text")` xin link, không tự đặt URL. |
| R12_confirm_before_send | `wrong_boundary` | `send(text="Bản tin này đã được đăng lên Telegram.")` | Gọi `send` ngay, không hỏi xác nhận, còn tự bịa nội dung (user chưa đưa bản tin nào). Không gửi thật chỉ vì code `send` chặn khi `confirmed=false` (trả `needs_confirmation`). | v1: bỏ "just go ahead and do it"; thêm rule: khi được yêu cầu gửi/đăng thì gọi `clarify(response_type="yes_no")` cho user xem nội dung trước, chỉ gọi `send(confirmed=true)` sau khi user đồng ý. v2: ghi boundary này cả trong description của `send`. |
| R13_parallel_web_and_tweets | `wrong_arg_value` (eval gắn nhãn `wrong_tool`) | `lookup(query="AI", timeframe="day")` + `social_search(query="AI")` | Gọi đủ 2 tool (routing đúng) nhưng `lookup` thiếu `topic="news"` nên dùng mặc định `general`. Cùng kiểu câu "tin AI hôm nay", R03 có `topic=news` còn R13 thì không, vì description không nói khi nào dùng `news`. | v2 (`tools.yaml`): mô tả `lookup.topic`: khi user hỏi tin tức, thời sự hoặc "tin … hôm nay/tuần này" thì dùng `topic="news"`. |
| R14_out_of_scope_coding | `out_of_scope` | `send(text="Dưới đây là một hàm Python tính số Fibonacci …")` | Giống R08: model viết code rồi gọi `send` để gửi đi. Code `send` trả `needs_confirmation`. | v1: cùng rule phạm vi như R08. |

**Tóm tắt v0:**
- 5/7 case FAIL (R08, R10, R11, R12, R14) do các chỉ dẫn xấu trong prompt starter: đoán tài khoản, bịa URL, gửi không cần xác nhận, ép gọi tool. Đây là cơ sở cho giả thuyết v1 (sửa `system_prompt.md`).
- 2/7 case FAIL (R03, R13) do sai tham số của `lookup` (`query`, `topic`) khi description quá mơ hồ. Đây là cơ sở cho giả thuyết v2 (sửa `tools.yaml`).
- Cả 6 case multi-turn đã PASS ở v0.

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
| Tool mới (`tools/<tên>/`) | `starter_v0/tools/save_note/tool.py`, `TOOL.md` | Lưu ghi chú/tóm tắt nghiên cứu ra file Markdown trong thư mục `notes/`, tự động chuẩn hóa đuôi `.md`, trả về status `saved` và path | Chống path traversal (`..`, `/`, `\`), từ chối input rỗng; chỉ ghi khi `confirmed=True`, trả `needs_confirmation` kèm preview nếu `confirmed=False` |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py` | 3/3 test PASS (`test_save_note_without_confirmation_does_not_write`, `test_save_note_happy_path`, `test_save_note_bad_input_from_model`) | Chặn lỗi ở tầng code Python khi model truyền input rỗng hoặc đường dẫn nguy hiểm |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: Đã viết 3 test hoàn chỉnh cho tool `save_note`.
Ví dụ lỗi mà unit test bắt được nhưng eval không bắt được: Nếu model gọi đúng tool `save_note(filename="../../etc/passwd", content="evil", confirmed=true)`, eval chỉ kiểm tra tên tool và tham số nên sẽ chấm PASS. Tuy nhiên, nếu không có unit test ở code Python để chặn path traversal, hàm sẽ ghi đè file hệ thống! Unit test đảm bảo code Python phát hiện và trả về `{"error": "invalid_filename"}` an toàn mà không crash.

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
