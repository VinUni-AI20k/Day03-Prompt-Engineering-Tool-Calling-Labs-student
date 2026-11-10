---
name: dedupe
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [items, by]
outputs: [items, item_count, removed]
side_effect: false
---
# dedupe

Removes duplicate items from an already-collected list (for example results merged from
`lookup` and `social_search`) before formatting. It does not fetch data.

- `by="url"` (default): URLs are normalised (host case, `www.`, trailing slash, `utm_*` params, fragment ignored).
- `by="title"`: titles are compared case-insensitively, ignoring accents and extra whitespace.
- The first occurrence is kept. Items missing the compared field are always kept.
- Invalid `by` or a non-list `items` returns an error dict instead of raising.
