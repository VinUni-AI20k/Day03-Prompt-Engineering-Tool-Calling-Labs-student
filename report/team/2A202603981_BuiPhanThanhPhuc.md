# Báo cáo cá nhân — BÙI PHAN THANH PHÚC - 2A202603981

## 1. Thông tin thành viên

- Họ tên: BÙI PHAN THANH PHÚC
- MSSV: 2A202603981
- Email: thanhphuccrkh@gmail.com

## 2. Phần việc phụ trách

Người 3 của nhóm anbatocom: bộ eval nhóm (C5), UI và live chat (C6), báo cáo nhóm Part A và Part B (C7).

## 3. Đóng góp cụ thể

- Bộ eval nhóm `starter_v0/data/eval_group.json`: 9 trên 10 case (5 single-turn, 4 multi-turn). Đã kiểm tra bằng loader của runner: không trùng ID, không sao chép từ `eval_base.json`. Case thứ 10 chờ tool mới của Người 2.
- UI Streamlit `starter_v0/app.py`: hiển thị tool call và lỗi tool trong expander, có nút xoá hội thoại.
- Báo cáo nhóm `report/team/group_report.md`, Part A: mô tả agent, bảng tool, câu hỏi mẫu.
- Part B, run v3 chính thức và transcript live chat: chưa làm, chờ v3 của Người 1.

## 4. Bằng chứng

- File/commit/PR:
  - `1059b6d` Add Part A of group report
  - `632eef9` Add 9 group eval cases
  - `58f47bf` Add Streamlit UI
  - `d89522c` Merge branch 'feature/streamlit-ui' (vào main)
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Claude (chat) hướng dẫn từng bước lệnh.
  - Tự kiểm tra: tự chạy từng lệnh trên máy và đọc output (pytest, preflight_provider, run_eval, git status, git log, git ls-files --eol). UI thử với OpenAI thật, lỗi tool hiện trong expander.

## 5. Tự đánh giá

[TỰ VIẾT]
