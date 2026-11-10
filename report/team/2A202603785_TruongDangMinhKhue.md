# Báo cáo cá nhân — HoVaTen-MSSV

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Trương Đặng Minh Khuê
- MSSV: 2A202603785
- Email: 26ai.khuetdm@vinuni.edu.vn

## 2. Phần việc phụ trách

...

## 3. Đóng góp cụ thể

...

## 4. Bằng chứng

- File/commit/PR:
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:

## 5. Tự đánh giá

...

## Hướng V1:

Case Lỗi thực tế Nguyên nhân
R03 wrong_arg_value Thêm "news" vào query dù đã có topic=news
R08 unexpected_tool_call Dùng send để trả lời bài toán
R10 missing_info Tự đoán handle sama thay vì hỏi
R11 missing_info Tự đoán URL example.com/article
R12 wrong_boundary Gọi send trước khi user xác nhận
R13 wrong_arg_value Query web sai; thiếu topic=news
R14 unexpected_tool_call Dùng send để trả lời yêu cầu coding

Hai lỗi cần chú ý nhất
R08 và R14:

Agent có thể tạo câu trả lời trực tiếp, nhưng lại gọi send để đưa câu trả lời vào một hành động bên ngoài.

Đây là lỗi phân biệt giữa:

- Trả lời user trong chat.
- Gọi tool để thực hiện hành động bên ngoài.
  R10 và R11:

Agent tự điền thông tin còn thiếu thay vì hỏi user. Đây là lỗi hallucination ở bước thu thập thông tin.

2. Phân loại lỗi để ghi vào báo cáo
   Loại lỗi Case
   wrong_arg_value R03, R13
   out_of_scope R08, R14
   missing_info R10, R11
   wrong_boundary R12

v1: Sửa send boundary.

v2: Sửa missing information (R10, R11).

v3: Sửa argument convention (R03, R13).

**Note**:
v1 đã cải thiện đúng hướng:
Metric v0 v1
Passed 13/20 16/20
Accuracy 65% 80%
R08 FAIL PASS
R14 FAIL PASS
R12 FAIL FAIL
R12 chưa sửa được dù đã thêm confirmation boundary. Có thể model chưa hiểu rõ thứ tự bắt buộc: hỏi xác nhận trước, chỉ gửi sau khi user trả lời đồng ý.

Nhưng đừng sửa tiếp v1. Ta cần giữ kết quả thực nghiệm.

16/20 — 80%

- R08: fixed
- R14: fixed
- R12: chưa fixed
- R10: chưa fixed
- R03, R13: chưa fixed

**Note**:

## Hướng v2

Giả thuyết: Explicit clarification-type routing rules will reduce incorrect clarify.response_type selection.

**V2 Prompt**:

#### Clarification Rules

- Use clarify with response_type="text" when required
  information is missing, such as a username or URL.

- Use clarify with response_type="yes_no" when the user
  requests an external action that requires confirmation,
  such as sending, posting, or publishing.

- Never use response_type="text" to ask for action confirmation.

**Result**:
17/20 — 85%
So với v0: +20 percentage points (65% → 85%).

Phân tích R13
Routing đã đúng cả hai tool:

- lookup: đúng.
- social_search: đúng.
  Nhưng arguments sai:
  Argument Expected Actual
  query AI AI news
  topic news Missing

Nguyên nhân: Model chưa tuân thủ convention topic=news, đồng thời thêm "news" vào query.
Trạng thái hiện tại
Case Trạng thái
R03 PASS
R08 PASS
R10 FAIL
R12 FAIL
R13 FAIL

## Hướng v3

Bổ sung quy tắc xử lý trường hợp thiếu username khi người dùng yêu cầu tìm tweet.

Ưu tiên yêu cầu xác nhận yes_no trước khi thực hiện hành động gửi/đăng, kể cả khi nội dung chưa được cung cấp.
Case còn lại cần kiểm tra: R12_confirm_before_send.
18/20 PASS
Những file/artifacts đã chỉnh sửa

- artifacts/system_prompt.md: cải tiến prompt qua từng version.
- artifacts/tools.yaml: cập nhật mô tả và hướng dẫn arguments của tool lookup.
- version_log.csv: ghi lại lý do thay đổi, hypothesis và metric.
- runs/\*.json: lưu kết quả evaluation của từng lần chạy.

## Tool mới date calc

Implement tool date_calc hỗ trợ tính ngày hiện tại, số ngày giữa hai mốc, cộng ngày và xác định thứ.

Cập nhật tools.yaml, system_prompt.md, registry và eval cases G01–G03. Cả 3 cases đều PASS.

Khi chạy lại base, phát sinh R11: thiếu response_type="text" khi gọi clarify để hỏi URL.

Fix bằng cách bổ sung rule trong system_prompt.md: khi hỏi thông tin dạng văn bản còn thiếu (URL, nội dung bài viết, tên...), phải đặt response_type="text".

## Tool 2: cite_format

**Mục đích:** Tạo citation APA 7 từ metadata (title, authors, year, url).

**Quyết định thiết kế:**

- `title`, `authors` bắt buộc; thiếu `year` → `(n.d.)`; thiếu `url` → bỏ phần URL.
- Tên tác giả "Last, First" → initials; 2 tác giả nối bằng `&`.
- Style khác APA → trả `{"error": ...}`, không raise exception.

**Vấn đề gặp phải:**

1. Trùng chức năng với tool `format` có sẵn → làm rõ trong mô tả: `format` cho nội dung chung, `cite_format` chỉ cho APA.
2. Unit test phát hiện citation có URL bị mất dấu chấm cuối → sửa cách nối URL.

**Đăng ký:** `tools/__init__.py`, `artifacts/tools.yaml`.

**Kết quả:** Unit tests PASS. Group eval: 6/6 PASS (G04–G06 cho cite_format).

## Lỗi prompt: R10_missing_handle

- **Input:** "Tóm tắt 5 tweet mới nhất giúp mình"
- **Triệu chứng:** model gọi `social_search(query="tweet")` thay vì `clarify`.
- **Nguyên nhân:** prompt chỉ cấm đoán handle, không cấm bịa query khi thiếu cả account lẫn chủ đề. "Mới nhất" còn khớp với `search_type="Latest"`.
- **Cách sửa:** thêm luật phân biệt `timeline` (có handle), `social_search` (có chủ đề), `clarify` (thiếu cả hai).
- **Kết quả:** R10 PASS. Base suite: 19/20, **R12 còn FAIL (wrong_boundary), đang xử lý / ghi nhận là known issue.**
