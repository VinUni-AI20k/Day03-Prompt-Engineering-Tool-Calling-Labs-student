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
- Key/token không dán vào chat, báo cáo hay commit. Nếu cần key, xin QuanNH qua tin nhắn riêng.

### Riêng cho TrungNB
- Cần `.env` đầy đủ như QuanNH (provider + Tavily + Firecrawl + RapidAPI) để tự chạy eval, preflight và `--suite group`; xin key từ QuanNH qua tin nhắn riêng. Đọc trước: [CHECKPOINTS.md](../CHECKPOINTS.md) (CP4), mẫu trong `starter_v0/data/eval_base.json` (không sửa file đó), [RUBRIC.md](../RUBRIC.md)
- Mỗi case cần: `failure_type`, `expect`, `metadata.what_it_tests`. 5 case `query` (single turn) + 5 case `turns` (multi turn). Phải có ≥ 1 case route tới tool mới của DucLT, nên chờ DucLT chốt tên và args tool
- Tự chạy `--suite group` để kiểm tra schema và đủ 10 case trước khi mở PR
- Đọc log: `runs/*.json` (kiểm `provider_error_cases == 0` và `measured_cases == total_cases`), `scripts/parse_runs.py`
- Telegram (bonus): tài khoản Telegram, BotFather → `/newbot` (đặt name + username kết thúc bằng `bot`) → tạo private channel → thêm bot làm admin → lấy `TELEGRAM_CHAT_ID` qua `getUpdates`. Token chỉ để trong `.env`, chỉ gửi vào private channel nhóm
- Báo cáo: cần MSSV 2A202604013, và số liệu thật từ run của QuanNH

## Checklist
- [ ] Viết 10 case trong `data/eval_group.json`: 5 single turn + 5 multi turn
  - [ ] Có case thiếu thông tin (agent phải hỏi lại bằng `clarify`)
  - [ ] Có case `send` phải xin xác nhận trước khi gửi
  - [ ] Ít nhất 1 case route tới tool mới (phối hợp với DucLT)
  - Không sửa `eval_base.json` và `eval_research_extension.json`
- [ ] Điền Phần A của `group_report.md` TRƯỚC showdown 16:30 (A1 lệnh chạy UI, A3 câu hỏi mẫu)
- [ ] Bảng B2 (Failure Analysis v0), B1 (v1–v3), B3 (eval nhóm), B5a (tool mới) trong group report
- [ ] Đọc log từng version, ghi `artifacts/version_log.csv`: triệu chứng, giả thuyết, thay đổi, kết quả (chỉ số liệu thật)
- [ ] Điền `TEAM.md` (thông tin nhóm, thành viên, vai trò)
- [ ] Viết `report/team/group_report.md`: Phần A trước 16:30, Phần B để nộp
- [ ] Tạo bot Telegram (BotFather → `/newbot` → private channel → thêm bot làm admin → lấy chat id), token chỉ để trong `.env`
- [ ] Test `send` thật sau khi user xác nhận (chỉ gửi vào private channel của nhóm)
- [ ] Chat live ≥ 3 lượt trên UI, lưu transcript
- [ ] Có ít nhất 1 commit kỹ thuật trong lịch sử nhánh nộp
- [ ] Nộp link repo trên LMS bằng tài khoản cá nhân trước 23h59
- [ ] Báo cáo cá nhân `report/team/MSSV_HoTen.md`

## Việc đang làm
-

## Việc đã xong (kèm bằng chứng: PR, commit, file run)
-

## Vướng mắc / cần lead hỗ trợ
-

## Ghi chú kỹ thuật (giả thuyết, quyết định, vì sao sửa như vậy)
-

## Công cụ AI đã dùng (để ghi vào báo cáo cá nhân)
-
