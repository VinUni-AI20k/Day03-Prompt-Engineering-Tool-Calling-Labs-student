# UI — cửa sổ chat DNH team

Transcript kiểu Gemini: bubble phải = bạn, chữ trái = DNH team agent.
Gọi cùng tool loop như `chat.py`, ghi transcript vào `transcripts/` **khi có tin nhắn đầu** (không tạo file rỗng lúc mở server).

Mỗi trình duyệt có `session_id` riêng (localStorage + header `X-Session-Id`) — nhiều người mở link không dùng chung một history.
Nút **Xóa cuộc trò chuyện** gọi `POST /api/reset` để xóa cả UI lẫn history server.

Server dùng **stdlib** (`http.server`) — không thêm package bắt buộc.
Các SDK provider vẫn nằm ở `starter_v0/requirements.txt`.

## Chạy (từ `starter_v0/`)

```bash
cd starter_v0
source .venv/bin/activate   # nếu có
pip install -r requirements.txt
python -m ui --provider openrouter --version v3
# → http://127.0.0.1:8787  (bind mặc định 0.0.0.0 để tunnel/LAN mở được)
```

Public link nhanh:

```bash
cloudflared tunnel --url http://127.0.0.1:8787
```

| Flag / env | Mặc định |
|------------|----------|
| `--host` / `UI_HOST` | `0.0.0.0` |
| `--port` / `UI_PORT` | `8787` |
| `--provider` | bắt buộc |
| `--version` | bắt buộc (vd `v3`) |

## API

| | |
|--|--|
| `POST /api/chat` | header `X-Session-Id` + `{"text":"..."}` → `assistant_text` + `summary` |
| `POST /api/reset` | xóa history + mở transcript mới cho session |
| `POST /api/model` | chọn model (openrouter) theo session |
| `GET /api/health` | provider, model, version; kèm transcript nếu có `X-Session-Id` |
