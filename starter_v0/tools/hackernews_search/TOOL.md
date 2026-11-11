---
name: hackernews_search
track: core
kind: live_api
provider: Hacker News Algolia Search API
requires_env: []
inputs: [query, tags, sort, date_from, date_to, limit]
outputs: [items]
side_effect: false
---
# hackernews_search

Searches Hacker News stories through the public Algolia API
(`https://hn.algolia.com/api/v1/search`). No API key is needed.

- `tags`: `story` (default), `show_hn`, `ask_hn`, `front_page`, `comment`.
  With `front_page`, `query` may be empty.
- `sort`: `relevance` → `/search`, `date` → `/search_by_date` (newest first).
- `date_from` / `date_to`: `YYYY-MM-DD` (UTC), sent as `numericFilters=created_at_i>=…`.
- `limit`: clamped to 1–20.

Each item: `title, url, source, hn_url, points, author, num_comments, created_at, summary`.
Stories without an external link (Ask HN) use the HN discussion URL as `url`.

Errors (bad date, empty query, HTTP error) come back as `{"tool", "error", "message"}`
instead of raising.
