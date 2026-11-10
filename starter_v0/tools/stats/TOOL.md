---
name: stats
track: core
kind: local_formatter
requires_env: []
inputs: [values, statistic]
outputs: [statistic, count, value]
side_effect: false
---
# stats

Calculate descriptive statistics on numeric data already supplied by the user
or collected during research. This tool does not fetch data or evaluate code.

- `values`: non-empty list of finite numbers; booleans and numeric strings are rejected.
- `statistic`: `mean` (default), `median`, or `stdev` (sample standard deviation,
  using n - 1, requires at least two observations).
- Success: `{tool, statistic, count, value}`.
- Failure: `{tool, error, message}`; exceptions do not escape the tool.

Example: `stats(values=[2, 3, 7], statistic="mean")` returns `value=4`.
