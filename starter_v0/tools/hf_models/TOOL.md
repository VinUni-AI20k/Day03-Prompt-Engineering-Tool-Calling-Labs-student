---
name: hf_models
track: bonus
kind: live_api
provider: Hugging Face Hub API
requires_env: []
inputs: [query, task, sort_by, limit]
outputs: [items]
side_effect: false
---
# hf_models

Searches public AI models on Hugging Face Hub (`https://huggingface.co/api/models`).
Use when the user asks about open-weight models, Hugging Face checkpoints, model downloads/likes, or models for a specific pipeline task.

