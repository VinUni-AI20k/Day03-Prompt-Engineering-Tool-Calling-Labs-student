# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: OpenRouter · `openai/gpt-4o-mini` (mặc định của provider)

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

**Research agent cho tin AI/công nghệ:** tìm tin trên web (có lọc tin tức theo ngày/tuần/tháng), xem bài đăng của một tài khoản X hoặc tìm bài theo từ khóa, đọc và tóm tắt một URL, tìm và đọc paper arXiv, tra policy nội bộ công ty, gom kết quả thành digest markdown và **chỉ gửi lên Telegram sau khi người dùng xác nhận**. Khi thiếu thông tin (không rõ tài khoản nào, link nào), agent hỏi lại thay vì tự đoán.

**Cách chạy UI:**

```bash
cd starter_v0
pip install -r requirements.txt      # đã thêm streamlit
streamlit run app.py                 # http://localhost:8501
cloudflared tunnel --url http://localhost:8501   # lấy link public
```

UI (`starter_v0/app.py`) dùng chung vòng lặp tool với `chat.py`, hiện đầy đủ tool call, kết quả và lỗi tool cho từng lượt, đồng thời ghi transcript vào `starter_v0/transcripts/*_ui_*.transcript.json`.

**Link dùng thử (deploy):**

> URL: `https://<điền-link>.trycloudflare.com` _(link tạm thời, chỉ sống khi lệnh `cloudflared` còn chạy)_

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin (tài khoản, URL) hoặc xin xác nhận yes/no trước khi gửi | không |
| timeline | Lấy các bài đăng gần đây của **một tài khoản X** (handle không có `@`, vd `sama`, `karpathy`) | không |
| social_search | Tìm bài đăng X theo **từ khóa**, sắp xếp `Latest` (mới nhất) hoặc `Top` (nổi bật) | không |
| lookup | Tìm trên web qua Tavily; `topic=news` cho tin tức, `timeframe` = day/week/month/year | không |
| fetch | Đọc nội dung một URL cụ thể (Firecrawl) để tóm tắt | không |
| format | Trình bày các kết quả đã thu thập thành digest markdown (brief/sections/bullets/thread) | không |
| send | Gửi văn bản lên Telegram channel riêng của nhóm, **chỉ khi `confirmed=true`** | không |
| policy | Tra cứu company policy nội bộ (nguồn, trích dẫn, bảo mật dữ liệu, xuất bản) | không |
| papers | Tìm paper trên arXiv | không |
| paper_text | Tải PDF arXiv và trích text vài trang đầu | không |
| _&lt;tool mới&gt;_ | _&lt;Thành viên 2 điền: làm gì, khi nào agent gọi&gt;_ | **có** |

### A3. Câu hỏi mẫu để thử

1. `Tin tức AI hôm nay có gì nổi bật?` → `lookup(topic=news, timeframe=day)`
2. `Lấy 5 tweet mới nhất của Andrej Karpathy` → `timeline(screenname=karpathy, limit=5)`
3. `Tóm tắt bài này giúp mình` → agent **hỏi lại** link nào; trả lời bằng một URL → `fetch`
4. `Tìm paper arXiv mới về AI agent evaluation` → `papers`
5. `Đăng bản tin này lên Telegram giúp mình` → agent **xin xác nhận** trước, không gửi ngay
6. _&lt;câu hỏi dùng tool mới của nhóm&gt;_

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

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

> Cột Result sinh tự động sau khi chạy `--suite group`: `python scripts/report_tables.py --only B3` (chạy trong `starter_v0/`).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_timeline_name_to_handle_limit (single) | Map "Yann LeCun" → handle `ylecun`, giữ `limit=3`; "trên X" → timeline | `timeline(screenname=ylecun, limit=3)` |  |
| G02_news_timeframe_month (single) | "tin tức … tháng này" → `topic=news`, `timeframe=month` | `lookup(topic=news, timeframe=month)` |  |
| G03_smalltalk_no_tool (single) | Câu cảm ơn/kết thúc không cần tool | no tool (answer) |  |
| G04_out_of_scope_booking (single) | Đặt vé máy bay là ngoài phạm vi research | no tool (refuse) |  |
| G05_route_new_tool (single) | Route tới tool mới của nhóm _(đang tạm dùng `papers`, thay khi tool mới được merge)_ | `papers(max_results=3, sort_by=submittedDate)` |  |
| G06_clarify_then_handle (multi) | Lượt 1 thiếu tài khoản, lượt 2 bổ sung "Demis Hassabis" | `timeline(screenname=demishassabis)` |  |
| G07_send_needs_confirmation (multi) | "Gửi luôn" khi chưa duyệt nội dung → vẫn phải xác nhận | `clarify(response_type=yes_no)` |  |
| G08_send_after_explicit_confirm (multi) | User đã xác nhận rõ → gửi, không hỏi lại vô hạn | `send(confirmed=true)` |  |
| G09_switch_social_to_papers (multi) | Đổi nguồn từ Twitter sang arXiv ở lượt sau | `papers` |  |
| G10_carryover_change_timeframe (multi) | Giữ `topic=news`, đổi `timeframe` week → month | `lookup(topic=news, timeframe=month)` |  |

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
