# Báo cáo cá nhân — Trương Đặng Minh Khuê

## 1. Thông tin thành viên

- **Họ tên:** Trương Đặng Minh Khuê
- **MSSV:** 2A202603785
- **Email:** 26ai.khuetdm@vinuni.edu.vn

## 2. Phần việc phụ trách

- Cải tiến System Prompt và đánh giá khả năng routing, sử dụng tool của AI Agent.
- Phân tích lỗi từ evaluation, đề xuất giả thuyết và thực hiện các phiên bản prompt v1, v2, v3.
- Implement và tích hợp các tool mới: `date_calc`, `cite_format`.
- Viết và sửa unit tests, xử lý các lỗi phát sinh để đảm bảo chất lượng và độ an toàn của tool.
- Kiểm tra kết quả evaluation và ghi nhận thực nghiệm qua các artifacts.

## 3. Đóng góp cụ thể

### 3.1. Cải tiến System Prompt và Tool Routing

Thực hiện phân tích lỗi từ baseline v0 (13/20 cases PASS, accuracy 65%) và cải tiến prompt qua nhiều phiên bản:

- **v1 – Send boundary:** Làm rõ sự khác biệt giữa trả lời trực tiếp trong chat và sử dụng tool `send` để thực hiện hành động bên ngoài. Kết quả: 16/20 PASS (80%), sửa được R08 và R14.
- **v2 – Clarification routing:** Bổ sung quy tắc phân biệt `response_type="text"` khi thiếu thông tin và `response_type="yes_no"` khi cần xác nhận hành động. Kết quả: 17/20 PASS (85%).
- **v3 – Missing information:** Bổ sung quy tắc phân biệt `timeline`, `social_search` và `clarify` khi thiếu username hoặc chủ đề tìm kiếm. Kết quả: R10 PASS, base suite đạt 19/20 PASS.

Ngoài ra, xử lý các vấn đề liên quan đến argument convention (R03, R13), xác nhận trước khi gửi (R12) và thiếu `response_type` khi yêu cầu thông tin dạng văn bản.

### 3.2. Implement tool mới

**Tool `date_calc`:**

- Hỗ trợ lấy ngày hiện tại, tính số ngày giữa hai mốc, cộng ngày và xác định thứ.
- Cập nhật `tools.yaml`, System Prompt, tool registry và evaluation cases G01–G03.
- Kết quả: cả 3 evaluation cases PASS.

**Tool `cite_format`:**

- Implement chức năng tạo citation theo chuẩn APA 7 từ metadata gồm title, authors, year và URL.
- Xử lý trường hợp thiếu year bằng `(n.d.)`, thiếu URL thì bỏ phần URL.
- Chuyển tên tác giả dạng Last, First thành initials; hỗ trợ hai tác giả nối bằng `&`.
- Trả về error có cấu trúc khi yêu cầu style không được hỗ trợ.
- Phân biệt rõ chức năng với tool `format` có sẵn: `format` xử lý nội dung chung, `cite_format` chỉ dành cho APA.
- Sửa lỗi mất dấu chấm cuối citation khi có URL sau khi unit test phát hiện.
- Kết quả: unit tests PASS, group evaluation G04–G06 đạt 6/6 PASS.

### 3.3. Kiểm thử và xử lý lỗi

Tham gia xử lý các vấn đề trong quá trình chạy test:

- Sửa test `send` sau khi đọc lại fixture `fake_http` trong `conftest.py` và xác định đúng cách sử dụng factory.
- Cải thiện `send_telegram`: che token trong error message, yêu cầu `confirmed is True`, bỏ `parse_mode="Markdown"` để tránh lỗi định dạng, kiểm tra nội dung rỗng trước khi gửi request.
- Sửa test policy do nhầm cấu trúc dữ liệu `untrusted_text`, vốn nằm trong từng item của `results`.
- Điều chỉnh test trust boundary để tìm đúng nội dung trong source, tăng `top_k` và tránh phụ thuộc vào thứ hạng kết quả tìm kiếm.
- Sửa cách tìm kiếm file bằng PowerShell khi `Select-String` không hỗ trợ tham số `-Recurse`.

### 3.4. Bài học rút ra

- Cần đọc implementation và fixture thực tế trước khi viết test, thay vì suy đoán tên tham số hoặc cấu trúc dữ liệu.
- Test trust boundary cần dựa trên dữ liệu thực tế và kiểm tra đúng nguồn chứa nội dung.
- Prompt engineering cần dựa trên lỗi quan sát được, có giả thuyết cụ thể và đánh giá lại bằng cùng bộ test.
- Cần phân biệt rõ lỗi routing, lỗi arguments, lỗi thiếu thông tin và lỗi vi phạm ranh giới hành động.

## 4. Bằng chứng

**File/artifacts:**

- `artifacts/system_prompt.md`: Các phiên bản System Prompt và quy tắc routing được cải tiến.
- `artifacts/tools.yaml`: Cập nhật mô tả và hướng dẫn arguments của tools.
- `tools/date_calc.py`: Implementation tool tính toán ngày.
- `tools/cite_format.py`: Implementation tool tạo citation APA 7.
- `tools/__init__.py`: Đăng ký tool mới.
- `version_log.csv`: Ghi nhận hypothesis, thay đổi và kết quả qua từng phiên bản.
- `runs/*.json`: Lưu kết quả evaluation của từng lần chạy.
- Các file unit tests và test policy liên quan.

**AI/công cụ đã dùng và cách tự kiểm tra kết quả:**

- Sử dụng AI hỗ trợ phân tích lỗi, đề xuất hướng cải tiến System Prompt và hỗ trợ debugging.
- Sử dụng Python và pytest để chạy unit tests và evaluation.
- Sử dụng Git để quản lý các thay đổi và phiên bản.
- Tự kiểm tra bằng cách đối chiếu expected/actual tool calls, arguments, kết quả evaluation và chạy lại unit tests sau khi sửa lỗi.

## 5. Tự đánh giá

**Điểm đã làm tốt:**

- Có khả năng phân tích lỗi dựa trên kết quả thực nghiệm và đưa ra giả thuyết cải tiến cụ thể.
- Chủ động triển khai tool mới, tích hợp vào hệ thống và viết kiểm thử.
- Biết sử dụng test failures để truy ngược nguyên nhân thay vì chỉ sửa kết quả đầu ra.

**Điểm cần cải thiện:**

- Cần thiết kế test cases có độ bao phủ tốt hơn, đặc biệt với các trường hợp biên và trust boundary.
- Cần cải thiện khả năng thiết kế System Prompt để xử lý các tình huống phức tạp mà không gây ảnh hưởng đến các cases đã PASS.
- Cần chú trọng hơn đến việc kiểm thử hồi quy sau mỗi lần thay đổi prompt hoặc tool.

**Đánh giá chung:** Hoàn thành các phần việc được phụ trách, có đóng góp vào cải tiến khả năng routing, mở rộng chức năng tools và nâng cao chất lượng kiểm thử của hệ thống.
