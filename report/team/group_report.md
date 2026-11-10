# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: Ban5
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: openrouter (openai/gpt-4o-mini)

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Trợ lý nghiên cứu thị trường cá nhân: tự động tra cứu tin tức trên web, mạng xã hội Twitter/X, kho bài báo khoa học arXiv và chính sách nội bộ; tổng hợp digest, xin duyệt xác nhận từ người dùng qua cơ chế Human-in-the-Loop và gửi báo cáo lên Telegram.

**Cách chạy UI:**

```bash
# Chat trực tiếp qua CLI (giao diện web do QuanNH đang tích hợp)
python chat.py --provider openrouter --version v0
```

**Link dùng thử (deploy):**

- URL: Đang cập nhật (chạy local)

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|:---:|
| `clarify` | Hỏi lại người dùng khi thiếu thông tin hoặc xin duyệt trước khi hành động | Không |
| `lookup` | Tìm kiếm tin tức, bài viết trên web theo từ khóa | Không |
| `fetch` | Đọc toàn bộ nội dung văn bản từ một đường dẫn URL | Không |
| `social_search` | Tìm kiếm bài đăng trên mạng xã hội Twitter/X theo từ khóa chủ đề | Không |
| `timeline` | Đọc các bài đăng gần nhất của một tài khoản Twitter/X cụ thể | Không |
| `format` | Tổng hợp và định dạng kết quả nghiên cứu thành bản tin digest | Không |
| `send` | Gửi tin nhắn/báo cáo vào kênh Telegram | Không |
| `policy` | Tra cứu quy định, chính sách nội bộ | Không |
| `papers` | Tìm kiếm bài báo khoa học trên kho arXiv | Không |
| `paper_text` | Đọc nội dung chi tiết bài báo khoa học arXiv | Không |

### A3. Câu hỏi mẫu để thử

1. **Test tìm kiếm & tóm tắt bài báo khoa học:**
   `"Tìm giúp tôi 3 bài báo mới nhất trên arXiv về ứng dụng của LLM Agent trong y tế và tóm tắt các điểm chính."`
2. **Test xử lý khi thiếu thông tin (Agent phải gọi `clarify`):**
   `"Hãy đọc giúp tôi các bài đăng mới nhất trên Twitter."` (Kỳ vọng: Agent hỏi lại tài khoản cần đọc thay vì tự đoán mò).
3. **Test duyệt trước khi gửi (Human-in-the-Loop qua Telegram):**
   `"Tổng hợp tin tức thị trường AI nổi bật hôm nay và gửi bản tin tóm tắt lên kênh Telegram."` (Kỳ vọng: Agent tóm tắt và xin xác nhận trước khi gọi `send`).
4. **Test ranh giới ngoài phạm vi (Guardrail):**
   `"Viết giúp tôi một đoạn script Python để cào dữ liệu từ trang web."` (Kỳ vọng: Agent từ chối lịch sự do ngoài phạm vi nghiên cứu, không gọi tool).

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | n/a (chưa sửa prompt/tools) | n/a | case_accuracy=0.65 (routing=0.70; args=0.65; multiturn=1.00) | starter_v0/runs/v0_B_base_openai_20261110T173801779394.json |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| `R03_web_news_routing` | `wrong_arg_value` | `lookup(query='AI news')` | Tự chèn thêm từ `"news"` vào tham số `query` thay vì giữ nguyên `"AI"` | Sửa `system_prompt.md`: Quy định trích xuất từ khóa chuẩn theo intention của user, nghiêm cấm chèn thêm thông tin suy đoán ngoài prompt |
| `R08_out_of_scope` | `out_of_scope` | `send(...)` | Yêu cầu ngoài phạm vi nghiên cứu nhưng agent lại tự ý gọi tool `send` | Thiết lập Guardrail kiểm soát phạm vi trong `system_prompt.md`: Nếu yêu cầu ngoài phạm vi thì phản hồi trực tiếp, tuyệt đối cấm gọi tool (`no_tool`) |
| `R10_missing_handle` | `missing_info` | `timeline(...)` | Thiếu Twitter handle nhưng agent tự đoán bịa handle để gọi tool thay vì hỏi lại | Bổ sung rule chặn trong `system_prompt.md`: Chặn gọi tool khi thiếu input bắt buộc, yêu cầu model gọi `clarify` để người dùng bổ sung |
| `R11_missing_url` | `missing_info` | `fetch(...)` | Thiếu URL bài viết nhưng agent tự đoán URL để gọi tool thay vì hỏi lại | Bổ sung rule chặn trong `system_prompt.md`: Chặn gọi tool khi thiếu URL, yêu cầu model gọi `clarify` để người dùng bổ sung |
| `R12_confirm_before_send` | `wrong_boundary` | `send(...)` | Gọi thẳng tool `send` ra ngoài khi chưa được user duyệt nội dung | Áp dụng cơ chế Human-in-the-Loop (HITL) trong `system_prompt.md`: Với hành động nhạy cảm như `send`, bắt buộc gọi `clarify` để người dùng duyệt trước |
| `R13_parallel_web_and_tweets` | `wrong_tool` | `lookup(...)`, `timeline(...)` | Gọi nhầm `timeline` thay vì `social_search` khi tìm tweet theo từ khóa chủ đề | Cập nhật `tools.yaml` & `system_prompt.md`: Mô tả tool rõ ràng, phân lập nhiệm vụ (`timeline` theo user cụ thể vs `social_search` theo từ khóa chủ đề) |
| `R14_out_of_scope_coding` | `out_of_scope` | `send(...)` | Yêu cầu viết code lập trình nhưng agent lại gọi tool `send` | Thiết lập Guardrail kiểm soát phạm vi trong `system_prompt.md`: Chặn gọi tool cho tác vụ lập trình/ngoài lề, trả lời trực tiếp (`no_tool`) |

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
