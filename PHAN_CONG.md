# Phân công nhóm — Day 03 Research Agent Tool Eval

Nhóm: **DNH** · Lớp: **L3B** · Repo: `K5-L3B-DAY03-NhomDNH-ResearchAgentToolEval`

| Thành viên | Vai trò | Track chính | Điểm chính “sở hữu” | Bắt đầu |
|---|---|---|---:|---|
| **Nghị** | Prompt & tối ưu eval | Setup + baseline + prompt/`tools.yaml` + v0→v3 | ~45 (C1–C3) | Ngay |
| **Đạt** | Tool & test | Tool mới + unit test + khung UI | ~25 (C4 + nền C6) | Ngay |
| **Hà** | Eval nhóm & báo cáo | 10 case eval + live chat + báo cáo + hoàn thiện UI | ~30 (C5–C7) | Sau ~1 giờ |

Mỗi người vẫn tự viết `report/team/MSSV_HoTen.md` và có **≥ 1 commit kỹ thuật** (C8).

---

## Bản chất bài (nhắc nhanh)

Build research agent gọi tool thật → tối ưu bằng vòng lặp **chạy eval → đọc run JSON → sửa prompt/`tools.yaml` → đo lại**. Điểm dựa trên bằng chứng (run, version log, test, transcript, báo cáo).

| Tiêu chí | Điểm |
|---|---:|
| C1 Baseline v0 + phân tích lỗi | 10 |
| C2 Prompt & tool declaration | 15 |
| C3 Vòng lặp v1→v3 | 20 |
| C4 Tool mới + unit test | 15 |
| C5 10 case eval nhóm | 10 |
| C6 UI + live chat | 10 |
| C7 Báo cáo nhóm | 10 |
| C8 Đóng góp cá nhân | 10 |

**Rủi ro merge:** `system_prompt.md`, `tools.yaml`, `version_log.csv` chỉ **Nghị** sửa chính.

---

## Nghị — Prompt & tối ưu (làm ngay)

1. Điền `TEAM.md` (tên nhóm, 3 thành viên, phân công theo bảng trên).
2. Setup chung: `.env`, `preflight_provider.py`, `pytest` xanh (contract + examples).
3. Chạy **baseline v0** (chưa sửa prompt/tools), ghi `artifacts/version_log.csv`.
4. Phân loại từng case FAIL → bảng **B2** trong `report/team/group_report.md`.
5. Sửa `artifacts/system_prompt.md` + `artifacts/tools.yaml`:
   - bỏ chỉ dẫn xấu starter (đoán, gửi không hỏi, một bước);
   - thêm routing + convention args + boundary `send`.
6. Chạy **v1 → v2 → v3**, mỗi version **một** giả thuyết, ghi metric trước/sau.
7. Khi Đạt xong tool: **merge mô tả tool mới vào `tools.yaml`** (Nghị chốt file này).

**Không làm:** viết tool mới, viết 10 case eval (tránh đụng file với Hà).

---

## Đạt — Tool mới + test + khung UI (làm ngay, song song Nghị)

1. Chốt 1 tool mới (gợi ý dễ đạt điểm):
   - `summarize_items` — tóm tắt list item thành bullet ngắn, hoặc
   - `compare_sources` — so 2 URL/source đã fetch, hoặc
   - `datetime_window` — chuẩn hóa timeframe trước khi gọi `lookup`/`timeline`.
2. Tạo `tools/<tên>/tool.py` + `TOOL.md`, đăng ký trong `tools/__init__.py`.
3. Viết **≥ 3 test** trong `tests/test_tools_todo.py` (happy path / input xấu / error dict, không raise).
4. Nhắn Nghị: tên tool + params + “khi nào dùng” để đưa vào `tools.yaml` + prompt.
5. Scaffold UI Streamlit (`app.py` hoặc tương đương) + thêm dependency vào `requirements.txt` — chưa cần đẹp, chỉ chat được với agent.
6. Draft sẵn 2–3 dòng mô tả tool cho Phần A (mục A2).

**Không làm:** sửa sâu `system_prompt.md` / chạy chuỗi v1–v3 (để Nghị giữ bằng chứng sạch).

---

## Hà — Eval + demo + báo cáo (vào sau ~1 giờ)

Khi vào, nhận bàn giao từ Nghị + Đạt, rồi:

1. Viết đúng **10 case** `data/eval_group.json` (5 single + 5 multi), ≥ 1 case route tới tool mới của Đạt.
2. Chạy `--suite group`, lưu run.
3. Hoàn thiện UI + mở link dùng thử (Cloudflare Tunnel / Streamlit Cloud) → ghi mục A1.
4. Chạy `chat.py` ≥ 3 lượt: research thường · thiếu info rồi bổ sung · gửi/đăng Telegram (có hỏi xác nhận).
5. Lắp `report/team/group_report.md`:
   - **Phần A** ưu tiên nếu còn gần showdown 16:30;
   - **Phần B** (B1–B5) từ run / version_log / transcript có sẵn.
6. Nhắc cả nhóm viết báo cáo cá nhân; rà checklist `SUBMISSION.md`.

Nếu Nghị chưa xong v3 khi Hà vào: Hà **không tranh** prompt — làm eval / UI / report trước, v3 để Nghị chốt.

---

## Timeline

```text
Phút 0–20    Nghị + Đạt: setup .env chung, TEAM.md, preflight, pytest
Phút 20–45   Nghị: v0 + phân loại lỗi | Đạt: code tool + 3 test
Phút 45–75   Nghị: v1 | Đạt: đăng ký tool + khung UI
~Phút 60+    Hà vào → nhận handoff
Phút 75–120  Nghị: v2 | Hà: 10 eval case + chạy group | Đạt: chốt test xanh
Phút 120+    Nghị: v3 | Hà: live chat + Phần A/B + link UI | Đạt hỗ trợ bug tool/UI
Cuối buổi   Cả 3: MSSV_*.md + push + nộp LMS
```

---

## Handoff cho Hà (Nghị + Đạt chuẩn bị 1 message)

1. Provider/model đang dùng + `.env` đã đủ key nào.
2. Metric v0 (và v1 nếu có) + 3–5 lỗi FAIL chính.
3. Tên tool mới + signature + ví dụ args.
4. Lệnh chạy UI hiện tại.
5. Branch đang làm; file **đừng đụng:** `system_prompt.md`, `tools.yaml`, `version_log.csv` (chỉ Nghị).

---

## Owner theo file (tránh conflict)

| File | Owner |
|---|---|
| `artifacts/system_prompt.md`, `tools.yaml`, `version_log.csv`, chạy base v0–v3 | **Nghị** |
| `tools/<mới>/`, `tools/__init__.py`, `tests/test_tools_todo.py` | **Đạt** |
| `data/eval_group.json`, `transcripts/`, `group_report.md`, polish UI + link | **Hà** |
| `TEAM.md` | Nghị khởi tạo, cả nhóm bổ sung |
| `report/team/MSSV_HoTen.md` | Mỗi người tự viết |

---

## Bonus (chỉ khi phần bắt buộc đã xanh)

Ưu tiên nhanh: Telegram `send` thật (2đ) hoặc `pytest` 0 skipped (1đ). Small Local Model (4đ) làm sau nếu còn máy/thời gian.
