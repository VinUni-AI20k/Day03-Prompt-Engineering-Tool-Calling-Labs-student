# Báo cáo cá nhân — Hồ Trọng Nghĩa (2A202603729)

## 1. Thông tin thành viên

- Họ tên: Hồ Trọng Nghĩa
- MSSV: 2A202603729
- Email: 26ai.nghiaht@vinuni.edu.vn

## 2. Phần việc phụ trách

- Nhóm trưởng; tích hợp các tool mới vào registry và khai báo chung.
- Tự xây tool `source_audit` và viết ít nhất 3 unit test.
- Chạy bonus model local với ít nhất hai model; ghi các vòng tối ưu và bằng chứng vào B7.

## 3. Đóng góp cụ thể

- Tạo nhánh làm việc cá nhân `feature/nghia-source-audit-local-bonus` từ `main`.
- Tạo môi trường Python 3.11.9 trong `starter_v0/.venv` và cài các dependency trong `requirements.txt`.
- Xây tool local `source_audit`, đăng ký vào tool registry và khai báo schema để kiểm tra title/URL HTTP(S) của nguồn.
- Viết 3 unit test cho citation hợp lệ, metadata lỗi và input sai kiểu.
- Cài Ollama `0.40.16` tại `D:\Apps\Ollama`, chuyển kho model sang `D:\AIModels\TeLietOllama` và tải `qwen2.5:3b`.
- Chạy thử preflight tool-calling cho `qwen2.5:3b`, nhưng Ollama dừng vì lỗi CUDA `device kernel image is invalid`; chưa có model eval hợp lệ, chưa có vòng tối ưu local.

## 4. Bằng chứng

- Nhánh làm việc: `feature/nghia-source-audit-local-bonus`.
- Setup: `.venv` dùng Python 3.11.9; cài dependency bằng `uv pip install --python .venv\Scripts\python.exe -r requirements.txt`.
- Kiểm tra setup: import thành công `requests`, `yaml`, `pypdf`, `pytest`, `openai`, `anthropic`, `google.genai`.
- Tool và schema: `starter_v0/tools/source_audit/`, `starter_v0/tools/__init__.py`, `starter_v0/artifacts/tools.yaml`.
- Unit test: từ `starter_v0/`, `.venv\Scripts\python.exe -m pytest tests/test_tools_todo.py -k source_audit -q` — 3 passed; `.venv\Scripts\python.exe -m pytest tests/test_tool_contract.py -q` — 60 passed.
- Ollama preflight: `python scripts/preflight_provider.py --provider ollama --model qwen2.5:3b` dừng với lỗi CUDA; driver NVIDIA hiện tại đọc được là `546.30`. Lỗi này không được tính là benchmark. Chưa chạy toàn bộ pytest hoặc model eval.
- AI/công cụ: Codex hỗ trợ setup và code; tự kiểm tra bằng import, targeted pytest và contract test.

## 5. Tự đánh giá

Tool `source_audit` và 3 unit test đã hoàn tất, contract test xanh. Bonus model local còn dang dở vì preflight lỗi CUDA; cần xác nhận model chạy được rồi mới thu thập benchmark và tối ưu.
