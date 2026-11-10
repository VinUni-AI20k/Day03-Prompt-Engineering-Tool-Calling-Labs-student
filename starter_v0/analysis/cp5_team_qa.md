# CP5 — kiểm tra trên main của nhóm

Thực hiện 11/11/2026 (GMT+7), nền main GitHub `a557a55`. Bản thử nghiệm local trước đó được giữ riêng trong Git stash `backup-ui-local-before-team-main-2026-11-11`.

## Cấu hình kiểm tra

- Python 3.13.9; Streamlit 1.67.0; OpenAI / gpt-4o-mini.
- UI dùng `chat.py` và đủ **14 tool**, gồm 4 tool của Hà Anh. Không sửa `chat.py`, provider, code/registry tool, prompt, declaration hoặc base/group/extension của nhóm.
- Prompt SHA-256: `0d8d6477582f99aefd48c1b69a0527d133701fcf5112fd13f4affbe4e11b38d1`.
- Tools SHA-256: `835122e4256998446c166a8403490b94ec250f5becd413ec1e696d5ffaafbfee`.
- Hai hash khớp run CP4; snapshot đúng byte ở `artifacts/versions/cp5-team/`.

## Kiểm tra và bằng chứng

| Kiểm tra | Kết quả | Bằng chứng |
|---|---|---|
| Toàn suite pytest offline | **102 passed, 14 skipped, 0 failed** | [output](cp5_team_pytest.txt); 5 bài UI/support mới |
| Type check | `venv/Scripts/ty.exe check --python venv/Scripts/python.exe starter_v0/app.py starter_v0/ui_support.py` → All checks passed | lệnh chạy thực tế; không suy ra cả repo đã type check |
| Base, 14 tool | **17/20**, routing 95%, args 85%, multi 83.33%; 0 provider errors | [run](../runs/cp5-team_B_base_openai_20261111T004229851343.json) |
| Group của Nghĩa | **10/10**, đủ measured, 0 provider errors | [run](../runs/cp5-team_B_group_openai_20261111T004229756879.json) |
| CLI live | 5 lượt; github_search, clarify(text), timeline, clarify(yes_no), hủy không send | [transcript](../transcripts/cp5-team-live_openai_20261111T004205700741.transcript.json), [output](cp5_team_cli_live.txt) |
| UI runtime | Health ok, đăng nhập mã demo, 14 tool, dedup 2→1, compare_sources chạy thật, download JSON 3 lượt trả HTTP 200, reset về 0 tin nhắn | [transcript UI](../transcripts/cp5-team-ui_5133d9521b474828bbe6b38e8acc442f.transcript.json) |
| Link public | HTTP 200; `/_stcore/agent/openapi.json` ghi agent API disabled | https://writing-what-vat-dedicated.trycloudflare.com; kiểm tra lúc hoàn thiện CP5 |

AppTest dùng fake provider: kiểm tra clarify/history theo session, schema strategy của dedup trên main, lỗi provider được che credential khi lưu/download, giới hạn và đổi hash, reset không xóa transcript cũ, gate mã demo. HTTP thật vẫn bị fixture chặn. QA runtime dùng API/tool thật trên localhost:8766; không phải AppTest. Console server QA không có traceback hoặc cảnh báo mới.

## Giới hạn và phần cần người thực hiện

- Base còn R10 (`social_search` query rỗng thay clarify), R12 (`text` thay `yes_no`) và M03 (handle `andrejkarpathy` thay `karpathy`), giống regression đã ghi ở v3. CP5 giữ nguyên cấu hình nhóm, không tuyên bố đã sửa những lỗi này.
- UI live đôi khi model tự trả lời bằng tiếng Anh hoặc xử lý danh sách bằng lời thay vì gọi tool. Câu yêu cầu filter_by_date ở lượt 2 UI không gọi tool; không coi là tool đã chạy. Đây là hành vi model trên prompt main, không phải lỗi bị UI che.
- 14 skipped là challenge tùy chọn của starter; không claim bonus test challenge. Chưa có ≥2 model local hoặc Telegram gửi thật.
- Các run đo routing/args, không bảo đảm tool không có lỗi hoặc mọi fact/nguồn đều đúng. Case group G09 PASS routing dù send trả lỗi thiếu key. Bộ group không kiểm tra đầy đủ items đầu vào của mọi tool.
- Kịch bản CLI do Codex tự nhập, có API/tool thật. Chưa có người ngoài nhóm xác nhận dùng thử; cần thực hiện trước khi chốt nộp.
- Public quick tunnel tạm, phụ thuộc máy host và các tiến trình. Mã demo ở `.runtime/team-demo-access.txt`, không commit. Chưa kiểm tra trên nhiều thiết bị/trình duyệt; QA runtime không thay kiểm tra hiển thị trực quan.
- Bình cần tự review/giải thích phần được AI hỗ trợ. Không có bằng chứng Phần A hoàn thành trước showdown 16:30. Việc chấp nhận thời gian nộp theo quy định/coach.
