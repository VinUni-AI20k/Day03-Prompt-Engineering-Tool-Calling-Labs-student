# Báo cáo cá nhân — Nguyễn Văn Minh (2A202603771)

## 1. Thông tin thành viên

- Họ tên: Nguyễn Văn Minh
- MSSV: 2A202603771
- Email: 26ai.minhnv7@vinuni.edu.vn
- Vai trò trong nhóm: **Thành viên B — Tool Engineer & Unit Testing Specialist**

---

## 2. Phần việc phụ trách

Theo phân công trong kế hoạch làm việc nhóm và Rubric đánh giá (Tiêu chí C4 & Checkpoint 3):
- **Nghiên cứu, thiết kế và phát triển các công cụ mở rộng (Custom Tools)** cho Research Agent: Đảm bảo agent có khả năng tra cứu chuyên sâu ngoài các công cụ cơ bản của starter kit.
- **Hiện thực hóa 4 công cụ mới hoàn chỉnh** theo đúng hợp đồng thiết kế (`tool_contracts.md`):
  1. `github_repo`: Lấy thông tin chi tiết một repo GitHub (stars, forks, open issues, language, license, README) qua GitHub REST API.
  2. `pypi_package`: Lấy thông tin package Python trên PyPI (version mới nhất, yêu cầu Python, license, ngày release, lệnh cài đặt `pip install`) qua PyPI JSON API.
  3. `wiki_summary`: Tóm tắt các khái niệm, định nghĩa, thực thể bách khoa toàn thư qua Wikimedia REST API.
  4. `hn_search`: Tìm kiếm các bài thảo luận, câu chuyện công nghệ trên Hacker News qua Algolia API với các bộ lọc `timeframe` và sắp xếp `sort=relevance|date`.
- **Xây dựng bộ Unit Test độc lập và cô lập (Isolated Offline Testing)**: Viết tối thiểu 3 test/tool trong `tests/test_tools_todo.py` sử dụng mock HTTP (`fake_http`), đảm bảo kiểm thử toàn diện các nhánh hành vi (happy path, input xấu, xử lý lỗi HTTP).
- **Đăng ký tập trung và kiểm chuẩn hợp đồng**: Đồng bộ hóa toàn bộ các hàm vào registry `starter_v0/tools/__init__.py` và giữ cho suite kiểm tra hợp đồng `tests/test_tool_contract.py` luôn đạt 100% xanh.
- **Phối hợp thực hiện đo đạc Baseline v0**: Tham gia chạy thử nghiệm đánh giá ban đầu với OpenRouter (`openai/gpt-4o-mini`), phân tích các failure patterns của starter code.

---

## 3. Đóng góp cụ thể

1. **Kiến trúc và Triển khai Code 4 Tools (`starter_v0/tools/`)**:
   - Tạo đầy đủ 4 thư mục với cấu trúc chuẩn gồm `tool.py` (logic thực thi) và `TOOL.md` (metadata frontmatter mô tả input/output/provider):
     - `tools/github_repo/`: Hỗ trợ tự động bóc tách URL `https://github.com/owner/name` thành `owner/name`, kiểm tra regex format hợp lệ trước khi gửi request.
     - `tools/pypi_package/`: Tự động làm sạch input (loại bỏ tiền tố `pip install`, tách version `==`), map trường license và sinh lệnh cài đặt chuẩn.
     - `tools/wiki_summary/`: Tự động chuẩn hóa khoảng trắng thành `_`, encode URL, gửi kèm header `User-Agent` hợp lệ theo chính sách của Wikimedia Foundation, nhận diện trang định hướng (`disambiguation`).
     - `tools/hn_search/`: Xử lý ép kiểu an toàn cho `limit` (kẹp trong khoảng 1–20), tính toán timestamp Unix tự động theo `timeframe` (`day`, `week`, `month`, `year`) để áp dụng `numericFilters`.
2. **Áp dụng Nguyên Tắc Lập Trình Phòng Thủ (Defensive Programming)**:
   - **Tuyệt đối không để xảy ra unhandled exception**: Mọi hàm đều bọc trong khối `try...except Exception` và sử dụng hàm tiện ích `err(tool, exc)` từ `_shared.py` để trả về dictionary chứa thông tin lỗi rõ ràng thay vì làm crash luồng của agent.
   - **Xác thực dữ liệu trước khi gọi mạng (Pre-validation)**: Input rỗng hoặc sai cú pháp sẽ lập tức bị chặn và trả về lỗi nghiệp vụ (`invalid_repo`, `invalid_package`, `invalid_title`, `invalid_query`) mà không tiêu tốn tài nguyên mạng.
3. **Phát triển 12 Unit Tests Chuyên Biệt trong `tests/test_tools_todo.py`**:
   - Viết trọn vẹn 12 test cases (3 tests cho mỗi tool), kiểm tra chặt chẽ cả:
     - **Request gửi đi**: Kiểm tra endpoint URL, headers (`User-Agent`), tham số query params (`hitsPerPage`, `numericFilters`).
     - **Dữ liệu trả về**: Kiểm tra tính chính xác của các trường dữ liệu được map và logic format string.
     - **Kịch bản biên & lỗi**: Kiểm tra mã lỗi HTTP 404 trả về dictionary lỗi `not_found`, kiểm tra input không hợp lệ trả về `invalid_*`.
   - Kết quả: Toàn bộ **12/12 unit tests đều PASSED**, không có lỗi nào phát sinh.
4. **Kiểm chuẩn và Quản lý Phiên bản**:
   - Giữ cho bộ contract test `tests/test_tool_contract.py` luôn đạt **55/55 tests PASSED**.
   - Thực hiện commit kỹ thuật rõ ràng, chuẩn hóa lịch sử commit trên nhánh `2A202603771_NguyenVanMinh`.

---

## 4. Bằng chứng

- **Lịch sử Commit & Nhánh Git**:
  - Nhánh làm việc: `2A202603771_NguyenVanMinh` trên repository nhóm.
  - Commit chính: `95b3981` (*"CP4 4 tool succes"*) và các commit cập nhật kiểm thử:
    - Bổ sung 4 thư mục tool (`github_repo`, `pypi_package`, `wiki_summary`, `hn_search`).
    - Cập nhật file đăng ký tổng `starter_v0/tools/__init__.py`.
    - Bổ sung 12 tests trong `starter_v0/tests/test_tools_todo.py`.
- **Tập tin sản phẩm cụ thể**:
  - `starter_v0/tools/github_repo/tool.py` & `TOOL.md`
  - `starter_v0/tools/pypi_package/tool.py` & `TOOL.md`
  - `starter_v0/tools/wiki_summary/tool.py` & `TOOL.md`
  - `starter_v0/tools/hn_search/tool.py` & `TOOL.md`
  - `starter_v0/tools/__init__.py`
  - `starter_v0/tests/test_tools_todo.py`
  - `starter_v0/runs/v0_B_base_openrouter_20261110T174158381674.json`
- **Kết quả chạy Test thực tế**:
  - `pytest tests/test_tools_todo.py -k "github_repo or pypi_package or wiki_summary or hn_search"`: **12 passed, 0 failed**.
  - `pytest tests/test_tool_contract.py`: **55 passed, 0 failed**.
- **Công cụ AI và phương pháp kiểm chứng**:
  - Sử dụng trợ lý AI Antigravity để đối chiếu schema JSON với docstrings, sinh mock response cho fixture `fake_http`.
  - Tự kiểm chứng: Phân tích failure trace khi test `wiki_summary` phát hiện lệch ký tự nối giữa `_` (URL path) và `-` (tên bài viết), qua đó tinh chỉnh assertion và code xử lý chuỗi khớp 100% với đặc tả Wikimedia.

---

## 5. Tự đánh giá

- **Mức độ hoàn thành công việc:** **100% / Xuất sắc**
  - Đã hoàn thành vượt chỉ tiêu bắt buộc của Rubric C4: Tự thiết kế và hiện thực hóa thành công **4 công cụ mới** (vượt yêu cầu tối thiểu là 1 công cụ) với đầy đủ tài liệu `TOOL.md` và 12 unit tests hoàn toàn xanh sạch.
  - Sẵn sàng cung cấp các tool hoàn chỉnh để các thành viên khác trong nhóm tích hợp vào vòng lặp prompt `v3` và bộ đánh giá `eval_group.json`.
- **Điểm tự chấm cho đóng góp cá nhân (Tiêu chí C8):** **10/10**
