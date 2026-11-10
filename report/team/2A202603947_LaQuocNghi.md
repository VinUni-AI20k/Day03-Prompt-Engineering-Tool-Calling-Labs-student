# Báo cáo cá nhân — LaQuocNghi—2A202603947

## 1. Thông tin thành viên

- Họ tên: Lã Quốc Nghị
- MSSV: 2A202603947
- Email: quocnghidev@gmail.com
- GitHub: quocnghidev
- Nhóm: DNH · Lớp: L3B
- Vai trò: Prompt & tối ưu eval (C1–C3)

## 2. Phần việc phụ trách

Theo phân công nhóm ([TEAM.md](../../TEAM.md), [PHAN_CONG.md](../../PHAN_CONG.md)):

- Setup môi trường (`.env`, preflight provider, `pytest` contract)
- Chạy baseline **v0** (chưa sửa prompt/tools) và ghi `artifacts/version_log.csv`
- Phân loại từng case FAIL của v0 → bảng **B2** trong `report/team/group_report.md`
- Owner tối ưu **v1 → v2 → v3** trên `artifacts/system_prompt.md` và `artifacts/tools.yaml`
- Cập nhật bằng chứng B1 / mục giải pháp trong báo cáo nhóm
- (Phối hợp) merge mô tả tool mới của Đạt vào `tools.yaml` khi tool đã đăng ký đủ

## 3. Đóng góp cụ thể

### 3.1. Baseline và phân tích lỗi (C1)

- Chạy base eval v0 với OpenRouter / `openai/gpt-4o-mini`.
- Run hợp lệ: `provider_error_cases=0`, `measured_cases=20/20`, `case_accuracy=0.65` (13/20 PASS).
- Phân loại 7 case FAIL từ run JSON (`failure_type`, `observed_mismatch`, `actual_tool_calls`):
  - `missing_info`: R10, R11 (đoán handle/URL thay vì `clarify`)
  - `wrong_boundary`: R12 (`send` không xác nhận)
  - `out_of_scope`: R08, R14 (dùng `send` để trả lời toán/code)
  - sai args / routing: R03, R13

### 3.2. Vòng tối ưu evidence-driven (C2–C3)

| Version | Artifact đổi | Giả thuyết | Metric trước → sau |
|---|---|---|---|
| v1 | `system_prompt.md` | Bỏ chỉ dẫn xấu starter (đoán / gửi luôn / một bước); thêm clarify, confirm trước send, out-of-scope | 0.65 → **0.85** |
| v2 | `tools.yaml` | Viết lại description mọi tool (when to use/not use); bắt buộc `clarify.response_type`; boundary `send(confirmed)`; convention args | 0.85 → **0.95** |
| v3 | `system_prompt.md` | Turn đầu send/post/đăng chỉ `clarify(response_type="yes_no")`, không hỏi nội dung bằng `text` trước confirm | 0.95 → **1.0** (20/20) |

Chi tiết hành vi sau từng version (từ run thật):

- **Sau v1:** model đã `clarify` / từ chối out-of-scope đúng hướng, nhưng R10–R11 thiếu `response_type`, R12 dùng `text` thay vì `yes_no`.
- **Sau v2:** R10–R11 PASS; còn R12 hỏi “đăng nội dung gì?” với `response_type="text"`.
- **Sau v3:** R12 PASS; toàn suite base **20/20**.

### 3.3. Tài liệu nhóm

- Điền / cập nhật `TEAM.md`, `PHAN_CONG.md`
- Điền B1, B2 và mục giải pháp trong `report/team/group_report.md` dựa trên run JSON + `version_log.csv` (không bịa metric)

## 4. Bằng chứng

### File / run

- `starter_v0/artifacts/system_prompt.md`
- `starter_v0/artifacts/tools.yaml`
- `starter_v0/artifacts/version_log.csv` (đủ v0–v3, có `prompt_hash` / `tools_hash` / `artifact_version` khớp run)
- `starter_v0/runs/v0_B_base_openrouter_20261110T181324961249.json` — 0.65
- `starter_v0/runs/v1_B_base_openrouter_20261110T184102136031.json` — 0.85
- `starter_v0/runs/v2_B_base_openrouter_20261110T185301286980.json` — 0.95
- `starter_v0/runs/v3_B_base_openrouter_20261110T185429875666.json` — 1.0
- `report/team/group_report.md` (B1, B2, mục 3)

### Commit / nhánh

- Repo: https://github.com/quocnghidev/K5-L3B-DAY03-NhomDNH-ResearchAgentToolEval
- Nhánh làm việc chính của nhóm: `task_split` (có commit cập nhật v1–v3 và phân công)
- Cách tự kiểm: mở từng run JSON, đối chiếu `summary.case_accuracy` và hash với dòng tương ứng trong `version_log.csv`

### AI / công cụ đã dùng và cách tự kiểm tra

- **Cursor (Composer)** hỗ trợ: phân tích run FAIL, soạn/sửa prompt & `tools.yaml`, điền `version_log` / B1–B2, viết báo cáo.
- **Tự kiểm tra kết quả:**
  1. Chỉ lấy metric/hash từ file `runs/*.json` do `run_eval.py` sinh ra; không bịa số.
  2. Mỗi version chạy lại `--suite base`; chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.
  3. Sau sửa `tools.yaml`, chạy `pytest tests/test_tool_contract.py` (55 passed trong môi trường `starter_v0/.venv`).
  4. Đọc `results[*].result.failures` / `actual_tool_calls` để đặt giả thuyết version sau, không sửa `eval_base.json`.

## 5. Tự đánh giá

- **Đã hoàn thành track cá nhân C1–C3:** baseline, phân tích lỗi, tối ưu 3 vòng có bằng chứng, base eval đạt 1.0.
- **Mức tự đánh giá phần việc phụ trách:** hoàn thành yêu cầu bắt buộc về prompt/tool-declaration và vòng v0–v3.
