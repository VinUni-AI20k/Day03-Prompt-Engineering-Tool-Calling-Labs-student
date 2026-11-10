---
name: save_note
track: core
kind: action
provider: local
requires_env: []
inputs: [filename, content, confirmed]
outputs: [status, path, filename, chars]
side_effect: local_file_write
requires_confirmation: true
---
# save_note

Saves research notes, summaries, or reports to a local markdown file under the notes/ directory.
Writing only happens when `confirmed` is true.
