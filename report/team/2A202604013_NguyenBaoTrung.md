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
  - Công cụ AI: Google Antigravity Agent (Gemini 3.8 Flash High) hỗ trợ phân tích log thực nghiệm, rà soát schema test case và đối chiếu các tiêu chí trong rubric.
  - Tự kiểm tra kết quả: Kiểm tra cú pháp JSON bằng script Python `json.load()`; chạy kiểm thử toàn bộ test suite bằng `pytest` đạt 104/104 passed; đối chiếu từng case với allowed failure types của đề bài.

## 5. Tự đánh giá

- Hoàn thành đầy đủ 100% các đầu việc được phân công đúng thời hạn và đảm bảo chất lượng kỹ thuật.
- Đánh giá đóng góp: Hoàn thành tốt nhiệm vụ (mức A).
