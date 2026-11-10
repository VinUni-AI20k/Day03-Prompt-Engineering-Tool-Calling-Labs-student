---
name: dedupe
track: bonus
kind: local_formatter
requires_env: []
inputs: [items, key]
outputs: [items, item_count, removed_count]
side_effect: false
---
# dedupe

Removes duplicate items from a list collected by other tools (for example
`lookup` + `social_search`) before `format`. `key` is `url` (default) or
`title`. URLs are compared ignoring case of the host, a leading `www.`, and a
trailing slash. The first occurrence is kept. Items without the key are kept.
An unknown `key` returns an error dict instead of raising.
