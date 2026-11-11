---
name: filter_sources
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [items, domains, min_score]
outputs: [tool, items, item_count, domains, min_score]
side_effect: false
---
# filter_sources

Filter already-collected research items by publisher domains and/or a minimum existing relevance score. Use only when the user asks to restrict results; do not search, fetch pages, or invent scores. Domain matching is case-insensitive and ignores a leading `www.`. Matching items keep their original order and fields. This tool runs locally without network access or API keys.

`items` must be a list of objects. `domains` is an optional list of hostnames (for example, `example.com`); `min_score` is an optional finite number. Invalid input returns an error dict.
