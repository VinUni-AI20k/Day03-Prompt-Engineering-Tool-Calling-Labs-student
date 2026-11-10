Run v3: runs/v3_B_base_openai_20261110T095619294467.json; dùng OpenAI gpt-4o-mini.
Điểm v2 → v3: 80% → 80%.
R12 chuyển send → clarify(text), vẫn trượt vì cần yes_no.
R10/R11 vẫn thiếu response_type; M06 vẫn gọi thừa tool.
Giả thuyết chỉ được hỗ trợ một phần; hash tool khác giữa hai run nên chưa tách riêng được tác động của prompt.