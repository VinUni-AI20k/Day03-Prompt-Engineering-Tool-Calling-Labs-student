# Báo cáo cá nhân — Trần Thị Hà Anh — 2A202603887

## 1. Thông tin thành viên

- Họ tên: Trần Thị Hà Anh
- MSSV: 2A202603887
- Email: anhtth.it.work@gmail.com
- GitHub: `hnha02`

## 2. Phần việc phụ trách

- Phụ trách CP3: thiết kế, cài đặt và kiểm thử tool mới cho research agent.
- Hoàn thiện tool bắt buộc `github_search`, gồm code, `TOOL.md`, đăng ký registry, khai báo schema và eval routing.
- Thực hiện bonus “Hơn 3 tool mới” bằng ba tool xử lý nguồn cục bộ: `deduplicate_sources`, `compare_sources` và `filter_by_date`.
- Viết unit test offline cho bốn tool và bổ sung bằng chứng CP3/bonus vào báo cáo nhóm.
- Hỗ trợ đưa run baseline v0 vào repo để nhóm lưu bằng chứng thực nghiệm.

## 3. Đóng góp cụ thể

### 3.1. Tool `github_search`

- Tìm repository GitHub công khai theo từ khóa.
- Hỗ trợ lọc theo ngôn ngữ, sắp xếp theo độ liên quan/số sao/số fork/thời gian cập nhật và giới hạn số kết quả.
- Validate query, enum và limit; lỗi input hoặc HTTP được trả về dưới dạng error dict thay vì làm agent crash.
- Thêm một eval case kiểm tra routing và arguments: `query`, `language`, `sort`, `limit`.

### 3.2. Ba tool bonus

- `deduplicate_sources`: loại nguồn trùng theo URL chuẩn hóa hoặc tiêu đề, giữ nguyên thứ tự nguồn xuất hiện đầu tiên và báo lý do loại.
- `compare_sources`: so sánh metadata của ít nhất hai nguồn, tính độ đầy đủ và chỉ ra trường nào giống hoặc khác nhau mà không tự phán đoán độ đúng sai.
- `filter_by_date`: lọc nguồn theo khoảng ngày ISO bao gồm hai biên, hỗ trợ nhiều trường ngày và ghi rõ lý do loại nguồn.
- Cả ba tool chạy local, không cần API key, không gọi mạng và không tạo side effect.

### 3.3. Kiểm thử và tích hợp

- Đăng ký đủ bốn tool trong `TOOL_FUNCTIONS` và `artifacts/tools.yaml`.
- Viết 12 test function, tối thiểu 3 test/tool: happy path, input xấu và failure path.
- Test HTTP của GitHub được mock hoàn toàn; các test không dùng API thật và không tốn credit.
- Chạy lại toàn bộ suite ngày 10/11/2026: **97 passed, 14 skipped, 0 failed**. Các test skip còn lại là challenge tùy chọn cho tool có sẵn của starter.

## 4. Bằng chứng

### File

- [Tool GitHub](../../starter_v0/tools/github_search/tool.py) và [TOOL.md](../../starter_v0/tools/github_search/TOOL.md).
- [Tool loại nguồn trùng](../../starter_v0/tools/deduplicate_sources/tool.py) và [TOOL.md](../../starter_v0/tools/deduplicate_sources/TOOL.md).
- [Tool so sánh nguồn](../../starter_v0/tools/compare_sources/tool.py) và [TOOL.md](../../starter_v0/tools/compare_sources/TOOL.md).
- [Tool lọc theo ngày](../../starter_v0/tools/filter_by_date/tool.py) và [TOOL.md](../../starter_v0/tools/filter_by_date/TOOL.md).
- [Registry](../../starter_v0/tools/__init__.py) và [tool declarations](../../starter_v0/artifacts/tools.yaml).
- [Unit tests](../../starter_v0/tests/test_tools_todo.py).
- [Eval routing](../../starter_v0/data/eval_group.json), case `G01_github_repository_routing`.
- [Kết quả pytest CP3](../../starter_v0/analysis/cp3_pytest.txt).
- [Run baseline v0 đã đưa vào repo](../../starter_v0/runs/v0_B_base_openai_20261110T180640602946.json).

### Commit/PR

- `ff72034` — hoàn thành tool mới bắt buộc, unit test, registry, declaration, eval và bằng chứng CP3.
- `21e9423` — bổ sung ba tool và chín unit test để đạt bonus ≥4 tool tự viết.
- `64abe65` — bổ sung/đồng bộ code và `TOOL.md` của bốn tool CP3.
- `fa038dc` — đưa run baseline v0 vào repo.
- PR [#2 — tranthihaanh](https://github.com/trongnghia2304/K5-L3B-DAY03-Hehehe-ResearchAgentToolEval/pull/2), merge commit `96196bd`.

### AI/công cụ và cách tự kiểm tra

- Dùng Codex hỗ trợ rà yêu cầu CP3, soạn code, test và phần bằng chứng báo cáo.
- Tự kiểm tra bằng `pytest -v`, `pytest tests/test_tool_contract.py -v` và đối chiếu `tools.yaml` với chữ ký hàm trong registry.
- Kiểm tra các test API dùng mock HTTP, không phụ thuộc mạng hoặc API key thật.
- Đọc lại output và các nhánh lỗi để bảo đảm tool trả error dict thay vì phát sinh exception ra agent.

## 5. Tự đánh giá

Phần việc CP3 đã đáp ứng yêu cầu bắt buộc và tiêu chí bonus ≥4 tool mới: mỗi tool có code, `TOOL.md`, registry, declaration và ít nhất ba unit test. Điểm mạnh của phần triển khai là validate input rõ ràng, kiểm thử offline và ba tool xử lý nguồn không có side effect. Hạn chế hiện tại là `data/eval_group.json` mới có một case cho `github_search`; việc hoàn thiện đủ 10 case thuộc CP4 và cần phối hợp với phần eval nhóm. Ngoài ra, 14 test challenge của các tool starter vẫn đang được skip và không thuộc phạm vi CP3 bắt buộc.
