# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A / L3B
- Repo nhóm: `K5-L3A-DAY03-TenNhom-ResearchAgentToolEval` hoặc `K5-L3B-DAY03-TenNhom-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |        |      |       |        |         |
|   2 |        |      |       |        |         |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## Vũ Quang Hải — 2A202603935

### Phần việc phụ trách

- Phụ trách CP3: xây dựng tool mới `save_note`, bổ sung kiểm tra an toàn và unit test, đồng bộ khai báo tool với agent.

### Đóng góp cụ thể

- Cài đặt `save_note` trong `starter_v0/tools/save_note/tool.py`: kiểm tra tên file và nội dung, chặn path traversal, chỉ ghi khi `confirmed` đúng boolean `True`, và trả error dict khi filesystem gặp lỗi.
- Tạo `TOOL.md`, đăng ký tool trong `starter_v0/tools/__init__.py` và khai báo schema trong `starter_v0/artifacts/tools.yaml`.
- Bổ sung unit test cho happy path, xác nhận `False` và chuỗi `"false"`, input rỗng, path traversal, lỗi filesystem và hành vi ghi đè.
- Bảo vệ file hiện có: chỉ ghi đè sau xác nhận riêng qua `overwrite_confirmed=True`; cập nhật prompt để agent tuân thủ xác nhận trước khi lưu và ghi đè.
- Cập nhật `.gitignore`, `requirements.txt`, version log và bằng chứng CP3 trong báo cáo nhóm.

### Bằng chứng

- Các file chính: `starter_v0/tools/save_note/tool.py`, `starter_v0/tools/save_note/TOOL.md`, `starter_v0/tools/__init__.py`, `starter_v0/artifacts/tools.yaml`, `starter_v0/tests/test_tools_todo.py`.
- Commit trên nhánh `feature/CP3`: `56384df` (thêm tool và unit test), `02ba4be` (siết xác nhận ghi đè và mở rộng kiểm thử).
- Kiểm tra: 10 test `save_note` và 60 test contract pass; toàn suite có 77 passed, 14 skipped (TODO ở các tool khác).
