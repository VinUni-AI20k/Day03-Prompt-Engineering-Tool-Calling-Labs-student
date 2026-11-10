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

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
| ------- | ---------------- | ---------- | ------------: | -----------: | -------- |
| v0      | baseline         |            |               |              |          |
| v1      |                  |            |               |              |          |
| v2      |                  |            |               |              |          |
| v3      |                  |            |               |              |          |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
| ------- | ------------ | ----------------- | ----------- | --- |
|         |              |                   |             |     |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
| ------- | ------------- | ---------------------- | ------ |
|         |               |                        |        |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
| ---- | ------------ | ---------- | ---------------- | ------- |
|      |              |            |                  |         |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus                        | Evidence File     | What Worked | Risk / Guardrail |
| ---------------------------- | ----------------- | ----------- | ---------------- |
| send (Telegram)              |                   |             |                  |
| arXiv/company policy         |                   |             |                  |
| UI                           |                   |             |                  |
| Tool unit tests (`tests/`) | `pytest` output |             |                  |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?

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
