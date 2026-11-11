# Báo cáo cá nhân — BuiDucHieu-2A202604003

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Bùi Đức Hiếu
- MSSV: 2A202604003 
- Email: 

## 2. Phần việc phụ trách
- Thiết kế và xây dựng 10 eval case nhóm trong starter_v0/data/eval_group.json, bao gồm 5 single-turn và 5 multi-turn, nhằm đánh giá khả năng sử dụng tool và xử lý hội thoại nhiều lượt của Research Agent.
- Thực hiện Test Challenge trong starter_v0/tests/test_tools_todo.py: xây dựng unit test cho các tool có sẵn, kiểm tra hành vi bình thường, input biên, xử lý lỗi và các yêu cầu về an toàn.
- Kiểm tra các trường hợp lỗi trong quá trình sử dụng tool, tập trung vào tính chính xác của arguments, xử lý thông tin thiếu, giới hạn dữ liệu và trust boundary.
- Phối hợp với các thành viên trong nhóm để tích hợp eval dataset, unit test và kết quả kiểm thử vào nhánh main.

## 3. Đóng góp cụ thể
### Xây dựng bộ 10 eval case nhóm
Xây dựng bộ eval gồm đúng 10 trường hợp, chia thành:
- 5 single-turn case (G01–G05): kiểm tra định tuyến tool github_repo, xử lý repository thiếu owner, truyền arguments cho tool papers, không gọi tool khi câu hỏi chỉ yêu cầu kiến thức chung và giới hạn chức năng chỉ đọc của tool.
- 5 multi-turn case (M01–M05): kiểm tra khả năng duy trì ngữ cảnh qua nhiều lượt, bổ sung thông tin còn thiếu, cập nhật yêu cầu khi người dùng sửa thông tin, điều chỉnh arguments và tránh gọi tool không cần thiết.
Các case được thiết kế để kiểm tra những nhóm lỗi như wrong_tool, wrong_arg_value, wrong_boundary, unnecessary_tool, out_of_scope và missing_info.
Đặc biệt, bộ eval có các tình huống kiểm tra khả năng sử dụng tool mới github_repo, đồng thời kiểm tra khả năng kết hợp thông tin giữa các lượt hội thoại thay vì chỉ xử lý từng câu hỏi độc lập.

### Hoàn thiện Unit Test Challenge
Xây dựng các unit test cho 8 tool có sẵn trong test_tools_todo.py, với tổng cộng 14 test:
- clarify: kiểm tra lựa chọn và trạng thái chờ phản hồi từ người dùng.
- format: kiểm tra nhóm nội dung theo section, đánh số thread và xử lý danh sách rỗng.
- send: kiểm tra gửi Telegram khi đã xác nhận và xử lý khi thiếu cấu hình môi trường.
- lookup: kiểm tra việc không truyền time range khi không có timeframe.
- fetch: kiểm tra ánh xạ dữ liệu trả về từ Firecrawl và giới hạn nội dung Markdown ở 4.000 ký tự.
- timeline: kiểm tra giới hạn số lượng kết quả và bỏ qua bài viết thiếu ID.
- social_search: kiểm tra truyền đúng query và search type.
- policy: kiểm tra query rỗng, lọc theo policy area và phân tách nội dung không đáng tin cậy khỏi facts.
Các test sử dụng fake_http, FakeResponse và monkeypatch để giả lập HTTP request và API key, giúp kiểm thử offline mà không cần gọi API thật.
Ngoài ra, trong commit 64f6929, có bổ sung 3 unit test cho tool mới github_repo, bao gồm:
- Happy path: kiểm tra dữ liệu metadata repository trả về và HTTP request.
- Invalid input: kiểm tra các repository identifier không hợp lệ và xác nhận không phát sinh HTTP request.
- Failure path: kiểm tra trường hợp repository không tồn tại và bảo đảm tool trả về error dict thay vì làm chương trình phát sinh exception.
### Đánh giá và kiểm thử hành vi của Agent
Thông qua eval dataset và unit test, tập trung kiểm tra hai cấp độ:
- Cấp độ Agent: Agent có chọn đúng tool, truyền đúng arguments, hỏi lại khi thiếu thông tin, duy trì context và tránh gọi tool không cần thiết hay không.
- Cấp độ Tool: Các tool có xử lý đúng input, trả về dữ liệu theo contract, xử lý lỗi và tuân thủ các giới hạn an toàn hay không.
Cách tiếp cận này giúp phát hiện cả lỗi định tuyến ở cấp độ Agent lẫn lỗi xử lý ở cấp độ triển khai tool.

## 4. Bằng chứng

- File/commit/PR:
  - starter_v0/data/eval_group.json: bộ 10 eval case nhóm.
  - starter_v0/tests/test_tools_todo.py: unit test challenge cho các tool có sẵn và unit test cho github_repo.
  - `bed87cc`, `64f6929`, `dd8e3fb` 
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
- Python và pytest: xây dựng và chạy unit test.

- Git/GitHub: quản lý source code, commit và đồng bộ nhánh làm việc.

- Mock HTTP (fake_http, FakeResponse): giả lập phản hồi API để kiểm thử offline.

## 5. Tự đánh giá

### Kết quả đạt được
- Hoàn thành bộ 10 eval case nhóm theo đúng yêu cầu về số lượng và cấu trúc, bao gồm cả single-turn và multi-turn.
- Xây dựng unit test bao phủ 8 tool có sẵn, tập trung vào các tình huống thực tế và input biên.
- Bổ sung 3 unit test cho github_repo, giúp kiểm tra cả trường hợp thành công, input không hợp lệ và lỗi từ API.
- Góp phần nâng cao khả năng đánh giá Agent ở cả cấp độ lựa chọn tool và thực thi tool.

### Bài học kinh nghiệm
- Hiểu rõ hơn sự khác biệt giữa đánh giá hành vi của Agent thông qua eval và kiểm thử logic của từng tool thông qua unit test.
- Nhận thấy việc thiết kế multi-turn eval quan trọng vì Agent cần duy trì thông tin, tiếp nhận chỉnh sửa và xử lý ngữ cảnh qua nhiều lượt hội thoại.
- Hiểu được tầm quan trọng của mock API trong unit test, giúp kiểm thử ổn định và không phụ thuộc vào dịch vụ bên ngoài.
- Chú trọng hơn đến các trường hợp biên và trust boundary, đặc biệt khi Agent xử lý dữ liệu bên ngoài hoặc thực hiện hành động có side effect.

### Hướng cải thiện
- Mở rộng eval dataset với nhiều tình huống phức tạp hơn, đặc biệt là các hội thoại nhiều lượt có thay đổi đồng thời nhiều arguments.
- Bổ sung thêm negative test cho các trường hợp API timeout, HTTP error và dữ liệu trả về không đúng định dạng.
- Tiếp tục cải thiện khả năng phát hiện lỗi giữa cấp độ Agent và cấp độ Tool để việc đánh giá có tính toàn diện hơn.
