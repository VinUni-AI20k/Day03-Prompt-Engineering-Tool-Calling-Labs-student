# Phân công công việc nhóm — Day 03 Research Agent Tool Eval

## 1. Thông tin nhóm

| Thành viên | Mã sinh viên | Vai trò chính |
|---|---|---|
| Nguyễn Nho Trọng | 2A202603666 | Prompt, tool routing và tối ưu v0–v3 |
| Trần Minh Tân | 2A202603688 | Tool mới và unit test |
| Vũ Quang Minh | 2A202603657 | Eval, UI, live chat và report |

## 2. Nguyên tắc làm việc để hạn chế conflict

- Mỗi thành viên làm trên một branch riêng:
  - `feature/prompt-routing`
  - `feature/new-tool-tests`
  - `feature/eval-ui-report`
- Không cùng lúc sửa `agent.py`, `chat.py` hoặc cùng một phần của `REPORT.md`.
- Không commit file `.env`, API key, Telegram token hoặc dữ liệu bí mật.
- Mọi thay đổi phải kèm bằng chứng: lệnh đã chạy, kết quả test hoặc file output.
- Nếu cần sửa file thuộc người khác, phải báo trước trong nhóm và ghi lại lý do.

## 3. Phân quyền file

### Nguyễn Nho Trọng

Được chỉnh sửa chính:

```text
starter_v0/artifacts/system_prompt.md
starter_v0/artifacts/tools.yaml
starter_v0/artifacts/version_log.csv
```

### Trần Minh Tân

Được chỉnh sửa chính:

```text
starter_v0/tools/<tool_moi>/tool.py
starter_v0/tools/<tool_moi>/TOOL.md
starter_v0/tools/__init__.py
starter_v0/tests/test_tools_todo.py
```

`artifacts/tools.yaml` chỉ được thêm phần khai báo tool mới sau khi đã thống nhất với Nguyễn Nho Trọng.

### Vũ Quang Minh

Được chỉnh sửa chính:

```text
starter_v0/data/eval_group.json
starter_v0/app.py
starter_v0/artifacts/REPORT.md
starter_v0/transcripts/
starter_v0/runs/
```

Nếu chưa có `app.py`, Vũ Quang Minh được tạo file mới, không sửa logic lõi của agent.

## 4. Các mốc thực hiện

### Mốc 0 — Setup chung

**Mục tiêu:** mọi thành viên có thể chạy project và hiểu cấu trúc bài lab.

**Cả nhóm thực hiện:**

```powershell
cd starter_v0
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python scripts/preflight_provider.py --provider openrouter
pytest
```

**Checkpoint 0 — đạt khi:**

- Provider preflight chạy thành công.
- Các contract/example test chạy được.
- Không commit `.env`.
- Mỗi thành viên tạo branch riêng.

**Người xác nhận:** Vũ Quang Minh ghi kết quả setup vào nhóm.

---

### Mốc 1 — Chốt thiết kế trước khi code

**Thời điểm:** sau khi setup thành công.

#### Nguyễn Nho Trọng

- Đọc `data/eval_base.json`.
- Liệt kê các tool hiện có và trường hợp routing.
- Chạy baseline `v0`.
- Lập danh sách lỗi ban đầu từ `runs/*.json`.

#### Trần Minh Tân

- Đề xuất tên tool mới.
- Chốt input, output và lỗi của tool.
- Gửi contract cho cả nhóm trước khi viết eval.

Khuyến nghị tool mới: `source_check`, dùng để kiểm tra các item nghiên cứu có URL và thông tin nguồn hợp lệ.

#### Vũ Quang Minh

- Chuẩn bị khung 10 eval case.
- Viết trước 9 case dùng tool có sẵn.
- Tạo khung `REPORT.md` và `app.py`.

**Checkpoint 1 — đạt khi:**

- Có file run baseline `v0`.
- Tool mới có tên và contract rõ ràng.
- Có danh sách eval case dự kiến.
- Không có hai thành viên cùng sửa một file.

---

### Mốc 2 — Phát triển feature song song

#### Feature A — Prompt và routing

**Phụ trách:** Nguyễn Nho Trọng

Thực hiện:

1. Sửa các chỉ dẫn không an toàn trong `system_prompt.md`.
2. Thêm rule dùng `clarify` khi thiếu thông tin.
3. Thêm rule phân biệt `timeline`, `social_search`, `lookup`, `fetch`, `format`.
4. Thêm rule không gọi `send` nếu chưa có `confirmed=true`.
5. Viết lại description trong `tools.yaml`.
6. Chạy thử từng thay đổi và ghi giả thuyết.

**Đầu ra:** prompt tốt hơn baseline và bản ghi các lỗi đã phân tích.

#### Feature B — Tool mới và test

**Phụ trách:** Trần Minh Tân

Thực hiện:

1. Tạo `tools/<tool_moi>/tool.py`.
2. Tạo `TOOL.md` đúng frontmatter.
3. Đăng ký tool trong `tools/__init__.py`.
4. Thêm khai báo tool vào `tools.yaml`.
5. Viết tối thiểu 3 test:
   - happy path;
   - input xấu hoặc thiếu;
   - failure path trả về error dict.
6. Chạy test offline bằng mock, không gọi API thật.

**Đầu ra:** tool mới hoạt động, được registry nhận diện và test xanh.

#### Feature C — Eval và UI

**Phụ trách:** Vũ Quang Minh

Thực hiện:

1. Viết 5 single-turn case.
2. Viết 5 multi-turn case.
3. Chờ contract tool mới để thêm case kiểm tra tool mới.
4. Dựng UI có ô nhập, nút gửi và vùng hiển thị kết quả/tool call.
5. Chuẩn bị bảng report nhưng chưa điền metric khi chưa có run cuối.

**Đầu ra:** `eval_group.json` đủ 10 case và UI chạy được ở local.

**Checkpoint 2 — đạt khi:**

- Tool mới pass test riêng.
- Prompt và `tools.yaml` không còn chỉ dẫn đoán bừa.
- Có đủ 10 eval case, gồm 5 single-turn và 5 multi-turn.
- UI mở được bằng `streamlit run app.py`.

---

### Mốc 3 — Tích hợp lần 1

**Thứ tự merge bắt buộc:**

1. Trần Minh Tân merge tool mới và test.
2. Nguyễn Nho Trọng cập nhật prompt/routing cho tool mới.
3. Vũ Quang Minh thêm eval case cho tool mới và chạy group eval.

**Sau khi merge, chạy:**

```powershell
cd starter_v0
pytest -v
python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json
```

**Checkpoint 3 — đạt khi:**

- `pytest` không còn test failed hoặc skipped.
- Tool mới xuất hiện trong cả `tools.yaml` và `TOOL_FUNCTIONS`.
- `TOOL.md` có tên trùng với tên tool.
- Contract test không báo lỗi.

---

### Mốc 4 — Tối ưu v1, v2, v3 và chạy eval nhóm

**Phụ trách chính:** Nguyễn Nho Trọng

Chạy:

```powershell
python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v2 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v3 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
```

Mỗi version phải có:

- một giả thuyết rõ ràng;
- một thay đổi chính;
- metric trước và sau;
- đường dẫn run JSON;
- dòng tương ứng trong `version_log.csv`.

**Vũ Quang Minh:** lấy kết quả run JSON để cập nhật bảng eval và report.

**Trần Minh Tân:** sửa lỗi tool nếu test tích hợp phát hiện lỗi, đồng thời thêm regression test.

**Checkpoint 4 — đạt khi:**

- Có đủ `v0`, `v1`, `v2`, `v3`.
- `version_log.csv` có đủ 4 dòng tương ứng.
- Group eval chạy thành công.
- Các lỗi còn lại đã được phân loại trong report.

---

### Mốc 5 — Live chat và UI demo

**Phụ trách:** Vũ Quang Minh

Chạy:

```powershell
python chat.py --provider openrouter --version v3
streamlit run app.py
```

Thực hiện ít nhất 3 lượt:

1. Câu hỏi nghiên cứu bình thường.
2. Câu hỏi thiếu username hoặc URL để kiểm tra `clarify`.
3. Yêu cầu gửi bản tin để kiểm tra confirmation.

**Nguyễn Nho Trọng:** kiểm tra agent có route đúng và có hỏi lại khi thiếu dữ liệu.

**Trần Minh Tân:** kiểm tra tool call có truyền argument đúng vào tool.

**Checkpoint 5 — đạt khi:**

- Có transcript JSON của ít nhất 3 lượt live.
- UI chạy được.
- Không lộ API key trong screenshot, transcript hoặc report.
- Hành vi `send` không gửi khi chưa xác nhận.

---

### Mốc 6 — Hoàn thiện report và kiểm tra nộp bài

**Phụ trách chính:** Vũ Quang Minh

`artifacts/REPORT.md` phải có:

- Phần A: agent làm được gì, danh sách tool, câu hỏi mẫu, link UI.
- B1: bảng evidence v0–v3.
- B2: phân tích lỗi thật từ run JSON.
- B3: 10 eval case.
- B4: live chat evidence.
- B5: test, UI và bonus nếu có.
- B6: reflection.

**Nguyễn Nho Trọng:** kiểm tra B1, B2 và phần giải thích prompt/tool declaration.

**Trần Minh Tân:** kiểm tra B5, test count và mô tả tool mới.

**Checkpoint 6 — hoàn thành bài lab khi:**

- `pytest` báo 0 failed, 0 skipped.
- Có run JSON baseline và các version cải tiến.
- Có transcript JSON.
- Có UI chạy được hoặc link demo.
- Có `REPORT.md` hoàn chỉnh.
- Không có secret trong git diff.

## 5. Bảng theo dõi tiến độ

| Checkpoint | Nội dung | Trọng | Tân | Minh | Trạng thái | Bằng chứng |
|---|---|---|---|---|---|---|
| CP0 | Setup, preflight, test ban đầu | ☐ | ☐ | ☐ | Chưa bắt đầu |  |
| CP1 | Baseline v0 và chốt contract tool mới | ☐ | ☐ | ☐ | Chưa bắt đầu |  |
| CP2 | Prompt, tool mới, eval 10 case, UI bản đầu | ☐ | ☐ | ☐ | Chưa bắt đầu |  |
| CP3 | Merge lần 1, contract test xanh | ☐ | ☐ | ☐ | Chưa bắt đầu |  |
| CP4 | Chạy v1–v3 và group eval | ☐ | ☐ | ☐ | Chưa bắt đầu |  |
| CP5 | Live chat, transcript, UI demo | ☐ | ☐ | ☐ | Chưa bắt đầu |  |
| CP6 | Report và kiểm tra nộp bài | ☐ | ☐ | ☐ | Chưa bắt đầu |  |

Quy ước trạng thái: `Chưa bắt đầu` → `Đang làm` → `Chờ review` → `Hoàn thành`.

## 6. Quy tắc bàn giao

Mỗi lần bàn giao phải gửi trong nhóm:

1. Tên branch và commit.
2. Danh sách file đã sửa.
3. Lệnh đã chạy.
4. Kết quả test/eval.
5. Việc còn tồn đọng hoặc rủi ro.

Mẫu bàn giao:

```text
Feature: Tool source_check
Owner: Trần Minh Tân
Branch: feature/new-tool-tests
Files: tools/source_check/*, tools/__init__.py, tests/test_tools_todo.py
Verification: pytest -v
Result: 0 failed, 0 skipped
Remaining risk: Chưa chạy group eval với model thật
```
