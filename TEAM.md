# Team

## Thông tin nhóm

- Tên nhóm: MMV
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-MMV-ResearchAgentToolEval`
- URL repo, nhánh nộp, commit chốt: https://github.com/caominhnguyen05/K5-L3B-DAY03-MMV-ResearchAgentToolEval · nhánh `main` · commit chốt: `9bdc382`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
| 1 | Phạm Hoàng Đức Minh | 2A202604114 | ducminh03102005@gmail.com | https://github.com/PH31M | Prompt và eval, chạy run/transcript, tổng hợp B1–B5a |
| 2 | Nguyễn Cao Minh | 2A202604099 | 26ai.minhnc@vinuni.edu.vn | https://github.com/caominhnguyen05 | 4 tool xử lý dữ liệu đã thu thập và unit test |
| 3 | Nguyễn Công Huy | 2A202604086 | conghuycr@gmail.com | https://github.com/HyperSyst | 2 tool tìm bài báo khoa học (`openalex`, `semantic_scholar`) |
| 4 | Tào Quang Vinh | 2A202604081 | qvinhh2312@gmail.com | https://github.com/qvinhh2312 | UI Streamlit, Cloudflare Tunnel, Phần A báo cáo nhóm |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Tóm tắt đóng góp theo báo cáo cá nhân và bằng chứng trong repo.

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
- Thêm bốn eval case G01–G04 trong `starter_v0/data/eval_group.json` để kiểm tra model route đúng tới bốn tool mới và truyền đúng arguments.

### Bằng chứng

### File implementation và tài liệu

- `starter_v0/tools/deduplicate/`
- `starter_v0/tools/filter_sources/`
- `starter_v0/tools/filter_by_date/`
- `starter_v0/tools/validate_citations/`

### File đăng ký, khai báo, test và eval

- `starter_v0/tools/__init__.py`: đăng ký bốn tool trong `TOOL_FUNCTIONS`.
- `starter_v0/artifacts/tools.yaml`: khai báo description và parameter schema cho bốn tool.
- `starter_v0/tests/test_tools_todo.py`: unit test cho bốn tool và các tool có sẵn.
- `starter_v0/data/eval_group.json`: các case `G01_deduplicate_collected_articles`, `G02_filter_sources`, `G03_filter_by_date`, `G04_validate_citations`.

### Commit

- Tên/hash commit: `6a46ed5`, `1c8679c`

## Phạm Hoàng Đức Minh - 2A202604114

### Phần việc phụ trách

- Chạy baseline v0, tối ưu `system_prompt.md` và `tools.yaml` qua v1–v7, ghi `version_log.csv`.
- Viết bộ 10 eval case của nhóm (`data/eval_group.json`) để route tới cả 6 tool mới.
- Viết unit test cho `openalex` và `semantic_scholar`, sửa lỗi đăng ký tool `semantic_scholar`.
- Chạy 3 phiên chat live bằng `chat.py` và điền các bảng B1–B5a của `group_report.md`.
- Tích hợp (merge) các nhánh của các thành viên vào `optimize`.

### Đóng góp cụ thể

- Baseline v0 14/20 và bảng phân tích lỗi B2; 7 vòng tối ưu có giả thuyết, hash và metric trước/sau (v3 giảm điểm và v6 không xác nhận giả thuyết đều được ghi nguyên trạng).
- Bộ eval nhóm 10 case (5 single, 5 multi), run group 10/10 hợp lệ.
- 31 unit test mới (14 cho `openalex`, 17 cho `semantic_scholar`); toàn suite `pytest` 213 passed, 0 skipped.
- 3 transcript live: yêu cầu thường, thiếu thông tin rồi bổ sung, yêu cầu gửi có xác nhận.

### Bằng chứng

- Commit: `2f25a54`, `f60e41e`, `f893bbc`, `bbc847c`, `f29fd57`, `5fb6e01` và các commit merge trên `optimize`.
- Chi tiết: [report/team/2A202604114_PhamHoangDucMinh.md](report/team/2A202604114_PhamHoangDucMinh.md).
## NguyenCongHuy-2A202604086

### Phần việc phụ trách

- Xây dựng hai tool tìm kiếm học thuật `openalex` và `semantic_scholar`.

### Đóng góp cụ thể

- Triển khai tool và `TOOL.md`, chuẩn hóa dữ liệu bài báo (tiêu đề, tác giả, abstract, DOI, năm, trích dẫn và PDF nếu có), xử lý lỗi API/timeout và giới hạn kết quả.
- Viết test cho happy path, input không hợp lệ và lỗi API; đóng góp được mô tả trong `report/team/2A202604086_NguyenCongHuy.md`.

### Bằng chứng

- `starter_v0/tools/openalex/`, `starter_v0/tools/semantic_scholar/`, `starter_v0/artifacts/tools.yaml`, `starter_v0/tools/__init__.py`.
## TaoQuangVinh-2A202604081

### Phần việc phụ trách

- UI Streamlit, chốt xác nhận cho tool có tác dụng phụ, launcher Cloudflare Tunnel và Phần A báo cáo nhóm.

### Đóng góp cụ thể

- Xây dựng `starter_v0/app.py`, `starter_v0/ui_core.py`; viết test offline trong `starter_v0/tests/test_ui_core.py` và `starter_v0/tests/test_app_ui.py`; tạo `starter_v0/scripts/run_ui.ps1` và `starter_v0/scripts/run_ui.sh`.
- Chốt xác nhận UI ghi `ui_gate`; lớp này bổ sung cho boundary chính trong prompt và khai báo tool. Soạn A1–A3 và bảng A2.

### Bằng chứng

- Các commit UI/deploy trên `feat/ui-report`: `3bc365b`, `7d9bc2b`, `1df1a9e`, `9915721`, `36c4084`, `2c64780`, `3b4d2ae`, `de0c21d`, `69ed595`, `feeea4f`.
- Báo cáo cá nhân: [`report/team/2A202604081_TaoQuangVinh.md`](report/team/2A202604081_TaoQuangVinh.md).
