# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm


- Team name: H7 (Class L3B).
- Repository: [K5-L3B-DAY03-H7-ResearchAgentToolEval](https://github.com/Ngochung1772k4/K5-L3B-DAY03-H7-ResearchAgentToolEval).
- Members, student IDs and task split: recorded in [`TEAM.md`](../../TEAM.md) and the three individual reports in `report/team/`.
- Provider/model for v0-v3: OpenRouter / `openai/gpt-4o-mini` (recorded in the version runs).

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì


Research Agent searches the public web and social posts, reads a specific URL or arXiv paper, and turns collected sources into a digest. It can search internal policy documents and post to the configured Telegram channel only after the user confirms the exact message.

**Run the UI** from `starter_v0`:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

**Local demo:** `http://127.0.0.1:8501` (local machine only; not a public deployment).

### A2. Tool agent có


| Tool | Purpose | Added by the team? |
|---|---|---|
| `clarify` | Ask for missing details or explicit yes/no confirmation. | No |
| `timeline` | Retrieve recent posts from one explicitly named account. | No |
| `social_search` | Search social posts by keyword; choose Latest or Top. | No |
| `lookup` | Search public web pages and current/recent news. | No |
| `fetch` | Read a specific supplied or search-result URL. | No |
| `format` | Format collected source items as a Markdown digest. | No |
| `send` | Post a confirmed message to the configured Telegram channel. | No |
| `policy` | Search the local company policy documents. | No |
| `papers` | Search arXiv for academic papers and preprints. | No |
| `paper_text` | Download and extract text from a specific arXiv paper. | No |
| `dedupe_sources` | Remove duplicate source URLs while preserving the first item and order. | Yes (CP3) |

### A3. Câu hỏi mẫu để thử


1. Find three AI news stories published today; include each source link and publication date.
2. Show me the latest three posts from @karpathy.
3. Search Top social posts about Qwen3 and summarize the most relevant ones.
4. Read this article and summarize it: `https://openai.com/research/`.
5. Remove duplicate URLs from these collected sources and format the remaining items as bullets.

## 3. Giải pháp


- **Prompt (`artifacts/system_prompt.md`):** added out-of-scope refusal, missing-handle/URL clarification, multi-turn carryover/correction, and explicit confirmation before external publishing.
- **Tool declarations (`artifacts/tools.yaml`):** v2 clarified `clarify.response_type`; v3 clarified the `lookup` query/topic/timeframe mapping. The current declarations further specify when to use and avoid each tool, argument conventions, and a check for title/snippet mismatches. This latest edit has not yet been evaluated as a new version.
- **New tool (`dedupe_sources`):** locally normalizes URLs for duplicate comparison, removes fragments and common tracking parameters, keeps the first matching item in order, and returns structured errors for invalid input. It is called only when deduplication is requested.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi starter trước tối ưu | — | 0.70 (14/20) | `runs/v0_B_base_openrouter_20261110T174808932044.json` |
| v1 | `system_prompt.md` | Hỏi lại khi thiếu thông tin và xác nhận trước khi gửi | 0.70 | 0.85 (17/20) | `runs/v1_B_base_openrouter_20261110T175428175457.json` |
| v2 | `tools.yaml` | Mô tả rõ `response_type` sẽ giảm lỗi arguments của `clarify` | 0.85 | 0.90 (18/20) | `runs/v2_B_base_openrouter_20261110T175938790446.json` |
| v3 | `tools.yaml` | Làm rõ mapping arguments của `clarify` và `lookup` sẽ giảm lỗi tham số | 0.90 | 0.95 (19/20) | `runs/v3_B_base_openrouter_20261110T180412507897.json` |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `send` | Gọi `send` cho câu hỏi toán ngoài phạm vi, thay vì từ chối không gọi tool. | Thêm quy tắc từ chối yêu cầu ngoài phạm vi, không gọi tool. |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Đoán handle Sam Altman dù người dùng chưa nêu tài khoản. | Gọi `clarify` để hỏi người dùng muốn xem tài khoản nào. |
| R11_missing_url | missing_info | `fetch(url="https://example.com/article")` | Bịa URL vì người dùng chưa cung cấp liên kết. | Gọi `clarify` xin URL; không tự đoán URL. |
| R12_confirm_before_send | wrong_boundary | `send` | Gọi `send` khi chưa xác nhận chính xác nội dung với người dùng. | Dùng `clarify` hỏi yes/no; chỉ gọi `send` sau khi được xác nhận. |
| R13_parallel_web_and_tweets | wrong_arg_value | `lookup(query="AI news", timeframe="day")`; `social_search(query="AI")` | `lookup` đổi query từ `AI` thành `AI news` và thiếu `topic="news"`. | Giữ query là `AI`, đặt `topic="news"` khi tìm tin thời sự. |
| R14_out_of_scope_coding | out_of_scope | `send` | Dùng `send` để trả lời yêu cầu viết code ngoài phạm vi. | Từ chối yêu cầu ngoài phạm vi; chỉ dùng `send` cho việc đăng/gửi sau xác nhận. |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

Run: `starter_v0/runs/v3_B_group_openrouter_20261110T190141165371.json` — 10/10 measured, 10 pass, 0 provider errors.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_dedupe_sources_single_turn | Route yêu cầu gộp nguồn trùng vào tool mới | `dedupe_sources` | PASS |
| G02_format_explicit_bullets | Format dữ liệu đã có thành bullet digest | `format(template="bullets")` | PASS |
| G03_lookup_news_month | Query giữ chủ đề, đúng loại news và timeframe tháng | `lookup(topic="news", timeframe="month")` | PASS |
| G04_timeline_explicit_handle_limit | Chuẩn hóa handle `@karpathy` và giữ limit | `timeline(screenname="karpathy", limit=2)` | PASS |
| G05_internal_citation_policy | Route chính sách trích dẫn nội bộ đến policy | `policy(policy_area="source_citation")` | PASS |
| G06_multiturn_clarify_account | Dùng handle được bổ sung và giữ số lượng qua lượt | `timeline(screenname="karpathy", limit=3)` | PASS |
| G07_multiturn_lookup_carry_timeframe | Đổi query sang robotics, giữ news và timeframe tuần | `lookup(query="robotics", topic="news", timeframe="week")` | PASS |
| G08_multiturn_social_search_correction | Giữ query, sửa loại kết quả và số lượng | `social_search(query="Qwen3", search_type="Top", limit=3)` | PASS |
| G09_multiturn_url_clarification | Dùng URL đã được bổ sung ở lượt trước | `fetch(url="https://openai.com/research/")` | PASS |
| G10_multiturn_dedupe_sources | Route ngữ cảnh nhiều lượt đến tool mới | `dedupe_sources` | PASS |



Evidence: `starter_v0/transcripts/v3_openrouter_20261110T191513477383.transcript.json` (CLI transcript, 4 user turns; OpenRouter `openai/gpt-4o-mini`; artifact v3). The separate Streamlit transcript is `starter_v0/transcripts/v3_openrouter_streamlit_20261110T225954630476.transcript.json` (3 turns, all answered); it demonstrates live UI interaction but contains ordinary research requests only, with no clarification or send flow.

| Turn | User request | Tool calls | Outcome |
|---|---|---|---|
| 1 | Find recent AI research news and summarize it in 3 bullets. | `lookup(query="AI", topic="news", timeframe="day", max_results=3)` | Normal research request; lookup ran, but the search source returned a connection error. |
| 2 | Show me recent posts from the account. | `clarify(response_type="text")` | Asked which account; transcript status `waiting_for_user`. |
| 3 | Use @karpathy and show 2 posts. | `timeline(screenname="karpathy", limit=2)` | Used the supplied handle and limit; the social source returned a connection error. |
| 4 | Post this summary to our Telegram channel: AI agents are improving quickly. | No tool call | Asked for yes/no confirmation; no message was sent. |

These files document complementary behavior, not one complete UI transcript: the CLI transcript contains the missing-information/follow-up and send-request scenarios, while the Streamlit transcript has three completed UI turns. In the CLI send turn, the assistant asks for confirmation in plain text but does not call `clarify`; no send occurs. A separate successful Telegram send is documented only in the bonus transcript `starter_v0/transcripts/bonus-telegram_openrouter_20261111T101621746672.transcript.json`.

### B5a. Required Evidence — Tool mới, unit test, UI


| Item | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
| New tool (`dedupe_sources`) | `starter_v0/tools/dedupe_sources/tool.py`, `TOOL.md`, `tools/__init__.py`, `artifacts/tools.yaml` | Deduplicates by normalized URL, keeps first occurrence and order, preserves meaningful query parameters. | URL matching only: it does not follow redirects or detect identical page content at different URLs. Invalid input returns an error dict and rejects the whole list. |
| Unit and regression tests | `starter_v0/tests/test_tools_todo.py`, `starter_v0/tests/test_chat_transcripts.py`, `starter_v0/runs/pytest_postmerge_64a8fb1_20261111.txt` | Covers dedupe and bonus tools plus successful and failed-provider transcript persistence. Full suite after merge: 165 passed, 0 failed. | Tests use fake providers and mocked HTTP; external API availability is not covered by unit tests. |
| UI and live transcript | `starter_v0/app.py`, `starter_v0/requirements.txt`, `starter_v0/transcripts/v3_openrouter_streamlit_20261110T225954630476.transcript.json`, `starter_v0/transcripts/v3_openrouter_streamlit_20261110T192044246874.transcript.json`, `starter_v0/transcripts/v3_openrouter_20261110T191513477383.transcript.json` | Streamlit served HTTP 200 locally and supports chat/transcript download. The clean Streamlit transcript has three answered turns; a separate five-turn Streamlit transcript records three answers and two provider errors; the four-turn CLI transcript records clarification/follow-up and a send request. | Local-only UI; no public deployment. No single UI transcript demonstrates all required scenarios. The CLI send request received a text confirmation question without a `clarify` tool call; no message was sent. The two Streamlit provider errors are retained as observed, not represented as successful answers. |

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | `starter_v0/runs/v3-qwen7b_B_base_ollama_20261110T232218471039.json`; `starter_v0/runs/v3-qwen3b_B_base_ollama_20261111T093456906354.json`; `starter_v0/runs/v4-local-qwen7b_B_base_ollama_20261111T091247806442.json`; `starter_v0/runs/v5-local-qwen7b_B_base_ollama_20261111T091911691061.json`; `starter_v0/runs/v5-local-on-cloud_B_base_openrouter_20261111T092533127696.json` | Qwen 7B baseline 10/20; Qwen 3B baseline 8/20; v4 Qwen 7B improved to 13/20; v5 stayed at 13/20. Local-tuned artifacts scored 19/20 on cloud, matching cloud v3. All full runs measured 20 cases with 0 provider errors. | Llama3.2:3b attempt was interrupted at R12; the completed Qwen2.5:3b run supplies the second local baseline. Local models remain less accurate than cloud. |
| Hơn 3 tool mới (≥ 4) | `starter_v0/tools/dedupe_sources/`; `starter_v0/tools/rank_sources/`; `starter_v0/tools/filter_sources/`; `starter_v0/tools/group_sources/`; `starter_v0/data/eval_bonus_tools.json`; `starter_v0/runs/bonus-tools-v1_B_extension_openrouter_20261111T094527513436.json` | Four group-built tools are registered; all 3 extension routing cases passed. Each added curation tool has happy-path, invalid-input, and error-path unit tests. | The three bonus tools operate only on supplied items; they do not verify source facts or make network requests. |
| `send` gửi thật lên Telegram sau xác nhận | `starter_v0/transcripts/bonus-telegram_openrouter_20261111T101621746672.transcript.json` | Two-turn evidence: `clarify(response_type="yes_no")` showed the exact text; user replied `Yes`; then `send(confirmed=true)` returned `status: sent`. | The message was sent only after explicit confirmation. The transcript contains no bot token. |
| Test challenge (0 skipped / regression test) | `starter_v0/tests/test_tools_todo.py`, `starter_v0/tests/test_chat_transcripts.py`; `starter_v0/runs/pytest_bonus_20261111.txt`, `starter_v0/runs/pytest_postmerge_64a8fb1_20261111.txt` | Earlier bonus suite: 163 passed; after merging transcript persistence tests: 165 passed, 0 failed. | Tests are offline; HTTP calls use mocks and chat tests use fake providers. |

Test challenge command: `cd starter_v0 && .\.venv\Scripts\python.exe -m pytest -q` -> 165 passed, 0 failed. Output: `starter_v0/runs/pytest_postmerge_64a8fb1_20261111.txt`.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---:|---:|---:|---:|---|
| v3 | OpenRouter `openai/gpt-4o-mini` | cloud v3 | 0.95 | 1.00 | 0.95 | 1.00 | `starter_v0/runs/v3_B_base_openrouter_20261110T180412507897.json` |
| v3-qwen7b | Ollama `qwen2.5:7b` | shared prompt + current tools | 0.50 | 0.60 | 0.50 | 0.6667 | `starter_v0/runs/v3-qwen7b_B_base_ollama_20261110T232218471039.json` |
| v3-qwen3b | Ollama `qwen2.5:3b` | shared prompt + current tools | 0.40 | 0.55 | 0.40 | 0.50 | `starter_v0/runs/v3-qwen3b_B_base_ollama_20261111T093456906354.json` |
| v4-local-qwen7b | Ollama `qwen2.5:7b` | local prompt v4 + current tools | 0.65 | 0.70 | 0.65 | 0.50 | `starter_v0/runs/v4-local-qwen7b_B_base_ollama_20261111T091247806442.json` |
| v5-local-qwen7b | Ollama `qwen2.5:7b` | local prompt v4 + local tools v5 | 0.65 | 0.70 | 0.65 | 0.50 | `starter_v0/runs/v5-local-qwen7b_B_base_ollama_20261111T091911691061.json` |
| v5-local-on-cloud | OpenRouter `openai/gpt-4o-mini` | local prompt v4 + local tools v5 | 0.95 | 1.00 | 0.95 | 1.00 | `starter_v0/runs/v5-local-on-cloud_B_base_openrouter_20261111T092533127696.json` |

Llama3.2:3b preflight passed, but its full base run was interrupted at R12. The 3-case smoke run (`starter_v0/runs/smoke-llama3b_B_base_ollama_20261110T235342266196.json`) is diagnostic only; the complete qwen2.5:3b run above is the second local baseline.

The table below counts qwen2.5:7b baseline failures; v4/v5 outcomes are noted in the fix column. The qwen2.5:3b baseline scored 0.40 and reported 4 wrong-tool, 3 wrong-argument, 2 out-of-scope, 2 missing-info, and 1 boundary failure; it also had 7 missing-tool-call and 2 unexpected-tool-call mismatches.

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool | 4 wrong-tool failures | R03, R13 | v4 routing checklist; wrong-tool failures fell to 2 | Partly |
| invalid JSON args (`_invalid_json_arguments`) | 0 | None observed | No change needed | Not observed |
| no tool call / answered directly | 8 missing-tool-call mismatches | R01, R04, R10, R11 | v4 checklist; missing-tool-call mismatches fell to 6 | Partly |
| Clarification and confirmation | 3 failures | R10, R11, R12 | v5 added concrete clarify examples | No measurable change; v5 remained 13/20 |
| missed `clarify` | 3 (2 missing-info, 1 boundary) | R10, R11, R12 | v5 added concrete examples | No measurable change |

- **What helped most:** v4's routing checklist raised Qwen case accuracy from 0.50 to 0.65 and cut wrong-tool failures from 4 to 2. v5's clarify examples did not change the score.
- **Cloud cross-check:** v5 local artifacts scored 0.95 on OpenRouter (19/20), matching the cloud v3 baseline; routing, argument, and multiturn metrics were unchanged.
- **When to choose local:** current Qwen results are below cloud accuracy (0.65 vs 0.95); local is suitable when offline/privacy matters and measured quality is acceptable, while cloud remains the stronger choice for reliability.

## 5. Khó khăn và cách xử lý


- Gemini preflight initially returned a transient 503; a Groq check from the repository root also failed because `env_loader` was outside that working directory, and a later SDK call hit a Windows application-control block on the `jiter` DLL. The team switched evaluation to OpenRouter and confirmed the provider with the preflight script.
- RapidAPI initially returned HTTP 403 because the account was not subscribed to the selected API. After correcting the RapidAPI host/subscription setup, a direct timeline request returned HTTP 200. A later live transcript still records source connection errors, so live-tool availability can vary independently of model routing.
- Group evaluation initially reported no phase-B cases because `data/eval_group.json` was empty. Ten original group cases were added and the v3 group run measured 10/10 with zero provider errors (see B3 run reference).
- On Windows, the chat loop's wrench emoji could not be written using the legacy console encoding. The tool log marker was changed to ASCII `[tool]`; live chat then recorded tool calls instead of failing while printing them.
- Tavily returned a result whose title and snippet discussed different subjects, and the agent did not surface available publication dates. The current lookup declaration tells the agent to omit or verify mismatched results; this post-v3 change still needs a new eval run.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection


- **Prompt vs. tool declaration:** The system prompt fixed broad behavior boundaries and clarification/carryover; `tools.yaml` made individual routing and argument conventions explicit. Base accuracy improved from 14/20 (v0) to 19/20 (v3), while the v3 run still failed the confirmation-before-send case. See B1 and the corresponding run files.
- **Human review remains necessary:** Routing metrics do not catch a title/snippet mismatch, unsupported freshness claims, or an omitted caveat. Review source title, snippet, URL, and date before presenting a news digest; the AHA result, for example, is a preliminary conference abstract, not a peer-reviewed paper.
- **Remaining boundary risk:** The v3 base eval still failed R12 (`wrong_boundary`). The transcript's post request received a textual yes/no question and no `send` call, but the tool was not `clarify`; keep this as a known gap rather than claiming the boundary is fully solved.
- **Next experiment:** Treat the latest `tools.yaml` rewrite as a new version, run the contract check and base eval, and compare routing/argument scores. Add targeted evaluation for source-title/snippet consistency and publication-date reporting before claiming those quality issues are fixed.

## 8. Tài liệu tham khảo

-
