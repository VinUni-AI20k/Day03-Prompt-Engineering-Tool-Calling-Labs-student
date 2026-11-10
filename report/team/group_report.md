# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
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
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | _ | _ | case_accuracy = 75% | v0_B_base_openrouter_20261110T173925903234 |
| v1 | system prompt — thay chỉ dẫn tự đoán account/URL bằng kiểm tra lịch sử và hỏi lại | Prompt v0 khuyến khích tự đoán khi thiếu thông tin, khiến agent tự chọn tài khoản và tạo URL. Thay chỉ dẫn này bằng quy tắc kiểm tra lịch sử hội thoại và gọi clarify khi vẫn thiếu account hoặc URL sẽ giảm lỗi missing_info. | case_accuracy = 75% | case_accuracy = 85% |  |
| v2 |  | V1 đã chọn đúng tool clarify nhưng bỏ qua tham số response_type. Làm rõ trong tool declaration rằng khi hỏi thông tin còn thiếu phải truyền tường minh response_type="text" sẽ giảm lỗi wrong_arg_value, giúp R10/R11 đạt PASS. |  |  |  |
| v3 |  |  |  |  |  |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Version | Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|---|
| v0 | R08_out_of_scope | out_of_scope | send(text="Nguyên hàm…") | Câu hỏi toán không cần tool nhưng agent gọi tool gửi Telegram | Quy định câu hỏi không cần công cụ thì trả lời trực tiếp; send chỉ dùng để xuất bản khi đủ xác nhận |
| v0 | R10_missing_handle | missing_info | timeline(screenname="sama") | Tự đoán tài khoản khi user chưa cung cấp | Kiểm tra lịch sử; nếu chưa có tài khoản thì gọi clarify(response_type="text") |
| v0 | R11_missing_url | missing_info | fetch(url="https://example.com/article") | Tự tạo URL khi user chưa cung cấp | Kiểm tra lịch sử; nếu chưa có URL thì gọi clarify(response_type="text") |
| v0 | R12_confirm_before_send | wrong_boundary | send(text="Bản tin này") | Gọi gửi khi chưa xác nhận; dùng cụm “Bản tin này” làm nội dung thay vì xác định bản tin | Yêu cầu xác nhận bằng clarify(response_type="yes_no"); chỉ gửi nội dung cụ thể đã được xác nhận |
| v0 | R13_parallel_web_and_tweets | wrong_arg_value | lookup(query="AI news", timeframe="day") và social_search(query="AI", search_type="Latest") | Chọn đúng hai tool nhưng sai query và thiếu topic="news" | Làm rõ cách tách chủ đề, loại tìm kiếm và thời gian thành các arguments riêng |
| v1 | R10_missing_handle | wrong_arg_value | clarify(question="Bạn muốn tóm tắt tweet của tài khoản nào?") | V1: đã chọn đúng clarify, nhưng thiếu response_type; expected "text", actual không có. | Đề xuất: quy định gọi clarify để hỏi thông tin còn thiếu phải truyền rõ response_type="text"; làm rõ yêu cầu này trong tool declaration. |
| v1 | R11_missing_url | wrong_arg_value | clarify(question="Bạn vui lòng cung cấp URL của bài viết mà bạn muốn tóm tắt?") | V1: đã chọn đúng clarify, nhưng thiếu response_type; expected "text", actual không có. | Đề xuất: yêu cầu truyền rõ response_type="text" khi hỏi URL, rồi chạy lại kiểm tra. |
| v1 | R12_confirm_before_send | wrong_boundary | send(text="Bản tin này") | V1: vẫn gọi send thay vì clarify(response_type="yes_no") để xin xác nhận; chưa xác định nội dung bản tin cụ thể. | Đề xuất: bỏ chỉ dẫn gửi ngay; yêu cầu xác định nội dung và xin xác nhận trước khi gọi send. |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |


### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_policy_routing | Chọn tool tra cứu chính sách nội bộ khi người dùng hỏi về việc đưa dữ liệu khách hàng vào ChatGPT. | Gọi policy với policy_area="data_privacy". |  |
| G02_papers_sort_latest | Tìm paper trên arXiv và chọn cách sắp xếp theo ngày nộp mới nhất. | Gọi papers với sort_by="submittedDate". |  |
| G03_handle_strip_at | Chuẩn hóa tài khoản có ký tự @ và truyền đúng số lượng bài đăng. | Gọi timeline với screenname="ylecun", limit=3. |  |
| G04_news_timeframe_month | Nhận diện yêu cầu tìm tin tức trong tháng và truyền đúng loại tìm kiếm, khoảng thời gian. | Gọi lookup với topic="news", timeframe="month". |  |
| G05_out_of_scope_poem | Không gọi tool khi người dùng yêu cầu sáng tác thơ, không cần công cụ research. | Trả lời trực tiếp, không gọi tool. |  |
| G06_clarify_then_paper | Sử dụng thông tin paper được bổ sung trong hội thoại để đọc nội dung, không tìm kiếm lại không cần thiết. | Gọi paper_text sau khi người dùng cung cấp arXiv ID và yêu cầu đọc paper. Điều kiện expect hiện tại kiểm tra tên tool paper_text. |  |
| G07_confirm_before_send_multiturn | Giữ bước xin xác nhận xuất bản sau chuỗi yêu cầu tìm tin và tóm tắt. | Gọi clarify với response_type="yes_no" khi người dùng yêu cầu đăng bản tóm tắt. |  |
| G08_send_after_confirmation | Thực hiện gửi sau khi người dùng đã xác nhận rõ nội dung và đồng ý gửi. | Gọi send với confirmed=true. |  |
| G09_switch_timeline_to_top_search | Nhận diện việc người dùng đổi ý từ xem bài của một tài khoản sang tìm bài nổi bật theo chủ đề. | Gọi social_search với search_type="Top". |  |
| G10_papers_refine_args | Kết hợp yêu cầu số lượng và cách sắp xếp được bổ sung qua nhiều lượt. | Gọi papers với max_results=3, sort_by="submittedDate". |  |


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
