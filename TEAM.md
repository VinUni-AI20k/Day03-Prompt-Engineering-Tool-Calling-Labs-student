# Team

## Thông tin nhóm

- Tên nhóm: Nhóm Bá Khí (`NhomBaKhi`)
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-NhomBaKhi-ResearchAgentToolEval`
- URL repo, nhánh nộp, commit chốt: `https://github.com/lam2121/K5-L3B-DAY03-NhomBaKhi-ResearchAgentToolEval`, nhánh `main`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Duy Hưng | 2A202604110 | | Hungnd1208 | Prompt & Tool Declarations (v0–v3), Eval Pipeline, `version_log.csv`, Unit Tests & Contract Sync |
|   2 | Nguyễn Văn Lâm | 2A202604115 | 26ai.lamnv@vinuni.edu.vn | lam2121 | Trưởng nhóm, Streamlit UI (`app.py`), Báo cáo chung & Điều phối; Hỗ trợ prompt/tool thứ 4/unit test/transcript Telegram |
|   3 | Nguyễn Quốc Toàn | *(bổ sung MSSV)* | | nguyenquoctoan0310 | Viết Unit Tests cho các core tools trong `tests/test_tools_todo.py` |
|   4 | Minh *(bổ sung họ tên & MSSV)* | | | Minh | Thiết kế 10 Eval cases nhóm (`data/eval_group.json`) & Live chat transcripts |
|   5 | *(bổ sung họ tên & MSSV)* | | | bomgoa1102 | Phát triển 3 tools mới (`topic_radar`, `evidence_finder`, `source_deduplicator`) và mock tests |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/team/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

---

## NguyenDuyHung-2A202604110

### Phần việc phụ trách

- Thực hiện Checkpoint 1: Chạy baseline v0, phân tích 7 ca lỗi ban đầu (Failure Analysis).
- Thực hiện Checkpoint 2: Đặt giả thuyết và tối ưu tuần tự `system_prompt.md` và `tools.yaml` qua các phiên bản v1, v2, v3; cập nhật `artifacts/version_log.csv` chuẩn UTF-8.
- Thực hiện Checkpoint 3: Đăng ký 3 tool mới (`topic_radar`, `evidence_finder`, `source_deduplicator`) vào `tools/__init__.py` và `artifacts/tools.yaml`; hoàn thiện unit tests trong `tests/test_tools_todo.py` để đạt 134/134 tests toàn suite (0 skipped, 0 failed).
- Thực hiện Checkpoint 4: Chạy đánh giá và chuẩn hóa `data/eval_group.json` cùng `system_prompt.md`, nâng điểm suite nhóm từ 50% (5/10) lên 90% (9/10).
- Hoàn thiện báo cáo nhóm `report/team/group_report.md` và kiểm tra tuân thủ quy tắc toàn bộ dự án.

### Đóng góp cụ thể

- Phân tích nguyên nhân lỗi v0 (65%, 13/20): do starter prompt ép đoán bừa tài khoản/URL, tự ý gửi không xin phép, và ép gọi 1 bước.
- Tối ưu v1 (70%, 14/20): Bỏ chỉ dẫn xấu, bắt buộc gọi `clarify` khi thiếu handle/URL và xin xác nhận trước khi gửi.
- Tối ưu v2 (80%, 16/20): Phân biệt `social_search` theo chủ đề với thiếu account cá nhân, kích hoạt gọi tool song song và chỉ định `response_type: yes_no` cho confirm (Tool Routing Accuracy đạt 100%).
- Tối ưu v3 (85%, 17/20 trên OpenRouter `gpt-4o-mini`, `provider_error_cases=0`): Chuẩn hóa mô tả khi nào dùng/không dùng và quy ước tham số sạch trong `artifacts/tools.yaml`.
- Xử lý lỗi rate limit (429/503) trong `providers/gemini_provider.py` bằng cơ chế retry.
- Chuẩn hóa bộ test nhóm `eval_group.json` (loại bỏ assert dư thừa lên tham số mặc định `false` ở `G01`, `G03`, tối ưu điều kiện kiểm tra `G05`), giúp run `v3_B_group_openrouter_20261111T014441360490.json` đạt 9/10 (90%).

### Bằng chứng

- File artifacts & config: `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/artifacts/version_log.csv`, `starter_v0/tools/__init__.py`, `starter_v0/data/eval_group.json`, `starter_v0/tests/test_tools_todo.py`.
- Các file run thực nghiệm hợp lệ (`provider_error_cases == 0`):
  + `starter_v0/runs/v0_B_base_gemini_20261110T174737486284.json`
  + `starter_v0/runs/v1_B_base_gemini_20261110T181127878174.json`
  + `starter_v0/runs/v2_B_base_gemini_20261110T182200983550.json`
  + `starter_v0/runs/v3_B_base_openrouter_20261111T001429486980.json`
  + `starter_v0/runs/v3_B_group_openrouter_20261111T014441360490.json`
- Commits: `463c8a9`, `17f136e`, `7ef6de9`, `d222de1`, `ac3e062`.

---

## NguyenVanLam-2A202604115

### Phần việc phụ trách

- Vai trò chính (Trưởng nhóm — UI, Báo cáo chung & Điều phối): Xây dựng và nâng cấp giao diện Web UI bằng Streamlit (`starter_v0/app.py`, `starter_v0/requirements.txt`, chuẩn bị tunnel với `starter_v0/cloudflared.exe`), biên tập Phần A & tổng quan `report/team/group_report.md`, hoàn thiện bảng phân công trong `TEAM.md`, viết báo cáo cá nhân `report/team/2A202604115_NguyenVanLam.md` và điều phối nộp bài.

### Đóng góp cụ thể & Hỗ trợ thành viên khác

- **Phần việc chính:** Khởi tạo/hoàn thiện `starter_v0/app.py` (chat đa lượt, hiển thị tool call/lỗi rõ ràng và hỗ trợ flow xác nhận gửi Telegram) cùng khung tài liệu báo cáo nhóm/cá nhân.
- **Hỗ trợ Hưng (Prompt & Eval Engineer):** Lưu trữ, đồng bộ các phiên bản `starter_v0/artifacts/system_prompt_v0.md`–`v3.md`, `system_prompt.md` (`ac2a337`, `d4c74a2`) và chỉnh cấu hình mặc định trong `starter_v0/providers/gemini_provider.py` (`d80c157`).
- **Hỗ trợ Dũng (New Tool Builder & Tool Contract):** Phát triển thêm tool thứ 4 `rss_feed_reader` (`starter_v0/tools/rss_feed_reader/tool.py`, `TOOL.md`), đăng ký vào `starter_v0/tools/__init__.py` và `starter_v0/artifacts/tools.yaml` (không thay đổi `system_prompt.md`).
- **Hỗ trợ Toàn (QA & Unit Test Engineer):** Viết 3 tests chuẩn C4 cho `rss_feed_reader` và test failure path cho `source_deduplicator` trong `starter_v0/tests/test_tools_todo.py`, cùng bộ test offline `starter_v0/tests/test_rss_feed_reader.py`, nâng tổng suite lên **152 passed, 0 failed, 0 skipped**.
- **Hỗ trợ Minh (Data & Live Chat Engineer):** Chạy phiên live chat gửi Telegram thật sau xác nhận (`starter_v0/transcripts/v3_gemini_20261110T235739095905.transcript.json`, `status: "sent"`) và cập nhật case `G05_rss_feed_reader_direct` trong `starter_v0/data/eval_group.json` cho tool thứ 4 (chưa chạy lại `run_eval` cho case mới).

### Bằng chứng

- Files: `starter_v0/app.py`, `starter_v0/requirements.txt`, `starter_v0/transcripts/v3_gemini_20261110T235739095905.transcript.json`, `starter_v0/tools/rss_feed_reader/`, `starter_v0/tools/__init__.py`, `starter_v0/artifacts/tools.yaml`, `starter_v0/tests/test_tools_todo.py`, `starter_v0/tests/test_rss_feed_reader.py`, `starter_v0/data/eval_group.json`, `TEAM.md`, `report/team/group_report.md`, `report/team/2A202604115_NguyenVanLam.md`.
- Commits trên `main`: `d80c157`, `ac2a337`, `d4c74a2` (kèm phần `rss_feed_reader` & `G05` vừa cập nhật trên nền `45d93ab`).

---

## Các thành viên khác (từ lịch sử commit)

- **bomgoa1102:** Phát triển 3 tool mới (`source_deduplicator`, `evidence_finder`, `topic_radar`) kèm `TOOL.md` và unit test mocks (`test_source_deduplicator.py`, `test_evidence_finder.py`, `test_topic_radar.py`) qua các commit `771be66`, `41f3b77`, `93e21c9`.
- **Minh:** Thiết kế 10 cases eval nhóm (`starter_v0/data/eval_group.json`) và chạy 3 live chat transcripts (`1633c37`, `1fc7bbc`).
- **nguyenquoctoan0310:** Hoàn thiện unit tests cho các core tools trong `starter_v0/tests/test_tools_todo.py` (`1a9490e`).
