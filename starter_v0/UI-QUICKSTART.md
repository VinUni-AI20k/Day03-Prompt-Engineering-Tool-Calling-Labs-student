# Chạy UI local

Mở PowerShell trong `starter_v0`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Mở http://localhost:8501. Dừng server bằng Ctrl+C.

- **Thử tool trực tiếp**: chọn deduplicate/citation_audit và chạy dữ liệu mẫu;
  không cần key AI. Chọn lookup để tìm kiếm thật bằng Tavily (dùng quota).
- **Thử xác nhận**: giữ chọn mô phỏng, bấm Xem trước gửi rồi Xác nhận gửi
  hoặc Hủy gửi. Mô phỏng không gọi Telegram.
- **Gửi thật**: bỏ chọn mô phỏng, điền TELEGRAM_BOT_TOKEN và
  TELEGRAM_CHAT_ID trong .env, khởi động lại server. Kiểm tra nội dung trước
  khi bấm Xác nhận gửi. Một xác nhận chỉ cho một lần gửi; không tự retry.
- **Chat**: chọn provider khớp key trong .env; ví dụ openai. Có thể hỏi
  "Tìm kiếm thông tin về AI agent evaluation" hoặc "Gửi Telegram: Xin chào nhóm".
  Chat gọi API thật và dùng quota. Tool call/kết quả xuất hiện bên dưới.
- Transcript được lưu ở `transcripts/ui_*.transcript.json`, kèm thông tin
  phiên bản/hash, hoặc tải bằng nút trong sidebar. Không đưa key vào chat.

Kiểm tra UI offline: `python -m pytest tests/test_ui.py -v` bằng Python .venv.
Không cần Web UI để chạy những unit test đã có. UI này chạy trên máy,
chưa được triển khai lên Internet.
