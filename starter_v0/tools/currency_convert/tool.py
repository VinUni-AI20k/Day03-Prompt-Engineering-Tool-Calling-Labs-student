from __future__ import annotations

import re
from typing import Any

import requests

from tools._shared import TIMEOUT, err

CURRENCY_CODE_RE = re.compile(r"^[A-Z]{3}$")


def convert_currency(
    amount: float = 1.0,
    from_currency: str = "USD",
    to_currency: str = "VND",
) -> dict[str, Any]:
    try:
        numeric_amount = float(amount)
        if numeric_amount <= 0:
            raise ValueError("amount must be greater than 0")

        src = (from_currency or "").strip().upper()
        dst = (to_currency or "").strip().upper()
        if not CURRENCY_CODE_RE.match(src):
            raise ValueError(f"Invalid from_currency {from_currency!r}; must be a 3-letter ISO code like 'USD'")
        if not CURRENCY_CODE_RE.match(dst):
            raise ValueError(f"Invalid to_currency {to_currency!r}; must be a 3-letter ISO code like 'VND'")

        response = requests.get(
            f"https://open.er-api.com/v6/latest/{src}",
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        rates = data.get("rates") or {}
        if dst not in rates:
            raise ValueError(f"Unsupported target currency {dst!r}")

        rate = float(rates[dst])
        converted = round(numeric_amount * rate, 2)
        return {
            "tool": "convert_currency",
            "amount": numeric_amount,
            "from_currency": src,
            "to_currency": dst,
            "rate": rate,
            "converted_amount": converted,
        }
    except Exception as exc:
        return err("convert_currency", exc)
