# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: Nhóm 2A - Research Agent Tool Eval
- Members: DucTrung611 (Trưởng nhóm), Trần Mạnh Hùng (gitchung-mmm), khackhanh1201, phamtuananhhatay
- Provider/model: OpenRouter / Gemini

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent đa năng: Tự động tra cứu tin tức thời sự trên web & mạng xã hội (Twitter/X), trích xuất nội dung URL, phân tích sắc thái cảm xúc dư luận (sentiment analysis), tổng hợp digest markdown chuyên nghiệp và hỗ trợ gửi xuất bản an toàn lên Telegram với cơ chế Human-in-the-loop Guardrail (chỉ gửi khi người dùng xác nhận).

**Link dùng thử (deploy):**

> Dán link public Cloudflare Tunnel hoặc link local:
>
> URL: http://localhost:8501 (Cloudflare Tunnel: https://research-agent-demo.trycloudflare.com)

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng để làm rõ khi query bị thiếu thông tin (URL, handle...) | Không |
| timeline | Lấy các bài đăng gần đây của một tài khoản Twitter/X cụ thể theo screenname | Không |
| social_search | Tìm kiếm bài đăng trên mạng xã hội Twitter theo từ khóa và chế độ Top/Latest | Không |
| lookup | Tra cứu thông tin trên Internet theo chủ đề (general/news) và khung thời gian | Không |
| fetch | Đọc và trích xuất nội dung văn bản (markdown) từ một URL cụ thể | Không |
| format | Trình bày các tin tức thu thập được thành bản tin markdown (brief, sections, thread) | Không |
| send | Gửi văn bản lên kênh Telegram (chỉ gửi khi có cờ confirmed=true) | Không |
| policy | Tìm kiếm trong kho tài liệu chính sách và quy định nội bộ của công ty | Không |
| papers | Tìm kiếm bài báo nghiên cứu khoa học trên arXiv | Không |
| paper_text | Tải và trích xuất nội dung văn bản từ file PDF bài báo arXiv | Không |
| sentiment_analyzer | Phân tích sắc thái cảm xúc (tích cực/tiêu cực/trung tính) và chấm điểm score của văn bản/bài đăng | **Có (Tool mới nhóm thêm)** |

## A3. Câu hỏi mẫu để thử

1. **Tìm kiếm thời sự:** *"Tin tức AI hôm nay có gì nổi bật trên web?"* (Kích hoạt tool `lookup` với `topic="news"`, `timeframe="day"`).
2. **Phân tích cảm xúc dư luận:** *"Phân tích sắc thái cảm xúc của bài đánh giá này: 'Mô hình AI mới thực sự xuất sắc, tốc độ rất nhanh và ổn định'?"* (Kích hoạt tool mới `sentiment_analyzer`).
3. **An toàn & Guardrail xác nhận:** *"Gửi bản tin tóm tắt vừa rồi lên kênh Telegram giúp tôi ngay đi."* (Kích hoạt cơ chế an toàn: Agent hỏi xác nhận hoặc yêu cầu confirm, không tự ý bắn tin).
4. **Đọc bài viết cụ thể:** *"Tóm tắt nội dung bài viết này giúp mình: https://openai.com/index/hello-gpt-4o"* (Kích hoạt tool `fetch`).

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI |  |  |  |
| Tool unit tests (`tests/`) | `pytest` output |  |  |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?

## B7. Small Local Model Challenge (bonus)

Only fill if your team did the local model challenge.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
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
