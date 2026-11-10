# Phối hợp build tool và agent

## Phạm vi đợt này

Tool đầu tiên: `deduplicate_sources(items)` — bỏ nguồn trùng URL trong dữ liệu đã có,
không gọi API. Hợp đồng chi tiết và ví dụ: `starter_v0/tools/deduplicate_sources/TOOL.md`.

Luồng tích hợp: tìm/đọc nguồn → `deduplicate_sources` → kiểm tra có `error` không →
`format(items=result["items"], ...)` → trả lời. Nếu gửi Telegram, cần xác nhận riêng.
Tool không tự gọi các tool khác; agent điều phối từng bước.

## Hai phía làm song song

| Phía | Sở hữu chính | Tiêu chí bàn giao |
|---|---|---|
| Bạn: tool | `tools/deduplicate_sources/`, test hành vi tool | Contract ổn định; đúng input/output; xử lý input lỗi; test offline xanh |
| Phía agent/UI | `artifacts/system_prompt.md`, vòng lặp agent/chat, UI | Thu thập items thật; chọn đúng tool; xử lý error; chuyển items sang format |
| Một người tích hợp | `tools/__init__.py`, `artifacts/tools.yaml`, `data/eval_group.json` | Ghép đăng ký/schema/eval, chạy toàn bộ test, tránh sửa chồng các file chung |

Ba điểm ghép của tool này đã được thêm trong working tree. Phía agent có thể dùng
tên `deduplicate_sources` ngay sau khi nhận thay đổi, không cần đợi API key.
Đây là phân công giữa hai phía; chưa có một agent/UI khác đang chạy trong chat này.

Nếu dùng Git: mỗi phía làm trên một clone/worktree riêng với nhánh riêng, ví dụ
`codex/build-deduplicate-sources` và `codex/agent-ui`. Không đổi nhánh trong cùng
thư mục khi người/agent khác đang chỉnh file. Nhờ một người ghép các file chung.

## Chạy trên Windows PowerShell

Từ thư mục gốc repo, tạo môi trường một lần:

```powershell
python -m venv starter_v0/.venv
cd starter_v0
.\.venv\Scripts\python.exe -m pip install -r requirements-test.txt
.\.venv\Scripts\python.exe -m pytest -q tests/test_tool_contract.py tests/test_deduplicate_sources.py
.\.venv\Scripts\python.exe -m pytest -q
```

Test tool và fake-provider integration không cần `.env`, khóa API hay SDK provider.
`tests/test_tools_todo.py` có ba test thật cho tool mới; các stub của tool cũ vẫn
skip cho đến khi nhóm hoàn thành. CI chạy toàn bộ suite và hiển thị các skip;
CI xanh hiện tại không đồng nghĩa đã đạt yêu cầu cuối bài “0 skipped”.

## CI và CD

- CI đã cấu hình tại `.github/workflows/tool-ci.yml`: khi push hoặc mở PR,
  GitHub Actions cài Python 3.12, dependency test và chạy `python -m pytest -q`.
  Có thể chạy thủ công bằng `workflow_dispatch`. CI không cần secrets.
- Workflow chỉ được chuẩn bị ở local; cần đưa lên GitHub để có kết quả CI thật.
- CD là tự động đưa bản đã kiểm tra lên môi trường demo. Chưa cấu hình CD vì chưa
  có UI và đích triển khai của nhóm; ghép bước deploy khi hai phần đó đã chốt.
- Hướng dẫn tham khảo: https://docs.github.com/en/actions/tutorials/build-and-test-code/python

## Đánh giá bằng model thật sau khi ghép

1. Phía phụ trách setup chuẩn bị `.env` và cài `requirements.txt` trong cùng venv.
2. Chạy `python scripts/preflight_provider.py --provider openrouter`.
3. Chạy baseline trước khi sửa prompt; lưu đúng tools hash vì đã thêm tool mới.
4. Chạy group eval bằng model thật:

```powershell
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --version v1-dedup --suite group --eval-cases data/eval_group.json
```

Ba case mới gồm 2 single-turn và 1 multi-turn: chọn tool, thiếu danh sách cần hỏi,
và sử dụng danh sách ở lượt trước. Chưa có kết quả model thật. Các case dùng
`args: {}` để chấm routing; correctness của items được kiểm tra bằng unit test,
không coi group eval này là bằng chứng argument accuracy của tool mới.
Nhóm cần thêm 7 case (3 single-turn + 4 multi-turn) để đủ tổng 10 case, tỷ lệ 5/5.
Prompt starter có chỉ dẫn xấu cố ý; case thiếu thông tin có thể fail trước khi sửa.

## Việc tiếp theo của bạn

1. Đọc `TOOL.md`, thử thay danh sách nguồn trong ví dụ bằng dữ liệu của nhóm.
2. Thống nhất với phía agent tên tool và cấu trúc `items`; giữ nguyên sau khi ghép.
3. Thêm test cho tình huống thực tế mới trước khi thay đổi quy tắc bỏ trùng.
4. Chạy test, bàn giao code qua PR cùng output pytest và mô tả giới hạn.
5. Cùng phía agent kiểm tra log tool-call bằng model thật rồi đưa bằng chứng vào REPORT.
