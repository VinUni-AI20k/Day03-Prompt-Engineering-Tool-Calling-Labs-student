# Team

## Thông tin nhóm

- Tên nhóm: **DNH**
- Lớp: **L3B**
- Repo nhóm: `K5-L3B-DAY03-NhomDNH-ResearchAgentToolEval`
- URL repo, nhánh nộp, commit chốt:
  - URL: https://github.com/quocnghidev/K5-L3B-DAY03-NhomDNH-ResearchAgentToolEval
  - Nhánh nộp: `main`
  - Commit chốt: _(điền SHA khi nộp)_
- Chi tiết phân công theo timeline: xem [PHAN_CONG.md](PHAN_CONG.md)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nghị | _(điền)_ | _(điền)_ | quocnghidev | Prompt & tối ưu eval (C1–C3) |
|   2 | Đạt | _(điền)_ | _(điền)_ | _(điền)_ | Tool mới + unit test + khung UI (C4) |
|   3 | Hà | _(điền)_ | _(điền)_ | _(điền)_ | Eval nhóm + live chat + báo cáo + hoàn thiện UI (C5–C7) |

> Mỗi thành viên tự bổ sung họ tên đầy đủ, MSSV, email, GitHub trước khi nộp.

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

---

## Nghị

### Phần việc phụ trách

- Setup chung (`.env`, preflight, `pytest`)
- Baseline **v0** + phân loại lỗi FAIL (bảng B2)
- Sửa `artifacts/system_prompt.md` và `artifacts/tools.yaml`
- Chạy vòng tối ưu **v1 → v2 → v3**, ghi `artifacts/version_log.csv`
- Chốt merge mô tả tool mới của Đạt vào `tools.yaml`

### Đóng góp cụ thể

- Owner các file: `system_prompt.md`, `tools.yaml`, `version_log.csv`, run base v0–v3
- Khởi tạo `TEAM.md` + `PHAN_CONG.md`
- Tối ưu evidence-driven: v0 0.65 → v1 0.85 → v2 0.95 → v3 **1.0** (20/20, `provider_error_cases=0`)

### Bằng chứng

- `starter_v0/runs/v0_B_base_openrouter_20261110T181324961249.json`
- `starter_v0/runs/v1_B_base_openrouter_20261110T184102136031.json`
- `starter_v0/runs/v2_B_base_openrouter_20261110T185301286980.json`
- `starter_v0/runs/v3_B_base_openrouter_20261110T185429875666.json`
- `starter_v0/artifacts/version_log.csv`
- Bảng B1 / B2 trong `report/team/group_report.md`
- Commit kỹ thuật trên `main`

---

## Đạt - 2A202603922

### Phần việc phụ trách

- Thiết kế và viết **≥ 1 tool mới** (`tools/datetime_window/tool.py` + `TOOL.md`)
- Đăng ký tool trong `tools/__init__.py`
- Viết **≥ 3 unit test** trong `tests/test_tools_todo.py`
- Scaffold UI (Streamlit hoặc tương đương) + dependency trong `requirements.txt`
- Gửi Nghị mô tả tool (tên, params, khi nào dùng) để đưa vào prompt/`tools.yaml`

### Đóng góp cụ thể

- Owner các file: `tools/datetime_window/tool.py`, `tools/datetime_window/TOOL.md`, `tools/__init__.py`, `tests/test_tools_todo.py`
- Khung UI ban đầu để Hà hoàn thiện

### Bằng chứng

- Folder tool mới (`tools/datetime_window/`) + `TOOL.md`
- Output lệnh `pytest` (0 failed; ≥ 3 test tool mới không skip)
- Commit kỹ thuật trên nhánh `main`

---

## Hà

### Phần việc phụ trách

- Viết đúng **10 case** trong `data/eval_group.json` (5 single + 5 multi; ≥ 1 case route tới tool mới)
- Chạy `--suite group` và lưu run
- Hoàn thiện UI + link dùng thử (tunnel/deploy) → mục A1
- Live chat ≥ 3 lượt (`chat.py`) + transcript
- Lắp `report/team/group_report.md` (Phần A ưu tiên showdown; Phần B bằng chứng)

### Đóng góp cụ thể

- Owner các file: `data/eval_group.json`, `transcripts/`, `group_report.md`, polish UI + link public
- Rà checklist nộp bài (`SUBMISSION.md`)

### Bằng chứng

- `starter_v0/data/eval_group.json` + run group
- `starter_v0/transcripts/*.transcript.json`
- `report/team/group_report.md` (A + B)
- Commit kỹ thuật trên `main`
