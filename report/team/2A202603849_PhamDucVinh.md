# Báo cáo cá nhân — Phạm Đức Vinh - 2A202603849

## 1. Thông tin thành viên

- Họ tên: Phạm Đức Vinh
- MSSV: 2A202603849
- Email:  26ai.vinhpd@vinuni.edu.vn

## 2. Phần việc phụ trách

**CP3 — Tool mới và unit test:** thiết kế, viết, đăng ký và kiểm thử tool `wiki` (tóm tắt bài Wikipedia).

## 3. Đóng góp cụ thể

### 3.1. Tool `wiki`

- **Mục đích:** trả lời câu hỏi định nghĩa / kiến thức nền ổn định ("X là gì", "giới thiệu về Y"). Trước đó agent chỉ có `lookup` (search web, tốn credit Tavily, kết quả là danh sách link) cho loại câu hỏi này.
- **API:** `GET https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}` — không cần API key, không side effect.
- **Signature:** `wiki_summary(title: str = "", lang: str = "vi")`.
- **Output:** `title`, `lang`, `found`, `is_disambiguation`, `description`, `summary`, `url`.

Quyết định thiết kế:

| Tình huống | Hành vi | Lý do |
| --- | --- | --- |
| `title` rỗng / `None` | error dict `ValueError`, không gọi mạng | Model có thể gửi arg rỗng; không tốn request vô ích |
| `lang` không phải 2–3 chữ cái (vd `evil.com/x`) | error dict `ValueError`, không gọi mạng | `lang` nằm trong hostname — nhận bừa thì model/prompt injection có thể đổi đích request |
| HTTP 404 | `found: false`, **không** phải lỗi | "Không có bài" là kết quả hợp lệ; tools.yaml hướng dẫn agent thử lại với `lang=en` |
| Trang định hướng | `is_disambiguation: true` | tools.yaml hướng dẫn agent `clarify` hỏi user muốn nghĩa nào |
| HTTP 5xx / timeout | error dict, không raise | Theo contract chung của các tool (`tools._shared.err`) |
| Request | gửi kèm `User-Agent` | Wikipedia REST API yêu cầu User-Agent |

### 3.2. Đăng ký tool (đồng bộ 3 nơi)

- `starter_v0/tools/wiki/tool.py` + `starter_v0/tools/wiki/TOOL.md` (frontmatter đúng contract trong `tools/README.md`: `kind: live_api`, `requires_env: []`, `side_effect: false`).
- `starter_v0/tools/__init__.py`: thêm `"wiki": wiki_summary` vào `TOOL_FUNCTIONS`.
- `starter_v0/artifacts/tools.yaml`: description ghi rõ **khi nào dùng** (định nghĩa, khái niệm, tiểu sử) và **khi nào không dùng** (tin tức mới → `lookup` + `topic=news`; URL cụ thể → `fetch`; mạng xã hội); mô tả convention args (`title` là tên bài, không phải câu hỏi; `lang=en` cho thuật ngữ kỹ thuật tiếng Anh).

### 3.3. Unit test (`starter_v0/tests/test_tools_todo.py`)

5 test, chạy offline với fixture `fake_http`, assert cả request gửi đi lẫn kết quả trả về:

| Test | Loại | Kiểm tra |
| --- | --- | --- |
| `test_wiki_builds_request_url_and_maps_summary` | happy path | URL đúng (khoảng trắng → `_`), method GET, có `User-Agent`, map đúng `summary`/`url`/`found` |
| `test_wiki_rejects_empty_title_without_calling_network` | input xấu từ model | `title="   "` và `title=None` → `ValueError`, 0 request |
| `test_wiki_rejects_lang_that_would_change_hostname` | input xấu / bảo mật | `lang="evil.com/x"` → `ValueError`, 0 request |
| `test_wiki_404_means_not_found_not_error` | nhánh biên | 404 → `found: false`, không có key `error` |
| `test_wiki_http_error_returns_error_dict` | nhánh lỗi | 503 → `error: HTTPError`, không raise |

## 4. Bằng chứng

- File:
  - `starter_v0/tools/wiki/tool.py`, `starter_v0/tools/wiki/TOOL.md`
  - `starter_v0/tools/__init__.py`, `starter_v0/artifacts/tools.yaml`
  - `starter_v0/tests/test_tools_todo.py` (mục "YOUR NEW TOOL(S)")
- Kết quả `pytest` (chạy bằng `.venv/Scripts/python -m pytest -q` trong `starter_v0/`):

  ```text
  72 passed, 14 skipped in 0.57s
  ```

  0 failed. 5 test của `wiki` đều chạy (không skip); contract test (`tests/test_tool_contract.py`) xanh với `wiki`. 14 skipped là stub của tool có sẵn, được phép còn skip.
- Smoke test với API thật: `wiki_summary(title="Trí tuệ nhân tạo")` → `found: True`, trả về summary và URL `https://vi.wikipedia.org/wiki/Tr%C3%AD_tu%E1%BB%87_nh%C3%A2n_t%E1%BA%A1o`.
- Commit: (cập nhật hash sau khi commit)
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: dùng Claude Code để đọc contract tool (`tools/README.md`, `tests/conftest.py`, `tests/test_tools_examples.py`) và sinh code/test theo pattern có sẵn. Tự kiểm tra bằng: chạy toàn bộ `pytest` (0 failed), contract test cho `wiki`, và gọi thử API Wikipedia thật để xác nhận format response khớp với mapping trong code.

## 5. Tự đánh giá

- Đã hoàn thành yêu cầu CP3: 1 tool mới có `TOOL.md`, đăng ký đủ `TOOL_FUNCTIONS` + `tools.yaml`, ≥ 3 test (5 test), `pytest` 0 failed.
- Lưu ý: thêm `wiki` vào `tools.yaml` làm `tools_hash` khác bản v3 trong `version_log.csv`; run eval sau đó cần ghi thành version mới.
- Việc tiếp theo: thêm eval case trong `data/eval_group.json` kiểm tra agent route tới `wiki` đúng lúc (CP4), và điền bảng B5a trong `group_report.md`.
