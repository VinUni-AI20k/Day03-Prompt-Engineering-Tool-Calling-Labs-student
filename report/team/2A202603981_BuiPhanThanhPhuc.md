# Báo cáo cá nhân — BÙI PHAN THANH PHÚC - 2A202603981

## 1. Thông tin thành viên

- Họ tên: BÙI PHAN THANH PHÚC
- MSSV: 2A202603981
- Email: thanhphuccrkh@gmail.com
- GitHub: `Jancaster1234`
- Vai trò trong nhóm: **Người 3 — Eval nhóm, UI, báo cáo** (rubric C5, C6, C7)

## 2. Phần việc phụ trách

Người 3 của nhóm anbatocom: bộ eval nhóm (C5), UI Streamlit (C6), báo cáo nhóm Part A (C7).

## 3. Đóng góp cụ thể

### Bộ eval nhóm (C5)

- Viết 9 trong 10 case của `starter_v0/data/eval_group.json`: G01–G05 (single turn) và GM01–GM04 (multi turn), commit `632eef9`. Phủ các hành vi: arg `topic`/`timeframe` (G01, GM01), `search_type`/`limit` (G02, GM02), không cần tool (G03), thiếu thông tin → `clarify` (G04), boundary gửi Telegram (G05, GM03, GM04).
- Kiểm tra bằng loader của runner (`load_cases`) trước khi push: 9 case, 5 single + 4 multi, không trùng ID, không sao chép từ `eval_base.json`.
- Case thứ 10 `GM05_keywords_from_pasted_text` (route tới tool mới `extract_keywords`) do Người 1 viết, không phải mình.
- Kết quả suite group v3 (10/10) nằm trong `starter_v0/runs/v3_B_group_openai_20261110T194452423053.json`, do Người 1 chạy.

### UI (C6)

- Viết `starter_v0/app.py` (Streamlit): chat gọi cùng vòng lặp tool với `chat.py` (`run_model_tool_loop`), hiển thị từng tool call và lỗi tool trong expander, có nút xoá hội thoại. Thêm `streamlit>=1.67.0` vào `requirements.txt`. Commit `58f47bf`, merge vào main bằng `d89522c`.
- Chạy thử cục bộ `streamlit run app.py`: trang tải được; khi chưa có API key, UI hiện thông báo lỗi provider thay vì crash.
- Sau đó Người 1 sửa `app.py` để provider đọc từ biến môi trường `UI_PROVIDER` (mặc định `openai`), thêm lệnh chạy UI và link Cloudflare Tunnel vào mục A1.
- Transcript live chat trong mục B4 của báo cáo nhóm do Người 1 chạy.

### Báo cáo nhóm (C7)

- Part A (commit `1059b6d`): A1 mô tả agent, A2 bảng 10 tool có sẵn, A3 câu hỏi mẫu. Người 1 sau đó bổ sung lệnh chạy UI, link dùng thử và dòng tool mới `extract_keywords` ở A2.
- Part B do Người 1 hoàn thiện (B1–B5a và các mục 3, 5, 7, 8); mình không viết phần này.

## 4. Bằng chứng

- **Commit (tác giả `Jancaster1234`):**
  - `1059b6d` — Add Part A of group report
  - `632eef9` — Add 9 group eval cases
  - `58f47bf` — Add Streamlit UI
  - `d89522c` — Merge branch 'feature/streamlit-ui' (vào main)
- **File:** `starter_v0/data/eval_group.json` (9 case của mình, case 10 của Người 1), `starter_v0/app.py`, `starter_v0/requirements.txt`, `report/team/group_report.md` (Part A).
- **Kiểm tra đã chạy:**
  - `pytest` trên bản clone ban đầu: 62 passed, 17 skipped, 0 failed.
  - Loader của runner trên `eval_group.json`: 9 case, 5 single + 4 multi, 0 trùng ID, 0 case chép từ base.
  - `streamlit run app.py`: trang tải được, lỗi thiếu key hiển thị trong chat.
  - Đọc `git diff` của commit Part A để xem nội dung thực tế đã push.
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Dùng Claude (chat). Claude hướng dẫn từng lệnh, và soạn nội dung 9 case eval (JSON), code `app.py` và văn bản Part A; mình dán vào file, chạy kiểm tra và commit.
  - Tự kiểm tra bằng các lệnh ở mục "Kiểm tra đã chạy" ở trên, và tự chạy từng lệnh trên máy, đọc output (pytest, preflight_provider, run_eval, git status, git log, git ls-files --eol). UI thử với OpenAI thật, lỗi tool hiện trong expander.

## 5. Tự đánh giá

- **Làm tốt:**
  - Kiểm tra trước khi push: nạp `eval_group.json` bằng loader của runner (9 case, 5 single + 4 multi, không trùng ID, không chép từ `eval_base.json`) và chạy `pytest` (62 passed, 17 skipped, 0 failed ở bản clone ban đầu).
  - UI hiện từng tool call và lỗi tool trong expander, nên lỗi tool không bị che.
  - Case nhóm phủ boundary gửi Telegram ở 3 dạng: chưa xác nhận (G05), đã xác nhận (GM03), hủy (GM04).
- **Chưa tốt:**
  - `app.py` của mình gán cứng provider `openrouter`, nên UI không chạy được với key OpenAI của nhóm cho đến khi Người 1 sửa ở `5ff50ee`. Lúc push mình mới thử khi chưa có API key.
  - Cả 10 case đều PASS ở v3, nên chưa case nào bắt được lỗi còn lại. R10 ở base (model tự chọn chủ đề "AI" khi yêu cầu tweet không có tài khoản/chủ đề) không có case tương ứng trong bộ nhóm.
  - Bằng chứng nhóm chỉ có 1 run group (v3), không có run group trên v0–v2, nên chưa biết case nào phân biệt được các version.
  - Live chat và Part B do Người 1 làm; case GM05 cũng do Người 1 viết.
- **Bài học:** case `no_tool` (G03, GM04) chỉ chứng minh model không gọi tool, không chứng minh câu trả lời text đúng. Bộ eval toàn PASS xác nhận hành vi đã sửa, chứ không đo được lỗi còn sót.
- **Nếu làm lại:**
  - Đổi một case trong bộ 10 (phải đúng 10) thành "Tóm tắt 5 tweet mới nhất" không kèm tài khoản/chủ đề, kỳ vọng `clarify`, để đo đúng lỗi R10.
  - Chạy suite group trên cả v0–v3.
  - Hỏi Người 2 tên và args tool mới từ sớm để tự viết case route tới tool mới.
  - Đọc provider từ biến môi trường ngay từ bản đầu của `app.py`.
