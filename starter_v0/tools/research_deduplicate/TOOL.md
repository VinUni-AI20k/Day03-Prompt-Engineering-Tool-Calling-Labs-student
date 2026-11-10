---
name: research_deduplicate
track: core
kind: local_formatter
requires_env: []
inputs: [items]
outputs: [items, original_count, unique_count, removed_count]
side_effect: false
---

# research_deduplicate

Removes duplicate research results based on normalized URLs.

- Keeps the first occurrence of each URL.
- Preserves items without URLs.
- Does not modify the input list.
- Returns an error dictionary for invalid input.
