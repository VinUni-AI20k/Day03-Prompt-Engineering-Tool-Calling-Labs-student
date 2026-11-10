---
name: deduplicate
track: core
kind: local_formatter
provider: local
requires_env: []
inputs: [items]
outputs: [items, item_count, duplicate_count]
side_effect: false
requires_confirmation: false
---

# Loại nguồn trùng

Dùng khi đã có danh sách nguồn và người dùng muốn loại các URL trùng.
Giữ item đầu tiên và thứ tự ban đầu; bỏ fragment, utm_*, fbclid, gclid
chỉ khi so sánh. URL và nội dung đầu ra vẫn giữ nguyên như item đầu tiên.
Giữ các query parameter có ý nghĩa, phân biệt HTTP/HTTPS và path có/không dấu / cuối.
Không gộp các bài khác URL chỉ vì cùng tiêu đề hoặc cùng domain.

Input: `items` là list object, mỗi object có URL HTTP(S) tuyệt đối, không chứa credentials.
List rỗng hợp lệ. Sai input hoặc lỗi xử lý trả `{tool, error, message}`, không trả kết quả một phần.
Không gọi mạng, không cần API key, không thay đổi danh sách đầu vào.
