---
name: github_repos
track: bonus
kind: live_api
provider: GitHub Search API
requires_env: []
inputs: [query, sort_by, timeframe, min_stars, language, limit]
outputs: [items]
side_effect: false
---
# github_repos

Searches public GitHub repositories via `https://api.github.com/search/repositories`.
Supports sorting by `stars`, `hot` (recent created + stars velocity), `updated`, or `forks`,
plus filtering by `timeframe` (`all`, `day`, `week`, `month`, `year`), `min_stars`, and `language`.
Optional `GITHUB_TOKEN` env var increases GitHub API rate limits when present.

