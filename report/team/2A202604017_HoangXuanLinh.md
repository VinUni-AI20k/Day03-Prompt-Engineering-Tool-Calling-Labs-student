# Báo cáo cá nhân — HoangXuanLinh-2A202604017

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Hoàng Xuân Lĩnh
- MSSV: 2A202604017
- Email:

## 2. Phần việc phụ trách

UI Streamlit, link dùng thử cho Team showdown, Phần A của báo cáo nhóm, chat live và bảng B4.

## 3. Đóng góp cụ thể

- Viết `starter_v0/app.py`, tái dùng vòng lặp model → tool của `chat.py` và ghi transcript cùng format.
  - Trang Chat: khung chat ở giữa, sidebar liệt kê tool đọc từ `tools.yaml` (tool mới tự có nhãn MỚI), câu hỏi mẫu bấm được, hiện mọi tool call và lỗi tool.
  - Trang Eval runs: đọc `runs/*.json`, kiểm tra run hợp lệ, hiện metric, case FAIL, expected vs actual, `version_log.csv`.
- Thêm `streamlit` vào `requirements.txt` và theme `.streamlit/config.toml`.
- Mở link public bằng Cloudflare Tunnel.
- Viết Phần A (A1, A2, A3) của `group_report.md`.
- Chạy `chat.py` live 5 lượt với prompt v2 và viết bảng B4.
- Phát hiện agent v2 tự đặt `confirmed=true` khi gọi `send` dù user chưa xác nhận. Đã báo nhóm để sửa ở v3.
- Phát hiện case R04 PASS dù URL `https://openai.com/blog/gpt-5` đã 404, vì eval chỉ chấm routing, không chấm nội dung.

## 4. Bằng chứng

- File/commit/PR:
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:

## 5. Tự đánh giá

- Hoàn thành đúng phần được giao (UI, link dùng thử, Phần A, bảng B4), và qua chat live đã phát hiện được lỗi thật để nhóm sửa ở v3.
- Có lúc kiểm tra chưa kỹ: chọn câu hỏi mẫu chỉ dựa vào kết quả PASS mà không tự chạy lại, nên dùng nhầm URL đã chết.
- Học được rằng eval PASS chưa đủ để tin kết quả, cần tự kiểm tra thủ công những phần người dùng thực sự thấy.