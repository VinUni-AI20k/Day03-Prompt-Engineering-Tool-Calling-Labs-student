# Team

## Thông tin nhóm

- Tên nhóm: Nhóm L3B - VuXuanBach & NguyenHoangTrung
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-VuXuanBach-2A202603803-ResearchAgentToolEval`
- URL repo, nhánh nộp, commit chốt: https://github.com/bachvx1709/K5-L3B-DAY03-VuXuanBach-2A202603803-ResearchAgentToolEval.git (nhánh: NguyenHoangTrung)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Vũ Xuân Bách | 2A202603803 | bachvx@example.com | bachvx1709 | Leader, Eval & Report |
|   2 | Nguyễn Hoàng Trung | 2A202603826 | 26ai.trungnh@vinui.edu.vn | trungtk03 | CP3: Custom Tool & Unit Tests |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

## NguyenHoangTrung-CP3

### Phần việc phụ trách

- Phụ trách toàn diện **Checkpoint 3 (CP3: Tool mới và unit test)**.
- Thiết kế, phát triển và tích hợp tool mới `source_credibility` (đánh giá độ tin cậy và phân cấp nguồn tin web).
- Đăng ký tool trong `starter_v0/tools/__init__.py` và khai báo trong `starter_v0/artifacts/tools.yaml`.
- Viết và hoàn thiện trọn bộ unit test trong `starter_v0/tests/test_tools_todo.py`, bao gồm các test cho tool mới và giải quyết tất cả stubs (đạt **0 skipped, 0 failed** trên toàn bộ 86 test cases).

### Đóng góp cụ thể

- Tạo module `starter_v0/tools/source_credibility/` với `tool.py` và `TOOL.md` chuẩn schema frontmatter.
- Hiện thực hàm `check_source_credibility(url, min_tier)` chuẩn guardrail (bắt toàn bộ ngoại lệ, trả error dict, không raise runtime exception).
- Hoàn thiện 14 test stubs cho các tool hệ thống (`clarify`, `format`, `send`, `lookup`, `fetch`, `timeline`, `social_search`, `policy`) và 5 test cases cho tool mới (`source_credibility`), kiểm tra đầy đủ happy path, input xấu, failure path, phân cấp tier và filtering.
- Đảm bảo contract test `test_tool_contract.py` pass 100%.

### Bằng chứng

- Code tool: `starter_v0/tools/source_credibility/tool.py`, `starter_v0/tools/source_credibility/TOOL.md`.
- Registry & Declaration: `starter_v0/tools/__init__.py`, `starter_v0/artifacts/tools.yaml`.
- Unit tests: `starter_v0/tests/test_tools_todo.py`.
- Kết quả test: `pytest tests/ -v` đạt **86 passed, 0 skipped, 0 failed**.
