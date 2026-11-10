---
name: hn_search
track: bonus
kind: live_api
provider: Hacker News Algolia API (free, no key)
requires_env: []
inputs: [query, sort_by, timeframe, limit]
outputs: [items]
side_effect: false
---
# hn_search

Searches Hacker News **stories** through the public Algolia HN API
(`https://hn.algolia.com/api/v1`). No API key is needed.

- `query`: keywords, e.g. `"LLM agents"`. Empty → error dict.
- `sort_by`: `relevance` (endpoint `/search`) or `date` (endpoint `/search_by_date`, newest first).
- `timeframe`: `any`, `day`, `week`, `month`, `year` → sent as `numericFilters=created_at_i>…`.
- `limit`: 1–20 (clamped). A numeric string such as `"5"` is accepted.

Each item has `title`, `url` (the linked article, or the HN discussion for Ask/Show HN),
`source`, `summary`, `date`, `discussion_url`, and `metrics` (`points`, `comments`).

**When to use:** the user wants to know what the tech / developer community
(Hacker News) is discussing about a topic, or wants top HN stories about it.

**When not to use:** general web news (`lookup`), tweets (`social_search` / `timeline`),
scientific papers (`papers`), or reading a given URL (`fetch`).

Never raises: invalid input, HTTP errors, and timeouts return
`{"tool": "hn_search", "error": ..., "message": ...}`.
