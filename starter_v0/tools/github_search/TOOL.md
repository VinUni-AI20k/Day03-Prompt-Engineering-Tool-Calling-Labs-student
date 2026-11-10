---
name: github_search
track: bonus
kind: live_api
provider: GitHub REST API
requires_env: []
inputs: [query, language, sort, limit]
outputs: [items, total_count]
side_effect: false
---
# github_search

Searches public GitHub repositories by keyword, with optional programming-language
and sort filters. It uses GitHub's unauthenticated public search endpoint and does
not modify repositories or user data.
