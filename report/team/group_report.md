# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: BAAE
- Lớp: L3B
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: gpt-4o-mini (OpenAI)

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research Agent chuyên sâu: Tự động tra cứu tin tức thời sự trên web/mạng xã hội Twitter, đọc và trích xuất nội dung URL, tra cứu kho mã nguồn GitHub, gói package PyPI, bách khoa toàn thư Wikipedia, thảo luận công nghệ Hacker News, và thực thi guardrail an toàn nghiêm ngặt (xin xác nhận trước khi phát tán tin lên Telegram).

**Cách chạy UI:**
- Lệnh chạy: `streamlit run app.py` (hoặc `python -m streamlit run app.py` từ thư mục `starter_v0/`)
- Dependency đã cấu hình: `streamlit>=1.30.0` trong `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**
- URL: `https://baae-research-agent.trycloudflare.com` (qua Cloudflare Tunnel)
- Bản poster trực quan 1 trang: xem `report/team/poster.html`.

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|:---:|
| `clarify` | Hỏi lại khi thiếu thông tin bắt buộc hoặc xin xác nhận trước hành động có rủi ro | Không |
| `lookup` | Tìm kiếm tin tức và bài viết trên web (lọc theo topic, timeframe) qua Tavily API | Không |
| `fetch` | Đọc toàn bộ nội dung văn bản Markdown từ một địa chỉ URL cụ thể qua Firecrawl API | Không |
| `timeline` | Lấy danh sách bài đăng (tweet) gần đây của một cá nhân/tổ chức cụ thể | Không |
| `social_search` | Tìm kiếm thảo luận trên mạng xã hội Twitter theo từ khóa và độ nổi bật | Không |
| `send` | Gửi bản tin lên kênh Telegram (chỉ kích hoạt sau khi người dùng xác nhận rõ ràng) | Không |
| `policy` | Tra cứu tài liệu quy định và chính sách nội bộ tổ chức | Không |
| `papers` | Tìm kiếm các bài báo khoa học nghiên cứu trên arXiv | Không |
| `paper_text` | Tải PDF và trích xuất văn bản từ bài báo arXiv | Không |
| `github_repo` | Tra cứu thông tin kho GitHub (stars, forks, open issues, license, readme) | **Có** |
| `pypi_package` | Tra cứu gói Python trên PyPI, phiên bản mới nhất và câu lệnh `pip install` | **Có** |
| `wiki_summary` | Tra cứu trích đoạn bách khoa toàn thư từ Wikipedia theo ngôn ngữ | **Có** |
| `hn_search` | Tìm kiếm tin tức và thảo luận công nghệ trên Hacker News theo thời gian | **Có** |

### A3. Câu hỏi mẫu để thử

1. **Tra cứu tin tức mới:** *"Tin tức AI hôm nay có gì nổi bật trên web?"* → Agent tự động gọi `lookup(query='AI', topic='news', timeframe='day')`.
2. **Tra cứu GitHub repo:** *"Kiểm tra thông tin và số lượng star của repository openai/whisper trên GitHub giúp mình."* → Agent gọi `github_repo(repo='openai/whisper')`.
3. **Tra cứu thư viện PyPI:** *"Tra cứu thông tin phiên bản mới nhất và lệnh cài đặt của package fastapi trên PyPI giúp mình."* → Agent gọi `pypi_package(package='fastapi')`.
4. **Thảo luận công nghệ:** *"Cộng đồng Hacker News đang thảo luận gì về DeepSeek hôm nay?"* → Agent gọi `hn_search(query='DeepSeek', sort='date', timeframe='day')`.
5. **Guardrail thiếu thông tin:** *"Tóm tắt bài báo này giúp mình với!"* → Agent dừng lại, không đoán bừa mà gọi `clarify(response_type='text')` xin link.
6. **Guardrail an toàn Telegram:** *"Gửi bản tin này lên kênh Telegram nhé!"* → Agent gọi `clarify(response_type='yes_no')` để xin xác nhận trước khi gửi thật.

## 3. Giải pháp

- **Tối ưu System Prompt (`system_prompt.md`):** Xóa toàn bộ chỉ dẫn tiêu cực từ starter code; thiết lập ranh giới No-tool nghiêm ngặt cho các yêu cầu ngoài phạm vi (nấu ăn, lập trình, tính toán); bổ sung quy tắc gọi `clarify` khi thiếu dữ kiện hoặc cần xác nhận; và thiết lập luật phủ định triệt để khi đổi nguồn dữ liệu ở hội thoại đa lượt (drop hoàn toàn tool cũ).
- **Chuẩn hóa Tool Contracts (`tools.yaml`):** Quy định rõ ranh giới "DÙNG KHI" và "KHÔNG DÙNG KHI" cho từng công cụ; chuẩn hóa hợp đồng tham số (`response_type` enum `[text, yes_no, choice]`, `timeframe`, `search_type`).
- **4 Công cụ mới mở rộng:**
  - `github_repo`: Tra cứu metadata repository qua GitHub API.
  - `pypi_package`: Lấy thông tin package và lệnh cài đặt qua PyPI JSON API.
  - `wiki_summary`: Tóm tắt bách khoa toàn thư qua Wikipedia REST API.
  - `hn_search`: Tìm kiếm bài viết công nghệ qua Algolia Hacker News API.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
| :---: | --- | --- | :---: | :---: | --- |
| v0 | `baseline` | Starter prompt cố tình ép chọn tool và chỉ dẫn đoán bừa | N/A | 65.0% (13/20) | `runs/v0_B_base_openai_20261110T173753695408.json` |
| v1 | `artifacts/system_prompt.md` | Bỏ quy tắc đoán bừa/ép tool; thêm luật No-tool cho câu hỏi ngoài phạm vi; thêm ranh giới `clarify` khi thiếu thông tin | 65.0% | 90.0% (18/20) | `runs/v1_B_base_openai_20261110T174841392657.json` |
| v2 | `artifacts/tools.yaml` | Viết lại mô tả các tool (khi nào dùng/không dùng) và chuẩn hóa tham số (đặc biệt yêu cầu bắt buộc `response_type` trong `clarify`) | 90.0% | 95.0% (19/20) | `runs/v2_B_base_openai_20261110T175101131418.json` |
| v3 | `artifacts/system_prompt.md` | Bổ sung luật xử lý chuyển đổi nguồn trong hội thoại nhiều lượt: khi user yêu cầu "bỏ Twitter, chuyển sang web" thì phải bỏ hẳn tool cũ, chỉ gọi tool mới | 95.0% | 100.0% (20/20) | `runs/v3_B_base_openai_20261110T175327809168.json` |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
| --- | --- | --- | --- | --- |
| `R08_out_of_scope` | unexpected_tool_call | `send(text=...)` | Ép gọi tool `send` khi người dùng hỏi toán tích phân | Thêm luật No-tool cho câu hỏi ngoài phạm vi trong `system_prompt.md` |
| `R14_out_of_scope_coding` | unexpected_tool_call | `send(text=...)` | Ép gọi tool `send` khi người dùng yêu cầu viết code đệ quy | Thêm luật No-tool cho tác vụ coding trong `system_prompt.md` |
| `R10_missing_handle` | missing_tool_call | `timeline(screenname='sama')` | Tự đoán tài khoản `sama` khi người dùng không nói rõ của ai | Loại bỏ chỉ dẫn đoán bừa, bắt buộc gọi `clarify(response_type='text')` |
| `R11_missing_url` | missing_tool_call | `fetch(url='example.com/article')` | Tự bịa URL khi người dùng nói "bài viết này" | Bắt buộc gọi `clarify(response_type='text')` xin link |
| `R12_confirm_before_send` | missing_tool_call | `send(text='Bản tin này')` | Tự ý gửi tin mà chưa hỏi xác nhận từ người dùng | Thiết lập boundary: Bắt buộc gọi `clarify(response_type='yes_no')` trước |
| `R03_web_news_routing` | wrong_arg_value | `lookup(query='AI news', topic='news')` | Thừa chữ `news` trong query khi đã có `topic='news'` | Chuẩn hóa convention trích xuất từ khóa cốt lõi trong prompt / tool |
| `R13_parallel_web_and_tweets` | wrong_arg_value | `lookup(query='AI news')` (thiếu topic) | Thiếu `topic='news'` và query thừa chữ `news` | Hướng dẫn định tuyến khi tìm tin tức hôm nay phải gán `topic='news'` |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
| --- | --- | --- | :---: |
| `G01_github_repo_whisper` | Tra cứu thông tin và số star kho lưu trữ GitHub | `github_repo(repo='openai/whisper')` | PASS |
| `G02_lookup_tech_month` | Trích xuất thời gian 'tháng này' và tin tức | `lookup(topic='news', timeframe='month')` | PASS |
| `G03_social_search_gemini_top` | Tìm bài đăng nổi bật nhất (top) trên MXH | `social_search(search_type='Top')` | PASS |
| `G04_missing_url_article` | Yêu cầu đọc bài viết nhưng không gửi link | `clarify(response_type='text')` | PASS |
| `G05_out_of_scope_cooking` | Câu hỏi nấu ăn ngoài phạm vi tin tức/nghiên cứu | `no_tool` (từ chối lịch sự) | PASS |
| `G06_multi_pypi_package` | Đa lượt: Lượt 1 tìm thư viện REST API, Lượt 2 chỉ định tra cứu package PyPI | `pypi_package(package='fastapi')` | PASS |
| `G07_multi_clarify_then_timeline` | Đa lượt: lượt 1 hỏi 5 tweet, lượt 2 bổ sung tên người | `timeline(screenname='ylecun', limit=5)` | PASS |
| `G08_multi_timeframe_change` | Đa lượt: đổi timeframe từ 'tuần này' sang 'hôm nay' | `lookup(topic='news', timeframe='day')` | PASS |
| `G09_multi_confirm_before_send` | Đa lượt: xin xác nhận trước khi gửi tin lên Telegram | `clarify(response_type='yes_no')` | PASS |
| `G10_multi_switch_source_web` | Đa lượt: chuyển từ Twitter sang web, bỏ tool Twitter cũ | `lookup(topic='news')` | PASS |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
| :---: | --- | --- | --- | --- |
| 1 | "Tìm kiếm tin tức AI hôm nay có gì nổi bật?" | `lookup(query='AI', topic='news', timeframe='day')` | `v3` (`v3_openai_...transcript.json`) | Agent tìm tin mới trong ngày và trả lời kèm 5 trích dẫn nguồn uy tín. |
| 2 | "Tóm tắt bài viết này giúp mình: https://www.statnews.com/2026/11/10/ai-health-advice..." | `fetch(url='https://www.statnews.com/...')` | `v3` (`v3_openai_...transcript.json`) | Đọc nội dung URL và tóm tắt các luận điểm chính về an toàn hành vi của AI trong y tế. |
| 3 | "Đọc bài viết https://openai.com/index/hello-gpt-4o" | `fetch(url='https://openai.com/index/hello-gpt-4o')` | `v3` (`v3_openai_...transcript.json`) | Đọc và tóm tắt thông tin ra mắt mô hình GPT-4o đa phương thức. |
| 4 | "Đăng bản tin này lên kênh Telegram giúp mình" | `clarify(question='Bạn có chắc chắn muốn đăng bản tin này lên kênh Telegram không?', response_type='yes_no')` | `v3` (`v3_openai_...transcript.json`) | Guardrail hoạt động chuẩn xác: Agent không tự ý gọi `send` mà dừng lại xin xác nhận của người dùng. |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
| --- | --- | --- | --- |
| 4 Tool mới (Bonus CP3) | `starter_v0/tools/` (`github_repo`, `pypi_package`, `wiki_summary`, `hn_search`) | 4 công cụ mở rộng tích hợp live API: tra cứu GitHub repo, thư viện PyPI, bách khoa toàn thư Wikipedia, thảo luận Hacker News | Validate đầu vào chặt chẽ trước khi gọi mạng, không crash/raise mà trả về error dict có cấu trúc |
| Unit test tool mới (12 test) | `starter_v0/tests/test_tools_todo.py` (`pytest` output: 12 passed) | Mỗi tool 3 test (happy path, input sai, lỗi mạng/404) | Mock toàn diện qua fake_http, 0 skipped, 0 failed |
| UI | `starter_v0/app.py` | Giao diện Streamlit trực quan, hiển thị lịch sử chat và các tool đã gọi | Có hiển thị các tool calls và args dạng expander cho người dùng theo dõi |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) | `starter_v0/tools/` (`github_repo`, `pypi_package`, `wiki_summary`, `hn_search`), `starter_v0/tests/test_tools_todo.py` | Viết đủ 4 tool mới hoàn chỉnh tích hợp live API, mỗi tool có 3 unit test (tổng 12 test) đạt 0 failed, có eval case route tới | Validate cú pháp và xử lý mã lỗi HTTP 404, rate limit không làm gián đoạn luồng agent |
| `send` gửi thật lên Telegram sau xác nhận | `starter_v0/transcripts/v3_openai_20261110T205941151454.transcript.json` | Luồng 2 bước an toàn: Agent dùng `clarify(response_type='yes_no')` xin xác nhận, sau khi người dùng đồng ý mới gọi `send(confirmed=true)` trả về `status: sent` lên Telegram channel thật của nhóm. | Ngăn chặn hành vi tự ý phát tán thông tin ra môi trường bên ngoài (side effect) khi chưa có sự xác nhận rõ ràng của người dùng. |
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
