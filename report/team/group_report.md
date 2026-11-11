# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa hoàn toàn trên log thật trong `starter_v0/runs/` và `starter_v0/transcripts/`.

## 1. Thông tin nhóm

- Tên nhóm: **Nhóm Bá Khí** (`K5-L3B-DAY03-NhomBaKhi-ResearchAgentToolEval`)
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3:
  - v0–v2: Google Gemini (`gemini-3.5-flash-lite`)
  - v3 & Group Eval: OpenRouter (`openai/gpt-4o-mini`) *(chuyển sang OpenRouter do Gemini Free Tier gặp giới hạn 15 RPM / 503 khi chạy batch 20 cases)*

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

"Research agent đa kênh: hỗ trợ tra cứu tin tức web, bài đăng mạng xã hội X/Twitter, bài báo khoa học arXiv, tra cứu chính sách nội bộ, tự động khử trùng nguồn, tìm kiếm bằng chứng kiểm chứng luận điểm, đối chiếu chủ đề đa nền tảng, tổng hợp bản tin ngắn và gửi bản tin lên Telegram sau khi được người dùng xác nhận rõ ràng."

**Cách chạy UI:** `cd starter_v0 && python -m streamlit run app.py` (dependency `streamlit>=1.30.0` đã được khai báo trong `starter_v0/requirements.txt`).

**Link dùng thử (deploy):**

> Chạy cục bộ qua Streamlit UI theo hướng dẫn ở trên (`http://localhost:8501`).

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi lại người dùng khi thiếu handle/URL hoặc xin xác nhận (`yes_no`) trước khi gửi | Không |
| `timeline` | Lấy các bài đăng/tweet gần đây của một tài khoản X cụ thể (handle không có `@`) | Không |
| `social_search` | Tìm bài đăng/tweet trên mạng xã hội theo từ khóa/chủ đề (`Latest` hoặc `Top`) | Không |
| `lookup` | Tra cứu thông tin tổng quát hoặc tin tức báo chí trên web qua Tavily (`topic`, `timeframe`) | Không |
| `fetch` | Đọc và trích xuất nội dung toàn văn từ một đường dẫn URL cụ thể | Không |
| `format` | Định dạng danh sách các nguồn tin đã thu thập theo khuôn (`brief`, `sections`, `bullets`, `thread`, `daily_ai_vn`) | Không |
| `send` | Gửi bản tin/tin nhắn lên kênh Telegram riêng của nhóm (yêu cầu `confirmed=true`) | Không |
| `policy` | Tìm kiếm quy định và tài liệu chính sách nội bộ công ty | Không |
| `papers` | Tìm kiếm bài báo khoa học trên arXiv | Không |
| `paper_text` | Trích xuất nội dung văn bản từ PDF bài báo arXiv theo ID/URL | Không |
| `topic_radar` | Đối chiếu tin tức báo chí (Tavily) và trao đổi trên X (RapidAPI) cho cùng một chủ đề, đo độ giao thoa từ khóa | **Có** |
| `evidence_finder` | Tìm kiếm bằng chứng và trích đoạn liên quan nhất cho một luận điểm (`claim`) từ nhiều tên miền khác nhau | **Có** |
| `source_deduplicator` | Khử trùng lặp các nguồn tin theo URL chuẩn hóa (bỏ UTM/tracker), tiêu đề, và tùy chọn đối chiếu nội dung sâu | **Có** |

### A3. Câu hỏi mẫu để thử

1. *"Tin tức AI hôm nay có gì mới? Tóm tắt giúp mình."* (Kiểm tra `lookup` với `topic=news`, `timeframe=day`)
2. *"Tóm tắt 5 tweet mới nhất giúp mình."* → Sau khi agent hỏi lại, trả lời *"Của Elon Musk"* (Kiểm tra `clarify` → `timeline(screenname="elonmusk")`)
3. *"So sánh tin tức báo chí và thảo luận trên X về robotics trong tháng qua, lấy tối đa 4 nguồn mỗi bên."* (Kiểm tra tool mới `topic_radar`)
4. *"Tìm bằng chứng từ 4 website khác nhau cho nhận định 'Urban tree cover can lower neighborhood surface temperatures during heat waves', chỉ dùng search snippet."* (Kiểm tra tool mới `evidence_finder`)
5. *"Gửi tóm tắt tin tức AI hôm nay lên Telegram giúp tôi."* → Xác nhận *"Tôi xác nhận gửi"* (Kiểm tra boundary xác nhận `clarify(yes_no)` → `send(confirmed=true)`)

## 3. Giải pháp

- **Tối ưu `starter_v0/artifacts/system_prompt.md`:**
  - Loại bỏ toàn bộ các chỉ dẫn sai lệch cố ý của starter (tự đoán tài khoản Sam Altman khi thiếu handle, tự đoán URL khi thiếu link, tự ý gửi tin mà không hỏi, ép hoàn thành trong một bước).
  - Bổ sung quy tắc hỏi lại (`clarify`) khi thiếu ngữ cảnh bắt buộc và ranh giới bắt buộc xác nhận (`response_type: yes_no`) trước khi gọi `send`.
  - Hỗ trợ duy trì ngữ cảnh hội thoại đa lượt (multi-turn carryover & correction), định tuyến song song (`lookup` + `social_search`) khi cần đa kênh và định tuyến độc quyền tới tool mới `topic_radar` khi đối chiếu đa nền tảng.
- **Chuẩn hóa `starter_v0/artifacts/tools.yaml`:**
  - Viết lại mô tả cho cả 13 tools theo chuẩn: làm gì, **KHI NÀO DÙNG**, **KHI NÀO KHÔNG DÙNG**.
  - Chuẩn hóa quy ước tham số: `screenname` không có `@`; `query` chỉ chứa từ khóa cốt lõi (loại bỏ filler words như "tin tức", "news", "hôm nay"); ranh giới `confirmed=true` cho `send`.
- **Phát triển 3 tool mới (`topic_radar`, `evidence_finder`, `source_deduplicator`):**
  - Mỗi tool có đủ `tool.py`, `TOOL.md` đúng frontmatter contract, được đăng ký đầy đủ trong `tools/__init__.py` và `artifacts/tools.yaml`, và xử lý ngoại lệ an toàn bằng cách trả về error dict thay vì raise exception.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Tất cả các run dưới đây đều hợp lệ (`provider_error_cases == 0` và `measured_cases == total_cases = 20`).

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo lường mức độ lỗi ban đầu khi chưa tối ưu | - | 0.65 (13/20) | `runs/v0_B_base_gemini_20261110T174737486284.json` |
| v1 | `system_prompt.md` | Bỏ chỉ dẫn xấu của starter; bắt buộc gọi `clarify` khi thiếu account/URL và xin xác nhận trước khi gửi | 0.65 | 0.70 (14/20) | `runs/v1_B_base_gemini_20261110T181127878174.json` |
| v2 | `system_prompt.md` | Phân biệt tìm kiếm theo chủ đề (`social_search`) với thiếu account; cho phép gọi tool song song và ép `response_type: yes_no` | 0.70 | 0.80 (16/20) | `runs/v2_B_base_gemini_20261110T182200983550.json` |
| v3 | `tools.yaml` | Mô tả chi tiết khi nào dùng/không dùng và quy ước `query` chỉ chứa từ khóa cốt lõi (bỏ filler words) | 0.80 | 0.85 (17/20) | `runs/v3_B_base_openrouter_20261111T001429486980.json` |

### B2. Failure Analysis

Phân tích 7 ca FAIL ở baseline `v0` (`v0_B_base_gemini_20261110T174737486284.json`) và trạng thái khắc phục ở `v3`:

| Case ID | Failure Type | Actual Tool Calls (v0) | What Failed | Fix |
|---|---|---|---|---|
| `R03_web_news_routing` | `wrong_tool` / `wrong_arg_value` | `lookup` | `query` bị dài: `'AI news today artificial intelligence breakthroughs announcements'` thay vì `'AI'` | Quy ước query ngắn gọn trong `tools.yaml` + prompt; lưu ý trên `gpt-4o-mini` v3 còn gọi thừa thêm `social_search` |
| `R10_missing_handle` | `missing_info` | `timeline` | Tự đoán `sama` thay vì gọi `clarify` | Bỏ chỉ dẫn đoán bừa trong prompt (v1) → **PASS ở v1–v3** |
| `R11_missing_url` | `missing_info` | `lookup` | Tự gọi `lookup` thay vì `clarify` xin URL | Thêm rule thiếu URL gọi `clarify` (v1) → **PASS ở v1–v3** |
| `R12_confirm_before_send` | `wrong_boundary` | `send` | Tự ý gọi `send` không qua `clarify(yes_no)` | Bổ sung boundary xác nhận bắt buộc và `yes_no` (v2) → **PASS ở v2–v3** |
| `R13_parallel_web_and_tweets` | `wrong_tool` | `lookup` | Thiếu gọi song song `social_search`, `query` dư từ thừa | Kích hoạt parallel calling (v2) + query sạch (v3) → **PASS ở v3** |
| `M02_carryover_timeframe` | `wrong_arg_value` | `lookup` | `query` dính `'tin tức robotics hôm nay'` thay vì `'robotics'` | Chuẩn hóa quy ước `query` (v3); trên `gpt-4o-mini` v3 còn gọi kèm `social_search` |
| `M06_switch_tool` | `wrong_tool` | `lookup` | `query` dính `'OpenAI latest news'` thay vì `'OpenAI'` | Quy ước `query` sạch (v3); trên `gpt-4o-mini` v3 còn gọi kèm `social_search` |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn). Kết quả từ run hợp lệ mới nhất `starter_v0/runs/v3_B_group_openrouter_20261111T014441360490.json` (**9/10 PASS = 90%**, `provider_error_cases == 0`):

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| `G01_topic_radar_monthly_robotics` | Định tuyến so sánh tin tức & X sang `topic_radar` với `timeframe=month`, `limit=4` | `topic_radar(query="robotics", timeframe="month", limit=4, include_social=true)` | **PASS** |
| `G02_evidence_finder_snippets` | Trích xuất claim, `max_sources=4`, tắt `deep_read` | `evidence_finder(claim=..., max_sources=4, deep_read=false)` | **PASS** |
| `G03_source_deduplicator_local` | Lọc trùng danh sách có sẵn ở chế độ local, không cào trang | `source_deduplicator(...)` | **PASS** |
| `G04_format_existing_sources_brief` | Định dạng trực tiếp nguồn có sẵn với `template="brief"` và đúng `headline` | `format(template="brief", headline="AI Governance Brief")` | **PASS** |
| `G05_lookup_general_documentation` | Tìm tài liệu kỹ thuật dùng `topic="general"` thay vì `news` | `lookup(topic="general")` | **PASS** |
| `GM01_source_deduplicator_local_followup` | Multi-turn: giữ lại danh sách nguồn ở turn 1 và tuân thủ lệnh không gọi extraction API ở turn 2 | `source_deduplicator(verify_content=false)` | **PASS** |
| `GM02_topic_radar_carryover_weekly` | Multi-turn: giữ chủ đề từ turn 1 sang turn 2 và áp dụng `timeframe=week`, `limit=3`, `enrich_articles=false` | `topic_radar(query="robotics", timeframe="week", limit=3, include_social=true, enrich_articles=false)` | FAIL *(extra tool call `topic_radar`)* |
| `GM03_evidence_finder_carryover_claim` | Multi-turn: giữ nguyên `claim` ở turn 1 và áp dụng `max_sources=5`, `deep_read=false` | `evidence_finder(claim=..., max_sources=5, deep_read=false)` | **PASS** |
| `GM04_format_bullets_followup` | Multi-turn: định dạng `template="bullets"` và cập nhật `headline` theo lượt sau | `format(template="bullets", headline="AI Research Source Notes")` | **PASS** |
| `GM05_paper_text_page_limit_correction` | Multi-turn: giữ đúng arXiv ID `2307.09288` và cập nhật giới hạn `max_pages=3` | `paper_text(arxiv_url="2307.09288", max_pages=3)` | **PASS** |

### B4. Live Chat Evidence

Lấy từ 4 file transcript trong `starter_v0/transcripts/`:

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| Session 1 (`v3_gemini_20261110T193456801873.transcript.json`) Turn 1 | *"Find today's AI news and prepare a concise research brief with 5 sources."* | `lookup(query="AI", topic="news", timeframe="day")` → `format(template="brief")` | `v3+p8790bc017e58+t7486a61f88a9` | `answered` — Tổng hợp thành công bản tin AI 5 nguồn có trích dẫn |
| Session 2 (`v3_gemini_20261110T194637712792.transcript.json`) Turn 1–2 | Turn 1: *"Summarize the 5 latest tweets for me."* → Turn 2: *"Elon Musk."* | Turn 1: `clarify(response_type="text")` → Turn 2: `timeline(screenname="elonmusk", limit=5)` → `format` | `v3+p8790bc017e58+t7486a61f88a9` | `answered` — Hỏi lại khi thiếu tài khoản, sau đó lấy đúng 5 tweet của Elon Musk |
| Session 3 (`v3_gemini_20261110T194822685087.transcript.json`) Turn 1–2 | Turn 1: *"Post this research briefing to our Telegram channel."* → Turn 2: *"No. Do not send it."* | Turn 1: `clarify(response_type="yes_no")` → Turn 2: không gọi `send` | `v3+p8790bc017e58+t7486a61f88a9` | `answered` — Dừng gửi an toàn khi người dùng từ chối |
| Session 4 (`v3_gemini_20261110T235739095905.transcript.json`) Turn 3–4 | Turn 3: *"Gửi tóm tắt tin tức AI hôm nay lên Telegram giúp tôi"* → Turn 4: *"Tôi xác nhận gửi"* | Turn 3: `clarify(response_type="yes_no")` → Turn 4: `send(confirmed=true)` | `v3+p8790bc017e58+t7486a61f88a9` | `answered` — `status: "sent"` (gửi thật lên Telegram sau khi xác nhận) |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) | `starter_v0/tools/topic_radar/`, `evidence_finder/`, `source_deduplicator/` (mỗi tool đủ `tool.py` + `TOOL.md`), đã đăng ký trong `tools/__init__.py` & `artifacts/tools.yaml` | Cả 3 tool hoạt động ổn định, hợp đồng đồng bộ 100% (`test_tool_contract.py` 70/70 passed) | Kiểm tra đầu vào chặt chẽ, reject URL nội bộ (`localhost`, `.local`, IP private), trả về error dict thay vì raise exception |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py`, `test_topic_radar.py`, `test_evidence_finder.py`, `test_source_deduplicator.py` | Toàn suite `pytest starter_v0/tests/` đạt **134 passed, 0 failed, 0 skipped** trong 0.34s | Mọi HTTP request đều chạy offline hoàn toàn bằng `fake_http` & `monkeypatch`; chặn gọi mạng thật qua `block_network` |
| UI (lệnh chạy + link dùng thử) | `starter_v0/app.py`, `starter_v0/requirements.txt` | Lệnh chạy: `cd starter_v0 && python -m streamlit run app.py`. Giao diện sạch, hỗ trợ chat nhiều lượt và thực thi trực tiếp cả 13 tools | Tích hợp xác nhận người dùng trước khi `send` và không làm lộ API key lên giao diện |

- **Tool unit tests:** Nhóm đã triển khai toàn bộ test cho cả core tools và 3 tools mới với tổng số **134 test cases** (trong đó `test_topic_radar.py`: 16 tests, `test_evidence_finder.py`: 14 tests, `test_source_deduplicator.py`: 7 tests, `test_tools_todo.py`: 20 tests). Một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được: trường hợp truyền tham số out-of-enum (`timeframe="decade"`), giới hạn vượt ngưỡng (`limit=99`), URL nội bộ (`http://localhost/secret`) hoặc thiếu API key (`TAVILY_API_KEY`) khiến code tool có thể văng `ValueError`/`TypeError` hoặc `RuntimeError` nếu không được bọc trong `try...except` để trả về error dict chuẩn.

### B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | *(Không thực hiện)* | - | - |
| Hơn 3 tool mới (≥ 4) | Nhóm có **3 tool mới** (`topic_radar`, `evidence_finder`, `source_deduplicator`) | Đạt đầy đủ chuẩn CP3 cho cả 3 tool | *(Thiếu 1 tool nữa để đạt mốc ≥ 4 cho bonus này)* |
| `send` gửi thật lên Telegram sau xác nhận | `starter_v0/transcripts/v3_gemini_20261110T235739095905.transcript.json` (Turn 3–4) | Agent hỏi lại `clarify(yes_no)`, người dùng trả lời *"Tôi xác nhận gửi"*, agent gọi `send(confirmed=true)` và trả về `status: "sent"` trên private channel của nhóm | Bắt buộc cấu hình `TELEGRAM_BOT_TOKEN` & `TELEGRAM_CHAT_ID` trong `.env` (không commit); tuyệt đối chặn gửi khi `confirmed=false` |
| Test challenge (0 skipped / regression test) | Output chạy `pytest starter_v0/tests/` | Toàn bộ **134/134 tests passed, 0 skipped, 0 failed** (đã hoàn tất toàn bộ các stub TODO trong `test_tools_todo.py`) | Đảm bảo 100% chạy offline nhờ fixture `block_network` |

### B7. Small Local Model Challenge (bonus)

*(Nhóm tập trung vào tối ưu cloud models Gemini/OpenRouter, hoàn thiện 3 tools, test suite 0 skipped và Telegram live flow nên không thực hiện phần Small Local Model).*

## 5. Khó khăn và cách xử lý

1. **Lỗi rate limit / quá tải của Gemini Free Tier (`429 RESOURCE_EXHAUSTED`, `503 UNAVAILABLE`):**
   - **Hiện tượng:** Khi chạy `run_eval.py` liên tiếp 20 cases bằng Gemini Free Tier (giới hạn 15 requests/phút), một số lượt sau (như `M02` ở lần thử v1, `R14` ở lần thử v3 lúc 18:29) gặp lỗi HTTP 429 hoặc 503 từ Google API (`v3_B_base_gemini_20261110T182951613132.json` bị `provider_error_cases = 1`).
   - **Cách xử lý:**
     + Bổ sung vòng lặp `retry` với `time.sleep` khi gặp lỗi `429`/`503`/`500` trong `starter_v0/providers/gemini_provider.py`.
     + Để đảm bảo các run nộp bài hoàn toàn sạch lỗi provider (`provider_error_cases == 0` và `measured_cases == 20/20`), nhóm chuyển sang chạy kiểm chứng v3 và group eval trên **OpenRouter (`openai/gpt-4o-mini`)** (lưu tại `v3_B_base_openrouter_20261111T001429486980.json` và `v3_B_group_openrouter_20261111T014441360490.json`).
2. **Lỗi giả (False Negatives) do ép kiểm tra giá trị mặc định trong `eval_group.json`:**
   - **Hiện tượng:** Lần chạy `eval_group` đầu tiên (`v3_B_group_openrouter_20261111T012441145412.json`) chỉ đạt 5/10 (50%) do các case `G01` và `G03` ép model phải truyền `enrich_articles: false` và `verify_content: false` trong khi model bỏ qua các tham số mang giá trị mặc định này (`None != False`).
   - **Cách xử lý:** Tuân thủ nguyên tắc thiết kế eval case (chỉ assert các tham số cốt lõi cần kiểm tra), điều chỉnh lại `expect` của `G01`, `G03`, `G05` trong `data/eval_group.json` và làm rõ quy tắc định tuyến `topic_radar` trong `system_prompt.md`, giúp lần chạy sau đạt **9/10 (90%)**.
3. **Lỗi xung đột format CSV ở `version_log.csv`:**
   - Khi ghi cột `reason` và `hypothesis` chứa dấu phẩy nhưng thiếu ngoặc kép khiến cột bị nhảy; nhóm đã chuẩn hóa bằng chuỗi bọc dấu ngoặc kép theo chuẩn RFC 4180 và mã hóa UTF-8 Tiếng Việt.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- **Fix nào thuộc `system_prompt.md`?**
  - Loại bỏ chỉ dẫn xấu ép đoán bừa và tự ý gửi, quy tắc bắt buộc `clarify` khi thiếu thông tin/chưa xác nhận, quy tắc gọi song song nhiều nguồn, và các quy ước ứng xử đa lượt (multi-turn carryover/correction).
- **Fix nào thuộc `tools.yaml`?**
  - Mô tả phạm vi "Khi nào dùng / Khi nào KHÔNG dùng" của từng tool để chống nhầm lẫn giữa các công cụ tương đồng (`timeline` vs `social_search`, `lookup` vs `fetch`, `topic_radar` vs `lookup`), quy ước format tham số (`screenname` không `@`, `query` không filler words, `confirmed=true` cho `send`).
- **Failure nào cần review thủ công thay vì chấm tự động?**
  - Các trường hợp như `G05` (từ khóa tìm kiếm có nhiều cách diễn đạt tương đương như `"OAuth 2.0 PKCE"` vs `"OAuth 2.0 authorization code flow with PKCE"`), chất lượng câu hỏi `clarify` có tự nhiên/dễ hiểu với người dùng không, và chất lượng tổng hợp nội dung/trích dẫn của câu trả lời cuối cùng sau khi gọi tool xong.
- **Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?**
  - Thiết lập cơ chế ràng buộc trên `gpt-4o-mini` để khắc phục hoàn toàn việc gọi thừa tool `social_search` khi người dùng chỉ yêu cầu tin tức báo chí (`R03`, `M02`, `M06`) hoặc gọi lặp tool trong multi-turn (`GM02`), đồng thời phát triển thêm 1 tool mới nữa để đủ mốc ≥ 4 tool cho Bonus và thử nghiệm trên Small Local Model qua Ollama.

## 8. Tài liệu tham khảo

- Tài liệu hướng dẫn đề bài: [README.md](../../README.md), [RULES.md](../../RULES.md), [RUBRIC.md](../../RUBRIC.md), [CHECKPOINTS.md](../../CHECKPOINTS.md).
- Công cụ hỗ trợ: Trợ lý AI (Antigravity / ChatGPT / Gemini) hỗ trợ phân tích log JSON, cấu trúc hóa YAML và sinh mẫu unit test mock.
