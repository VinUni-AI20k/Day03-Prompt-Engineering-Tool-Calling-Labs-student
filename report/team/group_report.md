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

- **`system_prompt.md` (v1 → v3):** bỏ 3 chỉ dẫn xấu của starter. v1 viết lại đoạn "đoán thay vì hỏi" (kể cả đoán Sam Altman / đoán URL); v2 bỏ "gửi/đăng ngay không cần xác nhận" và "luôn làm trong một bước, chỉ chọn một tool", thay bằng: hỏi lại khi thiếu thông tin thiết yếu, mọi hành động gửi ra ngoài phải có xác nhận rõ, được dùng nhiều tool khi cần. v3 thêm **Tool Routing Policy**: bảng *dùng khi / không dùng khi* cho 10 tool, quy ước argument, chuỗi routing (ví dụ `lookup(topic=news)` → `fetch` → `format`), quy trình 4 bước trước khi `send`, và cách xử lý khi tool lỗi.
- **`tools.yaml` (v4):** viết lại description của 10 tool có sẵn (làm gì, khi nào dùng / không dùng) và description từng tham số theo convention: handle không có `@`; `query` chỉ giữ chủ đề cốt lõi (không thêm "news", từ chỉ thời gian, bản dịch); `topic=news` cho tin tức; map "hôm nay/tuần này" → `timeframe`; `search_type` Top/Latest; `clarify.response_type=yes_no` khi xin xác nhận gửi; `send.confirmed=true` chỉ sau khi người dùng đã xác nhận ở lượt trước.
- **Tool mới `github_repo`** (`starter_v0/tools/github_repo/`): đọc metadata repo GitHub công khai theo `owner/repo` (mô tả, số sao, fork, ngôn ngữ, thời điểm cập nhật) qua GitHub REST API, không cần key. Agent gọi khi người dùng hỏi thông tin một repo đã biết `owner/repo`; thiếu `owner/repo` thì `clarify`, không đoán. Input sai định dạng hoặc API lỗi → trả error dict, không raise.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (starter) | — (đo điểm xuất phát) | — | case 0.70 · routing 0.80 · args 0.70 · multiturn 0.83 | `starter_v0/runs/v0_B_base_gemini_20261110T181043437185.json` |
| v1 | `system_prompt.md` | Đoạn "đừng hỏi lại, cứ đoán rồi gọi tool ngay" khiến agent gọi tool sai → viết lại thành "chỉ giả định khi rủi ro thấp, không tự chọn tài khoản/URL" sẽ giảm gọi tool sai | case 0.70 · routing 0.80 · args 0.70 · multiturn 0.83 | case 0.70 · routing 0.80 · args 0.70 · multiturn **1.00** | `starter_v0/runs/v1_B_base_gemini_20261110T183204301927.json` |
| v2 | `system_prompt.md` | Các lệnh còn sót của starter đều ép agent tự hành động thay người dùng ("gửi ngay", "chỉ một bước, một tool", vẫn còn giả định khi thiếu thông tin quan trọng) → thay bằng: hỏi lại khi thiếu thông tin thiết yếu, xác nhận trước hành động ra ngoài, cho phép nhiều bước/nhiều tool | case 0.70 · routing 0.80 · args 0.70 · multiturn 1.00 | case **0.80** · routing **0.95** · args **0.80** · multiturn 0.83 | `starter_v0/runs/v2_B_base_gemini_20261110T185059726081.json` |
| v3 | `system_prompt.md` | Thêm Tool Routing Policy (bảng dùng/không dùng, argument conventions, routing sequence) sẽ cải thiện chọn tool và args | case 0.80 · routing 0.95 · args 0.80 · multiturn 0.83 | case **0.85** · routing **1.00** · args **0.85** · multiturn **1.00** | `starter_v0/runs/v3_B_base_gemini_20261110T190416427568.json` |
| v4 | `tools.yaml` | 3 case còn FAIL ở v3 đều là lỗi convention args (model tự thêm chữ vào `query`; `clarify` dùng `text` thay vì `yes_no` khi xin xác nhận) → ghi convention ngay trong description tham số của `tools.yaml` sẽ sửa được | case 0.85 · routing 1.00 · args 0.85 · multiturn 1.00 | _(điền từ run v4)_ | _(điền `runs/v4_B_base_gemini_*.json`)_ |

Tất cả run dùng Gemini `gemini-3.8-flash`, 20/20 case được đo, `provider_error_cases = 0`. v0–v3 dùng cùng `tools_hash` `e69bc53ed884` (`tools.yaml` của starter, chưa có `github_repo`); v4 có `tools_hash` `a19f8e802c47` vì đổi `tools.yaml` và đã gồm tool mới `github_repo`.

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

Run v0 (`starter_v0/runs/v0_B_base_gemini_20261110T181043437185.json`): 6/20 case FAIL.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_tool (thực chất lỗi arg) | `lookup(query="AI news artificial intelligence", topic=news, timeframe=day)` | Đúng tool, nhưng `query` bị thêm "news artificial intelligence" thay vì `AI` | Vẫn FAIL đến v3 (query bị mở rộng) → v4: description `lookup.query` "chỉ chủ đề cốt lõi, không thêm news/bản dịch" |
| R10_missing_handle | missing_info | `timeline(screenname="sama", limit=5)` | Không rõ tài khoản nào nhưng agent tự đoán Sam Altman (do prompt starter dặn) thay vì `clarify` | v1 viết lại đoạn đoán nhưng vẫn FAIL (vẫn "make assumptions and proceed"); v2 bắt hỏi lại khi thiếu thông tin thiết yếu → PASS từ v2 |
| R11_missing_url | missing_info | `fetch(url="https://openai.com/news")` | "Bài này" không có URL nhưng agent tự bịa URL | Như R10: v1 vẫn FAIL, v2 PASS |
| R12_confirm_before_send | wrong_boundary | `send(text="Bản tin tổng hợp…", confirmed=true)` | Gửi Telegram ngay, không xin xác nhận (prompt starter: "just go ahead and do it") | v1 đã chuyển sang `clarify` nhưng `response_type=text`; v2 bỏ lệnh gửi ngay, thêm xác nhận, nhưng agent lại tra `policy`; v3 (quy trình 4 bước trước `send`) hỏi lại nhưng vẫn `text` → v4: `clarify.response_type=yes_no` bắt buộc khi xin xác nhận |
| R13_parallel_web_and_tweets | wrong_tool | `lookup(query="tin tức trí tuệ nhân tạo AI", …)` | Thiếu `social_search` (prompt starter ép "chỉ chọn một tool") và query bị mở rộng | v2: được gọi nhiều tool → có cả `lookup` + `social_search`; query vẫn bị mở rộng đến v3 → v4 |
| M02_carryover_timeframe | wrong_arg_value | `lookup(query="robotics news", topic=news, timeframe=day)` | Giữ đúng timeframe qua lượt, nhưng query thêm "news" | v3: argument conventions trong prompt → PASS ở v3 |

Ngoài ra v1 phát sinh 1 lỗi mới: **R08_out_of_scope** (`lookup(query="nguyên hàm của x^2")` — câu hỏi toán ngoài phạm vi nhưng vẫn gọi tool) → hết từ v2.

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_papers_routing | single · `wrong_tool`: yêu cầu tìm paper → arXiv, không web/social | `papers` | _chờ run `--suite group` trên v3_ |
| G02_policy_area_routing | single · `wrong_tool`: quy định nội bộ → policy, đúng area | `policy` policy_area=source_citation | _chờ run `--suite group` trên v3_ |
| G03_handle_with_at_sign | single · `wrong_arg_value`: bỏ `@` khỏi handle, giữ limit | `timeline` screenname=karpathy, limit=4 | _chờ run `--suite group` trên v3_ |
| G04_search_type_latest | single · `wrong_arg_value`: "mới đăng gần đây nhất" → Latest | `social_search` search_type=Latest | _chờ run `--suite group` trên v3_ |
| G05_thanks_no_tool | single · `unnecessary_tool`: lời cảm ơn → không gọi tool | no_tool | _chờ run `--suite group` trên v3_ |
| G06_confirmed_send | multi (3) · `wrong_boundary`: user đã xác nhận rõ ở lượt cuối → gửi | `send` confirmed=true | _chờ run `--suite group` trên v3_ |
| G07_missing_topic_then_papers | multi (3) · `missing_info`: chủ đề ở lượt 2, số lượng ở lượt 3 | `papers` max_results=3 | _chờ run `--suite group` trên v3_ |
| G08_switch_web_to_account | multi (3) · `wrong_tool`: đổi từ tin web sang tài khoản cụ thể | `timeline` screenname=ylecun, limit=2 | _chờ run `--suite group` trên v3_ |
| G09_top_carryover_topic | multi (3) · `wrong_arg_value`: giữ query qua các lượt, đổi sang Top | `social_search` query=Llama, search_type=Top | _chờ run `--suite group` trên v3_ |
| G10_github_repo_after_clarify | multi (3) · `missing_info`: thiếu owner/repo ở lượt 1 → **tool mới** | `github_repo` repo=psf/requests | _chờ run `--suite group` trên v3_ |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới `github_repo` | `starter_v0/tools/github_repo/tool.py`, `TOOL.md`; đăng ký trong `starter_v0/tools/__init__.py` và `starter_v0/artifacts/tools.yaml` | Gọi GitHub REST API `GET /repos/{owner}/{repo}` (không cần key), trả `items` gồm title, url, summary, stars, forks, language, updated_at. Gọi thật `psf/requests` → 54,748 sao, Python | Validate `owner/repo` bằng regex trước khi gọi mạng (chặn URL, `.git`, `..`, kiểu sai); mọi lỗi → error dict, không raise; description từ GitHub coi là dữ liệu không đáng tin; giới hạn 60 request/giờ/IP |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py` (3 hàm test `test_github_repo_*`, 19 trường hợp tham số hoá); `pytest` 0 failed, 0 skipped | Happy path assert cả request (method, URL, header `Accept`, timeout) lẫn output; input xấu (8 trường hợp) trả `ValueError` và **không gọi HTTP**; lỗi API 403/404/429/timeout/payload sai trả error dict | Test chạy offline bằng `fake_http`, không gọi mạng thật |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

`github_repo`: 3 hàm test / 19 case. Ví dụ unit test bắt được mà eval không bắt được: model gọi đúng `github_repo(repo="https://github.com/psf/requests")` (đúng tool, args gần đúng) — eval chỉ so tên tool/args nên không biết tool xử lý ra sao; unit test `test_github_repo_invalid_input_returns_error_without_http` kiểm tra tool từ chối URL bằng error dict và không gửi request nào, thay vì ghép thành URL API sai.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output: 112 passed, 0 skipped; `starter_v0/tests/test_tools_todo.py` | Điền hết stub TODO của clarify, format, send, lookup, fetch, timeline, social_search, policy; tìm và sửa 2 bug trong tool có sẵn, giữ regression test | Mọi test chạy offline (`fake_http`), không gọi mạng thật |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

| Bug (tool có sẵn) | Hành vi sai | Sửa | Regression test |
|---|---|---|---|
| `send`: `confirmed` dạng chuỗi | Model gửi `confirmed="false"` (chuỗi) → Python coi là truthy → **tin vẫn được gửi** dù user chưa xác nhận | `tools/send/tool.py`: thêm `_is_confirmed()`, chỉ `True` hoặc chuỗi `"true"` mới là xác nhận | `test_send_string_false_is_not_treated_as_confirmation` |
| `timeline`, `social_search`: `limit <= 0` | `items[:int(limit)]` với `limit=-2` thành `items[:-2]` → trả sai số item; `limit=0` bị đổi thành 5 nhưng âm thì không | `tools/timeline/tool.py`, `tools/social_search/tool.py`: `limit < 1` → dùng mặc định 5 | `test_timeline_non_positive_limit_falls_back_to_default`, `test_social_search_non_positive_limit_falls_back_to_default` |

Cả hai bug này eval không bắt được: eval chỉ kiểm tra model gọi `send`/`timeline` với args nào, không kiểm tra tool xử lý args đó ra sao.

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

- **Fix nào thuộc `system_prompt.md`?** Hành vi và ranh giới chung: không đoán mà hỏi lại (R10, R11), xin xác nhận trước hành động ra ngoài (R12), cho phép nhiều tool trong một lượt (R13), từ chối câu hỏi ngoài phạm vi (R08). Đây là chỉ dẫn xuyên suốt mọi tool nên đặt ở prompt — v2 sửa được R10, R11, R08 chỉ bằng prompt.
- **Fix nào thuộc `tools.yaml`?** Convention của từng tham số: `query` chỉ giữ chủ đề cốt lõi, handle không có `@`, `topic`/`timeframe`, `search_type`, `response_type=yes_no` khi xin xác nhận, `confirmed` là boolean. Bằng chứng: v3 đã ghi convention trong prompt nhưng R03/R13 vẫn bị mở rộng query và R12 vẫn dùng `response_type=text` — model đọc description tham số ngay lúc điền args nên convention đặt ở đó (v4).
- **Failure nào cần review thủ công?** (1) Lỗi `query` (R03, R13): `"AI artificial intelligence news"` vẫn cho kết quả tìm kiếm hợp lý, chấm exact-match coi là FAIL — cần người xem kết quả thật. (2) R12: agent đã hỏi lại trước khi gửi (đúng tinh thần) nhưng FAIL chỉ vì `response_type`. (3) Chất lượng câu trả lời cuối, nguồn trích dẫn và nội dung digest — eval chỉ chấm tool/args, không chấm nội dung.
- **Nếu có thêm một vòng:** đo riêng tool mới — chạy `--suite group` để xem `github_repo` có được gọi đúng sau `clarify` không (G10); nếu model vẫn mở rộng `query`, thử thêm 1–2 ví dụ few-shot ngắn (user → args) vào description của `lookup`.

## 8. Tài liệu tham khảo

-
