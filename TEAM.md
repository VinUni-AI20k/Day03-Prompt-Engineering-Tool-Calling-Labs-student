# Team

## Thông tin nhóm

- Tên nhóm: Ban5
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-Ban5-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/haiquanng/K5-L3B-DAY03-Ban5-ResearchAgentToolEval, nhánh `main`, commit chốt: (điền khi nộp)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Văn Hải Quân | 2A202603994 | 26ai.quannvh@vinuni.edu.vn | haiquanng | Developer |
|   2 | Lại Trọng Đức | 2A202604019 | 26ai.duclt2@vinuni.edu.vn | laitrongduc | Developer |
|   3 | Nguyễn Bảo Trung | 2A202604013 | nbtrungrhm@gmail.com | trungnb | Developer |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/2A202604013_NguyenBaoTrung.md`.

Sao chép mục dưới đây cho từng thành viên.

## Lại Trọng Đức - 2A202604019

### Phần việc phụ trách

- Unit test cho tool có sẵn, phát triển tool mới `stats` và kiểm tra contract giữa khai báo với code.
- Tối ưu mô tả tool và quy ước tham số trong `tools.yaml` cho v3; phân tích lỗi, chạy eval và lưu bằng chứng đo lường.
- Viết tài liệu phương pháp trong changelog và báo cáo cá nhân.

### Đóng góp cụ thể

- Hoàn thành 17 hàm test: 14 cho tool có sẵn và 3 cho `stats`, mở rộng thành 37 trường hợp bằng parametrization. Test chạy offline với HTTP/key giả; toàn suite đạt **104 passed, 0 failed, 0 skipped**, bao gồm contract test.
- Viết tool local `stats` tính mean, median, độ lệch chuẩn mẫu; bổ sung `TOOL.md`, đăng ký trong `tools/__init__.py` và `artifacts/tools.yaml`; kiểm tra dữ liệu không hợp lệ và nhánh lỗi trả error dict.
- Viết lại description và quy ước tham số của 11 tool, giữ nguyên prompt v2, code, schema, bộ eval và model `gpt-4o-mini`. Làm rõ `clarify` dùng `yes_no` để xác nhận ý định gửi trước khi hỏi nội dung; `social_search` không được gọi khi người dùng đã bỏ Twitter.
- Phân tích R12/M06 từ tool call thực tế. Base eval v3 từ lần đầu 19/20 lên **20/20** sau khi làm rõ thứ tự ưu tiên và ví dụ trong description của `clarify`; đo đủ 20 case, 0 lỗi provider. R12/M06 đều PASS, không làm hỏng các case từng PASS ở v1/v2. Kết quả v2 dùng làm mốc là 18/20, do QuanNH thực hiện.
- Xuất `analysis/v3.csv`, cập nhật dòng v3 trong `version_log.csv` và mục v3 trong `CHANGED_LOGS.md`; giữ run đầu và run cuối để truy vết. Viết báo cáo cá nhân, ghi rõ hỗ trợ từ Codex và cách kiểm chứng.
- Đã push các commit dưới đây lên `feat/DucLT-tool-tests`. Chưa có bằng chứng xác nhận PR/merge; chưa có eval nhóm/chat riêng chứng minh routing tới `stats`, chưa hoàn thành bảng tổng hợp riêng v0–v3 theo loại lỗi.

### Bằng chứng

- Test: [test_tools_todo.py](starter_v0/tests/test_tools_todo.py), [log pytest](starter_v0/analysis/duclt_pytest.txt).
- Tool mới: [stats/tool.py](starter_v0/tools/stats/tool.py), [stats/TOOL.md](starter_v0/tools/stats/TOOL.md), [registry](starter_v0/tools/__init__.py), [tools.yaml](starter_v0/artifacts/tools.yaml).
- Eval v3: [run đầu 19/20](starter_v0/runs/v3_B_base_openai_20261110T182541886906.json), [run cuối 20/20](starter_v0/runs/v3_B_base_openai_20261110T183553607506.json), [bảng từng case](starter_v0/analysis/v3.csv), [version log](starter_v0/artifacts/version_log.csv).
- Tài liệu: [phương pháp v3 trong changelog](CHANGED_LOGS.md), [báo cáo cá nhân](report/team/2A202604019_LaiTrongDuc.md).
- Commit: [fefb019 — test và stats](https://github.com/haiquanng/K5-L3B-DAY03-Ban5-ResearchAgentToolEval/commit/fefb019), [0d4b517 — v3 và bằng chứng eval](https://github.com/haiquanng/K5-L3B-DAY03-Ban5-ResearchAgentToolEval/commit/0d4b517), [bef3bb9 — báo cáo cá nhân](https://github.com/haiquanng/K5-L3B-DAY03-Ban5-ResearchAgentToolEval/commit/bef3bb9).

## Nguyễn Bảo Trung - 2A202604013

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
