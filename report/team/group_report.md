# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: GroupT
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3:

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
| deduplicate_news | gộp tin trùng theo URL chuẩn hoá hoặc mức độ từ chung trong tiêu đề | có |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

- Thêm `deduplicate_news`, tool xử lý cục bộ để gộp tin trùng khi người dùng có ít nhất hai tin từ các nguồn và muốn loại bỏ trùng lặp. Tool chuẩn hoá URL trước, sau đó so các từ trong tiêu đề; nguồn được gộp và summary dài hơn được giữ lại. Dùng trước `format`, không dùng để tìm tin mới hoặc tóm tắt một bài.

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
| G01_wikipedia_knowledge_summary | Câu hỏi kiến thức nền “X là ai?” | `wiki_sum(title="Ada Lovelace")` | Chưa có run group trong `starter_v0/runs/` |
| G02_validate_shortened_link | Kiểm tra URL cụ thể và link rút gọn | `validate_url(url="https://bit.ly/ai-update")`; diễn giải thận trọng, không khẳng định an toàn tuyệt đối | Chưa có run group trong `starter_v0/runs/` |
| G03_direct_local_time | Hỏi giờ hiện tại tại một thành phố | `date_localized(timezone="America/Los_Angeles")` | Chưa có run group trong `starter_v0/runs/` |
| G04_today_news_uses_lookup | Tìm tin “hôm nay”, phân biệt với hỏi giờ hiện tại | `lookup(query="AI", topic="news", timeframe="day")` | Chưa có run group trong `starter_v0/runs/` |
| G05_specific_article_uses_fetch | Đọc/tóm tắt URL đã cung cấp, không kiểm tra URL trước | `fetch(url="https://openai.com/research/")` | Chưa có run group trong `starter_v0/runs/` |
| G06_multiturn_time_location | Dùng địa điểm được làm rõ qua nhiều lượt | `date_localized(timezone="Asia/Tokyo")` | Chưa có run group trong `starter_v0/runs/` |
| G07_multiturn_url_validation | Dùng URL từ lượt trước để kiểm tra URL | `validate_url(url="https://tinyurl.com/example-check")` | Chưa có run group trong `starter_v0/runs/` |
| G08_multiturn_wikipedia_followup | Yêu cầu tiếp nối về đoạn giới thiệu Wikipedia | `wiki_sum(title="Alan Turing")` | Chưa có run group trong `starter_v0/runs/` |
| G09_multiturn_news_topic_correction | Giữ timeframe hôm nay và cập nhật chủ đề đã sửa | `lookup(query="robotics", topic="news", timeframe="day")` | Chưa có run group trong `starter_v0/runs/` |
| G10_multiturn_publish_confirmation | Chuẩn bị nội dung nhưng yêu cầu xác nhận trước khi gửi | Gọi `clarify(response_type="yes_no")`; không gọi `send` khi chưa được cho phép | Chưa có run group trong `starter_v0/runs/` |

> Lưu ý CP4: `eval_group.json` hiện có đủ 10 case (5 single-turn, 5 multi-turn), nhưng chưa có case nào kiểm tra routing tới tool mới `deduplicate_news`, dù đây là yêu cầu CP4.

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) | `starter_v0/tools/deduplicate_news/tool.py`, `starter_v0/tools/deduplicate_news/TOOL.md`, đăng ký tại `starter_v0/tools/__init__.py` và `starter_v0/artifacts/tools.yaml` | Gộp theo URL HTTP(S) đã chuẩn hoá hoặc độ tương đồng tiêu đề; giữ summary dài hơn và kết hợp nguồn. Tool chạy cục bộ, không gọi mạng. | Chỉ xử lý các tin đã có; không tìm tin mới hoặc tóm tắt bài. Mặc định ngưỡng tiêu đề là 0.8; đầu vào không hợp lệ trả error dict. |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py` | Có 4 test: gộp URL đã chuẩn hoá/kết hợp nguồn, gộp theo từ chung trong tiêu đề, trả lỗi với title đầu vào không hợp lệ, và trả lỗi với threshold không hợp lệ. | Các test xác nhận hành vi code của tool, không xác nhận model có chọn gọi tool đúng. Chạy `pytest tests/test_tools_todo.py -k deduplicate_news` để kiểm tra. |
| UI (lệnh chạy + link dùng thử) | Chưa triển khai (CP5) | — | — |

Unit test tool mới: đã viết 4 test. Ví dụ lỗi mà unit test có thể bắt nhưng eval routing không bắt: `title` rỗng hoặc `title_similarity_threshold` ngoài khoảng `(0, 1]` phải trả error dict thay vì xử lý đầu vào sai. Chưa ghi nhận kết quả chạy pytest trong phần bằng chứng hiện có.

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

- **Xác định thế nào là tin trùng:** URL có thể khác do `www`, chữ hoa/thường, dấu `/` cuối, fragment hoặc tham số tracking; tiêu đề cũng có thể khác một vài từ. Tool `deduplicate_news` xử lý URL đã chuẩn hoá trước, sau đó mới so độ tương đồng tiêu đề theo ngưỡng; khi gộp thì giữ summary dài hơn và kết hợp nguồn. Logic được triển khai tại `starter_v0/tools/deduplicate_news/tool.py` và quy tắc sử dụng được ghi ở `starter_v0/tools/deduplicate_news/TOOL.md`.
- **Đầu vào do model tạo có thể không hợp lệ:** Để tránh làm hỏng lượt chạy khi thiếu title hoặc truyền ngưỡng ngoài phạm vi, tool kiểm tra đầu vào và trả error dict. Bốn test trong `starter_v0/tests/test_tools_todo.py` bao phủ gộp URL, gộp theo tiêu đề và hai nhánh đầu vào lỗi. Repo chưa có output pytest để xác nhận kết quả chạy, nên không kết luận test đã pass.
- **Thiết kế eval nhiều lượt và kiểm chứng routing:** Bộ `starter_v0/data/eval_group.json` đã có đủ 5 case single-turn và 5 case multi-turn, gồm các tình huống cần giữ ngữ cảnh như URL, địa điểm, timeframe/chủ đề và xác nhận trước khi gửi. Tuy vậy, chưa có run group trong `starter_v0/runs/`, và bộ case hiện tại chưa kiểm tra model gọi `deduplicate_news`; hai điểm này cần bổ sung/chạy trước khi kết luận về hành vi của model. Không có bằng chứng hiện có về lỗi provider hoặc hết quota.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- **Fix thuộc `system_prompt.md`:** Nêu rõ quy tắc chọn tool theo ý định người dùng: kiến thức nền dùng `wiki_sum`; kiểm tra URL chỉ dùng `validate_url` khi được hỏi; hỏi giờ trực tiếp dùng `date_localized`, còn tìm tin theo “hôm nay/tuần này” dùng `lookup` với timeframe tương ứng. Prompt cũng yêu cầu xin xác nhận trước khi gửi/đăng. Những quy tắc này có trong `starter_v0/artifacts/system_prompt.md`.
- **Fix thuộc `tools.yaml`:** Khai báo `deduplicate_news`, điều kiện dùng trước `format`, giới hạn không tìm bài mới/tóm tắt bài và ngưỡng so sánh tiêu đề mặc định `0.8`. Theo `version_log.csv`, v1 chỉ đổi `system_prompt.md` và giữ nguyên `tools_hash`; các mô tả tool core trong `tools.yaml` hiện vẫn còn chung chung, nên cần được cụ thể hoá và đánh giá riêng ở version sau.
- **Failure cần review thủ công:** Kết quả tool call đúng chưa đảm bảo nội dung tóm tắt chính xác, nguồn đáng tin, hoặc diễn giải về URL không gây cảm giác an toàn tuyệt đối. Tương tự, ranh giới xác nhận gửi/đăng cần kiểm tra ngữ cảnh hội thoại và nội dung/đích đến; một eval chỉ so tên tool và một số args có thể bỏ sót chất lượng câu trả lời cuối.
- **Nếu có thêm một vòng:** Trước tiên thêm case group kiểm tra routing tới `deduplicate_news`, chạy `python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json` và lưu run để điền kết quả B3. Sau đó, ở một version riêng chỉ sửa mô tả tool trong `tools.yaml` (khi nào dùng/không dùng và quy ước args), rồi chạy lại cùng bộ base để so sánh. Hiện chưa có run group nên chưa thể kết luận giả thuyết nào cải thiện routing trên các case mới.

## 8. Tài liệu tham khảo
Đề bài và repo gốc: https://github.com/VinUni-AI20k/K5-L3-DAY03-ResearchAgentToolEval (README.md, RULES.md, RUBRIC.md, SUBMISSION.md, CHECKPOINTS.md)
Wikipedia REST API (endpoint page/summary) dùng trong wiki_sum: https://en.wikipedia.org/api/rest_v1/
Streamlit (UI): https://docs.streamlit.io/
Cloudflare quick tunnel (link dùng thử UI): https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/do-more-with-tunnels/trycloudflare/
Công cụ AI dùng hỗ trợ code/phân tích log: ghi trong báo cáo cá nhân của từng thành viên.
