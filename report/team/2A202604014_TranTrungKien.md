# Báo cáo cá nhân — HoVaTen-MSSV

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Trần Trung Kiên
- MSSV: 2A202604014
- Email:

## 2. Phần việc phụ trách

- Phụ trách prompt và mô tả tool.
- Phân tích các case lỗi từ kết quả eval, đề xuất giả thuyết cải tiến cho từng phiên bản, chỉnh sửa system prompt/tool declaration và phối hợp với thành viên A chạy lại để đánh giá.
- Tổng hợp các mục B1–B3 trong báo cáo nhóm.
...

## 3. Đóng góp cụ thể
- Phân tích năm case lỗi v0: R08_out_of_scope, R10_missing_handle, R11_missing_url, R12_confirm_before_send và R13_parallel_web_and_tweets; xác định lỗi gọi tool không cần thiết, tự đoán thông tin, thiếu xác nhận và sai arguments.
- Đề xuất giả thuyết v1: thay chỉ dẫn tự đoán tài khoản/URL bằng kiểm tra lịch sử hội thoại và hỏi lại khi thiếu thông tin.
- Phân tích kết quả v1: R10/R11 đã chuyển sang gọi đúng clarify nhưng vẫn thiếu response_type; R12 vẫn gọi send trước khi xác nhận.
- Đề xuất giả thuyết v2: làm rõ yêu cầu truyền tường minh response_type="text" khi hỏi thông tin còn thiếu nhằm giảm lỗi arguments ở R10/R11.
- Tổng hợp bảng B1 về phiên bản và bảng B2 về lỗi, liên kết với run JSON thực tế.
Tổng hợp B3 từ 10 case eval của nhóm và kết quả chạy.
...

## 4. Bằng chứng

- File/commit/PR:
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:

## 5. Tự đánh giá

...
