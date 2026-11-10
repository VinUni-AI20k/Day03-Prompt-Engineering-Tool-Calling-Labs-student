---
name: web_answer
track: bonus
kind: live_api
provider: Tavily
requires_env: [TAVILY_API_KEY]
inputs: [question, max_results]
outputs: [answer, answer_source, confidence, items]
side_effect: false
---
# web_answer

Tool dự phòng (fallback) do nhóm thêm. Dùng khi người dùng hỏi một câu hỏi thông tin
trong phạm vi research nhưng không có tool chuyên biệt nào khớp, ví dụ "GPU H200 khác
H100 thế nào?", "RAG là gì?", "Ai sáng lập Mistral AI?".

Cách hoạt động: gọi Tavily `search` với `topic=general`, `search_depth=advanced`,
`include_answer=advanced` để lấy một câu trả lời đã tổng hợp từ nhiều trang, kèm danh sách
nguồn. Nếu Tavily không trả `answer`, tool ghép 1–2 câu đầu của 3 kết quả tốt nhất kèm tên
nguồn (`answer_source="top_snippets"`, `confidence="low"`).

Agent hiện chỉ chạy một bước (không đưa kết quả tool lại cho model), nên phần "suy luận"
được thực hiện ngay trong tool thay vì nhờ model đọc kết quả rồi trả lời.

Không dùng cho:
- tin tức theo thời gian (`lookup` với `topic=news`, `timeframe`)
- tweet (`timeline`, `social_search`), URL đã cho (`fetch`), bài báo arXiv (`papers`), quy định nội bộ (`policy`)
- câu ngoài phạm vi (toán, code, dịch, sáng tác) và câu hỏi về bản thân agent: trả lời bằng text, không gọi tool
