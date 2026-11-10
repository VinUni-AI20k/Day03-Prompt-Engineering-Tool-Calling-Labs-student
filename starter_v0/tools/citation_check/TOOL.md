---
name: citation_check
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [draft_text, check_type]
outputs: [passed, url_count, violations]
side_effect: false
---
# citation_check

Validates a draft text (`draft_text`) before publishing to check that it
includes source URLs (`citation`) and does not leak sensitive tokens or
personal emails (`privacy`).
