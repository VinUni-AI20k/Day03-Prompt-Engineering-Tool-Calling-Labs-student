---
name: hf_models
track: bonus
kind: live_api
provider: Hugging Face Hub API (api/models)
requires_env: []
inputs: [query, task, limit]
outputs: [items]
side_effect: false
---

# hf_models

Tìm model AI/LLM open-weight công khai trên Hugging Face Hub theo từ khóa và tác vụ (pipeline task), sắp xếp theo lượt tải giảm dần.

## Khi nào dùng / không dùng

- Dùng: người dùng hỏi tìm model AI, checkpoint, LLM open-weight hoặc model theo tác vụ (như text-generation, sentence-similarity, text-classification) trên Hugging Face.
- Không dùng: tìm repo code trên GitHub (github_search), bài báo arXiv (papers), thảo luận Hacker News (hn_search), gói thư viện PyPI (pypi_info), hoặc tin tức web (lookup).

## Tham số

| Tham số | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| query | string | có | Từ khóa tên model hoặc chủ đề (vd "Qwen", "reranker"). Rỗng hoặc sai kiểu trả error dict, không gọi mạng. |
| task | string | không | Lọc theo pipeline_tag trên Hugging Face (vd "text-generation", "sentence-similarity"). Để rỗng nếu không lọc. |
| limit | integer | không | Mặc định 5, ép tối đa 10. limit <= 0 trả error dict. |

## Biến môi trường

HF_TOKEN là tùy chọn. Không có token tool vẫn truy vấn bình thường với các model công khai trên Hugging Face Hub.
