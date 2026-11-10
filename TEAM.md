# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A / L3B
- Repo nhóm: `K5-L3A-DAY03-TenNhom-ResearchAgentToolEval` hoặc `K5-L3B-DAY03-TenNhom-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
| 1 | Hồ An Lộc | 2A202603743 | 26ai.locha@vinuni.edu.vn | hoanloc | Eval nhóm, UI, báo cáo |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## HoAnLoc-2A202603743

### Phần việc phụ trách

- Thiết kế & thực thi bộ 10 ca kiểm thử nhóm `starter_v0/data/eval_group.json` (5 single-turn + 5 multi-turn) (C5).
- Xây dựng ứng dụng Streamlit trong `starter_v0/app.py` hiển thị chi tiết tool calls và tham số (C6).
- Đồng phụ trách tối ưu hóa Prompt và Tool Declarations qua các vòng lặp v0 → v1 → v2 → v3 (C1, C2, C3).
- Hoàn thiện tài liệu Báo cáo Nhóm `report/team/group_report.md` và thiết kế `report/team/poster.html` (C7).
- Cấu hình và kiểm thử tích hợp gửi tin thật lên Telegram Channel sau xác nhận (Bonus).

### Đóng góp cụ thể

- Phân tích 7 ca lỗi baseline v0; thiết kế các quy tắc no-tool, clarify và ranh giới guardrail an toàn trong `system_prompt.md`.
- Chuẩn hóa toàn bộ schema `tools.yaml` với mô tả rõ ràng ranh giới khi nào dùng/không dùng và ràng buộc tham số.
- Thiết kế 10 ca eval nhóm chất lượng cao bẫy các lỗi phổ biến (tính toán, đa lượt chuyển nguồn, từ chối ngoài phạm vi, hỏi xác nhận gửi tin).
- Viết ứng dụng Streamlit trực quan, minh bạch toàn bộ các lượt gọi công cụ và tham số cho buổi Showdown.

### Bằng chứng

- Báo cáo cá nhân chi tiết: `report/team/2A202603743_HoAnLoc.md`.
- Code & cấu hình: `starter_v0/data/eval_group.json`, `starter_v0/app.py`, `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/artifacts/version_log.csv`.
- Runs & Transcripts: `starter_v0/runs/v3_B_base_openai_20261110T175327809168.json`, `starter_v0/runs/v3_B_group_openai_20261110T183722324187.json`, `starter_v0/transcripts/v3_openai_20261110T182210209855.transcript.json`, `starter_v0/transcripts/v3_openai_20261110T205941151454.transcript.json` (Bonus Telegram).
