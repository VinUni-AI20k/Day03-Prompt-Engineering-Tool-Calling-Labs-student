# Day 03 Lab v2 Report — Research Agent

## Team
- Team / Members: Nguyễn Minh Khôi (2A202603528), Võ Công Minh, Nguyễn Đắc Tuấn Nghĩa (2A202603442), Nguyễn Ngọc Hiếu (2A202603502).
- Provider/model baseline: OpenRouter / `openai/gpt-4o-mini`.

# PHẦN A — Giới thiệu agent

## A1. Khả năng
Research Agent tìm tin trên web và mạng xã hội, xem bài đăng theo tài khoản, đọc URL và paper arXiv, tra cứu policy nội bộ, loại URL trùng và định dạng digest. Gửi Telegram cần xác nhận rõ ràng trước khi thực hiện.

**Link dùng thử:** chưa có URL deploy công khai trong repo; có mã `app.py`.

## A2. Tools
Các tool được khai báo trong `artifacts/tools.yaml` và đăng ký trong `tools/__init__.py`.

| Tool | Chức năng | Trạng thái |
|---|---|---|
| `clarify` | Hỏi lại khi thiếu thông tin hoặc cần xác nhận. | Có |
| `timeline` | Lấy bài đăng theo tài khoản. | Có |
| `social_search` | Tìm bài đăng theo từ khóa (`Latest`/`Top`). | Có |
| `lookup` | Tìm kiếm web, gồm tin tức theo khoảng thời gian. | Có |
| `fetch` | Đọc URL được cung cấp. | Có |
| `format` | Định dạng kết quả thành digest. | Có |
| `send` | Gửi Telegram sau xác nhận (`confirmed=true`). | Có (bonus) |
| `policy` | Tìm trong policy nội bộ. | Có (bonus) |
| `papers` | Tìm paper trên arXiv. | Có (bonus) |
| `paper_text` | Trích xuất nội dung paper arXiv. | Có (bonus) |
| `deduplicate_sources` | Loại URL trùng, giữ nguồn đầu tiên. | Tool mới nhóm thêm |

## A3. Câu hỏi thử
1. Tin tức AI hôm nay có gì nổi bật?
2. Mọi người đang bàn gì về GPT-5 trên Twitter?
3. Tóm tắt 5 tweet mới nhất của Elon Musk.
4. Tìm paper mới về RAG và tóm tắt một paper.
5. Loại URL trùng trong danh sách nguồn này: [dán danh sách].

# PHẦN B — Bằng chứng

## B1. Version Evidence
Hiện có run baseline v0; chưa có run v1–v3 hoặc version log đã điền.

| Version | Thay đổi | Kết quả | Run |
|---|---|---|---|
| v0 | Baseline | 15/20 pass; accuracy 0.75, routing 0.80, arguments 0.75, multi-turn 1.00; 0 provider errors. | `runs/v0_B_base_openrouter_20261110T102236137498.json` |
| v1–v3 | Chưa có bằng chứng | Chưa đo | Chưa có |

## B2. Lỗi baseline và hướng sửa

| Case | Lỗi / tool thực tế | Hướng sửa |
|---|---|---|
| `R08_out_of_scope` | Ngoài phạm vi nhưng gọi `send`. | Quy định phạm vi; không gọi tool cho yêu cầu ngoài phạm vi. |
| `R10_missing_handle` | Đoán `sama`, gọi `timeline` thay vì hỏi. | Thiếu tài khoản thì gọi `clarify`. |
| `R11_missing_url` | Gọi `fetch` khi chưa có URL. | Thiếu link thì hỏi người dùng. |
| `R12_confirm_before_send` | Gọi `send` trước khi xác nhận. | Hỏi xác nhận trước; chỉ gửi khi được đồng ý. |
| `R13_parallel_web_and_tweets` | Gọi `lookup` + `social_search`, arguments sai. | Làm rõ cách gán query/topic/timeframe và kiểm tra lại bằng eval. |

Nguồn: run v0 và `analysis/base_runs.csv`; không suy đoán arguments sai của R13 khi log tóm tắt không ghi rõ.

## B3. Team Eval
`data/eval_group.json` có đủ 10 case (5 single-turn, 5 multi-turn) do nhóm tự xây dựng để kiểm thử các tình huống chuyên biệt. Đã chạy đánh giá thực tế với model OpenRouter (`runs/v0_B_group_openrouter_20261110T222620690855.json`), đạt **7/10 pass (70%)**, **tool routing accuracy đạt 90%**.

| Case | Kiểm tra | Kỳ vọng | Kết quả baseline v0 |
|---|---|---|---|
| `group_dedup_single` | Deduplicate danh sách đã cho (single-turn). | `deduplicate_sources` | PASS |
| `group_dedup_missing_items` | Hỏi khi thiếu danh sách nguồn (single-turn). | `clarify` | PASS |
| `group_arxiv_paper_search` | Tìm bài báo khoa học trên arXiv (single-turn). | `papers` | PASS |
| `group_company_policy_search` | Tra cứu chính sách công ty (single-turn). | `policy` | FAIL (arg query dài) |
| `group_out_of_scope_math` | Từ chối câu hỏi giải toán ngoài phạm vi (single-turn). | Không gọi tool | FAIL (gọi lookup do prompt v0) |
| `group_dedup_multi` | Dùng danh sách ở lượt trước để bỏ trùng (multi-turn). | `deduplicate_sources` | PASS |
| `group_clarify_then_send` | Xác nhận ở lượt sau rồi mới gửi Telegram (multi-turn). | `send` (`confirmed=true`) | PASS |
| `group_missing_url_then_fetch` | Cung cấp URL ở lượt sau rồi mới đọc (multi-turn). | `fetch` | PASS |
| `group_correction_search_timeframe` | Sửa khoảng thời gian tìm kiếm từ hôm nay sang tháng (multi-turn). | `lookup` (`timeframe=month`) | FAIL (arg query thừa từ) |
| `group_switch_search_to_timeline` | Đổi từ tìm kiếm sang xem bài đăng tài khoản chính chủ (multi-turn). | `timeline` | PASS |

## B4. Live Chat
Đã thu thập 3 transcript tương tác thực tế qua giao diện Streamlit (`app.py`), lưu tại `starter_v0/transcripts/`:

| Transcript ID | Yêu cầu người dùng | Tool được gọi | Kết quả thực thi |
|---|---|---|---|
| `v0_openrouter_ui_20261110T224705052469.transcript.json` | Tìm 2 bài báo khoa học mới nhất về RAG trên arXiv và tóm tắt ngắn gọn. | `papers` -> `format` | Trích xuất thành công 2 bài báo arXiv và định dạng thành digest các phần. |
| `v0_openrouter_ui_20261110T224721535793.transcript.json` | Tìm tin tức công nghệ nổi bật về OpenAI trong tuần này. | `lookup` (`timeframe="week"`, `topic="news"`) | Tìm kiếm và tổng hợp các tin thời sự mới nhất về OpenAI. |
| `v0_openrouter_ui_20261110T224734173076.transcript.json` | Loại bỏ các URL trùng lặp trong danh sách nguồn có gắn UTM params. | `deduplicate_sources` | Loại bỏ thành công URL trùng lặp (chuẩn hóa UTM param), giữ nguyên nguồn sạch. |

## B5. Bonus và tests
- Đã chạy unit test toàn bộ bằng pytest: **104 passed** (`tests/test_deduplicate_sources.py`, `tests/test_tool_contract.py`, `tests/test_tools_examples.py`).
- Các tool bonus `papers`, `lookup`, `deduplicate_sources` đã được kiểm chứng hoạt động thực tế qua 3 transcript live ở mục B4.
- Giao diện Streamlit `app.py` đã hoàn thành và chạy được trực tiếp trên local (`http://localhost:8501`).

| Bonus | Bằng chứng | Guardrail |
|---|---|---|
| Telegram | `tools/send/`, `artifacts/tools.yaml` | Chỉ gửi sau xác nhận. |
| arXiv/policy | `tools/papers/`, `tools/paper_text/`, `tools/policy/` | Kiểm tra nguồn và trích dẫn; dùng policy cho câu hỏi nội bộ. |
| UI | `app.py` | Chưa có URL public. |
| Unit tests | `tests/test_deduplicate_sources.py` | Cần lưu output chạy pytest. |

## B6. Reflection
- Prompt nên yêu cầu hỏi lại khi thiếu dữ kiện, giới hạn phạm vi và xác nhận trước hành động có side effect.
- `tools.yaml` nên nói rõ cách chọn tool và quy ước arguments.
- Boundary gửi/publish và câu hỏi ngoài phạm vi cần review cẩn thận, không chỉ dựa vào điểm tự động.
- Tiếp theo: hoàn thiện prompt, chạy v1–v3 và group eval, bổ sung 7 eval case, lưu transcript và kết quả pytest.

## B7. Local Model Challenge
Chưa có bằng chứng chạy Ollama/local model; chưa thể đánh giá độ chính xác hoặc các kiểu lỗi.
