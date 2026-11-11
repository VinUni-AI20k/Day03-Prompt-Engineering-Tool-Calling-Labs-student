---
name: validate_citations
track: core
kind: local_formatter
requires_env: []
inputs:
- items
outputs:
- valid
- item_count
- errors
side_effect: false
---
# validate_citations

Check collected citations for nonempty title/source strings and an absolute HTTP(S) URL with a valid port. Returns valid and errors with zero-based item index and issues. Empty list is valid (nothing to check). Non-list input returns invalid_input. Does not fetch URLs, verify reachability, assess credibility, or establish that a source supports a claim. Never edits input.
