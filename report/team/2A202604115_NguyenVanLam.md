# Báo cáo cá nhân — Nguyễn Văn Lâm (2A202604115)

## 1. Thông tin thành viên

- Họ tên: Nguyễn Văn Lâm
- MSSV: `2A202604115`
- Email: `26ai.lamnv@vinuni.edu.vn`
- GitHub: `lam2121`
- Vai trò chính (Trưởng nhóm): UI & Demo Lead (`starter_v0/app.py`, Cloudflare Tunnel), phụ trách tổng hợp Báo cáo chung (`report/team/group_report.md`), `TEAM.md`, báo cáo cá nhân và điều phối nộp bài.

## 2. Phần việc phụ trách

### 2.1. Công việc chính theo phân công nhóm
- Khởi tạo và nâng cấp giao diện Web UI bằng Streamlit (`starter_v0/app.py`, `starter_v0/requirements.txt`) để chat trực tiếp với Research Agent, hiển thị quá trình gọi tool/lỗi rõ ràng và hỗ trợ luồng xác nhận gửi Telegram.
- Chuẩn bị binary `starter_v0/cloudflared.exe` phục vụ mở Cloudflare Tunnel demo UI khi trình diễn.
- Khởi tạo và hoàn thiện phần cá nhân trong `TEAM.md`, `report/team/group_report.md` và báo cáo cá nhân `report/team/2A202604115_NguyenVanLam.md`; theo dõi, rà soát tiến độ chung và điều phối nộp bài của nhóm.

### 2.2. Phần hỗ trợ các thành viên khác
- **Hỗ trợ Hưng (Prompt & Eval Engineer):** Lưu trữ, đồng bộ lịch sử các phiên bản prompt (`starter_v0/artifacts/system_prompt_v0.md` → `v3.md`) vào `starter_v0/artifacts/system_prompt.md` và cấu hình model mặc định trong `starter_v0/providers/gemini_provider.py`.
- **Hỗ trợ Dũng (New Tool Builder & Tool Contract):** Phát triển thêm tool thứ 4 `rss_feed_reader` (`starter_v0/tools/rss_feed_reader/tool.py`, `TOOL.md`), đăng ký vào `starter_v0/tools/__init__.py` và khai báo schema vào `starter_v0/artifacts/tools.yaml` (không làm thay đổi `starter_v0/artifacts/system_prompt.md`) để hướng tới tiêu chí Bonus ≥ 4 tool mới.
- **Hỗ trợ Toàn (QA & Unit Test Engineer):** Viết bổ sung bộ 3 unit tests theo chuẩn C4 cho `rss_feed_reader` và test failure path cho `source_deduplicator` trong `starter_v0/tests/test_tools_todo.py`, cùng bộ test offline mở rộng trong `starter_v0/tests/test_rss_feed_reader.py`.
- **Hỗ trợ Minh (Data & Live Chat Engineer):** Chạy phiên live chat sinh transcript gửi Telegram thực tế sau xác nhận người dùng (`starter_v0/transcripts/v3_gemini_20261110T235739095905.transcript.json`) và cập nhật case `G05_rss_feed_reader_direct` vào `starter_v0/data/eval_group.json` (giữ đúng 10 cases: 5 single-turn + 5 multi-turn) cho tool thứ 4.

## 3. Đóng góp cụ thể

- **Xây dựng Streamlit UI (`starter_v0/app.py`, `starter_v0/requirements.txt`):**
  - Thiết kế giao diện hội thoại đa lượt kết nối trực tiếp `ResearchAgent` và `TOOL_FUNCTIONS`.
  - Hỗ trợ kiểm soát hành vi xác nhận `yes_no` trước khi gửi bản tin ra Telegram và hiển thị rõ các tool call / lỗi tool thay vì che lỗi.
- **Hỗ trợ luồng Live Chat & Gửi Telegram thật (`d4c74a2`):**
  - Thực hiện phiên chat đa lượt lưu tại `starter_v0/transcripts/v3_gemini_20261110T235739095905.transcript.json` (Turn 3–4 cho thấy agent gọi `clarify(response_type="yes_no")` hỏi xác nhận, sau khi user xác nhận mới gọi `send(confirmed=true)` và trả về `status: "sent"`).
- **Hỗ trợ đồng bộ Prompt & Provider (`d80c157`, `ac2a337`, `d4c74a2`):**
  - Lưu lại lịch sử `system_prompt_v0.md` đến `system_prompt_v3.md` phục vụ đối chiếu quá trình tối ưu của nhóm, đồng thời giữ nguyên `system_prompt.md` ở trạng thái chuẩn sau `ac3e062` / `45d93ab`.
- **Hỗ trợ Tool thứ 4 `rss_feed_reader` + Unit Tests + Eval Case (`G05`):**
  - Xây dựng `read_rss_feed(url, max_items, keyword)` đọc RSS 2.0 / RSS 1.0 (RDF) và Atom XML feed với kiểm tra URL an toàn (chặn `localhost`, `.local`, `.internal`, userinfo, IP private/loopback và redirect nội bộ), chặn `<!DOCTYPE` / `<!ENTITY`, làm sạch HTML description và luôn trả dict lỗi chuẩn qua `err("rss_feed_reader", exc)`.
  - Hoàn thiện 3 tests chuẩn C4 cho `rss_feed_reader` và test failure path cho `source_deduplicator` trong `tests/test_tools_todo.py`, cùng 9 ca test offline (`fake_http`) trong `tests/test_rss_feed_reader.py`, nâng tổng suite lên **152 passed, 0 failed, 0 skipped**.
  - Thay `G05_lookup_general_documentation` bằng `G05_rss_feed_reader_direct` trong `starter_v0/data/eval_group.json` (giữ đúng 5 single-turn + 5 multi-turn) để kiểm tra routing vào tool thứ 4.

## 4. Bằng chứng

- **File/commit/PR:**
  - Commits đã ghi nhận trên `main`:
    + `d80c157`: Khởi tạo Streamlit UI (`starter_v0/app.py`), `requirements.txt`, chỉnh mặc định `providers/gemini_provider.py`, khung `TEAM.md` và `report/team/`.
    + `ac2a337`: Nâng cấp `starter_v0/app.py`, đồng bộ `system_prompt.md` và lưu `system_prompt_v1.md`–`v3.md`.
    + `d4c74a2`: Lưu `system_prompt_v0.md` và transcript gửi Telegram thực tế `starter_v0/transcripts/v3_gemini_20261110T235739095905.transcript.json`.
  - Files phần việc chính & hỗ trợ hiện có trong workspace (bao gồm phần `rss_feed_reader` vừa thêm trên `45d93ab`, chưa commit):
    + `starter_v0/app.py`, `starter_v0/requirements.txt`
    + `starter_v0/tools/rss_feed_reader/tool.py`, `starter_v0/tools/rss_feed_reader/TOOL.md`
    + `starter_v0/tools/__init__.py`, `starter_v0/artifacts/tools.yaml`
    + `starter_v0/tests/test_tools_todo.py`, `starter_v0/tests/test_rss_feed_reader.py`
    + `starter_v0/data/eval_group.json`
    + `TEAM.md`, `report/team/group_report.md`, `report/team/2A202604115_NguyenVanLam.md`
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Sử dụng trợ lý AI (Antigravity) hỗ trợ thiết kế mã nguồn Streamlit UI, parser XML + SSRF guard cho `rss_feed_reader`, chuẩn hóa test offline và biên tập tài liệu báo cáo.
  - Cách tự kiểm tra kết quả:
    + Chạy `.\venv\Scripts\python.exe -m pytest tests/ -v`: đạt **152 passed in 0.86s** (`0 failed, 0 skipped`), mọi contract test trong `test_tool_contract.py` đều pass và không có kết nối mạng thật (`block_network`).
    + Kiểm tra cấu trúc `starter_v0/data/eval_group.json` bằng `load_cases` + `validate_expected_tools` trong `run_eval.py`: hợp lệ **10 cases** (`single=5, multi=5`).
    + Kiểm tra `git diff starter_v0/artifacts/system_prompt.md`: trống (đảm bảo thêm tool thứ 4 không ảnh hưởng đến system prompt đã chốt).
    + Kiểm chứng luồng live chat & Telegram thật qua log JSON `starter_v0/transcripts/v3_gemini_20261110T235739095905.transcript.json` (`status: "sent"`).

## 5. Tự đánh giá

- **Điểm làm tốt:** Hoàn thành đầy đủ giao diện UI Streamlit, chứng minh được luồng live chat có xác nhận trước khi gửi Telegram thật, hoàn thiện tài liệu phân công/báo cáo theo đúng vai trò Trưởng nhóm và kịp thời hỗ trợ các thành viên khác hoàn thiện tool thứ 4 `rss_feed_reader` cùng unit tests offline (0 skipped, 0 failed) mà không làm biến đổi `system_prompt.md`.
- **Hạn chế / Việc cần lưu ý:** Sau khi thay case `G05_rss_feed_reader_direct` vào `eval_group.json` để phục vụ tool thứ 4, chưa chạy lại `run_eval` với model provider nên kết quả chạy group eval mới chưa được cập nhật vào bảng B3/B5 trong `group_report.md` (các bảng phần B hiện vẫn phản ánh đúng run đã chạy trước đó).
