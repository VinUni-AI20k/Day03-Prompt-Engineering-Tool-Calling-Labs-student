# Bàn giao Feature B — Trần Minh Tân

- Ngày: 10/11/2026.
- Owner: Trần Minh Tân — 2A202603688.
- Branch: `feature/new-tool-tests-03688`.
- Trạng thái mới nhất (10/11/2026): tool/test và prompt/routing đã merge vào
  `main`; Tân kiểm tra tích hợp tại `57c2065`, **122 passed, 0 failed, 0 skipped**.
  Chờ transcript/report của Minh để kiểm tra arguments thật và review B5.
- Commit bàn giao: xem `git log -1 --oneline` trên branch này; phần tool và test
  được commit cùng tài liệu bàn giao, chờ review/merge vào nhánh chung.

## Cập nhật kiểm tra tích hợp

Đã fetch remote và xác minh `HEAD` trùng `origin/main` tại
`57c20650fd2fdaa260c405e2edbc4791a6e2bcde` (PR #3 của Trọng đã merge).
Chạy lại `.venv\Scripts\python -m pytest -v`: **122 passed, 0 failed,
0 skipped**, gồm 60 contract, 7 example, 55 tool cases; 1 warning deprecation
từ plugin `anyio`. Chưa phát hiện lỗi tool cần sửa. Evidence mới:
[pytest-integration-output.txt](pytest-integration-output.txt), có source commit
và SHA256 của prompt/tools để Minh đối chiếu khi điền REPORT B5.

Kiểm tra này chạy offline với fake HTTP/provider. Chưa có bằng chứng live
`source_check` hoặc review B5 hoàn chỉnh; không đánh dấu hai phần đó đã xong.
Minh có thể làm eval/UI/report ngay bằng code đã merge, không cần chờ Tân.
Khi có thay đổi mới từ Trọng/Minh, cập nhật code và chạy lại test tương ứng.
Các bảng bên dưới là hồ sơ bàn giao ban đầu; trạng thái chung mới nhất nằm ở
[TEAM_HANDOFF_CHECKLIST.md](../../../TEAM_HANDOFF_CHECKLIST.md).

## Tiến độ từng phần

| Phần của Tân | Kết quả | Bằng chứng |
|---|---|---|
| CP0 — kiểm tra môi trường offline | Xong; tạo `.venv --system-site-packages`, cài PyYAML 6.0.3 còn thiếu | Baseline thực tế: 62 passed, 17 skipped |
| CP0 — provider preflight | Chưa chạy: không có `.env` hoặc `OPENROUTER_API_KEY` | Chỉ kiểm tra sự hiện diện, không ghi giá trị key |
| CP1 — đề xuất tool, input/output/error | Xong contract `source_check` | `TOOL.md` cùng thư mục |
| CP2 — tool, frontmatter, registry, declaration | Xong; chỉ thêm block mới trong YAML | `tool.py`, `TOOL.md`, `tools/__init__.py`, `artifacts/tools.yaml` |
| CP2 — unit test offline | Xong cả 17 stub ban đầu; thêm test tham số hóa cho tool mới | `tests/test_tools_todo.py` |
| CP3 — kiểm tra tương thích trước merge | Xong offline: 122 passed, 0 failed, 0 skipped | `pytest-output.txt` cùng thư mục |
| CP3 — merge vào nhánh tích hợp | Chưa thực hiện | Chờ quy trình review/merge của nhóm |
| CP4 — sửa lỗi khi chạy model/group eval | Chưa có run tích hợp để kiểm tra | Trọng/Minh chạy sau khi tích hợp |
| CP5 — kiểm tra argument tool call | Đã kiểm tra bằng fake provider qua `ResearchAgent`; chưa kiểm tra live | `test_source_check_is_declared_and_executed_by_agent` |
| CP6 — mô tả tool/test count cho B5 | Đã chuẩn bị nội dung bên dưới | Minh đưa vào report chung sau khi review |

Không đánh dấu các checkpoint chung là hoàn thành khi prompt, eval, UI hoặc live
chat của nhóm chưa hoàn thành. Không tạo log model giả hoặc metric eval giả.

## Files bàn giao

Đường dẫn tương đối từ `starter_v0/`:

1. `tools/source_check/tool.py` — kiểm tra metadata trích dẫn, không dùng mạng.
2. `tools/source_check/TOOL.md` — frontmatter và contract đầy đủ.
3. `tools/__init__.py` — đăng ký `source_check`.
4. `artifacts/tools.yaml` — chỉ bổ sung khai báo `source_check`.
5. `tests/test_tools_todo.py` — hoàn thành test challenge, thêm test cho tool mới.
6. `tools/source_check/HANDOFF.md` — tiến độ và hướng dẫn tích hợp.
7. `tools/source_check/pytest-output.txt` — output thật của lần chạy kiểm chứng.

`artifacts/tools.yaml` thuộc phần phối hợp với Nguyễn Nho Trọng theo phân công.
Block khai báo mới được chuẩn bị để hoàn chỉnh feature theo yêu cầu của Tân;
Trọng cần review block này trước khi merge. Chưa có bằng chứng thống nhất trong
nhóm và chưa gửi tin nhắn cho ai. Không đổi prompt hoặc khai báo tool hiện có.

## Lệnh kiểm chứng

Chạy tại `starter_v0/` bằng PowerShell:

```powershell
.venv\Scripts\python -m pytest -v
.venv\Scripts\python -m pytest -v tests/test_tools_todo.py -k source_check
.venv\Scripts\python -m pytest -v tests/test_tool_contract.py
```

Lệnh đầu đã chạy và được lưu trong `pytest-output.txt`; hai lệnh sau dùng để
lọc phần cần review. Toàn bộ test chặn HTTP thật bằng `tests/conftest.py`.
Các request Telegram, Tavily, Firecrawl và RapidAPI trong test đều được mock.
Không cần API key thật để chạy test.

Môi trường Python 3.14.3 dùng lại pytest/requests từ hệ thống thông qua
`--system-site-packages`; chỉ cài bổ sung PyYAML trong `.venv`. Môi trường sạch
của nhóm vẫn nên cài `requirements.txt` như README trước khi chạy provider thật.
Có một warning deprecation từ plugin `anyio` của môi trường hệ thống; không có
test failed/skipped, không thay dependency chung chỉ để xử lý warning này.

## Gợi ý tích hợp cho Trọng

- Tên model gọi là `source_check`; chỉ có argument `items`.
- Khi người dùng yêu cầu kiểm tra metadata trích dẫn của item đã có, gọi tool
  này thay vì `lookup`, `fetch` hoặc `format`.
- Truyền nguyên `items` người dùng cung cấp; không tự bổ sung URL/source thiếu.
- Nếu có item lỗi, báo lỗi theo `results[index].issues`; không tuyên bố tất cả
  nguồn hợp lệ hoặc âm thầm bỏ item lỗi trong câu trả lời.
- Có thể truyền `result.items` cho `format` sau khi thông báo các item bị loại.
- `all_valid=true` chỉ nghĩa là metadata hợp lệ; không có nghĩa nội dung đã
  được xác thực. Tool không fetch URL hoặc kiểm tra uy tín nguồn.

## Mẫu eval để Minh đưa vào `data/eval_group.json`

Đây là case đề xuất, chưa phải kết quả chạy model. Giữ đủ 5 single-turn và
5 multi-turn của nhóm khi đưa case này vào suite; không đổi base eval.

```json
{
  "id": "G_source_check_existing_items",
  "phase": "B",
  "failure_type": "wrong_tool",
  "query": "Chỉ kiểm tra URL và thông tin nguồn của các item đã có sau đây, chưa cần tìm kiếm hay định dạng: [{\"title\":\"Paper\",\"url\":\"https://arxiv.org/abs/1706.03762\",\"source\":\"arxiv.org\"},{\"title\":\"Missing citation\"}]",
  "expect": {
    "tool_calls": [
      {
        "name": "source_check",
        "args": {
          "items": [
            {"title": "Paper", "url": "https://arxiv.org/abs/1706.03762", "source": "arxiv.org"},
            {"title": "Missing citation"}
          ]
        }
      }
    ]
  },
  "metadata": {
    "what_it_tests": "Route vào source_check với item đã có, giữ nguyên item thiếu URL/source để tool báo lỗi; không fetch/search/format."
  }
}
```

Kết quả tool dự kiến: `valid_count=1`, `invalid_count=1`, `all_valid=false`;
item index 1 có `missing_url` và `missing_source`. Eval hiện tại chấm tên tool
và args; unit test riêng mới kiểm chứng nội dung output của tool.

## Nội dung cung cấp cho REPORT B5

Trần Minh Tân bổ sung tool offline `source_check` để kiểm tra URL HTTP(S) và
trường nguồn của item nghiên cứu, trả trạng thái từng item và danh sách item có
metadata hợp lệ. Tool có `TOOL.md`, registry và khai báo YAML đồng bộ. Bộ test
đạt **122 passed, 0 failed, 0 skipped**: 60 contract cases, 7 example cases,
55 cases trong `test_tools_todo.py` (gồm 38 cases cho `source_check`). Đã hoàn
thành toàn bộ 17 test stub ban đầu, dùng mock cho mọi HTTP request và fake
provider để kiểm tra argument được truyền vào tool qua agent.

Ví dụ unit test kiểm tra điều mà routing eval không kiểm tra: model có thể gọi
đúng `source_check(items=...)` nhưng implementation vẫn nhận nhầm URL có port
sai hoặc không báo `missing_source`. Unit tests kiểm tra trực tiếp các output
đó. Chưa sửa bug trong tool có sẵn; không ghi nhận bug đã sửa khi chưa có bằng
chứng. Output test thực tế: `tools/source_check/pytest-output.txt`.

## Việc còn lại của nhóm

- Trọng review declaration mới, cập nhật routing/prompt và chạy eval v0–v3.
- Minh thêm case của tool mới vào suite, chạy group eval và tổng hợp report.
- Khi có credentials/provider, kiểm tra live chat và arguments thực tế.
- Tân xử lý regression nếu các lần tích hợp trên phát hiện lỗi tool.
