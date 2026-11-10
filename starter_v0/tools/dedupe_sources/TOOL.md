---
name: dedupe_sources
track: core
kind: local_formatter
requires_env: []
inputs: [urls]
outputs: [urls, duplicate_count]
side_effect: false
---

# dedupe_sources

Use this tool to remove exact duplicates from a list of known HTTP(S) URLs. It preserves the first occurrence of each URL and returns the number of entries removed. Query strings and fragments remain part of the comparison. Invalid input returns an error dictionary. The tool operates entirely on the supplied strings.
