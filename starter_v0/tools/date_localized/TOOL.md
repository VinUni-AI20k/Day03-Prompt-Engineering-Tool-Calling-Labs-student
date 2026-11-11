---
name: date_localized
track: bonus
kind: control
provider: Python zoneinfo
requires_env: []
inputs: [timezone]
outputs: [location, timezone, datetime, formatted]
side_effect: false
---
# date_localized

Returns the current local date and time for an IANA timezone or a supported
city name (Hanoi, Ho Chi Minh City, London, New York, San Francisco, Singapore,
Tokyo, or UTC). Use only when the user directly asks what time or date it is
somewhere. Do not use for searches containing relative terms such as "today"
or "this week"; those use the search tool's `timeframe` argument.
