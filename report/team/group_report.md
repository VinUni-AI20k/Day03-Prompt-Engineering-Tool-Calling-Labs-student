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
| timeline | lấy các bài đăng gần đây của một tài khoản | không |
| social_search | tìm kiếm bài đăng trên mạng xã hội | không |
| lookup | tra cứu thông tin và tin tức trên internet | không |
| fetch | lấy nội dung văn bản từ một URL | không |
| format | trình bày dữ liệu đã có thành văn bản theo template | không |
| send | gửi một đoạn văn bản lên Telegram (khi được xác nhận) | không |
| policy | tra cứu tài liệu quy định nội bộ công ty | không |
| papers | tìm kiếm bài báo khoa học trên arXiv | không |
| paper_text | trích xuất nội dung text từ bài báo arXiv | không |
| text_stats | tính số từ, số ký tự và thời gian đọc ước tính cho văn bản | Có (Nguyễn Tuấn Dũng) |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

- **Tool mới `text_stats` (Nguyễn Tuấn Dũng - 2A202603859, CP3)**:
  - **Làm gì**: nhận `text` (chuỗi không rỗng) và `wpm` (mặc định 200 từ/phút, > 0), trả về số từ (`word_count`), số ký tự (`char_count`) và thời gian đọc ước tính theo giây (`estimated_reading_seconds`). Nếu input rỗng/sai kiểu hoặc `wpm <= 0`, tool trả về error dict (`status: "error"`) thay vì raise exception.
  - **Khi nào agent nên gọi**: khi người dùng yêu cầu đếm từ/ký tự, kiểm tra độ dài đoạn tóm tắt/bản nháp hoặc ước tính thời gian đọc (ví dụ trước khi gửi); không dùng để tìm kiếm web hay đọc URL.
  - **Tích hợp**: khai báo trong `starter_v0/artifacts/tools.yaml`, đăng ký trong `starter_v0/tools/__init__.py`, mô tả tại `starter_v0/tools/text_stats/Tool.md` (`starter_v0/tools/text_stats/tool.py`).

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

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) | `starter_v0/tools/text_stats/tool.py`, `Tool.md`, `starter_v0/tools/__init__.py`, `starter_v0/artifacts/tools.yaml` | Tính chính xác `word_count`, `char_count`, `estimated_reading_seconds` (hỗ trợ ép kiểu `wpm` dạng chuỗi như `"200"`), khớp contract test | Kiểm tra `text` rỗng/không phải `str`, `wpm` không phải số nguyên hoặc `<= 0` → trả error dict (`status: "error"`, `items: []`), không raise exception |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py`, `pytest tests/ -v` (`84 passed in 0.96s`, 0 failed, 0 skipped) | 3 tests cho `text_stats` (happy path, input chuỗi khoảng trắng rỗng, `wpm=0` và `wpm="invalid_int"`) + 14 tests cho các tool có sẵn đều pass | Toàn bộ suite chạy offline qua `fake_http` và `monkeypatch` (`block_network` chặn mọi request thật) |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: Đã viết 3 unit tests cho `text_stats` và hoàn thiện 14 test stubs cho các tool có sẵn (`clarify`, `format`, `send`, `lookup`, `fetch`, `timeline`, `social_search`, `policy`) trong `starter_v0/tests/test_tools_todo.py` (tổng 17 tests trong file này; toàn bộ suite `pytest tests/ -v` đạt **84 passed, 0 failed, 0 skipped**). Ví dụ lỗi mà unit test bắt được nhưng eval không bắt được: eval chỉ chấm việc model có gọi đúng tên tool và subset tham số hay không, còn unit test (`test_text_stats_bad_input_empty_string_from_model`, `test_text_stats_failure_invalid_wpm_returns_error_dict`) kiểm chứng trực tiếp rằng khi model truyền chuỗi toàn khoảng trắng `"   "`, `wpm=0` hoặc `wpm="invalid_int"`, hàm vẫn xử lý an toàn và trả về error dict có `status == "error"` thay vì văng lỗi làm gián đoạn agent.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `starter_v0/tests/test_tools_todo.py`, `pytest tests/ -v` (`84 passed, 0 failed, 0 skipped`) | Hoàn thiện toàn bộ 14 stubs cho tool có sẵn (`clarify`, `format`, `send`, `lookup`, `fetch`, `timeline`, `social_search`, `policy`) + 3 tests cho `text_stats` | 100% offline với `fake_http` và `monkeypatch`, kiểm tra cả request gửi đi, mapping kết quả, guardrail `send` và trust boundary `policy` |

Test challenge: Đã hoàn thiện toàn bộ 14 stubs trong `starter_v0/tests/test_tools_todo.py` để toàn bộ test suite đạt **84 passed, 0 failed, 0 skipped** (không phát hiện bug cần sửa trong code của các tool có sẵn; tất cả assert hành vi hiện tại đều pass).

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

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`:

- **Nguyễn Tuấn Dũng (`2A202603859`)**: hoàn thành CP3 — tool mới `text_stats` và hoàn thiện toàn bộ `starter_v0/tests/test_tools_todo.py` (84 passed, 0 failed, 0 skipped). Xem chi tiết tại [2A202603859_NguyenTuanDung.md](./2A202603859_NguyenTuanDung.md).

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
