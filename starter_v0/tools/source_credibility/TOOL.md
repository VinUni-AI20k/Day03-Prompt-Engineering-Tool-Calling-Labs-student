---
name: source_credibility
track: core
kind: local_knowledge
requires_env: []
inputs: [url, min_tier]
outputs: [tool, url, domain, tier, score, min_tier, meets_min_tier, is_reliable, recommendation]
side_effect: false
---
# source_credibility

Đánh giá độ uy tín, phân cấp nguồn tin (source authority tier) và tính đáng tin cậy của một URL hoặc tên miền web.

### Mục đích
- Phân loại nguồn tin thành các bậc: `academic` (khoa học/học thuật), `verified_news` (báo chí chính thống), `tech_media` (kênh công nghệ/lab chính thức), `community` (mạng xã hội/diễn đàn), hoặc `unverified` (chưa xác minh).
- Cung cấp chỉ số tin cậy (reliability score: 0.0 - 1.0) và khuyến nghị xử lý để hỗ trợ research agent thẩm định nguồn thông tin trước khi tổng hợp tin tức hay đưa vào bản tin chính thức.

### Đầu vào
- `url`: Địa chỉ URL hoặc tên miền cần kiểm tra (bắt buộc).
- `min_tier`: Bậc tin cậy tối thiểu mong muốn (`all`, `academic`, `verified_news`, `tech_media`, `community`). Mặc định: `all`.

### Đầu ra
- `tool`: Tên tool (`source_credibility`).
- `domain`: Tên miền được trích xuất (ví dụ: `arxiv.org`, `reuters.com`).
- `tier`: Bậc phân loại nguồn tin.
- `score`: Điểm số tin cậy từ 0.0 đến 1.0.
- `meets_min_tier`: Liệu nguồn tin có đạt ngưỡng min_tier yêu cầu không.
- `is_reliable`: Đánh giá boolean xem nguồn có đủ tiêu chuẩn sử dụng trực tiếp không.
- `recommendation`: Khuyến nghị cách trích dẫn và xử lý thông tin từ nguồn này.
