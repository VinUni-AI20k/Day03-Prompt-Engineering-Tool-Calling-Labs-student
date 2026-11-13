# Phân việc nhóm

| Người | Vai trò | File |
| ----- | ------- | ---- |
| QuanNH | Dev: prompt, tools.yaml, eval v0→v3, review PR, server + UI | [QuanNH.md](QuanNH.md) |
| TrungNB | Dev: eval case, version log, báo cáo, Telegram | [TrungNB.md](TrungNB.md) |
| DucLT | Dev: unit test, tool mới, metric, Ollama | [DucLT.md](DucLT.md) |

## Quy tắc chung
- Mỗi người làm trên nhánh riêng (`feat/<tên>-<việc>`), mở PR, lead review rồi merge.
- Chạy mọi lệnh từ `starter_v0/`. `pytest` phải xanh trước khi mở PR.
- Không commit `.env`, không dán key/token vào chat hay báo cáo.
- Không bịa run/metric/transcript. Chỉ ghi những gì đã chạy thật.
- Dùng AI được, nhưng phải tự giải thích được phần mình làm. Ghi công cụ AI vào báo cáo cá nhân.
- Giữ nguyên một provider và model xuyên suốt v0→v3.

## Mốc (giờ tại lớp, không phải deadline; deadline 23h59 ngày lab)
- CP1 15:00: setup, preflight, pytest, baseline v0 + bảng B2
- CP2 15:30 / 16:00 / 17:30: v1 / v2 / v3
- CP3 15:30: tool mới + ≥ 3 test
- CP4 16:00: 10 case nhóm + run `--suite group`
- CP5 16:30: showdown, Phần A xong và UI dùng thử được; sau đó hoàn thiện Phần B, transcript, báo cáo cá nhân
- Nộp: run JSON, transcript JSON, repo đúng tên, không lộ key
