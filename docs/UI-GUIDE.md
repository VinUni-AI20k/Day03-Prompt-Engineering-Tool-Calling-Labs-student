# CP5 — Research desk trên main của nhóm

UI dùng trực tiếp `chat.py`, prompt, declaration và registry **14 tool** lấy từ main GitHub `a557a55`. Không dùng bộ prompt/tool/eval của bản thử nghiệm local trước đó.

## Cài và chạy

Từ root repo trên Windows:

```powershell
py -3 -m venv venv
& .\venv\Scripts\python.exe -m pip install -r starter_v0/requirements.txt
Copy-Item starter_v0/.env.example starter_v0/.env
# Điền OPENAI_API_KEY và key tool trong .env; không commit file này.
& .\starter_v0\scripts\start_ui.ps1
```

Nếu đã có venv và .env thì giữ nguyên, chỉ cài dependency còn thiếu. UI: http://127.0.0.1:8501. Đổi cổng bằng `-Port 8511`. Chạy trực tiếp từ `starter_v0/`:

```powershell
& ..\venv\Scripts\python.exe -m streamlit run app.py --server.address=127.0.0.1 --server.port=8501 --server.enableAgentApi=false
```

Provider/model giống các run nhóm: OpenAI / gpt-4o-mini. `github_search` dùng GitHub public API; ba tool xử lý nguồn chạy local; các tool web/X cần key tương ứng. Tool lỗi được hiển thị và lưu nguyên trạng, không giả kết quả thành công. Telegram chỉ hoạt động nếu có key và user xác nhận; demo hiện không cấu hình gửi thật.

## Dùng thử và chia sẻ

Nhập câu hỏi mẫu ở A3 của báo cáo nhóm; tiếp tục trả lời nếu agent hỏi thông tin hoặc xác nhận. Có thể xem tool/arguments/results dưới từng lượt, tải transcript JSON và tạo phiên mới. Mỗi phiên tối đa 20 lượt, mỗi lượt 6000 ký tự và 4 vòng tool.

Đặt `DEMO_ACCESS_CODE` trong `.env` trước khi chia sẻ; khởi động lại UI sau khi đổi mã. Nếu không đặt thì UI local không yêu cầu mã. API key nằm trên máy host.

Mở terminal thứ hai:

```powershell
& .\starter_v0\scripts\share_ui.ps1 -Port 8501
```

Script dùng `cloudflared` trên PATH hoặc `.tools/cloudflared.exe`. Chép URL `https://…trycloudflare.com` vào A1, gửi mã riêng cho người thử. Quick tunnel chỉ tồn tại khi máy host, UI và tunnel còn chạy; restart tunnel sẽ đổi URL. Server chia sẻ không bật agent API.

Phiên đang chạy khi hoàn thiện CP5 dùng cổng **8511**; mã tự sinh lưu tại `.runtime/team-demo-access.txt` (được gitignore), chỉ có hiệu lực trên tiến trình hiện tại. Nếu chạy lại bằng script, đặt mã của riêng bạn trong `.env`.

## Tái lập kiểm tra

Từ `starter_v0/`:

```powershell
& ..\venv\Scripts\python.exe -m pytest
& ..\venv\Scripts\python.exe run_eval.py --provider openai --model gpt-4o-mini --version cp5-team-recheck --suite base --eval-cases data/eval_base.json
& ..\venv\Scripts\python.exe run_eval.py --provider openai --model gpt-4o-mini --version cp5-team-recheck --suite group --eval-cases data/eval_group.json
& ..\venv\Scripts\python.exe scripts/cp5_live_demo.py
```

Eval và live demo gọi API thật, có thể tốn quota. `cp5_live_demo.py` nhập kịch bản 5 lượt vào CLI thật, không phải unit test hoặc bằng chứng người ngoài nhóm đã thử. Kịch bản hủy gửi; không gửi Telegram. Eval group có case gọi `send(confirmed=true)`, vì vậy cần dùng môi trường không cấu hình Telegram nếu chỉ kiểm tra routing.

Unit test offline dùng fake provider/mocked HTTP. QA runtime chỉ bật agent API trên localhost riêng, không đưa cấu hình đó vào server chia sẻ. Xem `starter_v0/analysis/cp5_team_qa.md` để biết kết quả và giới hạn thực tế.
