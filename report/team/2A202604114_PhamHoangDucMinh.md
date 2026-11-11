# Báo cáo cá nhân — Phạm Hoàng Đức Minh - 2A202604114

## 1. Thông tin thành viên

- Họ tên: Phạm Hoàng Đức Minh
- MSSV: 2A202604114
- Email: ducminh03102005@gmail.com
- GitHub: PH31M

## 2. Phần việc phụ trách

Phụ trách vòng lặp tối ưu dựa trên bằng chứng cho agent: chạy baseline v0, tối ưu `system_prompt.md` và `tools.yaml` qua v1–v7, viết bộ 10 eval case của nhóm (`data/eval_group.json`), ghi `version_log.csv`, và điền các bảng B1, B2, B3, B4, B5a trong `group_report.md`. Ngoài ra:

- viết unit test cho hai tool `openalex` và `semantic_scholar` và sửa lỗi đăng ký tool `semantic_scholar`;
- chạy 3 phiên chat live để lấy transcript;
- tích hợp (merge) các nhánh của các thành viên khác vào nhánh `optimize`.

## 3. Đóng góp cụ thể

**Baseline v0 và phân tích lỗi (CP1).** Chạy base eval với prompt và tool declaration gốc của starter (model `openai/gpt-4o-mini` qua OpenRouter): 14/20 pass (case_accuracy 0.70, tool_routing 0.75, argument 0.70). Đọc `failures` và `observed_mismatch` trong run JSON, gán loại lỗi cho từng case FAIL và viết bảng B2. Nguyên nhân chính là các chỉ dẫn xấu cố ý trong prompt gốc (đoán thay vì hỏi, gửi ngay không xác nhận, ép làm một bước): R10 và R11 bị đoán tài khoản và URL, R12 gọi `send` ngay, R08 và R14 gọi `send` cho câu ngoài phạm vi.

**Tối ưu v1–v3 (CP2).** Mỗi version đặt một giả thuyết, chạy lại base eval và ghi hash cùng metric trước/sau:

| Version | Thay đổi | Kết quả | Nhận xét |
|---|---|---|---|
| v1 | Bỏ chỉ dẫn xấu; thêm rule hỏi lại bằng `clarify` và xác nhận trước `send` | 16/20 (0.80) | Sửa R08, R10, R11, R14 (và R13 ngoài dự kiến). R12 vẫn FAIL. Hồi quy R01, M02, M06 vì bỏ "pick one tool" mà chưa có rule thay thế |
| v2 | Thêm rule routing theo loại yêu cầu (timeline / social_search / lookup / fetch / không tool) và điều kiện chỉ `clarify` khi thật sự thiếu thông tin | 18/20 (0.90) | Sửa R01, M02. Còn M06 (gọi thừa `social_search`) và R12 (`response_type` sai) |
| v3 | Viết rule đổi nguồn và rule xác nhận thành mệnh lệnh cụ thể; viết lại description mọi tool trong `tools.yaml` theo dạng làm gì / DÙNG khi / KHÔNG dùng khi, kèm convention args và boundary `send` | 17/20 (0.85) | Giả thuyết không được xác nhận: R12 và M06 vẫn FAIL, thêm hồi quy M01 |

**Tối ưu v4–v7 sau khi nhóm có thêm 6 tool mới.** Các run v0–v3 dùng `tools_hash` cũ, nên trước v4 tôi chạy lại prompt v3 trên `tools.yaml` hiện hành (16 tool) để có `metric_before` hợp lệ: base 18/20 (0.90), group 7/10. Lần đo lại này không sửa artifact nào nên không tính là một version; nó được ghi trong dòng v4 của `version_log.csv`.

| Version | Thay đổi | Base | Group (bộ case cũ) | Nhận xét |
|---|---|---:|---:|---|
| v4 | Thêm rule routing cho `papers`, `semantic_scholar`, `openalex`, `paper_text`, `policy`, `format` và 4 tool xử lý danh sách đã thu thập; thiếu danh sách thì `clarify`, không gọi tool với danh sách rỗng | 19/20 (0.95) | 9/10 | Giả thuyết đúng: G02 từ FAIL sang PASS. Còn R12 và G07 |
| v5 | Dòng `lookup`: nếu không nhắc tweet / X / Twitter thì chỉ gọi `lookup`, không thêm `social_search` | 18/20 (0.90) | 10/10 | G07 PASS. Base giảm vì R12 và M01 FAIL, trong đó M01 không liên quan dòng đã sửa |
| v6 | Thêm câu: rule xác nhận `send` được ưu tiên hơn rule hỏi thiếu thông tin | 17/20 (0.85) | 10/10 | **Giả thuyết không được xác nhận**: R12 vẫn hỏi `text`, thêm hồi quy R10. Tôi bỏ câu này và v7 quay lại prompt v5 |
| v7 | Mô tả `limit` của `timeline`: nếu người dùng nêu số cụ thể (kể cả bằng 5) thì luôn điền `limit` | 19/20 (0.95) | 9/10 | M01 PASS nhưng M01 cũng PASS ở 2 run trước khi chưa sửa, nên chưa kết luận được. G08 FAIL (dao động) |

Kết quả giữa các lần chạy dao động (M01 và G08 đổi PASS/FAIL với cùng prompt và tools), nên chênh 1 case (0.05) chưa đủ để chắc một version tốt hơn. R12 là case duy nhất FAIL ở mọi run từ v1 đến v7.

**Eval nhóm (CP4).** Viết 10 case trong `data/eval_group.json` (5 single turn và 5 multi turn), mỗi case có `failure_type`, `expect` và `metadata.what_it_tests`. Bản đầu (G01–G10) chạy với v3 được 8/10 pass. Sau đó tôi thay 5 case (G03, G04, G07, G09, G10) bằng G11–G15 để bộ case route tới cả 6 tool mới của nhóm: `deduplicate` (G01, G02), `semantic_scholar` (G11), `openalex` (G12), `filter_sources` (G13), `filter_by_date` (G14), `validate_citations` (G15). Các case giữ lại: convention args của `lookup` (G05), hỏi lại rồi bổ sung (G06), xác nhận rồi mới gửi (G08). Run group trên bản hiện tại (`v7_B_group_openrouter_20261110T230626499597.json`): 10/10 pass, 0 lỗi provider. Viết bảng B3 kèm nhận xét từng case.

**Unit test và sửa lỗi đăng ký tool.** Sau khi merge hai tool của Huy, `tools/__init__.py` đăng ký nhầm khoá `"senmatic_scholar"`, khiến 2 contract test FAIL. Tôi sửa lại thành `"semantic_scholar"`, rồi viết 31 test cho hai tool (14 cho `openalex`, 17 cho `semantic_scholar`) trong `tests/test_tools_todo.py`. Test dùng `fake_http`, assert cả request gửi đi lẫn kết quả đã chuẩn hóa, và gồm: `query` rỗng, `max_results` ngoài khoảng, `sort_by` sai, bản ghi thiếu field, HTTP 429/404/503, timeout, retry và giãn cách 1 giây của `semantic_scholar`. Toàn suite `pytest`: 213 passed, 0 skipped. Lỗi đăng ký này là ví dụ unit test bắt được mà eval không bắt được (eval không có case nào kỳ vọng `semantic_scholar`), đã ghi ở B5a.

**Chat live (CP5).** Chạy 3 phiên bằng `chat.py` trên artifact v7: yêu cầu thường (`lookup`), thiếu thông tin rồi bổ sung (hỏi lại tài khoản, rồi `timeline(sama, limit=3)`), và yêu cầu gửi (`clarify` yes/no, rồi `send(confirmed=true)` sau khi đồng ý). Điền bảng B4 kèm nhận xét: `send` lỗi vì chưa cấu hình Telegram nên không có tin nào được gửi thật.

**Dọn bằng chứng.** Loại khỏi repo run v0 thứ hai (do Huy chạy, 15/20) và file `analysis/base_runs.csv` parse từ run đó, vì nó trùng nhãn `v0` và không có trong `version_log.csv`.

**Tích hợp nhánh.** Merge `feat/tool-eval`, `feat/ui-report`, `eval_2` và pull request #2 vào `optimize`, để prompt, tool mới của các bạn và UI chạy cùng một bản.

## 4. Bằng chứng

- Commit của tôi: `2f25a54` (system_prompt_v0), `f60e41e` (system_prompt_v1), `f893bbc` (system_prompt_v2), `bbc847c` (system_prompt_v3), `f29fd57` (eval_group_v3), `5fb6e01` (v4–v7, eval nhóm cho 6 tool mới, test, transcript) và các commit merge trên nhánh `optimize`.
- Run JSON hợp lệ (`provider_error_cases == 0`, `measured_cases == total_cases`), trong `starter_v0/runs/`:
  - Base: `v0_B_base_openrouter_20261110T174519840832.json`, `v1_B_base_openrouter_20261110T180453970452.json`, `v2_B_base_openrouter_20261110T182517635389.json`, `v3_B_base_openrouter_20261110T184418744227.json`, `v4_B_base_openrouter_20261110T224558978889.json`, `v5_B_base_openrouter_20261110T224819699492.json`, `v6_B_base_openrouter_20261110T225025242839.json`, `v7_B_base_openrouter_20261110T225246707082.json`
  - Đo lại v3 trên 16 tool: `v3-tools17_B_base_openrouter_20261110T224250589557.json` và `v3-tools17_B_group_openrouter_20261110T224332128774.json` (tên file giữ nhãn lúc chạy)
  - Group: `v3_B_group_openrouter_20261110T192836267042.json`, `v4_B_group_…T224634984917.json`, `v5_B_group_…T224846947529.json`, `v6_B_group_…T225055601556.json`, `v7_B_group_…T225319237135.json` (bộ case cũ) và `v7_B_group_openrouter_20261110T230626499597.json` (bộ case hiện tại, 10/10)
- Transcript: `starter_v0/transcripts/v7_openrouter_20261110T230951533091.transcript.json`, `…T231006560268.transcript.json`, `…T231021464746.transcript.json`.
- File: `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/artifacts/version_log.csv`, `starter_v0/data/eval_group.json`, `starter_v0/tests/test_tools_todo.py`, `starter_v0/analysis/pytest_output.txt`; bảng B1, B2, B3, B4, B5a trong `report/team/group_report.md`.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: dùng Claude Code để đọc repo, đối chiếu run JSON với `version_log.csv`, soạn báo cáo này, và (với v4–v7, 31 test mới, eval nhóm G11–G15, transcript live) soạn thay đổi và chạy lệnh theo mục tiêu tôi đặt ra; tôi chọn giả thuyết và duyệt kết quả. Mọi số liệu (số case pass, accuracy, hash, tên run file) đối chiếu với trường `summary` trong từng run JSON và với `version_log.csv`, không lấy từ trí nhớ. Mỗi lần sửa prompt hoặc `tools.yaml` đều chạy lại eval thật để kiểm tra; kết quả xấu đi (v3, v6) vẫn được ghi nguyên trạng. Transcript được kiểm tra không chứa API key trước khi đưa vào repo.

## 5. Tự đánh giá

Điểm làm tốt: chỉ dùng run hợp lệ làm bằng chứng, mỗi version có hash và giả thuyết riêng, và ghi trung thực cả khi kết quả xấu đi (v3 giảm từ 0.90 xuống 0.85, v6 không xác nhận giả thuyết). Qua 7 vòng tôi rút ra hai điều: một dòng rule thêm vào prompt có thể sửa một case nhưng làm hồi quy case khác (v5, v6), và với một model, một run duy nhất chưa đủ để kết luận vì kết quả dao động giữa các lần chạy. Tôi cũng thấy unit test bắt được lỗi mà eval không chạm tới (lỗi đăng ký `semantic_scholar`).

Hạn chế:
- v3 đổi cả `system_prompt.md` lẫn `tools.yaml` trong một lần, nên không tách được tác động của từng phần, trái với nguyên tắc một giả thuyết mỗi version. Nhận định ban đầu rằng hồi quy M01 do mô tả `limit` mới chưa chắc đúng: M01 đổi PASS/FAIL giữa các run khi chưa sửa gì.
- Mỗi version chỉ có một run base và một run group, nên chênh lệch 1 case (0.05) nằm trong mức dao động và chưa chứng minh được version nào tốt hơn.
- R12 (xin xác nhận `yes_no` trước khi gửi khi nội dung mơ hồ) vẫn FAIL ở mọi run từ v1 đến v7 và chưa có hướng sửa hiệu quả. Một hướng đã thử (v6) không thành công.
- Các run group của v3–v7 ở B1 chạy trên bộ case cũ; sau khi thay 5 case ở bộ group, chỉ có một run trên bộ mới (v7), nên chưa so sánh các version trên bộ mới được.
- Harness chỉ chấm tên tool và các arg đơn giản, không so sánh được danh sách `items`. Ở bộ case cũ, G04 (làm thơ) được tính PASS dù model viết luôn bài thơ thay vì từ chối, nên các case dạng "từ chối" cần review thủ công. G11 và G12 chỉ kiểm tra rule routing do nhóm tự viết.
- Chat live: `send` chưa gửi thật lên Telegram do chưa cấu hình token, nên chưa có bằng chứng `status: sent`. Agent trả lời tiếng Anh cho câu hỏi tiếng Việt ở phiên 1, và khi `send` lỗi thì không nêu nguyên nhân thật.
- Hai tool của Huy chưa có unit test khi được merge; test do tôi bổ sung sau. Tôi chưa làm bonus Telegram và Small Local Model.
