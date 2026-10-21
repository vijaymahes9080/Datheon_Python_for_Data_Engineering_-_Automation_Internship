"""Data parsers module: currency, compensation ranges, and date normalization."""

from __future__ import annotations

import datetime
import logging
import re
from typing import Any
from dateutil import parser as dateutil_parser

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
        num_min = min(parsed_numbers)
        num_max = max(parsed_numbers)
        result["salary_min"] = num_min
        result["salary_max"] = num_max
        result["salary_avg"] = round((num_min + num_max) / 2.0, 2)

    return result


def parse_and_normalize_date(
    raw_date: str | None,
    reference_date: datetime.date | None = None,
) -> tuple[str | None, bool, str]:
    """Parse raw date text into ISO-8601 YYYY-MM-DD.

    Returns:
        (iso_date_string, is_valid, status_or_reason)
    """
    if not raw_date or not str(raw_date).strip():
        return None, False, "Missing date string"

    text = str(raw_date).strip()
    ref = reference_date or datetime.date.today()

    # 1. Check relative date formats (e.g., '2 days ago', 'yesterday', 'today')
    rel_match = re.search(r"(\d+)\s+day[s]?\s+ago", text, re.IGNORECASE)
    if rel_match:
        days = int(rel_match.group(1))
        computed = ref - datetime.timedelta(days=days)
        return computed.isoformat(), True, "Parsed relative days"

    if "yesterday" in text.lower():
        computed = ref - datetime.timedelta(days=1)
        return computed.isoformat(), True, "Parsed yesterday"

    if "today" in text.lower() or "just posted" in text.lower():
        return ref.isoformat(), True, "Parsed today"

    # 2. Explicit ISO format check YYYY-MM-DD
    if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
        try:
            dt = datetime.date.fromisoformat(text)
            if dt > ref + datetime.timedelta(days=1):
                return None, False, f"Future date violation: {text}"
            return dt.isoformat(), True, "Valid ISO format"
        except ValueError:
            return None, False, f"Invalid calendar date: {text}"

    # 3. Parse with dateutil parser for multiple formats
    try:
        # Check European day-first convention (e.g. 15/10/2026)
        dayfirst = bool(re.match(r"^\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}", text))
        parsed = dateutil_parser.parse(text, dayfirst=dayfirst, default=datetime.datetime(ref.year, ref.month, ref.day))
        dt_val = parsed.date()

        # Invariant check: reject future dates beyond 1 day tolerance
        if dt_val > ref + datetime.timedelta(days=1):
            return None, False, f"Future date violation: {dt_val.isoformat()}"

        # Invariant check: reject ancient dates older than 10 years
        if dt_val < ref - datetime.timedelta(days=3650):
            return None, False, f"Out of range ancient date: {dt_val.isoformat()}"

        return dt_val.isoformat(), True, "Parsed date successfully"

    except (ValueError, OverflowError, dateutil_parser.ParserError):
        # Identified invalid date instead of silently returning corrupted data
        return None, False, f"Unparseable date string: '{text}'"
