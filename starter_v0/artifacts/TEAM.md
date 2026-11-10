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

1. Xây dựng tool weather
- Viết implementation tại starter_v0/tools/weather/tool.py.
- Tích hợp Open-Meteo để tìm tọa độ địa điểm và lấy dữ liệu thời tiết hiện tại.
- Hỗ trợ tên thành phố, mã quốc gia và đơn vị nhiệt độ Celsius/Fahrenheit.
- Trả về nhiệt độ, nhiệt độ cảm nhận, độ ẩm, tốc độ gió, trạng thái thời tiết, thời điểm dữ liệu và URL nguồn.
- Xử lý địa danh trùng tên: ưu tiên tên khớp chính xác và kết quả thủ đô được API xác định; trả danh sách lựa chọn nếu vẫn chưa xác định được địa điểm.
- Kiểm tra đầu vào và xử lý các trường hợp không tìm thấy địa điểm, timeout, lỗi HTTP hoặc dữ liệu API không hợp lệ.
- Chuẩn hóa kết quả thành items để sử dụng với tool format.
2. Xây dựng tool github_search
- Viết implementation tại starter_v0/tools/github_search/tool.py.
- Tích hợp GitHub REST API để tìm kiếm repository công khai.
- Hỗ trợ truy vấn theo chủ đề, ngôn ngữ, owner và số sao bằng cú pháp tìm kiếm GitHub.
- Hỗ trợ sắp xếp theo mức độ liên quan, stars, forks hoặc thời điểm cập nhật; giới hạn từ 1 đến 10 kết quả.
- Trả về tên repository, mô tả, URL, stars, forks, ngôn ngữ, license, topics và ngày cập nhật.
- Hỗ trợ GITHUB_TOKEN tùy chọn; token được gửi trong header.
- Kiểm tra tham số đầu vào, xử lý lỗi API và loại bỏ kết quả riêng tư hoặc thiếu thông tin cần thiết.
3. Viết tài liệu cho hai tool
Hoàn thiện hai file:
- starter_v0/tools/weather/TOOL.md
- starter_v0/tools/github_search/TOOL.md
Tài liệu gồm frontmatter đúng contract, chức năng, trường hợp sử dụng, tham số, kết quả trả về, cách xử lý lỗi, ví dụ gọi tool và liên kết tài liệu API.
4. Đăng ký và tích hợp vào agent
- Đăng ký hai hàm trong TOOL_FUNCTIONS tại starter_v0/tools/__init__.py.
- Bổ sung schema trong starter_v0/artifacts/tools.yaml, gồm mô tả chức năng, quy tắc chọn tool, tham số bắt buộc, giá trị mặc định và giới hạn đầu vào.
5. Đóng góp tài liệu và báo cáo
- Bổ sung hai tool vào bảng A2 – Tool agent có trong starter_v0/artifacts/REPORT.md.

## Phạm vi phần Nguyễn Trung Duy - 2A202603387

- `deduplicate`: lọc URL trùng sau khi chuẩn hóa tracking/fragment, giữ nguồn đầu tiên; không so sánh nội dung bài viết.
- `citation_audit`: kiểm tra thiếu `title`, `source`, `url`, URL sai hoặc trùng; không kiểm chứng sự thật hay độ tin cậy của nguồn.
- Test riêng `tests/test_person3.py`: **26 passed** ở lần kiểm tra khi cập nhật B5. Không dùng kết quả này thay điểm eval hay kết quả test toàn nhóm.
- Viết `TOOL.md`, đăng ký hàm trong `tools/__init__.py` và khai báo schema trong `artifacts/tools.yaml` cho hai tool mới.
- Phụ trách mô tả hai tool tại A2 và bằng chứng tại B5 trong `artifacts/REPORT.md`.

## Phạm vi phần Lê Xuân Hà - 2A202603571



## Phạm vi phần Đỗ Minh Hoàng - 2A202603554
