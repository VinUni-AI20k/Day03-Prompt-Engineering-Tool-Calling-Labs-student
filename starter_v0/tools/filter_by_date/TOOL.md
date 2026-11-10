---
name: filter_by_date
track: core
kind: local_formatter
requires_env: []
inputs:
- items
- start_date
- end_date
outputs:
- items
- removed_count
- excluded
side_effect: false
---
# filter_by_date

Keep collected items whose date field is within inclusive start_date/end_date. All dates must be YYYY-MM-DD calendar dates; timestamps must be converted by the caller first. Missing/invalid item dates are excluded with their zero-based index and reason, never guessed. Invalid range or list returns invalid_input. Preserves order and deep-copies output. Does not search or infer publication dates.
