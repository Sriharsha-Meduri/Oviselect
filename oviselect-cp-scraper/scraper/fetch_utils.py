"""Shared HTTP fetch utilities using Scrapling as the primary engine.

Scrapling provides stealth TLS fingerprinting (browser impersonation) and
automatic header generation, which helps bypass anti-bot protections common
on Indian academic institution websites.

All deep scrapers (NIT, IIIT, IIT, GFTI) import `fetch` and `post` from
here instead of using `requests` directly.

Fallback
--------
If Scrapling itself raises an unexpected error, both helpers fall back
transparently to plain ``requests`` so scrapers never break silently.
"""

from __future__ import annotations

import time
from typing import Any

import requests
import urllib3
from bs4 import BeautifulSoup
from loguru import logger
from scrapling.fetchers import Fetcher

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Default headers used by the requests fallback path only.
# Scrapling generates realistic browser headers automatically via stealthy_headers=True.
_FALLBACK_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch(
    url: str,
    *,
    retries: int = 2,
    timeout: int = 20,
    verify: bool = False,
) -> BeautifulSoup | None:
    """Fetch *url* with Scrapling (stealth GET), fall back to requests.

    Returns a BeautifulSoup of the page on HTTP 200, or None otherwise.
    """
    # ── Primary: Scrapling ────────────────────────────────────
    try:
        resp = Fetcher.get(
            url,
            timeout=timeout,
            verify=verify,
            stealthy_headers=True,
            retries=retries,
            follow_redirects=True,
        )
        if resp.status == 200:
            return BeautifulSoup(str(resp.html_content), "html.parser")
        if resp.status == 404:
            logger.warning(f"HTTP 404 for {url}")
            return None
        logger.warning(f"HTTP {resp.status} for {url}")
        return None
    except Exception as exc:
        logger.debug(f"Scrapling GET failed for {url}: {exc} — falling back to requests")

    # ── Fallback: plain requests ──────────────────────────────
    for attempt in range(retries + 1):
        try:
            r = requests.get(
                url,
                headers=_FALLBACK_HEADERS,
                timeout=timeout,
                allow_redirects=True,
                verify=verify,
            )
            if r.status_code == 200:
                return BeautifulSoup(r.text, "html.parser")
            logger.warning(f"[fallback] HTTP {r.status_code} for {url}")
            return None
        except Exception as exc2:
            if attempt < retries:
                time.sleep(2)
            else:
                logger.warning(f"[fallback] Failed {url}: {exc2}")
    return None


def post(
    url: str,
    *,
    data: dict[str, Any] | None = None,
    json: Any = None,
    retries: int = 2,
    timeout: int = 20,
    verify: bool = False,
) -> BeautifulSoup | None:
    """POST *url* with Scrapling (stealth), fall back to requests.

    Returns a BeautifulSoup of the response body on HTTP 200, or None.
    """
    # ── Primary: Scrapling ────────────────────────────────────
    try:
        resp = Fetcher.post(
            url,
            data=data,
            json=json,
            timeout=timeout,
            verify=verify,
            stealthy_headers=True,
            retries=retries,
        )
        if resp.status == 200:
            return BeautifulSoup(str(resp.html_content), "html.parser")
        logger.warning(f"[POST] HTTP {resp.status} for {url}")
        return None
    except Exception as exc:
        logger.debug(f"Scrapling POST failed for {url}: {exc} — falling back to requests")

    # ── Fallback: plain requests ──────────────────────────────
    for attempt in range(retries + 1):
        try:
            r = requests.post(
                url,
                data=data,
                json=json,
                headers=_FALLBACK_HEADERS,
                timeout=timeout,
                allow_redirects=True,
                verify=verify,
            )
            if r.status_code == 200:
                return BeautifulSoup(r.text, "html.parser")
            logger.warning(f"[fallback POST] HTTP {r.status_code} for {url}")
            return None
        except Exception as exc2:
            if attempt < retries:
                time.sleep(2)
            else:
                logger.warning(f"[fallback POST] Failed {url}: {exc2}")
    return None

