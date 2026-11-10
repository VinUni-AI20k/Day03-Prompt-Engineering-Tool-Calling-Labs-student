# TrungNB — Dev (eval case, báo cáo, Telegram)

**Nhánh làm việc:** `feat/TrungNB-...`

## Điều kiện cần & hướng dẫn

### Chung (ai cũng cần)
- Git, Python 3 (`python3 --version`), quyền Collaborator trên repo nhóm
- Setup một lần:
  ```bash
  git clone https://github.com/haiquanng/K5-L3B-DAY03-Ban5-ResearchAgentToolEval.git
  cd K5-L3B-DAY03-Ban5-ResearchAgentToolEval/starter_v0
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  cp .env.example .env     # .env KHÔNG commit
  pytest                   # contract + example xanh, TODO đang skipped là bình thường
  ```
- Làm việc: `git checkout -b feat/<tên>-<việc>` → commit → push → mở PR → QuanNH review. Không push thẳng `main`.
- Key/token không dán vào chat, báo cáo hay commit.

### Riêng cho TrungNB
- Cần `.env` đầy đủ (provider + Tavily + Firecrawl + RapidAPI) để tự chạy eval, preflight và `--suite group`. Đọc trước: [CHECKPOINTS.md](../CHECKPOINTS.md) (CP4), mẫu trong `starter_v0/data/eval_base.json` (không sửa file đó), [RUBRIC.md](../RUBRIC.md)
- Mỗi case cần: `failure_type`, `expect`, `metadata.what_it_tests`. 5 case `query` (single turn) + 5 case `turns` (multi turn). Phải có ≥ 1 case route tới tool mới của DucLT, nên chờ DucLT chốt tên và args tool
- Tự chạy `--suite group` để kiểm tra schema và đủ 10 case trước khi mở PR
- Đọc log: `runs/*.json` (kiểm `provider_error_cases == 0` và `measured_cases == total_cases`), `scripts/parse_runs.py`
- Telegram (bonus): tài khoản Telegram, BotFather → `/newbot` (đặt name + username kết thúc bằng `bot`) → tạo private channel → thêm bot làm admin → lấy `TELEGRAM_CHAT_ID` qua `getUpdates`. Token chỉ để trong `.env`, chỉ gửi vào private channel nhóm
- Báo cáo: cần MSSV 2A202604013, và số liệu thật từ run của QuanNH

## Checklist
- [x] Viết 10 case trong `data/eval_group.json`: 5 single turn + 5 multi turn
  - [x] Có case thiếu thông tin (agent phải hỏi lại bằng `clarify`)
  - [x] Có case `send` phải xin xác nhận trước khi gửi
  - [x] Ít nhất 1 case route tới tool mới (phối hợp với DucLT - tool `stats`)
  - [x] Không sửa `eval_base.json` và `eval_research_extension.json`
- [x] Điền Phần A của `group_report.md` TRƯỚC showdown 16:30 (A1 lệnh chạy UI, A3 câu hỏi mẫu)
- [x] Bảng B2 (Failure Analysis v0), B1 (v1–v3), B3 (eval nhóm), B5a (tool mới) trong group report
- [x] Đọc log từng version, ghi `artifacts/version_log.csv`: triệu chứng, giả thuyết, thay đổi, kết quả (chỉ số liệu thật)
- [x] Điền `TEAM.md` (thông tin nhóm, thành viên, vai trò)
- [x] Viết `report/team/group_report.md`: Phần A trước 16:30, Phần B để nộp
- [ ] Tạo bot Telegram (BotFather → `/newbot` → private channel → thêm bot làm admin → lấy chat id), token chỉ để trong `.env`
- [ ] Test `send` thật sau khi user xác nhận (chỉ gửi vào private channel của nhóm)
- [ ] Chat live ≥ 3 lượt trên UI, lưu transcript
- [x] Có ít nhất 1 commit kỹ thuật trong lịch sử nhánh nộp
- [ ] Nộp link repo trên LMS bằng tài khoản cá nhân trước 23h59
- [x] Báo cáo cá nhân `report/team/MSSV_HoTen.md`

## Việc đang làm
- Hoàn thiện báo cáo cá nhân và nộp bài trên LMS trước 23h59.

## Việc đã xong (kèm bằng chứng: PR, commit, file run)
- Merge và giải quyết conflict từ `origin/main`: commit `fa5c001`, `7618298`
- Hoàn thành Phần A (A1, A2, A3), phân tích lỗi v0 (Bảng B2), cập nhật B1: commit `c35c322`
- Merge tích hợp tool mới `stats` và test offline từ nhánh `origin/feat/DucLT-tool-tests`: commit `b788f27` (chạy pytest 104 passed)
- Xây dựng 10 test case nhóm trong `starter_v0/data/eval_group.json`, cập nhật Bảng B3, B5a: commit `0cdeb72`

## Vướng mắc / cần lead hỗ trợ
- Không còn vướng mắc kỹ thuật.

## Ghi chú kỹ thuật (giả thuyết, quyết định, vì sao sửa như vậy)
- Áp dụng cơ chế Human-in-the-Loop (HITL) cho tool `send` và chặn gọi tool khi thiếu tham số bắt buộc (gọi `clarify`).
- Bổ sung Guardrail từ chối các yêu cầu ngoài phạm vi nghiên cứu (như code bài toán) với kỳ vọng `no_tool: true`.
- Tích hợp tool `stats` của DucLT để kiểm tra khả năng trích xuất danh sách số liệu và tính trung bình cộng.

## Công cụ AI đã dùng (để ghi vào báo cáo cá nhân)
- Google Antigravity Agent (Gemini 3.8 Flash High): Trợ lý lập trình cặp (pair programming) theo phương thức tương tác hỏi - đáp từng bước, hỗ trợ phân tích log lỗi thất bại v0, rà soát cú pháp schema eval cases, chẩn đoán merge conflict git và đối chiếu các tiêu chí trong rubric. Toàn bộ logic nghiệp vụ và kịch bản test case do sinh viên trực tiếp quyết định.
