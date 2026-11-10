---
name: github_search
track: bonus
kind: live_api
provider: GitHub REST API (search/repositories)
requires_env: []
inputs: [query, language, limit]
outputs: [items]
side_effect: false
---
# github_search

Tìm repository mã nguồn mở công khai trên GitHub theo từ khóa, sắp xếp theo số sao giảm dần.

## Khi nào dùng / không dùng

- Dùng: người dùng hỏi repo, mã nguồn, thư viện, project open-source trên GitHub.
- Không dùng: tin tức web (`lookup`), bài báo khoa học (`papers`), bài đăng X (`social_search`).

## Tham số

| Tham số | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| `query` | string | có | Không được rỗng. Rỗng hoặc sai kiểu thì trả error dict, không gọi mạng. |
| `language` | string | không | Thêm `language:<x>` vào truy vấn GitHub. Để rỗng nếu không lọc. |
| `limit` | integer | không | Mặc định 5, ép tối đa 10. `limit <= 0` trả error dict. |

## Biến môi trường

`GITHUB_TOKEN` là tùy chọn. Không có token tool vẫn chạy (GitHub giới hạn khoảng 10 request/phút cho search ẩn danh). Có token thì được nâng hạn mức.

## Output

- Thành công:
    {"tool": "github_search", "query": "llm agent language:python", "items": [{"title": "owner/repo", "url": "https://github.com/owner/repo", "source": "github.com", "stars": 1234, "language": "Python", "summary": "..."}]}

- Lỗi (input xấu, HTTP 403/429, timeout, mất mạng): tool không raise mà trả:
    {"tool": "github_search", "query": "...", "items": [], "error": "...", "next_step": "..."}
