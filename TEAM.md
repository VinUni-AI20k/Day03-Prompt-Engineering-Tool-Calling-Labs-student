# Team

## Thông tin nhóm

- Tên nhóm: MMV
- Lớp: L3B
- Repo nhóm: `https://github.com/caominhnguyen05/K5-L3B-DAY03-MMV-ResearchAgentToolEval`
- URL repo, nhánh nộp, commit chốt: `main`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |        |      |       |        |         |
|   2 |    Nguyễn Cao Minh    |   2A202604099   |  26ai.minhnc@vinuni.edu.vn     |  https://github.com/caominhnguyen05      |    Tạo các tool mới     |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## NguyenCaoMinh-2A202604099

### Phần việc phụ trách

- Tạo, viết test, và tạo rule cho 4 tool mới để xử lý dữ liệu đã thu thập của research agent
- Viết unit test cho các tool có sẵn trong `starter_v0/tests/test_tools_todo.py`.

### Đóng góp cụ thể

- Tạo 4 tool mới, mỗi tool ít nhất 3 test:

1. `deduplicate`: loại bỏ các kết quả trùng URL, bỏ phần fragment (`#...`) khi so sánh, giữ item xuất hiện đầu tiên và bảo toàn thứ tự.
2. `filter_sources`: lọc kết quả theo domain được cho phép hoặc bị chặn; hỗ trợ khớp domain chính xác và subdomain, trong đó danh sách chặn được ưu tiên.
3. `filter_by_date`: lọc kết quả theo khoảng ngày bao gồm cả ngày bắt đầu và ngày kết thúc; ghi rõ những item bị loại do nằm ngoài khoảng hoặc thiếu ngày hợp lệ.
4. `validate_citations`: kiểm tra cấu trúc trích dẫn của từng item, gồm tiêu đề, nguồn và URL HTTP/HTTPS hợp lệ.
- Viết unit test ở file `starter_v0/tests/test_tools_todo.py` cho các tool đã có sẵn trong repo.
- Viết `TOOL.md` cho từng tool theo đúng folder contract của repo, mô tả input, output, giới hạn và side effect.
- Khai báo tên, description và JSON schema của bốn tool trong `artifacts/tools.yaml` để model biết khi nào dùng tool và cách truyền arguments.
- Viết unit test cho happy path, input xấu, trường hợp biên và nhánh lỗi. Các test chạy offline và kiểm tra thêm việc giữ thứ tự, không sửa input, xử lý URL/domain/ngày không hợp lệ và báo lỗi theo đúng index.
- Thêm bốn eval case G01–G04 trong 1starter_v0/data/eval_group.json1 để kiểm tra model route đúng tới bốn tool mới và truyền đúng arguments.

### Bằng chứng

### File implementation và tài liệu

- `starter_v0/tools/deduplicate/tool.py`
- `starter_v0/tools/deduplicate/TOOL.md`
- `starter_v0/tools/filter_sources/tool.py`
- `starter_v0/tools/filter_sources/TOOL.md`
- `starter_v0/tools/filter_by_date/tool.py`
- `starter_v0/tools/filter_by_date/TOOL.md`
- `starter_v0/tools/validate_citations/tool.py`
- `starter_v0/tools/validate_citations/TOOL.md`

### File đăng ký, khai báo, test và eval

- `starter_v0/tools/__init__.py`: đăng ký bốn tool trong `TOOL_FUNCTIONS`.
- `starter_v0/artifacts/tools.yaml`: khai báo description và parameter schema cho bốn tool.
- `starter_v0/tests/test_tools_todo.py`: unit test cho bốn tool và các tool có sẵn.
- `starter_v0/data/eval_group.json`: các case `G01_deduplicate_collected_articles`, `G02_filter_sources`, `G03_filter_by_date`, `G04_validate_citations`.

### Commit

- Tên/hash commit: `6a46ed5`, `1c8679c`
