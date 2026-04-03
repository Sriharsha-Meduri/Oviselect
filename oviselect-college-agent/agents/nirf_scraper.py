"""NIRF ranking scraper — fetches latest engineering rankings."""

from __future__ import annotations

import re
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup
from loguru import logger

from config import HTTP_USER_AGENT
from pipeline.cache import has_cache, read_cache, write_cache

# NIRF engineering ranking page
NIRF_URL = "https://www.nirfindia.org/Rankings/2025/EngineeringRanking.html"
NIRF_OVERALL_URL = "https://www.nirfindia.org/Rankings/2025/OverallRanking.html"

CACHE_KEY = "nirf_rankings"


def _fetch_page(url: str) -> str:
    """Fetch a web page with proper headers."""
    headers = {"User-Agent": HTTP_USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def _parse_nirf_table(html: str) -> list[dict[str, Any]]:
    """Parse NIRF ranking table from HTML.

    Returns list of {rank, name, city, state, score}.
    """
    soup = BeautifulSoup(html, "html.parser")
    rows: list[dict[str, Any]] = []

    # NIRF tables use <table> with ranking data
    tables = soup.find_all("table")
    for table in tables:
        for tr in table.find_all("tr")[1:]:  # Skip header
            cells = tr.find_all("td")
            if len(cells) < 3:
                continue
            try:
                rank_text = cells[0].get_text(strip=True)
                rank = int(re.sub(r"[^0-9]", "", rank_text) or "0")
                name = cells[1].get_text(strip=True)

                # Try to extract city/state from the name cell
                city, state = "", ""
                small = cells[1].find("small")
                if small:
                    loc = small.get_text(strip=True)
                    parts = [p.strip() for p in loc.split(",")]
                    if len(parts) >= 2:
                        city, state = parts[0], parts[-1]
                    elif len(parts) == 1:
                        city = parts[0]
                    # Clean name by removing location
                    name = name.replace(loc, "").strip().rstrip(",")

                score_text = cells[-1].get_text(strip=True) if len(cells) > 3 else ""
                score = float(re.sub(r"[^0-9.]", "", score_text) or "0")

                if rank > 0 and name:
                    rows.append({
                        "rank": rank,
                        "name": name,
                        "city": city,
                        "state": state,
                        "score": score,
                    })
            except (ValueError, IndexError):
                continue

    return rows


def scrape_nirf_rankings() -> dict[str, dict[str, Any]]:
    """Scrape NIRF engineering rankings.

    Returns dict keyed by normalized institute name → {engineering_rank, overall_rank, score}.
    Uses cache if available.
    """
    if has_cache("__global__", CACHE_KEY):
        cached = read_cache("__global__", CACHE_KEY)
        if cached:
            logger.debug(f"NIRF cache hit: {len(cached)} institutes")
            return cached

    result: dict[str, dict[str, Any]] = {}

    # Engineering rankings
    try:
        html = _fetch_page(NIRF_URL)
        eng_rows = _parse_nirf_table(html)
        for row in eng_rows:
            key = row["name"].lower().strip()
            result[key] = {
                "engineering_rank": row["rank"],
                "score": row["score"],
                "city": row["city"],
                "state": row["state"],
            }
        logger.info(f"NIRF engineering: parsed {len(eng_rows)} entries")
    except Exception as e:
        logger.error(f"Failed to scrape NIRF engineering: {e}")

    # Overall rankings
    try:
        html = _fetch_page(NIRF_OVERALL_URL)
        overall_rows = _parse_nirf_table(html)
        for row in overall_rows:
            key = row["name"].lower().strip()
            if key in result:
                result[key]["overall_rank"] = row["rank"]
            else:
                result[key] = {"overall_rank": row["rank"]}
        logger.info(f"NIRF overall: parsed {len(overall_rows)} entries")
    except Exception as e:
        logger.error(f"Failed to scrape NIRF overall: {e}")

    write_cache("__global__", CACHE_KEY, result)
    return result


def find_nirf_rank(
    college_name: str,
    rankings: dict[str, dict[str, Any]],
) -> Optional[dict[str, Any]]:
    """Fuzzy-match a college name against NIRF rankings."""
    name_lower = college_name.lower().strip()

    # Exact match
    if name_lower in rankings:
        return rankings[name_lower]

    # Substring match
    for key, val in rankings.items():
        if key in name_lower or name_lower in key:
            return val

    # Token overlap match
    tokens = set(name_lower.split())
    best_match, best_score = None, 0
    for key, val in rankings.items():
        key_tokens = set(key.split())
        overlap = len(tokens & key_tokens)
        if overlap > best_score and overlap >= 2:
            best_score = overlap
            best_match = val

    return best_match

