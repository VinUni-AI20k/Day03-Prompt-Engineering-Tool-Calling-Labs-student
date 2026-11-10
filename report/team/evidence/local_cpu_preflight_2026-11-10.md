# Ollama CPU preflight evidence

- Date: 2026-11-10
- Ollama version: `0.40.16`
- Model alias: `qwen2.5:3b-cpu`
- Alias parameter: `num_gpu=0` (created from the existing `qwen2.5:3b`; no model download)
- Command, run from `starter_v0/`:

  ```powershell
  .venv\Scripts\python.exe scripts\preflight_provider.py --provider ollama --model qwen2.5:3b-cpu
  ```

- Preflight output:

  ```text
  OK provider=ollama model=qwen2.5:3b-cpu
  tool=social_search
  args={'query': 'Sam Altman', 'search_type': 'Latest'}
  ```

- `ollama ps` reported `100% CPU` for `qwen2.5:3b-cpu`.
- Scope: this proves the local provider returned a structured tool call on CPU. It is not a base-eval run and is not counted in B7 metrics.
