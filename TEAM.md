# Team — agentcuibap

## Thông tin nhóm

- Tên nhóm: **agentcuibap**.
- Lớp: **L3B** — khóa K5, Day 03 Research Agent Tool Eval.
- Repo nhóm: `K5-L3B-DAY03-agentcuibap-ResearchAgentToolEval`.
- URL repo:
- Nhánh chuẩn bị bài nộp: `main`.
- Commit chốt kỹ thuật và bằng chứng:
- Báo cáo nhóm: [group_report.md](report/team/group_report.md).

## Thành viên và phân công

| STT | Họ tên | MSSV | Email | GitHub | Trách nhiệm chính | Tỷ trọng phân công |
| --: | --- | --- | --- | --- | --- | ---: |
| 1 | Đinh Phúc Diên | | | | Baseline, tối ưu prompt/tool contract, phân tích version | 1/3 |
| 2 | Đào Văn Hiệp | | | | Tool `research_board`, contract, xử lý lỗi và unit test | 1/3 |
| 3 | Lê Nguyễn Anh Nhân | | | | Eval nhóm, UI/live chat, pipeline và tích hợp báo cáo | 1/3 |

Tỷ trọng trên là phân bổ trách nhiệm, không phải số giờ hoặc tỷ lệ commit đã đo. Mỗi người nhận ba gói việc cùng trách nhiệm kiểm tra chéo. Báo cáo được tổng hợp với hỗ trợ Codex từ code/run/test thật; bảng này không thay thế bằng chứng commit kỹ thuật của từng thành viên.

| Gói việc | Đinh Phúc Diên | Đào Văn Hiệp | Lê Nguyễn Anh Nhân |
| --- | --- | --- | --- |
| 1 — Thiết kế và triển khai | CP1: đọc yêu cầu, kiểm tra Groq/baseline; CP2: giải thích giả thuyết v1–v4, sửa prompt và tool description theo từng vòng | CP3: triển khai `research_board`, chuẩn hóa/gộp URL, nhóm domain, provenance, comparison và graph; đồng bộ `TOOL.md`/registry/YAML | CP4: thiết kế 10 case gốc, 5 single + 5 multi; kiểm tra schema và case route tới tool mới |
| 2 — Thực nghiệm và kiểm thử | Đối chiếu hash/snapshot, run v0–v4 và version log; phân tích lỗi, hồi quy và giới hạn điểm tự động | Kiểm tra happy path, input xấu, thiếu key/HTTP 429; partial/skipped, giới hạn request và error dict; giữ contract test xanh | CP5: tích hợp chat/research desk/UI pipeline, transcript, xác nhận và public read-only; kiểm tra AppTest và tunnel |
| 3 — Báo cáo và nghiệm thu | Tổng hợp B1/B2, giải thích khác biệt `system_prompt.md`/`tools.yaml`; kiểm tra chéo tính nguyên gốc/expect của eval nhóm | Tổng hợp B5a và giới hạn nguồn/overlap; kiểm tra chéo trace/lỗi UI, redaction và cơ chế chặn gửi | Tổng hợp Phần A/B3/B4, liên kết bằng chứng, checklist và commit chốt; kiểm tra chéo hash/version và kết quả pytest |

## Đinh Phúc Diên — trách nhiệm và bằng chứng

- Báo cáo cá nhân: `MSSV_DinhPhucDien.md` — chờ thành viên bổ sung.
- Giải thích được: tại sao v1 hỏi lại, v2 yêu cầu xác nhận, v3 làm rõ contract; vì sao v4 không tăng điểm và có hồi quy.
- Sản phẩm nghiệm thu: [system_prompt.md](starter_v0/artifacts/system_prompt.md), [tools.yaml](starter_v0/artifacts/tools.yaml), [version_log.csv](starter_v0/artifacts/version_log.csv), [nhật ký CP2](starter_v0/artifacts/cp2/experiment_log.md), bảng B1/B2 trong báo cáo nhóm.
- Bằng chứng kiểm tra chéo: [eval_group.json](starter_v0/data/eval_group.json) và bảng B3; case phải xuất phát từ lỗi thật và không sao chép bộ base.
- Commit kỹ thuật cá nhân:

## Đào Văn Hiệp — trách nhiệm và bằng chứng

- Báo cáo cá nhân: `MSSV_DaoVanHiep.md` — chờ thành viên bổ sung.
- Giải thích được: tool mới trả error dict; chuẩn hóa URL không làm mất tham số có nghĩa; overlap không phải kiểm chứng claim; query lỗi có coverage chưa biết.
- Sản phẩm nghiệm thu: [tool.py](starter_v0/tools/research_board/tool.py), [TOOL.md](starter_v0/tools/research_board/TOOL.md), [registry](starter_v0/tools/__init__.py), [test_tools_todo.py](starter_v0/tests/test_tools_todo.py), [bằng chứng CP3 v2](starter_v0/artifacts/cp3_v2/README.md), bảng B5a.
- Bằng chứng kiểm tra chéo: [ui/runtime.py](starter_v0/ui/runtime.py), [test_ui_runtime.py](starter_v0/tests/test_ui_runtime.py), cơ chế hiển thị lỗi/khóa `send`.
- Commit kỹ thuật cá nhân:

## Lê Nguyễn Anh Nhân — trách nhiệm và bằng chứng

- Báo cáo cá nhân: [2A202603838_LeNguyenAnhNhan.md](report/team/2A202603838_LeNguyenAnhNhan.md).
- Giải thích được: routing PASS khác tool thành công; Research desk bỏ qua model; prompt/policy/history/schema đi vào adapter thế nào; vì sao CP5 đổi sang 20b mà group eval vẫn giữ 120b.
- Sản phẩm nghiệm thu: [eval_group.json](starter_v0/data/eval_group.json), [run group](starter_v0/runs/cp3-research-board-v2_B_group_groq_20261111T022506173733.json), [app.py](starter_v0/app.py), [pipeline.py](starter_v0/ui/pipeline.py), [transcript CLI](starter_v0/transcripts/cp3-research-board-v2_groq_20261111T023231396178.transcript.json), [bằng chứng pipeline](starter_v0/artifacts/cp5_pipeline/README.md), Phần A/B3/B4 và checklist.
- Bằng chứng kiểm tra chéo: [nhật ký CP2](starter_v0/artifacts/cp2/experiment_log.md), [test contract](starter_v0/tests/test_tool_contract.py), [pytest cuối](starter_v0/artifacts/cp5_pipeline/pytest.txt).
- Commit kỹ thuật cá nhân:

## Checklist chốt bài

- [x] Có phân công cho đủ ba thành viên; Diên và Hiệp tự bổ sung báo cáo cá nhân.
- [x] Báo cáo nhóm có Phần A và B, dẫn tới code/run/transcript thật.
- [x] Có run v0–v4 và run group; transcript, code UI và hướng dẫn chạy.
- [x] Pytest lần chốt: **195 passed, 0 failed, 0 skipped**; [output](starter_v0/artifacts/cp5_pipeline/pytest.txt).
- [ ] Nhóm tự quyết định thời điểm commit và điền hash chốt bài.
- [x] `.env` dùng local được ignore, không đưa vào commit; `.env.example` chỉ chứa cấu hình mẫu.
- [ ] Điền MSSV, email/GitHub và URL repo được xác nhận.
- [ ] Diên và Hiệp bổ sung báo cáo bằng MSSV thật và cập nhật các link tương ứng; báo cáo Nhân đã dùng tên MSSV thật.
- [ ] Từng người đọc, tự kiểm tra và điền tự đánh giá/công cụ AI đã dùng trong báo cáo cá nhân.
- [ ] Mỗi người có commit kỹ thuật thật dưới danh tính của mình; điền hash ở mục cá nhân. Không tạo commit giả người khác.
- [ ] Push nhánh/commit chốt lên repo nhóm và kiểm tra người chấm truy cập được.
- [ ] Mỗi thành viên nộp cùng link repo trên LMS bằng tài khoản cá nhân.

Kết quả pytest, kiểm tra bằng chứng và kiểm tra secret lần cuối được lưu ở [artifacts/cp5_pipeline/validation.json](starter_v0/artifacts/cp5_pipeline/validation.json). Thông tin cá nhân còn trống do chưa được cung cấp, không phải dữ liệu suy đoán.
