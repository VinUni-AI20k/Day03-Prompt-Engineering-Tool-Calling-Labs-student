---
name: dedupe_sources
track: core
kind: local_formatter
requires_env: []
inputs: [items]
outputs: [tool, items, duplicate_count]
side_effect: false
---
# dedupe_sources

Use only when the user asks to merge or remove duplicate sources from research
results already available, for example before formatting a digest. Do not use
this tool to search for new sources, fetch pages, or deduplicate without a user
request. It runs locally without network access, API keys or file writes.

## Input

`items` is a required list of objects. Every object must have a non-empty `url`
containing an absolute HTTP or HTTPS URL with a valid hostname and port, if
present. Other fields (title, summary, source, custom metadata, etc.) are kept
unchanged. An empty list is valid; omitted `items` or `None` is an error.

## Matching and output

For comparison only, lowercase the URL scheme and host, remove the fragment,
and remove all `utm_*` query parameters plus `fbclid`, `gclid`, `dclid`,
`msclkid`, `mc_cid` and `mc_eid`. Tracking keys are matched case-insensitively,
including percent-encoded keys. Other query fields retain their exact values,
order, repetitions, blank values and encoding. In particular, `id`, `q`,
`page`, `source` and `ref` are meaningful and stay in the comparison key.
Different schemes, paths, trailing slashes and explicit ports remain distinct.
There is no redirect resolution or content-based matching.

Keep the first item for each comparison key in its original position. The
original URL and all other fields of that item remain unchanged; inputs are
never modified. Success returns:

```json
{"tool": "dedupe_sources", "items": [{"url": "https://example.com/paper?id=7&utm_source=news#intro"}], "duplicate_count": 1}
```

For example, the success above results from the args:

```json
{"items": [{"url": "https://example.com/paper?id=7&utm_source=news#intro"}, {"url": "https://example.com/paper?id=7&utm_medium=email#summary"}]}
```

Invalid input (including a non-object item, missing URL, unsupported scheme,
malformed hostname/port, whitespace/control characters or invalid percent
escapes) returns an error dict instead of raising:

```json
{"tool": "dedupe_sources", "error": "ValueError", "message": "items[0].url is invalid: url must be a non-empty absolute HTTP(S) URL"}
```

The error type is `TypeError` for a wrong list/item type and `ValueError` for a
missing or invalid URL. Any invalid item fails the whole call, with no partial
`items` or `duplicate_count` in the result. List indexes in errors are zero-based.
