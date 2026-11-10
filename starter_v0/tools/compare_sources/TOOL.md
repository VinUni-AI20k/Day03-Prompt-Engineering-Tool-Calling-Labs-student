---
name: compare_sources
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [sources, fields]
outputs: [comparisons, field_analysis, source_count, fields]
side_effect: false
---
# compare_sources

Creates a side-by-side comparison of two or more sources using selected metadata
fields. It reports completeness and exact agreement without inventing judgments.
