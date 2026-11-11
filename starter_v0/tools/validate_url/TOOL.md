---
name: validate_url
track: bonus
kind: control
provider: Local URL parser and configured domain list
requires_env: []
inputs: [url]
outputs: [valid, is_shortened, is_blocked, blacklist_configured, domain, reason]
side_effect: false
---
# validate_url

Checks a user-provided URL's format, flags common URL shorteners, and checks
the hostname against the locally configured comma-separated
`URL_BLACKLIST_DOMAINS` list. Use when the user asks whether a specific link is
valid or safe. This tool does not fetch the link or guarantee that a URL is
safe; do not call it before ordinary `fetch` requests.
