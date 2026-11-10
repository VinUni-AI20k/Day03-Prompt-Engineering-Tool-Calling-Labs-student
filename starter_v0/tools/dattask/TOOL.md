        "today" | "yesterday"
        "this week" | "last week"
        "this month" | "last month"

- name: reference_date
  type: string
  required: false
  description: >
  ISO 8601 datetime string to use as the anchor "now".
  Defaults to current system time if omitted.
- name: tz
  type: string
  required: false
  description: >
  IANA timezone name (e.g. "Asia/Ho_Chi_Minh", "America/New_York").
  Defaults to "UTC".
  returns:
  success:
  start: ISO datetime string — start of the window
  end: ISO datetime string — end of the window (usually now)
  label: human-readable label echoing the input
  duration_days: float — length of window in days
  timeframe_code: compact code like "7d" or "24h" ready for lookup/timeline
  error:
  error: string describing why the timeframe could not be parsed
  when_to_use: >
  Call datetime_window BEFORE lookup or timeline whenever the user's
  request contains a vague or relative time expression:
- "tuần trước", "3 ngày gần đây", "hôm qua", "tháng này"
- "last week", "past 3 hours", "yesterday"
  Use the returned `start`, `end`, and `timeframe_code` as arguments
  to lookup (timeframe=) or timeline (timeframe=).
  when_not_to_use: >
- When the user already provides explicit ISO dates or a numeric
  timeframe code like "7d" — pass that directly to lookup/timeline.
- For timezone conversion unrelated to tool arguments.
- When no time constraint is mentioned at all.
  examples:
- input: {timeframe: "last 7 days"}
  output: {start: "2026-11-03T17:00:00+00:00", end: "2026-11-10T17:00:00+00:00", label: "last 7 days", duration_days: 7.0, timeframe_code: "7d"}
- input: {timeframe: "yesterday", tz: "Asia/Ho_Chi_Minh"}
  output: {start: "2026-11-09T00:00:00+07:00", end: "2026-11-10T00:00:00+07:00", label: "yesterday", duration_days: 1.0, timeframe_code: "1d"}
- input: {timeframe: "gibberish xyz"}
  output: {error: "Không thể parse timeframe: 'gibberish xyz'. Thử dùng: ..."}

---

# datetime_window

Chuẩn hoá một biểu thức timeframe dạng ngôn ngữ tự nhiên thành
start/end datetime ISO 8601 có cấu trúc, kèm `timeframe_code` dạng gọn
(`"7d"`, `"24h"`) để truyền thẳng vào `lookup` hoặc `timeline`.

## Tại sao cần tool này?

`lookup` và `timeline` nhận `timeframe` dạng code gọn (`"7d"`, `"24h"`),
nhưng user thường nói `"tuần trước"`, `"3 ngày gần đây"` hoặc `"hôm qua"`.
Tool này làm cầu nối, tính toán khoảng thời gian chính xác và trả về
cả `start`/`end` ISO (cho báo cáo) lẫn `timeframe_code` (cho tool call tiếp theo).

## Luồng sử dụng điển hình

```
user: "tìm tin tức AI trong tuần trước"
 → datetime_window(timeframe="last week", tz="Asia/Ho_Chi_Minh")
 → {start: "...", end: "...", timeframe_code: "7d", ...}
 → lookup(query="AI news", topic="news", timeframe="7d")
```

## Lỗi & xử lý

Tool **không raise exception**. Khi không parse được, trả về:

```json
{ "error": "Không thể parse timeframe: ..." }
```

Agent nên gọi `clarify` để hỏi lại user khi nhận được `error`.
