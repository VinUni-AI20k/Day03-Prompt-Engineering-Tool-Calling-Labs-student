# Review code Minh — Tân kiểm tra ngày 10/11/2026

## Phạm vi và kết luận

- Nhánh được review: `origin/feature/eval-ui-report-03657`, commit `92a54c4`.
- Remote đã có merge PR #4 trên `main` tại `29c966c` khi bắt đầu review.
  Đây là trạng thái đã tồn tại; lần review này không merge hay sửa `main`.
- Review thực hiện trong worktree riêng, không thay đổi code nhánh Minh.
- **Chưa nên dùng transcript UI làm evidence cuối cho tới khi sửa hai lỗi
  dưới đây.** Tool và cấu trúc eval không làm bộ test hiện có bị lỗi.

## Findings cần sửa

### P2 — Đổi cấu hình làm transcript mất ngữ cảnh mà model vẫn nhận

Vị trí: `starter_v0/app.py`, `ensure_transcript()` và đoạn xử lý `user_text`.

Cách tái hiện bằng Streamlit AppTest với fake provider:

1. Gửi một lượt chat khi version label là `dev`.
2. Đổi version label thành `changed-version`, rồi gửi lượt tiếp theo.
3. `ensure_transcript()` tạo transcript mới chỉ có lượt thứ hai.
4. `st.session_state.history` vẫn có lượt đầu và được truyền vào model qua
   `trim_history()`. Nội dung đó không xuất hiện trong transcript mới.

Đã xác nhận: `new_transcript_turns=1`, `previous_turn_in_model_context=true`,
`new_transcript_has_previous_turn=false`. Điều này cũng áp dụng khi thay đổi
provider/model; transcript không mô tả đủ ngữ cảnh model đã dùng để trả lời
hoặc quyết định gọi tool.

Đề xuất cho Minh: khi đổi cấu hình, bắt đầu conversation mới và xóa history
trước khi thêm lượt mới; hoặc giữ đầy đủ ngữ cảnh kế thừa trong transcript với
nguồn/config rõ ràng. Kiểm tra lại bằng ít nhất hai lượt và đổi config ở giữa.

### P2 — Artifact thay đổi nhưng transcript vẫn ghi hash cũ

Vị trí: `starter_v0/app.py`, điều kiện dùng lại transcript trong
`ensure_transcript()`, `config_key` và lời gọi `load_artifacts()` mỗi lượt.

`config_key` chỉ gồm provider, model, version label, history window và số vòng
tool. Nếu sửa `system_prompt.md` hoặc `tools.yaml` trong khi UI đang chạy mà
không đổi label, UI đọc nội dung mới nhưng dùng lại transcript có hash cũ.

Đã tái hiện bằng cách sửa một bản copy prompt trong thư mục tạm giữa hai lượt:
fake provider nhận prompt mới, nhưng `transcript.prompt_hash` không bằng SHA256
của prompt đã dùng. Trường hợp này dễ xảy ra trong lúc tối ưu prompt v1–v3.

Đề xuất cho Minh: dùng cùng một snapshot prompt/tools cho việc tính hash và
gọi model; đưa hash vào khóa nhận diện session hoặc ghi artifact theo từng lượt.
Khi artifact đổi, áp dụng cùng quy tắc quản lý history/transcript ở finding trên.

## Giới hạn eval đã biết — cần phối hợp với chủ runner

G01 và G10 khai báo `expect.tool_calls[0].args={}`, nên chỉ chấm tên
`source_check`. Đã tái hiện lời gọi `source_check()` thiếu `items` được evaluator
tính PASS trong khi implementation trả `ValueError`. Minh đã công khai giới hạn
này trong metadata/report; không coi kết quả hai case này là bằng chứng args đúng.

Nguyên nhân workaround có thật: `run_eval.normalize_value()` dùng `sorted()`
trên list dict, không so sánh được `items` có nhiều object. Đề xuất nhóm giao rõ
người sửa runner và thêm regression test cho list object trước khi thêm expected
`items` vào hai case. Trong lúc chờ, Tân cần kiểm tra `tool_events[].args` và
output thực tế trong live transcript; test unit hiện có không chứng minh model
đã truyền đúng dữ liệu.

## Kết quả kiểm chứng

- Chạy toàn bộ pytest trên commit Minh: **122 passed, 0 failed, 0 skipped**;
  1 warning từ plugin `anyio` của môi trường.
- Eval JSON: đủ 10 ID riêng, 5 single-turn và 5 multi-turn, tool được khai báo,
  failure type hợp lệ. Các expected calls lý tưởng chấm được 10/10; đây là kiểm
  tra cấu trúc evaluator, **không phải kết quả eval model thật**.
- Streamlit AppTest: app mở và nhận nhiều lượt chat bằng fake provider; hai
  finding trên đều tái hiện được, không cần model/API thật.
- Mọi HTTP thật bị chặn trong kiểm tra UI; transcript thử nghiệm nằm trong thư
  mục tạm và không được dùng làm live evidence.
- Bằng chứng tái hiện: [minh-review-output.txt](starter_v0/tools/source_check/minh-review-output.txt).
- B5 mô tả `source_check` đúng phạm vi metadata-only và test count 122 đúng với
  lần chạy review. Chưa chốt B4/B5 live: snapshot Minh chưa có transcript live
  hoặc run group cuối để Tân kiểm tra arguments thật.

## Việc tiếp theo

1. **Minh:** sửa hai lỗi quản lý transcript; thêm kiểm tra hồi quy đổi config
   và đổi artifact; push commit sửa để nhóm review lại. Cập nhật report sau khi
   có bằng chứng live/group eval và link demo.
2. **Trọng và Minh:** thống nhất provider/model dùng so sánh; report mới đề xuất
   Groq, trong khi các lệnh checklist cũ còn Gemini/OpenRouter. Ghi nhận cấu hình
   thực tế và chạy đủ v0–v3, không suy ra metric từ kiểm tra offline.
3. **Nhóm:** phân công sửa so sánh list object trong runner nếu cần chấm args
   cho `source_check`; giữ nguyên base eval.
4. **Tân:** review lại commit sửa, chạy test tích hợp và kiểm tra args trong live
   transcript khi Minh bàn giao. Không cần viết lại tool hiện tại chỉ vì hai
   lỗi UI; chưa phát hiện regression của implementation `source_check`.

File review này và output được chuẩn bị để nhóm xem; chưa gửi tin nhắn cho
thành viên và chưa tự sửa file thuộc phần Minh hoặc runner.
