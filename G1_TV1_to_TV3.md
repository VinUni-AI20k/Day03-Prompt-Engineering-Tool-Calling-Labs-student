# G1 — Bàn giao từ TV1 cho TV3

**Dự án:** K5-L3B-DAY03 — Research Agent Tool Evaluation  
**Nhóm:** FcLomDom | **Lớp:** L3B  
**Người bàn giao:** TV1 — Triệu Hải Đăng Trình (2A202603874), GitHub `DangTrinhdzZz`  
**Người nhận:** TV3 — MSSV 2A202603898, GitHub `MinhNGD76`  
**Repository:** https://github.com/DangTrinhdzZz/K5-L3B-DAY03-FcLomDom-ResearchAgentToolEval  
**Nhánh TV1:** `trinh` | **Nhánh TV3:** `minhnd`  
**Ngày lập:** 10/11/2026  
**Trạng thái:** Bản bàn giao ban đầu; các kết quả kiểm thử tại máy local chưa được cung cấp và phải bổ sung trước khi xác nhận hoàn tất G1.

## 1. Phạm vi bàn giao

G1 gồm: (G1.1) thông tin nhóm; (G1.2) môi trường Python và OpenAI provider; (G1.3) chạy kiểm thử; (G1.4) kiểm tra tính toàn vẹn cấu hình và dữ liệu; (G1.5) tài liệu bàn giao này. G1 không bao gồm tối ưu prompt, thay đổi tool contracts, chỉnh sửa baseline hoặc triển khai các nhiệm vụ riêng của thành viên khác.

## 2. Danh mục file và trách nhiệm

| Đường dẫn | Vai trò | Trạng thái / hành động |
| --- | --- | --- |
| `TEAM.md` | Thông tin nhóm và phân công | Đã soạn bản cập nhật; cần xác nhận đã thay vào repository và commit; còn thiếu tên đầy đủ TV2–TV4. |
| `docs/handoffs/G1_TV1_to_TV3.md` | Biên bản bàn giao | File này; cần commit lên nhánh `trinh`. |
| `starter_v0/env_loader.py` | Đọc biến môi trường | Đã quan sát có trong repository ở nhánh `trinh`; cần kiểm tra thực thi local. |
| `starter_v0/providers/openai_provider.py` | OpenAI provider | Đã quan sát có trong repository; sử dụng `OPENAI_API_KEY`; chưa xác nhận preflight PASS. |
| `starter_v0/providers/__init__.py` | Factory/registry provider | Đã quan sát có hỗ trợ `openai`; cần kiểm tra import local. |
| File `requirements.txt` thực tế | Khai báo dependencies | Chưa xác nhận vị trí; tìm trong repository trước khi cài. |
| `scripts/preflight_provider.py` (nếu tồn tại) | Kiểm tra kết nối provider | Cần xác nhận đường dẫn và chạy đúng cú pháp từ repo. |
| `starter_v0/artifacts/tools.yaml` | Tool declarations | Đã quan sát tồn tại; giữ nguyên trong G1. |
| `starter_v0/data/eval_base.json` | Baseline evaluation data | Đã quan sát tồn tại; **không chỉnh sửa**. |
| `starter_v0/data/eval_research_extension.json` | Research extension evaluation data | Đã quan sát tồn tại; giữ nguyên trong G1. |
| `starter_v0/tests/` | Bộ kiểm thử | Có các test TODO/skip; cần chạy và báo cáo số lượng PASS/FAIL/SKIP. |
| System prompt (đường dẫn thực tế) | Prompt hệ thống | Cần xác định vị trí, kiểm tra hiện diện và giữ nguyên trong G1. |

> Không cần nhân bản các file cấu hình/mã nguồn vào `docs/handoffs/`. Bàn giao thông qua Git và dẫn đường dẫn chính xác trong tài liệu này.

## 3. Kết quả kiểm tra và bằng chứng

| Hạng mục | Kết quả hiện tại | Bằng chứng cần bổ sung |
| --- | --- | --- |
| Git branch và remote | Nhánh `trinh` có trên GitHub | `git branch --show-current`, `git remote -v`, `git status --short` ở local |
| Python | **Chưa kiểm tra local** | `python --version` |
| Dependencies | **Chưa kiểm tra local** | Vị trí file requirements, kết quả cài đặt/import |
| OpenAI provider | **Có mã nguồn; chưa xác nhận chạy thành công** | Preflight, model sử dụng, lỗi nếu có (không ghi key) |
| Pytest | **Chưa chạy/không có log** | Lệnh chạy và tổng `passed / failed / skipped / errors` |
| Tool contracts | **Chưa xác nhận PASS** | Kết quả kiểm thử liên quan |
| Integrity | **Kiểm tra sơ bộ một số file** | Đường dẫn thực tế, diff và các thiếu sót |

Không được diễn giải “file tồn tại” thành “đã kiểm thử thành công”. Các test `skip` do TODO không được tính là `pass`.

## 4. Lệnh kiểm tra đề xuất (PowerShell)

Chạy tại thư mục gốc repository, trên nhánh `trinh`. Không chạy đánh giá tốn API ngoài phạm vi G1.

```powershell
git branch --show-current
git remote -v
git status --short
python --version
Get-ChildItem -Recurse -Filter requirements.txt | Select-Object -ExpandProperty FullName
Get-ChildItem -Recurse -Filter system_prompt.md | Select-Object -ExpandProperty FullName
Get-ChildItem -Recurse -Filter preflight_provider.py | Select-Object -ExpandProperty FullName
Get-ChildItem -Recurse -Filter 'test_*.py' | Select-Object -ExpandProperty FullName
```

Sau khi xác định đúng thư mục chứa test và dependencies, cài đặt dependencies vào virtual environment và chạy `python -m pytest` theo hướng dẫn thực tế của repo. Nếu script preflight có mặt và đã thiết lập key an toàn, chạy:

```powershell
python scripts/preflight_provider.py --provider openai
```

Lệnh preflight trên chỉ áp dụng nếu script nằm ở `scripts/preflight_provider.py` tính từ thư mục đang đứng; cần điều chỉnh theo đường dẫn thực tế. Không in hoặc commit API key.

## 5. Những việc còn mở trước khi TV3 nhận bàn giao chính thức

1. Xác nhận `TEAM.md` trong repo và bổ sung họ tên chính xác TV2, TV3, TV4.
2. Xác định vị trí file dependencies, system prompt và preflight; sửa lại bảng đường dẫn nếu khác thực tế.
3. Chạy cài đặt/import, OpenAI preflight (nếu có quyền sử dụng API), pytest và tool contract tests; ghi log tóm tắt vào Mục 3.
4. Ghi rõ lỗi, skipped tests, giới hạn môi trường và thay đổi G1 đã thực hiện; không tự ý nhận các test TODO của thành viên khác.
5. Commit/push các file G1 lên `origin/trinh`; TV3 chỉ tích hợp sau khi nhóm thống nhất cách đồng bộ branch.

## 6. Hướng dẫn cho TV3

- Đọc `TEAM.md`, tài liệu này, cấu hình provider và bộ test trước khi bắt đầu phần việc được giao.
- Sử dụng `OPENAI_API_KEY` từ môi trường riêng, không đưa key vào Git; không tự động chuyển sang OpenRouter.
- Giữ nguyên `eval_base.json` và các file benchmark gốc.
- Báo lỗi có thể tái hiện bằng lệnh chạy, traceback đã ẩn secrets và commit hash; không coi các mục chưa kiểm tra là PASS.
- Làm việc trên branch `minhnd`; không push trực tiếp `main` hoặc sửa branch `trinh` khi chưa thống nhất.

## 7. Xác nhận bàn giao

- **TV1:** Chưa xác nhận hoàn tất G1 do thiếu bằng chứng chạy local.
- **TV3:** Chưa xác nhận tiếp nhận.
- **Commit bàn giao:** _Điền commit hash sau khi push._
