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
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

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
|Item|Evidence File|What Worked|Risk / Guardrail|
|-|-|-|-|
|Tool mới (`tools/<tên>/`)|[`github_search`](../../starter_v0/tools/github_search/tool.py), [`hf_search`](../../starter_v0/tools/hf_search/tool.py); đăng ký trong [`tools/__init__.py`](../../starter_v0/tools/__init__.py) và khai báo trong `artifacts/tools.yaml`|Bổ sung tìm repository GitHub và model/dataset Hugging Face; chuẩn hóa kết quả về `title`, `url`, `source`, `summary` cùng metadata riêng của từng nguồn. Eval nhóm có case dùng cả hai tool (G01–G03, G06–G10); run có 10/10 case được đo.|GitHub Search API bị HTTP 403 rate limit trong cả 7 lần gọi ở run nhóm; kết quả PASS của eval chỉ xác nhận routing/arguments, không đảm bảo API trả dữ liệu. Có thể cấu hình `GITHUB_TOKEN`/`HF_TOKEN`; lỗi API được trả về dưới dạng error dict.|
|Unit test tool mới (≥ 3 test/tool)|[`tests/test_tools_todo.py`](../../starter_v0/tests/test_tools_todo.py); `pytest -q` từ `starter_v0/` → **93 passed, 0 failed, 0 skipped**|Đã viết **7 test** cho hai tool mới: 4 cho `github_search` và 3 cho `hf_search`, bao gồm request/response mapping, input không hợp lệ, lỗi HTTP/timeout. Test dùng HTTP giả lập, không cần gọi API thật.|Eval không kiểm tra phần triển khai HTTP hay chuẩn hóa payload. Ví dụ, nếu `github_search` lấy sai `html_url`/`full_name` từ payload thì unit test `test_github_search_sends_expected_request_and_maps_repos` bắt được, trong khi eval chỉ chấm tool và arguments do model chọn.|
|UI (lệnh chạy + link dùng thử)|Chạy từ `starter_v0/`: `streamlit run app.py`; local: [http://localhost:8501](http://localhost:8501)|App Streamlit cho phép chọn provider/model, nhãn phiên bản, chat và xem tool events.|Đây là link local, chỉ truy cập được khi app đang chạy trên máy người dùng; chưa có link deploy/public để báo cáo. Cần cấu hình API key phù hợp trong `.env` hoặc qua UI.|

**Tool unit tests:** 7 test cho tool mới (4 `github_search`, 3 `hf_search`). Ví dụ lỗi implementation mà eval không bắt được: API response có repository nhưng mapping trả sai URL hoặc tên; unit test kiểm tra request và object đã chuẩn hóa, còn eval chỉ chấm lựa chọn tool/arguments.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper\_text`) không tự được bonus.

|Bonus|Evidence File|What Worked|Risk / Guardrail|
|-|-|-|-|
|Small Local Model|Chưa có run Ollama/local model được lưu; xem B7.|Chưa có kết quả local để báo cáo.|Không tuyên bố đã đạt bonus khi chưa có run JSON làm bằng chứng.|
|Hơn 3 tool mới (≥ 4)|Chưa áp dụng: có 2 tool mới (`github_search`, `hf_search`).||Không đạt ngưỡng 4 tool mới; không tính tool có sẵn.|
|`send` gửi thật lên Telegram sau xác nhận|Chưa có transcript gửi Telegram thật được lưu trong workspace.||Không khẳng định đã gửi thật; unit test chỉ giả lập HTTP và không gửi Telegram.|
|Test challenge (0 skipped / regression test)|`pytest -q` từ `starter_v0/` → **93 passed, 0 skipped**; [`tests/test_tools_todo.py`](../../starter_v0/tests/test_tools_todo.py)|Các test challenge hiện chạy hết; có test kiểm tra policy đưa nội dung giống chỉ dẫn vào `untrusted_text`, không coi nội dung đó là facts.|Chưa có bằng chứng về bug tool có sẵn đã được xác định, sửa và gắn regression test cụ thể; vì vậy không tuyên bố đã đạt bonus bug-fix/regression.|

Test challenge: chưa ghi nhận bug tool có sẵn nào đã được xác nhận và sửa trong bằng chứng hiện có (0 bug-fix/regression được báo cáo). `test_policy_instruction_like_lines_go_to_untrusted_text` là kiểm tra guardrail hiện có, không được trình bày như regression test cho một bug đã sửa.

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
