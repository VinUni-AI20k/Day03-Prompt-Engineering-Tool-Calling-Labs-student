# Báo cáo cá nhân — Phạm Hoàng Đức Minh - 2A202604114

## 1. Thông tin thành viên

- Họ tên: Phạm Hoàng Đức Minh
- MSSV: 2A202604114
- Email: ducminh03102005@gmail.com
- GitHub: PH31M

## 2. Phần việc phụ trách

Phụ trách vòng lặp tối ưu dựa trên bằng chứng cho agent: chạy baseline v0, tối ưu `system_prompt.md` và `tools.yaml` qua v1–v3, viết bộ 10 eval case của nhóm (`data/eval_group.json`), ghi `version_log.csv` và điền các bảng B1, B2, B3 trong `group_report.md`. Ngoài ra tích hợp (merge) các nhánh của các thành viên khác vào nhánh `optimize`.

## 3. Đóng góp cụ thể

**Baseline v0 và phân tích lỗi (CP1).** Chạy base eval với prompt và tool declaration gốc của starter (model `openai/gpt-4o-mini` qua OpenRouter): 14/20 pass (case_accuracy 0.70, tool_routing 0.75, argument 0.70). Đọc `failures` và `observed_mismatch` trong run JSON, gán loại lỗi cho từng case FAIL và viết bảng B2. Nguyên nhân chính là các chỉ dẫn xấu cố ý trong prompt gốc (đoán thay vì hỏi, gửi ngay không xác nhận, ép làm một bước): R10 và R11 bị đoán tài khoản và URL, R12 gọi `send` ngay, R08 và R14 gọi `send` cho câu ngoài phạm vi.

**Tối ưu v1–v3 (CP2).** Mỗi version đặt một giả thuyết, chạy lại base eval và ghi hash cùng metric trước/sau:

| Version | Thay đổi | Kết quả | Nhận xét |
|---|---|---|---|
| v1 | Bỏ chỉ dẫn xấu; thêm rule hỏi lại bằng `clarify` và xác nhận trước `send` | 16/20 (0.80) | Sửa R08, R10, R11, R14 (và R13 ngoài dự kiến). R12 vẫn FAIL. Hồi quy R01, M02, M06 vì bỏ "pick one tool" mà chưa có rule thay thế |
| v2 | Thêm rule routing theo loại yêu cầu (timeline / social_search / lookup / fetch / không tool) và điều kiện chỉ `clarify` khi thật sự thiếu thông tin | 18/20 (0.90) | Sửa R01, M02. Còn M06 (gọi thừa `social_search`) và R12 (`response_type` sai) |
| v3 | Viết rule đổi nguồn và rule xác nhận thành mệnh lệnh cụ thể; viết lại description mọi tool trong `tools.yaml` theo dạng làm gì / DÙNG khi / KHÔNG dùng khi, kèm convention args và boundary `send` | 17/20 (0.85) | Giả thuyết không được xác nhận: R12 và M06 vẫn FAIL, thêm hồi quy M01 |

**Eval nhóm (CP4).** Viết 10 case trong `data/eval_group.json` (5 single turn và 5 multi turn), mỗi case có `failure_type`, `expect` và `metadata.what_it_tests`. Bản đầu (G01–G10) chạy với v3 được 8/10 pass. Sau đó tôi thay 5 case (G03, G04, G07, G09, G10) bằng G11–G15 để bộ case route tới cả 6 tool mới của nhóm: `deduplicate` (G01, G02), `semantic_scholar` (G11), `openalex` (G12), `filter_sources` (G13), `filter_by_date` (G14), `validate_citations` (G15). Các case giữ lại: convention args của `lookup` (G05), hỏi lại rồi bổ sung (G06), xác nhận rồi mới gửi (G08). Run group trên bản hiện tại (`v7_B_group_openrouter_20261110T230626499597.json`): 10/10 pass, 0 lỗi provider. Viết bảng B3 kèm nhận xét từng case.

**Tích hợp nhánh.** Merge `feat/tool-eval`, `feat/ui-report` và `eval_2` vào `optimize`, để prompt, tool mới của các bạn và UI chạy cùng một bản.

## 4. Bằng chứng

- Commit của tôi: `2f25a54` (system_prompt_v0), `f60e41e` (system_prompt_v1), `f893bbc` (system_prompt_v2), `bbc847c` (system_prompt_v3), `f29fd57` (eval_group_v3) và các commit merge trên nhánh `optimize`.
- Run JSON hợp lệ (20/20 case đo được, `provider_error_cases == 0`), trong `starter_v0/runs/`:
  - `v0_B_base_openrouter_20261110T174519840832.json`
  - `v1_B_base_openrouter_20261110T180453970452.json`
  - `v2_B_base_openrouter_20261110T182517635389.json`
  - `v3_B_base_openrouter_20261110T184418744227.json`
  - `v3_B_group_openrouter_20261110T192836267042.json` (10/10 case đo được)
- File: `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/artifacts/version_log.csv`, `starter_v0/data/eval_group.json`; bảng B1, B2, B3 trong `report/team/group_report.md`.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: dùng Claude Code để đọc repo, đối chiếu run JSON với `version_log.csv` và soạn báo cáo này. Mọi số liệu (số case pass, accuracy, hash, tên run file) đối chiếu lại với trường `summary` trong từng run JSON và với `version_log.csv`, không lấy từ trí nhớ. Mỗi lần sửa prompt hoặc `tools.yaml` đều chạy lại eval thật để kiểm tra, không kết luận trước khi có run.

## 5. Tự đánh giá

Điểm làm tốt: chỉ dùng run hợp lệ làm bằng chứng, mỗi version có hash và giả thuyết riêng, và ghi trung thực cả khi kết quả xấu đi (v3 giảm từ 0.90 xuống 0.85). Từ việc này tôi hiểu rõ hơn cách đọc `observed_mismatch` để phân biệt lỗi chọn tool, lỗi args và lỗi hỏi lại, và rút ra rằng một rule thiếu ví dụ cụ thể thì model nhỏ vẫn chọn theo cảm nhận.

Hạn chế:
- v3 đổi cả `system_prompt.md` lẫn `tools.yaml` trong một lần, nên không tách được tác động của từng phần, trái với nguyên tắc một giả thuyết mỗi version. Hồi quy M01 (thiếu `limit=5`) nhiều khả năng do mô tả `limit` mới, nhưng tôi chưa chạy một run riêng để kiểm chứng.
- Sau v3 vẫn còn 3 case FAIL trên bộ base (R12, M01, M06) và 2 case FAIL trên bộ nhóm (G02, G07). Tôi chưa làm v4 để sửa các case này.
- Các run v0–v3 chạy trước khi nhóm thêm các tool mới, nên `tools_hash` của chúng khác với `tools.yaml` hiện tại và prompt chưa có rule routing cho các tool mới. Đây là lý do G02 gọi `deduplicate` với danh sách rỗng thay vì hỏi lại.
- Scorer chỉ kiểm tra có gọi tool hay không. Ở bộ case cũ, G04 (làm thơ) được tính PASS dù model viết luôn bài thơ thay vì từ chối, nên cần review thủ công những case dạng "từ chối". Ngoài ra harness không so sánh được danh sách `items`, nên các case của tool lọc chỉ chấm tên tool và các arg đơn giản.
- Chưa tham gia viết tool mới hay unit test, và chưa làm bonus nào.
