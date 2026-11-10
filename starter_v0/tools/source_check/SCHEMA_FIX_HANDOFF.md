# Bàn giao sửa schema source_check — Trần Minh Tân

- Ngày: 10/11/2026.
- Branch: `feature/source-check-schema-03688`.
- Base: `main` tại `9b24a6a` (đã có bản sửa UI của Minh).
- Trạng thái: sửa xong và test offline đạt; chờ review/merge, sau đó chạy eval thật.

## Lỗi và thay đổi

Run group G01 của Minh phát hiện provider từ chối item thiếu URL/source ngay
ở bước kiểm tra JSON Schema. Khai báo tool bắt buộc `url/source` trên từng item,
trong khi mục đích của `source_check` là nhận item thiếu metadata để báo lỗi.

Đã bỏ `required: [url, source]` trong schema của item. Argument ngoài cùng
`items` vẫn bắt buộc và vẫn phải là array; các kiểu field khác giữ nguyên.
Description nhắc truyền nguyên dữ liệu, không tự điền field thiếu.
Implementation không đổi: item thiếu trường vẫn invalid, không bị tính thành
nguồn hợp lệ. Không thay đổi prompt, tool khác hoặc snapshot baseline v0.

## Kiểm chứng

- Thêm 4 regression cases qua JSON Schema validator thật và fake provider:
  object rỗng, chỉ có title, thiếu URL, thiếu source; mỗi case trộn một item tốt.
- Cả 4 case **FAIL trước sửa** do validation, **PASS sau sửa**.
- Kiểm tra args không bị tự điền, item tốt còn nguyên và item lỗi có đúng
  `missing_url`/`missing_source` khi chạy qua agent.
- Cập nhật test cũ từng ép schema phải có nested `required`.
- Thêm `jsonschema>=4.0.0` vào test dependencies trong `requirements.txt` để
  regression test dùng validator chuẩn, không mô phỏng lại logic validator.
- Bộ test cuối: **131 passed, 0 failed, 0 skipped**, gồm 60 contract, 7 example,
  59 tool và 5 UI cases; 1 warning deprecation của plugin `anyio` môi trường.
- [Trước sửa](schema-regression-before.txt) và [sau sửa](schema-fix-test-output.txt)
  là output thật; file sau sửa có SHA256 của `tools.yaml`.

Chạy tại `starter_v0/` trong môi trường đã cài dependencies:

```powershell
python -m pip install -r requirements.txt
python -m pytest -v
python -m pytest -v tests/test_tools_todo.py -k provider_schema_accepts
```

## Trọng và Minh làm tiếp

1. Review block `source_check` trong `tools.yaml`, merge bản sửa này vào `main`,
   rồi cập nhật vào các nhánh làm việc trước khi chạy eval liên quan.
2. Trọng dùng YAML mới cho vòng tối ưu/eval tiếp theo và ghi nhận tools hash
   mới trong evidence/version log. Giữ nguyên các log/snapshot cũ để so sánh.
3. Minh chạy lại G01/group eval với provider/model thực tế của nhóm; không đổi
   kết quả ERR cũ trong report thành PASS khi chưa chạy lại. Cập nhật B5 với
   test count 131 và link evidence mới.
4. Tân kiểm tra `tool_events[].args` và output trong live transcript sau khi
   Minh bàn giao; hiện chưa chạy lại model/API thật trong lần sửa này.

Giới hạn khác vẫn còn: G01/G10 chỉ chấm routing vì evaluator chưa so sánh
được list object. Bản sửa schema này không sửa runner hoặc tự tăng độ bao phủ
chấm arguments của group suite. Không cần chờ Tân viết thêm tool để tiếp tục
v2/v3 sau khi đã tích hợp bản sửa này.
