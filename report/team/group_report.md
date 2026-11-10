# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> CP5 bổ sung ngày 11/11/2026 (GMT+7) trên main GitHub `a557a55`; giữ kết quả và đóng góp CP1–CP4 của nhóm. Không có bằng chứng Phần A xong trước showdown 16:30. Không hồi tố thời gian hoàn thành; việc chấp nhận bài theo deadline/gia hạn do coach quyết định.

## 1. Thông tin nhóm

- Tên nhóm: Hehehe (theo tên repo; cần nhóm xác nhận).
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model: v0–v3 và CP5 dùng `openai` / `gpt-4o-mini`.
- Trạng thái kỹ thuật: có CP1–CP4 của nhóm, UI 14 tool, 5 lượt CLI thật, run base/group mới và báo cáo cá nhân 4 thành viên. Còn cần nhóm tự review, xác nhận người ngoài nhóm dùng thử và chốt commit nộp bài.

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research desk tìm web, bài đăng, repository GitHub, paper và chính sách nội bộ; đọc nguồn, loại trùng, so sánh và lọc ngày trước khi tạo digest. Agent hỏi khi thiếu dữ liệu và xin xác nhận trước hành động gửi Telegram.

**Cách chạy UI:**

Từ `starter_v0/`, sau khi cài requirements và cấu hình `.env`:

```powershell
& ..\venv\Scripts\python.exe -m streamlit run app.py --server.address=127.0.0.1 --server.port=8501 --server.enableAgentApi=false
```

Dependency `streamlit>=1.67,<2`; đã kiểm tra bản 1.67.0. Có script `starter_v0/scripts/start_ui.ps1`; xem [hướng dẫn đầy đủ](../../docs/UI-GUIDE.md).

**Link dùng thử (deploy):**

https://writing-what-vat-dedicated.trycloudflare.com — quick tunnel tới cổng demo 8511, có mã dùng thử do Bình cung cấp riêng. Link đã trả HTTP 200; agent API trên server chia sẻ bị tắt. Link chỉ còn hoạt động khi máy host/UI/tunnel chạy; cập nhật URL khi khởi động lại tunnel. Chưa có xác nhận người ngoài nhóm thử.

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
| timeline | lấy bài đăng của một tài khoản X/Twitter | không |
| social_search | tìm bài đăng theo chủ đề | không |
| lookup | tìm web/tin tức theo từ khóa và thời gian | không |
| fetch | đọc nội dung URL | không |
| format | trình bày items thành digest Markdown | không |
| send | gửi Telegram khi đã xác nhận; demo chưa có key gửi thật | không |
| policy | tra kho chính sách Markdown nội bộ | không |
| papers | tìm paper arXiv | không |
| paper_text | tải PDF arXiv và trích text | không |
| github_search | tìm repository GitHub công khai theo từ khóa, ngôn ngữ và cách sắp xếp | có |
| deduplicate_sources | loại nguồn trùng theo URL chuẩn hóa hoặc tiêu đề | có |
| compare_sources | so sánh metadata, độ đầy đủ và điểm giống/khác giữa các nguồn | có |
| filter_by_date | lọc danh sách nguồn theo khoảng ngày bao gồm hai biên | có |

### A3. Câu hỏi mẫu để thử

1. Tìm 3 repository Python về research agent trên GitHub, sắp theo số sao, kèm URL.
2. Theo chính sách nội bộ, có được đưa dữ liệu khách hàng vào AI bên ngoài không?
3. Loại trùng theo URL: `[{"title":"A","url":"https://example.com/a?utm_source=demo"},{"title":"B","url":"https://example.com/a"}]`.
4. Lấy 2 bài đăng mới nhất giúp tôi. Sau khi agent hỏi lại, trả lời: Tài khoản NASA trên X.
5. Tôi muốn gửi 'Bản tin demo của nhóm Hehehe' lên Telegram. Hãy hỏi xác nhận trước và chưa gửi. Sau đó trả lời: Không, hủy gửi.

## 3. Giải pháp

- Tiệp tối ưu CP2 qua v1–v3; giữ nguyên các run/metric ở B1. Hà Anh triển khai 4 tool mới ở CP3; Nghĩa hoàn thiện 10 case của CP4 ở B3.
- CP5: Codex triển khai theo yêu cầu Bình trên main `a557a55`; UI dùng cùng `run_model_tool_loop` của `chat.py`, prompt/declaration/registry 14 tool của nhóm. Không áp dụng lại prompt, dedup hoặc bộ case ở bản local tự thử trước đó.
- UI tách phiên, lưu/download JSON, hiện lỗi tool/provider, giới hạn lượt/input/vòng và có mã demo tùy chọn.

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
| cp5-team | UI/support; giữ prompt và 14 tool từ main | Kiểm tra bàn giao đúng cấu hình nhóm; không phải vòng tối ưu prompt mới | v3 base=0.85; CP4 group=1.00 | base=0.85; group=1.00; 0 provider errors | [Base](../../starter_v0/runs/cp5-team_B_base_openai_20261111T004229851343.json), [group](../../starter_v0/runs/cp5-team_B_group_openai_20261111T004229756879.json) |

**Bàn giao CP5:** base 17/20, routing 95%, arguments 85%, multi-turn 83.33%; group 10/10. Mỗi suite đo đủ case và không lỗi provider. `prompt_hash=0d8d6477582f…`, `tools_hash=835122e42569…`, khớp cấu hình CP4 trên Windows. Snapshot đúng byte ở [artifacts/versions/cp5-team](../../starter_v0/artifacts/versions/cp5-team/README.md). Pytest mới **102 passed, 14 skipped, 0 failed**; [output](../../starter_v0/analysis/cp5_team_pytest.txt). Chưa lặp thống kê; không diễn giải group 100% là độ đúng tổng quát.

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

Nguồn cho bảng: [run v0](../../starter_v0/runs/v0_B_base_openai_20261110T180441850646.json), `results[*].result`. Cột Fix ghi đề xuất tại thời điểm baseline; các thay đổi đã thực hiện và đo ở v1–v3 xem B1. Kiểm tra CP5 vẫn còn R10 (`social_search(query="")`), R12 (`clarify(text)` thay `yes_no`) và M03 (`andrejkarpathy` thay `karpathy`).

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

Nguồn: [transcript CLI CP5](../../starter_v0/transcripts/cp5-team-live_openai_20261111T004205700741.transcript.json), [output](../../starter_v0/analysis/cp5_team_cli_live.txt). Codex tự động nhập kịch bản vào `chat.py`; model/API/tool chạy thật, không phải mock và không phải bằng chứng người ngoài nhóm đã dùng thử. Cùng prompt/tools hash với run cp5-team.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tìm 2 repo Python về research agent | github_search | cp5-team-live+p0d8d6477582f+t835122e42569 | GitHub API trả repo, URL và số sao |
| 2 | Lấy bài nhưng chưa chọn tài khoản | clarify(text) | như trên | waiting_for_user, hỏi tài khoản |
| 3 | Bổ sung NASA, 2 bài | timeline | như trên | API thật trả 2 bài kèm URL |
| 4 | Xin gửi bản demo, yêu cầu xác nhận | clarify(yes_no) | như trên | hỏi xác nhận, chưa send |
| 5 | Từ chối, hủy gửi | không gọi tool | như trên | thông báo không gửi |

**UI runtime:** [transcript](../../starter_v0/transcripts/cp5-team-ui_5133d9521b474828bbe6b38e8acc442f.transcript.json) chứng minh `deduplicate_sources(strategy="url")` chạy thật trên main: 2 nguồn còn 1. Đã kiểm tra đăng nhập mã demo, danh sách 14 tool, JSON download và reset; chi tiết ở [QA](../../starter_v0/analysis/cp5_team_qa.md).

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) | `starter_v0/tools/{github_search,deduplicate_sources,compare_sources,filter_by_date}/`; registry và `artifacts/tools.yaml` | 1 tool tìm repository và 3 tool xử lý nguồn cục bộ | Validate kiểu/range/enum; mọi lỗi trả error dict; không có write side effect |
| Unit test tool mới (≥ 3 test/tool) | `starter_v0/tests/test_tools_todo.py`; `starter_v0/analysis/cp3_pytest.txt` | 12 test function cho happy path, input xấu và failure path của 4 tool | HTTP GitHub được mock offline; local tools không gọi mạng |
| UI (lệnh chạy + link dùng thử) | [app.py](../../starter_v0/app.py), [ui_support.py](../../starter_v0/ui_support.py), [hướng dẫn](../../docs/UI-GUIDE.md), A1 | 14 tool, nhiều lượt, hiện lỗi, lưu/download transcript, reset, mã demo | 20 lượt/phiên, 6000 ký tự, 4 vòng tool; không chia sẻ credential; tunnel tạm |

Tool unit tests: đã viết 12 test function cho 4 tool tự thêm. Ví dụ lỗi mà unit test bắt được nhưng eval không bắt được: GitHub trả HTTP 503, item không phải object, khoảng ngày đảo ngược; tool phải trả error dict thay vì làm agent crash.

### B5. Bonus Evidence

Bonus ghi riêng theo rubric; chỉ claim phần có bằng chứng thực tế.

| Bonus | Bằng chứng | Trạng thái |
|---|---|---|
| Hơn 3 tool mới (≥4) | 4 folder tool của Hà Anh, TOOL.md, registry/declaration, ≥3 test/tool và group cases G01/G02/G06/G07/G08 | Có bằng chứng; giữ nguyên phần nhóm đã làm |
| Small Local Model | Không có run ≥2 model local | Không thực hiện |
| Telegram gửi thật | CLI kiểm tra xác nhận/hủy; group G09 trả lỗi thiếu key | Không claim gửi thành công |
| Test challenge | 102 passed, 14 skipped; chưa có regression bug starter được chứng minh | Không claim bonus này |

### B7. Small Local Model Challenge (bonus)

Không thực hiện, không có run local hoặc so sánh cloud/local để báo cáo.

## 5. Khó khăn và cách xử lý

- Bản local của Bình ở commit CP1, chậm 18 commit so với main GitHub; đã stash bản tự thử, fetch và fast-forward main trước khi làm CP5. Không lấy các run/local edits thay đóng góp của nhóm.
- Main có 14 tool còn bản tự thử có 11 tool và dedup signature khác. UI mới đọc declaration/registry của main; test xác nhận tham số strategy, không sửa tool của Hà Anh.
- AppTest/socket localhost bị hạn chế bởi sandbox Windows; kiểm thử được chạy với quyền socket nội bộ. Tests vẫn offline và fixture chặn HTTP thật.
- [Run base mới](../../starter_v0/runs/cp5-team_B_base_openai_20261111T004229851343.json) xác nhận R10/R12/M03 chưa đạt; giữ nguyên prompt nhóm trong CP5, ghi lỗi và hướng sửa thay vì dùng metric bản local.
- UI gọi model thật có lúc đổi sang tiếng Anh hoặc tự xử lý thay gọi filter_by_date; [transcript UI](../../starter_v0/transcripts/cp5-team-ui_5133d9521b474828bbe6b38e8acc442f.transcript.json) ghi hành vi thực tế. Quick tunnel có hạn uptime; xem [QA](../../starter_v0/analysis/cp5_team_qa.md).

### Ghi nhận xử lý môi trường tại CP1

- Bình ban đầu gặp lỗi PowerShell vì biến `$labPython` chưa có giá trị trong phiên Terminal; đã gán đường dẫn Python của venv và chạy được script.
- Sau đó gặp `Missing API key env var: OPENAI_API_KEY`; đã được hướng dẫn cấu hình đúng `starter_v0/.env`. Bình báo preflight thành công; không lưu API key vào báo cáo. Chưa có file log riêng cho hai lỗi này; bằng chứng trao đổi nằm trong chat, không coi là log đã nộp trong repo.
- Run v0 trong repo xác nhận provider OpenAI hoạt động: 20 case được đo, 0 lỗi provider.

## 6. Tổng hợp đóng góp

Bình phụ trách CP1 và CP5 với hỗ trợ Codex; Tiệp phụ trách CP2; Hà Anh phụ trách CP3 và 4 tool mới; Nghĩa phụ trách CP4. Codex trực tiếp triển khai/chạy kiểm tra CP5 theo yêu cầu Bình. Chi tiết và commit nằm trong [TEAM.md](../../TEAM.md) và báo cáo cá nhân của 4 thành viên; không ghi các thao tác AI làm là thao tác mỗi người tự làm.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- **Prompt và declaration:** CP2 của Tiệp sửa hành vi clarify/xác nhận/routing trong prompt, rồi làm rõ từng tool/arguments trong declaration. Kết quả v3 giảm so với v2 nên không thể kết luận sửa description luôn tốt hơn; B1 giữ cả regression.
- **Review thủ công:** R12 hỏi nội dung còn thiếu là hợp lý về hội thoại nhưng không khớp kiểu yes_no của base; chỉ nên xác nhận hành động gắn với nội dung cụ thể. R08/R14 PASS khi không gọi tool không chứng minh model từ chối yêu cầu ngoài phạm vi. Chất lượng nguồn và items đầu vào không được metric routing chấm đầy đủ.
- **Vòng sau:** thử một giả thuyết nhỏ để tránh social_search(query rỗng) khi thiếu chủ đề/account; đo lại base và group. Kiểm tra cách giữ handle được user sửa ở M03; không sửa case cố định để tăng điểm.
- **Giới hạn CP5:** UI dùng cùng cấu hình main để bảo toàn tính đối chiếu; chưa sửa các regression R10/R12/M03 hoặc rule ngôn ngữ. Không dùng 95% của bản local làm kết quả của nhóm.
- **Độ tin cậy:** mỗi cấu hình/suite mới chỉ một run, chưa lặp thống kê; 100% group không suy ra khả năng tổng quát. Compare_sources so metadata, không xác minh sự thật; dedup theo URL/title có thể gộp hai nội dung khác nhau cùng tiêu đề.
- **Trước chốt nộp:** cần người ngoài nhóm dùng thử, từng thành viên tự review và giải thích phần việc, gộp CP5 vào main và chốt commit, từng người nộp LMS. Không có bằng chứng mốc Phần A 16:30 hoặc Telegram gửi thật.

## 8. Tài liệu tham khảo

- [Quy định bài lab](../../RULES.md), [checkpoints](../../CHECKPOINTS.md), [rubric](../../RUBRIC.md).
- [System prompt hiện tại](../../starter_v0/artifacts/system_prompt.md), [tool declaration](../../starter_v0/artifacts/tools.yaml).
