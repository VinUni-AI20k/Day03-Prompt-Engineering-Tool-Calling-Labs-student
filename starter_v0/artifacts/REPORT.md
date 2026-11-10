# NoName Research Agent — Báo cáo Day 03

- Team: Nhóm NoName
- Provider/model: OpenRouter / `nvidia/nemotron-3-ultra-550b-a55b:free`

**Members:**

| Mã học viên | Họ và tên |
|---|---|
| 2A202603703 | Vương Xuân Dương |
| 2A202603715 | Dương Thái Bình |
| 2A202603689 | Vũ Hải Tuấn |

- Bản cuối: `v3+p03f49c00c387+tf71266163eeb`. Ngày hoàn thiện: 10/11/2026.

# PHẦN A — Giới thiệu agent

## A1. Agent làm được gì

Trợ lý nghiên cứu tìm tin web hoặc bài đăng X, đọc URL, tra chính sách nội bộ,
tìm paper và tổng hợp dữ liệu thành bản tin có nguồn. Tool mới loại URL trùng
trước khi tổng hợp, giữ nguồn đầu tiên và không tự sửa nội dung nguồn.

**Link dùng thử:** https://bring-documents-matching-health.trycloudflare.com

UI Streamlit, kết nối model và tool thật. Link Cloudflare là link tạm thời, chỉ
hoạt động khi máy và tiến trình Streamlit/cloudflared đang chạy. Chạy lại theo
[SUBMISSION.md](../SUBMISSION.md) nếu link hết hạn. Link này đã trả health `ok`.
Không tuyên bố đã hoàn thành trước mốc 16:30 của buổi học gốc; đây là bản hoàn thiện sau buổi lab.

## A2. Tool agent có

| Tool | Chức năng | Nhóm thêm? |
|---|---|---|
| clarify | Hỏi thông tin còn thiếu hoặc xác nhận | Không |
| timeline | Lấy bài mới từ tài khoản X đã xác định | Không |
| social_search | Tìm bài X theo chủ đề, Top/Latest | Không |
| lookup | Tìm web/tin tức theo thời gian | Không |
| fetch | Đọc URL cụ thể | Không |
| format | Trình bày items đã có thành markdown | Không |
| policy | Tìm tài liệu chính sách cục bộ | Không |
| papers | Tìm paper arXiv | Không |
| paper_text | Đọc PDF arXiv | Không |
| send | Gửi Telegram khi được xác nhận, có cấu hình | Không |
| deduplicate | Loại URL trùng, giữ item đầu tiên | **Có** |

UI cung cấp 10 tool nghiên cứu, loại `send` khỏi danh sách model được phép gọi.
CLI có 11 tool. Phần gửi Telegram không được trình bày như bonus đã kiểm chứng
end-to-end; không gửi tin thật trong quá trình chuẩn bị bài.

## A3. Câu hỏi mẫu

1. Tin GPU hôm nay có gì nổi bật?
2. Lấy 4 bài đăng mới nhất của tài khoản @NASA.
3. Chính sách nội bộ yêu cầu trích dẫn nguồn như thế nào?
4. Loại link trùng: `[{"url":"https://example.com/a"},{"url":"https://example.com/a"}]`.
5. Tóm tắt bài viết này giúp mình. (Agent phải hỏi URL.)

# PHẦN B — Chi tiết và bằng chứng

## B1. Version evidence và phương pháp

Giữ các run **v0–v2 gốc** sau khi xác minh SHA256 prompt/tools; khôi phục snapshot
vào `artifacts/versions/v0`, `v1`, `v2`. Không đổi nhãn log v4–v7 thành v3.
Chạy **v3 mới** trên bộ hoàn thiện. Các thử nghiệm cũ ngoài phạm vi đã được tách
sang `.lab_archive/` ngoài thư mục nộp. Bản hiện tại và snapshot v3 khớp hash của run mới.

| Version | Case accuracy | Tool routing | Arguments | Multi-turn | Run |
|---|---:|---:|---:|---:|---|
| v0 | 15/20 (75%) | 95% | 75% | 83.33% | [v0_B_base_openrouter_20261110T102258892961.json](../runs/v0_B_base_openrouter_20261110T102258892961.json) |
| v1 | 17/20 (85%) | 100% | 85% | 100.00% | [v1_B_base_openrouter_20261110T112040663135.json](../runs/v1_B_base_openrouter_20261110T112040663135.json) |
| v2 | 17/20 (85%) | 100% | 85% | 100.00% | [v2_B_base_openrouter_20261110T112501268964.json](../runs/v2_B_base_openrouter_20261110T112501268964.json) |
| v3 | 19/20 (95%) | 100% | 95% | 100.00% | [v3_B_base_openrouter_20261110T124215449978.json](../runs/v3_B_base_openrouter_20261110T124215449978.json) |

- **v0:** đo baseline starter có các chỉ dẫn cố ý chưa tốt; 15/20.
- **v1:** giả thuyết quy tắc hỏi tài khoản thay cho tự đoán sẽ sửa R10; đạt 17/20.
  R10 và M02 chuyển PASS. Không quy toàn bộ thay đổi M02 cho quy tắc hỏi tài khoản.
- **v2:** giả thuyết giữ nguyên query trong prompt sẽ giảm mở rộng từ khóa; vẫn 17/20.
  Giả thuyết chưa được xác nhận bằng mức tăng điểm.
- **v3:** giả thuyết hợp đồng prompt/declaration nhất quán sẽ cải thiện arguments:
  bỏ đoán URL/thông tin, bỏ ép một tool, định nghĩa query là trích xuất, cập nhật
  từng tham số theo lần sửa gần nhất, mô tả routing và xác nhận rõ. R03, R13 đạt;
  giữ toàn bộ case đã đạt ở v2; tổng 19/20. Thêm deduplicate và test/case tương ứng.
  Đây là vòng tích hợp nhiều thành phần, không phải phép thử cô lập một dòng prompt.

So v0: tăng **20 điểm phần trăm**, từ 75% lên 95%. Cùng provider/model và bộ base
không chỉnh sửa. Mỗi phiên bản chỉ có một lần đo trong bộ bằng chứng chính;
không đủ để khẳng định độ ổn định thống kê hoặc mọi mức tăng đều có quan hệ nhân quả.
Chi tiết giả thuyết, hash và metric: [version_log.csv](version_log.csv).

## B2. Failure analysis

| Case baseline | Mismatch thực tế | Lỗi v0 | Xử lý/kết quả cuối |
|---|---|---|---|
| R03_web_news_routing | wrong_arg_value | query: expected 'AI', got 'AI news today artificial intelligence breakthrough' | v3 giữ query=AI; PASS. |
| R10_missing_handle | missing_tool_call | missing tool call clarify; extra tool call timeline | v1 thêm hỏi lại khi thiếu tài khoản; v3 vẫn PASS. |
| R12_confirm_before_send | wrong_arg_value | response_type: expected 'yes_no', got 'text' | v3 hỏi nội dung bằng text; FAIL theo kỳ vọng yes_no. Không gửi tin. |
| R13_parallel_web_and_tweets | wrong_arg_value | query: expected 'AI', got 'AI news today'; query: expected 'AI', got 'AI artificial intelligence' | v3 gọi đủ lookup và social_search với query=AI; PASS. |
| M02_carryover_timeframe | wrong_arg_value | query: expected 'robotics', got 'robotics news today' | v3 giữ query=robotics, topic=news, timeframe=day; PASS. |

**R12 cần đánh giá thủ công:** yêu cầu chỉ có “Đăng bản tin này lên Telegram giúp mình”,
không có bản tin hay lịch sử. Model hỏi nội dung trước là hợp lý. Base chỉ so
`response_type=yes_no`, không chấm ý nghĩa câu hỏi. Giữ nguyên base và điểm 19/20,
không ép agent xin xác nhận gửi nội dung chưa biết. Hai case nhóm cung cấp đủ
nội dung/nơi nhận kiểm tra xác nhận trước gửi và xác nhận lại khi nội dung thay đổi.

`failure_type` của case là nhãn thiết kế bộ đề, không nhất thiết là nguyên nhân
quan sát. Ví dụ R03 in `wrong_tool` nhưng routing đúng; `observed_mismatch` là
`wrong_arg_value`. Phân tích dùng failures và actual_tool_calls.

**Bug evaluator đã sửa:** run nhóm đầu `v3_B_group_openrouter_20261110T124251084050.json` gặp
`TypeError` vì normalize_value sắp xếp list chứa dict. Harness gắn nhãn nhầm
`provider_error`; đây là lỗi bộ chấm, không phải OpenRouter. Bản sửa giữ thứ tự
list có object (items có ý nghĩa thứ tự), giữ cơ chế cũ cho list scalar.
Ba regression test kiểm tra bằng nhau, đổi thứ tự và list scalar. Chấm lại offline
mọi tool call base v0–v3 cho kết quả pass/fail không đổi. Giữ log lỗi đầu và log
chạy lại, không sửa hoặc xóa bằng chứng lỗi để tăng điểm.

## B3. Team eval cases

Đủ **10 case: 5 single-turn và 5 multi-turn**, không thay nội dung `eval_base.json`.
Run chính: [v3_B_group_openrouter_20261110T124403993220.json](../runs/v3_B_group_openrouter_20261110T124403993220.json), kết quả **10/10**, 0 lỗi provider.
Run nhóm đầu: 9/9 đo được và một lỗi harness; không gọi đó là 10/10.

| Case | Loại | Tool kỳ vọng | Kết quả cuối |
|---|---|---|---|
| G01_handle_without_at | single-turn | timeline | PASS |
| G02_social_top | single-turn | social_search | PASS |
| G_missing_url | single-turn | clarify | PASS |
| G_deduplicate | single-turn | deduplicate | PASS |
| G_missing_send_content | single-turn | clarify | PASS |
| G_count_correction | multi-turn | timeline | PASS |
| G_time_carryover | multi-turn | lookup | PASS |
| G_account_correction | multi-turn | timeline | PASS |
| G_send_confirmation | multi-turn | clarify | PASS |
| G_changed_content_confirmation | multi-turn | clarify | PASS |

Các case Telegram có hướng dẫn khá rõ nên chứng minh hành vi trong tình huống
được chỉ định, chưa đủ chứng minh khả năng xử lý mọi cách diễn đạt. Các case
multi-turn của harness kiểm tra sử dụng ngữ cảnh ghép, không phải cuộc hội thoại
model thực sự tự hỏi/đáp ở từng bước. Kiểm chứng hội thoại thực ở B4.

## B4. Live chat evidence

Transcript CLI: [v3_openrouter_20261110T124153293098.transcript.json](../transcripts/v3_openrouter_20261110T124153293098.transcript.json).
Ba yêu cầu demo được nhập bằng script qua CLI; **mọi phản hồi và tool call là gọi
API model thật**, không phải cuộc trò chuyện tự phát của người dùng hoặc transcript giả.

| Lượt | Yêu cầu | Tool thực tế | Trạng thái |
|---|---|---|---|
| 1 | Bạn là gì và có thể giúp gì cho nhóm nghiên cứu? | (không gọi tool) | answered |
| 2 | Loại nguồn trùng trong danh sách này: [{"url":"https://example.com/a","title":"Nguồn đầu"},{"url":"https://example.com/a","title":"Bản sao"},{"url":"https://example.com/b","title":"Nguồn khác"}]. Không cần tìm kiếm web. | deduplicate | answered |
| 3 | Chính sách nội bộ yêu cầu trích dẫn nguồn trong bản tin như thế nào? Hãy dùng policy để tra cứu. | policy, policy | answered |

Tool mới trả 2 item và duplicate_count=1. Lượt policy ban đầu tìm tiếng Việt ít
kết quả, model tìm lại bằng từ khóa tiếng Anh rồi trả lời dựa tài liệu nội bộ.
Không có hành động gửi Telegram thật.

UI được kiểm tra bằng Streamlit AppTest: render không exception, chat_input có,
gửi một yêu cầu qua model thật, nhận answered, lưu history và transcript. Bằng
chứng ở `artifacts/ui_verification.json` và `transcripts/ui_*.transcript.json`.
Kiểm tra này chạy UI runtime, không thay thế kiểm tra trực quan đầy đủ trên mọi
trình duyệt/thiết bị. Health public đã phản hồi `ok`.

## B5. Tool mới, unit test và phạm vi bonus

Tool mới: [deduplicate/TOOL.md](../tools/deduplicate/TOOL.md).
Có code, frontmatter, registry và YAML; không gọi mạng, không yêu cầu key.
Chuẩn hóa URL để so sánh (bỏ fragment và tham số tracking), giữ item đầu và thứ tự.
Không gộp khác bài chỉ vì chung domain/tiêu đề; giữ tham số id có ý nghĩa.
Không thay đổi input. URL sai hoặc lỗi xử lý trả error dict, không ném exception.

**Toàn bộ pytest: 94 passed, 0 failed, 0 skipped**, bằng chứng
[pytest_results.txt](pytest_results.txt). Các test TODO đã được triển khai thật.
Tool mới có test thành công, input không hợp lệ, lỗi parser, URL khác query và list rỗng.
Mock HTTP với fake_http, fixture chặn requests thật và xóa credentials.
Regression test cho comparator bắt lỗi mà các contract test trước đó không bao phủ.
`pip check` không có dependency conflict.

UI là phần bắt buộc đã làm bằng Streamlit, không coi UI là bonus. Không thực hiện
bonus model local, không tuyên bố hơn 3 tool mới. `policy`, `papers`, `paper_text`
là tool có sẵn, không tính thành tool nhóm tự viết.

## B6. Reflection, giới hạn và cách tái hiện

- Prompt chịu trách nhiệm routing tổng thể, không đoán, đọc ngữ cảnh, xác nhận và
  coi tài liệu truy xuất là dữ liệu không đáng tin để làm theo chỉ dẫn.
- Declaration chịu trách nhiệm ý nghĩa tool, khi nào dùng/không dùng và convention arguments.
- R12 cần xem xét thủ công vì thiếu tiền đề; không sửa đáp án để đạt 100%.
- Base chỉ đo routing/arguments lần model đầu. Tool results được lưu nhưng kết quả
  chấm không đánh giá độ chính xác nội dung nghiên cứu hoặc gửi thành công.
- `confirmed` của send vẫn là cờ do model truyền, chưa có state machine xác nhận
  gắn nội dung/nơi nhận ở runtime. Vì vậy UI không cung cấp hành động gửi; chưa nhận
  bonus gửi Telegram end-to-end. Cải tiến tiếp theo là lưu trạng thái xác nhận và
  kiểm tra ở executor trước khi gửi.
- Link demo tạm thời cần giữ tiến trình chạy hoặc triển khai lâu dài trước khi chấm.
- Ưu tiên tiếp: kiểm tra lặp nhiều lần, case paraphrase ít gợi ý hơn, chất lượng câu
  trả lời có nguồn và đánh giá end-to-end. Không tiếp tục tối ưu sau v3 trong bộ nộp này.

Hướng dẫn chạy và đóng gói: [SUBMISSION.md](../SUBMISSION.md).
Snapshots: `artifacts/versions/v0` đến `v3`; hash trong run JSON/version log và
`artifacts/evidence_manifest.json`. `analysis/base_runs.csv` được trích từ log thật,
bao gồm cả log nhóm đầu bị lỗi để bảo toàn bằng chứng.

## B7. Small Local Model Challenge

Không thực hiện; không yêu cầu điểm bonus phần này.
