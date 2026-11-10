---
name: date_diff
track: bonus
kind: local_formatter
requires_env: []
inputs: [start_date, end_date]
outputs: [days, weeks]
side_effect: false
---
# date_diff

Returns the number of days (signed) and weeks between two ISO dates
(`YYYY-MM-DD`). A negative `days` means `end_date` is before `start_date`.
An empty or badly formatted date returns an error dict instead of raising.
