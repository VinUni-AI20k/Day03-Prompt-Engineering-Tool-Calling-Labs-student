# QuanNH — Dev (lead: prompt, eval, UI)

**Nhánh làm việc:** `feat/QuanNH-...`

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

### Riêng cho QuanNH
- `.env` đủ key: một provider (`GEMINI_API_KEY` hoặc `OPENROUTER_API_KEY`...), `TAVILY_API_KEY`, `FIRECRAWL_API_KEY`, `RAPIDAPI_KEY` (đã Subscribe gói free của twitter-api45) + `RAPIDAPI_TWITTER_HOST`
- Smoke test từng tool theo [docs/TOOL-SETUP.md](../docs/TOOL-SETUP.md); preflight: `python scripts/preflight_provider.py --provider <gemini|openrouter|openai>`
- Chạy eval: `python run_eval.py --provider <p> --version v1 ...`. Giữ nguyên provider và model từ v0 đến v3.
- UI: Node.js 18+ và `npm`, `cloudflared` (`brew install cloudflared`), `fastapi` + `uvicorn` trong `requirements.txt`
- Mỗi người có `.env` riêng và tự chạy được eval

## Checklist
- [ ] Setup venv, `.env` (một provider), `preflight_provider.py` xanh
- [ ] Chạy `pytest`, ghi trạng thái ban đầu
- [ ] Chạy baseline v0 (CHƯA sửa prompt/tools), lưu run JSON, kiểm tra `provider_error_cases == 0` và `measured_cases == total_cases` (CP1, 15:00)
- [ ] Gán loại lỗi (`wrong_tool`, `wrong_arg_value`, `missing_info`, `wrong_boundary`) cho từng case FAIL của v0 → bảng B2
- [ ] Sửa `artifacts/system_prompt.md`: bỏ chỉ dẫn xấu (đoán thay vì hỏi, gửi không xác nhận, ép một bước), thêm rule routing
- [ ] Viết lại description trong `artifacts/tools.yaml` (khi nào dùng / không dùng, convention args)
- [ ] Tối ưu v1 (15:30), v2 (16:00), v3 (17:30): mỗi vòng MỘT giả thuyết → sửa → đo lại; ghi `version_log.csv` (hash, giả thuyết, metric trước/sau) → bảng B1
- [ ] Chạy `--suite group` với `data/eval_group.json` sau khi TrungNB viết xong 10 case
- [ ] Đổi tên repo theo `K5-L3A-DAY03-TenNhom-ResearchAgentToolEval`, ghi commit chốt trong `TEAM.md`
- [ ] Review và merge PR của TrungNB và DucLT
- [ ] `server.py` (FastAPI, SSE stream tool call) + `web/` (Next.js, shadcn/ui), thêm dependency vào `requirements.txt`. LƯU Ý: UI phải dùng thử được TRƯỚC showdown 16:30, nên làm ngay sau v1 + tool mới, không để cuối
- [ ] Mở link dùng thử (cloudflared), ghi lệnh chạy UI vào mục A1 group report; nhờ người ngoài nhóm thử câu hỏi mẫu A3
- [ ] Chat live ≥ 3 lượt, lưu transcript
- [ ] Nộp link repo trên LMS bằng tài khoản cá nhân trước 23h59
- [ ] Báo cáo cá nhân `report/team/MSSV_HoTen.md`
- [ ] Kiểm tra `runs/` và `transcripts/` không lộ key trước khi nộp

## Việc đang làm
-

## Việc đã xong (kèm bằng chứng: PR, commit, file run)
-

## Vướng mắc
-

## Ghi chú kỹ thuật (giả thuyết, quyết định, vì sao sửa như vậy)
-

## Công cụ AI đã dùng (để ghi vào báo cáo cá nhân)
-
