# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: <<CHỜ: người dùng/A cung cấp tên nhóm>>
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: <<CHỜ: A/người dùng gửi provider và model>>

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research Agent hỗ trợ tìm tin trên web, lấy bài đăng X theo tài khoản, đọc URL, tra cứu policy nội bộ và bài báo arXiv, rồi định dạng kết quả thành digest. UI có chốt xác nhận trước khi thực thi các tool có tác dụng phụ, gồm gửi Telegram.

**Cách chạy UI:**

Từ thư mục `starter_v0/` với venv đã kích hoạt:

```powershell
streamlit run app.py --server.headless true
```

Dependency đã thêm: `streamlit>=1.40.0` trong `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

URL đã được người dùng xác nhận mở được từ thiết bị khác: [https://testing-alternatively-dash-cherry.trycloudflare.com](https://testing-alternatively-dash-cherry.trycloudflare.com).

Lưu ý: link `trycloudflare.com` chỉ sống khi lệnh `cloudflared tunnel --url http://localhost:8501` còn chạy. Khi kiểm tra lại ngày 2026-11-10 sau khi tunnel đã tắt, link này không còn truy cập được (không phân giải được tên miền). Cần chạy lại `streamlit run app.py` và `cloudflared`, rồi thay URL mới vào đây trước khi nộp hoặc demo.

### A2. Tool agent có

Danh sách dưới đây lấy từ `starter_v0/artifacts/tools.yaml` hiện tại; đối chiếu registry trong `starter_v0/tools/__init__.py` và lịch sử Git không thấy tool mới ngoài 10 tool gốc.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Đặt câu hỏi và chờ người dùng bổ sung thông tin | không |
| timeline | Lấy bài đăng gần đây từ tài khoản X | không |
| social_search | Tìm trên mạng xã hội | không |
| lookup | Tra cứu thông tin trên internet | không |
| fetch | Lấy nội dung từ một URL | không |
| format | Trình bày dữ liệu đã có thành văn bản | không |
| send | Gửi văn bản tới Telegram khi được xác nhận | không |
| policy | Tìm trong tài liệu nội bộ | không |
| papers | Tìm bài báo khoa học | không |
| paper_text | Tải PDF arXiv và trích xuất văn bản cục bộ | không |
| <<CHỜ: B>> | <<CHỜ: B gửi tên/mô tả tool mới hoặc xác nhận chưa thêm tool>> | <<CHỜ: B>> |

### A3. Câu hỏi mẫu để thử

1. Tìm tin AI hôm nay và tổng hợp thành một bản tin ngắn giúp mình.
2. Tóm tắt 5 tweet mới nhất giúp mình.
3. Đăng bản tin AI ở lượt đầu lên Telegram giúp mình.
4. Đọc và tóm tắt trang này giúp mình: https://example.com

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

- <<CHỜ: A và B gửi tóm tắt thay đổi prompt/tools/tool mới để ghép nguyên văn>>

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi chưa tối ưu (prompt starter còn chỉ dẫn xấu) | — | 0.70 (14/20) | `runs/v0_B_base_openrouter_20261110T174519840832.json` |
| v1 | system_prompt.md | Bỏ chỉ dẫn đoán/gửi ngay/một bước, thêm rule `clarify` khi thiếu thông tin và xác nhận trước `send` thì R10, R11, R12 sẽ PASS | 0.70 | 0.80 (16/20) | `runs/v1_B_base_openrouter_20261110T180453970452.json` |
| v2 | system_prompt.md | Thêm rule routing theo loại yêu cầu và điều kiện không cần hỏi lại thì hồi quy R01, M02, M06 của v1 sẽ được sửa | 0.80 | 0.90 (18/20) | `runs/v2_B_base_openrouter_20261110T182517635389.json` |
| v3 | system_prompt.md + tools.yaml | Làm rõ khi nào dùng / không dùng ở cả prompt (rule đổi nguồn, rule xác nhận trước `send`) và `tools.yaml` (description, convention args, boundary `send`) thì R12 và M06 sẽ PASS | 0.90 | 0.85 (17/20) | `runs/v3_B_base_openrouter_20261110T184418744227.json` |
| v4 | system_prompt.md | Prompt chưa có rule cho tool ngoài lõi nên model gọi `deduplicate` với `items` rỗng (G02); thêm rule routing cho các tool này và rule "thiếu danh sách thì `clarify`" thì G02 sẽ PASS mà không hồi quy | 0.90 (*) | 0.95 (19/20) | `runs/v4_B_base_openrouter_20261110T224558978889.json` |
| v5 | system_prompt.md | Model hiểu rộng rule "gọi cả `lookup` và `social_search`" nên gọi thừa `social_search` (G07); nói rõ "không nhắc tweet thì chỉ gọi `lookup`" thì G07 sẽ PASS | 0.95 | 0.90 (18/20) | `runs/v5_B_base_openrouter_20261110T224819699492.json` |
| v6 | system_prompt.md | Rule hỏi thiếu thông tin (`text`) lấn át rule xác nhận `send` nên R12 dùng `text`; nói rõ rule `send` được ưu tiên thì R12 sẽ PASS | 0.90 | 0.85 (17/20) | `runs/v6_B_base_openrouter_20261110T225025242839.json` |
| v7 | tools.yaml (prompt quay về v5) | Mô tả `limit` cũ khiến model bỏ `limit` khi số người dùng nêu đúng bằng mặc định 5 (M01); nói rõ luôn điền `limit` khi người dùng nêu số thì M01 sẽ PASS | 0.90 | 0.95 (19/20) | `runs/v7_B_base_openrouter_20261110T225246707082.json` |

(*) `metric_before` của v4 (0.90) lấy từ lần đo lại prompt v3 trên `tools.yaml` 16 tool hiện hành, vì run v3 gốc dùng `tools_hash` cũ (`750b80a50283`) trước khi nhóm merge thêm 6 tool mới. Lần đo lại này không sửa artifact nào nên không tính là một version: base 18/20 (FAIL R12, M06), file `runs/v3-tools17_B_base_openrouter_20261110T224250589557.json`.

Kết quả trên bộ group của lần đo lại prompt v3 và các version v4 đến v7 (cùng `tools.yaml` 16 tool, 0 lỗi provider, 10/10 case đo được). Các run này chạy trên bộ case group trước khi thay 5 case ở B3 (G03, G04, G07, G09, G10), nên G07 và G08 nhắc ở dưới là case của bộ cũ:

| Version | Group case_accuracy | Case FAIL | Run File |
|---|---:|---|---|
| v3 (đo lại trên 16 tool) | 0.70 (7/10) | G02, G07, G08 | `runs/v3-tools17_B_group_openrouter_20261110T224332128774.json` |
| v4 | 0.90 (9/10) | G07 | `runs/v4_B_group_openrouter_20261110T224634984917.json` |
| v5 | 1.00 (10/10) | không | `runs/v5_B_group_openrouter_20261110T224846947529.json` |
| v6 | 1.00 (10/10) | không | `runs/v6_B_group_openrouter_20261110T225055601556.json` |
| v7 | 0.90 (9/10) | G08 | `runs/v7_B_group_openrouter_20261110T225319237135.json` |

Nhận xét dựa trên các run trên:

- **v4 xác nhận giả thuyết:** G02 từ FAIL sang PASS, base tăng 0.90 lên 0.95.
- **v5 xác nhận trên bộ group:** G07 PASS và group đạt 10/10. Base giảm 0.95 xuống 0.90 vì R12 và M01 FAIL, trong đó M01 không liên quan tới dòng đã sửa.
- **v6 không xác nhận giả thuyết:** R12 vẫn FAIL (model hỏi `text` "đăng bản tin nào?") và R10 hồi quy, base giảm xuống 0.85. Nhóm bỏ câu thêm của v6 và v7 quay lại prompt v5. R12 là case duy nhất FAIL ở mọi run từ v1 đến v7 và còn mở.
- **v7 chưa kết luận được:** M01 PASS, nhưng M01 cũng PASS ở lần đo lại v3 và ở v4 khi chưa sửa gì, nên một run PASS chưa chứng minh được giả thuyết về `limit`.
- **Kết quả dao động giữa các lần chạy:** với cùng prompt và tools, M01 và G08 đổi PASS/FAIL giữa các run. Chênh lệch 1 case (0.05) nằm trong mức dao động này, nên mỗi bản chỉ có một run thì chưa đủ để chắc một version tốt hơn version trước.

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `send(text="Nguyên hàm của x^2 là …")` | Câu hỏi toán nằm ngoài phạm vi research agent nhưng model gọi `send` thay vì từ chối (`unexpected_tool_call`). Nguyên nhân: prompt bảo "cứ làm ngay", không có rule phạm vi/từ chối. | Thêm vào prompt: ngoài phạm vi (toán, code, hỏi đáp chung) thì từ chối ngắn gọn, không gọi tool. |
| R14_out_of_scope_coding | out_of_scope | `send(text="Dưới đây là một hàm Python tính Fibonacci …")` | Yêu cầu viết code bị coi như nội dung để gửi, gọi `send` (`unexpected_tool_call`). Cùng nguyên nhân với R08. | Cùng fix với R08 (rule phạm vi), mô tả `send` chỉ dùng khi user yêu cầu gửi/đăng bản tin. |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Câu hỏi không nói rõ tài khoản nhưng model tự chọn Sam Altman (`missing_tool_call: clarify`, thêm `timeline`). Nguyên nhân: prompt bảo "chọn một tài khoản nổi tiếng". | Xoá chỉ dẫn đoán; thêm rule: thiếu handle thì gọi `clarify` (`response_type=text`). |
| R11_missing_url | missing_info | `fetch(url="https://example.com/article")` | Chỉ có "bài viết này" nhưng model tự bịa URL (`missing_tool_call: clarify`, thêm `fetch`). Nguyên nhân: prompt bảo "assume a likely URL". | Xoá chỉ dẫn đoán URL; thêm rule: thiếu URL thì gọi `clarify`. |
| R12_confirm_before_send | wrong_boundary | `send(text="Bản tin này")` | Gọi `send` ngay, không hỏi xác nhận (`missing_tool_call: clarify`, thêm `send`). Nguyên nhân: prompt bảo "cứ gửi luôn"; `send` không mô tả điều kiện xác nhận. Guardrail của code chỉ trả `needs_confirmation`. | Prompt: gửi/đăng thì `clarify(response_type=yes_no)` trước, chỉ `send(confirmed=true)` sau khi user đồng ý; sửa description `send` trong `tools.yaml`. |
| R13_parallel_web_and_tweets | wrong_tool (harness gán; `observed_mismatch` = `wrong_arg_value`) | `lookup(query="AI news", timeframe="day", max_results=5)` + `social_search(query="AI", search_type="Latest", limit=5)` | Chọn đúng cả hai tool (`routing_correct=True`) nhưng `lookup` sai args: `query` là "AI news" thay vì "AI" và thiếu `topic="news"`. Nguyên nhân: `tools.yaml` chưa nêu convention `topic=news` cho tin tức và `query` chỉ chứa từ khoá. | Sửa description/param của `lookup` trong `tools.yaml`: tin tức dùng `topic="news"`, `query` chỉ là từ khoá, không thêm "news". |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn). Bộ này route tới cả 6 tool mới của nhóm: `deduplicate`, `filter_sources`, `filter_by_date`, `validate_citations`, `openalex`, `semantic_scholar`.

Run: `starter_v0/runs/v7_B_group_openrouter_20261110T230626499597.json` (artifact `v7+pe31381cc6f1d+t4b97f259dc5b`, 10/10 case đo được, 0 lỗi provider). Kết quả: case_accuracy 1.00 (10/10), tool_routing 1.00, argument 1.00, multiturn 1.00.

Lưu ý về các run group cũ: trước đó bộ này gồm các case G03, G04, G07, G09, G10 (xác nhận gửi khi đã có nội dung, làm thơ ngoài phạm vi, đổi timeframe, lời cảm ơn, lọc trùng nhiều lượt). Nhóm thay 5 case này bằng G11–G15 để có eval route tới từng tool mới còn lại. Các run group của v3-tools17 đến v7 ở B1 và run `v3_B_group_...192836267042.json` chạy trên bộ case cũ (xem commit `f29fd57`); số liệu trong file run vẫn đúng với bộ case lúc chạy, nhưng không so sánh trực tiếp được với run mới. Id của 5 case thay thế dùng số mới (G11–G15) để không trùng id với run cũ.

| Case ID | Loại | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|---|
| G01_deduplicate_collected_articles | single | Danh sách có URL trùng (khác fragment) → route tới tool mới `deduplicate`, không gọi `lookup`/`fetch`/`format` | `deduplicate` (chỉ chấm routing) | PASS |
| G02_dedupe_missing_list | single | Yêu cầu lọc trùng nhưng không có danh sách → hỏi lại, không gọi tool với dữ liệu bịa | `clarify` (`response_type=text`) | PASS: hỏi xin danh sách bài viết |
| G05_news_week_keyword_only | single | Tin tức tuần này: `topic=news`, `timeframe=week`, `query` chỉ từ khóa | `lookup(query="chip AI", topic="news", timeframe="week")` | PASS |
| G11_semantic_scholar_most_cited | single | Bài báo được trích dẫn nhiều nhất → tool mới `semantic_scholar`, `sort_by=citationCount` (rule citation trong prompt), không gọi `papers`/`lookup` | `semantic_scholar(sort_by="citationCount")` | PASS về routing và args. Tool trả `HTTPError` 429 khi chạy thật (API không key bị giới hạn request); tool trả error dict, không raise |
| G12_openalex_recent_doi_open_access | single | Công trình học thuật mới kèm DOI và link open access → tool mới `openalex`, `sort_by=publication_date` | `openalex(sort_by="publication_date")` | PASS: tool trả 5 kết quả thật |
| G06_multiturn_clarify_topic_then_search | multi | Lượt 1 thiếu chủ đề, lượt 2 bổ sung "Gemini", lượt 3 chọn mới nhất | `social_search(query="Gemini", search_type="Latest")` | PASS |
| G08_multiturn_confirmed_send | multi | Người dùng đã xác nhận ở lượt cuối → gửi, không hỏi lại thừa | `send(confirmed=true)` | PASS (case này PASS/FAIL dao động giữa các run: FAIL ở v3-tools17 và v7 bộ cũ, xem B1) |
| G13_multiturn_filter_sources_from_earlier_list | multi | Danh sách ở lượt 1, hai nguồn tin cậy ở lượt 2, yêu cầu lọc ở lượt 3 → tool mới `filter_sources` với `allowed_domains` đúng `arxiv.org`, `nature.com`, dùng lại danh sách từ ngữ cảnh | `filter_sources(allowed_domains=["arxiv.org","nature.com"])` | PASS: giữ 2 trong 4 bài |
| G14_multiturn_filter_by_date_range | multi | Danh sách có `date` ở lượt 1, "tháng 10/2026" ở lượt 2 → tool mới `filter_by_date` với `start_date=2026-10-01`, `end_date=2026-10-31` | `filter_by_date(start_date="2026-10-01", end_date="2026-10-31")` | PASS: giữ 2 trong 4 bài |
| G15_multiturn_validate_citations_before_report | multi | Danh sách trích dẫn ở lượt 1, mục đích ở lượt 2, yêu cầu kiểm tra ở lượt 3 → tool mới `validate_citations`, không mở từng link bằng `fetch` | `validate_citations` (chỉ chấm routing) | PASS: `valid=false` vì phát hiện trích dẫn thiếu title và URL sai |

Giới hạn của bộ case: harness không so sánh được danh sách `items` trong args nên G01, G13, G14, G15 chỉ chấm tên tool và các arg đơn giản. G11, G12 kiểm tra rule routing do chính nhóm viết trong prompt (citation thì `semantic_scholar`, DOI và open access thì `openalex`), nên PASS chỉ cho thấy model làm theo rule đó chứ không chứng minh đây là lựa chọn duy nhất đúng. Ở bộ case cũ, scorer từng cho PASS case làm thơ dù model viết luôn bài thơ vì chỉ kiểm tra không có tool call; những case dạng "từ chối" cần review thủ công.

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

Ba phiên chat live bằng `python chat.py --provider openrouter --version v7` (model `openai/gpt-4o-mini`), mỗi phiên một file transcript. Cả ba chạy trên artifact `v7+pe31381cc6f1d+t4b97f259dc5b`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 (yêu cầu thường) | "Tìm tin AI trong tuần này giúp mình" | `lookup(query="AI", topic="news", timeframe="week")` | `transcripts/v7_openrouter_20261110T230951533091.transcript.json` | Đúng tool và args (`topic=news`, `timeframe=week`, query chỉ từ khóa). Trả 4 bài có link nguồn. Nhược điểm: user viết tiếng Việt nhưng agent trả lời bằng tiếng Anh |
| 2a (thiếu thông tin) | "Cho mình xem tweet mới nhất" | không gọi tool | `transcripts/v7_openrouter_20261110T231006560268.transcript.json` | Agent không đoán tài khoản mà hỏi lại bằng văn bản "tài khoản X nào?". Hành vi đúng về mặt người dùng nhưng agent trả lời thẳng thay vì gọi tool `clarify` như rule trong prompt, nên `status=answered` chứ không phải `waiting_for_user` |
| 2b (bổ sung) | "Của Sam Altman nhé, lấy 3 bài thôi" | `timeline(screenname="sama", limit=3)` | cùng file transcript 2a | Đúng tool và args (handle không có `@`, `limit=3`). Trả 3 tweet kèm ngày, retweet, lượt xem |
| 3a (yêu cầu gửi) | "Gửi dòng này lên Telegram giúp mình: Họp sprint dời sang thứ Sáu 9h" | `clarify(response_type="yes_no")`, câu hỏi nêu rõ nội dung sẽ gửi | `transcripts/v7_openrouter_20261110T231021464746.transcript.json` | Không gọi `send` ngay; dừng ở `waiting_for_user` để xin xác nhận. Đúng boundary |
| 3b (xác nhận) | "Đồng ý, gửi đi" | `send(text="Họp sprint dời sang thứ Sáu 9h", confirmed=true)` | cùng file transcript 3a | Agent gọi `send` với `confirmed=true` đúng sau khi user đồng ý. Tool trả `RuntimeError: Missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID env var` vì nhóm chưa cấu hình Telegram nên không có tin nào được gửi. Agent báo lại là "thiếu thông tin cần thiết", chưa nói rõ thiếu cấu hình Telegram |

Nhận xét: luồng hỏi lại, bổ sung và xác nhận trước khi gửi hoạt động đúng. Hai điểm chưa tốt: (1) agent trả lời tiếng Anh cho câu hỏi tiếng Việt ở turn 1, (2) khi tool `send` lỗi, câu trả lời của agent không nêu nguyên nhân thật. Chưa tính là gửi Telegram thật cho bonus vì `status: sent` chưa xảy ra.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) | 6 tool mới, mỗi tool có `tool.py` và `TOOL.md`, đăng ký trong `tools/__init__.py` và `tools.yaml`: `deduplicate`, `filter_sources`, `filter_by_date`, `validate_citations`, `openalex`, `semantic_scholar` | Bốn tool đầu xử lý danh sách item đã thu thập (lọc trùng URL, lọc theo tên miền, lọc theo ngày, kiểm tra trích dẫn). Hai tool sau: tạo thành công 2 tool tìm kiếm bài báo khoa học thông qua OpenAlex API và Semantic Scholar API. Có khả năng truy xuất, chuẩn hóa thông tin bài báo như tiêu đề, tác giả, năm xuất bản, abstract, DOI và số lượt trích dẫn. | Phụ thuộc vào API bên ngoài nên có thể gặp lỗi kết nối, giới hạn số request hoặc thiếu dữ liệu ở một số bài báo. Có xử lý lỗi và giới hạn số lượng kết quả trả về. |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py`; output `pytest` đầy đủ: `starter_v0/analysis/pytest_output.txt` (213 passed, 0 failed, 0 skipped) | Mỗi tool mới đều có test cho happy path, input xấu và nhánh lỗi trả error dict thay vì raise. Số test theo pytest (tính cả các case parametrize): `deduplicate` 22, `filter_sources` 12, `filter_by_date` 8, `validate_citations` 11, `openalex` 14, `semantic_scholar` 17. Test của `openalex` và `semantic_scholar` assert cả request gửi đi (URL, params, header) lẫn kết quả đã chuẩn hóa, và bao gồm `query` rỗng, `max_results` ngoài khoảng, `sort_by` sai, bản ghi thiếu field, HTTP 429/404/503, timeout, retry và giãn cách 1 giây của `semantic_scholar`. `tests/test_tool_contract.py` cũng xanh cho cả hai tool (85 passed). | Test dùng `fake_http` nên chưa đảm bảo khả năng chạy với API thật (giới hạn request, thay đổi định dạng trả về). Test của `openalex` và `semantic_scholar` được bổ sung sau khi hai tool đã được merge. |
| UI (lệnh chạy + link dùng thử) | `starter_v0/app.py`, `starter_v0/ui_core.py`, `starter_v0/tests/test_app_ui.py`, `starter_v0/tests/test_ui_core.py`; lệnh chạy và link ở mục A1 | UI Streamlit có chốt xác nhận trước khi chạy tool có tác dụng phụ; lệnh chạy: `streamlit run app.py --server.headless true` (từ `starter_v0/`). Test UI nằm trong cùng suite 213 test. | Link `trycloudflare.com` chỉ sống khi tunnel còn chạy. Link hiện đã tắt (xem A1) nên cần chạy lại tunnel trước khi demo. Transcript bằng chứng ở B4 là của `chat.py` (`starter_v0/transcripts/`, không bị ignore); transcript do UI tạo ghi vào `transcripts_ui/` và bị `.gitignore`, chưa có file nào. |

**Ví dụ lỗi unit test bắt được nhưng eval không bắt được:** sau khi merge hai tool `openalex` và `semantic_scholar`, `tools/__init__.py` đăng ký nhầm khoá `"senmatic_scholar"` thay vì `"semantic_scholar"`. `pytest` báo 2 test FAIL (`test_every_declared_tool_has_implementation[semantic_scholar]` và `test_declared_params_exist_in_function_signature[semantic_scholar]`, cùng lỗi `KeyError: 'semantic_scholar'`) và hết lỗi sau khi sửa tên khoá. Eval không thể bắt lỗi này vì không có case nào trong `eval_base.json` hay `eval_group.json` kỳ vọng `semantic_scholar`, nên mọi lần chạy eval đều không chạm tới tool này, trong khi nếu model gọi nó thì agent chỉ trả `unknown_tool` (`agent.py`).

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

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
