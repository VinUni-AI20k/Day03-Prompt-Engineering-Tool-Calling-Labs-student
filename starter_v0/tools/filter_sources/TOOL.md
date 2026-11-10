---
name: filter_sources
track: core
kind: local_formatter
requires_env: []
inputs:
- items
- allowed_domains
- blocked_domains
outputs:
- items
- removed_count
side_effect: false
---
# filter_sources

Filter collected items by bare domain names, matching exact hosts and subdomains (case insensitive). Empty allow list allows all; blocked domains take precedence. Invalid URLs or filters return invalid_input with no partial results. Preserves order and deep-copies output. No search, network access, or source credibility verification.
