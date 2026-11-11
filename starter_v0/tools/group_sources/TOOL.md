---
name: group_sources
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [items, group_by]
outputs: [tool, group_by, groups, group_count, item_count]
side_effect: false
---
# group_sources

Group already-collected research items by publisher domain, source label, or section. Use when the user requests grouped results or a source-coverage view. Pass the collected items unchanged and set `group_by` to exactly `domain`, `source`, or `section`. Do not search, fetch, or infer missing source metadata. Missing group values go into `Unknown`; group order follows the first occurrence in the input. This tool runs locally without network access or API keys.
