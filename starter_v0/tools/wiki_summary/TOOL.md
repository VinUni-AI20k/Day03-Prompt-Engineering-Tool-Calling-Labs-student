---
name: wiki_summary
track: bonus
kind: live_api
provider: Wikimedia REST API
requires_env: []
inputs: [title, lang]
outputs: [title, lang, description, extract, url, page_type]
side_effect: false
---
# wiki_summary

Lấy tóm tắt bài viết Wikipedia qua `GET https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}`.
Bắt buộc gửi User-Agent. Hỗ trợ tiếng Anh (`en`) và tiếng Việt (`vi`).