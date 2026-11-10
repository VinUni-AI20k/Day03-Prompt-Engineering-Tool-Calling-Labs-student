# Báo cáo cá nhân — HoVaTen-MSSV

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Nguyễn Lương Nguyên
- MSSV: 2A202604005
- Email: nglngnguyen@gmail.com

## 2. Phần việc phụ trách

- CP1 — Setup và baseline v0
- CP2 — Tối ưu prompt và tool declaration v1–v3

## 3. Đóng góp cụ thể

- Chạy và tạo baseline v0
- Sửa đổi system prompt để không bắt buộc chạy tool lung tung, chạy bản v1 để kiểm định
- Sửa system prompt để không tự ý suy đoán khi thiếu thông tin quan trọng, yêu cầu xác nhận trước hành động bên ngoài và cho phép xử lý tác vụ qua nhiều bước khi cần thiết, chạy bản v2 để kiểm định
- Sửa system prompt nhằm rút gọn và chuẩn hóa Tool Routing Policy: phân biệt rõ chức năng 10 tools, quy định argument conventions, routing sequences và send confirmation boundary, chạy bản v3 để kiểm định

## 4. Bằng chứng

- File/commit/PR: CP2
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: ChatGPT, tự kiểm tra kết quả qua kiểm tra log và kết quả xuất ra command line sau khi chạy run_eval

## 5. Tự đánh giá

Cần cải thiện phần sửa lại tools description để prompt biết sử dụng tool tốt hơn
