---
name: calculator
track: bonus
kind: local_formatter
requires_env: []
inputs: [expression, precision]
outputs: [expression, result, error]
side_effect: false
---
# calculator

Safely evaluates a math expression (+ - * / // % ^, sqrt, abs, round, min, max,
sum, avg, log, log10, pi, e). Uses an AST whitelist, never `eval`. Returns
`{"error": ...}` on bad input or division by zero instead of raising.
