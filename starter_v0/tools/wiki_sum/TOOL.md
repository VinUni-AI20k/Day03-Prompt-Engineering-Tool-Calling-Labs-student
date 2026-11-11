---
name: wiki_sum
track: bonus
kind: live_api
provider: Wikipedia REST API
requires_env: []
inputs: [title]
outputs: [title, summary, url, description]
side_effect: false
---
# wiki_sum

Retrieves Wikipedia's introductory summary for a specific person, concept, or
other knowledge-baseline question. Use for questions such as "Who is X?" or
"What is Y?". Do not use for current news, which belongs to `lookup`, or for
questions about the identity or capabilities of this assistant.
