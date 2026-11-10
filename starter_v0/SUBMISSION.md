# NoName Research Agent — chạy và kiểm tra

## Cài đặt

Từ thư mục `starter_v0/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Điền key riêng vào .env, tuyệt đối không commit hoặc nộp file này.
python scripts/preflight_provider.py --provider openrouter
```

Model đã chọn: `nvidia/nemotron-3-ultra-550b-a55b:free` qua OpenRouter.
Có thể bị giới hạn lượt gọi; không có bảo đảm về tốc độ/khả dụng.
`requirements.lock.txt` ghi môi trường đã kiểm tra; `requirements.txt` là danh sách dependency trực tiếp.

## UI

```bash
python -m streamlit run app.py
```

Mở http://localhost:8501. Có lịch sử chat, trạng thái đang xử lý, kết quả tra cứu,
hỏi lại khi thiếu thông tin, tải và lưu transcript. UI chỉ nghiên cứu, không cung cấp
hành động gửi Telegram; CLI vẫn khai báo `send` và yêu cầu xác nhận.

Link demo hiện tại nằm trong `artifacts/REPORT.md`. Link Cloudflare tạm thời chỉ hoạt
động khi máy và hai tiến trình Streamlit/cloudflared còn chạy. Khi cần tạo link mới:

```bash
cloudflared tunnel --url http://localhost:8501
```

Cập nhật URL trong báo cáo trước buổi demo nếu đã khởi động lại tunnel.

## Kiểm tra và tái hiện

```bash
pytest -q
python run_eval.py --provider openrouter --version v3 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
python chat.py --provider openrouter --version v3
```

Bản nộp giữ các run gốc v0–v2 và snapshot khớp SHA256, không đổi nhãn run cũ.
Ví dụ tái hiện một phiên bản:

```bash
python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json --system-prompt artifacts/versions/v1/system_prompt.md --tools artifacts/versions/v1/tools.yaml
```

Các snapshot v0–v2 có chỉ dẫn chưa hoàn thiện của starter, chỉ dùng phân tích/tái hiện;
không dùng chúng cho gửi tin thật. Base eval đo routing/arguments của một lượt model,
không đo đầy đủ chất lượng bản tin hoặc toàn bộ cuộc hội thoại.

## Gói nộp

Đọc `artifacts/REPORT.md`, `artifacts/version_log.csv`, `artifacts/pytest_results.txt`,
`runs/`, `transcripts/`. Tool mới: `tools/deduplicate/`; 10 case nhóm: 5 single-turn,
5 multi-turn. Báo cáo ghi rõ giới hạn và các case chưa đạt.

```bash
python scripts/package_submission.py
```

Gói `NoName_Lab_Submission.zip` ở thư mục cha có manifest SHA256, loại `.env`, venv,
cache và secrets.toml. Không bao gồm thư mục `.lab_archive` ngoài starter_v0.
Báo cáo đã có tên và mã học viên của 3 thành viên nhóm.
