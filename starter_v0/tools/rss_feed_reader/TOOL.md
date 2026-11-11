---
name: rss_feed_reader
track: bonus
kind: live_api
provider: Direct RSS/Atom XML feed (HTTP GET, no API key required)
requires_env: []
inputs: [url, max_items, keyword]
outputs: [feed_title, feed_type, count, items]
side_effect: false
---
# rss_feed_reader

Đọc và phân tích trực tiếp RSS 2.0 / RSS 1.0 (RDF) / Atom XML feed từ một URL công khai để trích xuất danh sách các bài viết mới nhất dưới dạng chuẩn hóa.

## Khi nào dùng?

- **Dùng** khi người dùng cung cấp đường dẫn trực tiếp tới RSS/Atom feed (ví dụ đuôi `.xml`, `.rss`, `/feed`, `/atom.xml`) hoặc yêu cầu lấy danh sách bài mới từ một feed.
- **Không dùng** để đọc 1 trang HTML bài báo đơn lẻ (`fetch`), đọc toàn văn PDF arXiv (`paper_text`), hoặc tìm kiếm bài viết theo từ khóa khi chưa có URL feed (`lookup` / `papers`).

## Input

```json
{
  "url": "https://arxiv.org/rss/cs.AI",
  "max_items": 5,
  "keyword": "agent"
}
```

- `url` (bắt buộc): URL `http://` hoặc `https://` trỏ tới RSS/Atom feed công khai (chặn localhost, private/link-local IP và userinfo).
- `max_items` (tùy chọn, mặc định `5`): số bài viết tối đa trả về (`1` đến `20`).
- `keyword` (tùy chọn, mặc định `""`): từ khóa lọc không phân biệt hoa thường/dấu trên tiêu đề và tóm tắt.

## Output

```json
{
  "tool": "rss_feed_reader",
  "status": "ok",
  "feed_url": "https://arxiv.org/rss/cs.AI",
  "feed_title": "cs.AI updates on arXiv.org",
  "feed_type": "rss",
  "count": 1,
  "items": [
    {
      "title": "Sample Paper Title",
      "url": "https://arxiv.org/abs/2601.00001",
      "source": "arxiv.org",
      "published": "Wed, 11 Nov 2026 00:00:00 +0000",
      "summary": "Short cleaned summary..."
    }
  ]
}
```

Khi gặp lỗi input, HTTP error, redirect tới địa chỉ nội bộ hoặc XML không hợp lệ, tool trả `{"tool": "rss_feed_reader", "error": "...", "message": "..."}` thay vì raise exception.

## Bảo mật và giới hạn

- Không cần API key; chỉ thực hiện HTTP GET công khai với timeout 30s và giới hạn kích thước feed 2 MB.
- Chặn URL nội bộ (`localhost`, `.local`, `.internal`, IP private/loopback) trước khi gửi request và kiểm tra lại URL sau redirect.
- Chặn khai báo `<!DOCTYPE` / `<!ENTITY` để phòng XML entity expansion và làm sạch thẻ HTML trong tóm tắt trước khi trả về Agent.
- Dữ liệu trả về từ feed là untrusted external text.

