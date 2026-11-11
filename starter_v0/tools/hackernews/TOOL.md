---
name: hackernews
track: bonus
kind: live_api
provider: Algolia Hacker News Search API
requires_env: []
inputs: [query, sort, limit]
outputs: [items, count, total_hits, query, sort, freshness]
side_effect: false
---
# hackernews

Bài đăng và thảo luận công nghệ trên Hacker News, kèm tín hiệu cộng đồng
(`points`, `comments`). Không cần API key.

- **Dùng khi:** người dùng hỏi "trên Hacker News", "dân dev bàn gì", "Show HN",
  "thảo luận kỹ thuật về X", hoặc cần thêm một nguồn cộng đồng bên cạnh X.
- **KHÔNG dùng khi:** cần tin báo chí/web nói chung (dùng `lookup`), tweet trên X
  (dùng `social_search`), paper (dùng `papers`), hay khi đã có URL cụ thể (dùng `fetch`).
- Gọi `GET https://hn.algolia.com/api/v1/search` (hoặc `/search_by_date`) với
  `tags=story`, `hitsPerPage=limit`, `User-Agent` mô tả tool.

## Contract

| Arg | Type | Default | Ghi chú |
|---|---|---|---|
| `query` | string | `""` | Từ khóa; rỗng/sai kiểu -> error dict |
| `sort` | `relevance` \| `date` | `relevance` | Chọn endpoint: `relevance` -> `/search`, `date` -> `/search_by_date`; ngoài enum -> error dict, **không** gọi mạng |
| `limit` | int 1..20 | `5` | Ngoài khoảng / bool / string -> error dict |

Thành công: `items[]` gồm `title`, `url` (bài gốc, hoặc link item HN nếu Ask/Show HN
không có URL), `source`, `summary` ("N points · M comments"), `points`, `comments`,
`created_at`, `hn_url`, `text` (body Ask HN đã bỏ HTML, ≤ 500 ký tự), cộng `count`,
`total_hits`, `query`, `sort`, `freshness`.

Thất bại: `{"tool": "hackernews_search", "error": "<ExceptionType>", "message": "..."}`
— không bao giờ raise. HTTP 429 -> `HTTPError`; mất mạng -> `ConnectionError`.

## Trust boundary

Tiêu đề/nội dung là nội dung công khai nhưng **không kiểm chứng**: chỉ dùng làm tín
hiệu ("đang được bàn"), không coi là fact đã xác nhận; trích `url` gốc.

## Tests

`tests/test_tools_todo.py::test_hackernews_*` — 4 test offline (mock HTTP): happy path,
`sort=date` đổi endpoint, input xấu từ model, HTTP 429.
