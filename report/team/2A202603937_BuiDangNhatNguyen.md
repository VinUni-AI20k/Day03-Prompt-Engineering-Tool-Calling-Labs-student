# Báo cáo cá nhân — BuiDangNhatNguyen-2A202603937

## 1. Thông tin thành viên

- Họ tên: Bùi Đặng Nhật Nguyên
- MSSV: 2A202603937
- Email: nhatnguyenmtvt@gmail.com
- GitHub: double-n-021 (branch `BuiDangNhatNguyen`)

## 2. Phần việc phụ trách

Trong nhóm mình phụ trách vai trò **Người 2 (Tool Declarations + Custom Tools + Unit Tests + Bonus ≥ 4 Tools)**. Cụ thể:

- **CP2 (`starter_v0/artifacts/tools.yaml`):** Viết lại toàn bộ mô tả (`description`) và quy ước tham số (`parameters`) cho 10 tool gốc qua các vòng lặp tối ưu `v2`, `v3` và `v4`, tách bạch rõ ranh giới `DÙNG KHI` / `KHÔNG DÙNG KHI` và chuẩn hóa kiểu dữ liệu tham số.
- **CP3 & Bonus (`starter_v0/tools/<name>/` + `starter_v0/tools/__init__.py`):** Thiết kế và lập trình **4 tool mới hoàn toàn** của nhóm để đạt mốc **Bonus +3 điểm (`≥ 4 tool do nhóm tự viết`)**:
  1. `github_search` (`starter_v0/tools/github_search/tool.py`, `TOOL.md`)
  2. `hf_models` (`starter_v0/tools/hf_models/tool.py`, `TOOL.md`)
  3. `hn_search` (`starter_v0/tools/hn_search/tool.py`, `TOOL.md`)
  4. `pypi_info` (`starter_v0/tools/pypi_info/tool.py`, `TOOL.md`)
- **CP3 (`starter_v0/tests/test_tools_todo.py`):** Viết **21 hàm unit test** (tổng cộng 34 test item khi parametrize, ≥ 4–7 test/tool) kiểm thử offline bằng `fake_http` cho cả 4 tool mới, bao phủ happy path, input xấu từ model và nhánh lỗi API/mạng.
- **CP4 (`starter_v0/data/eval_group.json` & `starter_v0/data/eval_research_extension.json`):** Thiết kế case `G05_custom_tools_routing` trong bộ eval nhóm 10 case và các case đơn lẻ `E11`–`E14` trong bộ extension để kiểm tra khả năng agent route chính xác tới cả 4 tool mới.

## 3. Đóng góp cụ thể

**1. Tối ưu Tool Declarations (`starter_v0/artifacts/tools.yaml`) qua `v2` → `v3` → `v4`**

- **Ở `v2` (PR #3, commit `b4e39cb`):**
  - Từ phân tích run `v1` của bạn Đỗ Hoàng Vũ (tester), mình nhận thấy 3 case FAIL (`R10`, `R12`, `G01`) đều là lỗi `wrong_arg_value`: agent đã gọi đúng `clarify` và `lookup` nhưng bỏ trống `response_type` hoặc chọn sai `timeframe="day"` cho câu hỏi `"tháng này"`.
  - Mình đặt giả thuyết: đưa `response_type` vào `required: [question, response_type]` của `clarify` và viết rõ quy ước ánh xạ mốc thời gian (`hôm nay -> day`, `tuần này -> week`, `tháng này -> month`, `năm nay -> year`) cùng quy ước định dạng `screenname` (bỏ `@`), `query` (ngắn gọn, không chép từ chỉ nguồn/thời gian) trong `tools.yaml` sẽ triệt tiêu lỗi `wrong_arg_value`.
  - Kết quả đo `v2` (`runs/v2_B_base_openrouter_20261110T191207255603.json`): Base tăng từ **18/20 (0.90) lên 19/20 (0.95)**, Group tăng từ **7/9 lên 8/9**, sửa thành công `R10`, `R12`, `G01` và `GM03`.
- **Ở `v3` (PR #6, commit `b293c41`):**
  - Khi đọc kết quả `v2`, mình và Vũ phát hiện 2 lỗi hồi quy (regression) do mô tả trong `v2` gây ra:
    1. `GM02` (group): Do mô tả `clarify` dùng từ quá cứng nhắc, khi người dùng ở lượt cuối đã nói `"Ừ, nội dung ok, mình xác nhận gửi"`, agent vẫn gọi `clarify(yes_no)` hỏi lại thay vì gọi `send(confirmed=true)`.
    2. `M06` (base): Do mô tả `lookup` có câu gợi ý `"Có thể gọi CÙNG LƯỢT với social_search"`, nên khi người dùng bảo `"Bỏ Twitter đi, tìm trên web thôi"`, model tự động gọi thừa cả `social_search` của lượt trước.
  - Mình sửa lại `clarify`/`send` (nếu ở lượt tin nhắn mới nhất người dùng đã xác nhận đồng ý thì gọi ngay `send(confirmed=true)`, chỉ hỏi `clarify(yes_no)` khi chưa có xác nhận) và bỏ câu gợi ý gọi kèm trong `lookup`/`social_search`, đồng thời viết tổng quát hóa toàn bộ mô tả để không phụ thuộc câu chữ cụ thể của bộ eval.
  - Kết quả đo `v3` (`runs/v3_B_base_openrouter_20261110T193230070343.json` và `runs/v3_B_group_openrouter_20261110T193308629861.json`): Base đạt **20/20 (1.00)** và Group đạt **10/10 (1.00)**.
- **Ở `v4` (PR #8, commit `8bfb987`):** Mở rộng khai báo thêm 3 tool mới (`hf_models`, `hn_search`, `pypi_info`) với ranh giới âm bản (`KHÔNG DÙNG KHI`) rõ ràng trong `lookup` và các tool chuyên biệt. Kết quả đo `v4` (`runs/v4_B_base_openrouter_20261110T200626400416.json`, `runs/v4_B_group_openrouter_20261110T200706447380.json`, `runs/v4_B_extension_openrouter_20261110T200748658442.json`): giữ nguyên **Base 20/20 (1.00)**, **Group 10/10 (1.00)** (case `G05_custom_tools_routing` gọi song song cả 4 tool mới PASS), và **Extension đạt 13/14** (cả 4 case `E11`–`E14` của 4 tool mới đều PASS).

**2. Xây dựng 4 Custom Tools (CP3 + Bonus ≥ 4 tool mới) và bộ Unit Test Offline**

- Mình thiết kế và cài đặt 4 công cụ nghiên cứu bổ trợ trực tiếp cho bài toán AI Research Agent, tất cả đều sử dụng REST API công khai miễn phí (`requires_env: []`) và chuẩn hóa đầu ra về khuôn `{"tool", ..., "items": [{"title", "url", "source", "summary", ...}]}` để tương thích với tool `format`:
  1. **`github_search`** (`tools/github_search/`): Tìm repository mã nguồn mở trên GitHub REST API (`api.github.com/search/repositories`) theo `query`, `language`, `limit` (sắp xếp theo `stars`).
  2. **`hf_models`** (`tools/hf_models/`): Tìm model AI/LLM open-weight trên Hugging Face Hub API (`huggingface.co/api/models`) theo `query`, `task` (`pipeline_tag`), `limit` (sắp xếp theo `downloads`).
  3. **`hn_search`** (`tools/hn_search/`): Tìm bài đăng và thảo luận kỹ thuật trên Hacker News qua Algolia API (`hn.algolia.com/api/v1/search` cho `sort_by='points'` và `search_by_date` cho `sort_by='date'`).
  4. **`pypi_info`** (`tools/pypi_info/`): Tra cứu thông tin phát hành chính thức của gói thư viện Python trên PyPI JSON API (`pypi.org/pypi/<package>/json`), lấy phiên bản mới nhất, `requires_python`, `license` và `summary`.
- Cả 4 tool đều tuân thủ nghiêm ngặt quy tắc **defensive tool design** (RUBRIC C4): kiểm tra tham số đầu vào trước khi gọi mạng, ép trần `limit <= 10`, từ chối `limit <= 0` hoặc enum sai, và bắt mọi lỗi HTTP/timeout/dữ liệu hỏng để trả về `{"error": ..., "next_step": ...}` thay vì raise exception.
- Trong `starter_v0/tests/test_tools_todo.py`, mình viết **21 hàm unit test** (7 hàm cho `github_search`, 5 hàm cho `hf_models`, 5 hàm cho `hn_search`, 4 hàm cho `pypi_info`), tất cả mock mạng bằng `fake_http`. Toàn bộ suite đạt **137 passed, 0 skipped, 0 failed**.

## 4. Bằng chứng

- **File/commit/PR chính:**
  - PR #3 (`da76c7f`, commit `b4e39cb`): Viết lại toàn bộ `starter_v0/artifacts/tools.yaml` cho vòng `v2` (tăng Base từ 0.90 lên 0.95).
  - PR #6 (`9c68583`, commit `b293c41`): Thêm tool `github_search` (`TOOL.md`, `tool.py`), đăng ký trong `tools/__init__.py`, viết 7 hàm unit test trong `tests/test_tools_todo.py`, thêm case `G05` trong `data/eval_group.json`, và sửa lỗi hồi quy `GM02`/`M06` trong `artifacts/tools.yaml` cho vòng `v3` (đạt 1.00 Base và 10/10 Group).
  - PR #8 (`2e8cd23`, commit `8bfb987`): Bổ sung 3 tool Bonus (`hf_models`, `hn_search`, `pypi_info`), 14 hàm unit test mới (nâng tổng số test toàn suite lên `137 passed, 0 skipped`), cập nhật case `G05` + `E11..E14`, và báo cáo cá nhân `report/team/2A202603937_BuiDangNhatNguyen.md`.
  - Run files kiểm chứng: `runs/v2_B_base_openrouter_20261110T191207255603.json`, `runs/v3_B_base_openrouter_20261110T193230070343.json`, `runs/v3_B_group_openrouter_20261110T193308629861.json`, `runs/v4_B_base_openrouter_20261110T200626400416.json`, `runs/v4_B_group_openrouter_20261110T200706447380.json`, `runs/v4_B_extension_openrouter_20261110T200748658442.json`.
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Mình sử dụng trợ lý AI trong IDE để hỗ trợ tra cứu cấu trúc payload của GitHub REST API, Hugging Face Hub API, Hacker News Algolia API, PyPI JSON API và rà soát cú pháp YAML/pytest.
  - Các quyết định kỹ thuật do mình trực tiếp kiểm soát và lựa chọn: chọn tổ hợp 4 công cụ nghiên cứu không cần API key trả phí để cả nhóm và người chấm chạy live được ngay; quyết định xử lý `limit <= 0` trả về error dict thay vì âm thầm đổi về mặc định 5; và điều chỉnh ranh giới câu chữ giữa `clarify` với `send` để cân bằng giữa case `G04` (ép gửi không xác nhận) và `GM02` (đã xác nhận gửi).
  - Cách tự kiểm tra: sau mỗi lần chỉnh sửa, mình chạy `pytest -v` (đảm bảo `137 passed, 0 skipped, 0 failed` và `test_tool_contract.py` xanh 100%) trước khi mở Pull Request và phối hợp cùng bạn Vũ chạy `run_eval.py` kiểm chứng trên `eval_base.json`, `eval_group.json` và `eval_research_extension.json`.

## 5. Tự đánh giá

- **Học được:** Hiểu rõ sự khác biệt giữa việc tối ưu System Prompt (định hình quy trình suy luận tổng quát) và tối ưu Tool Declarations (`tools.yaml` là nơi quyết định trực tiếp việc model phân biệt các tool gần giống nhau và điền đúng định dạng tham số). Ngoài ra mình học được cách thiết kế tool phòng vệ (defensive programming) để không bao giờ làm sập vòng lặp của agent.
- **Làm tốt:** Thiết kế mô tả `tools.yaml` có cấu trúc rõ ràng (`DÙNG KHI` / `KHÔNG DÙNG KHI`), nhanh chóng tìm ra nguyên nhân 2 lỗi hồi quy ở `v2` để đưa `v3` đạt điểm tuyệt đối `20/20` (Base) và `10/10` (Group), đồng thời xây dựng trọn vẹn 4 tool mới kèm bộ unit test chặn toàn bộ biên đầu vào xấu.
- **Chưa tốt:** Ở bản `v2` đầu tiên, mình viết điều kiện chặn của `clarify` hơi cứng và thêm gợi ý gọi song song trong `lookup`, dẫn tới việc sửa được lỗi cũ nhưng lại sinh ra 2 regression ở hội thoại nhiều lượt (`GM02` và `M06`).
- **Rút ra:** Khi viết prompt hoặc tool description cho agent nhiều lượt (multi-turn), không được chỉ nhìn vào câu hỏi đơn lẻ (single-turn) mà phải luôn đặt câu hỏi: *"Nếu ở lượt tiếp theo người dùng xác nhận đồng ý hoặc đổi ý chuyển sang nguồn khác, quy tắc này có vô tình khóa cứng hành vi của agent hay không?"*
