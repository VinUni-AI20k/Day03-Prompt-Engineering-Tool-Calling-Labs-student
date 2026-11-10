# Báo cáo cá nhân — NguyenTuanDung-2A202603859

## 1. Thông tin thành viên

- Họ tên: Nguyễn Tuấn Dũng
- MSSV: 2A202603859
- Email: 26ai.dungnt16@vinuni.edu.vn
- GitHub: DungNguyen74

## 2. Phần việc phụ trách

- **Checkpoint 3 (CP3) — Tool mới và Unit Test**:
  - Thiết kế và hiện thực tool mới `text_stats` (tính số từ, số ký tự và ước tính thời gian đọc cho một đoạn văn bản hoặc bản nháp).
  - Soạn đặc tả tool tại `starter_v0/tools/text_stats/Tool.md`.
  - Đăng ký tool vào `TOOL_FUNCTIONS` trong `starter_v0/tools/__init__.py` và khai báo schema trong `starter_v0/artifacts/tools.yaml`.
  - Viết bộ unit test cho tool mới `text_stats` và hoàn thiện toàn bộ các stub test trong `starter_v0/tests/test_tools_todo.py` để toàn bộ test suite đạt **0 failed, 0 skipped** (Test Challenge).

## 3. Đóng góp cụ thể

1. **Thiết kế và cài đặt tool mới `text_stats` (`starter_v0/tools/text_stats/tool.py` & `Tool.md`)**:
   - Xây dựng hàm `text_stats(text: str, wpm: int = 200) -> Dict[str, Any]` trả về dict có cấu trúc thống nhất:
     - **Kiểm tra input xấu (`text`)**: nếu `text` không phải `str` hoặc chỉ chứa khoảng trắng (`not text.strip()`), trả về error dict (`status: "error"`, `error: "Parameter 'text' must be a non-empty string."`, `items: []`) thay vì `raise` exception.
     - **Kiểm tra và chuẩn hóa tham số `wpm`**: hỗ trợ ép kiểu `int(wpm)` (xử lý được trường hợp model truyền chuỗi số), bắt `ValueError`/`TypeError` khi giá trị không hợp lệ và kiểm tra `wpm_val <= 0`, đều trả về error dict rõ ràng.
     - **Happy path**: chuẩn hóa `text.strip()`, tính `word_count` (theo `split()`), `char_count` (`len(cleaned_text)`), `estimated_reading_seconds` (`round((word_count / wpm_val) * 60, 1)`), trả về `status: "ok"` cùng `items` chứa bản ghi thống kê (`title`, `word_count`, `char_count`, `wpm`, `estimated_reading_seconds`, `snippet`).
   - Tạo tài liệu `starter_v0/tools/text_stats/Tool.md` với frontmatter (`name: text_stats`, `description`, `category: analysis`, `requires_env: []`) và hướng dẫn mục đích, trường hợp sử dụng (`When to use`), cùng mô tả tham số (`Arguments`).

2. **Tích hợp registry và tool declaration**:
   - Import `text_stats` từ `.text_stats.tool` và đăng ký khóa `"text_stats": text_stats` vào `TOOL_FUNCTIONS` trong `starter_v0/tools/__init__.py`.
   - Khai báo schema `text_stats` trong `starter_v0/artifacts/tools.yaml`, nêu rõ khi nào dùng (`USE WHEN`), khi nào không dùng (`DO NOT USE WHEN`), và chi tiết kiểu/ràng buộc của `text` (required) và `wpm` (tùy chọn, mặc định 200, > 0).
   - Toàn bộ contract tests trong `starter_v0/tests/test_tool_contract.py` đều pass (60/60).

3. **Hoàn thiện Unit Test trong `starter_v0/tests/test_tools_todo.py`**:
   - Viết **3 unit tests cho tool mới `text_stats`**:
     - `test_text_stats_happy_path_returns_counts`: kiểm chứng kết quả với `wpm=120` (6 từ, 37 ký tự, 3.0 giây đọc, `status == "ok"`).
     - `test_text_stats_bad_input_empty_string_from_model`: kiểm chứng input chuỗi khoảng trắng `"   "` trả về error dict (`status == "error"`, `items == []`).
     - `test_text_stats_failure_invalid_wpm_returns_error_dict`: kiểm chứng `wpm=0` và `wpm="invalid_int"` trả về error dict, không crash agent.
   - Hoàn thiện toàn bộ **14 test stubs cho các tool có sẵn** (chạy 100% offline bằng `fake_http` và `monkeypatch`):
     - `clarify` (1 test): `test_clarify_choice_returns_options_and_awaits_user`.
     - `format` (3 tests): `test_format_sections_groups_items_by_section`, `test_format_thread_numbers_items`, `test_format_empty_items_does_not_crash`.
     - `send` (2 tests): `test_send_confirmed_posts_to_telegram`, `test_send_confirmed_without_env_returns_error_and_no_request`.
     - `lookup` (1 test): `test_lookup_without_timeframe_omits_time_range`.
     - `fetch` (2 tests): `test_fetch_maps_firecrawl_response`, `test_fetch_truncates_markdown_to_4000_chars`.
     - `timeline` & `social_search` (2 tests): `test_timeline_respects_limit_and_skips_items_without_id`, `test_social_search_passes_search_type`.
     - `policy` (3 tests): `test_policy_empty_query_returns_no_results`, `test_policy_area_filter_only_returns_that_area`, `test_policy_instruction_like_lines_go_to_untrusted_text`.

## 4. Bằng chứng

- **File/commit/PR**:
  - Commit: `0b0adce` (`Update tool`, nhánh `Dungv2`)
  - Các file đã tạo/chỉnh sửa:
    - `starter_v0/tools/text_stats/tool.py`
    - `starter_v0/tools/text_stats/Tool.md`
    - `starter_v0/tools/__init__.py`
    - `starter_v0/artifacts/tools.yaml`
    - `starter_v0/tests/test_tools_todo.py`
  - Kết quả chạy kiểm thử `cd starter_v0; .\venv\Scripts\python.exe -m pytest tests/ -v`: **84 passed in 0.96s** (0 failed, 0 skipped), gồm 60 contract tests (`test_tool_contract.py`), 7 example tests (`test_tools_examples.py`), và 17 TODO/tool tests (`test_tools_todo.py`).
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả**:
  - Dùng `pytest tests/ -v` chạy offline (mạng bị chặn bởi fixture `block_network` trong `conftest.py`, HTTP được giả lập qua `fake_http` và biến môi trường qua `monkeypatch`).
  - Đối chiếu chữ ký hàm `text_stats(text, wpm=200)` trong `tool.py` với khai báo trong `artifacts/tools.yaml` thông qua `test_tool_contract.py`.

## 5. Tự đánh giá

- Hoàn thành đầy đủ yêu cầu của Checkpoint 3 (tạo tool mới `text_stats`, đăng ký, viết đặc tả và ≥ 3 unit tests theo 3 nhóm happy path / input xấu / nhánh lỗi).
- Hoàn thành phần Test Challenge trong `tests/test_tools_todo.py` khi đưa toàn bộ test suite về **84 passed, 0 failed, 0 skipped**.
- Lưu ý nhỏ cần kiểm tra trước khi ghép bài: file đặc tả hiện đang đặt tên `Tool.md` (chữ thường), nên đổi thành `TOOL.md` (in hoa) để đảm bảo `test_tool_folder_has_tool_md_with_matching_name` hoạt động đồng nhất trên cả hệ điều hành phân biệt hoa/thường như Linux.
