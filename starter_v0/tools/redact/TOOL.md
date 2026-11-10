---
name: redact
track: core
kind: control
requires_env: []
inputs: [text, extra_patterns]
outputs: [redacted_text, findings, redaction_count]
side_effect: false
---
# redact

Masks sensitive data (email, phone number, API key, bearer token, password,
credentials in URL) out of a block of text.

Use it when the user pastes text that contains personal data or secrets and
the content may be sent to another tool (web search, URL fetch, social
search) or posted to a channel. Call it BEFORE handing the text to any live
tool.

Do not use it to summarize, to search, or to render a digest.

Trust boundary: the result reports only the *type* and *count* of each
redaction, never the raw secret value, so the output is safe to log.
