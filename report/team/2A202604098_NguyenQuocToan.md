# Báo cáo cá nhân — NguyenQuocToan-2A202604098

## 1. Thông tin thành viên

- Họ tên: Nguyễn Quốc Toàn
- MSSV: 2A202604098
- Email: 
- GitHub: nguyenquoctoan0310
- Lớp: K5 - L3B
- Nhóm: Nhóm Bá Khí (`NhomBaKhi`)

## 2. Phần việc phụ trách

Phụ trách hoàn thiện bộ unit test cho các tool nghiên cứu trong `starter_v0`, tập trung vào việc đối chiếu với format mẫu trong `test_tools_examples.py` và bảo đảm test chạy offline.

## 3. Đóng góp cụ thể

- Hoàn thiện các test core cho `clarify`, `format`, `lookup`, `fetch`, `timeline`, `social_search` và `policy`.
- Bổ sung test guardrail cho tool `send`, gồm trường hợp gửi thành công và thiếu biến môi trường Telegram.
- Bổ sung test cho `papers`, gồm mapping dữ liệu Atom/arXiv và xử lý HTTP error.
- Bổ sung test cho `paper_text`, gồm tải PDF giả lập, trích xuất text, URL không hợp lệ và lỗi mạng.
- Bảo đảm mọi request HTTP đều được mock bằng fixture `fake_http`; rate limit và PDF extraction được monkeypatch khi cần.
- Hỗ trợ kiểm tra boundary Telegram qua test `send`: chỉ gửi khi `confirmed=true`, thiếu cấu hình thì trả về error dict và không phát sinh request.

## 4. Bằng chứng

- File/commit/PR: `starter_v0/tests/test_tools_todo.py`.
- Bằng chứng Telegram bonus của nhóm: `starter_v0/transcripts/v3_gemini_20261110T235739095905.transcript.json`; flow thể hiện agent gọi `clarify(response_type="yes_no")`, người dùng xác nhận, sau đó gọi `send(confirmed=true)` và nhận `status: "sent"`.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Dùng Codex để đối chiếu `test_tools_examples.py`, registry `TOOL_FUNCTIONS` và implementation của từng tool.
  - Dùng `pytest` để chạy test tập trung và toàn bộ test suite.
  - Kết quả: `31 passed` cho `test_tools_todo.py` và `159 passed` cho toàn bộ thư mục `tests/`.
  - Kiểm tra các test không gọi mạng thật bằng fixture chặn network và mock HTTP.

## 5. Tự đánh giá

Hoàn thành đúng phần việc được giao, bổ sung coverage cho các tool còn thiếu và giữ test theo format của file mẫu. Kết quả kiểm thử toàn bộ đều đạt, không có test failed hoặc skipped. Tự đánh giá: Hoàn thành tốt.
