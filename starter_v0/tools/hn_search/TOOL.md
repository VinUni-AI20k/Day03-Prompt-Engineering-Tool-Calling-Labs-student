---
name: hn_search
track: bonus
kind: live_api
provider: Hacker News Algolia API
requires_env: []
inputs: [query, sort, timeframe, limit]
outputs: [query, sort, timeframe, results]
side_effect: false
---
# hn_search

Tìm kiếm các bài thảo luận trên Hacker News qua Algolia API (`https://hn.algolia.com/api/v1/search`).
Không cần API key.