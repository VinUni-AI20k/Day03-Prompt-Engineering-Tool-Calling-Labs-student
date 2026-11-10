# Day 03 Lab v2 Report — Research Agent

> Báo cáo được điền theo các artifact có trong repository tại thời điểm kiểm tra. Không suy diễn kết quả cho run, transcript, deployment hoặc thông tin nhóm chưa được commit; các mục thiếu bằng chứng được đánh dấu rõ.

## Team

- Team: chưa có thông tin trong repository.
- Members: chưa có thông tin trong repository.
- Provider/model: OpenRouter / `openai/gpt-4o-mini` (theo run baseline v0).

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent hỗ trợ tìm tin trên web và mạng xã hội, xem bài đăng theo tài khoản, đọc URL, tìm và đọc paper arXiv, tra cứu policy nội bộ, loại URL trùng và định dạng kết quả thành digest. Tool gửi Telegram là hành động có tác động bên ngoài; cần xác nhận rõ ràng trước khi gửi.

**Link dùng thử (deploy):** chưa có URL deploy được lưu trong repository. Có `app.py`, nhưng chưa có bằng chứng về deployment công khai.

## A2. Tool agent có

Các tool dưới đây được khai báo trong `artifacts/tools.yaml` và đăng ký trong `tools/__init__.py` (`TOOL_FUNCTIONS`); “có” nghĩa là tool được triển khai/đăng ký trong repo, không phải là tool mới nhóm thêm.

| Tên tool | Làm được gì | Phân loại / evidence |
|---|---|---|
| `clarify` | Hỏi người dùng để bổ sung thông tin còn thiếu hoặc xác nhận hành động. | Có · `tools/clarify/` |
| `timeline` | Lấy bài đăng gần đây theo tài khoản; cần handle/tên tài khoản. | Có · `tools/timeline/` |
| `social_search` | Tìm bài đăng mạng xã hội theo từ khóa, sắp xếp `Latest` hoặc `Top`. | Có · `tools/social_search/` |
| `lookup` | Tìm kiếm web; hỗ trợ chủ đề chung/tin tức và khoảng thời gian. | Có · `tools/lookup/` |
| `fetch` | Đọc nội dung từ URL người dùng cung cấp. | Có · `tools/fetch/` |
| `format` | Định dạng các nguồn đã thu thập thành digest/bullets/thread. | Có · `tools/format/` |
| `send` | Gửi nội dung lên Telegram; chỉ thực hiện sau xác nhận rõ ràng (`confirmed=true`). | Có (bonus) · `tools/send/` |
| `policy` | Tìm kiếm tài liệu policy nội bộ trong knowledge base của lab. | Có (bonus) · `tools/policy/` |
| `papers` | Tìm paper khoa học trên arXiv. | Có (bonus) · `tools/papers/` |
| `paper_text` | Trích xuất nội dung văn bản từ paper arXiv. | Có (bonus) · `tools/paper_text/` |
| `deduplicate_sources` | Loại URL trùng đã chuẩn hóa, giữ thứ tự và metadata của nguồn đầu tiên. | Tool mới nhóm thêm · `tools/deduplicate_sources/` |

## A3. Câu hỏi mẫu để thử

1. “Tin tức AI hôm nay có gì nổi bật?”
2. “Mọi người đang bàn gì về GPT-5 trên Twitter?”
3. “Tóm tắt 5 tweet mới nhất của Elon Musk.”
4. “Tìm các paper mới về RAG rồi tóm tắt nội dung một paper.”
5. “Bỏ các nguồn có URL trùng trong danh sách này: [dán danh sách URL].”

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Bằng chứng hiện có chỉ gồm một run baseline v0. `version_log.csv` chưa có dòng log version nào; chưa tìm thấy run v1–v3 nên không thể báo cáo metric trước/sau cho các phiên bản đó.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | Baseline: prompt và tool declarations hiện có | Baseline để đo routing, arguments, multi-turn và boundary. | N/A | case accuracy 0.75 (15/20); tool routing 0.80; argument 0.75; multi-turn 1.00 | `runs/v0_B_base_openrouter_20261110T102236137498.json` |
| v1 | Chưa có bằng chứng | Chưa ghi nhận | N/A | N/A | Chưa có |
| v2 | Chưa có bằng chứng | Chưa ghi nhận | N/A | N/A | Chưa có |
| v3 | Chưa có bằng chứng | Chưa ghi nhận | N/A | N/A | Chưa có |

Run v0 có 20/20 case được đo và 0 provider error. Tổng kết ghi nhận 5 case fail: 1 `out_of_scope`, 2 `missing_info`, 1 `wrong_boundary`, 1 `wrong_tool`; mismatch gồm 1 unexpected tool call, 3 missing tool calls và 1 wrong argument value.

## B2. Failure Analysis

Các lỗi dưới đây lấy từ run v0 và `analysis/base_runs.csv`. Với R13, artifact phân tích xác nhận sai arguments nhưng không hiển thị rõ các giá trị thực tế trong bản CSV hiện có, nên không suy đoán giá trị đó.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `R08_out_of_scope` | `out_of_scope` | `send` | Câu hỏi tích phân ngoài phạm vi research nhưng agent gọi tool gửi Telegram. | Nêu rõ phạm vi agent và quy tắc không gọi tool cho yêu cầu ngoài phạm vi; không chọn action tool để trả lời nội dung. |
| `R10_missing_handle` | `missing_info` | `timeline(screenname="sama")` | Tự đoán tài khoản khi người dùng chưa nêu handle; đáng lẽ hỏi lại bằng `clarify`. | Bổ sung quy tắc thiếu account/handle thì hỏi, không suy đoán từ ngữ cảnh không có. |
| `R11_missing_url` | `missing_info` | `fetch` | Gọi fetch dù người dùng chưa cung cấp URL; đáng lẽ hỏi xin link. | Quy định `fetch` chỉ dùng khi có URL cụ thể; nếu thiếu URL thì `clarify`. |
| `R12_confirm_before_send` | `wrong_boundary` | `send` | Bắt đầu luồng gửi mà chưa hỏi xác nhận người dùng. | Yêu cầu xác nhận yes/no trước; chỉ gọi `send` sau xác nhận rõ ràng và đặt `confirmed=true`. |
| `R13_parallel_web_and_tweets` | `wrong_arg_value` | `lookup` + `social_search` | Đã chọn đủ hai tool theo yêu cầu nhưng arguments không khớp kỳ vọng. | Làm rõ trong prompt/tool descriptions cách tách chủ đề và gán query/`topic`/`timeframe` cho từng tool; chạy lại eval để xác minh. |

## B3. Team Eval Cases

`data/eval_group.json` hiện có 3 case (không phải 10: còn thiếu 2 single-turn và 5 multi-turn so với yêu cầu). Repository chưa có run eval cho suite `group`, vì vậy kết quả ghi là chưa đo.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| `group_dedup_single` | Chỉ loại URL trùng trong danh sách được cung cấp; không tìm thêm hoặc format. | `deduplicate_sources` | Chưa có group run để xác định |
| `group_dedup_missing_items` | Hỏi lại khi yêu cầu deduplicate nhưng chưa có danh sách nguồn. | `clarify` | Chưa có group run để xác định |
| `group_dedup_multi` | Dùng danh sách nguồn ở lượt trước và chỉ deduplicate theo yêu cầu mới nhất. | `deduplicate_sources` | Chưa có group run để xác định |

## B4. Live Chat Evidence

Không tìm thấy transcript live trong `transcripts/`; chỉ có transcript mẫu trong `samples/`, không dùng làm bằng chứng chạy thật.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| Chưa có | Chưa có transcript live được commit | N/A | N/A | Chưa thể xác minh |

## B5. Bonus Evidence

**Các tool bonus đều có trong repository**: `send`, `policy`, `papers`, `paper_text` được khai báo trong `artifacts/tools.yaml`, đăng ký trong `tools/__init__.py` và có thư mục implementation tương ứng. Chưa có transcript xác nhận Telegram hoặc run riêng chứng minh các tool bonus đã được thực thi; thiếu run evidence không đồng nghĩa là thiếu tool. Unit tests cho tool mới nằm trong `tests/test_deduplicate_sources.py`; file có các test về URL trùng/chuẩn hóa, URL không hợp lệ, bảo toàn dữ liệu và tích hợp dispatch/format. Chưa có kết quả `pytest` được lưu nên không khẳng định số test pass hoặc bug đã tìm thấy.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `tools/send/`, `artifacts/tools.yaml`; chưa có transcript gửi thật | Tool đã được triển khai/đăng ký; contract có tham số xác nhận `confirmed`. | Không gửi trước xác nhận rõ ràng; tránh coi lời yêu cầu ban đầu là xác nhận. |
| arXiv/company policy | `tools/papers/`, `tools/paper_text/`, `tools/policy/` và declarations trong `artifacts/tools.yaml` | Cả ba tool đã có implementation và đăng ký; chưa có run evidence riêng. | Paper text là nội dung nguồn ngoài; policy chỉ dùng cho câu hỏi về tài liệu nội bộ; kiểm chứng trích dẫn và nội dung trước khi kết luận. |
| UI | `app.py` | Có mã ứng dụng trong repo. | Chưa có URL public hoặc bằng chứng UI chạy/deploy. |
| Tool unit tests (`tests/`) | `tests/test_deduplicate_sources.py` | Bao phủ nhiều trường hợp hợp lệ, lỗi URL, chuẩn hóa và dispatch tool. | Chưa có output pytest đã lưu; không ghi nhận bug cụ thể khi chưa có bằng chứng. |

**Tool unit tests:** Có suite riêng cho `deduplicate_sources`; chưa có output chạy test để xác nhận số test pass hoặc bug phát hiện được. Ví dụ lớp lỗi unit test có thể bắt nhưng eval routing không bắt là URL malformed/URL chứa credentials hoặc việc chuẩn hóa URL làm gộp nhầm hai nguồn khác nhau; đây là phạm vi được test trong unit suite, không phải bug đã xác nhận.

## B6. Reflection

- **Fix thuộc `system_prompt.md`:** thay chỉ dẫn baseline khuyến khích đoán khi thiếu thông tin, gửi ngay và ép một bước. Nêu rõ phạm vi research, thứ tự routing, dùng `clarify` khi thiếu dữ kiện, hỗ trợ nhiều tool khi một yêu cầu cần nhiều nguồn, và xác nhận trước mọi hành động có side effect.
- **Fix thuộc `tools.yaml`:** mô tả cụ thể công dụng, khi nào dùng/không dùng, quy ước arguments (handle, `news`, timeframe, `Top`/`Latest`) và điều kiện `confirmed=true` cho `send`. Tool description tốt giúp model phân biệt tool ở ngay thời điểm chọn tool.
- **Failure cần manual review:** nội dung ngoài phạm vi và ranh giới gửi/publish cần đánh giá ý định, ngữ cảnh và xác nhận thực sự của người dùng; chỉ chấm tool name có thể bỏ sót rủi ro hành động.
- **Cải thiện tiếp theo:** hoàn thiện prompt/tool descriptions, chạy và lưu v1–v3 theo từng giả thuyết, thêm 7 eval case còn thiếu, chạy group eval, lưu ít nhất 3 lượt chat thật, ghi output pytest và bổ sung URL deploy nếu có. Sau đó đối chiếu metric mới với baseline v0.

## B7. Small Local Model Challenge (bonus)

Không có run Ollama/local model hoặc bằng chứng tối ưu local trong repository; phần này chưa thực hiện/không thể báo cáo.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v0 baseline | `openai/gpt-4o-mini` (OpenRouter) | Baseline artifacts | 0.75 | 0.80 | 0.75 | 1.00 | `runs/v0_B_base_openrouter_20261110T102236137498.json` |
| v3-local | Chưa chạy | N/A | N/A | N/A | N/A | N/A | Chưa có |
| v4-local | Chưa chạy | N/A | N/A | N/A | N/A | N/A | Chưa có |
| v5-local | Chưa chạy | N/A | N/A | N/A | N/A | N/A | Chưa có |

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---:|---|---|---|
| wrong / hallucinated tool | Chưa đo | N/A | Chưa có local run | Chưa xác định |
| invalid JSON args (`_invalid_json_arguments`) | Chưa đo | N/A | Chưa có local run | Chưa xác định |
| no tool call / answered directly | Chưa đo | N/A | Chưa có local run | Chưa xác định |
| missed `clarify` | Chưa đo | N/A | Chưa có local run | Chưa xác định |
| repeated / unnecessary calls | Chưa đo | N/A | Chưa có local run | Chưa xác định |

- Chưa có dữ liệu để kết luận thay đổi nào giúp model nhỏ gọi tool đúng hơn.
- Chưa có phép thử kiểm tra prompt tối ưu local trên model cloud.
- Chưa có dữ liệu về trade-off để quyết định khi nào chọn model local thay vì cloud.
