---
name: text_stats
track: bonus
kind: local_formatter
requires_env: []
inputs: [text]
outputs: [chars, words, sentences, reading_minutes]
side_effect: false
---
# text_stats

Counts characters, words and sentences of a text and estimates reading time
(200 words per minute, rounded up). Runs locally, no API key. A non-string
`text` returns an error dict instead of raising.
