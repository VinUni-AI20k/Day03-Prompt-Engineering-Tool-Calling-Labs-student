---
name: wikipedia
track: bonus
kind: live_api
provider: Wikipedia (MediaWiki Action API)
requires_env: []
inputs: [query, lang]
outputs: [items]
side_effect: false
---
# wikipedia

Looks up background knowledge: searches Wikipedia (`en` or `vi`) and returns the intro
of the best-matching article (title, url, plain-text summary capped at 1500 chars).
Use for "X là gì / ai là ...", definitions and background — not for news.

Robustness: empty query -> error dict; unknown `lang` falls back to `en`;
no match -> empty `items`.
