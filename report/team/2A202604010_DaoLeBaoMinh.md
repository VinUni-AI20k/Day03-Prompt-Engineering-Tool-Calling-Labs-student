# Báo cáo cá nhân — DaoLeBaoMinh-2A202604010

## 1. Thông tin thành viên

- Họ tên: Đào Lê Bảo Minh
- MSSV: 2A202604010
- Email: 26ai.dlbminh@vinuni.edu.vn
- Vai trò: Trưởng nhóm (A)

## 2. Phần việc phụ trách

- Setup repo nhóm, `.env`, preflight provider, `pytest`.
- Chạy toàn bộ eval (base v0–v4, group v3–v4), kiểm tra run hợp lệ (`provider_error_cases = 0`, `measured_cases = total_cases`) và ghi `starter_v0/artifacts/version_log.csv`.
- Là người duy nhất sửa `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, theo hypothesis của B, mỗi version một giả thuyết.
- Viết 10 case eval nhóm trong `starter_v0/data/eval_group.json`.
- Điều phối, phân công, merge nhánh và push bản nộp.

## 3. Đóng góp cụ thể

- **Baseline và vòng lặp v0 → v4:** chạy 5 version base và 2 run group, tất cả hợp lệ, cùng model `openai/gpt-4o-mini`. Case accuracy bộ base: v0 0.75 → v1 0.85 → v2 0.80 → v3 0.80 → v4 0.90.
- **Sửa prompt:**
  - v1: bỏ chỉ dẫn "cứ đoán" và thêm rule gọi `clarify` khi thiếu account/URL. Kết quả: R10, R11 không còn bịa `sama` hay `example.com`.
  - v3: bỏ chỉ dẫn "cứ gửi luôn" và thêm boundary `clarify(yes_no)` trước `send`. Kết quả: R12 không còn gọi `send` khi chưa xác nhận.
- **Kiểm soát giả thuyết:**
  - Tách bản `tools.yaml` viết lại 6 tool của C (`fcad954`), chỉ giữ phần `clarify` cho v2.
  - Phát hiện merge `56fcefc` làm `tools.yaml` lệch khỏi v2 (so hash với run v2) và khôi phục lại trước khi sửa v3 (`42a645c`).
- **Eval nhóm:** viết 10 case (5 single turn, 5 multi turn) phủ `policy`, `papers`, `paper_text`, quy ước handle bỏ `@`, `timeframe=month`, boundary gửi/xác nhận và carry-over tham số qua nhiều lượt. Thay G05 bằng case route tới tool mới `hn_search` (`f1e6069`). Kết quả group v4: 9/10.
- **Đăng ký tool mới:** khai báo `hn_search` của C trong `tools.yaml` thành version riêng (v4), để đo được việc thêm tool có làm nhiễu routing hay không. Kết quả: không case base nào gọi nhầm `hn_search`.
- **UI chạy lại version cũ:**
  - Thêm `scripts/snapshot_version.py` và snapshot `artifacts/versions/v0`–`v4`, hash khớp run JSON.
  - Thêm dropdown chọn version trong `app.py`, để transcript ghi đúng prompt/tools đã dùng.
- **Telegram:** kiểm tra cấu hình bằng lệnh chỉ đọc (`getChat`), phát hiện chat ID ban đầu là chat cá nhân và yêu cầu đổi sang private channel của nhóm.
- **Báo cáo:**
  - Viết `TEAM.md` (phân công theo rubric).
  - Viết các mục 1, 2 (Phần A), 3, 5, 7, 8 và B5/B5a (UI, bonus) của `group_report.md`.
  - B1–B3 do B viết.

## 4. Bằng chứng

- **Commit:**
  - `c23148b` (v0 run)
  - `7d4aec7` (v0 version log + 10 eval case)
  - `75ef318` (v1 prompt + run)
  - `c7ed48b` (v2 tools.yaml)
  - `42a645c` (khôi phục tools.yaml v2, UI chọn version)
  - `45dc2b5` (v3 prompt)
  - `8efc190` (v3 runs)
  - `f1e6069` (v4: khai báo `hn_search`, G05)
  - `15e52e6` (v4 runs)
- **Run:**
  - `starter_v0/runs/v0_B_base_openrouter_20261110T173925903234.json`
  - `starter_v0/runs/v1_B_base_openrouter_20261110T185630444201.json`
  - `starter_v0/runs/v2_B_base_openrouter_20261110T225827485272.json`
  - `starter_v0/runs/v3_B_base_openrouter_20261111T010153897358.json`
  - `starter_v0/runs/v3_B_group_openrouter_20261111T010252364523.json`
  - `starter_v0/runs/v4_B_base_openrouter_20261111T012740238004.json`
  - `starter_v0/runs/v4_B_group_openrouter_20261111T012817479092.json`
- **File khác:** `starter_v0/artifacts/version_log.csv`, `starter_v0/data/eval_group.json`, `starter_v0/artifacts/versions/`, `starter_v0/scripts/snapshot_version.py`.
- **Ghi chú về commit:** commit `de57d0c` (tool `hn_search` + 12 test) mang tên tôi nhưng là phần việc của Trần Phú Thái (C), được commit từ máy của tôi.
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Dùng **Claude Code** để lên timeline và phân công, viết nháp 10 eval case, soạn rule prompt v1/v3, đọc run JSON để tóm tắt case FAIL, sửa `app.py` và viết script snapshot.
  - Cách tự kiểm tra:
    - Chạy `pytest` sau mỗi thay đổi (contract test phải xanh).
    - So `artifact_version` của file hiện tại với run JSON trước khi sửa version mới. Cách này phát hiện được lỗi merge `tools.yaml`.
    - `git diff` giữa hai version để chắc mỗi version chỉ đổi một thứ.
    - Đọc trực tiếp `actual_tool_calls` trong run JSON trước khi ghi nhận định vào báo cáo.
    - Chạy thử UI bằng `streamlit.testing` để xác nhận chọn `v0` thì transcript ghi đúng hash v0.
  - Không dùng AI để tạo run, metric hay transcript. Mọi số liệu lấy từ file do `run_eval.py` sinh ra.

## 5. Tự đánh giá

- **Làm tốt:**
  - Giữ được nguyên tắc một giả thuyết mỗi version, kể cả khi phải tách bản sửa lớn của đồng đội.
  - Phát hiện và sửa lỗi merge nhờ đối chiếu hash.
  - Ghi trung thực các version không tăng điểm (v2, v3) và mức tăng v4 phần lớn do dao động của model.
- **Chưa tốt:**
  - Để các thành viên làm trên nhiều nhánh mà không có quy ước merge từ đầu, dẫn tới sự cố `tools.yaml`.
  - Nhiều commit của thành viên khác đứng tên tôi, gây khó cho việc tính đóng góp cá nhân.
  - Mỗi version chỉ chạy một lần nên không đo được độ dao động (R13, M06).
  - Rule v3 gộp "hỏi nội dung" và "xin xác nhận" vào một câu, gây lỗi `response_type` ở R12/G07.
- **Học được:**
  - Fix hành vi chung thuộc prompt, fix cách gọi tool thuộc tool declaration.
  - Description quá cụ thể có thể gây regression (R01 ở v2).
  - Eval chỉ đo lựa chọn tool và args, còn chất lượng output cần unit test và review thủ công.
