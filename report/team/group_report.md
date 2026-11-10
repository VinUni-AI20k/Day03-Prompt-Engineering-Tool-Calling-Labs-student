# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: Hehehe (theo tên repo; cần nhóm xác nhận).
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model: v0 dùng `openai` / `gpt-4o-mini`; v1–v3 chưa chạy.
- Trạng thái: đã hoàn thiện bằng chứng CP1, CP3 và bonus ≥ 4 tool tự viết (12 unit test, 1 eval routing); eval nhóm còn 9 case, CP2, UI và live chat chưa hoàn thành.

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
| github_search | tìm repository GitHub công khai theo từ khóa, ngôn ngữ và cách sắp xếp | có |
| deduplicate_sources | loại nguồn trùng theo URL chuẩn hóa hoặc tiêu đề | có |
| compare_sources | so sánh metadata, độ đầy đủ và điểm giống/khác giữa các nguồn | có |
| filter_by_date | lọc danh sách nguồn theo khoảng ngày bao gồm hai biên | có |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

- Thêm `github_search` để tìm implementation, thư viện và dự án mã nguồn trên GitHub; agent chỉ nên gọi tool này cho yêu cầu về repository/code, không dùng thay web search, arXiv hoặc social search.
- Thêm ba tool xử lý cục bộ: `deduplicate_sources` loại kết quả trùng, `compare_sources` tạo bảng so sánh metadata minh bạch, và `filter_by_date` lọc nguồn theo khoảng ngày. Cả ba không gọi mạng và không có side effect.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Chưa áp dụng thay đổi; đo điểm xuất phát | N/A | case_accuracy=0.70 | [Run v0](../../starter_v0/runs/v0_B_base_openai_20261110T180441850646.json) |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

**Chi tiết v0:** 20/20 case được đo, 0 lỗi provider, 14/20 pass; `tool_routing_accuracy=0.75`, `argument_accuracy=0.70`, `multiturn_accuracy=1.00`. Multi-turn 100% chỉ phản ánh các case multi-turn trong suite này.

- `artifact_version`: `v0+peb1c8179815b+te69bc53ed884`
- `prompt_hash`: `eb1c8179815bd79d34de7d326420bb99b3072e6e8ae96464c02d4411f905fc68`
- `tools_hash`: `e69bc53ed8846a5c2192e950c539806a61a6902b718f06d6773db6a42e9b996c`
- [Version log](../../starter_v0/artifacts/version_log.csv).
- Kiểm thử offline được Codex chạy lại: **62 passed, 17 skipped, 0 failed**; [output](../../starter_v0/analysis/cp1_pytest.txt). Các skip là TODO, không phải test đã triển khai.

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `send(text=trả lời tích phân)` | Kỳ vọng không gọi tool; model dùng send cho bài toán ngoài phạm vi. Giả thuyết: mô tả vai trò/tool chưa giới hạn rõ mục đích. | Đề xuất: quy định phạm vi research và không gọi tool cho yêu cầu ngoài phạm vi. |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | User chưa cho tài khoản nhưng model tự chọn sama thay vì clarify; phù hợp với chỉ dẫn đoán trong prompt baseline. | Đề xuất: thiếu tài khoản thì hỏi bằng clarify, không tự chọn người. |
| R11_missing_url | missing_info | `fetch(url="https://example.com/article")` | User chưa đưa URL nhưng model tự tạo URL thay vì hỏi lại; phù hợp với chỉ dẫn đoán trong prompt baseline. | Đề xuất: thiếu URL thì clarify, không tự tạo liên kết. |
| R12_confirm_before_send | wrong_boundary | `send(text="Bản tin này")` | Thiếu clarify với response_type=yes_no trước gửi; prompt baseline khuyến khích gửi ngay. | Đề xuất: chuẩn bị nội dung và xin xác nhận rõ trước khi gọi send với confirmed=true. |
| R13_parallel_web_and_tweets | wrong_tool (nhãn case); thực tế wrong_arg_value | `lookup(query="AI news", timeframe="day", max_results=5)` và `social_search(query="AI", search_type="Latest", limit=5)` | Chọn đúng hai tool nhưng lookup thiếu topic=news và query không khớp giá trị AI mà eval yêu cầu. Giả thuyết: convention arguments chưa rõ. | Đề xuất: làm rõ topic=news, timeframe=day và quy ước query trong declaration; review mức chặt của kỳ vọng query. |
| R14_out_of_scope_coding | out_of_scope | `send(text=code Fibonacci)` | Kỳ vọng không gọi tool; model dùng send cho yêu cầu coding ngoài phạm vi. | Đề xuất: làm rõ phạm vi và send chỉ dành cho gửi Telegram sau xác nhận. |

Nguồn cho toàn bộ bảng: [run v0](../../starter_v0/runs/v0_B_base_openai_20261110T180441850646.json), `results[*].result`. Mọi mục Fix ở trên là **đề xuất, chưa áp dụng và chưa đo hiệu quả**.

Lưu ý khi đọc kết quả:

- R13 có `routing_correct=true`, `args_correct=false`, `observed_mismatch=wrong_arg_value`. Bộ chấm giữ nhãn failure_type của case là wrong_tool; cần phân biệt nhãn thiết kế với lỗi quan sát thực tế, không sửa case để tăng điểm.
- Các lời gọi send sai ở R08, R12, R14 đều bị code chặn với `status=needs_confirmation`; log không chứng minh có gửi Telegram thành công.
- Run hợp lệ về provider không đồng nghĩa mọi nội dung nguồn hoặc mọi kết quả tool đều đúng; vẫn cần review thủ công.


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
| Tool mới (`tools/<tên>/`) | `starter_v0/tools/{github_search,deduplicate_sources,compare_sources,filter_by_date}/`; registry và `artifacts/tools.yaml` | 1 tool tìm repository và 3 tool xử lý nguồn cục bộ | Validate kiểu/range/enum; mọi lỗi trả error dict; không có write side effect |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py`; `starter_v0/analysis/cp3_pytest.txt` | 12 test function cho happy path, input xấu và failure path của 4 tool | HTTP GitHub được mock offline; local tools không gọi mạng |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: đã viết 12 test function cho 4 tool tự thêm. Ví dụ lỗi mà unit test bắt được nhưng eval không bắt được: GitHub trả HTTP 503, item không phải object, khoảng ngày đảo ngược; tool phải trả error dict thay vì làm agent crash.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) | `tools/github_search`, `tools/deduplicate_sources`, `tools/compare_sources`, `tools/filter_by_date`; `tests/test_tools_todo.py` | Đủ 4 tool tự viết, mỗi tool có `TOOL.md`, registry, declaration và ≥ 3 test | Ba tool xử lý nguồn chạy local; GitHub chỉ đọc public API; mọi tool validate input |
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

### Ghi nhận xử lý môi trường tại CP1

- Bình ban đầu gặp lỗi PowerShell vì biến `$labPython` chưa có giá trị trong phiên Terminal; đã gán đường dẫn Python của venv và chạy được script.
- Sau đó gặp `Missing API key env var: OPENAI_API_KEY`; đã được hướng dẫn cấu hình đúng `starter_v0/.env`. Bình báo preflight thành công; không lưu API key vào báo cáo. Chưa có file log riêng cho hai lỗi này; bằng chứng trao đổi nằm trong chat, không coi là log đã nộp trong repo.
- Run v0 trong repo xác nhận provider OpenAI hoạt động: 20 case được đo, 0 lỗi provider.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

### Nhận xét sau baseline v0

- Thay đổi thuộc system prompt: bỏ hành vi đoán account/URL; hỏi lại khi thiếu dữ liệu; đặt phạm vi research và quy tắc xác nhận.
- Thay đổi thuộc tools.yaml: mô tả khi dùng/không dùng tool, convention arguments, ý nghĩa send và confirmed.
- Cần review thủ công: chênh lệch nhãn lỗi R13; tính hợp lý của query tương đương; chất lượng dữ liệu tool; việc code chặn send dù model đã chọn sai hành động.
- Giả thuyết dự kiến v1: thay riêng quy tắc thiếu thông tin trong prompt bằng yêu cầu clarify sẽ giảm lỗi missing_info của R10/R11. Chưa sửa prompt, chưa chạy v1; sẽ đo lại toàn suite để kiểm tra tác động và regression.

## 8. Tài liệu tham khảo

- [Quy định bài lab](../../RULES.md), [checkpoints](../../CHECKPOINTS.md), [rubric](../../RUBRIC.md).
- [System prompt baseline](../../starter_v0/artifacts/system_prompt.md), [tool declaration](../../starter_v0/artifacts/tools.yaml).
