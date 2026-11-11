# Báo cáo cá nhân — HoVaTen-MSSV

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Nguyễn Công Huy
- MSSV: 2A202604086
- Email: conghuycr@gmail.com

## 2. Phần việc phụ trách

Phụ trách nghiên cứu, xây dựng hai tool mới phục vụ chức năng tìm kiếm tài liệu khoa học cho Research Agent. Bên cạnh đó, tham gia xây dựng các test case nhằm kiểm tra tính chính xác, khả năng xử lý dữ liệu đầu vào không hợp lệ và khả năng xử lý lỗi của các tool.

...

## 3. Đóng góp cụ thể

2 tool mới được tạo:

    * openalex: tìm kiếm và truy xuất thông tin nghiên cứu từ OpenAlex API.

    * semantic_scholar: tìm kiếm bài báo khoa học từ Semantic Scholar API.

Xây dựng cấu trúc cho mỗi tool gồm hai file tool.py và TOOL.md, đảm bảo thống nhất với cấu trúc các tool có sẵn trong project.

Triển khai các chức năng tìm kiếm, xử lý và chuẩn hóa thông tin bài báo như tiêu đề, tác giả, abstract, DOI, năm xuất bản, số lượt trích dẫn và đường dẫn PDF nếu có.

Bổ sung xử lý lỗi API, timeout và giới hạn số lượng kết quả trả về.

Xây dựng test case cho tool mới, tập trung vào ba trường hợp: hoạt động bình thường (happy path), dữ liệu đầu vào không hợp lệ (bad input) và lỗi khi gọi API (failure path).

Bổ sung mô tả chức năng, tham số đầu vào và dữ liệu đầu ra trong TOOL.md để hỗ trợ Agent nhận diện và sử dụng đúng tool.

...

## 4. Bằng chứng

- File/commit/PR:
    ..\tool\openalex : có 2 file tool.py và TOOL.md
    ..\tool\semantic_scholar : có 2 file tool.py và TOOL.md
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: Sử dụng ChatGPT để hỗ trợ xây dựng code, thiết kế test case và giải thích cách triển khai. Kiểm tra bằng cách rà soát cấu trúc code, kiểm tra cú pháp Python và sử dụng pytest với các trường hợp dữ liệu giả lập để đánh giá kết quả trả về.

## 5. Tự đánh giá

2 tool hoạt động khá ổn định nhưng có thể cải tiến thêm. Qua quá trình thực hiện, tôi hiểu rõ hơn cách tích hợp API bên ngoài vào hệ thống, cách chuẩn hóa dữ liệu trả về và cách xây dựng test case để kiểm tra chức năng. Tôi cũng nhận thấy việc xử lý lỗi và kiểm tra dữ liệu đầu vào rất quan trọng để đảm bảo tính ổn định của hệ thống. Tuy nhiên, các tool vẫn còn một số hạn chế như phụ thuộc vào khả năng phản hồi và giới hạn truy cập của API bên ngoài, chưa kiểm thử đầy đủ trong mọi tình huống thực tế và có thể cải thiện thêm về tốc độ cũng như chất lượng kết quả tìm kiếm.

...
