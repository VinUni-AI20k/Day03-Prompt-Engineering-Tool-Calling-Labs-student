# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A / L3B
- Repo nhóm: `K5-L3A-DAY03-TenNhom-ResearchAgentToolEval` hoặc `K5-L3B-DAY03-TenNhom-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Bùi Đặng Nhật Nguyên | 2A202603937 | nhatnguyenmtvt@gmail.com | nhatnguyenmtvt@gmail.com | Dev Tool |
|   2 | Nguyễn Bá Quang Huy | 2A202603926 | quanghuynguyenba@gmail.com | quanghuynguyenba@gmail.com | Update System Prompt|
|   3 | Đỗ Hoàng Vũ  | 2A202603920 | dohoangvu.nt2005@gmail.com | dohoangvu.nt2005@gmail.com | Tester |
|   4 | Lê Hải Lân  | 2A202603915 | lehailan110@gmail.com | lehailan110@gmail.com | Design UI |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## HoVaTen-MSSV

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-

## DoHoangVu-2A202603920

### Phần việc phụ trách

- Tester: viết unit test cho tool, viết eval case của nhóm, chạy eval sau mỗi version và phân tích case FAIL.
- Giữ `starter_v0/artifacts/version_log.csv`: ghi kết quả từng version v0–v4.

### Đóng góp cụ thể

- Viết 14 unit test offline cho 8 tool có sẵn (`tests/test_tools_todo.py`), HTTP được mock bằng `fake_http`.
- Tìm và sửa 3 bug trong tool: `limit=0`/`max_results=0` bị âm thầm đổi thành 5 (timeline, social_search, lookup); `policy(top_k=0)` bị đổi thành 1; `clarify(response_type="choice")` không có `options` vẫn chạy. Thêm `positive_int` trong `tools/_shared.py` và 5 regression test.
- Viết 9/10 case trong `data/eval_group.json` (G01–G04, GM01–GM05), phủ đủ 6 loại lỗi.
- Chạy base, group (và extension ở v4) sau mỗi version, đọc `failures`/`actual_tool_calls` trong run JSON và báo nguyên nhân cho nhóm làm giả thuyết version sau: thiếu `response_type` của clarify (→ v2), regression GM02/M06 (→ v3), rule xin credentials trong prompt (đã bỏ), E01 chọn sai `policy_area` (gợi ý cho v5).
- Kết quả theo dõi: base 13/20 → 18/20 → 19/20 → 20/20 → 20/20; group 5/9 → 7/9 → 8/9 → 10/10 → 10/10; extension v4 13/14.
- Sửa lỗi môi trường làm `pytest` crash (lệch phiên bản `opentelemetry-exporter-otlp-proto-grpc`).

### Bằng chứng

- Branch `DoHoangVu`; commit `8f54f78` (test, sửa bug, eval case nhóm, run v0 — PR #1), `e7ad2ad` (log v0), `4969420`/`9947499` (eval v1 — PR #2, #4), `cd377bf` (eval v2 — PR #5), `30647fe` (eval v4).
- `starter_v0/artifacts/version_log.csv` (dòng v0–v4) và các run JSON trong `starter_v0/runs/`.
- `pytest`: 137 passed.
- Báo cáo cá nhân: `report/team/2A202603920_DoHoangVu.md`.
