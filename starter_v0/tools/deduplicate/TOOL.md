---
name: deduplicate
track: bonus
kind: local_formatter
provider: local Python
requires_env: []
inputs: [items]
outputs: [items, input_count, removed_count]
side_effect: false
---
# deduplicate

Remove duplicate source URLs, preserving the first item and input order. Normalization removes fragments, utm_* / fbclid / gclid parameters and sorts remaining query parameters. HTTP and HTTPS, paths and meaningful query values stay distinct. No network, no API key, no input mutation. Invalid items return an error dictionary. Maximum 100 items. This does not detect equivalent claims or article text.
