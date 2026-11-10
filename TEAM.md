# Team

## Thông tin nhóm

- Tên nhóm: anbatocom
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-anbatocom-ResearchAgentToolEval`
- URL repo, nhánh nộp, commit chốt: https://github.com/czx04/K5-L3B-DAY03-anbatocom-ResearchAgentToolEval — nhánh `main` — commit chốt: 

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Dư Văn Hùng | 2A202603975 | dhit2k4@gmail.com | `czx04` | Prompt, tool declaration, eval v0→v3 (C1, C2, C3) |
|   2 |  |  |  | `hoangngochieu` | Người 2 — Tool mới `extract_keywords` + unit test (C4) |
|   3 |  |  |  | `Jancaster1234` | Người 3 — Eval nhóm, UI Streamlit, báo cáo Phần A (C5, C6, C7) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

## DuVanHung-2A202603975

### Phần việc phụ trách

- Tạo repo nhóm, cấu hình provider `openai` / `gpt-4o-mini`, chạy preflight và `pytest`.
- Chạy baseline v0 và phân tích lỗi (B2); tối ưu `system_prompt.md` và `tools.yaml` qua v1, v2, v3; ghi `version_log.csv` và bảng B1.
- Khai báo tool mới `extract_keywords` vào `tools.yaml` ở v3; tổng hợp báo cáo nhóm Phần B.

### Đóng góp cụ thể

- v0: 0.70 (14/20) → v1 (sửa prompt): 0.85 → v2 (sửa tool description): 0.95 → v3 (rule xác nhận `yes_no` + tool mới): 0.95 base, 1.00 suite group.
- Viết lại system prompt: bỏ 3 chỉ dẫn xấu của starter, thêm rule clarify / xác nhận trước khi gửi / ngoài phạm vi / routing.
- Viết lại description mọi tool trong `tools.yaml` (làm gì / khi nào dùng / khi nào không dùng + convention args).

### Bằng chứng

- Commit: `ad1c762` (v0), `41e2f46` (v1), `7ad1134` (v2).
- Run: `starter_v0/runs/v0_…`, `v1_…`, `v2_…`, `v3_B_base_…`, `v3_B_group_…`.
- File: `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/artifacts/version_log.csv`.
- Báo cáo cá nhân: `report/team/2A202603975_DuVanHung.md`.

## HoVaTen-MSSV (GitHub `hoangngochieu`)

### Phần việc phụ trách

- Viết tool mới `extract_keywords` và unit test (CP3).

### Đóng góp cụ thể

- `starter_v0/tools/keywords/tool.py` + `TOOL.md`: trích từ khóa lặp nhiều nhất từ text có sẵn, chạy local, validate input và trả error dict thay vì raise.
- Đăng ký tool trong `starter_v0/tools/__init__.py`.
- 3 unit test trong `starter_v0/tests/test_tools_todo.py`: happy path, text rỗng từ model, lỗi nội bộ → error dict.

### Bằng chứng

- Commit: `1ea2387` (feat: implement extract_keywords tool and associated tests), merge qua PR #2.
- Báo cáo cá nhân: `report/team/<MSSV>_<HoTen>.md` (chưa có)

## HoVaTen-MSSV (GitHub `Jancaster1234`)

### Phần việc phụ trách

- Báo cáo nhóm Phần A, eval nhóm (CP4), UI Streamlit (CP5).

### Đóng góp cụ thể

- Viết Phần A của `report/team/group_report.md` (A1–A3).
- Viết eval case trong `starter_v0/data/eval_group.json` (suite group v3: 10/10 PASS).
- Viết UI `starter_v0/app.py` (Streamlit) + thêm dependency vào `requirements.txt`.

### Bằng chứng

- Commit: `1059b6d` (Phần A), `632eef9` (9 group eval cases), `58f47bf` (Streamlit UI), merge `d89522c`.
- Báo cáo cá nhân: `report/team/<MSSV>_<HoTen>.md` (chưa có)
