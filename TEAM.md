# Team

## Thông tin nhóm

- Tên nhóm: TeLiet
- Lớp: L3B
- Repo nhóm: K5-L3B-DAY03-TeLiet-ResearchAgentToolEval
- URL repo: https://github.com/Youngboy1609/K5-L3B-DAY03-TeLiet-ResearchAgentToolEval
- Nhánh nộp, commit chốt: điền khi nhóm chốt bài

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |Hồ Trọng Nghĩa|2A202603729|26ai.nghiaht@vinuni.edu.vn|Youngboy1609|Nhóm trưởng; tự làm `source_audit` và ≥3 test; tích hợp registry; chạy bonus model local và ghi B7|
|   2 |Phạm Lê Chuẩn|2A202603784|26ai.chuanpl@vinuni.edu.vn|22520160|Tự làm `deduplicate_sources` và ≥3 test; tối ưu system prompt v1-v3; chạy eval cloud và ghi version log|
|   3 |Phạm Đăng Quang|2A202603760|26ai.quangpd@vinuni.edu.vn|DanggQuangg|Tự làm `domain_filter` và ≥3 test; viết đúng 10 eval case nhóm, có case route tới cả 4 tool mới; phân tích kết quả|
|   4 |Nguyễn Minh Quân|2A202603747|26ai.quannm8@vinuni.edu.vn|minhquannm0905-cloud|Tự làm `rank_sources` và ≥3 test; làm UI, live chat/transcript và Phần A báo cáo|

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## PhamLeChuan-2A202603784

### Phần việc phụ trách

- Tự làm tool `deduplicate_sources` và ít nhất 3 unit test.
- Tối ưu `system_prompt.md` qua các phiên bản v1-v3.
- Chạy eval cloud bằng Gemini và ghi version log.

### Đóng góp cụ thể

- Loại item trùng URL, giữ item đầu tiên và thứ tự ban đầu.
- Xử lý item không có URL và input sai kiểu bằng error dict phù hợp.
- Phân tích kết quả baseline v0 và các vòng tối ưu v1-v3.

### Bằng chứng

- `starter_v0/tools/deduplicate_sources/`
- `starter_v0/tests/test_tools_todo.py`
- `starter_v0/artifacts/system_prompt.md`
- `starter_v0/artifacts/version_log.csv`
