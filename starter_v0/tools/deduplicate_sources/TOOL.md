---
name: deduplicate_sources
track: bonus
kind: local_formatter
requires_env: []
inputs: [items]
outputs: [items, removed_count]
side_effect: false
---

# deduplicate_sources

Removes duplicate items based on their URL.

The first item with a URL is kept and the original order is preserved.
Items without a URL are kept unchanged and are not deduplicated.