# Thông tin nhóm và phân công công việc

- **Tên nhóm:** DoMinhHoang
- **Bài tập:** Day 03 — Research Agent Tool Evaluation
- **Repository:** [K5-L3-DAY03-DoMinhHoang-2A202603554-ResearchAgentToolEval](https://github.com/worryveem/K5-L3-DAY03-DoMinhHoang-2A202603554-ResearchAgentToolEval)

## Thành viên

| STT | Họ và tên | Mã học viên | Vai trò |
|---|---|---|---|
| 1 | Phạm Đức Hồng Đức | 2A202603558 | Agent Core, Prompt & Tool Spec |
| 2 | Đỗ Minh Hoàng | 2A202603554 | UI & Live Application |
| 3 | Vũ Đức Tâm | 2A202603522 | Tool Coder A — weather, github_search |
| 4 | Lê Xuân Hà | 2A202603571 | Testing & Eval Suite |
| 5 | Nguyễn Trung Duy | 2A202603387 | Tool Coder B — deduplicate, citation_audit |


## Phân công công việc

| Phân công | Người phụ trách | Công việc chính | File / sản phẩm bàn giao | Đóng góp báo cáo |
|---|---|---|---|---|
| Agent Core, Prompt & Tool Spec | Phạm Đức Hồng Đức | Viết rules routing; quy định khi nào clarify/search; tối ưu mô tả tool và tham số; quản lý các vòng eval v0 → v1 → v2 → v3 | `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `runs/*.json`, `artifacts/version_log.csv` | B1 — Version Evidence |
| Tool Coder A | Vũ Đức Tâm | Viết hai tool `weather`, `github_search`; xử lý đầu vào/lỗi; viết tài liệu và đăng ký tool | `tools/weather/`, `tools/github_search/`, `tools/__init__.py`, khai báo trong `artifacts/tools.yaml` | A2 — Danh sách tool |
| Tool Coder B | Nguyễn Trung Duy | Viết `deduplicate`, `citation_audit`; xử lý đầu vào/lỗi; viết tài liệu, đăng ký tool và kiểm thử | `tools/deduplicate/`, `tools/citation_audit/`, `tests/test_person3.py`, đăng ký trong `tools/__init__.py` và schema trong `artifacts/tools.yaml` | A2 — Hai tool mới; B5 — Bonus Evidence |
| Testing & Eval Suite | Lê Xuân Hà | Hoàn thiện unit test cho tool toàn nhóm, tối thiểu 3 test/tool; mock network; viết 10 case eval gồm 5 single-turn và 5 multi-turn; phân tích lỗi thực tế | `tests/test_tools_todo.py`, các file test liên quan, `data/eval_group.json`, kết quả pytest/eval | B2 — Failure Analysis; B3 — Team Eval Cases |
| UI & Live Application | Đỗ Minh Hoàng | Phụ trách giao diện chat; hiển thị tool call và kết quả Markdown; tạo transcript từ chạy thực tế | UI của nhóm, `transcripts/*.transcript.json` | A1 — Giới thiệu; A3 — Câu hỏi mẫu; B4 — Live Chat Evidence |

## Phạm vi phần Phạm Đức Hồng Đức - 2A202603558


## Phạm vi phần Vũ Đức Tâm - 2A202603522

## Phạm vi phần Nguyễn Trung Duy - 2A202603387

- `deduplicate`: lọc URL trùng sau khi chuẩn hóa tracking/fragment, giữ nguồn đầu tiên; không so sánh nội dung bài viết.
- `citation_audit`: kiểm tra thiếu `title`, `source`, `url`, URL sai hoặc trùng; không kiểm chứng sự thật hay độ tin cậy của nguồn.
- Test riêng `tests/test_person3.py`: **26 passed** ở lần kiểm tra khi cập nhật B5. Không dùng kết quả này thay điểm eval hay kết quả test toàn nhóm.
- Viết `TOOL.md`, đăng ký hàm trong `tools/__init__.py` và khai báo schema trong `artifacts/tools.yaml` cho hai tool mới.
- Phụ trách mô tả hai tool tại A2 và bằng chứng tại B5 trong `artifacts/REPORT.md`.

## Phạm vi phần Lê Xuân Hà - 2A202603571



## Phạm vi phần Đỗ Minh Hoàng - 2A202603554
