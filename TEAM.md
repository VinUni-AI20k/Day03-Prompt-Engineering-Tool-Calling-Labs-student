# Team contract: new research tool

The new tool is **`deduplicate`**, a deterministic local tool that removes duplicate research results before formatting. This is the agreed contract for implementation, `tools.yaml`, unit tests, and team eval cases.

## Tool API

- **Name:** `deduplicate`
- **Location:** `starter_v0/tools/deduplicate/tool.py` and `TOOL.md`
- **Arguments:**
  - `items` (required): list of result objects; each may contain `title`, `url`, `source`, `summary`, and other existing result fields.
  - `key_by` (optional): `"url"` or `"title"`; defaults to `"url"`.
- **Behavior:** preserve input order and keep the first item for each non-empty key. Compare keys after trimming surrounding whitespace and case-folding; for `url`, also ignore trailing `/` characters. Keep items whose selected key is missing or empty instead of dropping them.
- **Return:** `{"tool": "deduplicate", "items": [...], "removed_count": <int>}`.
- **Invalid input:** return an error dict; do not raise. A non-list `items` or unsupported `key_by` is invalid.
- **No network, environment variables, or side effects.**

## Integration and evaluation

- Register the implementation as `"deduplicate"` in `starter_v0/tools/__init__.py`.
- Declare the same name, arguments, enum, and default in `starter_v0/artifacts/tools.yaml`.
- Add at least 3 focused unit tests in `starter_v0/tests/test_tools_todo.py`: duplicate removal preserves the first item and order; missing keys are retained; invalid arguments return an error dict.
- Add at least one group eval case where the user asks to remove duplicate research results and the expected tool is `deduplicate`.
- Keep these files as the source of truth; coordinate before editing another owner's file.