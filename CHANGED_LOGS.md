# Nhật ký thay đổi

Ghi lại nhóm Ban5 đã sửa gì, kết quả tốt lên hay xấu đi, và bằng chứng nằm ở đâu.
Mới nhất ở trên cùng. Chỉ ghi những gì đã làm và đo thật.

**Cách đọc điểm:** bộ kiểm tra có 20 tình huống. Mỗi tình huống đạt nếu trợ lý chọn đúng công cụ và điền đúng thông tin. "Đạt 13/20" nghĩa là đúng 13 trong 20 tình huống.

## Kết quả qua các lần sửa

| Lần | Ai làm | Đã sửa gì | Đạt | Bằng chứng |
|---|---|---|---|---|
| v0 | QuanNH | Chưa sửa gì (đo mốc ban đầu) | 13/20 | `starter_v0/runs/v0_B_base_openai_20261110T173801779394.json` |
| v1 | QuanNH | Sửa lời dặn cho trợ lý: hỏi lại khi thiếu thông tin, xin xác nhận trước khi gửi | 18/20 | `starter_v0/runs/v1_B_base_openai_20261110T175732383834.json` |
| v2 | QuanNH | Sửa lời dặn: nói rõ công cụ nào dùng cho việc nào, từ chối việc ngoài phạm vi, xin xác nhận dạng có/không | 18/20 | `starter_v0/runs/v2_B_base_openai_20261110T181054950591.json` |
| v3 | DucLT | Mô tả rõ điều kiện dùng tool, ưu tiên xác nhận gửi/đăng và quy ước tham số; giữ prompt v2, gpt-4o-mini | 20/20 | `starter_v0/runs/v3_B_base_openai_20261110T183553607506.json` |

Số liệu chi tiết: `starter_v0/artifacts/version_log.csv`. Bảng lỗi từng tình huống: `starter_v0/analysis/v0.csv`, `v1.csv`, `v2.csv`, `v3.csv`.

## Chi tiết

### v3 — Viết rõ cách chọn tool và kiểu câu hỏi xác nhận

- **Người thực hiện:** DucLT.
- **Sửa file nào:** chỉ các trường `description` trong `starter_v0/artifacts/tools.yaml`. Giữ nguyên `system_prompt.md`, code tool, tên/tham số, giá trị mặc định, bộ chấm và các case eval. Model vẫn là `gpt-4o-mini`.
- **Giả thuyết duy nhất:** nếu mô tả tool nói rõ khi nào dùng, khi nào không dùng và quy tắc nào được ưu tiên khi có nhiều điều kiện cùng đúng, model sẽ chọn đúng tool và tham số hơn.

**1. Đọc log để xác định sai ở đâu**

Không chỉ nhìn tổng điểm. Với từng case FAIL, đối chiếu `expect`, `actual_tool_calls` và `failures` trong run JSON:

| Case | Bộ kiểm tra yêu cầu | Model thực sự làm | Cần sửa ở đâu |
|---|---|---|---|
| R12 | `clarify(response_type="yes_no")` | Gọi đúng clarify nhưng truyền `text`, hỏi người dùng cung cấp nội dung bản tin | Quy tắc chọn kiểu câu hỏi |
| M06 | Chỉ gọi lookup sau khi người dùng nói bỏ Twitter | v2 gọi lookup và thêm social_search | Điều kiện ngừng dùng công cụ cũ |

R12 không phải lỗi API hay lỗi hàm clarify: model đã truyền rõ `text`, và tool trả lại đúng giá trị đó. Yêu cầu đăng bản tin đồng thời thiếu nội dung, nên có hai quy tắc cùng áp dụng: “thiếu dữ kiện thì hỏi” và “trước khi gửi phải xin xác nhận”. Hành vi quan sát được phù hợp với việc model chọn hỏi dữ kiện trước. Đây là suy luận từ log, không phải quan sát trực tiếp suy nghĩ bên trong model.

**2. Viết mô tả thành quy tắc quyết định, kèm ví dụ đối chiếu**

Trước hết viết lại mô tả của cả 11 tool: làm gì, khi nào dùng/không dùng, quy ước tham số. Với social_search, nói rõ chỉ tìm bài đăng mạng xã hội nếu người dùng vẫn yêu cầu nguồn đó; khi đã nói bỏ Twitter/chuyển sang tin web thì không gọi thêm theo ngữ cảnh cũ.

Lần đo đầu v3 đạt **19/20**: M06 đúng lại nhưng R12 vẫn sai. Vì vậy, vẫn trong v3, chỉ làm rõ thêm description của clarify bằng bảng quyết định sau:

| Ưu tiên | Người dùng đang cần gì? | Cách gọi clarify |
|---|---|---|
| 1 | Gửi/đăng nhưng chưa xác nhận, kể cả chưa đưa nội dung | `response_type="yes_no"`, hỏi xác nhận ý định trước |
| 2 | Đọc/tìm kiếm nhưng thiếu account, URL hoặc chủ đề | `response_type="text"`, hỏi dữ kiện còn thiếu |
| 3 | Chọn một phương án trong danh sách | `response_type="choice"`, cung cấp `options` |

Ví dụ đối chiếu được thêm ngay trong description để model thấy cách áp dụng:

- “Gửi bản tóm tắt qua Telegram” khi chưa có bản nháp → hỏi “Bạn xác nhận muốn gửi qua Telegram sau khi cung cấp và duyệt nội dung cuối chứ?”, dùng `yes_no`.
- “Đọc bài viết đó” khi chưa có link → hỏi URL, dùng `text`.

Điểm mấu chốt là **chọn kiểu câu hỏi theo mục đích yêu cầu**, thay vì cứ thấy thiếu thông tin là dùng text. Không đổi mặc định của clarify thành yes_no vì sẽ ảnh hưởng các yêu cầu thiếu URL/account.

Xác nhận ý định gửi chưa cho phép gửi nội dung chưa biết. Agent vẫn phải có nội dung cuối và được người dùng duyệt nội dung đó trước khi gọi `send(confirmed=true)`.

**3. Giữ phép đo công bằng và kiểm tra toàn bộ case**

Không sửa đáp án eval, không chèn điều kiện nhận diện riêng R12, không sửa tool call sau khi model trả về. Sau lần đo v3 đầu, chỉ description của clarify thay đổi; prompt, schema, model và các tool khác giữ nguyên. Kiểm tra toàn bộ suite, không chỉ chạy riêng R12, để phát hiện trường hợp sửa một lỗi nhưng làm hỏng case khác.

Chạy từ `starter_v0/`, sau khi kích hoạt `.venv`:

```bash
python -m pytest -q
python run_eval.py --provider openai --version v3 --suite base --eval-cases data/eval_base.json
python scripts/parse_runs.py runs/v3_B_base_openai_20261110T183553607506.json --output analysis/v3.csv
```

Tên run JSON trong lệnh parse là file của lần đo cuối đã thực hiện; lần chạy mới sẽ sinh tên có thời gian khác.

**4. Kết quả đo và bằng chứng**

| Chỉ số | v2 | v3 đầu | v3 cuối |
|---|---|---|---|
| Case đạt | 18/20 | 19/20 | **20/20** |
| R12 — xác nhận gửi | FAIL | FAIL | **PASS: yes_no** |
| M06 — bỏ Twitter | FAIL | PASS | **PASS: chỉ lookup** |
| Case từng PASS ở v2 bị hỏng | — | 0 | **0** |

- Lần v3 cuối: đo đủ **20/20 case**, **0 lỗi provider**; chọn tool, tham số và hội thoại nhiều lượt đều đạt 1.00.
- Cả 18 case từng PASS ở v1 cũng giữ PASS. Unit test: **104 passed, 0 failed, 0 skipped**.
- Run cuối: `starter_v0/runs/v3_B_base_openai_20261110T183553607506.json`.
- Bảng từng case: `starter_v0/analysis/v3.csv`; dòng v3 trong `starter_v0/artifacts/version_log.csv` trỏ tới run cuối này.
- Run đầu 19/20 được giữ nguyên để thấy quá trình chỉnh: `starter_v0/runs/v3_B_base_openai_20261110T182541886906.json`. Không thay kết quả cũ bằng kết quả mới.
- Bản cuối: `v3+p1a376861025b+tbf2ad343d04f`. Prompt hash trùng v2; tools hash đổi theo nội dung description. Hash đầy đủ nằm trong run JSON và version log.
- Ghi chú nhãn: một lần kiểm tra tạm từng được gắn nhãn v4 trước khi thống nhất giữ v3; file gốc được chuyển ra `/tmp/duclt_mislabeled_eval_20261110T183257225088.json`, không tính thành version riêng. Kết quả chính thức ở trên là lần chạy lại với đúng `--version v3`.

**Bài học để nhóm áp dụng lại:** đọc tool call thật → phân biệt lỗi chọn tool với lỗi tham số/code → tìm các quy tắc cạnh tranh → viết rõ thứ tự ưu tiên và ví dụ đối chiếu → đo lại toàn bộ suite → lưu cả kết quả chưa đạt lẫn kết quả cuối.

**Giới hạn và việc tiếp theo:** 20/20 là kết quả trên bộ base đã đo, chưa bảo đảm mọi câu hỏi mới. v3 kế thừa tool stats từ commit trước, còn v1/v2 dùng bộ lịch sử 10 tool; so sánh v2 với v3 vì thế còn khác biệt về bộ tool. Run JSON v1/v2 hiện không có ở local nên đối chiếu từng case dùng CSV đã lưu. Tiếp theo cần thử thêm các cách diễn đạt khác, hủy gửi và thay đổi nội dung sau xác nhận trong eval nhóm/UI.

### v2 — Dặn rõ công cụ nào dùng cho việc nào

- **Sửa file nào:** `starter_v0/artifacts/system_prompt.md` (vẫn chưa sửa mô tả công cụ).
- **Vì sao sửa:** sau v1 còn 2 tình huống sai. R12: trợ lý hỏi "bạn muốn đăng nội dung gì?" thay vì hỏi có đồng ý đăng không. M02: ở lượt cuối trợ lý đi tìm trên mạng xã hội thay vì tìm tin tức.
- **Đã làm:** thêm mục "chọn công cụ" (tin tức thì dùng `lookup`, bài đăng của một người thì dùng `timeline`, bài đăng theo chủ đề thì dùng `social_search`, đọc link thì dùng `fetch`), dặn giữ công cụ cũ khi người dùng chỉ đổi chủ đề, dặn từ chối việc ngoài phạm vi, và dặn hỏi xác nhận dạng có/không ngay cả khi chưa có nội dung để gửi.
- **Kết quả:** vẫn 18/20, không tiến thêm.
  - Tốt lên: M02 đúng lại (trợ lý giữ đúng công cụ tìm tin tức).
  - Vẫn sai (R12): trợ lý vẫn hỏi "bạn muốn đăng nội dung gì?" dù đã dặn rõ. Lời dặn này xung đột với lời dặn "thiếu thông tin thì hỏi lại", và mô hình chọn hỏi thông tin.
  - Mới sai (M06): người dùng bảo "bỏ Twitter, chuyển sang tìm tin tức", trợ lý tìm tin tức nhưng vẫn gọi thêm tìm trên Twitter. Rất có thể do lời dặn "giữ công cụ cũ" mới thêm bị hiểu quá rộng.
- **Bài học:** sửa một chỗ có thể làm hỏng chỗ khác, nên mỗi lần chỉ nên đổi ít. Lời dặn mâu thuẫn nhau thì mô hình chọn theo một bên. Chỉ chạy một lần nên chưa chắc M06 do lời dặn mới hay do mô hình lúc đúng lúc sai.
- **Việc tiếp theo (v3):** sửa mô tả công cụ trong `tools.yaml` (khi nào dùng, khi nào không), đặc biệt mô tả `clarify` (dùng dạng có/không để xin xác nhận) và `social_search`.

### v1 — Dặn trợ lý hỏi lại và xin xác nhận

- **Sửa file nào:** `starter_v0/artifacts/system_prompt.md` (lời dặn cho trợ lý).
- **Vì sao sửa:** ở v0, trợ lý tự đoán khi người dùng nói thiếu (ví dụ không nói tweet của ai thì tự chọn một người nổi tiếng) và gửi tin đi mà không hỏi. Lời dặn gốc của bài mẫu chính là bảo nó làm như vậy.
- **Đã làm:** bỏ các lời dặn đó, thay bằng: thiếu thông tin thì hỏi lại; trước khi gửi gì đi thì hỏi người dùng đồng ý chưa.
- **Kết quả:** từ 13/20 lên 18/20.
  - Tốt lên: trợ lý biết hỏi lại khi thiếu tên tài khoản hoặc đường link. Không còn tự gửi bài toán hay đoạn code đi. Tìm tin tức và tìm tweet cùng lúc cũng đúng.
  - Vẫn sai (R12): khi người dùng bảo "đăng bản tin lên Telegram", trợ lý có hỏi lại nhưng hỏi "bạn muốn đăng nội dung gì?" thay vì hỏi "bạn đồng ý đăng không?".
  - Mới sai (M02): trong hội thoại nhiều lượt, ở lượt cuối trợ lý đi tìm trên mạng xã hội thay vì tìm tin tức. Trước đây tình huống này đúng, nên đây là lỗi mới do thay đổi gây ra, hoặc chỉ là do mô hình lúc đúng lúc sai. Cần chạy thêm để biết.
- **Bài học:** gỡ lời dặn xấu cải thiện nhiều nhất. Nhưng chỉ nói "hãy hỏi lại" là chưa đủ, cần nói rõ hỏi kiểu nào và dùng công cụ nào cho việc gì.
- **Việc tiếp theo (v2):** dặn rõ công cụ nào dùng cho việc nào, và khi xin xác nhận thì hỏi dạng có/không.

### v0 — Đo mốc ban đầu

- Chưa sửa gì, chạy thử để biết trợ lý đang làm tốt đến đâu: 13/20.
- 7 tình huống sai, chia thành 4 kiểu:
  - Tự đoán thay vì hỏi lại (R10, R11): tự đoán tên tài khoản và đường link.
  - Gửi đi mà không xin phép (R12).
  - Làm việc ngoài phạm vi (R08, R14): bài toán và đoạn code đáng lẽ phải từ chối, nhưng trợ lý lại gửi đi.
  - Chọn sai công cụ hoặc thiếu công cụ (R03, R13).
- Bảng chi tiết nằm trong `report/team/group_report.md` (mục B2).

## Giao diện

### Giao diện web và server cho agent

- **Thêm:** thư mục `web/` (Next.js, React, shadcn/ui) và `starter_v0/server.py` (FastAPI).
- **Vì sao:** đề bài yêu cầu giao diện chạy được và chat thử ít nhất 3 lượt có lưu transcript.
- **Làm được gì:**
  - Chat với agent thật, thấy từng công cụ được gọi (tên, tham số, kết quả, thời gian) ngay khi nó chạy.
  - Khi agent hỏi lại thì hiện câu hỏi; khi cần xác nhận trước khi gửi thì hiện hộp Đồng ý / Không.
  - Lưu transcript mỗi phiên, cùng định dạng với `chat.py`; che khóa bí mật trước khi ghi. Có nút tải transcript.
  - Lưu lịch sử chat trong trình duyệt, có chế độ sáng/tối, dùng được trên điện thoại.
- **Cách chạy:** xem `web/README.md`.
- **Kiểm tra đã làm:** build và lint sạch; gọi thử qua proxy thấy kết quả về từng bước (không phải chờ đến cuối). Chưa chat thử ba lượt đầy đủ trên giao diện.
- **Việc tiếp theo:** chat thử ba lượt (yêu cầu thường, thiếu thông tin rồi bổ sung, yêu cầu gửi) và lưu transcript làm bằng chứng.

### Chat với agent ngay trên Telegram

- **Thêm:** `starter_v0/telegram_bot.py` và `starter_v0/tests/test_telegram_bot.py`.
- **Vì sao:** trước đó bot Telegram chỉ gửi tin đi (công cụ `send` đăng lên kênh), chưa nghe và trả lời tin nhắn của người dùng.
- **Làm được gì:** nhắn riêng cho bot thì agent chọn công cụ, chạy thật và trả lời lại. Khi cần xác nhận thì hiện nút Đồng ý / Không; khi hỏi chọn thì hiện nút lựa chọn. Mỗi cuộc chat lưu transcript như trên web.
- **An toàn:** chỉ các chat nằm trong `TELEGRAM_ALLOWED_CHAT_IDS` mới dùng được, để người lạ không tiêu tốn tiền API. Tin trong kênh và nhóm bị bỏ qua. Khóa bí mật bị che khỏi log và transcript.
- **Kiểm tra đã làm:** 10 bài test mới chạy không cần mạng (toàn bộ test là 118 đạt). Chạy thử logic với mô hình thật và Telegram giả: agent hỏi xác nhận bằng nút, sau khi bấm đồng ý thì gọi `send`. Chưa chạy với Telegram thật.
- **Cách chạy:** `python telegram_bot.py --provider openai --version v3` (xem `.env.example`).

### Đưa giao diện lên Vercel

- **Làm gì:** deploy thư mục `web/` lên Vercel, link dùng thử: https://research-agent-ban5.vercel.app
- **Cách hoạt động:** trang trên Vercel chỉ là giao diện; mọi lời gọi `/api/*` được chuyển về backend `server.py` chạy trên máy của nhóm qua tunnel Cloudflare (biến `API_ORIGIN` trên Vercel).
- **Điều kiện để dùng được:** máy nhóm phải đang chạy `python server.py` và `cloudflared tunnel --url http://localhost:8000`. Địa chỉ tunnel đổi mỗi lần chạy lại nên cần cập nhật `API_ORIGIN` và deploy lại.
- **Kiểm tra đã làm:** trang chủ, `/api/health`, `/api/tools` và một lượt chat có gọi tool đều chạy qua link Vercel.

### Chọn version của agent ngay trên giao diện

- **Thêm:** ô chọn version (v0, v1, v2, v3) ở đầu trang chat; mỗi cuộc chat chạy đúng prompt và mô tả công cụ của version đã chọn.
- **Không cần quay lại code cũ:** bản prompt và `tools.yaml` của từng version được chép nguyên văn từ lịch sử git vào `starter_v0/artifacts/versions/vN/`. Mã băm của từng file khớp với `version_log.csv` (có test kiểm tra). File `artifacts/system_prompt.md` và `tools.yaml` ở ngoài vẫn là bản đang sửa tiếp cho v4.
- **Cách hoạt động:** server có thêm `/api/versions`; giao diện gửi version khi mở chat mới. Đổi version giữa chừng sẽ mở một chat mới, để mỗi transcript chỉ thuộc về một version. Danh sách công cụ bên trái cũng đổi theo version (v0 chưa có `stats`).
- **Ví dụ thật cùng một câu hỏi ("Tóm tắt 5 tweet mới nhất giúp mình"):** v0 tự đoán tài khoản `sama` rồi gọi `timeline`; v3 hỏi lại bạn muốn tài khoản nào. Rất hợp để minh hoạ vòng lặp cải tiến khi demo.
- **Kiểm tra đã làm:** 130 test đạt (thêm 12 test cho phần version), lint và build giao diện sạch.
- **Khi làm v4:** chép `system_prompt.md` và `tools.yaml` hiện tại vào `artifacts/versions/v4/` sau khi chạy eval và ghi `version_log.csv`; ô chọn sẽ tự hiện thêm v4.

## Việc khác đã làm

- **Phân việc nhóm:** thư mục `tasks/` có bảng vai trò và checklist cho từng người.
- **Thông tin nhóm:** điền vào `TEAM.md` (nhóm Ban5, lớp L3B, 3 thành viên).
- **Telegram:** tạo bot và kênh riêng của nhóm để thử tính năng gửi tin. Khóa bí mật của bot chỉ lưu trên máy, không đưa vào repo.

## Còn phải làm

- [ ] v2, v3: tiếp tục sửa lời dặn và mô tả công cụ
- [ ] Thêm công cụ mới và kiểm tra nó chạy đúng (DucLT)
- [ ] Viết 10 tình huống kiểm tra riêng của nhóm (TrungNB)
- [ ] Làm giao diện chat và chat thử ít nhất 3 lượt, lưu lại
- [ ] Đổi khóa bot Telegram (khóa cũ đã lỡ lộ), thử gửi tin thật
- [ ] Hoàn thiện báo cáo nhóm và báo cáo cá nhân

## Mẫu cho lần ghi mới

```markdown
### vN — <tên ngắn>
- **Sửa file nào:**
- **Vì sao sửa:**
- **Đã làm:**
- **Kết quả:** X/20 lên Y/20
  - Tốt lên:
  - Vẫn sai hoặc mới sai:
- **Bài học:**
- **Việc tiếp theo:**
```
