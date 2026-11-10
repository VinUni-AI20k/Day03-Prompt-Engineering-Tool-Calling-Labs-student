---
name: source_audit
track: bonus
kind: local_formatter
provider: local Python
requires_env: []
inputs: [items]
outputs: [checked_count, valid_count, ok, issues]
side_effect: false
---
# source_audit

Checks whether each research item has a non-empty title and an HTTP(S) URL with a host. Use it to check citation metadata before formatting a digest. It does not fetch URLs or verify that their claims are true. Items without a title or valid URL are returned in `issues` with their list index and problem codes.
