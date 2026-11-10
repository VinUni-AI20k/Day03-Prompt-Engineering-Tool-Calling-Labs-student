---
name: openalex
track: bonus
kind: live_api
provider: OpenAlex API
requires_env: []
inputs: [query, max_results, sort_by]
outputs: [items, total_results]
side_effect: false
---

# openalex

Searches scholarly works using the official OpenAlex Works API.

- `query`: required text search query.
- `max_results`: number of results, clamped to 1–100 (default: 5).
- `sort_by`: `relevance`, `publication_date`, or `cited_by_count`
  (default: `relevance`).
- Returns normalized metadata, including title, reconstructed abstract, authors,
  publication date, venue, DOI, citation count, and open-access links.
- `OPENALEX_API_KEY` is optional. `OPENALEX_MAILTO` is also optional and can
  identify the client in API requests.
- No write operations are performed.
