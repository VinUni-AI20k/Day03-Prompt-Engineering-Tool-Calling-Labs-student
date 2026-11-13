# DucLT — Dev (test, tool mới, đo lường)

**Nhánh làm việc:** `feat/DucLT-...`

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

### Riêng cho DucLT
- Cần `.env` đầy đủ để tự chạy preflight và eval. Unit test thì chạy offline: mock HTTP bằng `fake_http`, gán key giả bằng `monkeypatch.setenv`. Mẫu để copy: `tests/test_tools_examples.py`, fixture trong `tests/conftest.py`
- Đọc trước: `tools/README.md` (cách viết tool), `tools/<tên>/tool.py` + `TOOL.md` của tool có sẵn, [CHECKPOINTS.md](../CHECKPOINTS.md) (CP3)
- Mỗi test: một hành vi, đặt tên theo hành vi; ≥ 3 test cho tool mới (happy path, input xấu từ model, nhánh lỗi). Tool nên trả error dict, không raise
- Làm xong tool thì chạy `pytest tests/test_tool_contract.py` (phải xanh) và báo tên tool, args cho TrungNB và QuanNH
- Tool mới cần đăng ký ở 2 chỗ: `tools/__init__.py` (`TOOL_FUNCTIONS`) và `artifacts/tools.yaml`
- Sau khi có tool mới, tự chạy eval/chat với tool thật để xem model có route đúng không
- Ollama (bonus): cài từ https://ollama.com/download, máy nên có ≥ 8 GB RAM trống; `ollama pull qwen2.5:7b` và `ollama pull llama3.2:3b`; preflight: `python scripts/preflight_provider.py --provider ollama --model qwen2.5:7b`
- Báo cáo: cần MSSV 2A202604019

## Checklist
- [x] Hoàn thành 17 hàm test trong `tests/test_tools_todo.py`: 14 cho tool có sẵn và 3 cho tool mới `stats`; bỏ toàn bộ `pytest.skip`. Contract test xanh.
- [ ] Tool mới xong trước 15:30 (CP3) để TrungNB có tool thật mà viết case route
- [x] Tool mới `stats` (mean, median, độ lệch chuẩn mẫu), gồm:
  - [x] `tools/stats/tool.py` và `TOOL.md`
  - [x] Đăng ký trong `tools/__init__.py` (`TOOL_FUNCTIONS`) và `artifacts/tools.yaml`
  - [x] ≥ 3 unit test
  - [ ] Bonus: làm ≥ 4 tool mới
- [ ] Dùng `scripts/parse_runs.py` tổng hợp metric v0→v3 (pass rate theo version, theo loại case), gửi bảng cho TrungNB ghi vào báo cáo
- [x] Bonus pytest: 0 failed, 0 skipped — xem `starter_v0/analysis/duclt_pytest.txt`.
- [ ] Bonus Ollama: `ollama pull qwen2.5:7b` và `llama3.2:3b`, preflight `--provider ollama`, ≥ 2 model và ≥ 2 vòng tối ưu local
- [ ] Có ít nhất 1 commit kỹ thuật trong lịch sử nhánh nộp
- [ ] Nộp link repo trên LMS bằng tài khoản cá nhân trước 23h59
- [ ] Báo cáo cá nhân `report/team/MSSV_HoTen.md`

## Việc đang làm
-

## Việc đã xong (kèm bằng chứng: PR, commit, file run)
- Hoàn thành 17 hàm test trên nhánh `feat/DucLT-tool-tests`; parametrization mở rộng thành 37 trường hợp.
- Thêm tool local `stats(values, statistic="mean")`, nhận `mean|median|stdev`; không gọi API, không cần key.
- Lệnh kiểm tra từ `starter_v0/`: `.venv/bin/python -m pytest -v` → **104 passed, 0 failed, 0 skipped**. Log: `starter_v0/analysis/duclt_pytest.txt`.
- Chưa chạy eval/chat thật cho `stats`; cần phối hợp TrungNB thêm case route tới tool mới.

## Vướng mắc / cần lead hỗ trợ
-

## Ghi chú kỹ thuật (giả thuyết, quyết định, vì sao sửa như vậy)
- HTTP được mock bằng `fake_http`; key giả qua `monkeypatch.setenv`, không nạp `.env` trong test.
- Test kiểm tra request và kết quả; thêm biên cắt markdown 3999/4000/4001/4500 ký tự, thiếu một trong hai biến Telegram, cả Top/Latest, input stats sai kiểu/NaN/Infinity.
- `stats` dùng thư viện chuẩn `statistics`; `stdev` là độ lệch chuẩn mẫu (n-1). Dữ liệu không hợp lệ hoặc không đủ mẫu trả error dict.

## Công cụ AI đã dùng (để ghi vào báo cáo cá nhân)
- Codex hỗ trợ viết tool/test và chạy pytest. Cần DucLT đọc lại, tự giải thích và review diff trước khi commit/PR.
