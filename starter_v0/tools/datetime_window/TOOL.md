---
name: datetime_window
track: core
kind: local
provider: none
requires_env: []
inputs: [timeframe, reference_date, tz]
outputs: [start, end, label, duration_days, timeframe_code]
side_effect: false
requires_confirmation: false
---

# datetime_window

Chuẩn hoá một biểu thức timeframe dạng ngôn ngữ tự nhiên thành `start`/`end` ISO 8601 cùng `timeframe_code` gọn (`"7d"`, `"24h"`) để dùng trong `lookup` hoặc `timeline`.
