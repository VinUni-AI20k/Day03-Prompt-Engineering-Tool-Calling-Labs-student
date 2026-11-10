# Báo cáo cá nhân — Nguyễn Duy Hưng (MSSV: 2A202604110)

## 1. Thông tin thành viên

- Họ tên: Nguyễn Duy Hưng
- MSSV: 2A202604110
- Email: 
- Lớp: K5 - L3B
- Nhóm: Nhóm Ba Khỉ

## 2. Phần việc phụ trách

- Thực hiện Checkpoint 1 (Setup, chạy baseline v0 và phân tích thất bại).
- Thực hiện Checkpoint 2 (Vòng lặp tối ưu v1 → v3 dựa trên bằng chứng).
- Tinh chỉnh `artifacts/system_prompt.md` và viết lại toàn diện `artifacts/tools.yaml`.
- Quản lý nhật ký phiên bản `artifacts/version_log.csv` và đồng bộ Bảng B1 trong `group_report.md`.

## 3. Đóng góp cụ thể

- **Baseline v0:** Chạy đánh giá ban đầu với Google Gemini API (`gemini-3.5-flash-lite`). Đo được độ chính xác 65% (13/20 cases). Lọc và phân tích 7 ca lỗi do starter prompt cố tình ép đoán bừa và vi phạm ranh giới an toàn.
- **Version v1:** Đặt giả thuyết 1, loại bỏ các chỉ dẫn sai lệch của starter prompt, bổ sung yêu cầu gọi `clarify(response_type="text")` khi thiếu thông tin bắt buộc và `clarify(response_type="yes_no")` khi người dùng yêu cầu gửi nội dung ra kênh ngoài -> Đẩy độ chính xác lên 70% (14/20 cases).
- **Version v2:** Đặt giả thuyết 2, phân định rõ ràng giữa tìm kiếm bài đăng theo chủ đề (`social_search`) và bài đăng của cá nhân thiếu tên (`clarify`), đồng thời kích hoạt luật gọi công cụ song song (`lookup` + `social_search`) khi yêu cầu đa nguồn -> Đẩy độ chính xác lên 80% (16/20 cases), Tool Routing Accuracy đạt 100%.
- **Version v3:** Đặt giả thuyết 3, viết lại toàn diện `artifacts/tools.yaml` với mô tả "Khi nào dùng / Khi nào không dùng" và quy ước tham số `query` cốt lõi (bỏ filler words như "news", "hôm nay", "latest") -> Giải quyết triệt để 4 ca lỗi `wrong_arg_value`, nâng độ chính xác lên 94.7% (18/19 measured cases).

## 4. Bằng chứng

- **File/artifacts:**
  - `starter_v0/artifacts/system_prompt.md`
  - `starter_v0/artifacts/tools.yaml`
  - `starter_v0/artifacts/version_log.csv`
  - `report/team/group_report.md` (Bảng B1)
- **File run JSON minh chứng trong `starter_v0/runs/`:**
  - `v0_B_base_gemini_20261110T174737486284.json`
  - `v1_B_base_gemini_20261110T181127878174.json`
  - `v2_B_base_gemini_20261110T182200983550.json`
  - `v3_B_base_gemini_20261110T182951613132.json`
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Sử dụng trợ lý AI Antigravity để hỗ trợ đọc và phân tích cấu trúc lỗi từ run JSON, đề xuất giả thuyết và hỗ trợ định dạng khai báo YAML.
  - Tự kiểm tra kết quả qua: `pytest tests/test_tool_contract.py` (đảm bảo hợp đồng tools.yaml khớp với code Python), script `scripts/parse_runs.py` và chạy live eval trực tiếp trên terminal với Gemini provider.

## 5. Tự đánh giá

- Hoàn thành đầy đủ các tiêu chuẩn kiểm thử của Checkpoint 1 và Checkpoint 2.
- Thực hiện đúng quy trình khoa học dựa trên bằng chứng (Evidence-driven Loop): Đặt một giả thuyết -> Thay đổi artifact -> Đo lường lại qua run JSON -> Ghi nhận log đối chiếu.
- Đóng góp: 100% trong phạm vi CP1 và CP2 của nhóm.
