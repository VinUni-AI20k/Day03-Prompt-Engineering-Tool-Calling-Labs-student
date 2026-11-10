---
name: deduplicate_sources
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [items, strategy, case_sensitive]
outputs: [items, duplicates, input_count, unique_count, duplicate_count]
side_effect: false
---
# deduplicate_sources

Removes repeated research sources by canonical URL, normalized title, or either.
It preserves first-seen order and reports which input entries were removed and why.
