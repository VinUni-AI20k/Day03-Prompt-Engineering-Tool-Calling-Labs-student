---
name: github_search
track: core
kind: live_api
provider: GitHub REST API (search/repositories)
requires_env: []
inputs: [query, sort, order, language, created_after, limit]
outputs: [items, total_count]
side_effect: false
---
# github_search

Searches GitHub repositories via `GET https://api.github.com/search/repositories`.

- `GITHUB_TOKEN` is optional but recommended: without it GitHub allows ~10 search
  requests/min, with it ~30. The token only needs public read access.
- `query` is the free-text keyword. `language` and `created_after` (YYYY-MM-DD) are
  appended as GitHub qualifiers: `language:python`, `created:>=2026-01-01`.
- `sort`: `stars` (default), `forks`, `updated`, `best_match` (no sort param sent).
  `order`: `desc` (default) or `asc`. Invalid values fall back to the defaults.
- `limit`: clamped to 1–20.

Each item: `title` (owner/repo), `url`, `source`, `description`, `stars`, `forks`,
`language`, `topics`, `created_at`, `updated_at`, `summary`.

Only repository search is supported (not code/issues/users search).
Errors come back as `{"tool", "error", "message"}` instead of raising.
