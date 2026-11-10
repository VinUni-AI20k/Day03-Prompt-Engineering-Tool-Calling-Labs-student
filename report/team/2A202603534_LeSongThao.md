# Báo cáo cá nhân — Lê Sông Thao — 2A202603534

## 1. Thông tin thành viên

- **Họ tên:** Lê Sông Thao.
- **MSSV:** 2A202603534.
- **Email:** sirothao123@gmail.com.
- **GitHub:** [lesongthao](https://github.com/lesongthao).
- **Phần việc phụ trách:** P1 và P5.

## 2. Phần việc phụ trách

| Gói | Mục tiêu | Phạm vi |
|---|---|---|
| P1 | Cho phép agent trả lời không dùng tool khi phù hợp và gọi nhiều tool khi cần nhiều nguồn | Snapshot prompt v1, chạy base eval, ghi version log và phân tích kết quả |
| P5 | Kiểm chứng và sửa lỗi các tool có sẵn | Test bắt lỗi, tám file tool và log pytest trước/sau sửa |

Các phần việc được tích hợp trên nền starter và mã dùng chung của nhóm. Báo cáo tập trung vào phạm vi tích hợp, kiểm chứng và phân tích của P1/P5.

## 3. Đóng góp cụ thể

### P1 — Prompt v1 và bằng chứng eval

Thay quy tắc “Always finish the request in a single step. Pick one tool” bằng hai hướng xử lý: trả lời trực tiếp khi không cần tool và gọi đủ các tool khi yêu cầu nhiều nguồn. Giữ nguyên khai báo tool của v0, phần hỏi lại khi thiếu thông tin và phần xác nhận trước khi gửi để các gói sau tiếp tục xử lý.

Chạy 20 case base bằng OpenRouter, model `openai/gpt-4o-mini`, rồi ghi kết quả từ run JSON vào version log:

| Chỉ số | Baseline v0 | P1 / v1 |
|---|---:|---:|
| Case PASS | 14/20 | 15/20 |
| Case accuracy | 0.70 | 0.75 |
| Lỗi provider | 0 | 0 |

Kết quả tăng **5 điểm phần trăm**. R08 và R14 chuyển FAIL → PASS. R13 đã gọi đủ `lookup` và `social_search` nhưng còn sai tham số nên vẫn FAIL. M06 chuyển PASS → FAIL do gọi thêm `social_search` khi chỉ cần `lookup`; R10/R11 và R12 còn lỗi thuộc phần hỏi lại/xác nhận gửi.

Vì vậy, giả thuyết P1 được hỗ trợ một phần; chưa thể kết luận thay đổi không gây regression. Những điểm này được ghi trong [nhận xét v1](../../starter_v0/analysis/notes_v1.md) để bàn giao cho các vòng tiếp theo.

### P5 — Kiểm thử trước, sửa lỗi sau

Tích hợp bộ 27 test P5, trong đó có 13 regression test cho 12 lỗi của tool có sẵn. Tổ chức thành hai commit để giữ bằng chứng trước và sau sửa:

| Trạng thái | FAIL | PASS | SKIP |
|---|---:|---:|---:|
| Trước sửa tool | 13 | 76 | 0 |
| Sau sửa tool | 0 | 89 | 0 |

Phần sửa tập trung ở `tools/_shared.py` và các tool `clarify`, `fetch`, `format`, `lookup`, `send`, `social_search`, `timeline`: kiểm tra xác nhận gửi dạng boolean, trả trạng thái chờ người dùng, tránh lộ token trong lỗi, xử lý Markdown lỗi, chuẩn hóa handle/limit/enum, kiểm tra URL và xử lý dữ liệu format chưa đúng kiểu.

Các test chạy offline, chặn HTTP thật và dùng dữ liệu/credential giả. P5 giữ nguyên prompt, khai báo tool, dữ liệu eval và run v0/v1. Bốn tool mới và 15 test bổ sung thuộc P6a được tách khỏi phạm vi P5.

## 4. Bằng chứng

### File, commit và PR

| Hạng mục | Bằng chứng |
|---|---|
| Snapshot v1 | [system_prompt.md](../../starter_v0/artifacts/versions/v1/system_prompt.md), [tools.yaml](../../starter_v0/artifacts/versions/v1/tools.yaml) |
| Run baseline v0 | [v0_B_base_openrouter_20261110T104242979050.json](../../starter_v0/runs/v0_B_base_openrouter_20261110T104242979050.json) |
| Run P1 / v1 | [v1_B_base_openrouter_20261110T145322191182.json](../../starter_v0/runs/v1_B_base_openrouter_20261110T145322191182.json) |
| Version log và nhận xét | [version_log.csv](../../starter_v0/artifacts/version_log.csv), [notes_v1.md](../../starter_v0/analysis/notes_v1.md) |
| Test P5 | [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py) — bộ test hiện tại còn được P6a bổ sung sau P5 |
| Log trước/sau sửa | [pytest_before_fix.txt](../../starter_v0/analysis/pytest_before_fix.txt), [pytest_after_fix.txt](../../starter_v0/analysis/pytest_after_fix.txt) |
| Commit P1 | [d47ed38 — prompt v1 và eval 0.75](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/commit/d47ed38fd918502eaad88ef979fa048a2f494b14) |
| Commit test P5 | [cacab35 — bổ sung test và tái hiện lỗi](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/commit/cacab3543c0dfb3a90da3214eff124ff64b30061) |
| Commit sửa P5 | [2a7280a — sửa lỗi và lưu kết quả kiểm chứng](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/commit/2a7280af49b149df85bd92d620722079e4ed3907) |
| PR đã được duyệt | [P1 — PR #7](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/pull/7), [P5 — PR #9](https://github.com/lesongthao/K5-L3A-DAY03-LeSongThao-2A202603534-ResearchAgentToolEval/pull/9) |

### AI/công cụ đã dùng và cách kiểm tra kết quả

- **Codex/ChatGPT:** hỗ trợ đọc mã, tổ chức thay đổi, thực thi lệnh, phân tích run log và đối chiếu kết quả. Các kết luận trong báo cáo dựa trên file bằng chứng, không lấy câu trả lời của AI thay cho kết quả chạy.
- **Git/GitHub:** tách nhánh theo gói, giới hạn file thay đổi, lưu commit và mở PR để kiểm tra trước khi merge.
- **OpenRouter và các API tool:** chạy eval P1 bằng model thật; API key chỉ lưu trong `.env` trên máy, không đưa vào commit.
- **pytest:** kiểm chứng P5 bằng cùng bộ test trước/sau sửa; fixture chặn mạng để test không phụ thuộc API thật.
- **Đối chiếu bằng chứng:** kiểm tra đủ 20 case và không có lỗi provider; đối chiếu hash prompt/tool với run JSON; tính lại PASS/FAIL từ lời gọi tool đã lưu; kiểm tra số liệu version log; rà soát diff và giá trị API key trước khi push.

## 5. Tự đánh giá

Tôi đánh giá kết quả hai gói phụ trách có thể truy vết được từ thay đổi code đến test/run, nhận xét và commit. P1 có cải thiện nhưng chưa đạt toàn bộ giả thuyết; việc ghi rõ cả R13 chưa PASS và M06 bị giảm kết quả giúp xác định đúng phần cần xử lý tiếp. P5 đạt tiêu chí kiểm thử trong phạm vi gói với 89 test PASS, không có FAIL hoặc SKIP sau sửa.

Điểm cần cải thiện là không chỉ nhìn điểm tổng mà phải kiểm tra từng case, tham số tool và các regression. Với prompt, agent có thể chọn đúng tool nhưng thiếu tham số tường minh; với action tool, phải kiểm tra cả giá trị xác nhận, trạng thái chờ và nhánh lỗi. Kết quả của một lượt eval cũng cần được xem trong bối cảnh cùng model, bộ case và phiên bản artifact.

Trước khi trình bày, tôi cần rà soát lại cách đọc run JSON, nguyên nhân từng test regression và luồng xác nhận của `send` để giải thích rõ bằng chứng của phần P1/P5. Hướng tiếp tục của nhóm là hoàn thiện các vòng hỏi lại/xác nhận gửi, xử lý tham số còn sai và kiểm tra lại các case hội thoại nhiều lượt.
