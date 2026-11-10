---
name: hackernews
track: bonus
kind: live_api
provider: Hacker News (Algolia HN Search API)
requires_env: []
inputs: [query, sort, limit]
outputs: [items]
side_effect: false
---
# hackernews

Searches Hacker News stories through `https://hn.algolia.com/api/v1` (public, no key).
`sort=relevance` uses `/search`, `sort=date` uses `/search_by_date`. Each item has the
story link, a `discussion_url` on news.ycombinator.com, points and comment count.

Robustness: empty query -> error dict; `limit` is coerced to an int in [1, 20];
unknown `sort` falls back to `relevance`.
