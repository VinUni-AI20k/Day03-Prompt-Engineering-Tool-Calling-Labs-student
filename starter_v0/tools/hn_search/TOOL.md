---
name: hn_search
track: core
kind: live_api
provider: Hacker News Algolia API
requires_env: []
inputs: [query, sort_by, timeframe, limit]
outputs: [items]
side_effect: false
---
# hn_search

Tìm story trên Hacker News qua https://hn.algolia.com/api (không cần key).
Dùng để xem cộng đồng dev/tech thảo luận gì về một chủ đề.
Trả về `items[{title, url, discussion_url, source, date, summary, metrics}]`,
cùng shape với các tool đọc khác nên `format` dùng lại được.
Mọi lỗi (query rỗng, HTTP lỗi, timeout) trả error dict, không raise.
