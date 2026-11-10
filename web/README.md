# Research Agent Web

Giao diện chat cho research agent của nhóm Ban5 (Next.js + React + Tailwind + shadcn/ui).
Hiển thị từng bước agent chọn tool, tham số, kết quả; hỏi lại khi thiếu thông tin;
hộp xác nhận trước khi `send`; tải transcript JSON của phiên chat.

## Kiến trúc

```
Trình duyệt ──► web (Next.js :3000) ──/api/*──► starter_v0/server.py (FastAPI :8000) ──► agent + tool thật
```

Backend chạy local (tool chậm, cần key trong `starter_v0/.env`). Next.js chỉ proxy `/api/*`
sang backend nên không cần CORS. Phản hồi được stream bằng Server-Sent Events.

## Chạy

Terminal 1 (backend, từ `starter_v0/`):

```bash
source .venv/bin/activate
pip install -r requirements.txt
python server.py --provider openai --version v2
```

Terminal 2 (giao diện, từ `web/`):

```bash
npm install
npm run dev          # http://localhost:3000
```

Chia sẻ link cho người ngoài nhóm dùng thử:

```bash
cloudflared tunnel --url http://localhost:3000
```

Đổi địa chỉ backend bằng biến môi trường `API_ORIGIN` (mặc định `http://127.0.0.1:8000`).

## Transcript

Mỗi phiên chat được ghi vào `starter_v0/transcripts/*.transcript.json` (cùng định dạng với `chat.py`,
thêm `"source": "web_ui"`). Key và token bị che trước khi ghi. Nút **Tải transcript** trên giao diện
tải đúng file đó.

## Phím tắt

- `Enter` gửi, `Shift + Enter` xuống dòng
- `⌘K` / `Ctrl + K` chat mới
