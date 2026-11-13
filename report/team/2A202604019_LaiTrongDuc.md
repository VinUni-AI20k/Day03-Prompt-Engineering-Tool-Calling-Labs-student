# Báo cáo cá nhân — Lại Trọng Đức — 2A202604019

## 1. Thông tin thành viên

- Họ tên: Lại Trọng Đức
- MSSV: 2A202604019
- Email: 26ai.duclt2@vinuni.edu.vn

## 2. Phần việc phụ trách

- Hoàn thiện unit test cho các tool có sẵn, kiểm tra hoạt động offline và giữ contract giữa khai báo tool với code.
- Viết tool mới `stats`, tài liệu sử dụng, đăng ký tool và kiểm tra các nhánh thành công/input sai/lỗi xử lý.
- Cải thiện mô tả tool và quy ước tham số trong `tools.yaml` cho v3; ưu tiên lỗi hỏi xác nhận trước khi gửi và lỗi tiếp tục tìm Twitter khi người dùng đã bỏ nguồn này.
- Chạy eval bằng provider thật, phân tích kết quả, xuất CSV, ghi version log và giải thích phương pháp trong changelog của nhóm.

## 3. Đóng góp cụ thể

### 3.1. Hoàn thành 17 hàm unit test

Hoàn thiện `starter_v0/tests/test_tools_todo.py`: 14 hàm test cho clarify, format, send, lookup, fetch, timeline, social_search, policy và 3 hàm test cho tool mới stats. Dùng `pytest.mark.parametrize` để mở rộng thành **37 trường hợp kiểm tra**, bỏ toàn bộ stub `pytest.skip` trong file.

Các hành vi được kiểm tra gồm: lựa chọn và trạng thái chờ của clarify; chia nhóm/đánh số/dữ liệu rỗng của format; request Telegram sau xác nhận và không gọi mạng khi thiếu credentials; bỏ time_range khi lookup không có timeframe; ánh xạ kết quả Firecrawl và cắt nội dung ở biên 4.000 ký tự; giới hạn bài đăng và bỏ bài không có ID; truyền đúng Top/Latest; lọc policy và tách câu chỉ dẫn không đáng tin khỏi facts.

Test dùng `fake_http`, `FakeResponse` và `monkeypatch.setenv` với key giả, không nạp `.env` hay gọi API thật. Toàn bộ suite đạt **104 passed, 0 failed, 0 skipped**, bao gồm contract test.

Ví dụ khác biệt giữa unit test và eval: eval có thể xác nhận model đã chọn đúng lookup và arguments, nhưng unit test mới kiểm tra được request thực sự có bỏ `time_range` khi timeframe=None hay không. Các test bổ sung là kiểm tra hành vi; không tuyên bố đã tìm và sửa bug trong code tool có sẵn.

### 3.2. Viết tool mới stats

Tạo `tools/stats/tool.py` và `TOOL.md`; đăng ký `stats` trong `TOOL_FUNCTIONS` và `artifacts/tools.yaml`.

Tool chạy cục bộ, dùng thư viện chuẩn Python `statistics`, không cần API key và không thực thi biểu thức:

- Input: `values` là danh sách số hữu hạn không rỗng; `statistic` là mean, median hoặc stdev, mặc định mean.
- Output thành công: `tool`, `statistic`, `count`, `value`.
- stdev là độ lệch chuẩn mẫu, dùng mẫu số n−1 và cần ít nhất hai giá trị.
- Input không hợp lệ hoặc lỗi xử lý trả error dict, không để exception thoát khỏi tool.

Ba hàm test của stats kiểm tra kết quả đúng, input sai từ model và lỗi tính stdev với một quan sát. Các trường hợp gồm chuỗi số, boolean, danh sách rỗng, NaN/Infinity, statistic ngoài enum. Ví dụ `stats(values=[2, 3, 7], statistic="mean")` cho kết quả 4.

Chưa có bằng chứng eval nhóm/chat riêng chứng minh model route tới stats; đây là phần cần phối hợp bổ sung, dù code và unit test đã hoàn thành.

### 3.3. Cải thiện tool declaration và phân tích R12/M06 trong v3

Viết lại description của 11 tool và mô tả tham số: tool làm gì, khi nào dùng, khi nào không dùng, quy ước handle/timeframe/search_type và điều kiện xác nhận gửi. Giữ nguyên prompt của v2, model `gpt-4o-mini`, code tool, schema và nội dung case eval.

Giả thuyết: mô tả tường minh điều kiện dùng/không dùng và thứ tự ưu tiên chọn tham số ngay trong tool declaration giúp xử lý R12/M06 mà không làm hỏng các case đã đúng.

- **M06:** mô tả social_search nói rõ không gọi khi người dùng đã bỏ Twitter/chuyển sang tin web; không tiếp tục gọi tool chỉ vì nguồn đó xuất hiện ở lượt trước.
- **R12:** run đầu v3 đã gọi đúng clarify nhưng truyền response_type=text để hỏi nội dung bản tin. Tool trả đúng giá trị model đưa vào; không có lỗi provider. Phân tích từ log cho thấy model ưu tiên hỏi dữ kiện còn thiếu hơn xin xác nhận gửi.
- **Cách sửa R12:** làm rõ thứ tự ưu tiên trong description của clarify và thêm ví dụ đối chiếu: yêu cầu gửi/đăng chưa xác nhận → yes_no, kể cả thiếu bản nháp; yêu cầu đọc/tìm thiếu account/URL/chủ đề → text; chọn phương án → choice. Xác nhận ý định không cho phép gửi nội dung chưa biết; nội dung cuối vẫn phải được cung cấp và duyệt trước send.

Lần đo v3 đầu đạt 19/20; sau khi làm rõ description của clarify, chạy lại đúng nhãn v3 đạt **20/20**. Giữ cả hai run để theo dõi quá trình chỉnh, không sửa đáp án hay ép lại kết quả tool call trong code. Phân tích nguyên nhân là suy luận từ hành vi quan sát được, không phải khẳng định về suy nghĩ bên trong model.

### 3.4. Đo lường và lưu bằng chứng

Chạy base eval bằng OpenAI gpt-4o-mini và dùng `scripts/parse_runs.py` tạo `analysis/v3.csv`. Cập nhật dòng v3 trong `artifacts/version_log.csv` với hash thật, giả thuyết, số đo và đường dẫn run; viết mục v3 trong `CHANGED_LOGS.md` để nhóm có thể làm lại phương pháp.

| Chỉ số | v2 (mốc so sánh) | v3 cuối |
|---|---:|---:|
| Case đúng | 18/20 | 20/20 |
| Chọn đúng tool | 0.95 | 1.00 |
| Tham số đúng | 0.90 | 1.00 |
| Hội thoại nhiều lượt | 5/6 | 6/6 |

Run v3 cuối đo đủ 20 case, có 0 lỗi provider. R12 và M06 đều PASS; cả 18 case từng PASS ở v2 và cả 18 case từng PASS ở v1 đều giữ PASS. Đối chiếu v1/v2 dựa trên CSV đã lưu vì run JSON của hai phiên bản này không có trong bản local tại thời điểm phân tích.

Kết quả v0–v2 là công việc đã có của QuanNH, được dùng làm mốc đối chiếu; phần đóng góp của tôi ở đây là v3. Chưa hoàn thành một bảng tổng hợp riêng v0–v3 theo từng loại lỗi để bàn giao cho TrungNB.

## 4. Bằng chứng

### File, commit và repo

| Nội dung | Bằng chứng |
|---|---|
| Test offline và kết quả toàn suite | [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py), [duclt_pytest.txt](../../starter_v0/analysis/duclt_pytest.txt) |
| Tool mới và tài liệu | [stats/tool.py](../../starter_v0/tools/stats/tool.py), [stats/TOOL.md](../../starter_v0/tools/stats/TOOL.md) |
| Đăng ký và khai báo tool | [tools/__init__.py](../../starter_v0/tools/__init__.py), [tools.yaml](../../starter_v0/artifacts/tools.yaml) |
| Run v3 đầu, 19/20 | [Run JSON](../../starter_v0/runs/v3_B_base_openai_20261110T182541886906.json) |
| Run v3 cuối, 20/20 | [Run JSON](../../starter_v0/runs/v3_B_base_openai_20261110T183553607506.json) |
| Phân tích và versioning | [v3.csv](../../starter_v0/analysis/v3.csv), [version_log.csv](../../starter_v0/artifacts/version_log.csv) |
| Phương pháp và bài học | [CHANGED_LOGS.md — mục v3](../../CHANGED_LOGS.md) |
| Commit test và stats | [fefb019](https://github.com/haiquanng/K5-L3B-DAY03-Ban5-ResearchAgentToolEval/commit/fefb019) |
| Commit v3 và bằng chứng đo | [0d4b517](https://github.com/haiquanng/K5-L3B-DAY03-Ban5-ResearchAgentToolEval/commit/0d4b517) |

Hai commit trên đã push lên nhánh `feat/DucLT-tool-tests`. Báo cáo này không khẳng định PR đã được mở/review/merge vì chưa có bằng chứng xác nhận các bước đó.

Các lệnh đã dùng, chạy từ `starter_v0/` trong `.venv`:

```bash
python -m pytest -v
python run_eval.py --provider openai --version v3 --suite base --eval-cases data/eval_base.json
python scripts/parse_runs.py runs/v3_B_base_openai_20261110T183553607506.json --output analysis/v3.csv
```

Tên file run trong lệnh parse là bằng chứng của lần đo đã thực hiện; khi chạy lại cần dùng tên file mới được sinh.

### AI/công cụ đã dùng và cách kiểm tra kết quả

Sử dụng Codex hỗ trợ đọc tài liệu, viết code/test, phân tích run, chỉnh description và soạn changelog/báo cáo. Vì vậy, các phần code và tài liệu trên có hỗ trợ của AI, không được trình bày là hoàn toàn tự viết thủ công.

Các bước kiểm chứng đã thực hiện trong phiên làm việc với Codex:

- Chạy pytest và đối chiếu số hàm test/trường hợp được tham số hóa với log; giữ contract test xanh.
- Đọc actual_tool_calls và failures để xác định lỗi model, thay vì chỉ dựa vào câu trả lời hoặc tổng điểm.
- Kiểm tra run có provider_error_cases=0, measured_cases=total_cases=20; đối chiếu model, prompt/tools hash và kết quả CSV với run JSON.
- So sánh các case từng PASS ở v1/v2 để phát hiện hồi quy; xác nhận không sửa prompt, schema hay bộ eval khi sửa v3.
- Kiểm tra các run JSON không chứa giá trị API key/token đã cấu hình trước khi commit; không đưa `.env` vào repo.

Các bước tự đọc lại, giải thích trực tiếp code/test và đánh giá mức độ hiểu của cá nhân cần do tôi thực hiện; báo cáo không coi việc AI chạy kiểm tra là bằng chứng đã hoàn thành phần tự kiểm tra bằng tay.

## 5. Tự đánh giá

Đánh giá dưới đây dựa trên sản phẩm và log hiện có, không tự chấm điểm hoặc khẳng định năng lực cá nhân chưa được kiểm chứng:

- **Phần có bằng chứng hoàn thành:** 17 hàm test, tool stats và đăng ký/tài liệu, suite 104 test pass, tool declaration v3, base eval 20/20, CSV/version log/changelog và hai commit kỹ thuật đã push.
- **Giới hạn:** kết quả 20/20 chỉ áp dụng bộ base đã đo, chưa chứng minh độ ổn định trên mọi cách diễn đạt. v3 có thêm stats so với bộ tool lịch sử của v1/v2, nên so sánh tổng thể chưa loại trừ ảnh hưởng của thay đổi bộ tool. Chưa có eval nhóm/chat riêng cho stats.
- **Việc còn lại:** phối hợp TrungNB bổ sung case route tới stats; hoàn thiện bảng tổng hợp metric v0–v3 theo loại lỗi; review code và tự giải thích từng test; kiểm tra việc đưa commit vào nhánh nộp; nộp link repo trên LMS. Chưa thực hiện bonus ≥4 tool mới hoặc Ollama trong phần việc này.
- **Đề xuất cải thiện:** thêm tình huống người dùng hủy gửi, sửa nội dung sau xác nhận, thiếu dữ kiện và các cách diễn đạt mới để kiểm tra quy tắc xác nhận ngoài bộ base.
