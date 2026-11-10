# KẾ HOẠCH PHÂN CHIA CÔNG VIỆC DỰ ÁN (NHÓM 4 NGƯỜI)
**Dự án:** Day 03 Lab v2 — Research Agent Tool Eval  
**Mục tiêu:** Xây dựng Research Agent theo quy trình Evidence-driven, tối ưu Prompt/Tools qua thực nghiệm, viết Tool mới, Unit Test 100%, dựng UI và hoàn thiện Báo cáo khoa học.

---

## 1. NGUYÊN TẮC LÀM VIỆC SONG SONG (PARALLEL WORKFLOW)

Để 4 thành viên làm việc đồng thời mà **không bị chặn (block)** và **không bị xung đột mã nguồn (merge conflict)**:
- Mỗi thành viên phụ trách một khu vực file/thư mục độc lập.
- **TV3 (QA & Unit Test)** chạy hoàn toàn **offline** bằng mock (`fake_http`), không cần API key và không tốn chi phí.
- **TV2 (Tool Dev)** làm việc trong thư mục con riêng `tools/<tên_tool>/`.
- **TV4 (UI & Report)** làm việc trên file giao diện riêng `app.py` và `artifacts/poster.html`.
- **TV1 (Prompt & Eval Lead)** điều phối benchmark và tối ưu hóa file cấu hình `system_prompt.md` và `tools.yaml`.

---

## 2. CHI TIẾT PHÂN CHIA VAI TRÒ 4 THÀNH VIÊN

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        PHÂN CÔNG NHIỆM VỤ 4 THÀNH VIÊN                │
├──────────────────────────┬─────────────────────────────────────────────┤
│ Thành viên 1 (Lead)      │ Prompt Engineering & Benchmark Eval         │
│ Thành viên 2             │ Tool Developer (Bonus Tools & Telegram)     │
│ Thành viên 3             │ QA & Unit Testing Lead (Pytest 100% Green)  │
│ Thành viên 4             │ UI Fullstack, Demo & Báo cáo viên           │
└──────────────────────────┴─────────────────────────────────────────────┘
```

---

### 👤 THÀNH VIÊN 1: Trưởng nhóm / Prompt & Eval Lead
> **Trọng tâm:** Đo lường định lượng, tối ưu routing và trích xuất tham số của Agent qua các vòng lặp thực nghiệm `v0 -> v1 -> v2 -> v3`.

* **Các file phụ trách chính:**
  - `starter_v0/artifacts/system_prompt.md`
  - `starter_v0/artifacts/tools.yaml` (phần core tools: clarify, timeline, social_search, lookup, fetch, format)
  - `starter_v0/artifacts/version_log.csv`
  - `starter_v0/data/eval_group.json` (5 multi-turn cases)
* **Nhiệm vụ cụ thể:**
  1. Cấu hình file `.env` cá nhân, kiểm tra preflight (`scripts/preflight_provider.py`).
  2. Chạy bài kiểm thử baseline `v0` trên `data/eval_base.json`.
  3. Đọc log kết quả `runs/v0_*.json`, phân tích các case bị FAIL (`wrong_tool`, `wrong_arg_value`, `missing_info`, `out_of_scope`...).
  4. Thực hiện chu kỳ tối ưu qua 3 phiên bản (`v1`, `v2`, `v3`):
     - Xóa các anti-patterns trong `system_prompt.md` (đoán mò, tự gửi không xin phép, ép 1 bước).
     - Viết quy tắc routing rõ ràng (cá nhân vs từ khóa, web tin tức vs cào URL).
     - Tinh chỉnh `tools.yaml` mô tả rõ *khi nào dùng / khi nào không dùng*, chuẩn hóa convention args (handle không có `@`, topic `news`, timeframe, search_type `Top`|`Latest`).
     - Mỗi phiên bản chỉ đổi **1 giả thuyết**, ghi lại kết quả định lượng vào `version_log.csv`.
  5. Viết **5 multi-turn eval cases** bổ sung vào `data/eval_group.json`.

---

### 👤 THÀNH VIÊN 2: Tool Developer & Integration Lead
> **Trọng tâm:** Phát triển các Tool mới để đạt điểm thưởng tối đa (**Bonus: tự viết > 3 tool mới**) và cấu hình bot Telegram cho tool `send`.

* **Các file phụ trách chính:**
  - Các thư mục tool mới tự viết: `starter_v0/tools/<tên_tool>/tool.py` và `TOOL.md`
  - `starter_v0/tools/__init__.py` (đăng ký vào từ điển `TOOL_FUNCTIONS`)
  - Bổ sung định nghĩa schema tool mới vào cuối file `starter_v0/artifacts/tools.yaml`
  - `starter_v0/data/eval_group.json` (5 single-turn cases)
* **Nhiệm vụ cụ thể:**
  1. Xây dựng ít nhất **1 tool bắt buộc** (khuyến nghị làm **3–4 tool mới** để ăn trọn điểm thưởng), ví dụ:
     - `wikipedia`: Tra cứu tóm tắt bách khoa toàn thư qua API Wikipedia.
     - `weather`: Lấy dữ liệu thời tiết thực tế qua Open-Meteo API (không cần API key).
     - `calculator` / `math_eval`: Tính toán số liệu, xử lý biểu thức toán an toàn.
     - `duckduckgo_search`: Công cụ tìm kiếm web dự phòng cho Tavily.
  2. Đảm bảo mỗi tool đều có file `TOOL.md` chuẩn frontmatter YAML (`name`, `track`, `kind`, `inputs`, `outputs`...).
  3. Cấu hình Telegram Bot qua `@BotFather`, lấy Token & Chat ID để kích hoạt tool `send` (đảm bảo guardrail `confirmed=True`).
  4. Viết **5 single-turn eval cases** bổ sung vào `data/eval_group.json` (kiểm tra routing chính xác đến các tool mới).

---

### 👤 THÀNH VIÊN 3: QA & Unit Test Lead (Kiểm thử phần mềm)
> **Trọng tâm:** Đảm bảo toàn bộ mã nguồn tool chạy ổn định, hoàn thành 100% stub test trong `test_tools_todo.py` (**0 failed, 0 skipped**).

* **Các file phụ trách chính:**
  - `starter_v0/tests/test_tools_todo.py`
  - `starter_v0/tests/test_tool_contract.py` (theo dõi kiểm tra contract liên tục)
* **Nhiệm vụ cụ thể:**
  1. Làm việc hoàn toàn **offline** dựa trên fixture `fake_http` và `clean_env` trong `tests/conftest.py` (không tốn chi phí và quota API).
  2. Nghiên cứu 5 mẫu test chuẩn trong `tests/test_tools_examples.py`.
  3. Hoàn thiện toàn bộ các hàm test đang bị `pytest.skip(TODO)` trong `test_tools_todo.py`:
     - Test tool cục bộ: `clarify` (lưu options, awaiting_user), `format` (gom section, đánh số thread, xử lý list rỗng).
     - Test guardrail bảo vệ: `send` (chưa xác nhận thì không gọi mạng; thiếu token thì trả về lỗi).
     - Test mock HTTP: `lookup` (tham số query/timeframe), `fetch` (cắt ngắn 4000 ký tự), `timeline`, `social_search`.
     - Test an toàn bảo mật: `policy` (dòng lệnh prompt injection bị đẩy vào `untrusted_text`).
  4. Viết **≥ 3 unit test** cho mỗi tool mới do Thành viên 2 tạo ra (happy path, input biên xấu từ model, nhánh lỗi mạng).
  5. Đạt mục tiêu: Chạy `pytest` hiển thị **0 failed, 0 skipped**.
  6. Tìm ra các lỗi biên trong tool có sẵn (ví dụ `limit=0`, string rỗng...) và viết regression test làm bằng chứng cho mục B5 của báo cáo.

---

### 👤 THÀNH VIÊN 4: Fullstack UI, Demo & Báo cáo viên
> **Trọng tâm:** Dựng giao diện Web tương tác, cấu hình Cloudflare Tunnel public link, thu thập transcript live chat và chủ trì hoàn thiện `REPORT.md`.

* **Các file phụ trách chính:**
  - `starter_v0/app.py` (Giao diện Streamlit UI)
  - `starter_v0/artifacts/REPORT.md` (Phần A & Phần B)
  - `starter_v0/artifacts/poster.html` (Poster demo trình chiếu 1 trang)
  - `starter_v0/transcripts/*.transcript.json`
* **Nhiệm vụ cụ thể:**
  1. **Xây dựng UI tương tác bằng Streamlit (`app.py`):**
     - Khung chat hiện đại, hỗ trợ hiển thị luồng suy nghĩ của Agent.
     - Hiển thị trực quan: Tool nào được gọi, các tham số truyền vào, kết quả trả về từ tool, và văn bản tóm tắt digest cuối cùng.
  2. **Mở link truy cập public bằng Cloudflare Tunnel:**
     - Chạy `cloudflared tunnel --url http://localhost:8501` để lấy URL công khai dạng `https://<random>.trycloudflare.com`.
  3. **Tương tác Live Chat thực tế:**
     - Chạy thử ít nhất 3 phiên chat đa lượt (qua UI hoặc `chat.py`), lưu lại các file transcript JSON làm bằng chứng nộp bài.
  4. **Hoàn thành PHẦN A của Report & Poster (Bắt buộc xong TRƯỚC 16:30):**
     - Viết tóm tắt giới thiệu agent, dán link public demo, bảng danh sách tool và 3–5 câu hỏi mẫu để người ngoài test.
     - Dựng file `artifacts/poster.html` để chiếu trực tiếp trong buổi Team Showdown.
  5. **Tổng hợp hoàn thiện PHẦN B của Report:**
     - Thu thập bảng số liệu `v0 -> v3` từ TV1.
     - Lấy danh sách tool và eval cases từ TV2.
     - Lấy kết quả `pytest` và regression test từ TV3.
     - Viết phần đúc kết kinh nghiệm (Reflection) và hoàn tất hồ sơ nộp bài.

---

## 3. LỘ TRÌNH VÀ CÁC ĐIỂM ĐỒNG BỘ (TIMELINE & SYNC POINTS)

| Mốc giờ | TV1 (Prompt & Eval) | TV2 (Tool Dev) | TV3 (QA & Test) | TV4 (UI & Report) | 🎯 ĐIỂM ĐỒNG BỘ (SYNC POINT) |
|---|---|---|---|---|---|
| **Mốc 1** *(30-45p)* | Cài env, preflight, chạy Baseline `v0`, ghi `version_log.csv` | Lên danh sách tool mới, viết mã code tool 1 & `TOOL.md` | Đọc `test_tools_examples.py`, viết test cho `clarify`, `format`, `send` | Tạo khung UI Streamlit `app.py`, kết nối với `ResearchAgent` | **Sync 1:** Chốt số điểm Baseline `v0`, thống nhất danh sách và tên tool mới. |
| **Mốc 2** *(30-45p)* | Xóa anti-pattern, viết rule routing, chạy `v1`, ghi log | Viết tiếp tool 2 & 3, cấu hình Bot Telegram `send` | Viết tiếp test cho `lookup`, `fetch`, `timeline`, `social_search`, `policy` | Hoàn thiện hiển thị Tool Calls trên UI, mở Cloudflare Tunnel | **Sync 2:** TV2 merge tool vào registry; TV3 lấy hàm viết unit test; TV1 cập nhật `tools.yaml`. |
| **Mốc 3** *(30-45p)* | Tinh chỉnh `tools.yaml`, chạy `v2`, phân tích lỗi | Viết 5 single-turn eval cases cho tool mới | Viết unit test cho các tool mới do TV2 viết | Chạy 3 phiên live chat lưu transcript; soạn **Phần A Report** | **Sync 3:** Ghép đủ 10 cases vào `eval_group.json`; TV4 lấy link Tunnel dán vào Report. |
| **Mốc 4** *(30p)* | Chạy eval suite `group` trên `eval_group.json` | Hỗ trợ kiểm thử ranh giới hoạt động của tool | Chạy toàn bộ `pytest`, đảm bảo **0 failed, 0 skipped** | Hoàn thiện **Poster HTML**, chuẩn bị thiết bị chiếu demo | **Sync 4 (16:30): DEMO SHOWDOWN** (Trình diễn UI live + Poster + Report Phần A). |
| **Mốc 5** *(Sau demo)* | Chạy tối ưu vòng cuối `v3`, ghi nhận số liệu | *(Bonus)* Thử nghiệm model local nhỏ qua Ollama | Ghi nhận bug tìm được làm tư liệu cho mục B5 Report | Tập hợp toàn bộ kết quả, hoàn thiện **Phần B REPORT.md** | **Sync 5:** Kiểm tra checklist nộp bài cuối cùng. |

---

## 4. CHIẾN LƯỢC ĐẠT ĐIỂM THƯỞNG TỐI ĐA (BONUS STRATEGY)

1. **Điểm thưởng nhóm (Bonus Points):** Hoàn thành đồng thời:
   - Dựng giao diện Web tương tác (Streamlit) chạy mượt mà kèm public link.
   - Tự xây dựng **hơn 3 tool mới** hoàn chỉnh (kèm `TOOL.md`, đăng ký `TOOL_FUNCTIONS`, khai báo trong `tools.yaml`, có unit test đầy đủ).
2. **Action Tool an toàn:** Kích hoạt tool Telegram `send` kèm cơ chế xác thực an toàn (bắt buộc hỏi người dùng xác nhận `confirmed=True` trước khi gửi).
3. **Small Local Model Challenge (Tùy chọn):** Nếu còn thời gian, TV1 & TV2 chạy thử nghiệm prompt v3 trên model local qua Ollama (`qwen2.5:7b` hoặc `llama3.2:3b`), phân tích sự khác biệt giữa Cloud vs Local và điền vào mục B7 của Report.

---

## 5. CHECKLIST NGHIỆM THU TRƯỚC KHI NỘP BÀI

- [ ] File `.env` tuyệt đối **không** được commit lên Git.
- [ ] `starter_v0/artifacts/system_prompt.md` đã được tối ưu, không còn chỉ dẫn đoán bừa.
- [ ] `starter_v0/artifacts/tools.yaml` mô tả đầy đủ điều kiện dùng/không dùng và quy ước tham số.
- [ ] `starter_v0/artifacts/version_log.csv` có tối thiểu 4 phiên bản: `v0`, `v1`, `v2`, `v3`.
- [ ] `starter_v0/data/eval_group.json` có đủ 10 test cases mới (5 single-turn, 5 multi-turn).
- [ ] Đã thêm ≥ 1 tool mới (khuyến nghị > 3 tool mới) kèm thư mục riêng, `TOOL.md` và đăng ký trong `tools/__init__.py`.
- [ ] Chạy `pytest` báo **0 failed, 0 skipped**.
- [ ] Có thư mục `starter_v0/transcripts/` chứa ít nhất 1 file `*.transcript.json` từ phiên chat live.
- [ ] Có file giao diện `starter_v0/app.py` chạy được trên Streamlit.
- [ ] `starter_v0/artifacts/REPORT.md` hoàn thành đầy đủ cả Phần A và Phần B.
- [ ] Đã tạo poster giới thiệu tại `starter_v0/artifacts/poster.html`.
