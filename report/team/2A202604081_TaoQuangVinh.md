# Báo cáo cá nhân — Tào Quang Vinh - 2A202604081

## 1. Thông tin thành viên

- Họ tên: Tào Quang Vinh
- MSSV: 2A202604081
- Email: qvinhh2312@gmail.com
- GitHub: https://github.com/qvinhh2312
- Nhóm: MMV (lớp L3B)
- Vai trò: UI Streamlit, deploy Cloudflare Tunnel, Phần A báo cáo nhóm

## 2. Phần việc phụ trách

- Xây UI Streamlit (`app.py`, `ui_core.py`) để team khác dùng thử Research Agent, có chốt xác nhận trước khi chạy tool có tác dụng phụ (gửi Telegram).
- Viết test offline cho UI (`tests/test_ui_core.py`, `tests/test_app_ui.py`).
- Viết script chạy UI kèm Cloudflare Tunnel để tạo link công khai (`scripts/run_ui.ps1`, `scripts/run_ui.sh`).
- Viết Phần A của `report/team/group_report.md` (A1 giới thiệu agent, lệnh chạy UI, link dùng thử; A2 bảng tool; A3 câu hỏi mẫu).
- Làm việc trên nhánh `feat/ui-report`, không sửa các file thuộc phần của A/B (prompt, `tools.yaml`, `tools/`, `chat.py`, `agent.py`, `run_eval.py`, `providers/`, dữ liệu eval).

## 3. Đóng góp cụ thể

**UI và logic lõi**

- `ui_core.py` không import Streamlit nên test được offline. Tái dùng các hàm nhỏ giống `chat.py` (`trim_history`, `execute_tool_call`, `assistant_tool_message`, `tool_results_message`, `write_transcript`) và tự viết vòng lặp tool có thể tạm dừng, vì `run_model_tool_loop` của `chat.py` chạy mọi tool ngay, không có điểm chèn xác nhận.
- Giữ đúng mặc định của `chat.py`: `HISTORY_WINDOW=5`, `MAX_TOOL_ROUNDS=4`, history chỉ lưu cặp (user, câu trả lời cuối).
- Mỗi lần Streamlit chạy lại script, đọc lại `artifacts/system_prompt.md` và `artifacts/tools.yaml`, tính `artifact_version` bằng `build_artifact_version` (cùng hàm hash với `chat.py`), hiển thị ở sidebar. Không dùng cache cho phần này. File thiếu hoặc YAML lỗi thì `st.error` rồi `st.stop()`.
- Hiển thị mỗi lượt: câu trả lời, danh sách tool đã gọi kèm args, kết quả tool trong expander. Lỗi tool và lỗi provider hiện bằng `st.error` ngoài expander, không che.
- Sidebar: chọn provider/model (mặc định từ `UI_PROVIDER`, `UI_MODEL`), nhãn version, nút "Cuộc hội thoại mới", danh sách tool (đánh dấu tool cần xác nhận), 4 câu hỏi mẫu.

**Chốt xác nhận (human-in-the-loop)**

- Tool cần chặn được xác định bằng `side_effect: true` hoặc `requires_confirmation: true` trong `tools/<tên>/TOOL.md`; không hard-code tên `send`.
- Fail-closed: tool khai báo trong `tools.yaml` mà không đọc được `TOOL.md` thì bị chặn, để tool mới của thành viên khác không lọt qua.
- Tool bị chặn không chạy ngay, kể cả khi model tự đặt `confirmed=true`. UI hiện nội dung sẽ gửi (sửa được), nút "Xác nhận gửi" và "Hủy"; chỉ sau khi xác nhận mới chạy tool với `confirmed=True` và nội dung đã sửa. Hủy thì model nhận `cancelled_by_user`.
- Tool đứng sau call đang chờ xác nhận không chạy sớm; gặp `awaiting_user` (clarify) thì dừng như `chat.py`.
- Mỗi event của tool bị chặn có khối `ui_gate` (`intercepted`, `model_confirmed_flag`, `user_decision`, `text_edited_by_user`) làm bằng chứng cho báo cáo nhóm.
- Hàm `redact()` che giá trị biến môi trường có tên chứa KEY/TOKEN/CHAT_ID và các mẫu key phổ biến (sk-, tvly-, AIza, token bot Telegram) trước khi hiển thị, gửi lại model hoặc ghi transcript. Lý do: `tools/_shared.py::err()` trả nguyên văn `str(exc)`, nên lỗi HTTP của `send_telegram` có thể chứa URL kèm token.
- Transcript của UI có cùng schema với `chat.py`, thêm `"source": "streamlit_ui"`, ghi vào `transcripts_ui/` (đã thêm vào `.gitignore`), đường dẫn artifact ghi dạng tương đối.

**Test offline** (provider giả, tool giả, không gọi mạng)

- `tests/test_ui_core.py` (14 test): lượt research thường; clarify dừng rồi history có câu hỏi; send bị chặn dù model đặt `confirmed=true`; xác nhận có sửa nội dung; xác nhận khi model bỏ trống `confirmed`; tool không có tham số `text`; chỉ xác nhận được một lần; hủy; thứ tự nhiều tool call; đọc lại artifact và hash đổi theo nội dung; phát hiện tool cần chặn từ manifest; fail-closed khi thiếu/hỏng manifest; `redact()`; schema transcript.
- `tests/test_app_ui.py` (3 test, dùng `streamlit.testing.v1.AppTest`): nhập câu hỏi thì có câu trả lời; model gọi send thì có nút xác nhận và ô nhập bị khóa; lỗi tool hiện trong chat.
- Kết quả `pytest` toàn suite ghi trong `starter_v0/analysis/pytest_output.txt`: 213 passed, 0 failed (file này do thành viên khác tạo; tôi không dùng nó để nói rằng tôi đã tự chạy lại).

**Deploy**

- `scripts/run_ui.ps1` kiểm tra `.venv` và `cloudflared` có sẵn rồi mở hai terminal (Streamlit và `cloudflared tunnel --url http://localhost:8501`); không in biến môi trường. `scripts/run_ui.sh` tương đương cho bash.

**Báo cáo nhóm Phần A**

- A1 (giới thiệu agent, lệnh chạy UI, dependency `streamlit>=1.40.0`, link dùng thử), A2 (bảng tool), A3 (câu hỏi mẫu), và đồng bộ lại phần tool/demo prompt sau khi nhóm thêm tool mới.

## 4. Bằng chứng

- Commit (tác giả `qvinhh2312`, nhánh `feat/ui-report`):
  - `3bc365b` feat(ui): streamlit chat UI with confirmation gate (`app.py`, `ui_core.py`, 2 file test, `requirements.txt`, `.gitignore`)
  - `7d9bc2b` feat(deploy): add Cloudflare demo launcher (`scripts/run_ui.ps1`, `scripts/run_ui.sh`)
  - `1df1a9e` docs(report): group report part A
  - `9915721` feat(ui): simplify tool event presentation
  - `36c4084` fix(ui): harden confirmation and transcript handling
  - `2c64780` style(ui): separate app tests
  - `3b4d2ae` test(ui): cover confirmation edge cases
  - `de0c21d` fix(ui): handle optional text in confirmed tools
  - `69ed595` feat(ui): abandon pending turn before new conversation
  - `feeea4f` docs(report): update phase A demo prompt and tool scope
- File: `starter_v0/app.py`, `starter_v0/ui_core.py`, `starter_v0/tests/test_ui_core.py`, `starter_v0/tests/test_app_ui.py`, `starter_v0/scripts/run_ui.ps1`, `starter_v0/scripts/run_ui.sh`, `report/team/group_report.md` (mục A, B5a dòng UI).
- Lệnh chạy UI (từ `starter_v0/`): `streamlit run app.py --server.headless true`, mở http://localhost:8501.
- Lệnh chạy test riêng phần UI: `pytest tests/test_ui_core.py tests/test_app_ui.py`.
- AI/công cụ đã dùng: OpenAI Codex để viết code, test và tài liệu theo bản mô tả yêu cầu do tôi soạn. Cách tự kiểm tra: đọc lại diff từng commit, chạy `pytest` (test dùng provider giả và tool giả, không gọi mạng), chạy UI thật và thử tay các câu mẫu (thường, thiếu thông tin, Telegram), kiểm tra `git diff --cached --stat` trước mỗi commit để không đưa file ngoài phạm vi, chỉ `git add` từng đường dẫn, không commit `.env`.

## 5. Tự đánh giá

**Làm được:** UI chạy với artifact đọc trực tiếp từ đĩa, hiển thị rõ tool và lỗi tool, có chốt xác nhận fail-closed cho tool có tác dụng phụ, che bí mật trước khi hiển thị và ghi transcript, và có bộ test offline bao phủ các nhánh chính của chốt này. Chốt xác nhận chỉ là lớp bảo vệ thứ hai; boundary chính nằm ở `system_prompt.md` và `tools.yaml` do thành viên khác viết.

**Hạn chế và việc còn lại (nói thẳng để khi được hỏi không bị lệch với repo):**

- Link `trycloudflare.com` trong A1 đã tắt khi nhóm kiểm tra lại; mỗi lần chạy tunnel URL đổi, nên cần chạy lại `scripts/run_ui.ps1` và cập nhật link trước khi demo.
- `transcripts_ui/` bị `.gitignore` và hiện chưa có file nào, nên chưa có transcript UI chứa `ui_gate` làm bằng chứng; bằng chứng của chốt xác nhận hiện là test `tests/test_ui_core.py`. Transcript live ở B4 là của `chat.py`, do thành viên khác chạy.
- Hai commit cuối `69ed595` (hủy lượt đang chờ khi bấm "Cuộc hội thoại mới", trạng thái `abandoned`) và `feeea4f` có trên `origin/feat/ui-report` nhưng chưa có trong `main`; trên `main`, nút "Cuộc hội thoại mới" vẫn bị khóa khi đang chờ xác nhận. Cần nhờ người gộp nhánh đưa hai commit này vào `main` hoặc thống nhất bỏ.
- `scripts/scan_secrets.ps1` (quét giá trị trong `.env` ở mọi file và lịch sử git) chưa có trong repo, nên chưa có bằng chứng quét secret bằng giá trị thật.
- Chốt xác nhận chỉ chặn trong UI; `chat.py` không có chốt này, và link công khai cho phép người lạ bấm "Xác nhận gửi", vì vậy khi mở link công khai phải để trống token/chat id Telegram và tắt tunnel sau buổi demo.

Qua phần việc này tôi hiểu rõ hơn vì sao không nên gọi thẳng vòng lặp tool có sẵn khi cần chèn bước xác nhận, vì sao phải che bí mật ở lớp UI khi tool trả lỗi nguyên văn, và vì sao mọi nhận xét trong báo cáo phải kèm bằng chứng (commit, test, transcript).