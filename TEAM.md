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
