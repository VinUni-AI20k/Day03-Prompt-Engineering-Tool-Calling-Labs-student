# Báo cáo cá nhân — Nguyễn Thành Tâm - 2A202603933

## 1. Thông tin thành viên

- **Họ tên:** Nguyễn Thành Tâm
- **MSSV:** `2A202603933`
- **Email:** `26ai.tamnt@vinuni.edu.vn`
- **GitHub:** `ngthanhtamtb`
- **Vai trò:** Prompt Engineer
- **Nhóm:** Nhom5W (Lớp L3B)

---

## 2. Phần việc phụ trách

- Thiết lập và chạy bộ đánh giá chuẩn với provider `gemini` (`gemini-3.8-flash`) trên bộ đề `starter_v0/data/eval_base.json` (20 cases: 14 single-turn và 6 multi-turn).
- Phụ trách vai trò **Prompt Engineer**: Thực hiện vòng lặp tối ưu **Evidence-driven** qua các phiên bản `v0` → `v1` → `v2` → `v3` dựa trên phân tích log `starter_v0/runs/*.json`, đặt giả thuyết (hypothesis), tinh chỉnh `artifacts/system_prompt.md` và `artifacts/tools.yaml`.
- Phân tích lỗi giữa các nhóm lỗi hành vi trong `system_prompt.md` và nhóm lỗi quy ước tham số trong `tools.yaml` (`wrong_arg_value` ở `lookup.query`).

---

## 3. Đóng góp cụ thể

Quá trình thực nghiệm và tối ưu hóa được ghi nhận đầy đủ qua 6 file run JSON trong `starter_v0/runs/` ứng với từng phiên bản từ `v0` đến `v3`:

### 3.1. Phiên bản Baseline (`v0`) — Chẩn đoán lỗi gốc của Starter
- **File kết quả:** [`starter_v0/runs/v0_B_base_gemini_20261110T180840811830.json`](`artifact_version: v0+pf0c107a9d7a1+t41a2894f8ad1`)
- **Chỉ số đo:** `case_accuracy = 0.75`, `tool_routing_accuracy = 0.80`, `argument_accuracy = 0.75`, `multiturn_accuracy = 1.00`.
- **Phân tích 5 cases FAIL ở `v0`:**
  1. `R10_missing_handle` & `R11_missing_url` (`missing_tool_call`): Agent không gọi `clarify` khi thiếu tên tài khoản hoặc thiếu URL mà tự đoán `screenname="sama"` và tự bịa URL để gọi `timeline`/`fetch` — do `system_prompt.md` gốc chứa chỉ dẫn xấu ép đoán mò.
  2. `R12_confirm_before_send` (`missing_tool_call`): Agent gọi thẳng `send(confirmed=True)` thay vì gọi `clarify(response_type="yes_no")` để xin xác nhận trước khi đăng lên Telegram.
  3. `R03_web_news_routing` & `R13_parallel_web_and_tweets` (`wrong_arg_value` / thiếu tool): Agent truyền `query="artificial intelligence news"` / `"trí tuệ nhân tạo AI hôm nay"` thay vì từ khóa cốt lõi `"AI"`, và ở `R13` chỉ gọi 1 tool (`lookup`) mà bỏ sót `social_search` do câu lệnh ép *"Always finish the request in a single step. Pick one tool"*.

### 3.2. Phiên bản `v1` — Loại bỏ chỉ dẫn đoán mò và thiết lập quy tắc hỏi lại (`clarify` khi thiếu thông tin)
Trong giai đoạn `v1`, tôi thực hiện 2 lần chạy để kiểm chứng giả thuyết về hành vi hỏi lại (`Missing Information`):
- **Lần chạy `v1` thứ nhất (Thử nghiệm & phát hiện lỗi mâu thuẫn prompt):**
  - **File kết quả:** [`starter_v0/runs/v1_B_base_gemini_20261110T183140172591.json`]
  - **Thay đổi:** Sửa cụm *"do not ask them back"* thành *"ask them back"* trong `system_prompt.md`, nhưng vẫn để sót vế sau *"— just make a sensible guess and call a tool right away..."*.
  - **Kết quả & Bài học:** `case_accuracy` tụt từ `0.75` xuống **`0.70`**. Nguyên nhân là do câu lệnh tự mâu thuẫn ngay trong cùng một câu (vừa bảo hỏi lại, vừa bảo đoán đại và gọi tool ngay) khiến model bị nhiễu.
- **Lần chạy `v1` thứ hai (Xóa triệt để câu xúi đoán mò & chỉ định rõ `clarify`):**
  - **File kết quả:** [`starter_v0/runs/v1_B_base_gemini_20261110T185237539301.json`]
  - **Giả thuyết:** Nếu xóa bỏ hoàn toàn câu lệnh xúi đoán mò Sam Altman/URL giả định và quy định rõ phải gọi `clarify(response_type="text")` khi thiếu thông tin tài khoản hoặc URL, các case `missing_info` sẽ PASS.
  - **Kết quả:** `case_accuracy` tăng lên **`0.80`**, `tool_routing_accuracy` tăng từ `0.80` → **`0.90`**. Cả 2 câu `R10_missing_handle` và `R11_missing_url` đều PASS; câu `R12` cũng đã chuyển từ gọi `send` sang gọi `clarify` (nhưng còn sai `response_type` là `"text"` thay vì `"yes_no"`).

### 3.3. Phiên bản `v2` — Giải quyết `Out of Scope`, `Multi-tool` và ranh giới xác nhận `Confirmation Before Sending`
Từ 4 câu còn FAIL ở cuối `v1` (`R03`, `R08`, `R12`, `R13`), tôi thực hiện 2 bước tinh chỉnh trên `system_prompt.md` trong phiên bản `v2`:
- **Lần chạy `v2` thứ nhất (Thêm quy tắc `Out of Scope` & `Multi-tool`):**
  - **File kết quả:** [`starter_v0/runs/v2_B_base_gemini_20261110T185924162965.json`]
  - **Giả thuyết:** Nếu bỏ quy định ép gọi 1 tool duy nhất, đồng thời dặn rõ không gọi tool cho câu hỏi toán/lập trình ngoài phạm vi (`R08`) và cho phép gọi nhiều tool song song khi câu hỏi yêu cầu nhiều nguồn (`R13`), thì `R08` và routing của `R13` sẽ được khắc phục.
  - **Kết quả:** `case_accuracy` tăng từ `0.80` → **`0.85`**, `tool_routing_accuracy` đạt **`0.95`**. Câu `R08_out_of_scope` đã PASS và `R13_parallel_web_and_tweets` đã gọi đủ cả `lookup` lẫn `social_search`.
- **Lần chạy `v2` thứ hai (Thêm quy tắc `Confirmation Before Sending` với `response_type="yes_no"`):**
  - **File kết quả:** [`starter_v0/runs/v2_B_base_gemini_20261110T191813503578.json`]
  - **Giả thuyết:** Ở lần chạy trước, `R12_confirm_before_send` bị FAIL do model truyền `response_type="text"` (hỏi nội dung bản tin). Nếu bổ sung mục `Confirmation Before Sending` vào `system_prompt.md` bắt buộc gọi `clarify(response_type="yes_no")` khi user yêu cầu gửi/đăng bài lên Telegram mà chưa xác nhận, thì `R12` sẽ PASS.
  - **Kết quả:** `case_accuracy = 0.85`, `tool_routing_accuracy = 0.95`. Câu `R12_confirm_before_send` đã **PASS** chính xác với `clarify(response_type="yes_no")`. Lúc này toàn bộ lỗi còn lại (`R03`, `R13`, `M02`) đều chỉ nằm ở tham số `lookup.query` (truyền thừa chữ `"news"`).

### 3.4. Phiên bản `v3` — Chuẩn hóa quy ước tham số `lookup` trong `tools.yaml` (Đạt 100% Accuracy)
- **File kết quả:** [`starter_v0/runs/v3_B_base_gemini_20261110T192529403171.json`]
- **Giả thuyết:** Ở `v2`, agent liên tục truyền thừa từ `"news"` / `"artificial intelligence"` vào `lookup.query` (như `"AI news"`, `"robotics news"`) và gọi lặp `lookup` 2 lần ở `R03`. Nếu sửa `starter_v0/artifacts/tools.yaml` tại tool `lookup`:
  1. Dặn rõ chỉ gọi `lookup` đúng 1 lần cho mỗi yêu cầu tra cứu web.
  2. Quy định `query` chỉ chứa từ khóa chủ đề cốt lõi ngắn gọn đúng như câu hỏi (`"AI"`, `"robotics"`, `"OpenAI"`), tuyệt đối không thêm `"news"`, `"tin tức"`, `"hôm nay"` vì phân loại tin tức và thời gian đã nằm ở `topic="news"` và `timeframe="day"|"week"`.
- **Kết quả:** **`case_accuracy = 1.00`**, `tool_routing_accuracy = 1.00`, `argument_accuracy = 1.00`, `multiturn_accuracy = 1.00`.

---

## 4. Bằng chứng

- **File/commit/PR:**
  - File đã chỉnh sửa: `starter_v0/artifacts/system_prompt.md` (`prompt_hash: 9c43efb47199`), `starter_v0/artifacts/tools.yaml` (`tools_hash: 65e0ae20ecad`).
  - Run log `v0` (`acc = 0.75`): `starter_v0/runs/v0_B_base_gemini_20261110T180840811830.json`
  - Run log `v1` (`acc = 0.70` → `0.80`): `starter_v0/runs/v1_B_base_gemini_20261110T183140172591.json`, `starter_v0/runs/v1_B_base_gemini_20261110T185237539301.json`
  - Run log `v2` (`acc = 0.85`): `starter_v0/runs/v2_B_base_gemini_20261110T185924162965.json`, `starter_v0/runs/v2_B_base_gemini_20261110T191813503578.json`
  - Run log `v3` (`acc = 1.00`): `starter_v0/runs/v3_B_base_gemini_20261110T192529403171.json`
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Dùng AI hỗ trợ đọc `failures` / `observed_mismatch` trong run JSON, tìm nguyên nhân tụt accuracy ở lần thử `v1` đầu tiên (do mâu thuẫn câu lệnh trong prompt) và gợi ý tách giả thuyết cho `v1`, `v2`, `v3`.
  - Tự kiểm tra bằng cách chạy `python run_eval.py --provider gemini` sau mỗi lần sửa và đối chiếu `summary` (`measured_cases`, `provider_error_cases`, `case_accuracy`) trong các file JSON.

---

## 5. Tự đánh giá

- **Mức độ hoàn thành:** Tối ưu Prompt & Tool Declarations, nâng kết quả từ `0.75` ở `v0` lên `1.00` ở `v3`.
- **Bài học rút ra:**
  1. **Tính nhất quán trong System Prompt:** Không được để các chỉ dẫn mâu thuẫn nhau cùng tồn tại song song; khi thay đổi hành vi của Agent, phải xóa triệt để các câu lệnh đoán mò cũ.
  2. **Phân vai rõ ràng giữa `system_prompt.md` và `tools.yaml`:** `system_prompt.md` giải quyết rất tốt bài toán điều phối hành vi và ranh giới an toàn (`clarify`, `yes_no` confirmation, `out_of_scope`, `multi-tool`), còn `tools.yaml` quyết định model trích xuất đúng định dạng tham số .
