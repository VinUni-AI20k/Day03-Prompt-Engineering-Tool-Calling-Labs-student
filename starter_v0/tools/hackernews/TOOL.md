---
name: hackernews
track: bonus
kind: live_api
provider: algolia_hn
requires_env: []
inputs: [query, sort_by, limit]
outputs: [items]
side_effect: false
---
# hackernews

Searches Hacker News stories via the public Algolia HN Search API (`hn.algolia.com`).
No API key is required. Useful for developer/startup/AI tech discussions on Hacker News.

