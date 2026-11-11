# Team

## Thông tin nhóm

- Tên nhóm: NhomSNN
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-NhomSNN-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo: https://github.com/sybui2004/K5-L3B-DAY03-NhomSNN-ResearchAgentToolEval
- Nhánh nộp: `main`
- Commit chốt: 0661df47ff2bbd649161476022bb464b3e86ef55

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Bùi Thái Sỹ | 2A202604002 |  | [sybui2004](https://github.com/sybui2004) | Nhóm trưởng; UI, live chat, Phần A báo cáo; v4–v8; bonus |
|   2 | Nguyễn Lương Nguyên | 2A202604005 |  | [nglngnguyen-gh](https://github.com/nglngnguyen-gh) | Prompt, vòng lặp v0→v3 |
|   3 | Mai Xuân Nhân | 2A202604006 |  | [nhan54v-boop](https://github.com/nhan54v-boop) | Tool mới `github_repo` + unit test |
|   4 | Bùi Đức Hiếu | 2A202604003 |  | [HieuData](https://github.com/HieuData) | Eval nhóm 10 case + test challenge |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

## BuiThaiSy-2A202604002

### Phần việc phụ trách

- Nhóm trưởng: chia việc theo file để tránh conflict (`ChiaViec.md`), khung `TEAM.md`, điều phối merge, chốt bài (`pytest`, kiểm tra secret, commit chốt).
- UI Streamlit (`starter_v0/app.py`) + link dùng thử, live chat/transcript, Phần A của `group_report.md`.
- v4 (`tools.yaml`) và các version v5–v8; bonus Small Local Model, 3 tool bonus, gửi Telegram thật, 2 bug test challenge.

### Đóng góp cụ thể

- UI Streamlit `starter_v0/app.py`: dùng chung vòng lặp tool của `chat.py`, hiện từng tool call/lỗi, tự nhận nhãn version bằng hash, cổng Đồng ý/Từ chối trước khi `send`; `streamlit` trong `requirements.txt`; instance public không có token Telegram.
- Phát hiện model mặc định `gpt-4o-mini` trả 402; chạy base eval v4 trên OpenRouter nemotron free (0.95); commit v4 `tools.yaml` (viết lại description 10 tool).
- Chuyển eval sang model local Ollama `qwen2.5:7b` (v5–v8) khi hết quota; v5 Security (+ `data/eval_security.json`, `tests/test_eval_security.py`), v6 (3 tool bonus), v7 (few-shot), v8 (dọn dẹp); ghi `version_log.csv`, snapshot `artifacts/versions/`.
- **Bonus Small Local Model:** 2 model (llama3.2:3b, qwen2.5:7b), Modelfile `num_ctx 16384`/`num_predict 1024`, baseline + 3 vòng tối ưu (local1–3), mục B7.
- **Bonus hơn 3 tool mới:** `hackernews`, `wikipedia`, `pypi_package` (+ `tests/test_tools_new.py`, `data/eval_new_tools.json`); cùng `github_repo` của Nhân = 4 tool, route đúng 4/4.
- **Bonus gửi Telegram thật:** agent xin xác nhận → user đồng ý → `send(confirmed=true)` → `status: sent`.
- **Test challenge (phần bổ sung):** sửa 2 bug trong tool có sẵn kèm regression test — `papers` bị 0 kết quả khi truy vấn có stopword (phát hiện khi chạy UI), `send` lộ token bot trong thông báo lỗi.

### Bằng chứng

- Commit: `f173fac`, `5357c6f`, `7811714`, `b73f1e8`, `a60356a` và commit chốt.
- Run: `starter_v0/runs/v4_B_base_openrouter_20261110T194629157695.json`; `v5…v8_*_ollama_*.json`; `{v4,local1,local2,local3}-{llama3b,qwen7b}_B_base_ollama_*.json`.
- Transcript: `starter_v0/transcripts/v5_ollama_*.transcript.json` (4 phiên, gồm gửi Telegram thật `…T224219995766`), `ui_v6_ollama_20261110T231814388412.transcript.json` (bug `papers`).
- Báo cáo cá nhân: [report/team/2A202604002_BuiThaiSy.md](report/team/202604002_BuiThaiSy.md).

## NguyenLuongNguyen-2A202604005

### Phần việc phụ trách

- `artifacts/system_prompt.md` v1–v3, chạy base eval v0→v3, `artifacts/version_log.csv`.

### Đóng góp cụ thể

- Chạy và tạo baseline v0 trên Gemini `gemini-3.8-flash`.
- v1: sửa system prompt để không bắt buộc chạy tool lung tung (sửa đoạn "đoán thay vì hỏi"), chạy bản v1 để kiểm định — commit `e4827f3`.
- v2: sửa system prompt để không tự ý suy đoán khi thiếu thông tin quan trọng, yêu cầu xác nhận trước hành động bên ngoài và cho phép xử lý tác vụ qua nhiều bước khi cần thiết, chạy bản v2 để kiểm định.
- v3: rút gọn và chuẩn hóa Tool Routing Policy: phân biệt rõ chức năng 10 tools, quy định argument conventions, routing sequences và send confirmation boundary, chạy bản v3 để kiểm định — commit `d56f348` (v2–v3); case_accuracy 0.70 → 0.85.

### Bằng chứng

- `starter_v0/runs/v0…v3_B_base_gemini_*.json`; dòng v0–v3 trong `starter_v0/artifacts/version_log.csv`; commit `e4827f3`, `d56f348`.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: ChatGPT; tự kiểm tra qua log và kết quả xuất ra command line sau khi chạy `run_eval`.

## MaiXuanNhan-2A202604006

### Phần việc phụ trách

- Tool mới `github_repo` (`tools/github_repo/`, đăng ký `tools/__init__.py` + `tools.yaml`) và ≥ 3 unit test.

### Đóng góp cụ thể

- Tool `github_repo`: đọc metadata repo GitHub công khai theo `owner/repo`, validate input trước khi gọi mạng, lỗi trả error dict — commit `b7a2a27`.
- 3 hàm test `test_github_repo_*` (19 trường hợp tham số hoá: happy path, input xấu, lỗi API) trong `tests/test_tools_todo.py`.
- _(Nhân tự bổ sung/chỉnh phần này.)_

### Bằng chứng

- `starter_v0/tools/github_repo/`; `starter_v0/tests/test_tools_todo.py`; commit `b7a2a27`, `0399b62`; báo cáo cá nhân `report/team/2A202604006_MaiXuanNhan.md`.

## BuiDucHieu-2A202604003

### Phần việc phụ trách

- 10 eval case trong `data/eval_group.json`, test challenge (`tests/test_tools_todo.py`); B3, B5 dòng Test challenge.

### Đóng góp cụ thể

- Xây dựng bộ 10 eval case nhóm: Thiết kế 5 single-turn và 5 multi-turn, bao phủ các tình huống tool routing, argument correctness, missing information, wrong boundary và unnecessary tool invocation. Bổ sung case kiểm tra tool mới github_repo, đồng thời kiểm tra khả năng hỏi lại khi thiếu owner, cập nhật yêu cầu khi người dùng sửa thông tin và duy trì context qua nhiều lượt hội thoại.

- Hoàn thiện unit test challenge: Viết 14 test cho 8 tool có sẵn, kiểm tra các hành vi chính và trường hợp biên. Các test bao gồm kiểm tra định dạng đầu ra, tham số API, xử lý input rỗng, giới hạn nội dung, xử lý dữ liệu thiếu và điều kiện xác nhận trước khi gửi Telegram.

- Kiểm thử độc lập với API bên ngoài: Sử dụng fake_http, FakeResponse và monkeypatch để mock HTTP request, giả lập API key và kiểm tra kết quả trong môi trường offline. Nhờ đó, test có thể kiểm tra request method, URL, headers, parameters, request body và dữ liệu trả về mà không phụ thuộc dịch vụ thật.

- Kiểm tra an toàn dữ liệu và trust boundary: Bổ sung test cho policy, xác minh nội dung chứa chỉ dẫn giả mạo được phân loại vào untrusted_text, không bị đưa vào phần facts.

- Đánh giá khả năng tổng quát hóa của agent: Các eval case được thiết kế không chỉ kiểm tra việc chọn đúng tool mà còn kiểm tra khả năng không gọi tool khi không cần thiết, không tự suy đoán thông tin còn thiếu và không thực hiện hành động vượt quá phạm vi của tool.

### Bằng chứng

- `starter_v0/data/eval_group.json`; `starter_v0/tests/test_tools_todo.py`; run `starter_v0/runs/v5-group_B_group_ollama_20261110T222936142201.json`, `v8-group_B_group_ollama_20261110T234927007107.json`.
