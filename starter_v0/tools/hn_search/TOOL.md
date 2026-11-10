---
name: hn_search
track: bonus
kind: live_api
provider: Hacker News Algolia API (hn.algolia.com)
requires_env: []
inputs: [query, sort_by, limit]
outputs: [items]
side_effect: false
---

# hn_search

Tìm kiếm bài đăng và thảo luận công nghệ trên Hacker News (Y Combinator) theo từ khóa, sắp xếp theo điểm bình chọn (points) hoặc thời gian mới nhất (date).

## Khi nào dùng / không dùng

- Dùng: người dùng hỏi tìm bài viết, thảo luận hoặc ý kiến cộng đồng kỹ thuật trên Hacker News (HN).
- Không dùng: bài đăng trên X/Twitter (social_search), tin tức báo chí chung trên web (lookup), repo GitHub (github_search), model Hugging Face (hf_models), hoặc gói PyPI (pypi_info).

## Tham số

| Tham số | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| query | string | có | Từ khóa chủ đề cần tìm trên Hacker News. Rỗng hoặc sai kiểu trả error dict, không gọi mạng. |
| sort_by | string | không | Chỉ nhận "points" (mặc định, bài nhiều điểm nhất) hoặc "date" (bài mới nhất). Giá trị khác trả error dict. |
| limit | integer | không | Mặc định 5, ép tối đa 10. limit <= 0 trả error dict. |

## Biến môi trường

Không cần biến môi trường (requires_env: []). Algolia Hacker News API hoàn toàn công khai và miễn phí.
