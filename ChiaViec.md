# Chia việc nhóm SNN — Day 03 Research Agent Tool Eval

Mục tiêu: 4 người làm song song **không đụng file của nhau**. Mỗi file (hoặc mỗi vùng trong file) chỉ có **một chủ**. Mọi lệnh chạy từ `starter_v0/`.

| Người | Họ tên | Vai trò | Tiêu chí rubric |
|---|---|---|---|
| Người 1 | **Nguyễn Lương Nguyên** | Prompt, tool declaration, vòng lặp v0→v3 | C1, C2, C3 |
| Người 2 | **Mai Xuân Nhân** | Tool mới + unit test cho tool mới | C4 (+ bonus ≥ 4 tool) |
| Người 3 | **Bùi Đức Hiếu** | 10 eval case nhóm + test challenge | C5 (+ bonus test) |
| Người 4 | **Bùi Thái Sỹ** | UI, live chat, Phần A báo cáo (nhóm trưởng) | C6, C7-A, C8 (+ bonus Telegram) |

Cả nhóm cùng làm C7 (Phần B, mỗi người một mục) và C8 (`TEAM.md` + báo cáo cá nhân).

---

## 1. Bảng sở hữu file

> ✅ = người duy nhất được sửa file/vùng đó. Muốn thay đổi file của người khác thì nhắn chủ file sửa giúp.

| File / vùng | Nguyên | Nhân | Hiếu | Sỹ |
|---|:-:|:-:|:-:|:-:|
| `artifacts/system_prompt.md` | ✅ | | | |
| `artifacts/tools.yaml` — 10 tool có sẵn (`clarify` … `paper_text`) | ✅ | | | |
| `artifacts/tools.yaml` — **block tool mới, thêm ở cuối file** | | ✅ | | |
| `artifacts/version_log.csv` | ✅ | | | |
| `tools/<tool_mới>/tool.py`, `tools/<tool_mới>/TOOL.md` | | ✅ | | |
| `tools/__init__.py` | | ✅ | | |
| `tests/test_tools_todo.py` — dòng 1–105 (stub tool có sẵn) | | | ✅ | |
| `tests/test_tools_todo.py` — mục `YOUR NEW TOOL(S)` (dòng 107 trở xuống) | | ✅ | | |
| Sửa bug trong tool có sẵn (`tools/<tool_có_sẵn>/tool.py`) | | | ✅ | |
| `data/eval_group.json` | | | ✅ | |
| `app.py` (UI mới), `requirements.txt` | | | | ✅ |
| `report/team/poster.html` | | | | ✅ |
| `runs/*.json` | run base v0–v3 | | run group | |
| `transcripts/*.transcript.json` | | | | ✅ |
| `TEAM.md` — bảng thành viên + khung 4 mục cá nhân + commit chốt | | | | ✅ |
| `TEAM.md` — mục cá nhân của mình | mỗi người | mỗi người | mỗi người | mỗi người |
| `report/team/MSSV_HoTen.md` của mình | mỗi người | mỗi người | mỗi người | mỗi người |

Không ai sửa nội dung case trong `data/eval_base.json` và `data/eval_research_extension.json`.

## 2. Chia vùng trong `report/team/group_report.md`

| Mục | Chủ |
|---|---|
| 1. Thông tin nhóm, **A1, A2, A3** (Phần A — xong trước 16:30) | Sỹ |
| 3. Giải pháp, **B1**, **B2**, 7. Reflection (B6), B7 (nếu làm local model) | Nguyên |
| **B5a** dòng "Tool mới" + "Unit test tool mới"; **B5** dòng "Hơn 3 tool mới" | Nhân |
| **B3**; **B5** dòng "Test challenge" | Hiếu |
| **B4**; **B5a** dòng "UI"; **B5** dòng "send gửi Telegram" | Sỹ |
| 5. Khó khăn | mỗi người thêm 1 gạch đầu dòng, Sỹ gom cuối buổi |

Quy tắc: chỉ sửa **đúng dòng của mình**, không format lại cả bảng, không đổi thứ tự dòng.

---

## 3. Việc của từng người

### Người 1 — Nguyễn Lương Nguyên (Prompt & vòng lặp version)

Branch: `p1-prompt`

**CP1 — trước 15:00**
- [ ] Cấu hình `starter_v0/.env` (provider key, `TAVILY_API_KEY`, `FIRECRAWL_API_KEY`, `RAPIDAPI_KEY`, `RAPIDAPI_TWITTER_HOST`) theo `docs/TOOL-SETUP.md`.
- [ ] `python scripts/preflight_provider.py --provider openrouter` pass; `pytest` chạy được.
- [ ] Chạy baseline **v0** (chưa sửa prompt/tools):
  `python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json`
- [ ] Kiểm tra run hợp lệ: `provider_error_cases == 0`, `measured_cases == total_cases`.
- [ ] Ghi dòng v0 vào `artifacts/version_log.csv`.
- [ ] Điền bảng **B2** — mỗi case FAIL có loại lỗi (`wrong_tool`, `wrong_arg_value`, `missing_info`, `wrong_boundary`, …) và nguyên nhân.
- [ ] Merge vào `main`.

**CP2 — v1 (15:30), v2 (16:00), v3 (17:30)**
- [ ] `system_prompt.md`: bỏ 3 chỉ dẫn xấu (đoán thay vì hỏi, gửi không cần xác nhận, ép một bước); thêm rule routing (khi nào `timeline` / `social_search` / `lookup` / `fetch` / `clarify` / `format`).
- [ ] `tools.yaml` (chỉ 10 tool có sẵn): mỗi `description` nói rõ làm gì, **khi nào dùng / không dùng**, convention args (handle không có `@`, `topic=news`, `timeframe`, `search_type=Top|Latest`); `send` chỉ gửi khi `confirmed=true`.
- [ ] Mỗi version **một giả thuyết**, chạy lại base eval, ghi `version_log.csv` (hash, hypothesis, metric before/after, run file).
- [ ] **Pull `main` sau khi Nhân merge tool mới, trước khi chạy v2.** Ghi chú trong `version_log.csv` rằng `tools_hash` của v2 đổi một phần vì có thêm tool mới.
- [ ] Sau mỗi lần sửa: `pytest tests/test_tool_contract.py` xanh.
- [ ] Merge v3 vào `main` và báo cho Hiếu + Sỹ.

**Báo cáo**
- [ ] Mục 3 Giải pháp, **B1**, **B2**, mục 7 Reflection.
- [ ] Báo cáo cá nhân + mục của mình trong `TEAM.md`.

**Bonus (nếu còn thời gian):** Small Local Model Challenge (Ollama, ≥ 2 model, `v4-local`, `v5-local`, bảng B7). Dùng file riêng `artifacts/system_prompt_local.md` để không phá bản v3.

---

### Người 2 — Mai Xuân Nhân (Tool mới + unit test)

Branch: `p2-newtool`

**CP3 — trước 15:30 (phải merge trước khi Nguyên chạy v2)**
- [ ] Chọn ý tưởng tool mới, báo nhóm tên tool (để Nguyên biết khi viết rule routing).
- [ ] Tạo `tools/<tên>/tool.py` + `tools/<tên>/TOOL.md`, frontmatter đúng contract trong `tools/README.md`.
- [ ] Tool **trả về error dict, không raise** khi input xấu hoặc API lỗi.
- [ ] Đăng ký trong `tools/__init__.py` (`TOOL_FUNCTIONS`).
- [ ] Thêm khai báo tool vào **cuối** `artifacts/tools.yaml` (chỉ block của tool mới, không sửa tool khác). Description nói rõ khi nào dùng / không dùng.
- [ ] Viết ≥ 3 test trong mục `YOUR NEW TOOL(S)` của `tests/test_tools_todo.py` (thay 3 stub `test_my_new_tool_*`):
  1. happy path (mock HTTP bằng `fake_http` nếu gọi API),
  2. input xấu từ model (chuỗi rỗng, sai kiểu, ngoài enum),
  3. nhánh lỗi (thiếu key, HTTP 429/timeout) → trả error dict.
- [ ] `pytest` 0 failed, `pytest tests/test_tool_contract.py` xanh.
- [ ] Viết 1–2 eval case route tới tool mới và **gửi nội dung cho Hiếu** (không tự sửa `eval_group.json`).
- [ ] Merge vào `main`, báo Nguyên pull.

**Báo cáo**
- [ ] **B5a** dòng "Tool mới" và "Unit test tool mới" (số test, một ví dụ lỗi unit test bắt được mà eval không bắt được).
- [ ] Báo cáo cá nhân + mục của mình trong `TEAM.md`.

**Bonus:** viết thêm tool cho đủ **≥ 4 tool tự viết**, mỗi tool đủ `TOOL.md` + đăng ký + ≥ 3 test + eval case (gửi case cho Hiếu). Điền dòng "Hơn 3 tool mới" trong B5.

---

### Người 3 — Bùi Đức Hiếu (Eval nhóm + test challenge)

Branch: `p3-eval`

**CP4 — trước 16:00**
- [ ] Viết **đúng 10 case** vào `data/eval_group.json`: **5 single turn** (`query`) + **5 multi turn** (`turns`).
- [ ] Mỗi case có: `id`, `phase: "B"`, `failure_type` (một trong `wrong_tool`, `wrong_arg_value`, `wrong_boundary`, `unnecessary_tool`, `out_of_scope`, `missing_info`), `expect` (`tool_calls` chỉ chứa args cần kiểm tra, hoặc `no_tool`), `metadata.what_it_tests`.
- [ ] Ít nhất 1 case route tới tool mới (lấy nội dung từ Nhân).
- [ ] Không chép case có sẵn trong `eval_base.json`.
- [ ] Chạy thử với prompt hiện tại để kiểm tra không lỗi schema.
- [ ] **Sau khi Nguyên merge v3**, pull `main` rồi chạy run chính thức:
  `python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json`
- [ ] Merge vào `main`.

**Test challenge (bonus)**
- [ ] Điền hết các stub `pytest.skip(TODO)` ở **dòng 1–105** của `tests/test_tools_todo.py` (clarify, format, send, lookup, fetch, timeline, social_search, policy). Không sửa mục `YOUR NEW TOOL(S)` của Nhân.
- [ ] Thử input biên (`limit=0`, `top_k=0`, `max_results="5"`, `items` thiếu `url`…). Nếu bắt được bug trong tool có sẵn: sửa tool, giữ regression test.
- [ ] Đạt khi `pytest` báo **0 failed, 0 skipped**.

**Báo cáo**
- [ ] **B3** (10 case, kết quả từ run group); **B5** dòng "Test challenge" (bug tìm được, cách sửa, test regression).
- [ ] Báo cáo cá nhân + mục của mình trong `TEAM.md`.

---

### Người 4 — Bùi Thái Sỹ (UI, live chat, Phần A)

Branch: `p4-ui`

**Nhóm trưởng**
- [ ] **Commit đầu tiên của cả nhóm** (trước khi mọi người tạo branch): điền bảng thành viên trong `TEAM.md` và tạo sẵn 4 mục `## HoTen-MSSV` trống cho cả nhóm → merge `main`, báo cả nhóm pull.
- [ ] Theo dõi thứ tự merge (mục 4), review/merge PR của các thành viên.
- [ ] Cuối buổi: gom mục 5 Khó khăn trong `group_report.md`.
- [ ] Chốt bài: pull `main`, chạy `pytest` (0 failed), `pytest tests/test_tool_contract.py` xanh; kiểm tra `runs/`, `transcripts/` không chứa key/token; `.env` không bị commit.
- [ ] Ghi URL repo, nhánh nộp, **commit chốt** vào `TEAM.md`; nhắc cả nhóm nộp link repo trên LMS.

**CP5 — Phần A + UI trước 16:30**
- [ ] Viết UI Streamlit `starter_v0/app.py` gọi agent (dùng lại `agent.py` / logic của `chat.py`); UI phải hiện lỗi tool, không che lỗi.
- [ ] Thêm dependency (`streamlit`, …) vào `requirements.txt`.
- [ ] Chạy `streamlit run app.py`, mở link public: `cloudflared tunnel --url http://localhost:8501`. Giữ tunnel chạy suốt showdown.
- [ ] Điền **Phần A** trong `group_report.md`: mục 1, A1 (mô tả + lệnh chạy UI + URL), A2 (bảng tool, hỏi Nhân phần tool mới), A3 (3–5 câu hỏi mẫu).
- [ ] (Khuyến khích) `report/team/poster.html` cùng nội dung Phần A.

**Live chat — sau khi Nguyên merge v3**
- [ ] Pull `main`, chạy `python chat.py --provider openrouter --version v3`, tối thiểu 3 kịch bản:
  1. Yêu cầu research bình thường.
  2. Yêu cầu thiếu thông tin (không nói account/URL) → lượt sau bổ sung.
  3. Yêu cầu "gửi/đăng bản tin lên Telegram" → agent phải hỏi xác nhận trước.
- [ ] Nếu agent hành xử sai ở kịch bản 3: **báo Nguyên sửa prompt**, không tự sửa `system_prompt.md`.
- [ ] Commit `transcripts/*.transcript.json` (kiểm tra không có token).

**Báo cáo**
- [ ] **B4** (live chat), **B5a** dòng "UI".
- [ ] Báo cáo cá nhân + mục của mình trong `TEAM.md`.

**Bonus:** tạo bot Telegram + private channel của nhóm, điền `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` trong `.env` (không commit). Transcript phải cho thấy: agent hỏi lại → user xác nhận → `send(confirmed=true)` → `status: sent`. Điền dòng Telegram trong B5.

---

## 4. Thứ tự merge

```text
⓪ Sỹ     : TEAM.md skeleton                                        → main
① Nguyên  : run v0 + version_log v0                                 → main
② Nhân    : tool mới (folder + __init__.py + block yaml cuối + test) → main  (TRƯỚC v2)
③ Nguyên  : pull main → v1, v2, v3                                  → main
④ Hiếu    : eval_group.json (viết song song) → chạy run group trên v3 → main
⑤ Sỹ      : UI + Phần A (song song, trước 16:30) → chat.py trên v3 → transcript → main
⑥ Cả nhóm : báo cáo cá nhân, mục TEAM.md, các mục Phần B của mình   → main
⑦ Sỹ      : pytest 0 failed, kiểm tra secret, ghi commit chốt trong TEAM.md
```

## 5. Quy tắc chung

1. Mỗi người làm trên **branch riêng**, `git pull origin main` trước khi bắt đầu và trước khi mở PR. Không force-push.
2. Chỉ sửa file/vùng mình là chủ (bảng mục 1, 2). Cần đổi file người khác → nhắn chủ file.
3. Chỉ **Nguyên** chạy `run_eval.py --suite base` và ghi `version_log.csv`.
4. Sau mỗi lần merge: `pytest tests/test_tool_contract.py` phải xanh.
5. Không commit `.env`, API key, token Telegram, `.venv`, `arxiv_papers/`.
6. Chỉ dùng run hợp lệ (`provider_error_cases == 0`, `measured_cases == total_cases`) làm bằng chứng.
7. Mỗi người phải có **commit kỹ thuật** của chính mình (C8) và tự giải thích được phần mình làm; ghi công cụ AI đã dùng trong báo cáo cá nhân.
