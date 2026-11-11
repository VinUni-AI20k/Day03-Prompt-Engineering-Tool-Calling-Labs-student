# Team

## Thông tin nhóm

- **Tên nhóm:** H7
- **Lớp:** L3B
- **Repo nhóm:** `K5-L3B-DAY03-H7-ResearchAgentToolEval`
- **URL repo:** [github.com/Ngochung1772k4/K5-L3B-DAY03-H7-ResearchAgentToolEval](https://github.com/Ngochung1772k4/K5-L3B-DAY03-H7-ResearchAgentToolEval)
- **Nhánh đang hoàn thiện:** `feature/2a202603770-buingochung-cp1-2`
- **Commit CP4–CP5:** `df4fe42` (UI/chat, Bùi Ngọc Hùng) và `64a8fb1` (hardening transcript, regression test, Phạm Minh Đức; fast-forward merge vào nhánh này).
- **Nhánh đã push:** `feature/2a202603770-buingochung-cp1-2`. Commit `d03674e` bổ sung CP4 eval, cập nhật báo cáo và lưu kết quả test sau merge. PR vào `main` và link demo public vẫn còn chờ.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
| 1 | Bùi Ngọc Hùng | 2A202603770 | 26ai.hungbn@vinuni.edu.vn | Ngochung1772k4 | CP1–CP2; UI/chat CP4–CP5; thử nghiệm prompt/tool và bonus |
| 2 | Trương Đức Phát | 2A202603757 | 26ai.phattd@vinuni.edu.vn | trdphat | CP3; tool `dedupe_sources`, đăng ký tool và unit test |
| 3 | Phạm Minh Đức | 2A202603758 | 26ai.ducpm@vinuni.edu.vn | ducpham13 | CP4–CP5; harden lưu transcript và regression test |

## Phân công và bằng chứng

### Bùi Ngọc Hùng — 2A202603770

- **Phần việc:** CP1–CP2, giao diện/chat CP4–CP5 và bonus.
- **Đóng góp:** thiết lập baseline; tối ưu prompt và mô tả tool qua v0–v3; chạy eval OpenRouter; triển khai UI/chat và transcript ban đầu; thực hiện thử nghiệm model local và các hạng mục bonus được ghi trong báo cáo nhóm.
- **Bằng chứng:** `report/team/2A202603770_BuiNgocHung.md`, `starter_v0/artifacts/version_log.csv`, các run v0–v3 và run bonus trong `starter_v0/runs/`, transcript Telegram trong `starter_v0/transcripts/`; commit CP1–CP2 `2da7e6e`, bonus `18a6c20`, UI/chat `df4fe42`.

### Trương Đức Phát — 2A202603757

- **Phần việc:** CP3.
- **Đóng góp:** cài đặt `dedupe_sources`, viết `TOOL.md`, đăng ký tool, bổ sung unit test và tham gia eval nhóm.
- **Bằng chứng:** `report/team/2A202603757_TruongDucPhat.md`, `starter_v0/tools/dedupe_sources/`, `starter_v0/tests/test_tools_todo.py`, commit `026d18b`.

### Phạm Minh Đức — 2A202603758

- **Phần việc:** CP4–CP5; tăng độ bền của lưu transcript và kiểm thử hồi quy.
- **Đóng góp:** rà soát `write_transcript()`, ghi JSON qua file tạm rồi thay thế file đích; thêm hai regression test cho phản hồi thành công và lỗi provider. Phần UI/transcript ban đầu do Bùi Ngọc Hùng triển khai.
- **Bằng chứng:** `report/team/2A202603758_PhamMinhDuc.md`, `starter_v0/chat.py`, `starter_v0/tests/test_chat_transcripts.py`, commit `64a8fb1` trên nhánh `feature/2a202603758-phamminhduc-cp4-5` (đã fast-forward merge local, push chờ).

## Báo cáo cá nhân

- `report/team/2A202603770_BuiNgocHung.md`
- `report/team/2A202603757_TruongDucPhat.md`
- `report/team/2A202603758_PhamMinhDuc.md`
