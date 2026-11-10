---
name: filter_by_date
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [items, start_date, end_date, date_field, include_undated]
outputs: [items, excluded, input_count, matched_count, excluded_count]
side_effect: false
---
# filter_by_date

Filters research sources to an inclusive ISO date range using a selected date field.
It can retain undated entries and reports why every excluded entry was removed.
