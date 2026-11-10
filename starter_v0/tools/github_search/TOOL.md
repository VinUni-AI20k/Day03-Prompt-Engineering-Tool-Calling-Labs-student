---
name: github_search
track: bonus
kind: live_api
provider: GitHub REST API
requires_env: []
inputs: [query, language, sort, max_results]
outputs: [items]
side_effect: false
---
# github_search

Searches public GitHub repositories by keyword, optional programming language,
and sort order (`stars`, `updated`, or `help-wanted-issues`).
