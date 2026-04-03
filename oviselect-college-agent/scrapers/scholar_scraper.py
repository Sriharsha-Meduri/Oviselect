"""Google Scholar scraper — no auth needed but aggressive rate limits.

Uses 10-second delays between requests. Skips gracefully on blocks.
Extracts institutional h-index and citation data.
"""

from __future__ import annotations

import re
import time
import random
from typing import Any

import requests
from bs4 import BeautifulSoup
from loguru import logger

from pipeline.cache import has_cache, read_cache, write_cache

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

REQUEST_DELAY = 10.0  # Google Scholar is very aggressive with rate limiting


def _fetch_scholar(query: str) -> str | None:
    """Search Google Scholar with a long polite delay."""
    time.sleep(REQUEST_DELAY + random.uniform(2, 5))
    url = "https://scholar.google.com/scholar"
    params = {"q": query, "hl": "en"}
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=20)
        if resp.status_code == 429:
            logger.warning("Google Scholar blocked (429), skipping...")
            return None
        if resp.status_code == 403:
            logger.warning("Google Scholar blocked (403), skipping...")
            return None
        if resp.status_code != 200:
            return None
        return resp.text
    except Exception as e:
        logger.debug(f"Scholar request failed: {e}")
        return None


def _extract_scholar_data(html: str) -> dict[str, Any]:
    """Extract citation info from Scholar search results."""
    soup = BeautifulSoup(html, "html.parser")
    data: dict[str, Any] = {}

    # Count total results
    result_stats = soup.find("div", id="gs_ab_md")
    if result_stats:
        text = result_stats.get_text(strip=True)
        m = re.search(r'About\s+([\d,]+)\s+results', text)
        if m:
            data["total_publications_approx"] = int(m.group(1).replace(",", ""))

    # Extract h-index from profiles if available (institution search)
    profiles = soup.find_all("div", class_="gs_ai_t")
    if profiles:
        data["scholar_profiles_count"] = len(profiles)

    return data


def scrape_scholar(college_name: str) -> dict[str, Any]:
    """Search Google Scholar for institution data. Uses cache.

    Fails gracefully if blocked — returns empty dict with found=False.
    """
    cache_key = "scholar"
    if has_cache(college_name, cache_key):
        cached = read_cache(college_name, cache_key)
        if cached:
            logger.debug(f"Scholar cache hit for {college_name}")
            return cached

    result: dict[str, Any] = {"source": "scholar", "found": False}

    html = _fetch_scholar(f'"{college_name}" institution')
    if html:
        result["found"] = True
        result.update(_extract_scholar_data(html))

    write_cache(college_name, cache_key, result)
    status = "found" if result["found"] else "blocked/failed"
    logger.info(f"Scholar: {college_name} → {status}")
    return result

