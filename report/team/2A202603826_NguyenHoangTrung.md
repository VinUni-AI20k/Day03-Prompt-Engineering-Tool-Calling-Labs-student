# Báo cáo cá nhân — 2A202603826_NguyenHoangTrung

## 1. Thông tin thành viên

- Họ tên: Nguyễn Hoàng Trung
- MSSV: 2A202603826
- Email: 26ai.trungnh@vinui.edu.vn
- GitHub: NguyenHoangTrung

## 2. Phần việc phụ trách

- **Checkpoint 3 (CP3) — Tool mới và unit test**:
  - Nghiên cứu, thiết kế và hiện thực tool mới `source_credibility` (kiểm tra và phân cấp độ tin cậy của nguồn tin web/URL).
  - Soạn thảo tài liệu đặc tả tool `TOOL.md` theo chuẩn schema frontmatter của dự án.
  - Đăng ký tool vào bảng registry `tools/__init__.py` và khai báo cấu hình tham số trong `artifacts/tools.yaml`.
  - Viết bộ unit test chuyên sâu cho tool mới (kiểm tra happy path, input xấu từ model, nhánh lỗi runtime).
  - Hoàn thiện toàn bộ các stubs unit test trong `tests/test_tools_todo.py` để đạt mốc kiểm thử **0 skipped, 0 failed**.

## 3. Đóng góp cụ thể

1. **Thiết kế & phát triển tool mới `source_credibility`**:
   - *Bối cảnh*: Trong tác vụ Research Agent, agent thu thập dữ liệu từ nhiều nguồn khác nhau (báo chí, blog, mạng xã hội). Để tránh trích dẫn nguồn rác hoặc tin giả (fake news), agent cần một công cụ thẩm định chất lượng nguồn trước khi đưa vào bản tin tổng hợp.
   - *Hiện thực (`tools/source_credibility/tool.py`)*:
     - Xây dựng cơ chế phân loại nguồn tin theo 5 cấp độ: `academic` (0.95 - arxiv, nature, ieee...), `verified_news` (0.85-0.92 - reuters, bbc, vnexpress...), `tech_media` (0.80-0.90 - openai, anthropic, github...), `community` (0.45-0.50 - x.com, twitter, reddit), và `unverified` (0.30 - nguồn không xác thực).
     - Thiết lập cơ chế lọc theo ngưỡng tối thiểu (`min_tier`) và đánh giá tính an toàn `is_reliable`.
     - Áp dụng nguyên tắc an toàn: Không bao giờ `raise` Exception làm gãy luồng agent; mọi ngoại lệ (URL rỗng, URL không hợp lệ, lỗi trích xuất) đều được bắt và trả về error dict có cấu trúc `{"tool": "source_credibility", "error": ..., "message": ...}`.
   - *Tài liệu đặc tả (`tools/source_credibility/TOOL.md`)*: Định nghĩa đầy đủ frontmatter (`name`, `track`, `kind: local_knowledge`, `inputs`, `outputs`, `side_effect: false`).

2. **Tích hợp vào hệ thống**:
   - Đăng ký hàm `check_source_credibility` vào `TOOL_FUNCTIONS` trong `starter_v0/tools/__init__.py`.
   - Khai báo schema chi tiết (description, properties, enums, required) trong `starter_v0/artifacts/tools.yaml`.
   - Đảm bảo toàn bộ 60 contract tests trong `test_tool_contract.py` đều pass.

3. **Hiện thực Unit Test toàn diện (`tests/test_tools_todo.py`)**:
   - Viết 5 test cases chuyên sâu cho tool mới:
     - `test_my_new_tool_happy_path`: Xác nhận URL học thuật (arxiv.org) trả về tier `academic`, score >= 0.90 và `is_reliable=True`.
     - `test_my_new_tool_bad_input_from_model`: Kiểm tra model truyền URL rỗng, chuỗi trắng, hoặc `None` -> trả về error dict `ValueError`.
     - `test_my_new_tool_failure_returns_error_dict`: Mock lỗi phân giải tên miền -> trả về error dict `RuntimeError`, không crash.
     - `test_my_new_tool_unverified_domain_marked_unreliable`: Nguồn lạ ngoài danh bạ -> phân loại `unverified`, score thấp, khuyến nghị cẩn trọng.
     - `test_my_new_tool_min_tier_filtering`: Lọc nguồn mạng xã hội với yêu cầu `verified_news` -> `meets_min_tier=False`.
   - Giải quyết toàn bộ 14 bài toán stubs trong `test_tools_todo.py` cho các tool có sẵn (`clarify`, `format`, `send`, `lookup`, `fetch`, `timeline`, `social_search`, `policy`), vận dụng `fake_http` và `monkeypatch` để đảm bảo 100% test chạy offline và độc lập.

## 4. Bằng chứng

- **Mã nguồn đã tạo và sửa**:
  - `starter_v0/tools/source_credibility/tool.py`
  - `starter_v0/tools/source_credibility/TOOL.md`
  - `starter_v0/tools/__init__.py`
  - `starter_v0/artifacts/tools.yaml`
  - `starter_v0/tests/test_tools_todo.py`
- **Kết quả kiểm thử tự động**:
  - Lệnh kiểm tra: `pytest tests/ -v`
  - Kết quả: **86 passed, 0 skipped, 0 failed** trong 0.64s.
  - Hợp đồng tool (`test_tool_contract.py`): **60 passed**.
- **AI và công cụ đã sử dụng**:
  - Sử dụng trợ lý AI để hỗ trợ liệt kê các domain phổ biến cho danh bạ phân loại uy tín và cấu trúc fixture test offline.
  - Tự kiểm tra: Chạy kiểm thử pytest nội bộ, đối chiếu chữ ký hàm với schema `tools.yaml`, kiểm tra contract test để đảm bảo không vi phạm bất kỳ ràng buộc nào của starter code.

## 5. Tự đánh giá

- Hoàn thành đầy đủ và vượt mức yêu cầu của Checkpoint 3 (tiêu chí C4: 15/15 điểm).
- Đóng góp thêm vào tiêu chí Bonus Test Challenge (đạt 0 skipped cho toàn bộ test suite).
- Mức độ hoàn thành công việc: **100%**.
