---
name: deduplicate_sources
track: core
kind: local_formatter
requires_env: []
inputs: [items]
outputs: [items, input_count, item_count, duplicates_removed]
side_effect: false
---
# deduplicate_sources

Remove duplicate sources from an already-collected list, before formatting a digest.
No network, API key, file write, model call, or confirmation is needed.

## Contract

- Input: `items`, an array of objects with a required absolute HTTP(S) `url`.
  Optional fields such as `title`, `summary`, `source`, and `section` are preserved.
- Output: `items` suitable for `format`, plus input/output counts and duplicates removed.
- Stable order: retain the first occurrence and its original URL and metadata.
- Comparison ignores surrounding URL whitespace, hostname/scheme case, default
  HTTP(S) ports, and `utm_*`, `fbclid`, `gclid`, `dclid`, `msclkid` query parameters.
  An empty root path is equivalent to `/`.
- Preserve path case, non-root trailing slash, HTTP vs HTTPS, other query parameters
  (including their order and blank values), and fragments. Do not assume those
  identify the same resource. Do not merge by title or semantic similarity.
- Empty array is valid. Missing/null/non-array input, non-object items, missing or
  invalid URLs, credentials, and malformed ports return `{tool, error, message}`.
  An invalid item rejects the whole batch; no partial success is returned.
- Input data is not modified.

## Routing

Use when the user explicitly asks to remove duplicate links/sources, or before a
digest when collected results contain duplicates. Pass actual items from tool
results or the user's message. Never invent a list to satisfy required arguments.
If no list is available, collect sources with the appropriate research tool or
ask `clarify`. Do not use this tool to search, read URLs, check facts, or format text.

## Example

```python
from tools import TOOL_FUNCTIONS

result = TOOL_FUNCTIONS["deduplicate_sources"](items=[
    {"title": "First", "url": "https://example.com/news?utm_source=chat"},
    {"title": "Repeated", "url": "https://example.com/news"},
])
assert result["item_count"] == 1
assert result["duplicates_removed"] == 1
digest = TOOL_FUNCTIONS["format"](items=result["items"], template="bullets")
```
