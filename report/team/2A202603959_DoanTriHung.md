# Báo cáo cá nhân

## 1. Thông tin thành viên

- Họ tên: Đoàn Trí Hùng
- MSSV: 2A202603959
- Email: 26ai.hungdt2@vinuni.edu.vn
- GitHub: [hungdt31](https://github.com/hungdt31)
- Nhóm: 3npc (L3B)

## 2. Phần việc phụ trách

- **CP1 — Setup và baseline:** cấu hình môi trường, provider Anthropic, chạy preflight, `pytest` và base eval v0; phân tích lỗi các case FAIL.
- **CP2 — Tối ưu prompt và tool declaration:** vòng lặp giả thuyết → sửa → đo từ v1 đến v6 trên `artifacts/system_prompt.md` và `artifacts/tools.yaml`; ghi `version_log.csv`.
- **CP4 — Eval nhóm:** viết 10 case trong `data/eval_group.json`, chạy lại base sau khi nhóm thêm tool mới (v7) và chạy suite group.
- **Báo cáo nhóm:** bảng B1 (Version Evidence), B2 (Failure Analysis), B3 (Team Eval Cases) trong `report/team/group_report.md`; điền `TEAM.md`.
- Review và merge PR #2 (`cp1_2_3`) và PR #6 (`cp4`).

Không phụ trách: tool mới (`github_repos`, `pypi_package` do Ngô Minh Cương; `hf_models`, `hn_search` do Trần Quang Hà) và UI Streamlit (Ngô Minh Cương).

## 3. Đóng góp cụ thể

**Setup (CP1)**
- Cấu hình `starter_v0/.env` với `ANTHROPIC_API_KEY` và key của Tavily / Firecrawl / RapidAPI.
- Xử lý lỗi kỹ thuật khi chạy provider Anthropic: SDK `anthropic` bản mới nhất (2.7.0) không còn nhận tham số `temperature`, trong khi `providers/anthropic_provider.py`, `agent.py` và `chat.py` đều truyền `temperature=0.0` → preflight báo `TypeError: Messages.create() got an unexpected keyword argument 'temperature'`. Cách xử lý không cần sửa code harness: hạ SDK xuống `anthropic<1` (0.125.0) và chọn model `claude-sonnet-4-6`, model vẫn chấp nhận `temperature=0` và `tool_choice` bắt buộc mà `run_eval.py` dùng.
- Chạy base eval v0: case_accuracy **0.70** (14/20), `provider_error_cases = 0`. Phân loại 6 case FAIL (R03, R10, R12, R13, R14, M02) vào bảng B2.

**Tối ưu v1–v6 (CP2)** — mỗi version một giả thuyết, metric = `case_accuracy` trên `eval_base.json`:

| Version | File | Giả thuyết | Before → After |
|---|---|---|---|
| v1 | `system_prompt.md` | Prompt starter bảo model đoán thay vì hỏi và gửi không cần xác nhận | 0.70 → 0.80 |
| v2 | `tools.yaml` | Thiếu quy ước args nên model nhét "news"/"today" vào `query` | 0.80 → 0.80 |
| v3 | `tools.yaml` | Description mơ hồ nên model không biết khi nào KHÔNG dùng tool (gọi thừa `social_search`) | 0.80 → 0.90 |
| v4 | `system_prompt.md` | Rule "hỏi khi thiếu thông tin" đè lên rule "xác nhận trước khi gửi" | 0.90 → 0.95 |
| v5 | `tools.yaml` | Từ "nổi bật" trong câu hỏi tin tức bị hiểu thành tweet `Top` | 0.95 → 1.00 |
| v6 | `system_prompt.md` | Gom rule routing vào prompt mà không gây regression | 1.00 → 1.00 |

- v2 không tăng điểm nhưng vẫn giữ trong log: `query` đã đúng ở R03, R13, M02, đồng thời làm lộ lỗi gọi thừa `social_search` — là căn cứ cho v3.

**Eval nhóm (CP4)**
- Chạy lại base với 4 tool mới của nhóm (v7) để kiểm tra regression: giữ 20/20.
- Viết 10 case mới (5 single turn + 5 multi turn), phủ đủ 6 loại lỗi; 7 case route tới tool mới, 2 case kiểm tra agent không bị kéo sang tool mới (G04 tin tức về Llama 4 phải dùng `lookup`, G05 debug code phải từ chối). Kết quả 10/10 PASS.

## 4. Bằng chứng

- **File/commit/PR:**
  - Commit `fde3e17` — checkpoint: finish cp1 (`runs/v0_B_base_anthropic_20261110T174610548208.json`, `analysis/base_runs.csv`)
  - Commit `8734337` — checkpoint: finish cp2 (`system_prompt.md`, `tools.yaml`, `version_log.csv`, `TEAM.md`, group report, run v1–v6)
  - Commit `cdd9128` — checkpoint: finish cp4 (`data/eval_group.json`, run v7 base + group, B3)
  - PR #2 (`cp1_2_3`) và PR #6 (`cp4`) trên repo nhóm
  - Run: `starter_v0/runs/v0_…` đến `v7_B_base_…` và `v7_B_group_anthropic_20261110T190257351685.json`; tất cả có `provider_error_cases = 0` và `measured_cases == total_cases`
  - Log: `starter_v0/artifacts/version_log.csv` (v0–v7)

- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Dùng **Claude Code** (model Claude Opus 5.5, trong VS Code) để: đọc README / tài liệu setup và tóm tắt các bước; tìm nguyên nhân lỗi `temperature` với SDK mới; đọc run JSON và liệt kê các case FAIL; viết nháp nội dung `system_prompt.md` và description trong `tools.yaml` cho từng version; viết nháp 10 case trong `eval_group.json`; chạy eval; điền nháp các bảng B1/B2/B3 và `version_log.csv`.
  - Cách tự kiểm tra:
    - Mọi metric trong `version_log.csv` và bảng B1 lấy từ run JSON thật; đối chiếu `prompt_hash`, `tools_hash`, `artifact_version` và `case_accuracy` của từng dòng log với file run tương ứng (khớp cả 8 dòng v0–v7).
    - Mỗi version kiểm tra `prompt_hash` hoặc `tools_hash` khác version trước, và chỉ dùng run có `provider_error_cases == 0`.
    - Sau mỗi lần sửa `tools.yaml` chạy `pytest tests/test_tool_contract.py` (xanh), và chạy toàn bộ `pytest` (0 failed).
    - Đọc lại `failures` và `actual_tool_calls` của từng case FAIL để xác nhận giả thuyết của version trước khi sửa, và xem case nào chuyển PASS/FAIL sau khi sửa.
    - Kiểm tra định dạng `eval_group.json` bằng script (đủ 10 case, 5 single + 5 multi, đủ trường bắt buộc) trước khi chạy suite group.

## 5. Tự đánh giá

- Hoàn thành đầy đủ các đầu việc được giao: setup môi trường và chạy baseline v0, tối ưu system prompt và tool declaration từ v1 đến v6, xây dựng 10 test case cho group eval, kiểm tra regression sau khi nhóm bổ sung tool mới và hoàn thiện các bảng báo cáo B1, B2, B3.

- Kết quả đạt được: nâng case_accuracy trên bộ eval base từ 0.70 lên 1.00, giữ kết quả 20/20 sau khi tích hợp tool mới và đạt 10/10 PASS trên group eval. Các lần chạy đều không có provider error.

- Qua quá trình thực hiện, tôi hiểu rõ hơn vai trò của system prompt và tool declaration, đồng thời nhận ra việc mô tả rõ cả trường hợp không nên sử dụng tool cũng quan trọng như hướng dẫn cách sử dụng.

- Điểm cần cải thiện: bộ eval base hiện chỉ có 20 test case nên kết quả 1.00 chưa đủ chứng minh agent hoạt động tốt trong mọi tình huống. Nếu thực hiện lại, tôi sẽ bổ sung thêm các test case độc lập, đa dạng hơn và kiểm tra khả năng tổng quát hóa để hạn chế việc tối ưu quá sát với dữ liệu kiểm thử hiện tại.
