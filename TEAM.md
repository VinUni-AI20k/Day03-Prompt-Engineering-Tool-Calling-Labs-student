# Team

## Thông tin nhóm

- Tên nhóm: Nhom100
- Lớp: L3B
- Repo nhóm: `K5-L3B-Nhom100-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/minhtriet061203/K5-L3B-Nhom100-ResearchAgentToolEval, nhánh `main`, commit chốt: _(điền sau khi merge)_

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | _(thành viên tự điền)_ | | | `minhtriet061203` | Baseline v0, tối ưu v1–v3, failure analysis B1/B2 |
|   2 | _(thành viên tự điền)_ | | | `w3schools-test` | Tool mới `text_stats`, `date_diff`, `dedupe` + unit test + 3 case group đầu |
|   3 | Khương Hoàng Nguyên | 2A202603987 | 26ai.nguyenkh@vinuni.edu.vn | `NguyenGL03` | CP3 test challenge + sửa bug tool có sẵn, CP4 eval group, live chat + Telegram thật, bonus Small Local Model, báo cáo |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

## minhtriet061203 _(HoVaTen-MSSV: thành viên tự điền)_

### Phần việc phụ trách

- CP1–CP2: baseline v0 và vòng tối ưu v1–v3.

### Đóng góp cụ thể

- Chạy baseline v0 (0.65), sửa `system_prompt.md` (v1, v2) và `tools.yaml` (v3), đạt 0.95; ghi `version_log.csv`; viết bảng B1/B2.

### Bằng chứng

- Commit `7cd8f4b`; `starter_v0/runs/v0…v3_B_base_openrouter_*.json`; `starter_v0/artifacts/version_log.csv`.

## w3schools-test _(HoVaTen-MSSV: thành viên tự điền)_

### Phần việc phụ trách

- CP3: tool mới và unit test.

### Đóng góp cụ thể

- Viết 3 tool `text_stats`, `date_diff`, `dedupe` (`tool.py` + `TOOL.md`), đăng ký trong `tools/__init__.py` và `tools.yaml`; 9 unit test; 3 case group đầu (G01–G03).

### Bằng chứng

- Commit `2636ec9`, `2d3ddf1`; `starter_v0/tools/{text_stats,date_diff,dedupe}/`.

## KhuongHoangNguyen-2A202603987

### Phần việc phụ trách

- CP3: hoàn thành test challenge (14 stub TODO), thêm test mới, tìm và sửa bug trong tool có sẵn.
- CP4: eval nhóm đủ 10 case (5 single + 5 multi) và chạy `--suite group`.
- CP5: live chat có transcript, viết báo cáo nhóm (Phần A, B3–B7, reflection). Phần UI chưa làm.
- Bonus: `send` gửi Telegram thật sau xác nhận; Small Local Model Challenge.

### Đóng góp cụ thể

- `tests/test_tools_todo.py`: viết 14 stub TODO, thêm 6 regression test và 3 test cho tool mới; `pytest` 109 passed, 0 skipped.
- Sửa 3 bug tool có sẵn: `send` nhận chuỗi `"false"` là đã xác nhận; `send` lỗi Markdown, text rỗng, mạng reset; `timeline` giữ dấu `@`.
- `data/eval_group.json`: thêm G04–G10; run group v3 đạt 10/10.
- Transcript Telegram: `clarify(yes_no)` → "Có" → `send(confirmed=true)` → `status: sent`.
- Bonus local: chạy base eval trên `qwen2.5:7b` và `llama3.2:3b`, 3 vòng tối ưu (v4–v6) prompt/tools riêng cho local (llama 0.15 → 0.50), kiểm tra ngược trên cloud (mục B7).

### Bằng chứng

- Xem [report/team/2A202603987_KhuongHoangNguyen.md](report/team/2A202603987_KhuongHoangNguyen.md).
