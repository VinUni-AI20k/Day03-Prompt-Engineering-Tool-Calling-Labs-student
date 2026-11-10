---
name: text_stats
description: Calculate word count, character count, and estimated reading time for a given research text or summary.
category: analysis
requires_env: []
---

# Text Stats Tool

## Purpose
Analyzes a piece of text (such as a research summary, article draft, or Telegram post) and returns quantitative statistics including word count, character count, and reading time in minutes.

## When to use
- When the user asks how long a summary/article is, or asks for word/character count and reading time.
- When checking if a draft message fits within length limits before sending.

## Arguments
- `text` (str, required): The text content to analyze. Must be a non-empty string.
- `wpm` (int, optional): Reading speed in words per minute (default: 200).