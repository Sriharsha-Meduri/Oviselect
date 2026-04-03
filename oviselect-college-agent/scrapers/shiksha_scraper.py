"""Shiksha public HTML scraper — no API key needed.

Scrapes fee structure, placement stats, and faculty info from public pages.
Uses 3-5 second random delay between requests.
"""

from __future__ import annotations

import re
import time
import random
from typing import Any
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from loguru import logger

from config import HTTP_USER_AGENT
from pipeline.cache import has_cache, read_cache, write_cache
from config.college_urls import get_shiksha_url

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

_robots_checked = False
_robots_allowed = True


def _check_robots() -> bool:
    global _robots_checked, _robots_allowed
    if _robots_checked:
        return _robots_allowed
    try:
        rp = RobotFileParser()
        rp.set_url("https://www.shiksha.com/robots.txt")
        rp.read()
        _robots_allowed = rp.can_fetch(HTTP_USER_AGENT, "/university/")
        _robots_checked = True
    except Exception:
        _robots_allowed = True
        _robots_checked = True
    return _robots_allowed


def _fetch_page(url: str) -> str | None:
    if not _check_robots():
        logger.warning("Shiksha robots.txt disallows scraping")
        return None
    time.sleep(random.uniform(3, 5))
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code == 429:
            logger.warning("Shiksha rate limit, waiting 60s...")
            time.sleep(60)
            resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code != 200:
            return None
        return resp.text
    except Exception as e:
        logger.debug(f"Shiksha request failed: {e}")
        return None


def _extract_data(html: str) -> dict[str, Any]:
    """Extract structured data from Shiksha college page."""
    soup = BeautifulSoup(html, "html.parser")
    data: dict[str, Any] = {}
    text = soup.get_text(separator=" ", strip=True).lower()

    # Average package
    m = re.search(r'average\s+(?:package|ctc|placement)[:\s]*(?:inr\s*)?([\d.]+)\s*(?:lpa|lakhs?)', text)
    if m:
        data["avg_package_lpa"] = float(m.group(1))

    # Highest package
    m = re.search(r'highest\s+(?:package|ctc|placement)[:\s]*(?:inr\s*)?([\d.]+)\s*(?:lpa|lakhs?|cr)', text)
    if m:
        val = float(m.group(1))
        if "cr" in text[m.start():m.end()+5]:
            val *= 100
        data["highest_package_lpa"] = val

    # Total faculty
    m = re.search(r'(?:total\s+)?faculty[:\s]*([\d,]+)', text)
    if m:
        data["total_faculty"] = int(m.group(1).replace(",", ""))

    # Student-faculty ratio
    m = re.search(r'student[\s-]*faculty\s+ratio[:\s]*([\d]+)\s*:\s*1', text)
    if m:
        data["student_faculty_ratio"] = float(m.group(1))

    # Tuition fee
    m = re.search(r'(?:b\.?tech|tuition)\s+fee[:\s]*(?:inr\s*)?(?:rs\.?\s*)?([\d,]+)', text)
    if m:
        data["tuition_fee"] = int(m.group(1).replace(",", ""))

    # Hostel fee
    m = re.search(r'hostel\s+fee[:\s]*(?:inr\s*)?(?:rs\.?\s*)?([\d,]+)', text)
    if m:
        data["hostel_fee"] = int(m.group(1).replace(",", ""))

    # NAAC grade
    m = re.search(r'naac\s+(?:grade|accreditation)[:\s]*([a-z]\+?\+?)', text)
    if m:
        data["naac_grade"] = m.group(1).upper()

    return data


def scrape_shiksha(college_name: str) -> dict[str, Any]:
    """Scrape Shiksha for college data. Uses cache."""
    cache_key = "shiksha"
    if has_cache(college_name, cache_key):
        cached = read_cache(college_name, cache_key)
        if cached:
            logger.debug(f"Shiksha cache hit for {college_name}")
            return cached

    result: dict[str, Any] = {"source": "shiksha", "found": False}

    url = get_shiksha_url(college_name)
    if url:
        html = _fetch_page(url)
        if html:
            result["found"] = True
            result.update(_extract_data(html))

    write_cache(college_name, cache_key, result)
    status = "found" if result["found"] else "no URL mapped"
    logger.info(f"Shiksha: {college_name} → {status}")
    return result

