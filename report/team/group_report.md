# Báo cáo nhóm — Day 03 Research Agent Tool Eval

Phần A hướng dẫn dùng thử agent. Phần B ghi lại kết quả đánh giá, test và hội thoại live. [Rubric](../../RUBRIC.md)

## 1. Thông tin nhóm

- Tên nhóm: Corner
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider và model: OpenRouter với `openai/gpt-4o-mini`.
- Từ `v7-openai-recheck` đến `v10`: provider `openai` trực tiếp với cùng model `gpt-4o-mini`. Các vòng này đo lại trạng thái main bằng provider mới trước khi sửa tiếp.

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Agent tìm tin web, bài đăng X và bài nghiên cứu arXiv, đọc URL, tra chính sách nội bộ và trình bày nguồn thành bản tin. Tool `dedupe_sources` lọc URL lặp từ danh sách nguồn đã có. Tool `hn_search` tìm thảo luận trên Hacker News. Quy trình đăng Telegram yêu cầu duyệt nội dung trước khi gửi.

**Cách chạy UI**

Từ thư mục gốc, cấu hình `starter_v0/.env` theo [hướng dẫn API](../../docs/TOOL-SETUP.md), rồi chạy trong PowerShell:

```powershell
cd starter_v0
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Để demo bằng OpenAI, đặt `DAY03_UI_PROVIDER=openai` và điền `OPENAI_API_KEY` trong `.env`.

Mở [UI tại localhost](http://127.0.0.1:8501).

**Link phiên demo đã kiểm tra** [Research Agent qua Cloudflare Tunnel](https://trail-sip-supplier-benchmark.trycloudflare.com). Phiên này hiện không truy cập được. Khi demo, chạy `cloudflared tunnel --url http://127.0.0.1:8501` và cập nhật A1 bằng URL mới.

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi thông tin còn thiếu hoặc xin xác nhận. | Không |
| `timeline` | Lấy bài gần đây từ một tài khoản X. | Không |
| `social_search` | Tìm bài đăng X theo chủ đề và thứ tự `Top` hoặc `Latest`. | Không |
| `lookup` | Tìm thông tin hoặc tin tức trên web. | Không |
| `fetch` | Đọc nội dung tại URL đã biết. | Không |
| `format` | Trình bày các nguồn đã có thành bản tin Markdown. | Không |
| `send` | Đăng nội dung đã được duyệt lên kênh Telegram đã cấu hình. | Không |
| `policy` | Tra tài liệu chính sách nội bộ. | Không |
| `papers` | Tìm bài nghiên cứu trên arXiv. | Không |
| `paper_text` | Tải PDF arXiv và trích xuất văn bản. | Không |
| `dedupe_sources` | Bỏ URL trùng và giữ thứ tự xuất hiện đầu tiên. | Có |
| `hn_search` | Tìm story và thảo luận trên Hacker News theo chủ đề, sắp theo độ nổi bật hoặc mới nhất (Algolia API, không cần key). | Có |

### A3. Câu hỏi mẫu để thử

1. Tìm hai tin web về pin thể rắn trong tuần này.
2. Tra một mục trong chính sách nội bộ về trích dẫn nguồn.
3. Tóm tắt một bài viết mà tôi chưa gửi URL. Sau khi agent hỏi lại, cung cấp `https://example.org/`.
4. Lọc trùng trong danh sách `https://example.org/a`, `https://example.org/b`, `https://example.org/a`.
5. Dân dev trên Hacker News đang bàn gì về Rust? Lấy 3 bài thôi. Sau đó: "Thôi chuyển qua Twitter đi, lấy mấy bài hot nhất".

## 3. Giải pháp

- Prompt phân biệt thao tác đọc với hành động đăng, yêu cầu hỏi lại khi thiếu tài khoản hoặc URL và chọn tool theo nguồn hiện hành. [System prompt](../../starter_v0/artifacts/system_prompt.md)
- Khai báo tool mô tả phạm vi của từng tool, quy ước tham số và điều kiện `confirmed=true` của `send`. [Khai báo YAML](../../starter_v0/artifacts/tools.yaml)
- `dedupe_sources` xử lý danh sách URL đã có. `app.py` dùng chung vòng lặp chạy tool với CLI và giữ hội thoại riêng cho từng phiên Streamlit. [Tool mới](../../starter_v0/tools/dedupe_sources/TOOL.md) · [UI](../../starter_v0/app.py)
- `hn_search` là tool mới thứ hai. Agent chỉ gọi tool này khi người dùng nhắc rõ Hacker News/HN. Tool chuẩn hóa input xấu từ model (`limit` sai kiểu hoặc ngoài khoảng, `sort` ngoài enum) và trả error dict khi query rỗng hoặc lỗi HTTP/timeout. [Tool](../../starter_v0/tools/hn_search/TOOL.md)
- `v9`–`v10` sửa lỗi M06 còn mở từ `v7`: nguồn người dùng đã bỏ thì bỏ luôn ở các lượt sau, và khi đổi nguồn chỉ gọi tool của nguồn mới.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi của starter trước khi tối ưu |  | 0.70 (14/20) | [Run v0](../../starter_v0/runs/v0_B_base_openrouter_20261110T175814995429.json) |
| v1 | `system_prompt.md` | Gọi `clarify` khi thiếu tài khoản hoặc URL sẽ giúp R10 và R11 đạt. | 0.70 (14/20) | 0.90 (18/20) | [Run v1](../../starter_v0/runs/v1_B_base_openrouter_20261110T180445251879.json) |
| v2 | `system_prompt.md` | Yêu cầu `clarify(response_type="yes_no")` trước khi gửi sẽ giúp R12 đạt. | 0.90 (18/20) | 0.90 (18/20) | [Run v2](../../starter_v0/runs/v2_B_base_openrouter_20261110T180925001898.json) |
| v3 | `system_prompt.md` | Tách xác nhận ý định khỏi duyệt nội dung sẽ giúp R12 hỏi `yes_no` trước. | 0.90 (18/20) | 0.85 (17/20) | [Run v3](../../starter_v0/runs/v3_B_base_openrouter_20261110T181244702942.json) |
| v4 | `tools.yaml` | Phân biệt tin web với bài đăng theo lựa chọn nguồn gần nhất sẽ giúp M02 và M06 đạt. | 0.85 (17/20) | 0.95 (19/20) | [Run v4](../../starter_v0/runs/v4_B_base_openrouter_20261110T181658156040.json) |
| v5 | `tools.yaml` | Khai báo rõ điều kiện sử dụng và tham số giúp R11 truyền `response_type` và giữ hành vi xác nhận của R12. | 0.95 (19/20) | 1.00 (20/20) | [Run v5](../../starter_v0/runs/v5_B_base_openrouter_20261110T182433343445.json) |
| v6 | `system_prompt.md` | Routing theo nguồn và theo thứ tự phụ thuộc sẽ giữ kết quả base khi bỏ quy tắc ép một tool. | 1.00 (20/20) | 0.95 (19/20) | [Run v6](../../starter_v0/runs/v6_B_base_openrouter_20261110T182703574719.json) |
| v7 | `system_prompt.md` | Tách đọc khỏi xác nhận gửi và từ chối rõ yêu cầu giải toán hoặc viết code. | 0.95 (19/20) | 0.95 (19/20) | [Run v7](../../starter_v0/runs/v7_B_base_openrouter_20261110T183204024791.json) |
| v7-openai-recheck | không đổi (prompt `v7`, `tools.yaml` đã có `dedupe_sources`) | Đo lại trạng thái main bằng provider `openai` để có mốc so sánh cùng provider | 0.95 (openrouter) | 1.00 (20/20) | [Run](../../starter_v0/runs/v7-openai-recheck_B_base_openai_20261110T222228169092.json) |
| v8 | `tools.yaml` + `system_prompt.md` | Thêm `hn_search` kèm một dòng routing sẽ route đúng tool mới mà không làm giảm base/group | 1.00 | 0.95 (19/20) · group 10/10 · hn 3/3 | [Base](../../starter_v0/runs/v8_B_base_openai_20261110T222512842967.json) · [Group](../../starter_v0/runs/v8_B_group_openai_20261110T222537990558.json) · [HN](../../starter_v0/runs/v8_B_extension_openai_20261110T222549520947.json) |
| v9 | `system_prompt.md` | M06 gọi lại `social_search` vì rule chưa nói nguồn đã bỏ thì phải bỏ luôn. Thêm rule + ví dụ 3 lượt | 0.95 | 1.00 (20/20) · group 10/10 · hn 2/3 | [Base](../../starter_v0/runs/v9_B_base_openai_20261110T222819788946.json) · [Group](../../starter_v0/runs/v9_B_group_openai_20261110T222846351882.json) · [HN](../../starter_v0/runs/v9_B_extension_openai_20261110T222900249358.json) |
| v10 | `system_prompt.md` | Ví dụ ở `v9` chỉ có trường hợp chuyển sang web nên N03 thêm `lookup`. Nói rõ "chỉ gọi tool của nguồn mới" | 1.00 · hn 2/3 | **1.00 (20/20, chạy 2 lần)** · group 10/10 · hn 3/3 | [Base 1](../../starter_v0/runs/v10_B_base_openai_20261110T223052527930.json) · [Base 2](../../starter_v0/runs/v10_B_base_openai_20261110T223256216225.json) · [Group](../../starter_v0/runs/v10_B_group_openai_20261110T223122934339.json) · [HN](../../starter_v0/runs/v10_B_extension_openai_20261110T223139440802.json) |

Prompt/tools bản cuối là `v10`. Cùng prompt `v7` nhưng M06 fail trên openrouter và pass trên openai (`v7-openai-recheck`), rồi fail lại ở `v8`. Case nhiều lượt này dao động giữa các lần chạy, nên `v10` được chạy base hai lần để xác nhận.

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

Run `v0` qua OpenRouter với `openai/gpt-4o-mini` chấm đủ 20 ca và có 0 lỗi provider. Tỷ lệ chọn đúng tool là 80%, tỷ lệ đúng tham số là 70%, và 6/6 ca nhiều lượt đạt. Cột Fix ghi các thay đổi đề xuất cho vòng sau.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `R03_web_news_routing` | `wrong_tool` | `lookup(query="AI news", topic="news", timeframe="day", max_results=5)` | Tool đúng, nhưng `query` nhận `AI news` thay vì `AI`. | Ghi rõ chủ đề tìm kiếm nằm trong `query` và loại tin nằm trong `topic`. |
| `R08_out_of_scope` | `out_of_scope` | `send(text=...)` | Gọi tool gửi lời giải toán dù ca này yêu cầu không gọi tool. | Thêm quy tắc trả lời ngắn khi yêu cầu nằm ngoài phạm vi nghiên cứu. |
| `R10_missing_handle` | `missing_info` | `timeline(screenname="sama")` | Tự đoán tài khoản khi người dùng chưa cung cấp handle. | Gọi `clarify(response_type="text")` để hỏi tài khoản. |
| `R11_missing_url` | `missing_info` | `fetch(url="https://example.com/article")` | Tự điền URL thay vì hỏi người dùng. | Gọi `clarify(response_type="text")` để xin URL trước khi đọc. |
| `R12_confirm_before_send` | `wrong_boundary` | `send(text="Bản tin này")` | Gọi `send` trước khi xác nhận. Tool trả `needs_confirmation`. | Hỏi bằng `clarify(response_type="yes_no")` và chỉ gọi `send` sau khi người dùng xác nhận nội dung. |
| `R13_parallel_web_and_tweets` | `wrong_tool` | `lookup(query="AI news", timeframe="day", max_results=5)` và `social_search(query="AI", search_type="Latest", limit=5)` | Cả hai tool đều được gọi. `lookup` dùng sai `query` và thiếu `topic="news"`. | Tách từ khóa và bộ lọc tin tức cho nhánh web, giữ lời gọi tìm bài đăng riêng. |

Đối chiếu với `v1`, R10 và R11 chuyển sang PASS nhờ gọi `clarify(response_type="text")`. R03, R08 và R13 cũng chuyển sang PASS trong lần chạy này. R12 vẫn gọi `send` trước khi hỏi xác nhận. M02 chuyển từ PASS sang FAIL vì gọi `social_search(query="robotics")` thay cho `lookup(query="robotics", topic="news", timeframe="day")`. Tỷ lệ ca nhiều lượt giảm từ 6/6 xuống 5/6.

Ở `v2`, cả 18 ca từng PASS trong `v1` vẫn đạt. R12 chuyển từ `send` sang `clarify`, nhưng gửi `response_type="text"` để xin nội dung bản tin thay vì `yes_no` theo kỳ vọng. Điểm routing tăng từ 90% lên 95% trong khi điểm tổng giữ ở 90%. M02 vẫn chọn `social_search` cho yêu cầu tin robotics hôm nay.

Ở `v3`, R12 gọi `clarify(response_type="yes_no")` và chuyển sang PASS. Run không gọi `send`. M02 tiếp tục chọn `social_search` cho tin robotics. Hai ca chuyển từ PASS sang FAIL so với `v2`: R01 hỏi lại handle của Sam Altman thay vì gọi `timeline(screenname="sama")`, còn M06 vẫn dùng `social_search` sau khi người dùng yêu cầu chuyển sang tìm tin trên web. Tỷ lệ đạt giảm từ 18/20 xuống 17/20, và số ca nhiều lượt đạt giảm từ 5/6 xuống 4/6.

Ở `v4`, M02 và M06 dùng `lookup` cho tin web và chuyển sang PASS. R01 cũng chuyển sang PASS, còn R12 tiếp tục gọi `clarify` với `yes_no`. R11 chuyển từ PASS sang FAIL vì agent hỏi đúng URL bằng `clarify` nhưng bỏ tham số `response_type` mà eval yêu cầu. Run đạt 19/20 ca, chọn đúng tool ở 20/20 ca và đạt 6/6 ca nhiều lượt.

Ở `v5`, R11 gọi `clarify` với `response_type="text"`, R12 vẫn hỏi bằng `yes_no` và 19 ca từng PASS đều giữ kết quả. `tools.yaml` khai báo `response_type` là bắt buộc, nêu điều kiện sử dụng và quy ước tham số của các tool, và yêu cầu xác nhận nội dung chính xác trước khi gọi `send` với `confirmed=true`.

Ở `v6`, R01 chuyển từ PASS sang FAIL vì agent hỏi xác nhận bằng `clarify(response_type="yes_no")` thay vì gọi `timeline(screenname="sama")`. R12 vẫn hỏi xác nhận gửi, R13 gọi đủ hai tool và 6/6 ca nhiều lượt vẫn đạt. Kiểm tra thủ công `actual_text` của `v5` và `v6` cho thấy R08 và R14 vẫn giải toán và viết code. Hai ca PASS trong eval vì điều kiện chấm của `no_tool` chỉ xét tool call.

Ở `v7`, R01 gọi thẳng `timeline(screenname="sama")` và R12 vẫn hỏi xác nhận bằng `yes_no`. Kiểm tra `actual_text` cho thấy R08 từ chối giải tích phân và R14 từ chối viết hàm nhưng giải thích công thức Fibonacci. M06 từ PASS sang FAIL vì gọi thêm `social_search` sau khi người dùng đã chuyển sang tin web. Điểm tổng giữ ở 19/20 và số ca nhiều lượt đạt giảm xuống 5/6.

| Version | Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|---|
| `v8` | `M06_switch_tool` | `wrong_tool` | `lookup(query="OpenAI", topic="news")` + `social_search(query="OpenAI")` | Lượt 3 "Giữ chủ đề OpenAI" không nhắc nguồn, model lấy lại Twitter từ lượt 1 | `v9`: nguồn đã bỏ thì bỏ luôn ở mọi lượt sau, kèm ví dụ 3 lượt |
| `v9` | `N03_mt_hn_switch_to_twitter_top` | `wrong_tool` | `social_search(query="Bun", search_type="Top")` + `lookup(query="Bun", topic="news")` | Đổi từ HN sang Twitter nhưng gọi thêm `lookup`: model khái quát ví dụ "chuyển sang web" thành "luôn thêm web" | `v10`: khi đổi nguồn chỉ gọi tool của nguồn mới; chỉ thêm `lookup` khi user yêu cầu web/tin tức |

### B3. Team Eval Cases

Run nhóm `v7-cp3` đạt 10/10 với 0 lỗi provider. Bộ dữ liệu có 5 ca một lượt (`G01`–`G05`) và 5 ca nhiều lượt (`G06`–`G10`). Hai ca gọi `dedupe_sources` đều loại đúng một URL trùng. [Bộ ca nhóm](../../starter_v0/data/eval_group.json) · [Run nhóm](../../starter_v0/runs/v7-cp3_B_group_openrouter_20261110T183908965916.json)

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| `G01_dedupe_given_urls` | Chuyển đủ danh sách nguồn, kể cả URL lặp. | `dedupe_sources` | PASS |
| `G02_internal_policy_area` | Tra đúng kho nội bộ và giới hạn hai mục. | `policy` với `data_privacy` | PASS |
| `G03_monthly_web_news` | Tìm ba kết quả trong một tháng. | `lookup` với `news`, `month` | PASS |
| `G04_arxiv_recent_papers` | Sắp theo ngày nộp và lấy hai bài. | `papers` với `submittedDate` | PASS |
| `G05_outside_research_poem` | Từ chối sáng tác ngoài phạm vi. | Trả lời không gọi tool | PASS |
| `G06_dedupe_prior_links` | Dùng danh sách URL từ lượt trước. | `dedupe_sources` | PASS |
| `G07_cancel_publish` | Dừng quy trình đăng theo yêu cầu hủy. | Xác nhận đã hủy và không gọi tool | PASS |
| `G08_switch_web_to_social` | Đổi nguồn từ web sang X và giữ chủ đề. | `social_search` với `Top`, giới hạn 2 | PASS |
| `G09_format_prior_sources` | Định dạng danh sách nguồn đã có. | `format` với `bullets` và tiêu đề đã chọn | PASS |
| `G10_policy_area_correction` | Ưu tiên nhóm chính sách mới và giới hạn một mục. | `policy` với `source_citation` | PASS |

Bản cuối `v10` chạy lại bộ nhóm đạt 10/10. [Run nhóm v10](../../starter_v0/runs/v10_B_group_openai_20261110T223122934339.json)

Tool mới thứ hai `hn_search` có bộ case riêng [`eval_new_tool_hn_search.json`](../../starter_v0/data/eval_new_tool_hn_search.json), chạy với `--suite extension`, không thay đổi 10 case trên. Kết quả `v10`: 3/3. [Run](../../starter_v0/runs/v10_B_extension_openai_20261110T223139440802.json)

| Case ID | What It Tests | Expected Tool/Behavior | Result (v10) |
|---|---|---|---|
| `N01_hn_routing` | Nhắc Hacker News → tool mới, không phải `lookup`/`social_search` | `hn_search(query="Rust")` | PASS |
| `N02_hn_sort_date_limit` | Viết tắt "HN"; "mới nhất" → `sort=date`; "3 bài" → `limit=3` | `hn_search(query="LLM agents", sort="date", limit=3)` | PASS |
| `N03_mt_hn_switch_to_twitter_top` | Đổi từ HN sang Twitter, giữ chủ đề, "hot nhất" → Top, không gọi thêm tool | `social_search(query="Bun", search_type="Top")` | PASS |

### B4. Live Chat Evidence

Phiên `v7-cp3+p73375dfef6dd+t5193d4feb298` có 5 lượt với OpenRouter. Phiên thử dừng ở câu hỏi xác nhận Telegram. [Transcript JSON](../../starter_v0/transcripts/v7-cp3_openrouter_20261110T184221721545.transcript.json)

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tra một mục chính sách trích dẫn nội bộ. | `policy` với `source_citation` | `v7-cp3` | Agent gọi đúng kho và báo không tìm thấy mục khớp. |
| 2 | Tóm tắt bài viết chưa có URL. | Không có | `v7-cp3` | Agent hỏi URL bằng câu trả lời trực tiếp. |
| 3 | Cung cấp `https://example.org/`. | `fetch` | `v7-cp3` | Agent đọc trang và mô tả nội dung. |
| 4 | Lọc URL trùng và giữ thứ tự. | `dedupe_sources` | `v7-cp3` | Trả hai URL theo thứ tự ban đầu, loại một mục trùng. |
| 5 | Yêu cầu đăng thông báo lên Telegram. | `clarify` với `yes_no` | `v7-cp3` | Agent chờ xác nhận. Phiên kết thúc tại đây. |

Phiên `v10` (`python chat.py --provider openai --version v10`) có 4 lượt. [Transcript JSON](../../starter_v0/transcripts/v10_openai_20261110T223316208929.transcript.json)

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Dân dev trên Hacker News đang bàn gì về Rust? Lấy 3 bài thôi | `hn_search(query="Rust", limit=3)` | `v10` | Tool mới trả 3 story kèm điểm và link thảo luận. |
| 2 | Thôi chuyển qua Twitter đi, lấy mấy bài hot nhất | `social_search(query="Rust", search_type="Top")` | `v10` | Đổi nguồn, giữ chủ đề, chỉ gọi tool của nguồn mới. |
| 3 | Đăng tóm tắt mấy bài đó lên Telegram giúp mình | `clarify(response_type="yes_no")` | `v10` | Xin xác nhận, không gọi `send`. |
| 4 | Không, đừng gửi | Không có | `v10` | Agent dừng, không gửi. Lượt 1–2 trả lời tiếng Anh dù câu hỏi tiếng Việt; eval không chấm điểm này. |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| `dedupe_sources` | [Hợp đồng tool](../../starter_v0/tools/dedupe_sources/TOOL.md), [mã Python](../../starter_v0/tools/dedupe_sources/tool.py) | Bỏ URL trùng và giữ thứ tự xuất hiện đầu tiên. | Xử lý tại chỗ, không đọc URL qua mạng. |
| Unit test tool mới | [Ba test](../../starter_v0/tests/test_tools_todo.py) | `pytest` có 70 test đạt, 14 test TODO được bỏ qua và 0 lỗi. | Test chuỗi thay cho danh sách và URL sai cú pháp trả error dict. |
| UI | [Mã Streamlit](../../starter_v0/app.py) · [Localhost](http://127.0.0.1:8501) | Trang và health endpoint trả HTTP 200. AppTest kiểm tra lọc URL qua OpenRouter, mở hội thoại mới và hiển thị lỗi provider. | Lịch sử giữ riêng theo phiên. UI hiển thị loại lỗi thay vì in phản hồi lỗi thô của provider. |

Ba unit test kiểm tra thứ tự và số URL trùng, đầu vào sai kiểu, và URL sai cú pháp. Ca URL thiếu dấu đóng ngoặc kiểm tra lỗi từ bộ phân tích URL được trả dưới dạng error dict. Eval routing chỉ kiểm tra model chọn đúng tool và tham số.

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| `hn_search` (tool mới thứ hai) | [Hợp đồng tool](../../starter_v0/tools/hn_search/TOOL.md), [mã Python](../../starter_v0/tools/hn_search/tool.py) | Gọi Algolia API thật trả đúng story (transcript `v10` lượt 1); route đúng ở N01–N03 | Read-only, không cần key. Input xấu được chuẩn hóa hoặc trả error dict, không raise |
| Unit test `hn_search` (6 test) | [`test_tools_todo.py`](../../starter_v0/tests/test_tools_todo.py) | Happy path assert cả request lẫn mapping; `sort=date` đổi endpoint; query rỗng/sai kiểu không gọi mạng; `limit`/`sort` xấu được chuẩn hóa; HTTP 503 và timeout trả error dict | Offline, HTTP mock bằng `fake_http` |
| `pytest` sau khi bổ sung | `cd starter_v0 && pytest` | **95 passed, 0 failed, 0 skipped** | 14 stub TODO đã có test thật (xem B5) |

Ví dụ lỗi unit test bắt được mà eval không bắt được: nếu model truyền `limit="abc"` hoặc `limit=999` cho `hn_search`, eval vẫn PASS vì tên tool đúng. Khi đó tool sẽ crash ở `int("abc")` hoặc gửi `hitsPerPage=999` lên API. `test_hn_search_bad_limit_and_sort_from_model_are_normalised` assert request thực tế gửi đi là 5 / 1 / 20.

### B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Test challenge (0 skipped) | [`test_tools_todo.py`](../../starter_v0/tests/test_tools_todo.py), `pytest` → 95 passed, 0 skipped | Điền hết 14 stub của tool có sẵn: clarify, format (3), send (2), lookup, fetch (2), timeline, social_search, policy (3). Có guardrail `send` (có env → đúng 1 POST; không env → error dict, không request) và trust boundary của `policy` (dòng giống lệnh nằm ở `untrusted_text`, không lọt vào `facts`) | Toàn bộ offline |

Không tìm thấy bug trong tool có sẵn. `lookup` đổi `max_results=0` thành 5, còn chuỗi không phải số trả error dict `ValueError`, không crash. Nhóm coi đây là hành vi chấp nhận được.

## 5. Khó khăn và cách xử lý

- Chạy script bằng Python hệ thống thiếu thư viện `openai`. Dùng Python trong `.venv` cho các run có số liệu trong B1.
- Khi người dùng thay đổi nguồn giữa các lượt, model đôi khi giữ cả nguồn cũ. `v7` được chốt ở 19/20 với lỗi gọi thừa tool tại M06. Run nhóm kiểm tra chiều đổi ngược, từ web sang X, ở G08. [Run base](../../starter_v0/runs/v7_B_base_openrouter_20261110T183204024791.json) · [Run nhóm](../../starter_v0/runs/v7-cp3_B_group_openrouter_20261110T183908965916.json)
- Tra chính sách bằng cụm từ tiếng Việt ở lượt live đầu tiên gọi đúng `policy` nhưng trả rỗng. Đọc kết quả tool cùng câu trả lời để phân biệt chất lượng truy xuất và routing. [Transcript](../../starter_v0/transcripts/v7-cp3_openrouter_20261110T184221721545.transcript.json)
- Lỗi M06 ở `v7` được sửa ở `v9`, nhưng ví dụ trong rule gây lỗi mới ở N03 (case của tool mới). Bài học: một ví dụ few-shot có thể bị model khái quát quá đà. `v10` nêu nguyên tắc chung và kiểm tra lại cả ba bộ eval.
- `prompt_hash` phụ thuộc kiểu xuống dòng: Windows có `core.autocrlf=true` nên file trong thư mục làm việc dùng CRLF. Run phải được tạo từ đúng file trong thư mục làm việc thì hash mới khớp với `version_log.csv`.

## 6. Tổng hợp đóng góp

Hà Lê Duy phụ trách phần kỹ thuật trên nhánh `haleduy`. Trưởng nhóm bổ sung tên nhóm, phân công các thành viên khác và thông tin nhánh nộp. [Thông tin nhóm](../../TEAM.md) · [Báo cáo cá nhân](2A202603851_HaLeDuy.md)

Nguyễn Thiên Bảo làm tool mới thứ hai `hn_search` cùng 6 unit test, điền 14 unit test TODO (test challenge 0 skipped), chạy `v7-openai-recheck` đến `v10` (sửa M06, base 20/20 hai lần) và thêm transcript `v10`. [Báo cáo cá nhân](2A202603861_NguyenThienBao.md)

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- `system_prompt.md` xử lý phạm vi nghiên cứu, ngữ cảnh nhiều lượt, dữ liệu còn thiếu và thứ tự xin duyệt khi đăng.
- `tools.yaml` mô tả điều kiện chọn từng tool và cách điền tham số như `response_type`, `topic`, `timeframe` và `confirmed`.
- Các ca `no_tool` cần đọc câu trả lời thực tế để xác nhận agent đã từ chối. Tool chạy thành công cũng cần được kiểm tra riêng, vì eval routing chủ yếu so sánh tên tool và args.
- Rule có ví dụ cụ thể sửa được ca khó (M06 ở `v9`) nhưng có thể làm hỏng ca khác có cấu trúc tương tự (N03). Khi thêm tool mới nên có bộ case riêng cho tool đó để phát hiện kiểu regression này.
- Nếu mở rộng bộ kiểm tra, thêm các ca đổi nguồn theo cả hai chiều và kiểm tra câu trả lời cuối từ tool thật. Đây là hai hành vi mà run hiện tại cho thấy cần thêm bằng chứng.

## 8. Tài liệu tham khảo

- [README của lab](../../README.md)
- [Tài liệu chat Streamlit](https://docs.streamlit.io/develop/api-reference/chat)
- [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest)
