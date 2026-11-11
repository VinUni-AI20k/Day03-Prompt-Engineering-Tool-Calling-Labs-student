# Báo cáo cá nhân — Trương Đức Phát (2A202603757)

## 1. Thông tin thành viên

- Họ tên: Trương Đức Phát
- MSSV: 2A202603757
- Email: 26ai.phattd@vinuni.edu.vn

## 2. Phần việc phụ trách

- CP3: xây dựng tool mới `dedupe_sources`, đăng ký tool, viết tài liệu và unit test; phối hợp tạo eval nhóm.

## 3. Đóng góp cụ thể

- Cài đặt `dedupe_sources` để chuẩn hóa URL, loại bỏ fragment và tham số tracking phổ biến, giữ lại nguồn đầu tiên và thứ tự ban đầu.
- Thêm xử lý input không hợp lệ, đăng ký tool trong registry và khai báo cách dùng trong `tools.yaml`.
- Viết unit test offline cho trường hợp bình thường, URL trùng sau chuẩn hóa và input lỗi.
- Tham gia chuẩn bị 10 eval case nhóm (5 single-turn, 5 multi-turn), trong đó có case yêu cầu route tới `dedupe_sources`.

## 4. Bằng chứng

- `starter_v0/tools/dedupe_sources/tool.py`, `starter_v0/tools/dedupe_sources/TOOL.md`.
- Đăng ký và khai báo: `starter_v0/tools/__init__.py`, `starter_v0/artifacts/tools.yaml`.
- Unit test: `starter_v0/tests/test_tools_todo.py`.
- Eval nhóm: `starter_v0/data/eval_group.json` và `starter_v0/runs/v3_B_group_openrouter_20261110T190141165371.json` (10/10 pass, không có provider error theo báo cáo nhóm).
- Commit kỹ thuật hiện có: `026d18b` (`feat: add local dedupe_sources tool and offline unit tests`).
- AI/công cụ: dùng agent hỗ trợ rà soát thiết kế và test; tự kiểm tra bằng unit test và đối chiếu kết quả eval nhóm đã lưu.

## 5. Tự đánh giá

Tool giữ thứ tự nguồn và tránh gộp nhầm khi URL khác nhau ở query có ý nghĩa. Giới hạn hiện tại là không theo redirect và không phát hiện hai URL khác nhau nhưng trỏ tới cùng nội dung. Các giới hạn này được nêu trong báo cáo nhóm. Cần bổ sung email nếu biểu mẫu yêu cầu.
