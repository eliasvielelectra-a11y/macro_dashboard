from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup


CBE_HOME_URL = "https://www.cbe.org.eg/en/"

# Safe backup values so the app still renders if scraping fails.
# Update manually whenever needed.
FALLBACK_CBE_STATS: dict[str, Any] = {
    "overnight_deposit_rate": 19.00,
    "overnight_lending_rate": 20.00,
    "main_operation": 19.50,
    "conia": 19.215,
    "core_inflation_rate": 12.700,
    "headline_inflation_rate": 13.400,
    "inflation_target_text": "7.0% (±2 percentage points) on average in 2026 Q4",
}


@dataclass
class CBEStatsResult:
    stats: dict[str, Any]
    source_url: str
    source_label: str
    fetch_status: str
    notes: list[str]
    fetched_at_utc: str
    used_fallback_keys: list[str]
    parsed_key_count: int


def _clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_percent_after_label(text: str, label_pattern: str) -> float | None:
    """
    Example match:
    'Overnight Deposit Rate 19.00%'
    """
    pattern = re.compile(
        rf"{label_pattern}\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)\s*%",
        flags=re.IGNORECASE,
    )
    match = pattern.search(text)
    if not match:
        return None
    return float(match.group(1))


def _extract_inflation_target_text(text: str) -> str | None:
    """
    Example match:
    'Current Inflation target 7.0% (±2 percentage points) on average in 2026 Q4'
    """
    pattern = re.compile(
        r"Current\s+Inflation\s+target\s*[:\-]?\s*(.*?)(?=(?:Overnight|Conia|Core|Headline|Main\s+Operation|$))",
        flags=re.IGNORECASE,
    )
    match = pattern.search(text)
    if not match:
        return None

    candidate = _clean_text(match.group(1))
    if len(candidate) > 160:
        candidate = candidate[:160].strip()

    return candidate or None


def _parse_cbe_homepage_text(text: str) -> dict[str, Any]:
    cleaned = _clean_text(text)

    return {
        "overnight_deposit_rate": _extract_percent_after_label(
            cleaned, r"Overnight\s+Deposit\s+Rate"
        ),
        "overnight_lending_rate": _extract_percent_after_label(
            cleaned, r"Overnight\s+Lending\s+Rate"
        ),
        "main_operation": _extract_percent_after_label(
            cleaned, r"Main\s+Operation"
        ),
        "conia": _extract_percent_after_label(
            cleaned, r"Conia"
        ),
        "core_inflation_rate": _extract_percent_after_label(
            cleaned, r"Core\s+Inflation\s+Rate"
        ),
        "headline_inflation_rate": _extract_percent_after_label(
            cleaned, r"Headline\s+Inflation\s+Rate"
        ),
        "inflation_target_text": _extract_inflation_target_text(cleaned),
    }


def _merge_with_fallback(parsed: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
    stats: dict[str, Any] = {}
    notes: list[str] = []
    used_fallback_keys: list[str] = []

    for key, fallback_value in FALLBACK_CBE_STATS.items():
        value = parsed.get(key)
        if value is None:
            stats[key] = fallback_value
            used_fallback_keys.append(key)
            notes.append(f"{key}: using fallback value")
        else:
            stats[key] = value

    return stats, notes, used_fallback_keys



def _is_reasonable_value(key: str, value: Any) -> bool:
    if value is None:
        return False

    if key == "inflation_target_text":
        return isinstance(value, str) and len(value.strip()) > 0

    try:
        v = float(value)
    except Exception:
        return False

    reasonable_ranges = {
        "overnight_deposit_rate": (0.0, 50.0),
        "overnight_lending_rate": (0.0, 50.0),
        "main_operation": (0.0, 50.0),
        "conia": (0.0, 50.0),
        "core_inflation_rate": (-10.0, 100.0),
        "headline_inflation_rate": (-10.0, 100.0),
    }

    lo, hi = reasonable_ranges.get(key, (-1e12, 1e12))
    return lo <= v <= hi


def _validate_parsed(parsed: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    cleaned: dict[str, Any] = {}
    notes: list[str] = []

    for key, value in parsed.items():
        if _is_reasonable_value(key, value):
            cleaned[key] = value
        else:
            cleaned[key] = None
            if value is not None:
                notes.append(f"{key}: parsed value rejected by sanity check")

    return cleaned, notes


def fetch_cbe_stats(timeout_seconds: int = 20) -> CBEStatsResult:
    """
    Pulls official CBE key statistics from the homepage.
    Falls back to local backup values if parsing fails partially or fully.
    """
    try:
        response = requests.get(
            CBE_HOME_URL,
            timeout=timeout_seconds,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                )
            },
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        full_text = soup.get_text(" ", strip=True)

        parsed_raw = _parse_cbe_homepage_text(full_text)
        parsed, validation_notes = _validate_parsed(parsed_raw)
        stats, notes, used_fallback_keys = _merge_with_fallback(parsed)
        notes = validation_notes + notes

        missing_count = len(used_fallback_keys)
        parsed_key_count = sum(1 for key in FALLBACK_CBE_STATS.keys() if parsed.get(key) is not None)

        fetch_status = "ok" if missing_count == 0 else "partial_fallback"

        return CBEStatsResult(
            stats=stats,
            source_url=CBE_HOME_URL,
            source_label="Central Bank of Egypt homepage key statistics",
            fetch_status=fetch_status,
            notes=notes,
            fetched_at_utc=datetime.now(timezone.utc).isoformat(),
            used_fallback_keys=used_fallback_keys,
            parsed_key_count=parsed_key_count,
        )

    except Exception as exc:
        return CBEStatsResult(
            stats=FALLBACK_CBE_STATS.copy(),
            source_url=CBE_HOME_URL,
            source_label="Central Bank of Egypt homepage key statistics",
            fetch_status="fallback_only",
            notes=[f"request/parsing failed: {exc}"],
        )