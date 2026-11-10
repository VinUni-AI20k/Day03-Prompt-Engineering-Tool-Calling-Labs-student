# Báo cáo cá nhân — Nguyễn Thiên Bảo — 2A202603861

## 1. Thông tin thành viên

- Họ tên: Nguyễn Thiên Bảo
- MSSV: 2A202603861
- Email: 26ai.baont5@vinuni.edu.vn
- GitHub: [Limdim1604](https://github.com/Limdim1604)
- Nhánh làm việc: `nguyenthienbao` (thử nghiệm độc lập từ starter) và `nguyenthienbao-main` (phần đưa lên `main`)

## 2. Phần việc phụ trách

- Tool mới thứ hai của nhóm: `hn_search` và unit test.
- Test challenge: điền 14 unit test TODO của các tool có sẵn.
- Vòng tối ưu nối tiếp `v7` của nhóm: đo lại trên provider `openai`, tích hợp tool mới và sửa lỗi M06 (`v8`–`v10`).

## 3. Đóng góp cụ thể

**Tool `hn_search` (CP3).** Tool tìm story trên Hacker News qua API công khai `hn.algolia.com`, không cần API key, nên cả nhóm chạy được mà không phải đăng ký thêm. Có 3 tham số `query`, `sort` (`relevance`/`date`), `limit` (1–20). Tool tự chuẩn hóa input xấu mà model hay gửi: `limit` sai kiểu thì về 5, ngoài khoảng thì kẹp lại, `sort` ngoài enum thì dùng `relevance`. Query rỗng, lỗi HTTP và timeout đều trả error dict, không raise. Có 6 unit test chạy offline, assert cả request gửi đi lẫn kết quả trả về. Tool được đăng ký trong `tools/__init__.py`, `tools.yaml` và có 1 dòng routing trong prompt. Bộ case riêng `eval_new_tool_hn_search.json` (3 case, chạy `--suite extension`) không động vào 10 case nhóm của Duy. [Tool](../../starter_v0/tools/hn_search/tool.py) · [TOOL.md](../../starter_v0/tools/hn_search/TOOL.md)

**Test challenge (bonus).** Thay 14 stub `pytest.skip(TODO)` bằng test thật cho clarify, format, send, lookup, fetch, timeline, social_search và policy. Trong đó có guardrail của `send`: có env thì đúng 1 POST với `chat_id` và `text`; không có env thì trả error dict và không gửi request. Test của `policy` kiểm tra trust boundary: dòng chứa chỉ dẫn nhúng trong file policy phải nằm ở `untrusted_text`, không lọt vào `facts`. Kết quả `pytest` từ 70 passed / 14 skipped lên **95 passed / 0 skipped / 0 failed**. [Test](../../starter_v0/tests/test_tools_todo.py)

**Vòng tối ưu v8–v10 (CP2).**

| Version | Thay đổi | Kết quả |
|---|---|---|
| `v7-openai-recheck` | Đo lại trạng thái `main` bằng `openai` | 20/20; M06 pass, trong khi trên openrouter M06 fail → case nhiều lượt dao động |
| `v8` | Thêm `hn_search` vào `tools.yaml` + 1 dòng routing | group 10/10, hn 3/3, base 19/20 (M06 fail lại) |
| `v9` | Rule "nguồn đã bỏ thì bỏ luôn" + ví dụ 3 lượt | base 20/20, group 10/10, nhưng N03 gọi thừa `lookup` |
| `v10` | Khi đổi nguồn chỉ gọi tool của nguồn mới | **base 20/20 (2 lần), group 10/10, hn 3/3** |

Mỗi vòng có đủ hash, giả thuyết và metric trước/sau trong [`version_log.csv`](../../starter_v0/artifacts/version_log.csv). Tôi cũng thêm bảng B1/B2 cho các vòng này và transcript live `v10` vào [báo cáo nhóm](group_report.md).

**Thử nghiệm độc lập trên nhánh `nguyenthienbao`.** Trước khi ghép vào `main`, tôi làm trọn lab từ starter gốc với `openai`: v0 0.65 → v8 1.00 (8 vòng), tool `hn_search`, 10 case eval riêng, UI Streamlit và transcript 6 lượt. Kết luận từ nhánh này được dùng lại ở `main`: với `gpt-4o-mini`, rule routing đặt trong system prompt hiệu quả hơn viết trong tool description, và khai báo `required` trong schema chặn được lỗi bỏ sót tham số.

## 4. Bằng chứng

- Commit trên nhánh `nguyenthienbao-main`:

| Commit | Nội dung |
|---|---|
| `90f1b1b` | 14 unit test TODO (0 skipped) |
| `116965e` | Tool `hn_search` + 6 unit test + đăng ký |
| `5f61ac7` | `v7-openai-recheck` + `v8` (tích hợp `hn_search`) |
| `c353b4d` | `v9` (sửa M06) |
| `fdd16e2` | `v10` (đổi nguồn chỉ gọi tool mới) |
| `00334ec` | Transcript live `v10` |
| `0a5e5c1` | Bổ sung báo cáo nhóm |

  (Hash có thể đổi sau khi rebase lên `main`; tra theo commit message.)
- Run: `starter_v0/runs/v7-openai-recheck_*.json`, `v8_*`, `v9_*`, `v10_*` (base, group, extension). Mọi run đều có `provider_error_cases = 0` và `measured_cases = total_cases`.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: tôi dùng Claude Code (Claude) để đọc đề và starter, phân tích run JSON, viết code tool, unit test, prompt và soạn báo cáo. Cách tôi tự kiểm tra:
  - Mỗi vòng đều chạy eval thật bằng API và đọc `actual_tool_calls` của từng case fail trước khi đặt giả thuyết tiếp theo.
  - Chạy `pytest` sau mỗi thay đổi tool/test, và smoke test `hn_search` với API thật.
  - Đối chiếu `prompt_hash`/`tools_hash` trong `version_log.csv` với run JSON. Khi hash lệch do kiểu xuống dòng CRLF/LF, tôi dựng lại đúng file rồi mới commit.
  - Kiểm tra `runs/` và `transcripts/` không chứa API key trước khi commit.

## 5. Tự đánh giá

Phần tôi làm tốt nhất là giữ vòng lặp giả thuyết → sửa → đo một cách trung thực. Các vòng làm giảm điểm (v2, v4 ở nhánh riêng; v8, v9 ở `main`) đều được ghi lại cùng nguyên nhân, thay vì chỉ giữ vòng đẹp. Bài học rõ nhất là ở `v9`: một ví dụ few-shot sửa được M06 nhưng làm hỏng N03, vì model khái quát ví dụ "chuyển sang web" thành "luôn thêm web". Nhờ có bộ case riêng cho tool mới nên regression này lộ ra ngay.

Hạn chế: kết quả của case nhiều lượt dao động giữa các lần chạy (M06 lúc pass lúc fail với cùng prompt). Hai lần chạy 20/20 ở `v10` chưa phải bằng chứng thống kê mạnh. Transcript cũng cho thấy agent đôi khi trả lời tiếng Anh cho câu hỏi tiếng Việt, và eval hiện tại không chấm điểm này. Nếu có thêm thời gian, tôi sẽ chạy lặp nhiều lần để đo độ ổn định, thêm rule và case kiểm tra ngôn ngữ trả lời, và làm bonus gửi Telegram thật.
