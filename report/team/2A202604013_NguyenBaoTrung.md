# Báo cáo cá nhân — 2A202604013_NguyenBaoTrung

## 1. Thông tin thành viên

- Họ tên: Nguyễn Bảo Trung
- MSSV: 2A202604013
- Email: nbtrungrhm@gmail.com
- Nhóm: Ban5 (Lớp L3B)

## 2. Phần việc phụ trách

- Xây dựng bộ test case đánh giá cho nhóm (`starter_v0/data/eval_group.json`) bao gồm cả single-turn và multi-turn.
- Phân tích nguyên nhân lỗi (Failure Analysis) của bản chạy baseline v0 và xây dựng giải pháp khắc phục (Bảng B2).
- Viết tài liệu giới thiệu agent (Phần A), hoàn thiện danh mục tool và soạn thảo các câu hỏi mẫu kiểm thử (A1, A2, A3).
- Cập nhật số liệu thực nghiệm v0, v1, v2 vào các bảng B1, B3, B5a trong báo cáo nhóm.
- Quản lý đồng bộ git, xử lý merge conflict và tích hợp mã nguồn từ các thành viên trong nhóm (QuanNH, DucLT).

## 3. Đóng góp cụ thể

- **Thiết kế 10 test case nhóm (`eval_group.json`):**
  - 5 case single-turn: kiểm tra thiếu thông tin gọi `clarify`, kiểm tra cơ chế Human-in-the-Loop xin duyệt trước khi `send`, kiểm tra định tuyến tìm kiếm bài báo arXiv (`papers`), kiểm tra Guardrail từ chối tác vụ viết code (`no_tool: true`), và kiểm tra gọi tool mới `stats` của DucLT.
  - 5 case multi-turn: kiểm tra hỏi lại sau đó cung cấp đủ thông tin, kiểm tra sau khi user duyệt "đồng ý" thì thực sự gọi `send`, kiểm tra chuyển đổi tool từ Twitter sang web search giữ nguyên chủ đề, kiểm tra đính chính từ nghỉ phép sang báo ốm trong `policy`, và kiểm tra bài toán chia tiền logic không gọi tool thừa (`no_tool: true`).
- **Phân tích lỗi baseline v0:** Rà soát và phân loại 7 case FAIL trong log `v0.csv`, chỉ ra lỗi suy đoán mù khi thiếu input, lỗi gọi thẳng `send` khi chưa được duyệt, và lỗi gọi tool ngoài phạm vi.
- **Tích hợp và kiểm thử:** Hợp nhất tool mới `stats` cùng 17 unit tests offline của DucLT vào nhánh làm việc, chạy toàn bộ test suite đạt **104 passed, 0 failed, 0 skipped**.

## 4. Bằng chứng

- **File / commit / PR:**
  - `starter_v0/data/eval_group.json`: Thiết kế 10 test cases nhóm (commit `0cdeb72`).
  - `report/team/group_report.md`: Hoàn thiện Phần A, Bảng B1, B2, B3, B5a (commit `c35c322`, `0cdeb72`).
  - `tasks/TrungNB.md` & `TEAM.md`: Cập nhật checklist và thông tin thành viên (commit `fa5c001`, `c35c322`).
  - Merge nhánh `origin/main` và `origin/feat/DucLT-tool-tests`: commit `fa5c001`, `7618298`, `b788f27`.
- **AI / công cụ đã dùng và cách tự kiểm tra kết quả:**
  - **Công cụ AI:** Google Antigravity Agent (Gemini 3.8 Flash High) đóng vai trò trợ lý lập trình cặp (pair programming) theo phương thức tương tác hỏi - đáp từng bước (không tự ý sinh mã bừa bãi, sinh viên quyết định từng nội dung kỹ thuật).
  - **Nội dung thực tế đã làm việc cùng AI:**
    1. *Xử lý conflict Git:* AI hỗ trợ phân tích nguyên nhân conflict duy nhất ở file `TEAM.md` khi merge `origin/main` (do cả 2 bên cùng sửa bảng thành viên và URL repo), sau đó thực hiện giải quyết conflict giữ trọn vẹn thông tin 3 thành viên và mục cá nhân.
    2. *Phân tích 7 case lỗi baseline v0 (Bảng B2):* Rà soát log `v0.csv`. Sinh viên đưa ra định hướng xử lý và AI hỗ trợ chuẩn hóa giải pháp kỹ thuật:
       - Bổ sung rule chặn khi thiếu input bắt buộc, ép gọi `clarify` (`R10`, `R11`).
       - Áp dụng cơ chế Human-in-the-Loop (HITL) xin duyệt trước khi gọi tool ghi `send` (`R12`).
       - Thiết lập Guardrail từ chối tác vụ lập trình/ngoài lề, trả lời trực tiếp `no_tool` (`R08`, `R14`).
       - Phân lập rõ nhiệm vụ của `timeline` (theo user) và `social_search` (theo chủ đề), trích xuất query chuẩn theo intention không chèn thêm từ suy đoán (`R03`, `R13`).
    3. *Xây dựng Phần A báo cáo nhóm:* Thảo luận và chốt mô tả agent (nghiên cứu thị trường qua web, Twitter, arXiv, policy), ghi nhận lệnh chạy CLI và 4 câu hỏi mẫu kiểm thử.
    4. *Thiết kế 10 test case trong `data/eval_group.json`:* Đi qua từng case theo ý tưởng thực tế của sinh viên (case thiếu chủ đề arXiv, duyệt Telegram, tra cứu paper, từ chối code Fibonacci, tính chi phí trung bình bằng tool `stats`, chuyển tool Twitter sang web, đính chính nghỉ phép sang báo ốm, và case chia tiền không gọi tool).
    5. *Tích hợp nhánh nhóm:* Merge nhánh `feat/DucLT-tool-tests` (tool `stats` và 17 test offline) và đồng bộ kết quả chạy v1, v2 (đạt 90% accuracy) của bạn Quân.
  - **Cách tự kiểm tra kết quả (Verification):**
    - Dùng script Python `json.load()` kiểm tra tính toàn vẹn và cú pháp của file `data/eval_group.json` (đạt 10/10 case hợp lệ).
    - Chạy lệnh test `.venv/bin/pytest -q` kiểm tra toàn bộ tool contract: **104 passed, 0 failed, 0 skipped**.
    - Kiểm tra `git status` và `git diff` trước và sau mỗi lần commit đảm bảo không rò rỉ key `.env` và code sạch sẽ.

## 5. Tự đánh giá

- Hoàn thành đầy đủ 100% các đầu việc được phân công đúng thời hạn và đảm bảo chất lượng kỹ thuật.
- Đánh giá đóng góp: Hoàn thành tốt nhiệm vụ (mức A).
