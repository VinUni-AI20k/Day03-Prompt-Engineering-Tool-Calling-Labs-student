# Team

## Thông tin nhóm

- Tên nhóm: Hehehe (theo tên repo; nhóm cần xác nhận).
- Lớp: L3B.
- Repo nhóm: `K5-L3B-DAY03-Hehehe-ResearchAgentToolEval`.
- URL repo: https://github.com/trongnghia2304/K5-L3B-DAY03-Hehehe-ResearchAgentToolEval
- Nhánh hiện tại: `main`; nhánh nộp và commit chốt: chưa chốt.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
| 1 | Vũ Văn Bình | Chưa cung cấp | Chưa cung cấp | Chưa cung cấp | Setup, chạy baseline v0, tổng hợp bằng chứng CP1 |
| 2 | Trần Thị Hà Anh | 2A202603887 | anhtth.it.work@gmail.com | hnha02 | CP3: phát triển 4 tool mới, unit test, eval routing |
| 3 | Nguyễn Trọng Nghĩa | 2A202603835 | nghiatrongnguyen2304@gmail.com | trongnghia2304 | CP4: viết 10 eval case nhóm, chạy suite group, bảng B3 |

Danh sách chưa đầy đủ; bổ sung các thành viên khác theo thông tin thực tế. Không suy ra tài khoản GitHub cá nhân từ chủ sở hữu repo.

## Vũ Văn Bình — MSSV chưa cung cấp

### Phần việc phụ trách

- Cấu hình provider OpenAI, kiểm tra môi trường và chạy baseline v0.
- Tổng hợp version log, phân tích lỗi và báo cáo CP1 với hỗ trợ của Codex.

### Đóng góp cụ thể

- Chạy preflight với OpenAI và xác nhận model `gpt-4o-mini` theo kết quả Terminal đã trao đổi.
- Chạy pytest: 62 passed, 17 skipped, 0 failed.
- Chạy base eval v0: 20 case được đo, 14 pass, không có lỗi provider.
- Nhờ Codex đối chiếu run JSON, ghi version log và soạn phân tích 6 case lỗi. Codex chạy lại pytest offline và lưu output; chưa áp dụng thay đổi v1.

### Bằng chứng

- [Run v0](starter_v0/runs/v0_B_base_openai_20261110T180441850646.json).
- [Version log](starter_v0/artifacts/version_log.csv).
- [Output pytest được Codex chạy lại](starter_v0/analysis/cp1_pytest.txt).
- [Báo cáo nhóm](report/team/group_report.md), mục B1 và B2.
- [Báo cáo cá nhân tạm](report/team/CHUA_CO_MSSV_VuVanBinh.md); cần đổi tiền tố sang MSSV thật trước khi nộp.
- Commit kỹ thuật của cá nhân: chưa ghi nhận trong phần việc này; cần bổ sung sau khi commit thực tế.

## Trần Thị Hà Anh — 2A202603887

### Phần việc phụ trách

- Phụ trách CP3: xây dựng tool mới và unit test cho research agent.
- Hoàn thiện tool bắt buộc `github_search` và eval case kiểm tra routing/arguments.
- Thực hiện bonus ≥4 tool tự viết với `deduplicate_sources`, `compare_sources` và `filter_by_date`.
- Đăng ký tool trong `TOOL_FUNCTIONS`, khai báo schema trong `artifacts/tools.yaml` và cập nhật bằng chứng CP3/bonus trong báo cáo nhóm.

### Đóng góp cụ thể

- Viết code và `TOOL.md` cho bốn tool: `github_search`, `deduplicate_sources`, `compare_sources`, `filter_by_date`.
- Viết 12 unit test cho happy path, input xấu và failure path; mock HTTP GitHub để toàn bộ kiểm thử chạy offline.
- Chạy toàn bộ suite: 97 passed, 14 skipped, 0 failed; các test skip là challenge tùy chọn của tool starter.
- Thêm case `G01_github_repository_routing` vào `starter_v0/data/eval_group.json`.
- Hỗ trợ đưa run baseline `v0_B_base_openai_20261110T180640602946.json` vào repo.

### Bằng chứng

- Các commit `ff72034`, `21e9423`, `64abe65`, `fa038dc`; PR #2, merge commit `96196bd`.
- `starter_v0/tools/{github_search,deduplicate_sources,compare_sources,filter_by_date}/`.
- `starter_v0/tests/test_tools_todo.py`, `starter_v0/analysis/cp3_pytest.txt`.
- Báo cáo cá nhân: `report/team/2A202603887_TranThiHaAnh.md`.

## Nguyễn Trọng Nghĩa — 2A202603835

### Phần việc phụ trách

- CP4: viết bộ eval nhóm 10 case trong `starter_v0/data/eval_group.json`, chạy `--suite group` bằng provider thật và điền bảng B3.

### Đóng góp cụ thể

- Giữ case G01 của CP3 và viết thêm 9 case (G02–G10): tổng 5 single turn + 5 multi turn, mỗi case có `failure_type`, `expect`, `metadata.what_it_tests`.
- Phủ cả 4 tool mới của CP3 (`github_search`, `deduplicate_sources`, `filter_by_date`, `compare_sources`) và luồng xác nhận trước khi `send` (G04, G09).
- Validate schema bằng code của `run_eval.py`; `pytest` 97 passed, 14 skipped, 0 failed.
- Chạy suite group với OpenAI `gpt-4o-mini`: 10/10 case được đo, `provider_error_cases=0`, 10/10 PASS.
- Điền bảng B3 trong báo cáo nhóm, ghi chú lý do `prompt_hash`/`tools_hash` khác dòng v3.

### Bằng chứng

- [`starter_v0/data/eval_group.json`](starter_v0/data/eval_group.json).
- [Run group v3](starter_v0/runs/v3_B_group_openai_20261110T193821499328.json).
- Bảng B3 trong [báo cáo nhóm](report/team/group_report.md).
- Báo cáo cá nhân: [`report/team/2A202603835_NguyenTrongNghia.md`](report/team/2A202603835_NguyenTrongNghia.md).
- Commit `5d09b27` (nhánh `feat/check-point-4`); PR #3, merge commit `9fc3ddd`.
