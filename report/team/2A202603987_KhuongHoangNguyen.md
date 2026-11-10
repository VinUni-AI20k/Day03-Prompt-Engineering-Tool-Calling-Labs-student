# Báo cáo cá nhân — KhuongHoangNguyen-2A202603987

## 1. Thông tin thành viên

- Họ tên: Khương Hoàng Nguyên
- MSSV: 2A202603987
- Email: 26ai.nguyenkh@vinuni.edu.vn

## 2. Phần việc phụ trách

- **CP3 — Unit test:** viết hết 14 stub TODO trong `tests/test_tools_todo.py`, thêm test mới, tìm và sửa bug trong tool có sẵn (regression test).
- **CP4 — Eval nhóm:** hoàn thiện `data/eval_group.json` đủ 10 case (5 single + 5 multi turn) và chạy `--suite group`.
- **CP5 — Live chat và báo cáo:** chạy `chat.py` có transcript; viết Phần A, B3, B4, B5a, B5, B7, mục 5 và 7 của `group_report.md`; điền `TEAM.md`.
- **Bonus:** `send` gửi Telegram thật sau khi user xác nhận; Small Local Model Challenge (Ollama).

## 3. Đóng góp cụ thể

1. **Test challenge (CP3):** viết 14 stub TODO (clarify, format, send, lookup, fetch, timeline, social_search, policy). Test nào cũng assert cả request gửi đi lẫn kết quả trả về, và chạy offline bằng `fake_http`. Test injection của `policy` tự tìm dòng `>` trong file policy thay vì hard-code. Thêm 3 test cho tool mới của nhóm: `text_stats` làm tròn thời gian đọc, `date_diff` nhận sai kiểu, `dedupe` theo title. Kết quả `pytest`: **109 passed, 0 failed, 0 skipped**.
2. **Tìm và sửa 3 bug trong tool có sẵn**, mỗi bug có regression test. Mình đã kiểm tra: các test này FAIL trên code gốc và PASS sau khi sửa.
   - `send`: code gốc dùng `if not confirmed`, nên chuỗi `"false"` được coi là đã xác nhận và tool **gửi thật**. Sửa bằng `_is_confirmed()` kiểm tra chặt.
   - `send`: text rỗng giờ trả error dict, không gọi mạng. Khi Telegram trả 400 vì Markdown, tool gửi lại dạng plain text. Khi mạng reset kết nối (lỗi 10054 gặp trong live chat), tool thử lại 1 lần. Trả thêm `message_id` để làm bằng chứng.
   - `timeline`: bỏ `@` ở đầu handle; handle rỗng thì trả error dict.
3. **Eval nhóm (CP4):** thêm 7 case G04–G10: papers args, user ép gửi không hỏi, multi turn clarify → `date_diff`, xác nhận → `send`, từ chối → `no_tool`, đổi `timeline` sang `social_search` Top, papers → `paper_text`. Chạy v3 trên OpenRouter được **10/10** (`provider_error_cases = 0`).
4. **Live chat + Telegram thật:** mình tự gõ tay 2 phiên: thiếu tài khoản → `clarify` → bổ sung → `timeline(elonmusk, limit=3)`; và đăng Telegram → `clarify(yes_no)` → "Có, gửi đi" → `send(confirmed=true)` → `status: sent` (`message_id: 8`). Thêm một transcript 5 lượt chạy bằng input soạn sẵn, gồm thiếu URL → hỏi lại → bổ sung → `fetch`, tin AI hôm nay → `lookup`, rồi `clarify(yes_no)` → "Có, gửi đi" → `send(confirmed=true)` → `status: sent`. Mình giữ lại 2 transcript lỗi làm bằng chứng: agent tự chọn URL khi user nói "bài này", và `send` bị reset mạng.
5. **Small Local Model (bonus):** chạy base eval v3 trên `qwen2.5:7b` (0.75) và `llama3.2:3b` (0.15). Với llama, run gốc bị treo do lặp token nên không hợp lệ; mình tạo biến thể `num_predict 512` qua Modelfile. Mình viết `scripts/local_failure_patterns.py` để đếm lỗi đặc thù của model nhỏ. Sau đó tối ưu 3 vòng, mỗi vòng một giả thuyết: v4 prompt ngắn + few-shot, v5 chỉ giữ 7 tool ngắn có enum, v6 bỏ cú pháp `tool(args)` khỏi ví dụ. Kết quả: llama 0.15 → 0.40 → 0.50 → 0.50; qwen 0.75 (v3) → 0.65 → 0.55 → 0.70, tức vẫn thấp hơn v3. Kiểm tra ngược bản v6 trên cloud: 0.95 → 0.85. Kết luận chính: few-shot giúp model 3B, nhưng ví dụ viết theo cú pháp giống code làm model 7B in lời gọi tool ra text. Chi tiết ở B7 của group report.

## 4. Bằng chứng

- File/commit/PR:
  - Code + test: `starter_v0/tests/test_tools_todo.py`, `starter_v0/tools/send/tool.py`, `starter_v0/tools/timeline/tool.py`
  - Eval nhóm: `starter_v0/data/eval_group.json`, `starter_v0/runs/v3_B_group_openrouter_20261111T000138322901.json`
  - Transcript Telegram (bằng chứng chính, phiên gõ tay): `starter_v0/transcripts/v3_openrouter_20261111T012155901977.transcript.json`: turn 1 `clarify(yes_no)` → turn 2 "Có, gửi đi" → `send(confirmed=true)` → `status: sent`, `message_id: 8`; turn 3 yêu cầu thường → `timeline(screenname="elonmusk")`
  - Transcript "thiếu thông tin rồi bổ sung" (phiên gõ tay): `starter_v0/transcripts/v3_openrouter_20261111T013659009272.transcript.json`: `clarify(text)` → "tài khoản elon musk" → `timeline(screenname="elonmusk", limit=3)`
  - Transcript khác: `…000512368617…` (đủ 5 lượt: thiếu URL → bổ sung → tin AI → gửi Telegram, `message_id: 6`), `…000200284279…`, `…000258204579…` (lỗi được giữ lại)
  - Local model: `starter_v0/runs/v3-qwen7b_*`, `v3-llama3b_*`, `v4-local-*`, `v5-local-*`, `v6-local-*` (gồm `v6-local-cloud`); `artifacts/system_prompt_local.md` + `tools_local.yaml` (v6), `system_prompt_local_v4v5.md` + `tools_local_v5.yaml` (v4/v5, hash khớp run); `artifacts/Modelfile.llama3b-np512`; `scripts/local_failure_patterns.py`; 11 dòng mới trong `artifacts/version_log.csv`
  - Báo cáo: `report/team/group_report.md` (Phần A, B3–B7, mục 5, 7), `TEAM.md`, checklist trong `README.md`
  - Commit: nhánh `feat/eval`
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Dùng Claude Code (AI coding assistant) để đọc repo, viết test/case và soạn báo cáo.
  - Tự kiểm tra: chạy `pytest` toàn suite; chạy regression test trên code gốc (`git show HEAD:…`) để chắc test thật sự bắt được bug; chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`; mọi số liệu trong báo cáo đọc trực tiếp từ run JSON/transcript; kiểm tra transcript không chứa token Telegram.

## 5. Tự đánh giá

- **Làm tốt:** suite test đạt 0 skipped và tìm được bug thật trong `send`: chuỗi `"false"` làm phá boundary xác nhận, eval không thể phát hiện. Luồng Telegram có bằng chứng thật. Mình báo cáo trung thực cả những lần lỗi.
- **Chưa làm / hạn chế:** Bộ group đạt 10/10 nên chưa đủ khó để phân biệt các version. Nhóm mới có 3 tool mới, chưa đạt bonus ≥ 4 tool.
- **Bài học:** unit test đo code của tool, eval đo lựa chọn của model, và hai loại test bắt các lỗi khác nhau. Eval một lượt cũng không thấy lỗi phụ thuộc lịch sử chat; phải đọc transcript mới thấy.
