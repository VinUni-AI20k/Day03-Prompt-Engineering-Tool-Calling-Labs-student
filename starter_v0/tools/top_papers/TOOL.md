---
name: top_papers
track: core
kind: live_api
provider: OpenAlex API, Semantic Scholar API
requires_env: []
inputs: [query, months, venue_type, limit, sort_by, source]
outputs: [items, total_matches, from_date, to_date]
side_effect: false
---
# top_papers

Returns top papers (default 10) published in **journals or conferences** within the
last N months (default 9), optionally filtered by a topic keyword.

## Parameters

| Param | Values | Default |
|---|---|---|
| `query` | topic keyword (English works best), may be empty | `""` |
| `months` | 1–24 (look-back window from today) | `9` |
| `limit` | 1–25 papers | `10` |
| `venue_type` | `all` \| `journal` \| `conference` | `all` |
| `sort_by` | `citations` (most cited) \| `relevance` (needs query) \| `newest` | `citations` |
| `source` | `openalex` \| `semantic_scholar` | `openalex` |

## Data sources

- **OpenAlex** `/works` — free, no key. Optional `OPENALEX_API_KEY` raises the daily budget.
  Filters `from_publication_date`, `to_publication_date`, `primary_location.source.type`;
  sort `cited_by_count:desc` / `relevance_score:desc` / `publication_date:desc`.
- **Semantic Scholar** — free, but the keyless pool is shared and often returns HTTP 429.
  Set `SEMANTIC_SCHOLAR_API_KEY` (sent as `x-api-key`) for reliable use.
  `citations`/`newest` use `/paper/search/bulk` with `sort=citationCount:desc|publicationDate:desc`;
  `relevance` uses `/paper/search` (relevance-ranked, no sort param).
  Filters `publicationDateOrYear=<from>:<to>` and `publicationTypes=JournalArticle,Conference`.

## Input handling (model may send bad values)

- `months`, `limit` clamped to their ranges; non-numeric → default.
- `venue_type`, `sort_by`, `source` outside their enum → default.
- `sort_by=relevance` with empty `query` → falls back to `citations` (noted in `note`).

Errors (HTTP error, timeout, bad JSON) return `{"tool", "error", "message"}`; the tool never raises.

Difference from `papers`: `papers` searches arXiv **preprints**; `top_papers` ranks
**published** journal/conference papers.
