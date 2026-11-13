# NEXUS — Tổng quan và hướng dẫn chạy

Project là agent nghiên cứu: model chọn tool để tìm/đọc nguồn, hỏi lại khi thiếu dữ liệu và xây research board. UI cho xem nguồn, graph, tool args/result và pipeline qua từng vòng.

**Tất cả lệnh bên dưới chạy trong `starter_v0/`, bằng PowerShell.**

## 1. Project gồm những gì?

| Thành phần | Vai trò |
| --- | --- |
| `app.py` | UI Streamlit: chat, research desk, pipeline và execution log |
| `chat.py` | Chat trực tiếp trong terminal; lưu transcript |
| `run_eval.py` | Chạy bộ case, chấm routing/args và lưu run JSON |
| `artifacts/system_prompt.md` | Chính sách chung cho agent |
| `artifacts/tools.yaml` | Mô tả tool, schema args, khi dùng/không dùng |
| `providers/` | Adapter gọi model; project đang dùng Groq |
| `tools/__init__.py` | Registry `TOOL_FUNCTIONS` và chuyển YAML thành schema |
| `tools/research_board/` | Tool mới: Tavily → chuẩn hóa/gộp URL → nhóm domain → graph/provenance/coverage |
| `ui/runtime.py`, `ui/pipeline.py` | Vòng model/tool, giới hạn thực thi, guard gửi và hiển thị trace |
| `data/`, `tests/` | Bộ eval và kiểm thử offline |
| `runs/`, `transcripts/` | Bằng chứng eval và hội thoại |
| `artifacts/cp2/`, `cp3/`, `cp3_v2/`, `cp4_cp5/`, `cp5_pipeline/` | Snapshot, phân tích và kết quả theo checkpoint |

Luồng **Agent chat trên UI**:

```text
Câu hỏi → system prompt + policy UI + history
        → Groq (nhận tool schema riêng)
        → đề xuất tool + args → runtime/registry → tool result
        → kết quả quay vào context → model tiếp tục hoặc dừng
        → trả lời / clarify chờ user / blocked / lỗi / chạm giới hạn
```

Research desk gọi thẳng `research_board`, không qua model. Tool này truy vấn Tavily trực tiếp, không gọi các tool lookup/social ở bên trong. URL overlap không phải xác minh claim.

## 2. Chuẩn bị terminal

Trên máy hiện tại đã có môi trường Conda `lab3`:

```powershell
conda activate lab3
cd D:\StudiAI20K\lab3\K5-L3B-DAY03-agentcuibap-ResearchAgentToolEval\starter_v0
python --version
```

Nếu PowerShell chưa dùng được `conda activate`, có thể thay `python` trong từng lệnh bằng executable đã cài:

```powershell
& "D:\miniconda3\envs\lab3\python.exe" --version
```

Chỉ khi cài trên môi trường mới:

```powershell
python -m pip install -r requirements.txt
if (-not (Test-Path -LiteralPath .env)) { Copy-Item -LiteralPath .env.example -Destination .env }
```

Điền key trong `.env` local. Máy hiện tại đã có `.env`; không chép đè từ file mẫu.

| Biến cấu hình | Dùng cho |
| --- | --- |
| `GROQ_API_KEY` | Model Groq |
| `GROQ_MODEL` | Model mặc định CLI/eval, hiện cấu hình 120b |
| `TAVILY_API_KEY` | `lookup`, `research_board` |
| `FIRECRAWL_API_KEY` | `fetch` |
| `RAPIDAPI_KEY`, `RAPIDAPI_TWITTER_HOST` | `timeline`, `social_search` |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Gửi Telegram ở CLI nếu có cấu hình và xác nhận |

UI chỉ dùng Groq trong bản hiện tại. Các provider khác có ở CLI. Có key chưa chứng minh API còn quota. `.env` được ignore; chỉ chia sẻ `.env.example` không chứa secret.

## 3. Chạy UI — cách demo chính

Nếu server đang chạy, mở ngay **http://localhost:8501**. Nếu cần khởi động:

```powershell
$env:NEXUS_MODEL = "openai/gpt-oss-20b"
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
```

`NEXUS_MODEL` chỉ đổi model UI; không đổi model của CLI/eval. UI dùng 20b vì phiên 120b trước đó gặp quota. Nếu port 8501 đã bận, dùng UI đang chạy hoặc đổi `--server.port 8502` rồi mở http://localhost:8502.

Các tab:

- **Agent chat:** gửi yêu cầu để model tự chọn tool. Câu mẫu chỉ điền ô nhập; bấm gửi mới chạy API.
- **Pipeline & prompt:** bấm node xem kiến trúc; xem prompt/policy/schema và chọn lượt để đọc payload từng vòng. Lượt cũ không có snapshot thì UI báo thiếu.
- **Research board:** form chạy tool trực tiếp, xem graph, cards, coverage và raw result.
- **Execution log:** đọc args/result/error từng lượt; tải transcript ở sidebar.

Ba tình huống demo:

1. `Tạo research board về pin thể rắn, general, month, tối đa 3 kết quả.`
2. `Đọc bài viết giúp tui, nhưng tui chưa đưa URL.` Sau khi agent hỏi, bổ sung `URL là https://www.example.com/`.
3. `Gửi bản nháp "Bản tin đang chờ kiểm tra nguồn" lên Telegram; tui chưa duyệt nội dung.` Quan sát hỏi lại hoặc bị chặn, không tự nhận đã gửi.

UI khóa `send` kể cả `confirmed=true`. CLI có thể thực thi gửi nếu được cấu hình và cho phép; hai đường có policy khác nhau. UI giới hạn 4 vòng model, 8 tool call/lượt và 30 lượt/phiên. Nút **Phiên mới** xóa history của phiên hiện tại.

Muốn dừng server chạy trong terminal, nhấn `Ctrl+C` ở terminal đó.

## 4. Chat trong terminal

```powershell
python chat.py --provider groq --model openai/gpt-oss-20b --version demo-current
```

Nhập câu hỏi, Enter để gửi; gõ `/exit` để thoát. Transcript tự lưu trong `transcripts/`. Đây là CLI gốc, không có toàn bộ deployment policy/guard riêng của UI.

Kiểm tra riêng model có trả structured tool calls không:

```powershell
python scripts/preflight_provider.py --provider groq --model openai/gpt-oss-20b
```

Preflight có gọi API Groq nhưng không thực thi tool được đề xuất; kết quả OK không chứng minh Tavily/Firecrawl/RapidAPI hoạt động.

## 5. Chạy test và eval

**Unit/contract/UI test — không cần gọi mạng thật:**

```powershell
python -B -m pytest -p no:cacheprovider -q
```

Bằng chứng lần chốt hiện có: **195 passed, 0 failed, 0 skipped**, tại [artifacts/cp5_pipeline/pytest.txt](artifacts/cp5_pipeline/pytest.txt).

**Eval bản artifact hiện tại — có gọi API và dùng quota:**

```powershell
python run_eval.py --provider groq --model openai/gpt-oss-120b --version verify-current --suite base --eval-cases data/eval_base.json
python run_eval.py --provider groq --model openai/gpt-oss-120b --version verify-current --suite group --eval-cases data/eval_group.json
```

Chạy từng lệnh, đọc kết quả rồi mới tiếp tục. `--suite` chỉ là nhãn, không tự chọn/filter case; cần chỉ rõ `--eval-cases`. Group có 10 case: 5 single, 5 multi. Run mới tự sinh file có timestamp trong `runs/`; nhật ký version cần được ghi và đối chiếu riêng.

**Quan trọng:** `--version` chỉ đặt nhãn, không tự nạp snapshot. Artifact hiện tại có 11 tool, khác bộ 10 tool CP2. Nếu muốn thử đúng prompt/tool của v3 cũ:

```powershell
python run_eval.py --provider groq --model openai/gpt-oss-120b --version verify-v3-snapshot --suite base --eval-cases data/eval_base.json --system-prompt artifacts/cp2/v3/system_prompt.md --tools artifacts/cp2/v3/tools.yaml
```

Đây vẫn là một lần chạy mới; không bảo đảm lặp đúng điểm cũ. Chỉ dùng run hoàn tất đủ case, `provider_error_cases == 0` làm bằng chứng. Khi đổi model/cấu hình phải ghi đúng sự thay đổi đó.

Không sửa nội dung `data/eval_base.json`, `data/eval_research_extension.json` hoặc contract test để tăng điểm.

## 6. Mở link public bằng Cloudflare

Giữ terminal UI hoạt động, mở **terminal thứ hai**:

```powershell
& "$env:TEMP\codex-research-tunnel\cloudflared.exe" tunnel --url http://localhost:8501 --no-autoupdate --protocol http2
```

Đường dẫn trên là binary đã có trên máy hiện tại. Nếu cloudflared đã nằm trong PATH, dùng `cloudflared tunnel --url http://localhost:8501 --no-autoupdate --protocol http2`. Nếu chạy UI port 8502 thì đổi URL tương ứng.

Lấy link `https://...trycloudflare.com` được in ra để chia sẻ. Giữ app, tunnel và máy hoạt động; khởi động lại tunnel có thể đổi link. Dừng tunnel bằng `Ctrl+C` ở terminal của nó.

Link đã tạo cho phiên demo: https://connection-hawaii-narrative-mom.trycloudflare.com — là link tạm, cần kiểm tra còn hoạt động trước khi trình bày.

## 7. Bằng chứng và kết quả đã có

| Phần | Bằng chứng / kết quả |
| --- | --- |
| CP1–CP2 | v0: 65%, v1: 80%, v2: 85%, v3: 90%, v4: 90%; cùng Groq 120b, đủ 20 case và 0 lỗi provider |
| CP3 | `research_board` đủ implementation, TOOL.md, registry, YAML; test happy/input xấu/error và bản mở rộng so sánh |
| CP4 | Group 10/10 PASS routing/args; G09/G10 vẫn có HTTPError của tool, G05 cần review nội dung |
| CP5 | UI, pipeline, CLI transcript 20b cùng lượt xác nhận tiếp nối; AppTest/API thật được lưu riêng với test offline |
| Kiểm thử cuối | 195 passed, 0 failed/skipped; chưa xác nhận browser visual/mobile hoặc dùng thử từ nhóm khác |

- [Báo cáo nhóm](../report/team/group_report.md), [TEAM.md](../TEAM.md).
- [Báo cáo Lê Nguyễn Anh Nhân](../report/team/2A202603838_LeNguyenAnhNhan.md).
- [Nhật ký CP2](artifacts/cp2/experiment_log.md), [CP3 v2](artifacts/cp3_v2/README.md), [CP4/CP5](artifacts/cp4_cp5/README.md), [pipeline và pytest cuối](artifacts/cp5_pipeline/README.md).

## 8. Lỗi thường gặp

| Hiện tượng | Kiểm tra / xử lý |
| --- | --- |
| `ModuleNotFoundError` | Dùng đúng Python của `lab3`; cài dependency vào chính môi trường đó |
| Không tìm thấy file prompt/tools | Chuyển vào `starter_v0/` trước khi chạy lệnh |
| Port 8501 đang được dùng | Mở server hiện có hoặc khởi động trên port 8502 |
| Groq 401/429 | Kiểm tra key/quota; UI có thể chọn 20b riêng, eval cần ghi nhận nếu đổi model |
| Tool social trả 403/429 | Kiểm tra quyền/gói/quota RapidAPI; tách lỗi dịch vụ khỏi lỗi routing |
| Model nói thành công nhưng tool báo lỗi | Đọc execution log/result thực tế; không lấy lời model thay cho trạng thái tool |
| Link Cloudflare không mở được | Kiểm tra app/tunnel/máy còn chạy và dùng link mới nhất |

Quy định gốc: [README lab](../README.md), [RULES](../RULES.md), [SUBMISSION](../SUBMISSION.md). Hướng dẫn key: [TOOL-SETUP](../docs/TOOL-SETUP.md).
