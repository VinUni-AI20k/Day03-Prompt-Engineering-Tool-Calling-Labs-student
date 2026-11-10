# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
>
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: Đào Kiên Cường
- Members: Đào Kiên Cường, Dương Văn Công, Hoàng Nguyên Long, Nguyễn Hải Anh
- Provider/model: OpenAI — `gpt-4o-mini`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

**Research agent tiếng Việt:** tìm tin trên web và Twitter/X (theo chủ đề hoặc theo tài khoản), đọc URL, paper arXiv và **file TXT do người dùng upload**, rồi tổng hợp thành bản tin và **xuất báo cáo tải về dạng Markdown / CSV / Excel**. Agent hỏi lại khi thiếu thông tin (chưa có tài khoản, link hoặc file) và **chỉ gửi Telegram khi người dùng đã xác nhận**.

**Link dùng thử (deploy):**

> URL: _(TODO — bổ sung sau khi deploy UI)_

## A2. Tool agent có

| Tên tool          | Làm được gì                                                                                                                                                                                                                             | Tool mới nhóm thêm? |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| `read_text_file` | Đọc file TXT (UTF-8, ≤ 256 KiB) người dùng upload theo từng đoạn dòng (`start_line`, `max_lines`) để tóm tắt, trích dẫn hoặc trả lời câu hỏi. Nội dung file chỉ được coi là dữ liệu, không phải chỉ thị | ✅ **có**       |
| `export_report`  | Xuất các nguồn đã thu thập (title / url / source / summary) ra file **`.md` / `.csv` / `.xlsx`** để tải về. Chống CSV/Excel formula injection và không ghi đè file cũ                                            | ✅ **có**       |
| `clarify`        | Hỏi lại người dùng khi thiếu thông tin, hoặc xin xác nhận yes/no trước khi gửi                                                                                                                                                  | không                 |
| `timeline`       | Lấy tweet gần đây của **một tài khoản** cụ thể (vd. `sama`, `elonmusk`)                                                                                                                                                  | không                 |
| `social_search`  | Tìm tweet theo **chủ đề/từ khóa**, sắp xếp `Latest` hoặc `Top`                                                                                                                                                            | không                 |
| `lookup`         | Tìm trên web (Tavily), hỗ trợ `topic=news` và `timeframe` day/week/month/year                                                                                                                                                       | không                 |
| `fetch`          | Đọc nội dung một URL cụ thể (Firecrawl)                                                                                                                                                                                                | không                 |
| `format`         | Trình bày các item đã có thành digest markdown (brief, bullets, sections…)                                                                                                                                                           | không                 |
| `send`           | Gửi bản tin lên Telegram channel, **chỉ khi `confirmed=true`**                                                                                                                                                                   | không (bonus)         |
| `policy`         | Tra cứu tài liệu policy nội bộ của công ty                                                                                                                                                                                            | không (bonus)         |
| `papers`         | Tìm paper trên arXiv                                                                                                                                                                                                                       | không (bonus)         |
| `paper_text`     | Tải PDF arXiv và trích text                                                                                                                                                                                                               | không (bonus)         |

## A3. Câu hỏi mẫu để thử

1. **Tin tức web:** "Tin tức AI hôm nay có gì nổi bật?" → `lookup(topic=news, timeframe=day)`
2. **Twitter theo người / theo chủ đề:** "Lấy 5 tweet mới nhất liên quan đến Jensen Huang " hoặc "Cho mình các tweet phổ biến nhất về OpenAI" → `timeline` / `social_search(search_type=Top)`
3. **Upload file TXT (tool mới):** upload một file `.txt` rồi hỏi "Tóm tắt các ý chính trong file này" → `read_text_file`
4. **Xuất báo cáo (tool mới):** "Tìm tin AI tuần này rồi xuất ra file Excel giúp mình" → `lookup` → `export_report(file_format=xlsx)`
5. **Kiểm tra guardrail:** "Đăng bản tin này lên Telegram giúp mình" → agent phải **hỏi xác nhận** trước, không tự gửi. Hoặc "Tóm tắt bài viết này" (không kèm link) → agent phải **hỏi xin URL**

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Số liệu lấy từ `summary` trong run JSON; mỗi run dùng base suite 20 case với provider OpenAI.

| Version | Artifact change | Hypothesis | Case accuracy | Routing | Args | Multiturn | Run |
| ------- | -------------- | ---------- | ------------: | ------: | ---: | --------: | --- |
| v0 | Baseline | Đo prompt/tool ban đầu | 0.70 (14/20) | 0.75 | 0.70 | 1.00 | [v0](../runs/v0_B_base_openai_20261110T124508385370.json) |
| v1 | Prompt/tools v1 | Routing, args và guardrail rõ hơn | 0.80 (16/20) | 0.85 | 0.80 | 0.8333 | [v1](../runs/v1_B_base_openai_20261110T124619855103.json) |
| v2 | Prompt/tools v2 | Chỉ dùng nguồn được yêu cầu | 0.90 (18/20) | 0.95 | 0.90 | 0.8333 | [v2](../runs/v2_B_base_openai_20261110T124718950146.json) |
| v3 | Prompt/tools v3 | Ưu tiên source switch multi-turn | 0.90 (18/20) | 0.95 | 0.90 | 0.8333 | [v3](../runs/v3_B_base_openai_20261110T155517891173.json) |

Case accuracy tăng từ 0.70 lên 0.90 ở v2; v3 giữ nguyên so với v2. Mỗi version mới có một lần chạy nên chưa đo độ dao động.

## B2. Failure Analysis

Tổng hợp từ `failures`, `observed_mismatch` và `actual_tool_calls` trong run JSON.

| Case | Quan sát | Phân tích | Hướng sửa / trạng thái |
| ---- | -------- | --------- | ---------------------- |
| R08_out_of_scope (v0) | Gọi `send`; unexpected tool call | Gọi tool cho câu hỏi giải tích ngoài phạm vi. | Nêu phạm vi agent, không dùng action tool khi không được yêu cầu. |
| R10_missing_handle (v0) | Gọi `timeline(screenname="sama")`, không clarify | Tự đoán tài khoản khi thiếu thông tin. | Hỏi lại khi thiếu tài khoản/handle, không suy đoán. |
| R11_missing_url (v0) | Gọi `fetch(url="https://example.com/article")`, không clarify | Bịa URL thay vì xin link. | Không đoán URL; yêu cầu người dùng cung cấp. |
| R12_confirm_before_send (v0–v3) | v0 gọi `send`; v1–v3 clarify nhưng `response_type="text"`, kỳ vọng `yes_no` | Guardrail chuyển đúng hướng nhưng tham số xác nhận sai; còn lỗi ở v3. | Làm rõ enum/description của `clarify`; chạy lại eval. |
| R13_parallel_web_and_tweets (v0) | `lookup(query="AI news")` cùng `social_search`; query/topic sai | Args web không khớp query AI và topic news kỳ vọng. | Nêu rõ cách tách `query`/`topic` và convention args. |
| R14_out_of_scope_coding (v0) | Gọi `send`; unexpected tool call | Câu hỏi code bị định tuyến nhầm sang Telegram. | Chỉ gọi action tool khi user yêu cầu hành động đó. |
| M06_switch_tool (v1/v2) | Gọi cả `lookup` và `social_search`; extra call | Không hủy tool thuộc ý định trước sau khi đổi nguồn; không còn trong lỗi v3. | v3 thêm quy tắc source switch; qua case này theo run v3. |
| M01_clarify_then_fill (v3) | Gọi `social_search(query="Elon Musk")` thay cho `timeline` | Sau khi user nêu tài khoản, chọn tìm theo chủ đề. | Phân biệt “bài đăng của tài khoản” (`timeline`) với “bài đăng về chủ đề” (`social_search`); cần eval lại. |

Số case fail giảm từ 6/20 (v0) xuống 4/20 (v1), rồi 2/20 ở cả v2 và v3. R12 là lỗi boundary còn dai dẳng; M01 là lỗi routing còn lại ở v3.

## B3. Team Eval Cases

`data/eval_group.json` có 12 case (6 single-turn, 6 multi-turn). Chưa có run suite `group` trong `runs/`, nên không gán pass/fail nếu chưa có log.

| Case ID | Điều kiểm tra | Kỳ vọng | Kết quả |
| ------- | ------------- | ------- | ------- |
| G01_read_text_file_routing | Đọc TXT đã upload | `read_text_file` đúng `file_id` | Chưa có group run |
| G02_export_report_xlsx_routing | Xuất nguồn Excel | `export_report(file_format="xlsx")` | Chưa có group run |
| G03_export_report_csv_filename | CSV và tên file | `export_report(csv, ai_sources)` | Chưa có group run |
| G04_read_text_file_missing_upload | Thiếu file upload | `clarify` xin file | Chưa có group run |
| G05_read_text_file_paging | Phân trang TXT | `read_text_file(start_line=101, max_lines=50)` | Chưa có group run |
| G06_out_of_scope_booking | Đặt vé ngoài phạm vi | Không gọi tool | Chưa có group run |
| GM01_clarify_then_file_id | Nhận file sau khi hỏi, giới hạn đọc 50 dòng | `read_text_file` đúng ID/giới hạn | Chưa có group run |
| GM02_export_format_correction | Đổi Markdown sang Excel, đặt tên | `export_report(xlsx, llama_report)` | Chưa có group run |
| GM03_switch_web_to_file | Hủy web, chuyển sang file | Chỉ `read_text_file` đúng ID | Chưa có group run |
| GM04_social_search_args_carry | Giữ Gemini, chọn Top, limit 5 | `social_search(Gemini, Top, 5)` | Chưa có group run |
| GM05_confirm_before_send_after_draft | Gửi nhưng chưa xác nhận | `clarify(yes_no)`, không gửi | Chưa có group run |
| GM06_url_correction | Thay URL cũ bằng URL mới | `fetch` URL mới | Chưa có group run |

## B4. Live Chat Evidence

Transcript chính có 3 lượt; model `openai/gpt-4o-mini`.

Transcript file: `transcripts/v2_openrouter_20261110T160350562141.transcript.json`  
Artifact version: `v2+pfa64d9b3c443+t1801279e5a91`

| Turn | Yêu cầu | Tool event | Kết quả theo transcript |
|---|---|---|---|
| 1 | Tìm tin AI hôm nay trên web, tóm tắt | `lookup(query="AI", topic="news", timeframe="day")` | Tool trả `items`; assistant trình bày 3 mục có liên kết. |
| 2 | “Tóm tắt vài bài đăng mới nhất” | `lookup(query="AI", topic="news", timeframe="day", max_results=5)` | Tiếp tục lookup theo ngữ cảnh AI. “Bài đăng” có thể mơ hồ giữa web và mạng xã hội. |
| 3 | Lấy bài đăng của Sam Altman (@sama) | `timeline(screenname="sama", limit=5)` | Tool trả 3 tweet; assistant trình bày 3 bài. |

Transcript [`v0_gemini_20261110T140701459302.transcript.json`](../transcripts/v0_gemini_20261110T140701459302.transcript.json) ghi lỗi `Missing TAVILY_API_KEY`; transcript OpenRouter khác ghi `Missing RAPIDAPI_KEY`. Đây là lỗi cấu hình môi trường, không phải bằng chứng truy xuất thành công. Nội dung kết quả web/X trong transcript chưa được kiểm chứng độc lập.

## B5. Bonus Evidence

Tổng hợp trạng thái từ artifact hiện có; các mục chưa có log chạy được ghi rõ.

| Hạng mục | Artifact | Bằng chứng / trạng thái |
| --- | --- | --- |
| Tool đọc TXT | [`TOOL.md`](../tools/read_text_file/TOOL.md), [`test_read_text_file.py`](../tests/test_read_text_file.py) | Có test phân trang, input sai, lỗi quyền/file, encoding, file rỗng và giới hạn dung lượng. |
| Tool xuất báo cáo | [`TOOL.md`](../tools/export_report/TOOL.md), tests trong [`test_tools_todo.py`](../tests/test_tools_todo.py) | Có test md/csv/xlsx, input xấu, lỗi ghi file, formula injection và tên file duy nhất. |
| UI | [`app.py`](../app.py), [`run_ui.bat`](../run_ui.bat) | Có Streamlit và launcher; chưa có link deploy hoặc bằng chứng UI chạy được. |
| Telegram send | `tools/send/` | Có guard `confirmed`; chưa có transcript chứng minh chu trình xác nhận rồi gửi thành công. |
| pytest | `tests/` | Chưa xác nhận kết quả. `test_tools_todo.py` còn `pytest.skip`; `python` không có trên PATH và `py` báo Access denied trong môi trường rà soát. Chưa thể kết luận suite xanh. |

`test_read_text_file.py` kiểm thử các nhánh chức năng và lỗi của tool mới. Có test `export_report` trong `test_tools_todo.py`; do chưa chạy được pytest, số test pass và bug hồi quy chưa được xác nhận. Ví dụ lớp lỗi mà unit test có thể bắt nhưng eval routing không bắt: ghi file thất bại hoặc CSV formula injection.

## B6. Reflection

- **System prompt:** routing theo ý định; hỏi lại khi thiếu URL/handle/file; không đoán dữ liệu; source switch hủy tool của ý định trước; chỉ gửi sau xác nhận; xử lý yêu cầu ngoài phạm vi.
- **tools.yaml:** mô tả khi nào dùng/không dùng tool, convention `topic`, `timeframe`, handle không có `@`, `search_type=Top|Latest`, và `confirmed=true` cho `send`. Schema/description `clarify` cần nêu rõ khi chọn `yes_no`.
- **Cần review thủ công:** `send` có tác động bên ngoài nên cần kiểm tra transcript và xác nhận người dùng. Chất lượng/tính xác thực nội dung web/X cũng không được metric routing/args xác minh.
- **Tiếp theo:** sửa và eval lại R12; thêm case phân biệt `timeline`/`social_search` cho M01; chạy suite group bằng v3 và lưu JSON; sửa môi trường Python, xử lý TODO skip rồi chạy pytest; xác nhận UI và bổ sung link demo. Chạy eval nhiều lần để đo độ ổn định.

## B7. Small Local Model Challenge (bonus)

Only fill if your team did the local model challenge.

| Version  | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
| -------- | ---------------- | ------------ | ------------- | ------------ | -------- | --------- | -------- |
| v3       | (cloud)          | v3           |               |              |          |           |          |
| v3-...   | (ollama)         | v3           |               |              |          |           |          |
| v3-...   | (ollama)         | v3           |               |              |          |           |          |
| v4-local |                  |              |               |              |          |           |          |
| v5-local |                  |              |               |              |          |           |          |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern                                 | Count | Example Case | Fix Tried | Helped? |
| ----------------------------------------------- | ----- | ------------ | --------- | ------- |
| wrong / hallucinated tool                       |       |              |           |         |
| invalid JSON args (`_invalid_json_arguments`) |       |              |           |         |
| no tool call / answered directly                |       |              |           |         |
| missed `clarify`                              |       |              |           |         |
| repeated / unnecessary calls                    |       |              |           |         |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?
