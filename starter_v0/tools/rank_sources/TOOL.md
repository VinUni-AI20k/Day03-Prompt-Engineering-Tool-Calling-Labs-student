---
name: rank_sources
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [items, query, limit]
outputs: [items, ranked_count]
side_effect: false
---

# rank_sources

Xếp hạng các nguồn đã thu thập theo số từ khóa của `query` xuất hiện trong
`title` và `summary`. Hai nguồn bằng điểm giữ nguyên thứ tự ban đầu.
Chỉ trả tối đa `limit` nguồn.

Đây là heuristic khớp từ khóa, không xác minh sự thật hoặc đánh giá độ tin cậy
của nguồn. Tool chạy cục bộ và không cần API key.