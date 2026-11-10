---
name: citation_audit
track: bonus
kind: local_formatter
provider: local Python
requires_env: []
inputs: [items]
outputs: [item_count, issues, passed, scope]
side_effect: false
---
# citation_audit

Audit citation metadata: missing title, source or URL; invalid HTTP(S) URLs; duplicate normalized URLs. Issues use zero-based item indices. No network or API key. Maximum 100 items; invalid collection types return an error dictionary. Empty input passes metadata checks but provides no research evidence. This does not check factual accuracy, source credibility or link reachability.
