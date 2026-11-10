# Kiểm tra gói nộp NoName

- [x] Provider/model thật: OpenRouter, Nemotron 3 Ultra free.
- [x] Ít nhất 5 tool: hiện có 11, UI nghiên cứu dùng 10 (không bật send).
- [x] v0, v1, v2 gốc giữ nguyên; snapshot prompt/tool khớp SHA256.
- [x] v3 mới: base 19/20; giữ nguyên bộ đề base.
- [x] 10 case nhóm: 5 single-turn, 5 multi-turn; run cuối đạt 10/10.
- [x] Tool mới deduplicate: tool.py, TOOL.md, registry và declaration.
- [x] Test thành công, input sai, failure handling cho tool mới.
- [x] Toàn bộ pytest: 94 passed, 0 failed, 0 skipped.
- [x] UI Streamlit chạy thật, có link demo tạm thời trong REPORT.md.
- [x] Kiểm tra UI render và chat thật bằng AppTest, health public ok.
- [x] Transcript CLI có 3 lượt model thật, status answered.
- [x] REPORT.md phần A và B, version_log.csv, run JSON, analysis CSV.
- [x] Manifest bằng chứng, hướng dẫn cài đặt/chạy và script đóng gói.
- [x] Script đóng gói loại .env, venv, secrets.toml và kiểm tra key đã cấu hình.
- [x] Đã điền đủ tên và mã học viên của 3 thành viên nhóm trong REPORT.md.

Trước buổi demo: mở lại link public để chắc chắn máy, Streamlit và cloudflared
vẫn đang chạy. Nếu tunnel đã tắt, tạo link mới và cập nhật REPORT.md.
Không yêu cầu base eval 100%; R12 chưa đạt được phân tích đầy đủ trong báo cáo.
Không tuyên bố đạt bonus model local, >3 tool mới hay gửi Telegram thật.
