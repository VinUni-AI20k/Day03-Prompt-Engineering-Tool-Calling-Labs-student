---
name: weather
track: bonus
kind: live_api
provider: Tavily
requires_env: [TAVILY_API_KEY]
inputs: [location, timeframe]
outputs: [tool, location, timeframe, summary, items]
side_effect: false
---
# weather

Tra cứu thông tin dự báo thời tiết cho một địa điểm cụ thể sử dụng Tavily Search API.

