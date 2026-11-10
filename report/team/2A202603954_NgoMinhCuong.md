# Báo cáo cá nhân — NgoMinhCuong-2A202603954

## 1. Thông tin thành viên

- Họ tên: Ngô Minh Cương
- MSSV: `2A202603954`
- Email: `26ai.cuongnm5@vinuni.edu.vn`
- GitHub: `ngominhcuong`
- Nhóm / Lớp: `3npc`

## 2. Phần việc phụ trách

- Thiết kế và cài đặt 2 custom tools mới cho Research Agent (`github_repos` và `pypi_package`), bao gồm code thực thi, tài liệu `TOOL.md`, đăng ký registry (`tools/__init__.py`) và khai báo schema/routing trong `artifacts/tools.yaml` (CP3 + đóng góp vào mục bonus ≥ 4 tool mới).
- Xây dựng giao diện web tương tác bằng Streamlit (`starter_v0/app.py`), cập nhật `starter_v0/requirements.txt`, mở link dùng thử công khai qua Cloudflare Tunnel và tạo mã QR demo (CP5).
- Cấu hình và kiểm thử luồng gửi thông báo thật lên private Telegram channel qua tool `send` có bước xác nhận `clarify(response_type="yes_no")` (CP5 + bonus Telegram).
- Review và merge các Pull Request của nhóm trên GitHub (`#1`, `#3`, `#4`, `#5`, `#7`).

## 3. Đóng góp cụ thể

1. **Xây dựng 2 tool mới (`github_repos` và `pypi_package`):**
   - `starter_v0/tools/github_repos/tool.py` ([`search_github_repos`](../../starter_v0/tools/github_repos/tool.py)): tìm kiếm repository trên GitHub Search API (`https://api.github.com/search/repositories`) theo từ khóa `query`, `language`, `min_stars`, `timeframe` (`all`/`day`/`week`/`month`/`year`) và `sort_by` (`stars`/`hot`/`updated`/`forks`); tự tính chỉ số `stars_per_day`, tự mặc định lọc 7 ngày gần nhất khi `sort_by="hot"`, ép kiểu an toàn cho tham số từ model và trả error dict qua `err()` khi lỗi HTTP.
   - `starter_v0/tools/pypi_package/tool.py` ([`get_pypi_package`](../../starter_v0/tools/pypi_package/tool.py)): tra cứu metadata package Python qua PyPI JSON API (`https://pypi.org/pypi/<package_name>/json`) gồm `version`, `license`, `requires_python`, `latest_release_date`, `project_urls` và tùy chọn `include_releases` (tối đa 5 phiên bản gần nhất); kiểm tra tên package hợp lệ bằng regex (chặn rỗng và path traversal) và trả error dict thay vì raise.
   - Viết `TOOL.md` đúng chuẩn frontmatter cho cả 2 tool, đăng ký vào `TOOL_FUNCTIONS` trong `starter_v0/tools/__init__.py` và viết mô tả `DÙNG KHI` / `KHÔNG DÙNG KHI` + convention tham số trong `starter_v0/artifacts/tools.yaml`.

2. **Xây dựng Streamlit UI & triển khai demo (`starter_v0/app.py`):**
   - Tái sử dụng vòng lặp hội thoại nhiều lượt `run_model_tool_loop`, `trim_history`, `write_transcript` từ `starter_v0/chat.py` và `build_artifact_version` từ `starter_v0/versioning.py`.
   - Hiển thị minh bạch toàn bộ tool calls, arguments JSON, kết quả trả về và cảnh báo lỗi tool/provider (không che lỗi) trong expander `_render_tool_trace`.
   - Bổ sung nút trả lời nhanh khi agent gọi `clarify` (`yes_no` / `choice`), sidebar chọn provider/model/version, kiểm tra trạng thái biến môi trường (không lộ secret), 6 câu hỏi mẫu test nhanh và nút tải/lưu transcript JSON vào `starter_v0/transcripts/`.
   - Thêm `streamlit>=1.35.0` vào `starter_v0/requirements.txt`, mở public link tạm thời qua `cloudflared tunnel --url http://localhost:8501` để team khác dùng thử.

3. **Kiểm thử live chat & luồng xác nhận gửi Telegram:**
   - Kiểm thử routing cho tool mới và tool cũ qua `chat.py` (OpenRouter) và UI `app.py`.
   - Cấu hình Telegram Bot (`@lab3RSbot`) và private channel của nhóm (`LabRSBot`), chạy luồng thực tế: yêu cầu tìm tin/tweet và gửi Telegram → agent gọi `clarify(response_type="yes_no")` → người dùng xác nhận → agent gọi `send(confirmed=true)` → trả về `status: "sent"`.

## 4. Bằng chứng

- **Commits & Pull Requests:**
  - `32595e1` (PR `#1`, nhánh `tools_ngominhcuong` → merge commit `907767c`): `feat: add github_repos and pypi_package custom tools with yaml definitions and implementations`
    - `starter_v0/tools/github_repos/tool.py`, `starter_v0/tools/github_repos/TOOL.md`
    - `starter_v0/tools/pypi_package/tool.py`, `starter_v0/tools/pypi_package/TOOL.md`
    - `starter_v0/tools/__init__.py`, `starter_v0/artifacts/tools.yaml`
  - `7f4beee` (PR `#5`, nhánh `ui_chat` → merge commit `9789f77`): `feat: add Streamlit UI and starter code for research agent tool calling lab`
    - `starter_v0/app.py`, `starter_v0/requirements.txt`
  - Merge các PR tích hợp bài nhóm: `25cd6fe` (PR `#3`), `b8091bd` (PR `#4`), `850386a` (PR `#7`).
- **Transcripts & Demo:**
  - `starter_v0/transcripts/test-tools_openrouter_20261110T181217445649.transcript.json` (4 lượt test live qua `chat.py`: `github_repos`, `pypi_package`, `lookup`, `timeline`).
  - `starter_v0/transcripts/ui_v6_openrouter_20261110T185326916931.transcript.json` (test giao diện Streamlit).
  - `starter_v0/transcripts/ui_v6_openrouter_20261110T193010078007.transcript.json` (3 turns) & `starter_v0/transcripts/ui_v6_openrouter_20261110T193709655529.transcript.json` (5 turns): chứng minh luồng hỏi xác nhận `clarify(yes_no)` → `send(confirmed=true)` → `"status": "sent"` lên Telegram.
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - **Công cụ AI đã dùng:** Trợ lý lập trình AI (Google Antigravity / Gemini) để gợi ý thiết kế 2 custom tools (`github_repos`, `pypi_package`), dựng giao diện Streamlit `app.py`.
  - **Cách tự kiểm tra kết quả:**
    1. Chạy `pytest -q` trong `starter_v0/`: **94 passed, 14 skipped, 0 failed** (mọi contract test giữa `tools.yaml` ↔ `TOOL_FUNCTIONS` ↔ `TOOL.md` và các unit test tool mới của nhóm đều pass).
    2. Smoke test trực tiếp qua `TOOL_FUNCTIONS` gọi API thật cho `github_repos`, `pypi_package` (happy path + input lỗi + 404) và `send` (`confirmed=False` trả `needs_confirmation`, `confirmed=True` gửi thật trả `sent`).
    3. Smoke test UI bằng `streamlit.testing.v1.AppTest` (`AppTest OK!`) và chạy live `streamlit run app.py` + `cloudflared tunnel --url http://localhost:8501` để kiểm tra từng tool call và log JSON trong `transcripts/`.

## 5. Tự đánh giá

- Hoàn thành đầy đủ các đầu việc được giao: 2 custom tools chạy thật và pass contract/unit test, giao diện Streamlit minh bạch tool trace + lỗi, mở link tunnel cho người khác dùng thử, và có transcript chứng minh luồng xác nhận gửi Telegram thật.
- Điểm cần lưu ý: link `trycloudflare.com` mang tính tạm thời theo phiên chạy máy cá nhân; nếu chấm bài sau buổi học nên deploy cố định lên Streamlit Community Cloud hoặc chạy lại theo hướng dẫn trong `report/team/group_report.md`. Ngoài ra có thể bổ sung thêm case vào `eval_group.json` để đo các tình huống từ khóa mơ hồ giữa `github_repos` và `pypi_package`.

