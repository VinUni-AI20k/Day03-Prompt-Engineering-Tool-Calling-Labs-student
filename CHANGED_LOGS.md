# Nhật ký thay đổi

Ghi lại nhóm Ban5 đã sửa gì, kết quả tốt lên hay xấu đi, và bằng chứng nằm ở đâu.
Mới nhất ở trên cùng. Chỉ ghi những gì đã làm và đo thật.

**Cách đọc điểm:** bộ kiểm tra có 20 tình huống. Mỗi tình huống đạt nếu trợ lý chọn đúng công cụ và điền đúng thông tin. "Đạt 13/20" nghĩa là đúng 13 trong 20 tình huống.

## Kết quả qua các lần sửa

| Lần | Ai làm | Đã sửa gì | Đạt | Bằng chứng |
|---|---|---|---|---|
| v0 | QuanNH | Chưa sửa gì (đo mốc ban đầu) | 13/20 | `starter_v0/runs/v0_B_base_openai_20261110T173801779394.json` |
| v1 | QuanNH | Sửa lời dặn cho trợ lý: hỏi lại khi thiếu thông tin, xin xác nhận trước khi gửi | 18/20 | `starter_v0/runs/v1_B_base_openai_20261110T175732383834.json` |
| v2 | QuanNH | Sửa lời dặn: nói rõ công cụ nào dùng cho việc nào, từ chối việc ngoài phạm vi, xin xác nhận dạng có/không | 18/20 | `starter_v0/runs/v2_B_base_openai_20261110T181054950591.json` |
| v3 | | | | |

Số liệu chi tiết: `starter_v0/artifacts/version_log.csv`. Bảng lỗi từng tình huống: `starter_v0/analysis/v0.csv`, `v1.csv`.

## Chi tiết

### v2 — Dặn rõ công cụ nào dùng cho việc nào

- **Sửa file nào:** `starter_v0/artifacts/system_prompt.md` (vẫn chưa sửa mô tả công cụ).
- **Vì sao sửa:** sau v1 còn 2 tình huống sai. R12: trợ lý hỏi "bạn muốn đăng nội dung gì?" thay vì hỏi có đồng ý đăng không. M02: ở lượt cuối trợ lý đi tìm trên mạng xã hội thay vì tìm tin tức.
- **Đã làm:** thêm mục "chọn công cụ" (tin tức thì dùng `lookup`, bài đăng của một người thì dùng `timeline`, bài đăng theo chủ đề thì dùng `social_search`, đọc link thì dùng `fetch`), dặn giữ công cụ cũ khi người dùng chỉ đổi chủ đề, dặn từ chối việc ngoài phạm vi, và dặn hỏi xác nhận dạng có/không ngay cả khi chưa có nội dung để gửi.
- **Kết quả:** vẫn 18/20, không tiến thêm.
  - Tốt lên: M02 đúng lại (trợ lý giữ đúng công cụ tìm tin tức).
  - Vẫn sai (R12): trợ lý vẫn hỏi "bạn muốn đăng nội dung gì?" dù đã dặn rõ. Lời dặn này xung đột với lời dặn "thiếu thông tin thì hỏi lại", và mô hình chọn hỏi thông tin.
  - Mới sai (M06): người dùng bảo "bỏ Twitter, chuyển sang tìm tin tức", trợ lý tìm tin tức nhưng vẫn gọi thêm tìm trên Twitter. Rất có thể do lời dặn "giữ công cụ cũ" mới thêm bị hiểu quá rộng.
- **Bài học:** sửa một chỗ có thể làm hỏng chỗ khác, nên mỗi lần chỉ nên đổi ít. Lời dặn mâu thuẫn nhau thì mô hình chọn theo một bên. Chỉ chạy một lần nên chưa chắc M06 do lời dặn mới hay do mô hình lúc đúng lúc sai.
- **Việc tiếp theo (v3):** sửa mô tả công cụ trong `tools.yaml` (khi nào dùng, khi nào không), đặc biệt mô tả `clarify` (dùng dạng có/không để xin xác nhận) và `social_search`.

### v1 — Dặn trợ lý hỏi lại và xin xác nhận

- **Sửa file nào:** `starter_v0/artifacts/system_prompt.md` (lời dặn cho trợ lý).
- **Vì sao sửa:** ở v0, trợ lý tự đoán khi người dùng nói thiếu (ví dụ không nói tweet của ai thì tự chọn một người nổi tiếng) và gửi tin đi mà không hỏi. Lời dặn gốc của bài mẫu chính là bảo nó làm như vậy.
- **Đã làm:** bỏ các lời dặn đó, thay bằng: thiếu thông tin thì hỏi lại; trước khi gửi gì đi thì hỏi người dùng đồng ý chưa.
- **Kết quả:** từ 13/20 lên 18/20.
  - Tốt lên: trợ lý biết hỏi lại khi thiếu tên tài khoản hoặc đường link. Không còn tự gửi bài toán hay đoạn code đi. Tìm tin tức và tìm tweet cùng lúc cũng đúng.
  - Vẫn sai (R12): khi người dùng bảo "đăng bản tin lên Telegram", trợ lý có hỏi lại nhưng hỏi "bạn muốn đăng nội dung gì?" thay vì hỏi "bạn đồng ý đăng không?".
  - Mới sai (M02): trong hội thoại nhiều lượt, ở lượt cuối trợ lý đi tìm trên mạng xã hội thay vì tìm tin tức. Trước đây tình huống này đúng, nên đây là lỗi mới do thay đổi gây ra, hoặc chỉ là do mô hình lúc đúng lúc sai. Cần chạy thêm để biết.
- **Bài học:** gỡ lời dặn xấu cải thiện nhiều nhất. Nhưng chỉ nói "hãy hỏi lại" là chưa đủ, cần nói rõ hỏi kiểu nào và dùng công cụ nào cho việc gì.
- **Việc tiếp theo (v2):** dặn rõ công cụ nào dùng cho việc nào, và khi xin xác nhận thì hỏi dạng có/không.

### v0 — Đo mốc ban đầu

- Chưa sửa gì, chạy thử để biết trợ lý đang làm tốt đến đâu: 13/20.
- 7 tình huống sai, chia thành 4 kiểu:
  - Tự đoán thay vì hỏi lại (R10, R11): tự đoán tên tài khoản và đường link.
  - Gửi đi mà không xin phép (R12).
  - Làm việc ngoài phạm vi (R08, R14): bài toán và đoạn code đáng lẽ phải từ chối, nhưng trợ lý lại gửi đi.
  - Chọn sai công cụ hoặc thiếu công cụ (R03, R13).
- Bảng chi tiết nằm trong `report/team/group_report.md` (mục B2).

## Việc khác đã làm

- **Phân việc nhóm:** thư mục `tasks/` có bảng vai trò và checklist cho từng người.
- **Thông tin nhóm:** điền vào `TEAM.md` (nhóm Ban5, lớp L3B, 3 thành viên).
- **Telegram:** tạo bot và kênh riêng của nhóm để thử tính năng gửi tin. Khóa bí mật của bot chỉ lưu trên máy, không đưa vào repo.

## Còn phải làm

- [ ] v2, v3: tiếp tục sửa lời dặn và mô tả công cụ
- [ ] Thêm công cụ mới và kiểm tra nó chạy đúng (DucLT)
- [ ] Viết 10 tình huống kiểm tra riêng của nhóm (TrungNB)
- [ ] Làm giao diện chat và chat thử ít nhất 3 lượt, lưu lại
- [ ] Đổi khóa bot Telegram (khóa cũ đã lỡ lộ), thử gửi tin thật
- [ ] Hoàn thiện báo cáo nhóm và báo cáo cá nhân

## Mẫu cho lần ghi mới

```markdown
### vN — <tên ngắn>
- **Sửa file nào:**
- **Vì sao sửa:**
- **Đã làm:**
- **Kết quả:** X/20 lên Y/20
  - Tốt lên:
  - Vẫn sai hoặc mới sai:
- **Bài học:**
- **Việc tiếp theo:**
```
