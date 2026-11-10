---
name: hn_search
track: bonus
kind: live_api
provider: Hacker News Algolia API
requires_env: []
inputs: [query, tag, sort_by, limit]
outputs: [items]
side_effect: false
---
# hn_search

Searches Hacker News stories, Ask HN, Show HN, or comments via the public Algolia HN Search API.
Use when the user specifically asks for Hacker News (HN) discussions, points, comments, or developer community threads.

