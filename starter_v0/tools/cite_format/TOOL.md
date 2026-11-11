---
name: cite_format
track: core
kind: local_formatter
inputs: [title, authors, year, url, style]
outputs: [citation, error]
side_effect: false
---

# cite_format

Format publication metadata into an APA 7 citation.

## Inputs

- `title` (string, required): Publication title.
- `authors` (list[string], required): Authors in "Last, First" format.
- `year` (integer, optional): Publication year. Defaults to n.d. when missing.
- `url` (string, optional): Source URL. Omitted when missing.
- `style` (string, optional): Citation style. Only "apa" is supported.

## Outputs

- Success: `{"citation": "..."}`
- Failure: `{"error": "..."}`

## Rules

- Convert given names into initials.
- One author: `Last, F.`
- Two authors: `Last1, F., & Last2, F.`
- Missing year: `(n.d.)`
- Missing URL: omit URL.
- Unsupported styles return an error.
- Empty title or authors return an error.
