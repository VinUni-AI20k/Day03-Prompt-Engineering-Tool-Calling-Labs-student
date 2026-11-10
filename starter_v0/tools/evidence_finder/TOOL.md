---
name: evidence_finder
track: extension
kind: live_api
provider: Tavily Search + Firecrawl v2 Scrape (fallback Tavily Extract)
requires_env: [TAVILY_API_KEY]
optional_env: [FIRECRAWL_API_KEY]
inputs: [claim, max_sources, deep_read]
outputs: [items, distinct_domains, status, warnings, assessment]
side_effect: false
---
# evidence_finder — Tìm bằng chứng theo nguồn

**Mục đích:** Nhận một nhận định cần kiểm tra, tìm nhiều trang web thuộc **hostname khác nhau**, lấy đoạn liên quan nhất và trả URL để con người/Agent đánh giá. Không suy diễn `relevance_score` thành *đúng/sai*.

## API và luồng

1. **Tavily Search** (`POST https://api.tavily.com/search`): tìm tối đa `max_sources * 3` kết quả.
2. Lọc URL không phải HTTP(S), URL nội bộ, nguồn trùng hostname; giữ tối đa `max_sources`.
3. Khi `deep_read=true`, thử **Firecrawl v2 Scrape** (`POST https://api.firecrawl.dev/v2/scrape`) để đọc trang. Nếu thất bại hoặc không có key, thử **Tavily Extract** (`POST https://api.tavily.com/extract`). Nếu cả hai thất bại, dùng snippet Tavily Search.
4. Chọn đoạn có nhiều từ khóa liên quan nhất với `claim`; trả link, excerpt, điểm phù hợp (0–1), tên API đã dùng, warning.

> **Điểm lưu ý:** Điểm chỉ đo mức trùng lặp từ khóa, **không** chứng minh tính đúng đắn, không phát hiện phủ định/số liệu sai; hostname khác nhau cũng không bảo đảm độc lập về biên tập. Với `deep_read=true`, một lần gọi có thể tiêu tốn 1 search + tối đa `2 × max_sources` extraction API calls.

## Hàm Python

```python
from tools.evidence_finder.tool import find_claim_evidence

result = find_claim_evidence(
    claim="Solar panel costs decreased in 2026",
    max_sources=3,  # 1..5
    deep_read=True,  # False: chỉ dùng snippet Search, ít tốn credits
)
print(result)
```

**Input:** `claim` bắt buộc (5–350 ký tự); `max_sources` mặc định 3 (1–5); `deep_read` mặc định `true`.

**Output mẫu (minh họa, không phải live result):**

```json
{
  "tool": "evidence_finder",
  "claim": "Solar panel costs decreased in 2026",
  "status": "ok",
  "assessment": "requires_review",
  "distinct_domains": 1,
  "items": [{
    "title": "Example report",
    "url": "https://example.org/report",
    "source": "example.org",
    "summary": "...",
    "relevance_score": 0.5,
    "extraction_provider": "firecrawl"
  }],
  "warnings": [],
  "note": "Keyword overlap measures relevance, NOT whether the claim is true."
}
```

## Khi nào dùng / không dùng

- **Dùng:** câu hỏi cần dẫn chứng cho một claim, tìm nhiều URL để dẫn nguồn; Agent cần tài liệu để phân tích thêm.
- **Không dùng:** muốn kết luận tự động `true/false`; yêu cầu trích số liệu có độ chính xác chuyên ngành mà chưa đọc/kiểm tra bản gốc; nội dung riêng tư/trang yêu cầu đăng nhập.
- **Tránh:** gán `distinct_domains` là số **nguồn độc lập** tuyệt đối.

## Lỗi và test

Lỗi theo contract repo: `{"tool":"evidence_finder","error":"RuntimeError","message":"..."}`. `status=no_results` khi search thành công nhưng không có kết quả hợp lệ.

```bash
python -m pytest tests/test_evidence_finder.py -v
```

Test sử dụng mock API, không tốn credits. Kết nối Agent bằng hướng dẫn trong `INTEGRATION.md` của bộ zip.
