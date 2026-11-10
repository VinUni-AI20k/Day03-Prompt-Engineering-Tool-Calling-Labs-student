# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: NhomSNN
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: Gemini — `gemini-3.8-flash` (model mặc định của `providers/gemini_provider.py`; xem `provider`/`model` trong `starter_v0/runs/v0_B_base_gemini_*.json`, `v1_B_base_gemini_*.json`)
- Provider/model của UI và live chat: cũng Gemini — `gemini-3.8-flash` (mặc định trong `starter_v0/app.py`; đổi bằng `AGENT_PROVIDER`/`AGENT_MODEL`)

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent cho tin tức AI/công nghệ: tìm tin trên web và trên X (theo từ khóa hoặc theo tài khoản), đọc nội dung một URL, tra arXiv và policy nội bộ, rồi tổng hợp thành digest markdown. Agent **hỏi lại** khi yêu cầu thiếu thông tin (không rõ tài khoản, URL…) và **chỉ gửi lên Telegram sau khi người dùng xác nhận**.

**Cách chạy UI:**

```bash
cd starter_v0
pip install -r requirements.txt      # đã thêm streamlit
streamlit run app.py                 # http://localhost:8501
```

UI mặc định dùng Gemini `gemini-3.8-flash` — cùng model với base eval v0–v3 (cần `GEMINI_API_KEY` trong `starter_v0/.env`); đổi ở sidebar hoặc qua biến môi trường `AGENT_PROVIDER`/`AGENT_MODEL`. Nhãn version được UI tự nhận bằng cách so `prompt_hash`/`tools_hash` với `artifacts/version_log.csv` (không khớp → `unversioned`). Chat terminal tương đương: `python chat.py --provider gemini --version v3`.

UI hiển thị từng tool call (tên, args, kết quả, lỗi nếu có) và lưu transcript vào `starter_v0/transcripts/ui_*.transcript.json`. Sidebar cho chọn provider/model/version và hiện `prompt_hash`/`tools_hash` đang chạy.

**Link dùng thử (deploy):**

```bash
# Instance public: env riêng không có token Telegram (xem mục 5)
DAY03_ENV_FILE=<env_không_telegram> streamlit run app.py --server.port 8502
cloudflared tunnel --url http://localhost:8502
```

URL: https://streams-stars-bucks-details.trycloudflare.com

> Link `trycloudflare.com` là tạm thời, chỉ sống khi máy chạy UI còn bật streamlit + cloudflared.

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin, rồi chờ lượt trả lời | không |
| timeline | Lấy bài đăng gần đây của một tài khoản X (handle không có `@`) | không |
| social_search | Tìm bài đăng trên X theo từ khóa (`Latest` / `Top`) | không |
| lookup | Tìm trên web qua Tavily (`topic` general/news, `timeframe`) | không |
| fetch | Đọc nội dung một URL cụ thể qua Firecrawl | không |
| format | Trình bày các item đã thu thập thành digest markdown | không |
| send | Gửi text lên Telegram channel của nhóm — chỉ khi đã xác nhận (`confirmed=true`) | không |
| policy | Tra cứu policy nội bộ công ty (markdown) | không |
| papers | Tìm paper trên arXiv | không |
| paper_text | Tải PDF arXiv và trích text | không |
| github_repo | Đọc metadata repo GitHub công khai theo `owner/repo`: mô tả, số sao, fork, ngôn ngữ, thời điểm cập nhật | **có** |

### A3. Câu hỏi mẫu để thử

1. "Tin tức mới nhất về AI agent trong tuần này là gì?" → `lookup` (topic=news, timeframe=week)
2. "Sam Altman gần đây đăng gì trên X?" → `timeline` (screenname=sama)
3. "Mọi người trên X đang nói gì nổi bật về GPT-5?" → `social_search` (search_type=Top)
4. "Tóm tắt giúp tôi bài viết này" → agent hỏi lại URL (`clarify`), sau đó `fetch`
5. "Tổng hợp tin AI hôm nay rồi gửi lên Telegram" → tổng hợp xong, agent hỏi xác nhận trước khi `send`
6. "Repo psf/requests có bao nhiêu sao, viết bằng ngôn ngữ gì?" → `github_repo` (repo=psf/requests)

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

- **Model mặc định không dùng được (HTTP 402).** Provider OpenRouter trong starter mặc định gọi `openai/gpt-4o-mini` (`starter_v0/providers/openrouter_provider.py`). Preflight trả `Error code: 402 - Insufficient credits. This account never purchased credits` vì tài khoản OpenRouter của nhóm chưa nạp credit. Nếu chạy eval với model này, mọi case sẽ là `provider_error`, run không hợp lệ (`provider_error_cases > 0`).
  - **Xử lý:** thử các model `:free` có tool calling trên OpenRouter; một số bị 429 (server free quá tải) và tài khoản chưa nạp credit chỉ có quota request/ngày rất thấp — không đủ cho 4 lần base eval + eval nhóm + live chat. Nhóm chuyển sang provider **Gemini, model `gemini-3.8-flash`** (model mặc định của `providers/gemini_provider.py`) cho toàn bộ base eval v0–v3, eval nhóm, UI và live chat, để mọi metric và transcript dùng cùng một model.
  - **Bằng chứng:** [evidence/preflight_openrouter.txt](evidence/preflight_openrouter.txt) (output preflight của cả hai model).
  - **Rủi ro còn lại:** Gemini cũng có giới hạn request; run nào có `provider_error_cases > 0` phải chạy lại, không dùng làm bằng chứng. Mọi thành viên chạy eval/chat phải có `GEMINI_API_KEY` và dùng đúng `gemini-3.8-flash`.
- **Link public + tool `send`.** Khi mở UI ra internet bằng Cloudflare Tunnel, bất kỳ ai có link đều có thể yêu cầu agent gửi tin lên Telegram; với prompt starter ("cứ gửi luôn"), agent sẽ gửi mà không hỏi lại.
  - **Xử lý:** instance UI public chạy với file env riêng (`DAY03_ENV_FILE`) không chứa `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID`, nên `send` trả lỗi thay vì gửi thật; UI hiển thị lỗi đó (không che). Transcript gửi Telegram thật chỉ quay trên máy nhóm, sau khi prompt v3 có boundary xác nhận.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
