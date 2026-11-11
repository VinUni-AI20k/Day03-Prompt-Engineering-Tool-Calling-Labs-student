# Team

## Thông tin nhóm

- Tên nhóm: **DaCoChu**
- Lớp: L3A / L3B
- Repo nhóm: `K5-L3-DAY03-DaCoChu-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Bùi Đặng Nhật Nguyên | 2A202603937 | nhatnguyenmtvt@gmail.com | double-n-021 | Dev Tool & `tools.yaml` |
|   2 | Nguyễn Bá Quang Huy | 2A202603926 | quanghuynguyenba@gmail.com | quanghuynguyenba | Update System Prompt |
|   3 | Đỗ Hoàng Vũ  | 2A202603920 | dohoangvu.nt2005@gmail.com | hoangvu1806 | Tester |
|   4 | Lê Hải Lân  | 2A202603915 | lehailan110@gmail.com | laaaaanleeeee | Design UI |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## BuiDangNhatNguyen-2A202603937

### Phần việc phụ trách

- **CP2 (`starter_v0/artifacts/tools.yaml`):** Viết lại toàn bộ mô tả (`description`) và quy ước tham số (`parameters`) cho 10 tool gốc qua các vòng lặp `v2`, `v3`, `v4`, tách bạch `DÙNG KHI` / `KHÔNG DÙNG KHI` và chuẩn hóa kiểu dữ liệu tham số.
- **CP3 & Bonus (`starter_v0/tools/<name>/` + `starter_v0/tools/__init__.py`):** Thiết kế và lập trình **4 tool mới do nhóm tự viết** (`github_search`, `hf_models`, `hn_search`, `pypi_info`), kèm `TOOL.md` chuẩn YAML frontmatter.
- **CP3 (`starter_v0/tests/test_tools_todo.py`):** Viết **21 hàm unit test** (34 test item khi parametrize) kiểm thử offline bằng `fake_http` cho cả 4 tool mới.
- **CP4 (`starter_v0/data/eval_group.json` & `starter_v0/data/eval_research_extension.json`):** Viết case `G05_custom_tools_routing` và `E11`–`E14` kiểm tra routing tới 4 tool mới.

### Đóng góp cụ thể

- Ở `v2`: đưa `response_type` vào `required` của `clarify`, bổ sung quy ước ánh xạ `timeframe` (`day/week/month/year`), `screenname` (bỏ `@`), và `query` ngắn gọn trong `tools.yaml` → nâng Base từ `0.90` lên `0.95` (19/20), Group từ `7/9` lên `8/9` (sửa `R10`, `R12`, `G01`, `GM03`).
- Ở `v3`: sửa 2 lỗi hồi quy của `v2` (`GM02` hỏi lại xác nhận dù user đã đồng ý; `M06` gọi thừa `social_search` khi user bảo bỏ Twitter) và thêm tool `github_search` → đưa Base đạt `20/20 (1.00)` và Group đạt `10/10 (1.00)`.
- Ở `v4`: phát triển thêm 3 tool mới (`hf_models`, `hn_search`, `pypi_info`) nâng tổng số tool mới lên 4 (đạt mốc Bonus `≥ 4 tool mới`), tất cả dùng REST API công khai miễn phí (`requires_env: []`), kiểm tra input trước khi gọi mạng và trả về error dict thay vì raise exception → giữ vững Base `20/20 (1.00)`, Group `10/10 (1.00)` và Extension đạt `13/14` (cả 4 case `E11`–`E14` của 4 tool mới đều PASS).
- Viết 21 hàm unit test cho 4 tool mới trong `tests/test_tools_todo.py` (happy path, input rỗng/sai kiểu/`limit <= 0`/ngoài enum, nhánh lỗi HTTP 404/429/500/503/timeout, dữ liệu hỏng), góp phần đưa toàn bộ test suite đạt `137 passed, 0 skipped, 0 failed`.

### Bằng chứng

- Branch `BuiDangNhatNguyen`; các commit & PR:
  - `b4e39cb` (PR #3 — merge `da76c7f`): viết lại `starter_v0/artifacts/tools.yaml` cho `v2`.
  - `b293c41` (PR #6 — merge `9c68583`): thêm tool `github_search`, 7 hàm unit test, case `G05`, và sửa `tools.yaml` cho `v3`.
  - `8bfb987` (PR #8 — merge `2e8cd23`): thêm 3 tool Bonus (`hf_models`, `hn_search`, `pypi_info`), 14 hàm unit test mới, cập nhật `G05` + `E11`–`E14`, và báo cáo cá nhân.
- Run JSON: `runs/v2_B_base_openrouter_20261110T191207255603.json`, `runs/v3_B_base_openrouter_20261110T193230070343.json`, `runs/v3_B_group_openrouter_20261110T193308629861.json`, `runs/v4_B_base_openrouter_20261110T200626400416.json`, `runs/v4_B_group_openrouter_20261110T200706447380.json`, `runs/v4_B_extension_openrouter_20261110T200748658442.json`.
- Báo cáo cá nhân: `report/team/2A202603937_BuiDangNhatNguyen.md`.

## DoHoangVu-2A202603920

### Phần việc phụ trách

- Tester: viết unit test cho tool, viết eval case của nhóm, chạy eval sau mỗi version và phân tích case FAIL.
- Giữ `starter_v0/artifacts/version_log.csv`: ghi kết quả từng version v0–v4.

### Đóng góp cụ thể

- Viết 14 unit test offline cho 8 tool có sẵn (`tests/test_tools_todo.py`), HTTP được mock bằng `fake_http`.
- Tìm và sửa 3 bug trong tool: `limit=0`/`max_results=0` bị âm thầm đổi thành 5 (timeline, social_search, lookup); `policy(top_k=0)` bị đổi thành 1; `clarify(response_type="choice")` không có `options` vẫn chạy. Thêm `positive_int` trong `tools/_shared.py` và 5 regression test.
- Viết 9/10 case trong `data/eval_group.json` (G01–G04, GM01–GM05), phủ đủ 6 loại lỗi.
- Chạy base, group (và extension ở v4) sau mỗi version, đọc `failures`/`actual_tool_calls` trong run JSON và báo nguyên nhân cho nhóm làm giả thuyết version sau: thiếu `response_type` của clarify (→ v2), regression GM02/M06 (→ v3), rule xin credentials trong prompt (đã bỏ), E01 chọn sai `policy_area` (gợi ý cho v5).
- Kết quả theo dõi: base 13/20 → 18/20 → 19/20 → 20/20 → 20/20; group 5/9 → 7/9 → 8/9 → 10/10 → 10/10; extension v4 13/14.
- Sửa lỗi môi trường làm `pytest` crash (lệch phiên bản `opentelemetry-exporter-otlp-proto-grpc`).

### Bằng chứng

- Branch `DoHoangVu`; commit `8f54f78` (test, sửa bug, eval case nhóm, run v0 — PR #1), `e7ad2ad` (log v0), `4969420`/`9947499` (eval v1 — PR #2, #4), `cd377bf` (eval v2 — PR #5), `30647fe` (eval v4).
- `starter_v0/artifacts/version_log.csv` (dòng v0–v4) và các run JSON trong `starter_v0/runs/`.
- `pytest`: 137 passed.
- Báo cáo cá nhân: `report/team/2A202603920_DoHoangVu.md`.

## NguyenBaQuangHuy-2A202603926

### Phần việc phụ trách

- **CP1 (`starter_v0/artifacts/system_prompt.md`):** Cải tiến system prompt cho **v1** — bỏ chỉ dẫn xấu của starter, thêm rule clarify / xác nhận trước `send` / routing tool / multi-turn chỉ xử lý lượt mới nhất.
- Phối hợp tester (Vũ) đọc fail log và phản hồi rủi ro credentials để chốt bản prompt cuối trước khi ghi dòng v1 vào `artifacts/version_log.csv`.

### Đóng góp cụ thể

- Commit `ba02a75` (`update system prompt`): thay toàn bộ starter xấu bằng rule clarify + routing + confirm trước khi `send`. Agent không còn được đoán handle/URL hay tự gửi.
- Commit `425911f` (`fix system prompt`): bỏ rule xin platform/credentials ngay trong chat (Vũ báo rủi ro lộ token); thu hẹp xác nhận còn `clarify(response_type=yes_no)` rồi `send(confirmed=true)`; siết multi-turn chỉ hành động theo message mới nhất.
- Giả thuyết v1: bỏ chỉ dẫn xấu + thêm rule clarify / xác nhận send / routing / chỉ xử lý lượt mới nhất sẽ giảm lỗi `missing_info`, `wrong_boundary`, `out_of_scope`.
- Kết quả đo được: Base v0 **0.65** → v1 **0.90** (18/20); Group **7/9** (case_accuracy 0.7778); cả hai run `provider_error_cases = 0`.
- Phân tích FAIL còn lại sau v1 và bàn giao giả thuyết cho v2/v3: `R10`/`R12` thiếu `response_type`; `G01` chưa map “tháng này → month”; `GM03` gọi thừa `lookup` — phần arg contract thuộc `tools.yaml` (Nguyên xử lý ở v2/v3).

### Bằng chứng

- Commit `ba02a75` (bản đầu), `425911f` (bản cuối v1); dòng v1 trong `artifacts/version_log.csv` (author `quanghuynguyenba`, prompt_hash `8c876c84e53c`).
- Run JSON: `runs/v1_B_base_openrouter_20261110T185510918902.json`, `runs/v1_B_group_openrouter_20261110T185542663317.json` (Vũ chạy lại trên prompt cuối).
- Báo cáo cá nhân: `report/team/2A202603926_NguyenBaQuangHuy.md`.

## LeHaiLan-2A202603915

### Phần việc phụ trách

- **UI Live Chat:** Xây giao diện Streamlit (`app.py` + `chat_service.py`) để người dùng chat trực tiếp với Research Agent thay vì terminal.
- **Bonus Telegram:** Tích hợp gửi tin nhắn thật lên Telegram sau khi người dùng xác nhận (`confirmed=true`).
- **Bonus Small Local Model Challenge:** Thử nghiệm Ollama (`qwen2.5:7b`, `llama3.2:3b`) với prompt/tools rút gọn và eval mini.

### Đóng góp cụ thể

- Xây `app.py` (Streamlit) và `chat_service.py` (`ChatSession`): khởi tạo provider, load system prompt + tool declarations, quản lý conversation history / transcript theo session, gọi `run_model_tool_loop()`.
- Dùng `st.session_state` giữ session riêng từng cuộc hội thoại; spinner/lỗi provider; khu vực `tool_events`; transcript ID + đường dẫn lưu.
- Thiết kế UI không phụ thuộc tên tool cụ thể — khi thêm `github_search` / `hf_models` / … vẫn hiện qua `tool_events` mà không sửa lại chat.
- Kiểm thử Live Chat với OpenRouter; đồng bộ version UI ↔ `ChatSession` ↔ transcript; bổ sung `streamlit` vào `requirements.txt`.
- Bonus Telegram: tích hợp gửi thật qua Bot Token/Chat ID, chỉ gửi khi `clarify(yes_no)` → `send(confirmed=true)`; chạy thử và lưu transcript chứng minh.
- Bonus Local Model: cấu hình `system_prompt_local.md` + `tools_local.yaml` (rút gọn, few-shot); eval `eval_base.json` / `eval_mini.json`; ghi log tới `v5` / `v5-mini` trên Ollama; khắc phục hang ở `R12` bằng cách đưa rule ép `clarify` lên đầu prompt.

### Bằng chứng

- File: `app.py`, `chat_service.py`, `artifacts/system_prompt_local.md`, `data/eval_mini.json`, `artifacts/version_log.csv` (đến v5), run JSON trong `runs/` (v1–v5, gồm `v5-mini` Ollama).
- Demo: Streamlit tại `http://localhost:8501/`; transcript Live Chat; log `OK provider=ollama model=llama3.2:3b` / `qwen2.5:7b`.
- Báo cáo cá nhân: `report/team/2A202603915_LeHaiLan.md`.
