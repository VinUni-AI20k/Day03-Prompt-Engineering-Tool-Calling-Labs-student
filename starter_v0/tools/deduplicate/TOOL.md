---
name: deduplicate
track: core
kind: local_formatter
requires_env: []
inputs: [items]
outputs: [items, removed_count]
side_effect: false
---
# deduplicate

Remove duplicate URLs from already-collected research items before formatting.
Does not search, fetch URLs, or detect similar article content.

Input: a list of objects, each with a nonempty absolute HTTP(S) `url`.
Other fields are preserved. An empty list is valid.

URLs are compared after removing the fragment (`#section`) only. Query
parameters, paths, trailing slashes and their order are preserved. The first
item wins, including its original URL and metadata; input order is preserved.
The returned items are independent copies and the input is never changed.

Success: `{tool: "deduplicate", items: [...], removed_count: N}`.
Invalid/missing input, malformed URL or invalid port returns
`{tool: "deduplicate", error: "invalid_input", message: "..."}` with no partial
results. No API key, network request or confirmation is needed.
