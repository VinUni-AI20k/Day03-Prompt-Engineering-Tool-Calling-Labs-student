# Team

## Thông tin nhóm

- Tên nhóm: Corner
- Lớp: L3B
- Repo nhóm: [K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling) (tên repo theo yêu cầu của giảng viên)
- Nhánh nộp: `main` · Commit chốt: (điền sau khi merge xong)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Hoàng Gia An | 2A202603799 | 26ai.annhg@vinuni.edu.vn | https://github.com/AnK17-UIT | Trưởng nhóm, viết và tổng hợp báo cáo, tích hợp tool và kiểm chứng eval |
|   2 | Hà Lê Duy | 2A202603851 | 26ai.duyhl@vinuni.edu.vn | https://github.com/duyhale95 | Kiểm chứng eval, duyệt prompt, tool và demo Streamlit |
|   3 | Nguyễn Thiên Bảo | 2A202603861 | 26ai.baont5@vinuni.edu.vn | https://github.com/Limdim1604 | Tool `hn_search`, test challenge, tối ưu prompt v8–v10 |
|   4 | Nguyễn Đức Nhật | 2A202603812 | 26ai.nhatnd@vinuni.edu.vn | https://github.com/NguyenDucNhat3006 | Chạy baseline, phân tích log và nắm chính cải tiến system prompt |


## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

## Nguyễn Hoàng Gia An - 2A202603799

### Phần việc phụ trách

- Trưởng nhóm, viết và tổng hợp báo cáo nhóm.
- Tích hợp `dedupe_sources`, kiểm chứng eval nhóm và đồng bộ bằng chứng kết quả.

### Đóng góp cụ thể

- Tối ưu `tools.yaml` ở v2–v3 (base eval 0.95 → 1.00), nối tiếp v0–v1 của Nhật trên nhánh `NguyenHoangGiaAn`.
- Với hỗ trợ Codex, sửa import tool mới và bỏ khai báo tool chưa có implementation.
- Bổ sung 4 unit test; kiểm tra bộ eval nhóm đủ 5 single turn + 5 multi turn.
- Chạy eval thật đạt 10/10 PASS; sửa hash và đường dẫn version log theo run JSON.

### Bằng chứng

- [Báo cáo cá nhân](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/7d387d0/report/team/2A202603799_NguyenHoangGiaAn.md).
- [v2 tools.yaml](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/403bf26), [v3](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/6f49b26).
- [Run group](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/7d387d0/starter_v0/runs/v3-group_B_group_openai_20261110T213547741621.json).
- [Kiểm chứng](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/blob/7d387d0/starter_v0/analysis/verification.md): pytest 71 passed, 14 skipped; các skip thuộc challenge của tool có sẵn.

## Hà Lê Duy — 2A202603851

### Phần việc phụ trách

- Kiểm chứng các vòng đánh giá, duyệt thay đổi prompt và mô tả công cụ, kiểm tra tool mới và thử giao diện Streamlit trên nhánh `haleduy`.

### Đóng góp cụ thể

- Đối chiếu baseline và các vòng v1–v7. Ở v7, kết quả đạt 19/20 và còn lỗi M06 khi agent tiếp tục gọi nguồn X sau khi người dùng chuyển sang web.
- Chuẩn hóa thông tin tác giả trong version log và kiểm tra `dedupe_sources` cùng ba unit test.
- Duyệt bộ eval nhóm gồm 5 ca một lượt và 5 ca nhiều lượt, đối chiếu kết quả 10/10, thử UI và kiểm tra transcript.

### Bằng chứng

- [Báo cáo cá nhân](report/team/2A202603851_HaLeDuy.md).
- [Prompt và run v7](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/b016f4d), [tool và unit test](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/9cc310b).
- [Eval nhóm](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/aec3144), [Streamlit và transcript](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/42721a9).

## Nguyễn Thiên Bảo - 2A202603861

### Phần việc phụ trách

- Phát triển tool mới thứ hai `hn_search` (Hacker News), hoàn thiện unit test TODO, và tiếp tục tối ưu prompt sau v7 để sửa lỗi M06 (nhánh `nguyenthienbao-main`, gộp vào `main`).

### Đóng góp cụ thể

- Tích hợp `hn_search` qua Hacker News Algolia API (không cần key) với 6 unit test, và thêm bộ case riêng `eval_new_tool_hn_search.json` kiểm tra agent chọn tool mới (3/3).
- Hoàn thiện 14 unit test TODO của tool có sẵn: `pytest` từ 70 passed / 14 skipped lên 95 passed, 0 skipped.
- Đo lại v7 bằng provider `openai`, rồi chạy v8–v10: tích hợp `hn_search`, sửa M06 (nguồn đã bỏ thì bỏ luôn, đổi nguồn chỉ gọi tool mới). Kết quả v10: base 20/20 (chạy 2 lần), group 10/10.
- Lưu transcript live v10, bổ sung Phần A/B của báo cáo nhóm cho các phần trên. Trước đó thử độc lập v0–v8 từ starter trên nhánh `nguyenthienbao` (0.65 → 1.00).

### Bằng chứng

- [Báo cáo cá nhân](report/team/2A202603861_NguyenThienBao.md).
- [Unit test TODO](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/90f1b1b), [tool `hn_search`](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/116965e).
- [v8](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/5f61ac7), [v9](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/c353b4d), [v10](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/fdd16e2), [transcript v10](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/00334ec).

## Nguyễn Đức Nhật - 2A202603812

### Phần việc phụ trách

- Chạy baseline, phân tích lỗi từ log và cải tiến system prompt trên nhánh `NguyenDucNhat3006`.

### Đóng góp cụ thể

- Chạy và phân tích baseline v0, sau đó cập nhật log JSON để lưu bằng chứng đánh giá.
- Chỉnh system prompt v1 để agent hỏi lại khi thiếu handle hoặc URL, xin xác nhận trước khi gửi và tách từ khóa tìm kiếm khỏi bộ lọc tin tức.
- Chạy lại v1 sau khi chỉnh prompt và lưu run JSON cùng bảng phân tích v1.

### Bằng chứng

- [Baseline v0](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/364263e), [cập nhật log JSON](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/fbbd6db).
- [System prompt, run JSON và bảng phân tích v1](https://github.com/AnK17-UIT/K5-L3B-DAY03-NguyenHoangGiaAn-2A202603799-PromptEngineeringToolCalling/commit/89be98d).
