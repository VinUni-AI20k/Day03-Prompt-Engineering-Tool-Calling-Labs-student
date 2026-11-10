---
name: hn_search
track: core
kind: live_api
provider: Hacker News Algolia API
requires_env: []
inputs: [query, sort, limit]
outputs: [items]
side_effect: false
---
# hn_search

Tìm các story trên Hacker News (cộng đồng developer/startup) qua API công khai
`https://hn.algolia.com/api/v1/search`, không cần API key.

- `query`: chủ đề, ví dụ `Rust`, `LLM agents`.
- `sort`: `relevance` (mặc định, bài nổi bật nhất) hoặc `date` (mới nhất).
- `limit`: 1–20, mặc định 5; giá trị sai kiểu được đưa về mặc định, ngoài khoảng bị kẹp lại.

Trả về `items` gồm `title`, `url` (link bài gốc, nếu không có thì link thảo luận HN),
`discussion_url`, `points`, `num_comments`, `published_at`.
Query rỗng hoặc lỗi HTTP/mạng trả về error dict, không raise.

Khi nào agent nên gọi: user hỏi rõ về Hacker News / HN, hoặc dân developer trên HN đang bàn gì về một chủ đề.
Không dùng cho tin tức web chung (`lookup`) hay Twitter (`social_search`).
