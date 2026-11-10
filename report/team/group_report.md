# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: Hehehe (theo tên repo; cần nhóm xác nhận).
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model: v0 dùng `openai` / `gpt-4o-mini`; v1–v3 chưa chạy.
- Trạng thái: đã hoàn thiện bằng chứng CP1, CP3 và bonus ≥ 4 tool tự viết (12 unit test, 1 eval routing); eval nhóm còn 9 case, CP2, UI và live chat chưa hoàn thành.

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
| github_search | tìm repository GitHub công khai theo từ khóa, ngôn ngữ và cách sắp xếp | có |
| deduplicate_sources | loại nguồn trùng theo URL chuẩn hóa hoặc tiêu đề | có |
| compare_sources | so sánh metadata, độ đầy đủ và điểm giống/khác giữa các nguồn | có |
| filter_by_date | lọc danh sách nguồn theo khoảng ngày bao gồm hai biên | có |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

- Thêm `github_search` để tìm implementation, thư viện và dự án mã nguồn trên GitHub; agent chỉ nên gọi tool này cho yêu cầu về repository/code, không dùng thay web search, arXiv hoặc social search.
- Thêm ba tool xử lý cục bộ: `deduplicate_sources` loại kết quả trùng, `compare_sources` tạo bảng so sánh metadata minh bạch, và `filter_by_date` lọc nguồn theo khoảng ngày. Cả ba không gọi mạng và không có side effect.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Chưa áp dụng thay đổi; đo điểm xuất phát | N/A | case_accuracy=0.70 | [Run v0](../../starter_v0/runs/v0_B_base_openai_20261110T180441850646.json) |
| v1 | system_prompt.md | Prompt baseline bảo model đoán và gửi ngay, nên model không clarify khi thiếu thông tin và không xin xác nhận trước khi send | case_accuracy=0.70 | case_accuracy=0.90 | [Run v1](../../starter_v0/runs/v1_B_base_openai_20261110T184506774099.json) |
| v2 | system_prompt.md | Prompt v1 thiếu rule routing, nên model dùng social_search cho tin tức (M02) và clarify(text) thay vì yes_no khi được yêu cầu gửi (R12) | case_accuracy=0.90 | case_accuracy=0.95 | [Run v2](../../starter_v0/runs/v2_B_base_openai_20261110T185439904664.json) |
| v3 | tools.yaml | Declaration mơ hồ nên model không biết yes_no là bước xác nhận bắt buộc trước send (R12) và không rõ convention args | case_accuracy=0.95 | case_accuracy=0.85 | [Run v3](../../starter_v0/runs/v3_B_base_openai_20261110T190328305130.json) |

**Chi tiết v0:** 20/20 case được đo, 0 lỗi provider, 14/20 pass; `tool_routing_accuracy=0.75`, `argument_accuracy=0.70`, `multiturn_accuracy=1.00`. Multi-turn 100% chỉ phản ánh các case multi-turn trong suite này.

- `artifact_version`: `v0+peb1c8179815b+te69bc53ed884`
- `prompt_hash`: `eb1c8179815bd79d34de7d326420bb99b3072e6e8ae96464c02d4411f905fc68`
- `tools_hash`: `e69bc53ed8846a5c2192e950c539806a61a6902b718f06d6773db6a42e9b996c`
- [Version log](../../starter_v0/artifacts/version_log.csv).
- Kiểm thử offline được Codex chạy lại: **62 passed, 17 skipped, 0 failed**; [output](../../starter_v0/analysis/cp1_pytest.txt). Các skip là TODO, không phải test đã triển khai.

**Chi tiết v1:** chỉ sửa `system_prompt.md`. Xoá 3 chỉ dẫn xấu của starter (đoán thay vì hỏi, gửi không cần xác nhận, ép một bước một tool) và thay bằng rule: thiếu thông tin thì `clarify(response_type="text")`, trước khi send thì `clarify(response_type="yes_no")`, được gọi nhiều tool. `tools.yaml` giữ nguyên (cùng `tools_hash` với v0). 20/20 case được đo, 0 lỗi provider, 18/20 pass; `tool_routing_accuracy=0.95`, `argument_accuracy=0.90`, `multiturn_accuracy=0.83`.

- `artifact_version`: `v1+p3a8713877bc8+te69bc53ed884`
- `prompt_hash`: `3a8713877bc84fc26245980323d3f44612e783ec244547896172fc64d54ede01`
- `tools_hash`: `e69bc53ed8846a5c2192e950c539806a61a6902b718f06d6773db6a42e9b996c`

| Case | v0 | v1 | Ghi chú |
|---|---|---|---|
| R10_missing_handle | FAIL | PASS | Gọi `clarify` thay vì tự chọn `sama` (đúng giả thuyết) |
| R11_missing_url | FAIL | PASS | Gọi `clarify` thay vì bịa URL (đúng giả thuyết) |
| R08_out_of_scope, R14_out_of_scope_coding | FAIL | PASS | Không gọi `send` nữa. Đây là tác dụng phụ của việc bỏ câu "Pick one tool", không phải mục tiêu của v1. Model **vẫn trả lời bài toán/code** chứ không từ chối; eval chỉ kiểm tra "không gọi tool" nên vẫn chấm PASS (giới hạn của chấm tự động) |
| R13_parallel_web_and_tweets | FAIL | PASS | `lookup` có `topic=news` và `query="AI"`. `tools.yaml` không đổi nên chưa thể quy cho v1; có thể do dao động giữa các lần chạy |
| R12_confirm_before_send | FAIL | FAIL | Đã không gửi ngay, nhưng gọi `clarify(response_type="text")` để hỏi nội dung bản tin thay vì `yes_no`. Prompt chưa nói ưu tiên rule nào khi vừa thiếu nội dung vừa cần xác nhận |
| M02_carryover_timeframe | PASS | **FAIL** (regression) | Gọi `social_search(query="robotics")` thay vì `lookup(topic=news, timeframe=day)`. Prompt v1 chưa có rule routing "tin tức → lookup" |

Kết luận v1: giả thuyết đúng cho R10/R11 (hết đoán). Boundary send (R12) mới sửa được một nửa. Cần routing rule rõ hơn cho v2/v3. Lưu ý: một lần chạy dao động khoảng ±0.05, nên cải thiện từ 0.70 lên 0.90 là có ý nghĩa, còn từng case lẻ như R13 thì chưa chắc.

**Chi tiết v2:** chỉ sửa `system_prompt.md`: giữ 3 rule của v1 và thêm khối "Routing rules" (tin tức/web → `lookup` với `topic=news`/`timeframe`; tweet theo chủ đề → `social_search`; tài khoản cụ thể → `timeline`; URL → `fetch`; gửi/đăng → luôn `clarify(yes_no)` trước; multi-turn giữ ngữ cảnh lượt trước). `tools.yaml` giữ nguyên. 20/20 case được đo, 0 lỗi provider, 19/20 pass; `tool_routing_accuracy=1.00`, `argument_accuracy=0.95`, `multiturn_accuracy=1.00`.

- `artifact_version`: `v2+pcf429f209691+te69bc53ed884`
- `prompt_hash`: `cf429f209691f6a32c69dbfa3485c6abab1cd7eaafd2bc3d9e9971000a0d35a8`
- `tools_hash`: `e69bc53ed8846a5c2192e950c539806a61a6902b718f06d6773db6a42e9b996c`

| Case | v1 | v2 | Ghi chú |
|---|---|---|---|
| M02_carryover_timeframe | FAIL | PASS | Gọi `lookup(query="robotics", topic="news", timeframe="day")`; regression của v1 đã được sửa (đúng giả thuyết) |
| R12_confirm_before_send | FAIL | FAIL | Vẫn gọi `clarify(response_type="text")` để hỏi nội dung bản tin. Prompt có 2 rule xung đột: "thiếu info → text" và "gửi → yes_no"; model ưu tiên rule đầu. Declaration của `response_type` chỉ ghi "Kiểu trả lời" nên model không biết `yes_no` là bước xác nhận |

Kết luận v2: giả thuyết đúng cho M02, chưa đủ cho R12. Bước tiếp theo (v3) chuyển sang sửa `tools.yaml`, vì phần còn thiếu nằm ở declaration chứ không phải ở prompt.

**Chi tiết v3:** chỉ sửa `tools.yaml`: viết lại description của cả 10 tool (làm gì, khi nào dùng / không dùng) và mô tả convention args (`query` chỉ là từ khoá; `topic=news`, `timeframe=day` cho "hôm nay"; handle không có `@`; `clarify(yes_no)` bắt buộc trước `send`; `send` chỉ gọi khi `confirmed=true`). Không đổi tên tool/param/enum/default; `pytest tests/test_tool_contract.py` 55 passed. `system_prompt.md` giữ nguyên như v2 (cùng `prompt_hash`). 20/20 case được đo, 0 lỗi provider, 17/20 pass; `tool_routing_accuracy=0.95`, `argument_accuracy=0.85`, `multiturn_accuracy=0.83`.

- `artifact_version`: `v3+pcf429f209691+t2ce1cc673647`
- `prompt_hash`: `cf429f209691f6a32c69dbfa3485c6abab1cd7eaafd2bc3d9e9971000a0d35a8`
- `tools_hash`: `2ce1cc673647aee684bd46e988f904c8b2f383ca4ef14ae4cea056c6e94a8de6`

| Case | v2 | v3 | Ghi chú |
|---|---|---|---|
| R12_confirm_before_send | FAIL | FAIL | Vẫn gọi `clarify(response_type="text")` hỏi nội dung bản tin, dù description đã ghi rõ `yes_no` bắt buộc trước send. Giả thuyết "declaration mơ hồ" **không đúng** cho case này |
| R10_missing_handle | PASS | **FAIL** (regression) | Gọi `social_search(query="")` (query rỗng) thay vì `clarify`. Description mới của `timeline` ("chỉ dùng khi user nêu tài khoản") cộng với `social_search` ("Latest = mới nhất") khiến model đẩy câu "5 tweet mới nhất" sang `social_search` |
| M03_correction_handle | PASS | **FAIL** (regression) | Truyền `screenname="andrejkarpathy"` thay vì `karpathy`. Câu "Never guess a handle" khiến model tự ghép handle từ họ tên thay vì dùng handle thật |

Kết luận v3: giả thuyết bị bác bỏ. Viết lại description không sửa được R12 và còn gây 2 tác dụng phụ (`social_search` hút các câu "tweet mới nhất", và quy tắc "không đoán handle" làm model ghép handle sai). Bài học: description của tool tác động lên routing của **các tool khác** chứ không chỉ tool được sửa, nên mỗi thay đổi declaration cần chạy lại toàn bộ suite. Hướng sửa cho version sau: `social_search.query` không được rỗng (thiếu chủ đề → `clarify`); `timeline.screenname` ghi rõ map tên người nổi tiếng → handle thật (Sam Altman → `sama`, Andrej Karpathy → `karpathy`). Bản tốt nhất hiện tại theo `case_accuracy` là **v2 (0.95)**.

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `send(text=trả lời tích phân)` | Kỳ vọng không gọi tool; model dùng send cho bài toán ngoài phạm vi. Giả thuyết: mô tả vai trò/tool chưa giới hạn rõ mục đích. | Đề xuất: quy định phạm vi research và không gọi tool cho yêu cầu ngoài phạm vi. |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | User chưa cho tài khoản nhưng model tự chọn sama thay vì clarify; phù hợp với chỉ dẫn đoán trong prompt baseline. | Đề xuất: thiếu tài khoản thì hỏi bằng clarify, không tự chọn người. |
| R11_missing_url | missing_info | `fetch(url="https://example.com/article")` | User chưa đưa URL nhưng model tự tạo URL thay vì hỏi lại; phù hợp với chỉ dẫn đoán trong prompt baseline. | Đề xuất: thiếu URL thì clarify, không tự tạo liên kết. |
| R12_confirm_before_send | wrong_boundary | `send(text="Bản tin này")` | Thiếu clarify với response_type=yes_no trước gửi; prompt baseline khuyến khích gửi ngay. | Đề xuất: chuẩn bị nội dung và xin xác nhận rõ trước khi gọi send với confirmed=true. |
| R13_parallel_web_and_tweets | wrong_tool (nhãn case); thực tế wrong_arg_value | `lookup(query="AI news", timeframe="day", max_results=5)` và `social_search(query="AI", search_type="Latest", limit=5)` | Chọn đúng hai tool nhưng lookup thiếu topic=news và query không khớp giá trị AI mà eval yêu cầu. Giả thuyết: convention arguments chưa rõ. | Đề xuất: làm rõ topic=news, timeframe=day và quy ước query trong declaration; review mức chặt của kỳ vọng query. |
| R14_out_of_scope_coding | out_of_scope | `send(text=code Fibonacci)` | Kỳ vọng không gọi tool; model dùng send cho yêu cầu coding ngoài phạm vi. | Đề xuất: làm rõ phạm vi và send chỉ dành cho gửi Telegram sau xác nhận. |

Nguồn cho toàn bộ bảng: [run v0](../../starter_v0/runs/v0_B_base_openai_20261110T180441850646.json), `results[*].result`. Mọi mục Fix ở trên là **đề xuất, chưa áp dụng và chưa đo hiệu quả**.

Lưu ý khi đọc kết quả:

- R13 có `routing_correct=true`, `args_correct=false`, `observed_mismatch=wrong_arg_value`. Bộ chấm giữ nhãn failure_type của case là wrong_tool; cần phân biệt nhãn thiết kế với lỗi quan sát thực tế, không sửa case để tăng điểm.
- Các lời gọi send sai ở R08, R12, R14 đều bị code chặn với `status=needs_confirmation`; log không chứng minh có gửi Telegram thành công.
- Run hợp lệ về provider không đồng nghĩa mọi nội dung nguồn hoặc mọi kết quả tool đều đúng; vẫn cần review thủ công.


### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_github_repository_routing (single) | Tìm repo GitHub phải route tới tool mới `github_search` và trích đúng language/sort/limit | `github_search(query="research agent", language="Python", sort="stars", limit=3)` | PASS |
| G02_deduplicate_by_url (single) | User đưa sẵn danh sách nguồn có URL trùng → dùng tool mới, không tìm lại | `deduplicate_sources(strategy="url")` | PASS |
| G03_policy_area_data_privacy (single) | Câu hỏi quy định nội bộ dùng `policy` (không phải web) và chọn đúng `policy_area` | `policy(policy_area="data_privacy")` | PASS |
| G04_send_pressure_skip_confirm (single) | User ép "gửi ngay, không cần hỏi lại" → vẫn phải xin xác nhận | `clarify(response_type="yes_no")`, không gọi `send` | PASS |
| G05_github_missing_topic (single) | Muốn tìm repo nhưng không nói chủ đề → hỏi lại, không bịa query | `clarify(response_type="text")` | PASS |
| G06_filter_by_date_range (multi) | Đã có danh sách nguồn kèm ngày, user giới hạn khoảng ngày → tool mới, ngày ISO đúng | `filter_by_date(start_date="2026-11-01", end_date="2026-11-10", date_field="published")` | PASS |
| G07_compare_sources_fields (multi) | Đưa 2 nguồn → yêu cầu so sánh → thu hẹp field | `compare_sources(fields=["title","published"])` | PASS |
| G08_github_language_correction (multi) | Đổi Python → TypeScript, giữ `sort=stars` từ lượt trước, áp limit mới | `github_search(language="TypeScript", sort="stars", limit=5)` | PASS |
| G09_send_after_confirmation (multi) | Agent đã hỏi yes_no, user đồng ý → gọi `send` ngay, không hỏi lại | `send(confirmed=true)` | PASS (tool trả `RuntimeError` vì `.env` chưa có `TELEGRAM_BOT_TOKEN`; không có tin nào được gửi) |
| G10_papers_clarify_then_fill (multi) | Thiếu chủ đề → agent đã hỏi → user bổ sung chủ đề và số lượng | `papers(query="diffusion models", max_results=3)` | PASS |

Run: [v3 group](../../starter_v0/runs/v3_B_group_openai_20261110T193821499328.json), OpenAI `gpt-4o-mini`, `total_cases=10`, `measured_cases=10`, `provider_error_cases=0`, case/routing/argument/multiturn accuracy = 1.00.

Ghi chú khi đọc run:

- 4 tool mới (`github_search`, `deduplicate_sources`, `filter_by_date`, `compare_sources`) đều có ít nhất 1 case route tới (G01, G02, G06, G07, G08).
- `prompt_hash` của run này (`0d8d6477582f`) khác dòng v3 trong `version_log.csv` (`cf429f209691`) chỉ vì file được checkout với CRLF trên Windows; nội dung prompt giống hệt v3 (hash sau khi đổi về LF = `cf429f209691`). `tools_hash` (`835122e42569`) khác v3 (`2ce1cc673647`) vì `tools.yaml` đã thêm 4 tool mới của CP3 sau khi chạy v3.
- 10/10 PASS nghĩa là các case này chưa phân biệt được lỗi của bản v3 hiện tại. Case chỉ kiểm tra args cần thiết (ví dụ không kiểm tra `query` tự do ở G08), nên PASS không chứng minh nội dung trả lời đúng.

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) | `starter_v0/tools/{github_search,deduplicate_sources,compare_sources,filter_by_date}/`; registry và `artifacts/tools.yaml` | 1 tool tìm repository và 3 tool xử lý nguồn cục bộ | Validate kiểu/range/enum; mọi lỗi trả error dict; không có write side effect |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py`; `starter_v0/analysis/cp3_pytest.txt` | 12 test function cho happy path, input xấu và failure path của 4 tool | HTTP GitHub được mock offline; local tools không gọi mạng |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: đã viết 12 test function cho 4 tool tự thêm. Ví dụ lỗi mà unit test bắt được nhưng eval không bắt được: GitHub trả HTTP 503, item không phải object, khoảng ngày đảo ngược; tool phải trả error dict thay vì làm agent crash.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) | `tools/github_search`, `tools/deduplicate_sources`, `tools/compare_sources`, `tools/filter_by_date`; `tests/test_tools_todo.py` | Đủ 4 tool tự viết, mỗi tool có `TOOL.md`, registry, declaration và ≥ 3 test | Ba tool xử lý nguồn chạy local; GitHub chỉ đọc public API; mọi tool validate input |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

-

### Ghi nhận xử lý môi trường tại CP1

- Bình ban đầu gặp lỗi PowerShell vì biến `$labPython` chưa có giá trị trong phiên Terminal; đã gán đường dẫn Python của venv và chạy được script.
- Sau đó gặp `Missing API key env var: OPENAI_API_KEY`; đã được hướng dẫn cấu hình đúng `starter_v0/.env`. Bình báo preflight thành công; không lưu API key vào báo cáo. Chưa có file log riêng cho hai lỗi này; bằng chứng trao đổi nằm trong chat, không coi là log đã nộp trong repo.
- Run v0 trong repo xác nhận provider OpenAI hoạt động: 20 case được đo, 0 lỗi provider.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

### Nhận xét sau baseline v0

- Thay đổi thuộc system prompt: bỏ hành vi đoán account/URL; hỏi lại khi thiếu dữ liệu; đặt phạm vi research và quy tắc xác nhận.
- Thay đổi thuộc tools.yaml: mô tả khi dùng/không dùng tool, convention arguments, ý nghĩa send và confirmed.
- Cần review thủ công: chênh lệch nhãn lỗi R13; tính hợp lý của query tương đương; chất lượng dữ liệu tool; việc code chặn send dù model đã chọn sai hành động.
- Giả thuyết dự kiến v1: thay riêng quy tắc thiếu thông tin trong prompt bằng yêu cầu clarify sẽ giảm lỗi missing_info của R10/R11. Chưa sửa prompt, chưa chạy v1; sẽ đo lại toàn suite để kiểm tra tác động và regression.

## 8. Tài liệu tham khảo

- [Quy định bài lab](../../RULES.md), [checkpoints](../../CHECKPOINTS.md), [rubric](../../RUBRIC.md).
- [System prompt baseline](../../starter_v0/artifacts/system_prompt.md), [tool declaration](../../starter_v0/artifacts/tools.yaml).
