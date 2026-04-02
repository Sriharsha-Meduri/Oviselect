"""Fetcher for official college websites with local HTML caching.

Uses Scrapling's Fetcher for stealth HTTP requests that bypass Cloudflare
and other anti-bot protections — no API key required.
"""

from __future__ import annotations

import hashlib
import random
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from loguru import logger
from scrapling.fetchers import Fetcher
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config.settings import OFFICIAL_CACHE_DIR
from config.official_urls import SECTION_PATHS


class FetchError(Exception):
    pass


def _url_to_cache_key(url: str) -> str:
    """Convert a URL to a safe filename using a hash."""
    return hashlib.md5(url.encode()).hexdigest()


def _cache_path(url: str, slug: str) -> Path:
    key = _url_to_cache_key(url)
    slug_dir = OFFICIAL_CACHE_DIR / slug
    slug_dir.mkdir(parents=True, exist_ok=True)
    return slug_dir / f"{key}.html"


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=5, min=5, max=60),
    retry=retry_if_exception_type(FetchError),
    reraise=True,
)
def _fetch_url(url: str) -> str | None:
    """Fetch a URL and return the HTML text, or None on failure."""
    try:
        resp = Fetcher.get(url, timeout=25, stealthy_headers=True)
        if resp.status == 429:
            raise FetchError(f"429 rate-limited: {url}")
        if resp.status in (403, 503):
            raise FetchError(f"HTTP {resp.status}: {url}")
        if resp.status == 404:
            return None
        if resp.status != 200:
            logger.debug(f"HTTP {resp.status} for {url}")
            return None
        return str(resp.html_content)
    except FetchError:
        raise
    except Exception as e:
        logger.debug(f"Request error for {url}: {e}")
        return None


def fetch_official_page(
    url: str,
    slug: str,
    *,
    force_refresh: bool = False,
    from_cache: bool = False,
) -> BeautifulSoup | None:
    """Fetch an official site page, using local cache when available.

    Args:
        url:           Full URL to fetch.
        slug:          College slug (used to organise cache files).
        force_refresh: If True, ignore cache and re-fetch.
        from_cache:    If True, only read from cache; no HTTP requests.

    Returns:
        Parsed BeautifulSoup or None on failure.
    """
    cache_file = _cache_path(url, slug)

    # ── Cache hit ────────────────────────────────────────────
    if not force_refresh and cache_file.exists():
        logger.debug(f"[{slug}] Official cache hit: {url}")
        html = cache_file.read_text(encoding="utf-8", errors="replace")
        return BeautifulSoup(html, "lxml")

    if from_cache:
        logger.debug(f"[{slug}] No official cache for {url} — skipping")
        return None

    # ── Fetch ────────────────────────────────────────────────
    logger.info(f"[{slug}] Fetching official page: {url}")
    try:
        html = _fetch_url(url)
    except FetchError as e:
        logger.warning(f"[{slug}] Official fetch failed: {e}")
        return None

    if not html:
        return None

    cache_file.write_text(html, encoding="utf-8")
    logger.debug(f"[{slug}] Cached official page ({len(html)} chars)")

    time.sleep(random.uniform(2, 4))
    return BeautifulSoup(html, "lxml")


def discover_section_url(
    base_url: str,
    slug: str,
    section: str,
    *,
    nav_soup: BeautifulSoup | None = None,
    force_refresh: bool = False,
    from_cache: bool = False,
) -> str | None:
    """Try to find the URL for a given section on the official website.

    Strategy:
    1. Look for nav links whose text/href matches the section keyword.
    2. Try known path patterns from SECTION_PATHS.

    Returns the first working URL found, or None.
    """
    # ── Strategy 1: parse navigation links ──────────────────
    if nav_soup is not None:
        keywords = [section.replace("_", " "), section.replace("_", "-")]
        for a in nav_soup.find_all("a", href=True):
            href = a["href"].lower()
            text = a.get_text(strip=True).lower()
            for kw in keywords:
                if kw in href or kw in text:
                    full_url = urljoin(base_url, a["href"])
                    # Verify it's the same domain
                    if urlparse(full_url).netloc == urlparse(base_url).netloc:
                        logger.debug(f"[{slug}] Found {section} via nav: {full_url}")
                        return full_url

    # ── Strategy 2: try known path patterns ─────────────────
    for path in SECTION_PATHS.get(section, []):
        candidate = base_url.rstrip("/") + path
        cache_file = _cache_path(candidate, slug)
        if not force_refresh and cache_file.exists():
            logger.debug(f"[{slug}] {section} cache hit: {candidate}")
            return candidate
        if from_cache:
            continue
        try:
            resp = Fetcher.get(candidate, timeout=15, stealthy_headers=True)
            html = str(resp.html_content)
            if resp.status == 200 and len(html) > 500:
                # Save to cache and return
                cache_file.write_text(html, encoding="utf-8")
                logger.debug(f"[{slug}] Found {section} at: {candidate}")
                time.sleep(random.uniform(1, 2))
                return candidate
        except Exception:
            pass

    logger.debug(f"[{slug}] Could not discover {section} section URL")
    return None

