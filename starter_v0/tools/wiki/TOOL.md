---
name: wiki
track: bonus
kind: live_api
provider: Wikipedia REST API
requires_env: []
inputs: [title, lang]
outputs: [title, found, is_disambiguation, description, summary, url]
side_effect: false
---
# wiki

Lấy tóm tắt (đoạn mở đầu) của một bài Wikipedia theo tên bài, qua
`https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}`. Không cần API key.

Dùng cho câu hỏi định nghĩa / kiến thức nền ổn định ("X là gì", "giới thiệu về Y").
Không dùng cho tin tức mới (dùng `lookup` với `topic=news`).

- `title`: tên bài, ví dụ `Transformer (machine learning model)`. Rỗng → error dict.
- `lang`: mã ngôn ngữ 2–3 chữ (`vi`, `en`). Mã khác → error dict (lang nằm trong hostname).
- 404 → `found: false`, không phải lỗi.
- Trang định hướng → `is_disambiguation: true`, agent nên hỏi lại hoặc thử tên cụ thể hơn.
