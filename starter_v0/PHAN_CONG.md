# Phân công — mỗi người một gói, mỗi gói một (vài) commit lên `main`

Nhóm chốt **v0 của Khôi Nguyên** (`runs/v0_B_base_openrouter_20261110T104242979050.json`, case_accuracy **0.70**)
làm baseline. 6 case FAIL của v0 đều do 3 câu chỉ dẫn xấu trong prompt, nên mỗi version v1–v3 gỡ **đúng một** câu,
v4–v5 mới đụng `tools.yaml`. File đã chuẩn bị sẵn nằm ở nhánh **`team-kit`** — mỗi người lấy đúng file của gói mình,
**tự chạy eval bằng key của mình, tự đọc kết quả, tự viết nhận xét**, rồi commit. Ai làm gói nào phải giải thích được gói đó khi demo.

## 1. Các gói việc (làm theo đúng thứ tự cột "Sau")

| Gói | Nội dung | File (trong `starter_v0/`) | Sau | Commit gợi ý |
|---|---|---|---|---|
| **P0** | Baseline v0 + công cụ phân tích + `TEAM.md` | `../TEAM.md` (gốc repo), `runs/v0_…json`, `artifacts/versions/v0/`, `scripts/compare_runs.py`, `scripts/log_version.py`, `analysis/v0_comparison.md`, `artifacts/version_log.csv` (dòng v0), `PHAN_CONG.md` | — | `eval: v0 baseline 0.70 + compare/log tools` |
| **P1** | v1: bỏ *"single step, pick one tool"* | `artifacts/versions/v1/`, `artifacts/system_prompt.md`, `runs/v1_…json`, `version_log.csv`, `analysis/notes_v1.md` | P0 | `prompt v1: allow no-tool & parallel calls` |
| **P2** | v2: bỏ *"đừng hỏi, cứ đoán"* → `clarify(text)` | `artifacts/versions/v2/`, `artifacts/system_prompt.md`, `runs/v2_…`, `version_log.csv`, `analysis/notes_v2.md` | P1 | `prompt v2: clarify instead of guessing` |
| **P3** | v3: bỏ *"cứ gửi"* → `clarify(yes_no)` | `artifacts/versions/v3/`, `artifacts/system_prompt.md`, `runs/v3_…`, `version_log.csv`, `analysis/notes_v3.md` | P2 | `prompt v3: confirm before send` |
| **P4** | v4: viết lại `tools.yaml` (khi nào dùng / KHÔNG dùng, convention args) | `artifacts/versions/v4/`, `artifacts/tools.yaml`, `runs/v4_…`, `version_log.csv`, `analysis/notes_v4.md` | P3 | `tools v4: rewrite tool descriptions` |
| **P5** | Sửa 12 bug tool có sẵn + toàn bộ unit test | `tools/_shared.py`, `tools/{clarify,fetch,format,lookup,send,social_search,timeline}/tool.py`, `tests/test_tools_todo.py`, `analysis/pytest_before_fix.txt`, `analysis/pytest_after_fix.txt` | P0 | 2 commit: `test: …` rồi `fix: …` |
| **P6a** | 4 tool mới + 15 unit test (nối vào cuối `tests/test_tools_todo.py`) | `tools/{wikipedia,hackernews,github_repos,hf_models}/`, `tools/__init__.py`, `tests/test_tools_todo.py` | P5 | `feat: 4 new tools + 15 unit tests` |
| **P6b** | v5: khai báo tool mới + 10 eval case nhóm | `artifacts/versions/v5/`, `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `data/eval_group.json`, `runs/v5_…` (base, group, extension), `version_log.csv`, `analysis/notes_v5.md` | P4, P6a | `v5: route new tools + team eval` |
| **P7a** | UI Streamlit + chat live + poster + link deploy | `app.py`, `requirements.txt`, `scripts/run_chat_demo.py`, `artifacts/poster.html`, `transcripts/*.json` | P6b | `ui: streamlit app + chat transcripts` |
| **P7b** | Report + tự động hoá (làm cuối) | `artifacts/REPORT.md`, `scripts/run_all.py`, `scripts/fill_report.py`, `HUONG_DAN_CHAY.md`, `analysis/all_runs.csv`, `artifacts/local/` | tất cả | `report: fill B1–B7 from runs` |
| P8 *(bonus)* | Model local qua Ollama | `runs/*ollama*`, `version_log.csv`, B7 | P6b | `bonus: local model challenge` |

Đã kiểm tra: áp từng gói theo thứ tự trên vào `main` gốc thì `pytest` luôn xanh ở mọi bước (62 → 89 → 104 → 124 passed).

## 2. Chia người

| Số người | A (Khôi Nguyên) | B | C | D | E |
|---|---|---|---|---|---|
| 3 | P0, P3, P6b, P7b | P1, P4, P5 | P2, P6a, P7a | | |
| 4 | P0, P6b, P7b | P1, P5 | P2, P4, P6a | P3, P7a | |
| 5 | P0, P7b | P1, P5 | P2, P6a | P3, P4, P6b | P7a, P8 |

## 3. Quy trình cho MỖI gói (PowerShell, đứng ở thư mục gốc repo)

```powershell
# (một lần) commit phải đứng tên đúng tài khoản GitHub của bạn
git config user.name  "TÊN-GITHUB-CỦA-BẠN"
git config user.email "EMAIL-GITHUB-CỦA-BẠN"

git fetch origin
git checkout -B <ten>-<goi> origin/main                 # luôn bắt đầu từ main MỚI NHẤT
git checkout origin/team-kit -- <các file của gói>      # vd: starter_v0/artifacts/versions/v1
# ... làm phần việc (mục 4) ...
git add <các file của gói>
git status                                              # không có .env / .venv
git commit -m "<commit gợi ý>"
git push -u origin <ten>-<goi>
```

Rồi lên GitHub → **Compare & pull request** → base `main` → **Merge**. Người làm gói sau chỉ bắt đầu khi PR gói trước
đã merge (vì `version_log.csv` và `artifacts/system_prompt.md` nối tiếp nhau).

## 4. Việc cụ thể từng gói (chạy trong `starter_v0`, đã bật `.venv`, có `.env`)

**P1 / P2 / P3 / P4** (thay `vN`):

```powershell
python run_eval.py --provider openrouter --version vN --suite base --eval-cases data/eval_base.json --system-prompt artifacts/versions/vN/system_prompt.md --tools artifacts/versions/vN/tools.yaml
Copy-Item artifacts/versions/vN/system_prompt.md artifacts/system_prompt.md   # P4: tools.yaml thay vì system_prompt.md
python scripts/log_version.py runs/vN_B_base_openrouter_<...>.json --author "Tên" --changed system_prompt.md --reason "<đổi gì>" --hypothesis "<vì sao — dẫn case v0>"
python scripts/compare_runs.py runs/ --version all                             # xem case nào đổi trạng thái
```

Viết `analysis/notes_vN.md` (3–5 dòng): metric trước → sau, case nào chuyển FAIL→PASS / PASS→FAIL, giả thuyết **đúng hay sai**
và vì sao (dẫn tên run file). Nếu sai: đổi giả thuyết, sửa `artifacts/versions/vN/`, chạy lại (log_version tự thay dòng cũ).

**P0:** điền `TEAM.md` (tên nhóm, thành viên, MSSV, GitHub, gói), `git checkout origin/nguyenkhoinguyen -- starter_v0/runs/v0_B_base_openrouter_20261110T104242979050.json`, lấy file P0 từ `team-kit`, rồi
`python scripts/log_version.py runs/v0_B_base_openrouter_20261110T104242979050.json --author "Khôi Nguyên" --changed baseline --reason "Baseline starter" --hypothesis "Đo hành vi chưa tối ưu"`
và `python scripts/compare_runs.py runs/ --version v0 --output analysis/v0_comparison.md`.

**P5:** commit 1 — chỉ lấy `tests/test_tools_todo.py`, chạy `pytest | Out-File -Encoding utf8 analysis/pytest_before_fix.txt` (kỳ vọng **13 failed**: các test bắt bug), commit `test: fill TODO tests + 13 regression tests`.
Commit 2 — lấy các file `tools/…`, chạy `pytest -v | Out-File -Encoding utf8 analysis/pytest_after_fix.txt` (0 failed), commit `fix: 12 bugs in starter tools`.

**P6a:** lấy 5 đường dẫn tool (`starter_v0/tools/wikipedia` … `starter_v0/tools/__init__.py`) từ `team-kit`, rồi nối test của tool mới vào cuối file test (đúng yêu cầu README: test tool mới nằm trong `tests/test_tools_todo.py`):
```powershell
git checkout origin/team-kit -- kit_extra/new_tools_tests_section.py
Get-Content -Encoding UTF8 kit_extra/new_tools_tests_section.py | Add-Content -Encoding UTF8 starter_v0/tests/test_tools_todo.py
git restore --staged kit_extra; Remove-Item -Recurse kit_extra
```
`pytest` (124 passed, 42 test trong `test_tools_todo.py`), commit `tools/…` + `tests/test_tools_todo.py`. **P6b:** chạy base v5 + group + extension (đổi `--suite group --eval-cases data/eval_group.json`, `--suite extension --eval-cases data/eval_research_extension.json`), `log_version.py` cho cả 3 run (label tự thành `v5`, `v5-group`, `v5-extension`), copy `versions/v5/*` vào `artifacts/`, `pytest` (124 passed).

**P7a:** `pip install streamlit`, `streamlit run app.py`, `cloudflared tunnel --url http://localhost:8501`, dán link vào poster + REPORT A1;
chat ≥ 3 lượt (`python chat.py --provider openrouter --version v5` hoặc `python scripts/run_chat_demo.py --provider openrouter --version v5 --system-prompt artifacts/versions/v5/system_prompt.md --tools artifacts/versions/v5/tools.yaml`).

**P7b:** `python scripts/parse_runs.py runs/ --output analysis/all_runs.csv`, `python scripts/fill_report.py`, gộp các `analysis/notes_v*.md` vào REPORT B1/B2/B6, điền tên nhóm + thành viên.

## 5. Nộp bài (theo slide lớp)

- **Hạn:** ca 9:00 và ca 14:00 → **23:59 hôm nay**; ca 16:30 → 12:00 trưa mai. Nộp muộn bị trừ điểm.
- **Mỗi học viên tự nộp link repo riêng** trên **aithucchien.vinuni.edu.vn**, tên repo: `K5-L3-DAY03-HoVaTen-MSSV-ResearchAgentToolEval`
  (không dấu, nối bằng `-`). Trưởng nhóm nộp thêm repo nhóm `K5-L3-DAY03-TenNhom-ResearchAgentToolEval`, có `TEAM.md`.
- Khi `main` của repo nhóm đã đủ mọi gói, mỗi người đẩy bản cuối sang repo cá nhân của mình:
```powershell
git checkout main; git pull
git remote add personal https://github.com/<github-cua-ban>/K5-L3-DAY03-<HoVaTen>-<MSSV>-ResearchAgentToolEval.git
git push personal main:main
```
  Nếu bị từ chối (`rejected … fetch first`) vì repo cá nhân đã có commit khác: hỏi lại trước khi dùng `--force`.
- Repo không chứa `.env` / API key. Cuối buổi quét QR điểm danh lần 2.

## 6. Lưu ý

- Không commit `.env`, không dán key vào chat/PR. Mỗi người dùng key của chính mình.
- Run cũ của vòng khám phá (nhánh `nguyenkhoinguyen`) không đưa vào `main`; REPORT đã ghi chú vòng đó.
- Eval có thể dao động giữa các lần chạy; nếu kết quả lạ, chạy lại 1 lần với `--version vN-rep2` và ghi cả hai vào notes.
