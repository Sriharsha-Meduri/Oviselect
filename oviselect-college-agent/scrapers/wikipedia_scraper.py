"""Wikipedia REST API scraper — completely free, no key required.

Uses:
  - /api/rest_v1/page/summary/{title} for quick facts
  - /w/api.php?action=parse for full HTML content
"""

from __future__ import annotations

import re
import time
from typing import Any, Optional

import requests
from bs4 import BeautifulSoup
from loguru import logger

from config import HTTP_USER_AGENT
from pipeline.cache import has_cache, read_cache, write_cache
from config.college_urls import get_wikipedia_title

HEADERS = {"User-Agent": HTTP_USER_AGENT}
REQUEST_DELAY = 1.0


def _fetch_summary(title: str) -> dict | None:
    """Fetch Wikipedia page summary via REST API."""
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    try:
        time.sleep(REQUEST_DELAY)
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return None
        return resp.json()
    except Exception as e:
        logger.debug(f"Wikipedia summary failed for {title}: {e}")
        return None


def _fetch_full_page(title: str) -> str | None:
    """Fetch full Wikipedia page HTML via MediaWiki API."""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "parse", "page": title, "prop": "text",
        "format": "json", "formatversion": "2",
    }
    try:
        time.sleep(REQUEST_DELAY)
        resp = requests.get(url, headers=HEADERS, params=params, timeout=20)
        if resp.status_code != 200:
            return None
        data = resp.json()
        return data.get("parse", {}).get("text", "")
    except Exception as e:
        logger.debug(f"Wikipedia full page failed for {title}: {e}")
        return None


def _extract_infobox(html: str) -> dict[str, str]:
    """Extract key-value pairs from Wikipedia infobox."""
    soup = BeautifulSoup(html, "html.parser")
    infobox = soup.find("table", class_="infobox")
    if not infobox:
        return {}
    data = {}
    for row in infobox.find_all("tr"):
        th = row.find("th")
        td = row.find("td")
        if th and td:
            key = th.get_text(strip=True).lower()
            val = td.get_text(strip=True)
            data[key] = val
    return data


def _parse_year(text: str) -> int | None:
    """Extract a 4-digit year from text."""
    m = re.search(r'(1[89]\d{2}|20[0-2]\d)', text)
    return int(m.group(1)) if m else None


def _parse_acres(text: str) -> float | None:
    """Extract campus area in acres from text."""
    m = re.search(r'([\d,]+(?:\.\d+)?)\s*(?:acres|acre)', text, re.IGNORECASE)
    if m:
        return float(m.group(1).replace(",", ""))
    # Try hectares → acres
    m = re.search(r'([\d,]+(?:\.\d+)?)\s*(?:hectares|ha)', text, re.IGNORECASE)
    if m:
        return round(float(m.group(1).replace(",", "")) * 2.471, 1)
    return None


def scrape_wikipedia(college_name: str) -> dict[str, Any]:
    """Scrape Wikipedia for college data. Returns extracted fields.

    Uses cache if available.
    """
    cache_key = "wikipedia"
    if has_cache(college_name, cache_key):
        cached = read_cache(college_name, cache_key)
        if cached:
            logger.debug(f"Wikipedia cache hit for {college_name}")
            return cached

    title = get_wikipedia_title(college_name)
    if not title:
        # Try auto-generating the title
        title = college_name.replace(" ", "_")

    result: dict[str, Any] = {"source": "wikipedia", "found": False}

    summary = _fetch_summary(title)
    if summary and summary.get("type") != "not_found":
        result["found"] = True
        result["extract"] = summary.get("extract", "")[:1000]
        result["thumbnail"] = summary.get("thumbnail", {}).get("source")

    html = _fetch_full_page(title)
    if html:
        result["found"] = True
        infobox = _extract_infobox(html)
        result["infobox"] = infobox

        # Extract structured fields
        for key in ["established", "founded"]:
            if key in infobox:
                yr = _parse_year(infobox[key])
                if yr:
                    result["establishment_year"] = yr

        for key in ["campus", "campus size", "area"]:
            if key in infobox:
                acres = _parse_acres(infobox[key])
                if acres:
                    result["campus_area_acres"] = acres

        if "motto" in infobox:
            result["motto"] = infobox["motto"]
        if "director" in infobox:
            result["director"] = infobox["director"]
        if "chancellor" in infobox:
            result["chancellor"] = infobox["chancellor"]
        if "students" in infobox:
            m = re.search(r'([\d,]+)', infobox["students"])
            if m:
                result["total_students"] = int(m.group(1).replace(",", ""))

    write_cache(college_name, cache_key, result)
    status = "found" if result["found"] else "not found"
    logger.info(f"Wikipedia: {college_name} → {status}")
    return result

