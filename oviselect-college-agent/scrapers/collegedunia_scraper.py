"""CollegeDunia public HTML scraper — no API key needed.

Scrapes placement stats, fee structure, and campus info from public pages.
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
from config.college_urls import get_collegedunia_url

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

_robots_checked = False
_robots_allowed = True


def _check_robots() -> bool:
    """Check robots.txt for collegedunia.com."""
    global _robots_checked, _robots_allowed
    if _robots_checked:
        return _robots_allowed
    try:
        rp = RobotFileParser()
        rp.set_url("https://collegedunia.com/robots.txt")
        rp.read()
        _robots_allowed = rp.can_fetch(HTTP_USER_AGENT, "/university/")
        _robots_checked = True
    except Exception:
        _robots_allowed = True
        _robots_checked = True
    return _robots_allowed


def _fetch_page(url: str) -> str | None:
    """Fetch a CollegeDunia page with polite delay."""
    if not _check_robots():
        logger.warning("CollegeDunia robots.txt disallows scraping /university/")
        return None
    time.sleep(random.uniform(3, 5))
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code == 429:
            logger.warning("CollegeDunia rate limit, waiting 60s...")
            time.sleep(60)
            resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code != 200:
            logger.debug(f"CollegeDunia {resp.status_code} for {url}")
            return None
        return resp.text
    except Exception as e:
        logger.debug(f"CollegeDunia request failed: {e}")
        return None


def _extract_number(text: str) -> float | None:
    """Extract first number from text like '12.5 LPA' or '₹1,20,000'."""
    text = text.replace(",", "").replace("₹", "").strip()
    m = re.search(r'([\d]+(?:\.\d+)?)', text)
    return float(m.group(1)) if m else None


def _scrape_placement_page(html: str) -> dict[str, Any]:
    """Extract placement data from CollegeDunia placement page."""
    soup = BeautifulSoup(html, "html.parser")
    data: dict[str, Any] = {}

    text = soup.get_text(separator=" ", strip=True).lower()

    # Try to find average package
    for pattern in [r'average\s+(?:package|ctc|salary)[:\s]*(?:inr\s*)?(?:rs\.?\s*)?([\d.]+)\s*(?:lpa|lakhs?)', 
                    r'average\s+(?:package|ctc)[:\s]*([\d.]+)\s*lpa']:
        m = re.search(pattern, text)
        if m:
            data["avg_package_lpa"] = float(m.group(1))
            break

    # Highest package
    for pattern in [r'highest\s+(?:package|ctc|salary)[:\s]*(?:inr\s*)?(?:rs\.?\s*)?([\d.]+)\s*(?:lpa|lakhs?|cr)',
                    r'highest\s+(?:package|ctc)[:\s]*([\d.]+)\s*(?:lpa|cr)']:
        m = re.search(pattern, text)
        if m:
            val = float(m.group(1))
            if "cr" in text[m.start():m.end()+5]:
                val *= 100  # Convert crore to LPA
            data["highest_package_lpa"] = val
            break

    # Placement percentage
    m = re.search(r'placement\s+(?:percentage|rate)[:\s]*([\d.]+)\s*%', text)
    if m:
        data["placement_percentage"] = float(m.group(1))

    # Companies visited
    m = re.search(r'([\d]+)\s+(?:companies|recruiters)\s+visited', text)
    if m:
        data["companies_visited"] = int(m.group(1))

    # Top recruiters from lists
    recruiters = []
    for el in soup.find_all(["li", "span", "td"]):
        t = el.get_text(strip=True)
        if any(comp in t for comp in ["Google", "Microsoft", "Amazon", "TCS", "Infosys", 
                                        "Wipro", "Goldman", "Morgan Stanley", "Adobe",
                                        "Flipkart", "Deloitte", "McKinsey"]):
            if len(t) < 50:
                recruiters.append(t)
    if recruiters:
        data["top_recruiters"] = list(set(recruiters))[:20]

    return data


def _scrape_fees_page(html: str) -> dict[str, Any]:
    """Extract fee structure from CollegeDunia fees page."""
    soup = BeautifulSoup(html, "html.parser")
    data: dict[str, Any] = {}
    text = soup.get_text(separator=" ", strip=True).lower()

    # Tuition fee
    for pattern in [r'tuition\s+fee[:\s]*(?:inr\s*)?(?:rs\.?\s*)?([\d,]+)', 
                    r'b\.?tech\s+fee[:\s]*(?:inr\s*)?(?:rs\.?\s*)?([\d,]+)']:
        m = re.search(pattern, text)
        if m:
            data["tuition_fee"] = int(m.group(1).replace(",", ""))
            break

    # Hostel fee
    m = re.search(r'hostel\s+fee[:\s]*(?:inr\s*)?(?:rs\.?\s*)?([\d,]+)', text)
    if m:
        data["hostel_fee"] = int(m.group(1).replace(",", ""))

    return data


def scrape_collegedunia(college_name: str) -> dict[str, Any]:
    """Scrape CollegeDunia for placement and fee data. Uses cache."""
    cache_key = "collegedunia"
    if has_cache(college_name, cache_key):
        cached = read_cache(college_name, cache_key)
        if cached:
            logger.debug(f"CollegeDunia cache hit for {college_name}")
            return cached

    result: dict[str, Any] = {"source": "collegedunia", "found": False}

    # Placement page
    url = get_collegedunia_url(college_name, "placement")
    if url:
        html = _fetch_page(url)
        if html:
            result["found"] = True
            result.update(_scrape_placement_page(html))

    # Fees page
    url = get_collegedunia_url(college_name, "fees-and-eligibility")
    if url:
        html = _fetch_page(url)
        if html:
            result["found"] = True
            result.update(_scrape_fees_page(html))

    write_cache(college_name, cache_key, result)
    status = "found" if result["found"] else "no URL mapped"
    logger.info(f"CollegeDunia: {college_name} → {status}")
    return result

