"""Merge CollegePravesh data with official website data.

Priority rule: official site data overrides CollegePravesh data for any
field where the official site provides a non-null, non-empty value.

Scalar fields are simply replaced.
List fields: official list replaces CP list if it is non-empty.
Dict / nested fields: official dict replaces CP dict if it is non-empty.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from loguru import logger


def _is_empty(value: Any) -> bool:
    """Return True when a value carries no meaningful data."""
    if value is None:
        return True
    if isinstance(value, (list, dict)) and len(value) == 0:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def merge(cp_data: dict, official_data: dict, slug: str = "") -> dict:
    """Merge official_data into cp_data, preferring official values.

    Args:
        cp_data:       Parsed CollegePravesh dict (base).
        official_data: Dict collected from official website scraping.
        slug:          College slug (for logging).

    Returns:
        Merged dict.
    """
    merged = deepcopy(cp_data)
    overrides: list[str] = []
    additions: list[str] = []

    for key, official_value in official_data.items():
        if key.startswith("_"):
            # Internal keys — carry over but don't count as override
            merged[key] = official_value
            continue

        if _is_empty(official_value):
            continue

        existing = merged.get(key)
        if _is_empty(existing):
            merged[key] = official_value
            additions.append(key)
        else:
            # Override: official wins
            merged[key] = official_value
            overrides.append(key)

    if overrides:
        logger.info(f"[{slug}] Official data overrode {len(overrides)} fields: {overrides}")
    if additions:
        logger.info(f"[{slug}] Official data added {len(additions)} new fields: {additions}")

    # Update data_sources list
    sources = merged.get("data_sources") or []
    if "official_website" not in sources:
        sources.append("official_website")
    merged["data_sources"] = sources

    return merged

