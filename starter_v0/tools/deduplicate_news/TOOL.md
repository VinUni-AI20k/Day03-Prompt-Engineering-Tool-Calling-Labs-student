---
name: deduplicate_news
track: bonus
kind: local_formatter
requires_env: []
inputs: [items, title_similarity_threshold]
outputs: [items, item_count, duplicates_removed]
side_effect: false
---

# Deduplicate news

Use this local tool when at least two news items from different sources are
available and the user asks to merge or remove duplicates. Each item should
have a non-empty `title` and may include `url`, `source`, `summary`, and
`section`, matching the items accepted by `format`.

The tool first compares normalized HTTP(S) URLs: host casing, `www.`, default
ports, trailing slashes, fragments, and common tracking parameters do not
distinguish URLs. If URLs do not match, it compares distinct title terms after
case and accent folding. Similarity is the number of shared terms divided by
the larger term count; the default match threshold is `0.8`.

Use it before `format` when preparing a digest from multiple sources. Do not
use it to find new articles or summarize a single article. Invalid input is
returned as an error dictionary; this tool makes no network requests.
