# CP5 — snapshot cấu hình main của nhóm

Nền main GitHub `a557a55`; snapshot giữ đúng byte prompt/declaration 14 tool và bộ group 10 case đang dùng khi kiểm tra CP5.

- Prompt: `0d8d6477582f99aefd48c1b69a0527d133701fcf5112fd13f4affbe4e11b38d1`.
- Tools: `835122e4256998446c166a8403490b94ec250f5becd413ec1e696d5ffaafbfee`.
- Base: `runs/cp5-team_B_base_openai_20261111T004229851343.json` (17/20).
- Group: `runs/cp5-team_B_group_openai_20261111T004229756879.json` (10/10).

Từ starter_v0, chạy `python run_eval.py --provider openai --model gpt-4o-mini --version cp5-team-recheck --suite base --eval-cases data/eval_base.json --system-prompt artifacts/versions/cp5-team/system_prompt.md --tools artifacts/versions/cp5-team/tools.yaml`. Với group, đổi suite thành group và dùng `--eval-cases artifacts/versions/cp5-team/eval_group.json`.

CP5 thêm UI và bằng chứng, không phải vòng tối ưu prompt/declaration mới. Giữ các run v0–v3 của nhóm và không thay nhãn/hash của lịch sử thử nghiệm.
