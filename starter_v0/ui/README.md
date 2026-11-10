# Web UI — Research Agent (CP5)

React (Vite) frontend + FastAPI backend. The backend reuses the agent loop of
`chat.py` (`run_model_tool_loop`, `write_transcript`), so the UI behaves exactly
like the CLI and every browser session writes `starter_v0/transcripts/ui_*.transcript.json`.

```text
ui/
  server.py        # FastAPI: /api/info, /api/chat, /api/reset + serves web/dist
  web/             # React app (src/App.jsx, src/ToolTrace.jsx, src/api.js, src/styles.css)
```

## Chạy (Windows PowerShell)

Yêu cầu: `starter_v0/.env` đã có `GEMINI_API_KEY` và các key tool; Node.js ≥ 18.

```powershell
cd starter_v0
.\.venv\Scripts\python -m pip install -r requirements.txt   # có fastapi + uvicorn

cd ui\web
npm install
npm run build                                               # tạo ui/web/dist

cd ..
..\.venv\Scripts\python -m uvicorn server:app --port 8000   # mở http://localhost:8000
```

Link dùng thử cho team khác (terminal thứ hai, giữ chạy suốt buổi demo):

```powershell
winget install --id Cloudflare.cloudflared
cloudflared tunnel --url http://localhost:8000              # in ra https://<random>.trycloudflare.com
```

Dev mode (hot reload): chạy backend như trên, rồi `cd ui\web; npm run dev` và mở http://localhost:5173
(Vite chuyển `/api` sang cổng 8000).

## Cấu hình (env, tuỳ chọn)

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `UI_PROVIDER` | `gemini` | provider như `chat.py --provider` |
| `UI_MODEL` | mặc định của provider | model override |
| `UI_VERSION` | `v4` | nhãn version ghi vào transcript (`artifact_version` = nhãn + hash prompt/tools) |
| `UI_MAX_TURNS` | `15` | số lượt tối đa mỗi phiên trình duyệt (bảo vệ quota API khi mở link public) |
| `UI_TRANSCRIPTS_DIR` | `starter_v0/transcripts` | nơi ghi transcript |

## Guardrail

- Mỗi câu trả lời hiển thị **mọi tool call, arguments và kết quả thô**; tool lỗi được tô đỏ, lỗi provider hiện nguyên văn — UI không che lỗi.
- Giới hạn lượt mỗi phiên và độ dài tin nhắn (2000 ký tự); không lộ API key hay `.env` ra frontend.
- Không cấu hình `TELEGRAM_BOT_TOKEN` khi mở link public: lúc đó `send` chỉ trả error dict, người ngoài không thể đăng lên channel. Sidebar hiển thị trạng thái Telegram.
