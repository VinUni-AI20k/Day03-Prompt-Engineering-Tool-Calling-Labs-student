# Báo cáo cá nhân — Nguyen Nghiem Khanh Tiep

## 1. Thông tin thành viên

- Họ tên: Nguyễn Nghiêm Khánh Tiệp
- MSSV: 2A202603863
- Email: tiepnnk04@gmail.com
- GitHub: `tiepnnk01-10` (commit cũ hiển thị tên `Tiepnnk`)

## 2. Phần việc phụ trách

- **CP2 — Tối ưu system prompt và tool declaration qua 3 version (v1, v2, v3).** Mỗi version chỉ kiểm chứng một giả thuyết, chạy lại base eval (20 case, OpenAI `gpt-4o-mini`) và ghi kết quả.
- Ghi `artifacts/version_log.csv` cho v1–v3 và điền bảng **B1 (Version Evidence)** cùng phần phân tích từng case trong `report/team/group_report.md`.
- Hỗ trợ CP1: chạy preflight và một lần base eval v0 để kiểm tra setup.

## 3. Đóng góp cụ thể

| Version | File sửa | Giả thuyết | case_accuracy | Kết luận |
|---|---|---|---:|---|
| v0 | — | Baseline của nhóm | 0.70 | Điểm xuất phát |
| v1 | `system_prompt.md` | Prompt starter bảo model đoán và gửi ngay, nên model không `clarify` khi thiếu thông tin và không xin xác nhận trước khi `send` | 0.90 | Đúng với R10, R11 (hết tự đoán handle/URL) |
| v2 | `system_prompt.md` | Prompt thiếu rule routing (tin tức → `lookup`, tweet → `social_search`, gửi → `clarify(yes_no)`) | **0.95** | Sửa được regression M02 của v1; `tool_routing_accuracy` và `multiturn_accuracy` đạt 1.00 |
| v3 | `tools.yaml` | Description của tool mơ hồ, nên model không biết `yes_no` là bước xác nhận bắt buộc và không rõ convention args | 0.85 | **Giả thuyết bị bác bỏ**: R12 vẫn FAIL, đồng thời gây regression R10 và M03 |

Các việc cụ thể:

- Đọc `failures`, `observed_mismatch` và `actual_tool_calls` của từng case FAIL để đặt giả thuyết, thay vì sửa theo cảm giác.
- Viết lại `system_prompt.md`: bỏ 3 chỉ dẫn xấu của starter, thêm rule clarify/xác nhận (v1) và khối Routing rules (v2).
- Viết lại description của cả 10 tool và convention args trong `tools.yaml` (v3), giữ nguyên tên tool/param/enum/default để contract test vẫn xanh.
- Phân tích nguyên nhân regression của v3:
  - **R10:** description mới của `timeline` và `social_search` khiến câu "5 tweet mới nhất" bị đẩy sang `social_search(query="")` thay vì `clarify`.
  - **M03:** câu "never guess a handle" khiến model tự ghép `andrejkarpathy` thay vì handle thật `karpathy`.
- Ghi nhận giới hạn của chấm tự động: ở R08/R14, model vẫn giải toán/viết code nhưng eval chấm PASS vì chỉ kiểm tra "không gọi tool".
- Ghi nhận độ dao động giữa các lần chạy: run v0 do tôi chạy lại đạt 0.65, còn run v0 chính thức của nhóm đạt 0.70 (cùng prompt và tools). Vì vậy chênh lệch dưới khoảng 0.05 không đủ để kết luận là có cải thiện.

## 4. Bằng chứng

- File/commit/PR:
  - Run: [v1](../../starter_v0/runs/v1_B_base_openai_20261110T184506774099.json), [v2](../../starter_v0/runs/v2_B_base_openai_20261110T185439904664.json), [v3](../../starter_v0/runs/v3_B_base_openai_20261110T190328305130.json)
  - [version_log.csv](../../starter_v0/artifacts/version_log.csv): dòng v1, v2, v3 (hash trong log khớp với hash trong run JSON)
  - [group_report.md](group_report.md): bảng B1 cùng các mục "Chi tiết v1/v2/v3"
  - Commit `252da65` (Complete CP2: v1, v2, v3), merge vào `main` qua PR #1 (`e1ff04e`)
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Đọc run JSON, tóm tắt case FAIL, gợi ý nội dung prompt/description và soạn phần ghi log/báo cáo.
  - Cách tự kiểm tra:
    - Đối chiếu `prompt_hash`/`tools_hash` trong run với version_log để chắc mỗi version chỉ đổi đúng một file.
    - Chạy `pytest tests/test_tool_contract.py` (55 passed) sau khi sửa `tools.yaml`, trước khi tốn tiền API.
    - Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.
    - Tự đọc lại `actual_tool_calls` của các case thay đổi trạng thái để xác nhận nguyên nhân thay vì tin vào tóm tắt.

## 5. Tự đánh giá

- **Làm tốt:** đi đúng vòng lặp giả thuyết -> sửa một thứ -> đo lại -> ghi log. Cả 3 version đều có run hợp lệ và hash khớp. Bản tốt nhất (v2) tăng `case_accuracy` từ 0.70 lên 0.95.
- **Chưa tốt:**
  - v3 sửa description của cả 10 tool trong một lần. Thay đổi quá rộng nên gây tác dụng phụ ngoài ý muốn (R10, M03).
  - R12 (xác nhận `yes_no` trước khi gửi) chưa sửa được ở cả 3 version.
- **Bài học:**
  - Description của một tool ảnh hưởng tới việc model chọn **các tool khác**, nên mỗi lần sửa declaration phải chạy lại toàn bộ suite.
  - Thay đổi nên nhỏ hơn để biết chính xác dòng nào gây ra kết quả.
  - Một giả thuyết bị bác bỏ vẫn là bằng chứng có giá trị.
- **Hướng tiếp theo:** làm v4 với thay đổi nhỏ trong `tools.yaml`: `social_search.query` không được rỗng, và `timeline.screenname` ghi rõ cách map tên người nổi tiếng sang handle thật. Với R12, thử thêm một ví dụ few-shot trong prompt.
