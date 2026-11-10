# Báo cáo cá nhân — Bùi Phan Thanh Phúc - 2A202603981

## 1. Thông tin thành viên

- Họ tên: Bùi Phan Thanh Phúc
- MSSV: 2A202603981
- Email: thanhphuccrkh@gmail.com
- GitHub: `Jancaster1234`
- Vai trò trong nhóm: Eval nhóm, UI Streamlit, báo cáo nhóm Phần A (rubric C5, C6, C7)

## 2. Phần việc phụ trách

Bộ eval nhóm (C5), UI Streamlit (C6), báo cáo nhóm Phần A (C7).

## 3. Đóng góp cụ thể

### Bộ eval nhóm (C5)

- Viết 9 trong 10 case của `starter_v0/data/eval_group.json`: G01–G05 (single turn) và GM01–GM04 (multi turn), commit `632eef9`. Phủ các hành vi: arg `topic`/`timeframe` (G01, GM01), `search_type`/`limit` (G02, GM02), không cần tool (G03), thiếu thông tin → `clarify` (G04), boundary gửi Telegram (G05, GM03, GM04).
- Kiểm tra bằng loader của runner (`load_cases`) trước khi push: 9 case (trước khi thêm GM05), 5 single + 4 multi, 0 trùng ID, 0 case chép từ `eval_base.json`.
- Case thứ 10 `GM05_keywords_from_pasted_text` (route tới tool mới `extract_keywords`) do Dư Văn Hùng viết.
- Kết quả suite group v3 (10/10) nằm trong `starter_v0/runs/v3_B_group_openai_20261110T194452423053.json`, do Dư Văn Hùng chạy.

### UI (C6)

- Viết `starter_v0/app.py` (Streamlit): chat gọi cùng vòng lặp tool với `chat.py` (`run_model_tool_loop`), hiển thị từng tool call và lỗi tool trong expander, có nút xoá hội thoại. Thêm `streamlit>=1.67.0` vào `requirements.txt`. Commit `58f47bf`, merge vào main bằng `d89522c`.
- Chạy thử cục bộ `streamlit run app.py` khi chưa có API key: trang tải được, UI hiện thông báo lỗi provider thay vì crash.
- `app.py` bản đầu gán cứng provider `openrouter`. Mình test UI với OpenAI thật và push lên nhánh riêng. Nhánh này không được merge vì Dư Văn Hùng đã sửa và push `app.py` lên main trước (`5ff50ee`: provider đọc từ biến môi trường `UI_PROVIDER`, mặc định `openai`), cùng lệnh chạy UI và link Cloudflare Tunnel ở mục A1.
- Transcript live chat (mục B4 của báo cáo nhóm) do Dư Văn Hùng chạy.

### Báo cáo nhóm (C7)

- Part A (commit `1059b6d`): A1 mô tả agent, A2 bảng 10 tool có sẵn, A3 câu hỏi mẫu. Dư Văn Hùng sau đó bổ sung lệnh chạy UI, link dùng thử và dòng tool mới `extract_keywords` (của Hoàng Ngọc Hiệu) ở A2.
- Part B do Dư Văn Hùng hoàn thiện; mình không viết phần này.

## 4. Bằng chứng

- **Commit (tác giả `Jancaster1234`):**
  - `1059b6d` — Add Part A of group report
  - `632eef9` — Add 9 group eval cases
  - `58f47bf` — Add Streamlit UI
  - `d89522c` — Merge branch 'feature/streamlit-ui' (vào main)
- **File:** `starter_v0/data/eval_group.json` (9 case của mình, case 10 của Dư Văn Hùng), `starter_v0/app.py`, `starter_v0/requirements.txt`, `report/team/group_report.md` (Part A).
- **Kiểm tra đã chạy:**
  - `pytest` trên bản clone ban đầu: 62 passed, 17 skipped, 0 failed.
  - Loader của runner trên `eval_group.json`: 9 case (trước khi thêm GM05), 5 single + 4 multi, 0 trùng ID, 0 case chép từ base.
  - `streamlit run app.py` khi chưa có API key: trang tải được, lỗi thiếu key hiển thị trong chat.
  - UI thử với OpenAI thật (nhánh riêng, không merge), lỗi tool hiện trong expander.
  - Đọc `git diff` của commit Part A để xem nội dung thực tế đã push.
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Dùng Claude (chat). Claude hướng dẫn từng lệnh, soạn nội dung 9 case eval (JSON), code `app.py` và văn bản Part A; mình dán vào file, chạy kiểm tra và commit.
  - Tự kiểm tra bằng các lệnh ở mục "Kiểm tra đã chạy", và tự chạy các lệnh `pytest`, `preflight_provider`, `git status`, `git log`, `git ls-files --eol`, đọc output.

## 5. Tự đánh giá

- **Làm tốt:**
  - Kiểm tra trước khi push: nạp `eval_group.json` bằng loader của runner (9 case, 5 single + 4 multi, không trùng ID, không chép từ `eval_base.json`) và chạy `pytest` (62 passed, 17 skipped, 0 failed ở bản clone ban đầu).
  - UI hiện từng tool call và lỗi tool trong expander, nên lỗi tool không bị che.
  - Case nhóm phủ boundary gửi Telegram ở 3 dạng: chưa xác nhận (G05), đã xác nhận (GM03), hủy (GM04).
- **Chưa tốt:**
  - `app.py` bản đầu của mình gán cứng provider `openrouter`, nên UI không chạy được với key OpenAI của nhóm. Lúc push mình mới thử khi chưa có API key; sau đó mới test với OpenAI thật, nhưng nhánh đó không được merge vì Dư Văn Hùng đã push bản sửa lên main trước (`5ff50ee`).
  - Cả 10 case đều PASS ở v3, nên chưa case nào bắt được lỗi còn lại. R10 ở base (model tự chọn chủ đề "AI" khi yêu cầu tweet không có tài khoản/chủ đề) không có case tương ứng trong bộ nhóm.
  - Báo cáo nhóm chỉ trích run group v3. Trong `runs/` còn có run group v2 (`v2_B_group_…`) nhưng chưa được phân tích, nên chưa biết case nào phân biệt được v2 và v3.
  - Live chat và Part B do Dư Văn Hùng làm; case GM05 cũng do Dư Văn Hùng viết.
- **Bài học:** case `no_tool` (G03, GM04) chỉ chứng minh model không gọi tool, không chứng minh câu trả lời text đúng. Bộ eval toàn PASS xác nhận hành vi đã sửa, chứ không đo được lỗi còn sót.
- **Nếu làm lại:**
  - Đổi một case trong bộ 10 (phải đúng 10) thành "Tóm tắt 5 tweet mới nhất" không kèm tài khoản/chủ đề, kỳ vọng `clarify`, để đo đúng lỗi R10.
  - Chạy và phân tích suite group trên cả v0–v3.
  - Hỏi Hoàng Ngọc Hiệu tên và args tool mới từ sớm để tự viết case route tới tool mới.
  - Đọc provider từ biến môi trường ngay từ bản đầu của `app.py`.
