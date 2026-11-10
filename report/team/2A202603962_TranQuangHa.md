# Báo cáo cá nhân — TranQuangHa-2A202603962

## 1. Thông tin thành viên

- Họ tên: Trần Quang Hà
- MSSV: 2A202603962
- Email: 26ai.hatq@vinuni.edu.vn

## 2. Phần việc phụ trách

- Thiết kế, triển khai và tích hợp 2 tool mới (`hf_models`, `hn_search`) vào agent (CP3).
- Viết unit test offline cho các tool mới của nhóm trong `tests/test_tools_todo.py` (`hf_models`, `hn_search`, `github_repos`, `pypi_package`) và chạy kiểm tra với `pytest -v`.
- Kiểm thử thực tế 2 tool mới qua CLI (`chat.py`) và chạy phiên chat live trên Streamlit UI (`app.py`) ở cấu hình `v7` để tạo transcript minh chứng (CP5).

## 3. Đóng góp cụ thể

1. **Xây dựng và tích hợp 2 tool mới (`hf_models` và `hn_search`):**
   - `starter_v0/tools/hf_models/tool.py` (`search_hf_models`) & `TOOL.md`: tìm kiếm model trên Hugging Face Hub API theo từ khóa, pipeline `task`, tiêu chí sắp xếp (`downloads`, `likes`, `lastModified`) và `limit`; kiểm tra hợp lệ đầu vào, chuẩn hóa kết quả `items` và trả về error dict khi lỗi HTTP/timeout.
   - `starter_v0/tools/hn_search/tool.py` (`search_hacker_news`) & `TOOL.md`: tìm kiếm bài viết/thảo luận trên Hacker News qua Algolia API theo `tag`, `sort_by` (`relevance`, `date`) và `limit`; làm sạch HTML markup trong trích đoạn, xử lý fallback link HN và bắt lỗi mạng/JSON an toàn thành error dict.
   - Hoàn thiện tài liệu `TOOL.md`, đăng ký cả 2 tool vào `TOOL_FUNCTIONS` (`starter_v0/tools/__init__.py`) và khai báo schema cùng mô tả routing trong `starter_v0/artifacts/tools.yaml`.

2. **Viết unit test offline cho 4 tool mới (`starter_v0/tests/test_tools_todo.py`):**
   - Bổ sung 12 unit test (3 test/tool cho `hf_models`, `hn_search`, `github_repos`, `pypi_package`) bao phủ: happy path (mock HTTP bằng `fake_http`), input sai/thiếu từ model, và nhánh lỗi HTTP/timeout/sai cấu trúc JSON trả về error dict thay vì raise exception.

3. **Kiểm thử thực tế qua CLI và Streamlit UI:**
   - **Test CLI (`chat.py --provider openrouter --version test-tools`):** Chạy hội thoại trực tiếp trên terminal để kiểm tra 2 tool mới (`hf_models`, `hn_search` + `format`). Lần 1 (`test-tools_openrouter_20261110T185151249949.transcript.json`) chạy trước khi cập nhật prompt tối ưu nên `hf_models` chạy đúng nhưng lượt `hn_search` còn tự gọi thừa `send`; lần 2 (`test-tools_openrouter_20261110T185642896564.transcript.json`) chạy lại sau khi cập nhật `system_prompt.md` và `tools.yaml` từ `main` thì luồng `hn_search` → `format` hoàn tất bình thường.
   - **Test live chat trên Streamlit UI (`ui_v7_openrouter_20261110T232341395795.transcript.json`):** Chạy `app.py` ở phiên bản `v7` qua 6 lượt hội thoại, bao phủ đủ các tình huống: truy vấn thường với tool mới (`hf_models`, `hn_search` + `format`), hỏi bổ sung khi thiếu tên tài khoản Twitter rồi gọi `timeline`, và xin xác nhận `clarify(yes_no)` trước khi `send(confirmed=true)` (xử lý lỗi thiếu cấu hình Telegram có kiểm soát).

## 4. Bằng chứng

- File/commit/PR:
  - Commit `0459b33` (PR `#3`, merge PR `#4` `b8091bd`): `starter_v0/tools/hf_models/tool.py`, `starter_v0/tools/hf_models/TOOL.md`, `starter_v0/tools/hn_search/tool.py`, `starter_v0/tools/hn_search/TOOL.md`, `starter_v0/tools/__init__.py`, `starter_v0/artifacts/tools.yaml`.
  - Commit `13211cb` (PR `#7`, merge `850386a`): `starter_v0/tests/test_tools_todo.py`, `starter_v0/transcripts/test-tools_openrouter_20261110T185151249949.transcript.json`, `starter_v0/transcripts/test-tools_openrouter_20261110T185642896564.transcript.json`.
  - File: `starter_v0/transcripts/ui_v7_openrouter_20261110T232341395795.transcript.json`.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - AI/công cụ đã dùng: Google Antigravity (model Gemini 3.8 flash) để hỏi gợi ý thiết kế 2 tool mới và viết unit test offline.
  - Cách tự kiểm tra kết quả:
    - Chạy `pytest -v` trong `starter_v0/`: đạt `94 passed, 14 skipped` (`0 failed`), trong đó toàn bộ contract test, example test và 12 unit test tool mới đều pass.
    - Kiểm tra trực tiếp từng lượt hội thoại và `tool_events` trong 2 file transcript CLI (`test-tools_*`) và file transcript UI `v7` (`ui_v7_openrouter_20261110T232341395795.transcript.json`).

## 5. Tự đánh giá

- Đã hoàn thành đầy đủ phần việc phụ trách: 2 tool mới (`hf_models`, `hn_search`) pass toàn bộ contract test và chạy ổn định qua API thực tế; 12 unit test offline cho 4 tool mới pass hoàn toàn (`0 failed`); transcript UI `v7` đáp ứng đủ các kịch bản hành vi theo yêu cầu.
