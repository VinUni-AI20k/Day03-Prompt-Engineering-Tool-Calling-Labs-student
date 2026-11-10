# Tài liệu Triển khai: Thêm 4 Tool Mới cho Research Agent

- **Ngày thực hiện:** 2026-11-10
- **Hạng mục:** Xây dựng và đăng ký 4 custom tools mới (`github_search`, `citation_check`, `currency_convert`, `weather_forecast`)

---

## 1. Tổng quan công việc đã hoàn thành

Đã xây dựng hoàn chỉnh **4 tool mới** (vượt mức `> 3 tool mới` để đủ điều kiện nhận Bonus Point của bài Lab) theo đúng chuẩn hợp đồng trong `tools/README.md` và `tests/test_tool_contract.py`. Tất cả 4 tool đều **không cần API key trả phí** và đã được kiểm tra hoạt động thực tế.

### Danh sách các file đã tạo mới và cập nhật:
1. **`tools/github_search/`**
   - `tools/github_search/TOOL.md`: Khai báo frontmatter chuẩn contract.
   - `tools/github_search/tool.py`: Hàm `search_github_repos(query, language, sort, max_results)`.
2. **`tools/citation_check/`**
   - `tools/citation_check/TOOL.md`: Khai báo frontmatter chuẩn contract.
   - `tools/citation_check/tool.py`: Hàm `check_draft_compliance(draft_text, check_type)`.
3. **`tools/currency_convert/`**
   - `tools/currency_convert/TOOL.md`: Khai báo frontmatter chuẩn contract.
   - `tools/currency_convert/tool.py`: Hàm `convert_currency(amount, from_currency, to_currency)`.
4. **`tools/weather_forecast/`**
   - `tools/weather_forecast/TOOL.md`: Khai báo frontmatter chuẩn contract.
   - `tools/weather_forecast/tool.py`: Hàm `get_weather(city, days, unit)`.
5. **Đăng ký vào hệ thống:**
   - `tools/__init__.py`: Đã import và đăng ký 4 hàm vào `TOOL_FUNCTIONS`.
   - `artifacts/tools.yaml`: Đã khai báo schema (`name`, `description`, `parameters`, `required`) của cả 4 tool ở cuối file.

---

## 2. Chi tiết kỹ thuật của 4 Tool mới

### 2.1. `github_search` (`search_github_repos`)
- **Chức năng:** Tìm kiếm kho mã nguồn mở (repository) trên GitHub qua GitHub Public REST API (`https://api.github.com/search/repositories`).
- **Tham số (`parameters`):**
  - `query` (`string`, bắt buộc): Từ khóa tìm kiếm.
  - `language` (`string`, tuỳ chọn, mặc định `""`): Ngôn ngữ lập trình (ví dụ: `"python"`, `"typescript"`).
  - `sort` (`string`, enum: `["stars", "updated", "help-wanted-issues"]`, mặc định `"stars"`): Tiêu chí sắp xếp.
  - `max_results` (`integer`, mặc định `5`, từ `1` đến `30`): Số lượng kết quả trả về.
- **Kết quả trả về (`dict`):**
  ```json
  {
    "tool": "search_github_repos",
    "query": "fastapi",
    "language": "python",
    "sort": "stars",
    "items": [
      {
        "title": "fastapi/fastapi",
        "url": "https://github.com/fastapi/fastapi",
        "source": "github.com",
        "summary": "FastAPI framework, high performance...",
        "stars": 104602,
        "language": "Python"
      }
    ]
  }
  ```

### 2.2. `citation_check` (`check_draft_compliance`)
- **Chức năng:** Kiểm duyệt một đoạn văn bản nháp (`draft_text`) trước khi xuất bản để kiểm tra xem đã có đính kèm link nguồn (`http/https`) chưa và có vô tình làm lộ thông tin nhạy cảm (email cá nhân, API key `sk-...`, `tvly-...`, `fc-...`, token Telegram) hay không. Chạy hoàn toàn cục bộ (offline).
- **Tham số (`parameters`):**
  - `draft_text` (`string`, bắt buộc): Nội dung văn bản nháp cần kiểm tra.
  - `check_type` (`string`, enum: `["all", "citation", "privacy"]`, mặc định `"all"`): Chế độ kiểm tra.
- **Kết quả trả về (`dict`):**
  ```json
  {
    "tool": "check_draft_compliance",
    "check_type": "all",
    "passed": true,
    "url_count": 1,
    "violations": []
  }
  ```

### 2.3. `currency_convert` (`convert_currency`)
- **Chức năng:** Quy đổi ngoại tệ và tra tỷ giá thực tế giữa 2 đồng tiền qua ExchangeRate-API (`https://open.er-api.com/v6/latest/{from_currency}`).
- **Tham số (`parameters`):**
  - `amount` (`number`, bắt buộc, mặc định `1.0`): Số tiền cần quy đổi (`> 0`).
  - `from_currency` (`string`, bắt buộc, mặc định `"USD"`): Mã tiền tệ gốc 3 chữ cái in hoa (ví dụ: `"USD"`, `"EUR"`, `"JPY"`).
  - `to_currency` (`string`, bắt buộc, mặc định `"VND"`): Mã tiền tệ đích 3 chữ cái in hoa (ví dụ: `"VND"`, `"USD"`).
- **Kết quả trả về (`dict`):**
  ```json
  {
    "tool": "convert_currency",
    "amount": 100.0,
    "from_currency": "USD",
    "to_currency": "VND",
    "rate": 25527.690563,
    "converted_amount": 2552769.06
  }
  ```

### 2.4. `weather_forecast` (`get_weather`)
- **Chức năng:** Xem thời tiết hiện tại và dự báo nhiệt độ cao/thấp, lượng mưa theo ngày tại một thành phố qua Open-Meteo API (`https://api.open-meteo.com/v1/forecast`). Có sẵn bảng toạ độ nhanh cho các thành phố phổ biến (`Hanoi`, `Ho Chi Minh`, `Da Nang`, `Da Lat`, `Hue`, `Tokyo`, `Seoul`, `Singapore`, `London`, `New York`, `Paris`) và tự động fallback sang Geocoding API cho mọi thành phố khác.
- **Tham số (`parameters`):**
  - `city` (`string`, bắt buộc): Tên thành phố.
  - `days` (`integer`, mặc định `1`, từ `1` đến `7`): Số ngày dự báo.
  - `unit` (`string`, enum: `["celsius", "fahrenheit"]`, mặc định `"celsius"`): Đơn vị nhiệt độ.
- **Kết quả trả về (`dict`):**
  ```json
  {
    "tool": "get_weather",
    "city": "Hanoi",
    "location": "Hanoi, Vietnam",
    "unit": "celsius",
    "days": 1,
    "current": {
      "temperature": 18.6,
      "humidity": 57,
      "precipitation_mm": 0.0
    },
    "daily": [
      {
        "date": "2026-11-10",
        "temp_max": 19.8,
        "temp_min": 15.4,
        "precipitation_mm": 0.4
      }
    ]
  }
  ```

---

## 3. Ghi chú phối hợp cho các thành viên khác trong nhóm

### A. Dành cho người viết `artifacts/system_prompt.md`
Có thể bổ sung đoạn quy tắc định tuyến (routing rules) sau vào `system_prompt.md` để model phân biệt rõ ranh giới:
- **`github_search`:** Dùng khi người dùng muốn tìm kiếm kho mã nguồn (repository) hoặc thư viện trên GitHub. **Không** dùng khi người dùng nhờ viết code hay giải bài tập lập trình (trường hợp đó là ngoài phạm vi, từ chối và không gọi tool).
- **`citation_check`:** Dùng khi người dùng đưa sẵn một đoạn văn bản nháp (`draft_text`) và yêu cầu kiểm tra xem đã có link trích dẫn chưa hoặc có bị lộ email/API key không. **Không** dùng để tra cứu quy định công ty (khi hỏi quy định/chính sách công ty, luôn dùng `policy`).
- **`currency_convert`:** Dùng khi người dùng yêu cầu quy đổi tiền tệ hoặc hỏi tỷ giá giữa các đồng tiền (truyền mã tiền 3 chữ cái in hoa như `USD`, `VND`, `JPY`, `EUR`).
- **`weather_forecast`:** Dùng khi người dùng hỏi thời tiết hoặc dự báo mưa nắng tại một thành phố cụ thể (`city`). Nếu người dùng hỏi thời tiết nhưng chưa nói tên thành phố, hãy gọi `clarify` để hỏi lại.

### B. Câu hỏi mẫu để test trong `chat.py` / `eval_group.json` / UI Showdown
1. **Test `github_search`:** *"Tìm giúp mình 5 repo Python nhiều sao nhất trên GitHub về RAG"* → `github_search(query="RAG", language="python", sort="stars", max_results=5)`
2. **Test `citation_check`:** *"Kiểm tra giúp mình bản nháp này xem có lộ thông tin hay thiếu nguồn không: Bản tin AI nội bộ liên hệ admin@company.com với key sk-proj-1234567890abcdef"* → `citation_check(draft_text="...", check_type="all")`
3. **Test `currency_convert`:** *"Đổi 250 USD sang VND giúp mình"* → `currency_convert(amount=250, from_currency="USD", to_currency="VND")`
4. **Test `weather_forecast`:** *"Dự báo thời tiết Hà Nội 3 ngày tới thế nào?"* → `weather_forecast(city="Hanoi", days=3, unit="celsius")`
