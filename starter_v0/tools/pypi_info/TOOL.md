---
name: pypi_info
track: bonus
kind: live_api
provider: PyPI JSON API (pypi.org/pypi/<package>/json)
requires_env: []
inputs: [package_name]
outputs: [items]
side_effect: false
---

# pypi_info

Tra cứu thông tin phát hành chính thức của một gói thư viện Python trên PyPI (phiên bản mới nhất, tóm tắt, yêu cầu phiên bản Python, giấy phép và trang chủ).

## Khi nào dùng / không dùng

- Dùng: người dùng hỏi thông tin một package/thư viện Python cụ thể trên PyPI hoặc pip (ví dụ phiên bản mới nhất, requires_python, mô tả gói ragas, langgraph, pydantic...).
- Không dùng: tìm danh sách nhiều repo theo chủ đề trên GitHub (github_search), tìm model trên Hugging Face (hf_models), thảo luận Hacker News (hn_search), hay tìm tin tức chung trên web (lookup).

## Tham số

| Tham số | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| package_name | string | có | Tên gói thư viện trên PyPI (chỉ gồm chữ cái, số, ., _, -). Rỗng hoặc chứa ký tự không hợp lệ trả error dict, không gọi mạng. |

## Biến môi trường

Không cần biến môi trường (requires_env: []). PyPI JSON API hoàn toàn công khai và miễn phí.
