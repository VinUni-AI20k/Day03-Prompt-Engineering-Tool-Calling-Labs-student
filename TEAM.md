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
| 2 | Nguyễn Văn Minh | 2A202603771 | 26ai.minhnv7@vinuni.edu.vn | nguyenvanminh | Tool Engineer & Testing Specialist |

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

## NguyenVanMinh-2A202603771

### Phần việc phụ trách

- Nghiên cứu, thiết kế và phát triển 4 công cụ mở rộng (Custom Tools) cho Research Agent: `github_repo`, `pypi_package`, `wiki_summary`, `hn_search` (C4).
- Xây dựng hệ sinh thái 12 Unit Tests độc lập, cô lập 100% offline sử dụng fixture `fake_http` trong `starter_v0/tests/test_tools_todo.py` (C4).
- Kiểm soát và bảo đảm tính tuân thủ hợp đồng hệ thống, giữ cho suite kiểm tra hợp đồng `starter_v0/tests/test_tool_contract.py` luôn đạt 100% xanh (55/55 tests).
- Tham gia chạy thử nghiệm Baseline v0 với OpenRouter, phân tích các failure trace ban đầu.

### Đóng góp cụ thể

- Hiện thực hóa 4 tools kèm tài liệu `TOOL.md` đặc tả schema, đăng ký tập trung vào `starter_v0/tools/__init__.py`.
- Áp dụng nguyên tắc lập trình phòng thủ: không bao giờ raise uncaught exception, validate tham số trước khi request, bóc tách URL và chuẩn hóa input lỏng từ LLM.
- Viết 12 test cases bao phủ happy path, input rỗng/sai định dạng và mã lỗi HTTP 404 (đạt 12/12 PASSED, 0 failed).
- Phối hợp đồng bộ hóa schema 4 công cụ mới vào `tools.yaml` để nhóm đánh giá mở rộng.

### Bằng chứng

- Báo cáo cá nhân chi tiết: `report/team/2A202603771_NguyenVanMinh.md`.
- Code & Unit tests:
  - `starter_v0/tools/github_repo/` (`tool.py`, `TOOL.md`)
  - `starter_v0/tools/pypi_package/` (`tool.py`, `TOOL.md`)
  - `starter_v0/tools/wiki_summary/` (`tool.py`, `TOOL.md`)
  - `starter_v0/tools/hn_search/` (`tool.py`, `TOOL.md`)
  - `starter_v0/tools/__init__.py`
  - `starter_v0/tests/test_tools_todo.py`
- Kết quả kiểm thử: `pytest tests/test_tools_todo.py`: 12 passed; `pytest tests/test_tool_contract.py`: 55 passed.
