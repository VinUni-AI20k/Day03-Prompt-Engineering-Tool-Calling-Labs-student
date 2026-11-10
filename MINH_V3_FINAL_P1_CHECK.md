# Kiểm tra lại bản `v3-final-p1` — Minh, 10/11/2026

Phản hồi review cuối của Tân (`MINH_FINAL_REVIEW.md`).

- Bản được kiểm tra: `main` tại `5f19ef9` (PR #10 của Trọng), artifact
  `v3-final-p1+pb768ae4b5c47+tfe7f33e09197`, model Groq `openai/gpt-oss-120b`.
- Kết quả và REPORT đã cập nhật nằm trên `main` (PR từ `feature/eval-ui-report-03657`).

## Kết quả kiểm tra

| Lỗi trong review của Tân | Kết quả | Bằng chứng |
|---|---|---|
| Routing arXiv (trước đây đi vào `lookup`) | ✅ **Đã sửa:** giờ gọi `papers`, lấy được 3 paper thật. Còn thiếu: model không truyền `sort_by="submittedDate"` dù người dùng nói "mới nộp gần đây nhất" | Live lượt 1 |
| **P1:** model bịa `source` cho item thiếu nguồn | ❌ **Vẫn còn:** quy tắc mới trong prompt không có tác dụng. Item `{"title":"Gemini roadmap","url":"https://blog.google/technology/ai/"}` vẫn được gửi cho tool kèm `"source": "blog.google"`, nên tool báo item này hợp lệ | G10 trong run group của Trọng; live lượt 2 |
| G01 | ✅ `items` nguyên vẹn, tool báo đúng `missing_url` và `missing_source` | Run group của Trọng |
| **P2:** B5 ghi sai số test | ✅ Đã sửa thành **131** (60 contract + 7 example + 59 tool + 5 UI; trong đó 42 case `source_check`) | Đã chạy lại `pytest` trên `5f19ef9`: 131 passed |

File bằng chứng:

- Run group: `starter_v0/runs/v3-final-p1_B_group_openai_20261110T142154758429.json` (8/9 PASS, 1 provider error ở G02)
- Live chat: `starter_v0/transcripts/v3-final-p1_openai_20261110T143232383389.transcript.json`

## REPORT đã cập nhật

- **B1:** thêm `v3-final` và `v3-final-p1` (base đều 0.95, chỉ còn R13 fail).
- **B2, B3:** theo run group mới (8/9 PASS).
- **B4:** thêm 2 lượt live mới.
- **B5:** dòng Telegram và dòng arXiv.
- **B6:** ghi rõ quy tắc dạng chữ trong prompt không đủ để sửa G10.

## Cập nhật sau đó: Minh đã thử sửa P1 (v4)

Minh đã làm luôn phần đề xuất cho Trọng ở bản trước của file này. **Trọng lưu ý:**
`system_prompt.md` và `version_log.csv` là file của Trọng, đã được sửa.

| Thử nghiệm | Thay đổi | G10 bịa nguồn thật | Kết luận |
|---|---|---|---|
| p1 (hiện tại trước đó) | Quy tắc dạng chữ "truyền `items` y nguyên" | 3/5 lần quan sát | Không đủ |
| **v4 (giữ lại)** | Thêm **ví dụ mẫu** vào prompt: item thiếu `source` phải giữ nguyên | **2/7** lần (các lần khác phần lớn điền `""`, tool vẫn báo `missing_source`) | Giảm nhưng chưa hết |
| "v5" (đã hoàn tác) | Sửa mô tả `url`/`source` trong `tools.yaml`: "chép đúng, thiếu thì bỏ key, không suy ra từ URL/domain" | 5/6 lần | Tệ hơn, không commit |

- v4: base **0.95** (19/20, chỉ R13 fail), group **8/9** — không làm giảm điểm nào.
- G01 (single-turn) giữ nguyên `items` ở mọi lần chạy (14/14 lần thử lặp).
- **Kết luận P1:** prompt và mô tả tool không chặn được hoàn toàn việc model bịa
  `source` ở case nhiều lượt → ghi là **giới hạn đã biết** trong REPORT B2/B6. Tool
  không thể tự phát hiện vì không có dữ liệu gốc.
- `version_log.csv` đã có đủ `v3-final`, `v3-final-p1`, `v4` (hash lấy từ run JSON).

Bằng chứng mới:

- `starter_v0/runs/v4_B_base_openai_20261110T145359081439.json`, `starter_v0/runs/v4_B_group_openai_20261110T145702253546.json`
- `starter_v0/transcripts/v4_openai_20261110T145738372871.transcript.json`
- `starter_v0/runs/v4_source_check_repeat_probe.txt` (đo lặp G01/G10 cho p1, v4, v5)

## Việc tiếp theo

| Ai | Việc |
|---|---|
| **Minh** | (1) Điền tên nhóm vào REPORT. (2) Link demo (Streamlit + Cloudflare Tunnel) khi demo |
| **Trọng** | Review thay đổi v4 trong `system_prompt.md` và 3 dòng mới trong `version_log.csv`; review REPORT B1/B2 |
| **Tân** | Review lại B5 và args G10/live trong các transcript mới |

Sau đó là bước kiểm tra cuối (Mốc 6) rồi nộp bài.
