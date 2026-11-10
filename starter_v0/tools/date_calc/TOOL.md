---
name: date_calc
track: core
kind: local_formatter
inputs: [op, date1, date2, days]
outputs: [result, error]
side_effect: false
requires_confirmation: false
---

# Date Calculator

Calculates dates using Python's datetime library.

## When to use

- Calculate the number of days between two dates.
- Calculate a date after or before a given number of days.
- Find the weekday of a specific date.
- Get today's date.

## When not to use

- Explain holidays, cultural events, or historical significance.
- Answer general questions about calendars.
- Estimate dates when required input is missing.

## Operations

- today: no date arguments required.
- diff_days: requires date1 and date2.
- add_days: requires date1 and integer days.
- weekday: requires date1.

Dates must use YYYY-MM-DD format.

Invalid inputs return {"error": "..."} instead of raising exceptions.
