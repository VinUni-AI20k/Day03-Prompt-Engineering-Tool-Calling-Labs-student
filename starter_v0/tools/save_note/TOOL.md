---
name: save_note
track: core
kind: action
provider: local
requires_env: []
inputs: [filename, content, confirmed, overwrite_confirmed]
outputs: [status, path, filename, chars, overwritten]
side_effect: local_file_write
requires_confirmation: true
---
# save_note

Saves research notes, summaries, or reports to a local markdown file under the notes/ directory.
Writing only happens when `confirmed` is true. If the filename already exists, the tool returns
`needs_overwrite_confirmation` without changing the file. Replace it only after the user explicitly
confirms and `overwrite_confirmed` is true.
