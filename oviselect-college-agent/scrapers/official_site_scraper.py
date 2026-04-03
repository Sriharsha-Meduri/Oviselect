"""Official college website scraper — fetches placement pages.

Since official sites vary widely in structure, this scraper fetches the raw
HTML and extracts text. The structuring layer (Ollama/Claude) then parses it.
"""

from __future__ import annotations

import time
import random
from typing import Any
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from loguru import logger

from config import HTTP_USER_AGENT
from pipeline.cache import has_cache, read_cache, write_cache
from config.college_urls import get_official_placement_url

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

_robots_cache: dict[str, bool] = {}


def _check_robots(url: str) -> bool:
    """Check robots.txt for the given URL's domain."""
    parsed = urlparse(url)
    domain = f"{parsed.scheme}://{parsed.netloc}"
    if domain in _robots_cache:
        return _robots_cache[domain]
    try:
        rp = RobotFileParser()
        rp.set_url(f"{domain}/robots.txt")
        rp.read()
        allowed = rp.can_fetch(HTTP_USER_AGENT, parsed.path)
        _robots_cache[domain] = allowed
        return allowed
    except Exception:
        _robots_cache[domain] = True
        return True


def _fetch_page(url: str) -> str | None:
    """Fetch with polite delay and robots.txt check."""
    if not _check_robots(url):
        logger.warning(f"robots.txt disallows: {url}")
        return None
    time.sleep(random.uniform(2, 4))
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        if resp.status_code != 200:
            logger.debug(f"Official site {resp.status_code} for {url}")
            return None
        return resp.text
    except Exception as e:
        logger.debug(f"Official site request failed for {url}: {e}")
        return None


def _extract_text(html: str, max_chars: int = 10000) -> str:
    """Extract clean text from HTML, removing scripts/styles."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    # Collapse multiple newlines
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    clean = "\n".join(lines)
    return clean[:max_chars]


def scrape_official_site(college_name: str) -> dict[str, Any]:
    """Scrape official college placement page. Returns raw text for structuring.

    Uses cache if available.
    """
    cache_key = "official_site"
    if has_cache(college_name, cache_key):
        cached = read_cache(college_name, cache_key)
        if cached:
            logger.debug(f"Official site cache hit for {college_name}")
            return cached

    result: dict[str, Any] = {"source": "official_site", "found": False}

    url = get_official_placement_url(college_name)
    if not url:
        write_cache(college_name, cache_key, result)
        logger.info(f"Official site: {college_name} → no URL mapped")
        return result

    html = _fetch_page(url)
    if html:
        result["found"] = True
        result["url"] = url
        result["raw_text"] = _extract_text(html)

    write_cache(college_name, cache_key, result)
    status = "found" if result["found"] else "fetch failed"
    logger.info(f"Official site: {college_name} → {status}")
    return result

