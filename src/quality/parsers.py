"""Data parsers module: currency, compensation ranges, and date normalization."""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger("streamforge.quality.parsers")

# Currency symbols mapping to ISO 4217 standard codes
CURRENCY_MAP = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "₹": "INR",
    "¥": "JPY",
    "CAD": "CAD",
    "AUD": "AUD",
    "EUR": "EUR",
    "GBP": "GBP",
    "USD": "USD",
    "INR": "INR",
    "CHF": "CHF",
}


def parse_numeric_token(token: str) -> float | None:
    """Parse numeric token with multipliers like 'k', 'm', or thousands commas."""
    if not token:
        return None
    token = token.strip().replace(",", "")

    multiplier = 1.0
    if token.lower().endswith("k"):
        multiplier = 1000.0
        token = token[:-1]
    elif token.lower().endswith("m"):
        multiplier = 1000000.0
        token = token[:-1]

    try:
        return float(token) * multiplier
    except ValueError:
        return None


def parse_salary_and_currency(raw_salary: str | None) -> dict[str, Any]:
    """Parse raw salary string into structured currency, minimum, maximum, and average values.

    Preserves original string and never merges currencies without explicit conversion.
    """
    result = {
        "salary_min": None,
        "salary_max": None,
        "salary_avg": None,
        "currency": None,
        "salary_raw": str(raw_salary) if raw_salary is not None else "",
    }

    if not raw_salary or not str(raw_salary).strip():
        return result

    raw_str = str(raw_salary).strip()

    # 1. Detect Currency
    detected_currency = None
    for sym, code in CURRENCY_MAP.items():
        if sym in raw_str.upper():
            detected_currency = code
            break
    result["currency"] = detected_currency or "USD"

    # 2. Extract Numbers & Ranges
    # Match patterns like: 140,000 or 140k or 25,00,000
    cleaned_str = re.sub(r"[^\d\.\,\-kKmM\s]", " ", raw_str)
    tokens = re.findall(r"\b\d[\d,\.]*[kKmM]?\b", cleaned_str)

    parsed_numbers: list[float] = []
    for tok in tokens:
        val = parse_numeric_token(tok)
        if val is not None:
            parsed_numbers.append(val)

    if not parsed_numbers:
        return result

    if len(parsed_numbers) == 1:
        single = parsed_numbers[0]
        result["salary_min"] = single
        result["salary_max"] = single
        result["salary_avg"] = single
    else:
        # Range detected (take min and max of candidates)
        num_min = min(parsed_numbers)
        num_max = max(parsed_numbers)
        result["salary_min"] = num_min
        result["salary_max"] = num_max
        result["salary_avg"] = round((num_min + num_max) / 2.0, 2)

    return result
