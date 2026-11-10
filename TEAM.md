# Team

## Thông tin nhóm

- Tên nhóm: MMV
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-MMV-ResearchAgentToolEval`
- URL repo, nhánh nộp, commit chốt: https://github.com/caominhnguyen05/K5-L3B-DAY03-MMV-ResearchAgentToolEval · nhánh `optimize` · commit chốt: điền sau khi chốt bài

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |   Phạm Hoàng Đức Minh     |    2A202604114  |   ducminh03102005@gmail.com    |    https://github.com/PH31M    |   Đóng góp viên      |
|   2 | Nguyễn Cao Minh | 2A202604099 | 26ai.minhnc@vinuni.edu.vn | https://github.com/caominhnguyen05 | 4 tool xử lý dữ liệu đã thu thập và unit test |
|   3 | Nguyễn Công Huy | 2A202604086 | conghuycr@gmail.com |  | 2 tool tìm bài báo khoa học (`openalex`, `semantic_scholar`) |
|   4 |  |  |  | https://github.com/qvinhh2312 | UI Streamlit, deploy Cloudflare, Phần A báo cáo nhóm |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

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






