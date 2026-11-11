# Báo cáo cá nhân — Trịnh Tuấn Phong (2A202603781)

## 1. Thông tin thành viên

- Họ tên: Trịnh Tuấn Phong
- MSSV: 2A202603781
- Email:  26ai.phongtt2@vinuni.edu.vn

## 2. Phần việc phụ trách

- CP1: chạy baseline v0 và phân tích 5 case FAIL (R08, R10, R11, R12, R13).
- CP2: `artifacts/system_prompt.md` v1–v3 và `artifacts/tools.yaml` v3 (12 tool, convention args, boundary `send`).
- CP3: 2 tool mới `wiki` + `hackernews` (tool.py, TOOL.md, đăng ký `TOOL_FUNCTIONS`, khai báo `tools.yaml`, 7 unit test offline).
- CP4: 6 case eval nhóm (3 single + 3 multi), 5 case route tới 2 tool mới.
- CP5: UI Streamlit `app.py`, live chat 4 lượt phủ 3 kịch bản.

## 3. Đóng góp cụ thể

- Vòng lặp evidence-driven: v0 0.75 → v1 0.90 (bỏ chỉ dẫn đoán + rule `clarify`) → v2 1.00 (Scope + Sending boundary) → v3 1.00 (viết lại description 12 tool + nhắc `clarify` luôn đặt `response_type`).
- Bảng B2 (failure analysis v0, 5 case R08/R10/R11/R12/R13) — đã điền trong `report/team/group_report.md` mục B2.
- 2 tool mới chạy offline/không cần API key, validate input trước khi gọi mạng, mọi lỗi trả error dict thay vì raise.
- `pytest -q -rs`: **93 passed, 0 skipped, 0 failed** trong 0.46s.

## 4. Bằng chứng

- File:
  - `starter_v0/runs/v0_B_base_openrouter_20261110T172631463565.json` … `v3_B_base_openrouter_20261110T183447099371.json`, `v3_B_group_openrouter_20261110T192049745700.json`
  - `starter_v0/transcripts/v3_openrouter_20261110T232722798444.transcript.json` (4 lượt: tin tức → hỏi lại account → `timeline(screenname="sama")` → `clarify(response_type="yes_no")`)
  - `starter_v0/tools/wiki/`, `starter_v0/tools/hackernews/`, `starter_v0/tools/__init__.py`
  - `starter_v0/tests/test_tools_todo.py` (21 test, trong đó 7 test cho 2 tool mới)
  - `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/artifacts/version_log.csv`
  - `starter_v0/app.py`, `starter_v0/requirements.txt`
- Preflight: `<dán output: OK provider=openrouter model=… / tool=timeline / args=…>`
- Commit/PR: `<commit hash>` — nhánh `trinhtuanphong` trên repo `mKhaiTruong/K5-L3B-DAY03-G2026-ResearchAgentToolEval`.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: dùng DeepSeek Harness/Claude để audit TODO, soạn unit test và báo cáo; dùng OpenRouter `openai/gpt-4o-mini` để chạy eval/chat. Tự kiểm tra bằng cách đọc trực tiếp `results[*].result.failures` trong run JSON, chạy lại `python -m pytest -q -rs`, chạy `chat.py` và xem tool call thật in ra màn hình.

## 5. Tự đánh giá

Hoàn thành phần lớn CP1–CP5 với bằng chứng thật (run JSON, transcript, test). Hạn chế: 4 case eval nhóm và 2 tool `date_calc`/`cite_format` do thành viên khác phụ trách, chưa merge; không làm bonus (Telegram/local model); một số description tool (`timeline`, `social_search`, `lookup`, `fetch`) chưa ghi rõ "khi nào KHÔNG dùng".
