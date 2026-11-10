# Team

## Thông tin nhóm

- Tên nhóm: NhomSNN
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-NhomSNN-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:
URL repo: https://github.com/sybui2004/K5-L3B-DAY03-NhomSNN-ResearchAgentToolEval/tree/buithaisy
Nhánh nộp: main
Commit chốt: ...

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Bùi Thái Sỹ | 2A202604002 |  | [sybui2004](https://github.com/sybui2004) | Nhóm trưởng; UI, live chat, Phần A báo cáo |
|   2 | Nguyễn Lương Nguyên | 2A202604005 |  | [nglngnguyen-gh](https://github.com/nglngnguyen-gh) | Prompt, tool declaration, vòng lặp v0→v3 |
|   3 | Mai Xuân Nhân | 2A202604006 |  | [nhan54v-boop](https://github.com/nhan54v-boop) | Tool mới + unit test |
|   4 | Bùi Đức Hiếu | 2A202604003 |  | [HieuData](https://github.com/HieuData) | Eval nhóm 10 case + test challenge |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## BuiThaiSy-2A202604002

### Phần việc phụ trách

- Nhóm trưởng: khung `TEAM.md`, điều phối merge, chốt bài (`pytest`, kiểm tra secret, commit chốt).
- UI Streamlit (`starter_v0/app.py`) + link dùng thử, live chat/transcript, Phần A của `group_report.md`.

### Đóng góp cụ thể

-

### Bằng chứng

-

## NguyenLuongNguyen-2A202604005

### Phần việc phụ trách

- `artifacts/system_prompt.md`, `artifacts/tools.yaml` (10 tool có sẵn), chạy base eval v0→v3, `artifacts/version_log.csv`; mục 3, B1, B2, Reflection.

### Đóng góp cụ thể

- Chạy và tạo baseline v0
- Sửa đổi system prompt để không bắt buộc chạy tool lung tung, chạy bản v1 để kiểm định
- Sửa system prompt để không tự ý suy đoán khi thiếu thông tin quan trọng, yêu cầu xác nhận trước hành động bên ngoài và cho phép xử lý tác vụ qua nhiều bước khi cần thiết, chạy bản v2 để kiểm định
- Sửa system prompt nhằm rút gọn và chuẩn hóa Tool Routing Policy: phân biệt rõ chức năng 10 tools, quy định argument conventions, routing sequences và send confirmation boundary, chạy bản v3 để kiểm định

### Bằng chứng

- File/commit/PR: CP2
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: ChatGPT, tự kiểm tra kết quả qua kiểm tra log và kết quả xuất ra command line sau khi chạy run_eval

## MaiXuanNhan-2A202604006

### Phần việc phụ trách

- Tool mới (`tools/<tên>/`, đăng ký `tools/__init__.py` + `tools.yaml`) và ≥ 3 unit test; B5a dòng tool mới/unit test.

### Đóng góp cụ thể

-

### Bằng chứng

-

## BuiDucHieu-2A202604003

### Phần việc phụ trách

- 10 eval case trong `data/eval_group.json`, run `--suite group`, test challenge (`tests/test_tools_todo.py`); B3, B5 dòng Test challenge.

### Đóng góp cụ thể

-

### Bằng chứng

-
