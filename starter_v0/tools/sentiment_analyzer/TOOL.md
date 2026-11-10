---
name: sentiment_analyzer
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [text]
outputs: [sentiment, score, summary]
side_effect: false
---

# sentiment_analyzer

Tool phân tích sắc thái cảm xúc (positive / negative / neutral) và cho ra điểm số phân cực từ một đoạn văn bản hoặc bài đăng.
Hoạt động hoàn toàn offline, tính toán an toàn và trả về dictionary.

