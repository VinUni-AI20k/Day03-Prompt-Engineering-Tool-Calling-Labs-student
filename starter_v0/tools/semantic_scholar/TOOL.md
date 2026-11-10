---
name: semantic_scholar
track: bonus
kind: live_api
provider: Semantic Scholar Academic Graph API
requires_env: []
inputs: [query, max_results, sort_by]
outputs: [items, total_results]
side_effect: false
---

# semantic_scholar

Searches scholarly papers using the official Semantic Scholar Academic Graph API.

- `query`: required plain-text search query.
- `max_results`: number of results, clamped to 1–100 (default: 5).
- `sort_by`: `relevance`, `citationCount`, or `publicationDate` (default: `relevance`).
- Returns normalized paper metadata, including title, abstract, authors, year,
  DOI, citation count, venue, URL, and open-access PDF URL when available.
- Uses `SEMANTIC_SCHOLAR_API_KEY` if configured; the key is optional.
- Retries rate-limit and transient server responses with bounded backoff.
