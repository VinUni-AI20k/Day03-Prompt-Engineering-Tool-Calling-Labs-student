# Bàn giao và checklist chung — Day 03 Research Agent Tool Eval

Cập nhật: **10/11/2026**. Phân công gốc: [TASK_ASSIGNMENT.md](TASK_ASSIGNMENT.md).
Đây là file theo dõi tiến độ hiện tại; phân công và phạm vi sở hữu file vẫn theo
`TASK_ASSIGNMENT.md`. Mỗi thành viên cập nhật phần của mình khi có kết quả mới.

**Cập nhật của Tân — sửa schema sau group eval:** branch
`feature/source-check-schema-03688`, base `main@9b24a6a`. Đã sửa khai báo
`source_check` để provider cho phép item thiếu URL/source tới tool; 4 regression
cases FAIL trước sửa và PASS sau sửa. Toàn bộ test đạt **131 passed, 0 failed,
0 skipped**. Chi tiết và output: [bàn giao schema fix](starter_v0/tools/source_check/SCHEMA_FIX_HANDOFF.md).
Trọng/Minh nhận bản sửa sau review/merge rồi chạy lại eval; chưa có kết quả API
thật sau sửa, không đổi các run ERR cũ thành PASS.

## 1. Tình trạng hiện tại và việc cần làm ngay

| Thành viên | Phần việc | Trạng thái đã biết | Việc tiếp theo |
|---|---|---|---|
| **Trần Minh Tân** — 2A202603688 | Tool mới và unit test | Đã commit/push `8682c8d` trên `feature/new-tool-tests-03688`; Tân xác nhận đã merge vào `main` | Hỗ trợ tích hợp, kiểm tra arguments và sửa regression nếu có |
| **Nguyễn Nho Trọng** — 2A202603666 | Prompt, routing, tối ưu v0–v3 | Chưa có bằng chứng cập nhật trong phiên bàn giao này | Lấy code từ `main`, review `source_check`, cập nhật routing và chạy eval |
| **Vũ Quang Minh** — 2A202603657 | Eval, UI, live chat, report | Chưa có bằng chứng cập nhật trong phiên bàn giao này | Lấy code từ `main`, thêm eval cho tool mới, hoàn thiện UI/report |

**Bước bàn giao tool đầu tiên đã hoàn tất theo xác nhận của Tân.** Tiếp theo,
Trọng tích hợp prompt/routing; Minh có thể viết eval và dựng UI song song, rồi
chạy group eval sau khi có bản prompt tích hợp. Tân chưa cần chờ để hỗ trợ review.

Thông tin merge vào `main` ở trên do Tân xác nhận; chưa kiểm tra lại remote ở
lần cập nhật tài liệu này. Trạng thái của Trọng/Minh là **chưa cập nhật**, không
có nghĩa hai bạn chưa làm. Mỗi bạn bổ sung branch, commit và bằng chứng bên dưới.

## 2. Gói bàn giao của Tân

- Tool: **`source_check(items=...)`**, kiểm tra cấu trúc URL HTTP(S) và trường
  `source`; chạy offline, không cần key, không xác minh sự thật hoặc uy tín nguồn.
- Đầu ra: `results` báo lỗi từng item; `items` chỉ giữ item hợp lệ;
  `valid_count`, `invalid_count`, `all_valid` tóm tắt kết quả.
- Input thiếu/sai kiểu list hoặc lỗi nội bộ trả error dict. Item lỗi trong list
  được báo riêng, không làm mất item tốt. List rỗng có `all_valid=false`.
- Đã đồng bộ implementation, frontmatter, registry và declaration YAML.
- Đã thay toàn bộ **17 test stub**; lần kiểm tra ở commit bàn giao đạt
  **122 passed, 0 failed, 0 skipped** (60 contract, 7 example, 55 tool cases;
  trong đó 38 cases dành cho `source_check`). Đây là kết quả offline trước tích
  hợp, cần chạy lại sau khi nhận thay đổi mới.
- Có 1 warning deprecation từ plugin `anyio` trong môi trường hệ thống.

Tài liệu để hai bạn dùng trực tiếp:

| Nội dung | Đường dẫn |
|---|---|
| Contract input/output/error và ví dụ gọi tool | [TOOL.md](starter_v0/tools/source_check/TOOL.md) |
| Gợi ý routing, mẫu eval JSON và đoạn nội dung cho REPORT B5 | [HANDOFF.md](starter_v0/tools/source_check/HANDOFF.md) |
| Output thật của bộ test | [pytest-output.txt](starter_v0/tools/source_check/pytest-output.txt) |
| Implementation | [tool.py](starter_v0/tools/source_check/tool.py) |
| Unit test | [test_tools_todo.py](starter_v0/tests/test_tools_todo.py) |

`HANDOFF.md` của tool ghi trạng thái tại thời điểm bàn giao trước merge.
Thông tin merge mới nhất được theo dõi trong file chung này.

## 3. Checklist của Trọng — prompt và routing

- [x] Cập nhật `main` vào nhánh làm việc; điền tên branch thực tế ở mục 8.
- [x] Đọc contract `source_check` và review block khai báo mới trong `artifacts/tools.yaml`.
- [x] Kiểm tra baseline `v0`: có run JSON và đúng prompt/tools hash của lần chạy. Evidence: `runs/v0_B_base_gemini_20261110T105830047307.json`; `artifact_version=v0+pc58791a20353+tb792b413ece1`; prompt hash `c58791a20353f34e23846cb5d459c72761343038fd451cfbe71c219e70d829ea`; tools hash `b792b413ece1b5a742e49f15fb78363f78a997e19dad03029446fced9ff043b6`; cả hai khớp hash tính từ artifact hiện tại.
- [x] Phân loại lỗi baseline từ log thật: kiểm tra [run v0 mới](starter_v0/runs/v0_B_base_gemini_20261110T110404621050.json), hash prompt/tools khớp artifact hiện tại và hash ở mục trên. Đo được 19/20 case, PASS 18, accuracy 94.74% trên 19 case đo được. `R03_web_news_routing` sai args (`wrong_arg_value`): gọi đúng `lookup`, nhưng query là `AI news` thay vì `AI`; `topic=news`, `timeframe=day` đúng. Nhãn `failure_counts.wrong_tool=1` là nhãn của case; lỗi quan sát thực tế nằm ở `observed_mismatch=wrong_arg_value`. `M01_clarify_then_fill` là `provider_error` do Gemini 503 quá tải, chưa đánh giá được hành vi thiếu thông tin. Các case đo được không phát hiện lỗi sai tool, missing-info hay boundary. Run dùng prompt/tools đã chỉnh sửa, không đại diện cho bản gốc trước tối ưu. Bước tiếp theo: làm rõ quy tắc query ở v1 và chạy lại để đo; chạy lại M01 khi provider ổn định.
- [x] Sửa chỉ dẫn đoán username/URL; dùng `clarify` khi thiếu dữ liệu.
- [x] Bổ sung routing cho `timeline`, `social_search`, `lookup`, `fetch`, `format`, `source_check`.
- [x] Chỉ cho phép `send` sau khi người dùng xác nhận rõ; khai báo `confirmed=true` tương ứng.
- [x] Làm rõ convention args: handle không có `@`, `topic`, `timeframe`, `Top/Latest`.
- [x] Chạy `v1`, ghi giả thuyết, một thay đổi chính, metric và đường dẫn run. Evidence: `runs/v1_B_base_openai_20261110T121418398315.json`; 18/20 PASS, accuracy 0.90, routing 0.95, arguments 0.90, multiturn 1.0; v0 0.65 → v1 0.90. Còn R12 boundary args và R13 thiếu `social_search`.
- [x] Chạy `v2`, ghi bằng chứng tương ứng. Evidence: `runs/v2_B_base_openai_20261110T122124813813.json`; 18/20 PASS, accuracy 0.90; không cải thiện so với v1.
- [x] Chạy `v3`, ghi bằng chứng tương ứng. Evidence: `runs/v3_B_base_openai_20261110T122544614376.json`; 17/19 measured PASS, accuracy 0.8947; 1 provider error do model.
- [x] Điền đủ `v0`–`v3` trong `artifacts/version_log.csv`; không tạo metric hoặc log giả.
- [ ] Chạy lại test sau thay đổi YAML; bàn giao commit/PR prompt cho cả nhóm. **Test đã đạt 122 passed, 0 failed, 0 skipped khi chạy lại; tài liệu bàn giao mới chưa commit/PR.**
- [ ] Review REPORT B1/B2 và mô tả prompt/tool declaration sau khi Minh tổng hợp.

Files chính: `starter_v0/artifacts/system_prompt.md`, `tools.yaml`, `version_log.csv`.
Tiến độ mới nhất: đã kiểm chứng baseline Groq `v0_B_base_openai_20261110T114359700556.json`
với snapshot starter (hai hash khớp), 13/20 PASS, 0 provider errors; đã ghi v0
vào version log. Phân tích 7 case lỗi và review sơ bộ REPORT B1/B2 ở
[TRONG_HANDOFF.md](starter_v0/artifacts/TRONG_HANDOFF.md).
v1–v3 chưa đo: môi trường hiện thiếu SDK `openai`, `OPENAI_API_KEY` và endpoint
Groq; thử cài SDK chưa thành công. Cần cấu hình trên máy chạy eval rồi đo v1
với prompt hiện tại; chọn thay đổi v2/v3 từ log từng vòng.
Nếu chưa có baseline trước khi thêm tool, ghi rõ bộ artifact thực tế dùng cho
baseline mới; không gọi kết quả đó là phép đo của code cũ chưa từng chạy.

## 4. Checklist của Minh — eval, UI, live chat và report

- [x] Cập nhật `main` vào nhánh làm việc; điền tên branch thực tế ở mục 8. Branch `feature/eval-ui-report-03657`, đã merge `origin/main` tới `57c2065` (PR #3 của Trọng).
- [x] Đọc mẫu eval `source_check` trong tài liệu bàn giao của Tân.
- [x] Hoàn thành `data/eval_group.json` với **5 single-turn + 5 multi-turn** (G01–G05 single, G06–G10 multi).
- [x] Có ít nhất 1 case kiểm tra routing/args của `source_check` trong 10 case: G01 (single) và G10 (multi). **Chỉ chấm routing**: `run_eval.compare_subset` gọi `sorted()` trên list nhiều dict → `TypeError`, bị ghi thành `provider_error`. Case mẫu của Tân (expect `items` 2 object) vì vậy không bao giờ PASS — cần quyết định ai sửa `run_eval.py` nếu muốn chấm `items`.
- [x] Mỗi case có ID riêng, `phase=B`, `failure_type` hợp lệ, `expect`, `metadata.what_it_tests`. Đã kiểm tra offline bằng `load_cases` + `validate_expected_tools` của `run_eval.py`, và chấm thử với "đáp án lý tưởng": 10/10 PASS, không crash.
- [x] Dựng `app.py`: ô nhập, nút gửi, kết quả và tool calls; cấu hình dependency UI nếu cần. Thêm `streamlit>=1.30.0` vào `requirements.txt`. Smoke test offline (`streamlit.testing`, fake provider): gọi tool, lỗi provider, nút câu hỏi mẫu đều đạt; `streamlit run app.py` health `ok`.
- [ ] Hoàn thành REPORT phần A: khả năng, danh sách tool, câu hỏi mẫu và link dùng thử. **Đã điền Team, A1, A2 (11 tool), A3 (5 câu mẫu); còn thiếu link demo** (điền khi mở Cloudflare Tunnel).
- [x] Nhận bản prompt/routing tích hợp từ Trọng; chạy group eval trên đúng artifact đã ghi nhận. Bản code cuối `v3+p39c95958ae7e+tfe7f33e09197` (prompt v3 + tools sau PR #7): `runs/v3_B_group_openai_20261110T125011759103.json`, 7/9 đo được (1 ERR).
- [x] Lưu run JSON thật và điền metric/report từ log, ghi rõ provider errors nếu có. REPORT B1 (v0–v3 theo `version_log.csv`), B2, B3, B6 điền từ run JSON; ghi rõ ERR G02 và nhiễu ±1 case giữa hai lần chạy cùng artifact v1.
- [x] Chạy ít nhất 3 lượt live: nghiên cứu bình thường, thiếu dữ liệu rồi bổ sung, yêu cầu gửi cần xác nhận. 6 lượt trong `transcripts/v3_openai_20261110T125044866247.transcript.json` (REPORT B4). Lượt nghiên cứu arXiv bị route nhầm sang `lookup` (thiếu key Tavily) — ghi là FAIL trong B4.
- [ ] Có transcript JSON thật; phối hợp với Tân kiểm tra args, với Trọng kiểm tra routing. **Transcript đã có; chờ Tân kiểm tra `items` (lượt 6: model bịa `source="blog.google"`) và Trọng kiểm tra routing (lượt 3: `lookup` thay vì `papers`).**
- [x] UI chạy được bằng `streamlit run app.py`; ghi cách chạy/link demo vào report. Cách chạy đã ghi ở REPORT A1; link demo điền khi chạy tunnel.
- [x] Hoàn thiện REPORT B1–B6; B5 lấy kết quả test hiện tại và mô tả tool từ Tân. Chờ Trọng review B1/B2, Tân review B5.
- [x] Kiểm tra report/transcript/screenshot không chứa secret trước khi bàn giao PR. Quét regex key Gemini/Groq/OpenAI/Tavily/Firecrawl/Telegram trên diff, run JSON và transcript: 0 kết quả.

Files chính: `starter_v0/data/eval_group.json`, `app.py`, `artifacts/REPORT.md`,
`runs/`, `transcripts/`. Không sửa `data/eval_base.json` để làm tăng điểm eval.

## 5. Checklist của Tân — phần đã bàn giao và kiểm tra tích hợp

- [x] Chốt contract tool mới `source_check`.
- [x] Tạo `tool.py` và `TOOL.md` đúng frontmatter.
- [x] Đăng ký `TOOL_FUNCTIONS` và bổ sung declaration trong `tools.yaml`.
- [x] Viết test happy path, bad/missing input và failure trả error dict.
- [x] Hoàn thành các test TODO; test offline bằng mock.
- [x] Lưu bằng chứng **122 passed, 0 failed, 0 skipped** tại commit bàn giao.
- [x] Chuẩn bị mẫu eval và nội dung REPORT B5 cho nhóm.
- [x] Commit/push `8682c8d`; merge vào `main` theo xác nhận của Tân.
- [ ] Sau khi phần Trọng/Minh merge, cập nhật `main` vào nhánh làm việc.
- [ ] Chạy lại toàn bộ test và ghi kết quả của bản tích hợp mới.
- [ ] Kiểm tra tool call thật truyền đúng `items`; item thiếu URL/source vẫn được báo lỗi.
- [ ] Nếu có bug, sửa tool và bổ sung regression test; ghi evidence trước/sau.
- [ ] Review REPORT B5: test count, mô tả tool, giới hạn metadata-only và bằng chứng.

## 6. Checklist chung trước khi chốt bài

- [ ] Cả ba thành viên xác nhận setup; provider preflight thành công trên môi trường chạy eval. Đã có xác nhận Gemini của Trọng; chưa đủ xác nhận cả ba thành viên. Groq tại môi trường hiện tại của Trọng chưa cấu hình.
- [ ] `main` chứa tool/test của Tân, prompt/routing của Trọng và eval/UI/report của Minh.
- [ ] Bản tích hợp cuối chạy `pytest`: **0 failed, 0 skipped**; lưu output mới.
- [ ] Contract khớp tên tool, function signature, YAML và `TOOL.md`.
- [ ] Có run JSON thật cho `v0`, `v1`, `v2`, `v3` và đủ 4 dòng version log.
- [x] Group eval đủ 10 case, đúng tỷ lệ 5/5, có case tool mới và run JSON. Evidence: `runs/v3_B_group_openai_20261110T122840577449.json`; 2 provider errors được ghi nhận.
- [ ] Có transcript ít nhất 3 lượt live, thể hiện clarification và confirmation.
- [ ] UI chạy được; có hướng dẫn chạy và link dùng thử theo yêu cầu bài lab.
- [ ] REPORT phần A và B1–B6 hoàn chỉnh, đối chiếu được tới evidence.
- [ ] Không commit `.env`, API key hoặc Telegram token; kiểm tra cả log/transcript.
- [ ] Các PR cần thiết đã review/merge; cả nhóm dùng cùng bản `main` để demo/nộp.

Setup/provider ở máy Tân chưa được xác nhận: lần kiểm tra trước không có `.env`
hoặc `OPENROUTER_API_KEY`. Mỗi thành viên tự ghi trạng thái môi trường của mình;
không suy ra máy khác cũng thiếu key. Trọng đã có `GEMINI_API_KEY` trong `.env`
nhưng chưa preflight được vì `.venv` thiếu `PyYAML` (và các dependency khác).

**Evidence Mốc 0 của Trọng (10/11/2026):** `.env` có `GEMINI_API_KEY` (không ghi
giá trị), dependencies đã hoạt động trong `.venv`, `pytest` đạt **122 passed,
0 failed, 0 skipped**, và Trọng xác nhận chạy ngoài sandbox:
`preflight_provider.py --provider gemini` trả `OK provider=gemini
model=gemini-3.5-flash` cùng tool call `timeline(screenname=sama, limit=1)`.
Checkpoint 0 của Trọng đạt; lỗi `WinError 10013` trước đó là giới hạn môi
trường sandbox, không phải lỗi provider/key.

## 7. Cách lấy code và kiểm chứng

Chạy từ thư mục gốc repo, khi đã commit hoặc xử lý các thay đổi đang làm.
Giữ nguyên nhánh riêng của mình:

```powershell
git status
git fetch origin
git merge origin/main
```

Nếu có conflict, chủ file phối hợp xử lý rồi chạy lại test trước khi push.
Không dùng force push hay reset để bỏ thay đổi của thành viên khác.

Các lệnh kiểm chứng chạy tại `starter_v0/`, sau khi kích hoạt môi trường đã cài
dependencies theo README. Eval/preflight cần provider key; pytest chạy offline:

```powershell
python -m pytest -v
python scripts/preflight_provider.py --provider openrouter
python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json
```

Trọng chạy lại lệnh base eval với từng `--version v1`, `v2`, `v3` sau thay đổi
thực tế tương ứng; không chạy bốn nhãn trên cùng code rồi coi là bốn lần tối ưu.
Sau khi tích hợp bản v3 và eval nhóm, Minh chạy:

```powershell
python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
python chat.py --provider openrouter --version v3
streamlit run app.py
```

## 8. Nhật ký bàn giao chung

Mỗi lần bàn giao, thêm một dòng vào bảng; đánh dấu checklist liên quan kèm đường
dẫn evidence và commit. Người sở hữu phần việc cập nhật trước; Minh tổng hợp
checkpoint chung sau review. Khi cùng sửa file này, fetch/merge trước khi push.

| Ngày | Người | Branch / commit hoặc PR | Nội dung bàn giao | Kiểm chứng / evidence | Việc tiếp theo |
|---|---|---|---|---|---|
| 10/11/2026 | Tân | `feature/new-tool-tests-03688` / `8682c8d` | `source_check`, registry, YAML, test; đã merge main theo Tân xác nhận | [122 passed](starter_v0/tools/source_check/pytest-output.txt) | Trọng cập nhật routing; Minh tích hợp eval/UI/report |
| 10/11/2026 | Trọng | `feature/prompt-routing-03666` / chưa commit | Cập nhật `system_prompt.md` và `tools.yaml`: clarify khi thiếu dữ liệu, routing 6 tool, convention args, confirmation trước `send`, metadata-only cho `source_check` | `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`; `compileall: PASS`; pytest/preflight bị chặn do thiếu `pytest`/`PyYAML` và pip `WinError 10013` | Cài dependencies hoặc dùng môi trường đã setup; chạy pytest, provider preflight, baseline và v1–v3; sau đó điền version log |
| 10/11/2026 | Trọng | `feature/prompt-routing-03666` / chưa commit | Kiểm tra baseline v0 và điều kiện phân loại lỗi | Chưa có `starter_v0/runs/`, `.env` hoặc `OPENROUTER_API_KEY`; preflight Python hệ thống thiếu `requests`; không có log thật để phân loại | Cấu hình provider và cài dependencies; chạy baseline v0, kiểm tra hash, rồi phân loại lỗi theo log |
| 10/11/2026 | Trọng | `feature/prompt-routing-03666` / chưa commit | Chạy Mốc 0 theo `TASK_ASSIGNMENT.md` | `.venv` sẵn có; `.env` tạo từ mẫu; `pip install -r requirements.txt` bị `WinError 10013`; preflight thiếu `yaml`; pytest thiếu module | Cài dependencies trên môi trường có network/provider key rồi chạy lại preflight và pytest |
| 10/11/2026 | Trọng | `feature/prompt-routing-03666` / chưa commit | Thử chạy lại Mốc 0 bằng Gemini | `GEMINI_API_KEY=SET` (không ghi giá trị); `preflight_provider.py --provider gemini` vẫn lỗi `ModuleNotFoundError: yaml` do `.venv` chưa có dependencies | Cài `requirements.txt` thành công rồi chạy lại preflight Gemini và pytest |
| 10/11/2026 | Trọng | `feature/prompt-routing-03666` / chưa commit | Kiểm tra lại Mốc 0 sau khi môi trường đã có dependencies | `pytest`: **122 passed, 0 failed, 0 skipped**; preflight Gemini exit 1 do `WinError 10013` khi kết nối API; key không bị in ra | Chạy lại preflight trên mạng cho phép kết nối Google API; sau đó xác nhận Checkpoint 0 |
| 10/11/2026 | Trọng | `feature/prompt-routing-03666` / chưa commit | Hoàn tất Mốc 0 | `pytest -q`: **122 passed**; preflight Gemini ngoài sandbox: `OK provider=gemini model=gemini-3.5-flash`, tool `timeline` gọi đúng args `screenname=sama`, `limit=1` | Chuyển sang Mốc 1: chạy baseline v0 và lập danh sách lỗi từ run JSON |
| 10/11/2026 | Trọng | `feature/prompt-routing-03666` / chưa commit | Chạy và kiểm tra baseline v0 | `runs/v0_B_base_gemini_20261110T105830047307.json`; hash prompt/tools khớp artifact; 20/20 case `provider_error`, `measured_cases=0` do `WinError 10013` | Chạy lại v0 trên môi trường có kết nối Gemini để phân loại routing/args/missing/boundary từ kết quả đo thật |
| 10/11/2026 | Minh | `feature/eval-ui-report-03657` / `7c57a0b` (eval), `8fc53d8` (UI), commit docs kèm theo | 10 eval case trong `data/eval_group.json` (5 single + 5 multi, có 2 case `source_check`); `app.py` Streamlit + `streamlit` trong `requirements.txt`; REPORT phần Team, A1–A3, B3 (mô tả case), B5; snapshot prompt/tools gốc cho baseline v0 tại `runs/v0_starter_snapshot/` (commit `65ae53a`) | `pytest`: 122 passed; validate offline 10/10 case; UI smoke test offline 3/3 + `streamlit run` health ok | **Trọng:** (1) **Gemini free tier chỉ 20 request/ngày/model** — key của Minh đã hết quota hôm nay, không đủ cho v1–v3 (mỗi base run = 20 request). Đề xuất cả nhóm chuyển sang **Groq `openai/gpt-oss-120b`** (1000 request/ngày, 8000 token/phút; chạy bằng `--provider openai --model openai/gpt-oss-120b` với `OPENAI_API_KEY=<key Groq>` + `OPENAI_BASE_URL=https://api.groq.com/openai/v1` trong `.env`, không cần sửa code). (2) Run `v0_*` hiện có dùng prompt/tools **đã sửa** (hash `c58791a…`/`b792b41…`), không phải baseline gốc → đề xuất coi đó là v1; baseline v0 thật chạy bằng `--system-prompt runs/v0_starter_snapshot/system_prompt.md --tools runs/v0_starter_snapshot/tools.yaml`. **Kết quả Groq `openai/gpt-oss-120b` (cùng model, so sánh được):** base v0 **0.65** → prompt PR #3 **0.85**; group v0 6/10, PR #3 6/10 (tính provider_error là FAIL). Việc cho v2/v3: R13 thiếu `social_search` song song; R03 thêm từ thừa vào `query`; R12 `clarify` dùng `text` thay vì `yes_no`; G02 không gọi `format`; G03 `sort_by` của `papers`; **G01: bỏ `required: [url, source]` trong schema item của `source_check`** (Groq trả 400). (3) `run_eval.compare_subset` crash (`TypeError`) khi expect args là list nhiều object → cần thống nhất ai sửa nếu muốn chấm `items`. (4) Với Groq, model không gọi tool khi `tool_choice=required` → HTTP 400 → `provider_error`, bị loại khỏi accuracy. |
| 10/11/2026 | Minh | `feature/eval-ui-report-03657` / commit kèm theo (sau `b176516`) | Group eval + live chat trên **bản code cuối** (prompt v3 + `tools.yaml` sau PR #7, artifact `v3+p39c95958ae7e+tfe7f33e09197`); REPORT B1 (v0–v3), B2, B3, B4, B6 | `runs/v3_B_group_openai_20261110T125011759103.json`: 7/9 đo được, 1 ERR (G02); `transcripts/v3_openai_20261110T125044866247.transcript.json`: 6 lượt; `pytest` 131 passed | **Tân:** G01 `items` nguyên vẹn, tool báo đúng `missing_url`+`missing_source`; nhưng **G10 và live lượt 6: model bịa `source="blog.google"`** cho item thiếu nguồn → tool báo hợp lệ (lỗi model/prompt, không phải tool). **Trọng:** (a) prompt thêm "truyền `items` y nguyên, không thêm/sửa field"; (b) live lượt 3 route "tìm paper arXiv" sang `lookup` thay vì `papers` — prompt v3 chưa có quy tắc cho `papers`/`paper_text`; (c) R13 FAIL ở mọi version; (d) run v3 base dùng tools trước PR #7 — nếu cần dòng B1 khớp code cuối thì chạy lại base; (e) cùng artifact v1 cho 0.85 và 0.90 → nhiễu ±1 case. **Minh còn lại:** link demo (A1). |
| 10/11/2026 | Minh | `feature/eval-ui-report-03657` / commit kèm theo (sau `5f19ef9`, PR #10) | Xác minh lại trên `v3-final-p1` theo review cuối của Tân: live chat 2 lượt (arXiv + `source_check`), kiểm tra tay args G01/G10 trong run group của Trọng; REPORT B1 (thêm `v3-final`, `v3-final-p1`), B2, B3, B4, B5 (131 test), B6 | `transcripts/v3-final-p1_openai_20261110T143232383389.transcript.json`; `runs/v3-final-p1_B_group_openai_20261110T142154758429.json` (8/9, 1 ERR); `pytest` 131 passed (60+7+59+5) | **P1 của Tân vẫn mở:** quy tắc prompt mới **không** ngăn model bịa `source="blog.google"` — G10 (group p1) và live lượt 2 đều tái hiện; G01 vẫn đúng. **Đã sửa:** routing arXiv → `papers` (live lượt 1), nhưng model bỏ `sort_by="submittedDate"`. **Trọng:** thêm dòng `v3-final`/`v3-final-p1` (base 0.95) vào `version_log.csv`; thử ví dụ mẫu cho G10 hoặc chốt là giới hạn. **Tân:** review lại B5 (131) và args G10/live. **Minh còn lại:** tên nhóm + link demo (A1). |
| 10/11/2026 | Minh | `feature/eval-ui-report-03657` → PR vào `main` | **v4** (sửa file của Trọng theo yêu cầu, có báo nhóm): thêm ví dụ mẫu `source_check` vào `system_prompt.md`; thêm `v3-final`, `v3-final-p1`, `v4` vào `version_log.csv` (hash lấy từ run JSON); REPORT B1–B4, B6; `MINH_V3_FINAL_P1_CHECK.md` | `runs/v4_B_base_openai_20261110T145359081439.json` 0.95; `runs/v4_B_group_openai_20261110T145702253546.json` 8/9; `transcripts/v4_openai_20261110T145738372871.transcript.json`; `runs/v4_source_check_repeat_probe.txt`; `pytest` 131 passed | **P1 chốt là giới hạn đã biết:** G10 bịa nguồn p1 3/5 → v4 2/7 (giảm, chưa hết); thử sửa mô tả `tools.yaml` ("v5") tệ hơn 5/6 nên đã hoàn tác. **Trọng:** review v4 + `version_log`. **Tân:** review B5/args. **Minh còn lại:** tên nhóm + link demo. |

Quy ước: `[x]` là đã có bằng chứng hoặc xác nhận được ghi rõ; `[ ]` là chưa xác
nhận hoàn tất. Bỏ tick nếu thay đổi mới làm điều kiện không còn đúng. Hoàn thành
phần của một người không tự động có nghĩa hoàn thành checkpoint chung.
