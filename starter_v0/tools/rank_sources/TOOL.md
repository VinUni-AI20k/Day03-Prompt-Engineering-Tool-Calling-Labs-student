---
name: rank_sources
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [items, limit]
outputs: [tool, items, item_count, limit]
side_effect: false
---
# rank_sources

Rank already-collected research items by their existing numeric `score`, highest first, and keep at most `limit` items. Use only when the user asks to rank or select top-scoring results. Do not search for sources or invent scores. Items without a score remain after scored items, preserving their original order. This tool runs locally without network access or API keys.

`items` must be a list of objects; `limit` must be a positive integer. Invalid input returns an error dict.
