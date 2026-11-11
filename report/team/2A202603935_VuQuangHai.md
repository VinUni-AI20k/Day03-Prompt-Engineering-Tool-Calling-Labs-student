# Báo cáo cá nhân — Vũ Quang Hải (2A202603935)

## 1. Thông tin thành viên

- Họ tên: Vũ Quang Hải
- MSSV: 2A202603935
- Email: haivq96@gmail.com

## 2. Phần việc phụ trách

Phụ trách CP3 — xây dựng tool mới `save_note` để lưu ghi chú nghiên cứu ở máy cục bộ, bổ sung kiểm tra an toàn và unit test, đồng bộ khai báo tool với agent. Trong lần hoàn thiện tiếp theo, bổ sung bảo vệ khi ghi đè file đã tồn tại và cập nhật bằng chứng liên quan trong báo cáo nhóm.

## 3. Đóng góp cụ thể

- Cài đặt `save_note` trong `starter_v0/tools/save_note/tool.py`: kiểm tra tên file và nội dung, chặn path traversal, chỉ ghi khi `confirmed` đúng boolean `True`, trả kết quả có cấu trúc và chuyển lỗi filesystem thành error dict.
- Thêm `starter_v0/tools/save_note/TOOL.md`, đăng ký tool trong `starter_v0/tools/__init__.py` và khai báo schema/description trong `starter_v0/artifacts/tools.yaml`.
- Bổ sung unit test cho happy path, xác nhận `False` và chuỗi `"false"`, input rỗng, path traversal, tên file hợp lệ có dấu chấm, lỗi filesystem và hành vi ghi đè.
- Bảo vệ file cũ: nếu tên file đã tồn tại, tool trả `needs_overwrite_confirmation` và không thay đổi nội dung cho tới khi có xác nhận riêng qua `overwrite_confirmed=True`.
- Cập nhật system prompt để hướng agent hỏi xác nhận trước khi lưu và hỏi lại riêng trước khi ghi đè.
- Cập nhật `.gitignore` để bỏ qua thư mục `notes/`, mở giới hạn trên của pytest trong `requirements.txt`, đồng bộ version log và mô tả bằng chứng trong báo cáo nhóm.

## 4. Bằng chứng

- File chính: `starter_v0/tools/save_note/tool.py`, `starter_v0/tools/save_note/TOOL.md`, `starter_v0/tools/__init__.py`, `starter_v0/artifacts/tools.yaml`, `starter_v0/tests/test_tools_todo.py`.
- File liên quan: `starter_v0/artifacts/system_prompt.md`, `starter_v0/data/eval_group.json`, `starter_v0/artifacts/version_log.csv`, `starter_v0/requirements.txt`, `.gitignore`, `report/team/group_report.md`.
- Commit trên nhánh `feature/CP3`:
  - `56384df` — `feat: complete CP3 with save_note tool, unit tests, and contract sync`
  - `02ba4be` — `feat: harden save_note confirmation and CP3 tests`
- Kiểm tra: 10 test `save_note` pass; 60 test contract pass; toàn suite có 77 passed và 14 skipped. Các test bị skip là TODO của tool khác, không phải test `save_note`. Pytest 9.2.0 gặp lỗi nội bộ của runner trong môi trường; chạy lại bằng pytest 8.4.2.
- AI/Copilot được dùng để hỗ trợ triển khai, rà soát và chạy kiểm thử. Các thay đổi được tự kiểm tra bằng unit test, contract test, full test suite, kiểm tra JSON eval và diff.

## 5. Tự đánh giá

Hoàn thành phần việc CP3: tool mới có schema, đăng ký, hướng dẫn, kiểm tra guardrail và hơn 3 unit test bao phủ các nhánh chính; các kiểm thử liên quan đều pass. Thay đổi ưu tiên tránh ghi file khi chưa xác nhận và tránh ghi đè ngoài ý muốn.
