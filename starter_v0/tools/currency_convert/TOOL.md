---
name: currency_convert
track: bonus
kind: live_api
provider: ExchangeRate-API
requires_env: []
inputs: [amount, from_currency, to_currency]
outputs: [rate, converted_amount]
side_effect: false
---
# currency_convert

Converts an amount from one 3-letter ISO currency code (`from_currency`, e.g.
`USD`) into another (`to_currency`, e.g. `VND`) using live exchange rates.
