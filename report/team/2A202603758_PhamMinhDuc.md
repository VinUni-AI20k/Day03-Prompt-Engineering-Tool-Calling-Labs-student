# Báo cáo cá nhân — Phạm Minh Đức (2A202603758)

## 1. Thông tin thành viên

- Họ tên: Phạm Minh Đức
- MSSV: 2A202603758
- Email: 26ai.ducpm@vinuni.edu.vn

## 2. Phần việc phụ trách

- CP4–CP5: rà soát và tăng độ bền của lưu transcript; thêm regression test cho chat CLI dùng chung với UI.

## 3. Đóng góp cụ thể

- Rà soát `write_transcript()` và phát hiện việc ghi trực tiếp vào file đích có thể để lại JSON không hoàn chỉnh nếu bị ngắt giữa lúc lưu.
- Sửa lưu transcript theo cơ chế ghi JSON vào file tạm rồi thay thế file đích.
- Thêm hai regression test offline cho phản hồi thành công và lỗi provider, xác nhận trạng thái turn được ghi lại và file tạm được dọn.
- UI/transcript ban đầu đã có trước commit này; phần đóng góp của tôi là hardening lưu transcript và kiểm thử, không nhận phần triển khai UI ban đầu.

## 4. Bằng chứng

- Thay đổi kỹ thuật: `starter_v0/chat.py`; regression tests: `starter_v0/tests/test_chat_transcripts.py`.
- Commit: [`64a8fb1`](https://github.com/Ngochung1772k4/K5-L3B-DAY03-H7-ResearchAgentToolEval/commit/64a8fb1), trên nhánh `feature/2a202603758-phamminhduc-cp4-5`, là con trực tiếp của `df4fe42`; đã fast-forward merge vào nhánh `feature/2a202603770-buingochung-cp1-2` ở local, push đang chờ.
- Kiểm tra tại máy của tôi lúc tạo commit: `py_compile` và `git diff --check` pass; `pytest` chưa chạy được do môi trường Python thiếu `pytest`. Sau khi merge, toàn bộ suite chạy tại máy Hùng: **165 passed, 0 failed** (gồm cả hai regression test này).
- Hướng dẫn chạy: từ `starter_v0`, chạy `.\.venv\Scripts\python.exe -m streamlit run app.py`.
- Báo cáo nhóm: mục B4/B5a trong `report/team/group_report.md` ghi rõ transcript UI/CLI và các giới hạn.
- AI/công cụ: dùng AI hỗ trợ rà soát và soạn nháp; tự xem lại logic ghi file và test fake provider trước khi commit.

## 5. Tự đánh giá

Đóng góp của tôi bổ sung kiểm thử cho lưu transcript thành công và lỗi provider, cùng cơ chế thay file an toàn hơn. UI/transcript ban đầu do Bùi Ngọc Hùng triển khai. Commit `64a8fb1` hiện ở nhánh riêng, nên cần merge vào nhánh nộp để xuất hiện trong lịch sử commit của bài nộp. Link demo public vẫn chưa có.
