---
name: extract_keywords
track: extension
kind: local
provider: none
requires_env: []
inputs: [text, max_keywords]
outputs: [keywords]
side_effect: false
---
# extract_keywords

Extracts ranked repeated keywords from text already supplied by the user or another tool.
Use it to prepare a compact research query or summarize the topic of a long passage.
It does not search the web, fetch a URL, or replace a factual summary.
