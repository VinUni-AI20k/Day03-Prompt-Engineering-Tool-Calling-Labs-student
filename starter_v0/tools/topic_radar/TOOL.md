---
name: topic_radar
track: extension
kind: live_api
provider: Tavily News + RapidAPI Twitter API45 + Firecrawl v2 Scrape (fallback Tavily Extract)
requires_env: []
optional_env: [TAVILY_API_KEY, RAPIDAPI_KEY, RAPIDAPI_TWITTER_HOST, FIRECRAWL_API_KEY]
inputs: [query, timeframe, limit, include_social, enrich_articles]
outputs: [items, signals, status, warnings]
side_effect: false
---
# topic_radar — Đối chiếu tin tức và trao đổi trên X

**Mục đích:** Với một chủ đề, lấy mẫu kết quả báo chí từ Tavily (news) và bài đăng X từ RapidAPI Twitter API45, chuẩn hóa `items` theo format của Agent, đo số trang tin khác hostname và từ khóa cùng xuất hiện ở 2 nền tảng.

## API và luồng

1. **Tavily Search** (`POST /search`, `topic=news`, `time_range=day|week|month|year`): tìm bài mới theo từ khóa.
2. **RapidAPI Twitter API45** (`GET /search.php`, `query=...`, `search_type=Latest`): tìm bài đăng X, loại ID trùng và trích engagement có sẵn.
3. (Tùy chọn) **Firecrawl v2 Scrape** làm giàu tối đa **2** bài báo. Khi thất bại, fallback **Tavily Extract**.
4. So sánh các token xuất hiện trong mẫu web và X. Trả `signals` để Agent nhận xét **sự tương đồng chủ đề**, không phải đo xu hướng toàn thị trường.

Để vẫn dùng được khi thiếu một API key, tool trả `status=partial` và `warnings` nếu nguồn khác vẫn hoạt động. Chỉ trả lỗi khi cả hai nguồn chính đều không thành công.

## Hàm Python

```python
from tools.topic_radar.tool import compare_topic_signals

result = compare_topic_signals(
    query="open source language models",
    timeframe="week",    # day, week, month, year
    limit=5,             # 1..10, mỗi nguồn tối đa limit item
    include_social=True, # False: bỏ RapidAPI
    enrich_articles=True # False: không tốn scraping API credits
)
print(result)
```

**Input:** `query` 2–250 ký tự; `timeframe` mặc định `week`; `limit` mặc định 5; `include_social` mặc định `true`; `enrich_articles` mặc định `false`.

**Output mẫu (minh họa, không phải live result):**

```json
{
  "tool": "topic_radar",
  "query": "open source language models",
  "timeframe": "week",
  "items": [
    {"title":"Example news", "url":"https://example.com/news", "source":"example.com", "summary":"...", "section":"news", "provider":"tavily", "date":null},
    {"title":"Example post", "url":"https://x.com/i/status/123456", "source":"x.com", "summary":"...", "section":"social", "provider":"rapidapi", "date":null, "metrics":{"likes":4,"retweets":1}}
  ],
  "signals": {"news_results":1,"news_domains":1,"x_post_results":1,"shared_terms":["models"]},
  "status":"ok", "warnings":[],
  "note":"These are small API samples; counts and overlap are not proof of popularity or truth."
}
```

## Khi nào dùng / không dùng

- **Dùng:** nghiên cứu một chủ đề đang được nhắc đến ở báo chí và X; muốn đối chiếu các từ khóa chung hoặc lấy mẫu minh họa có URL.
- **Không dùng:** tính số bài đăng X thực tế theo ngày, kết luận một chủ đề đang viral toàn cầu, phân tích sentiment, hoặc coi bài mạng xã hội là bằng chứng đã xác minh.
- `timeframe` **chỉ lọc Tavily news**; X API45 `/search.php` không được tool lọc cùng khung thời gian. Không so sánh trực tiếp số lượng `news_results` và `x_post_results` như thống kê chuẩn hóa.
- X API45 là một **RapidAPI product cụ thể**, key RapidAPI không tự cấp quyền truy cập mọi API; cần đăng ký riêng sản phẩm Twitter API45.

## Lỗi và test

Lỗi theo contract repo: `{"tool":"topic_radar","error":"RuntimeError","message":"..."}`. Nếu một nguồn lỗi, `status=partial` và `warnings` giải thích.

```bash
python -m pytest tests/test_topic_radar.py -v
```

Test dùng mock, không gọi API thật. Kết nối Agent xem `INTEGRATION.md`.
