---
name: send
track: bonus
kind: action
provider: Telegram Bot API
requires_env: [TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]
inputs: [text, confirmed]
outputs: [status]
side_effect: true
requires_confirmation: true
---
# send

Posts text to a Telegram channel. The message is only sent when `confirmed` is true.


Security boundary: confirmed must be the literal boolean True AND the trusted
host must open approve_message(text) after an explicit user confirmation for
that exact text. Approval is consumed by one attempt and cannot authorize a
changed message. The model cannot call approve_message as a tool.
CLI chat previews the text and requires typing SEND. Refusal/EOF cancels.
ResearchAgent/eval are fail-closed: they cannot send without host authorization.
UI integrations must preview text and call approve_message only from the user's
confirmation handler. Do not wrap model execution in a blanket approval context.
Messages are sent as plain text, maximum 4096 characters. No automatic retries.
Tests use fake credentials and mocked HTTP; no real Telegram message was sent.
