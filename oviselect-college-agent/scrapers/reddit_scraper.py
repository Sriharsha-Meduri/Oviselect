"""Reddit public JSON API scraper — zero authentication required.

Appends .json to any Reddit URL to get structured data.
Rate limit: ~1 request/sec (we use 2s delay to be safe).
"""

from __future__ import annotations

import time
import random
from typing import Any

import requests
from loguru import logger

from config import HTTP_USER_AGENT
from pipeline.cache import has_cache, read_cache, write_cache
from config.reddit_queries import SUBREDDITS, get_search_queries

HEADERS = {"User-Agent": HTTP_USER_AGENT}
REQUEST_DELAY = 2.0  # seconds between requests


def _safe_get(url: str, params: dict | None = None, max_retries: int = 3) -> dict | None:
    """Make a rate-limited GET request to Reddit JSON API with exponential backoff."""
    for attempt in range(max_retries):
        try:
            delay = REQUEST_DELAY + random.uniform(0.5, 2.0)
            if attempt > 0:
                delay = min(30, 5 * (2 ** attempt)) + random.uniform(0, 3)
                logger.debug(f"Reddit retry {attempt}/{max_retries}, waiting {delay:.0f}s...")
            time.sleep(delay)
            resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
            if resp.status_code == 429:
                wait = min(120, 30 * (2 ** attempt))
                logger.warning(f"Reddit 429, backing off {wait}s (attempt {attempt+1}/{max_retries})...")
                time.sleep(wait)
                continue
            if resp.status_code != 200:
                logger.debug(f"Reddit returned {resp.status_code} for {url}")
                return None
            return resp.json()
        except Exception as e:
            logger.debug(f"Reddit request failed: {e}")
            return None
    logger.warning(f"Reddit: exhausted {max_retries} retries for {url}")
    return None


def _extract_posts(data: dict) -> list[dict[str, Any]]:
    """Extract post data from Reddit search JSON response."""
    posts = []
    children = data.get("data", {}).get("children", [])
    for child in children:
        d = child.get("data", {})
        posts.append({
            "id": d.get("id", ""),
            "title": d.get("title", ""),
            "selftext": (d.get("selftext", "") or "")[:2000],  # cap at 2k chars
            "subreddit": d.get("subreddit", ""),
            "url": f"https://www.reddit.com{d.get('permalink', '')}",
            "score": d.get("score", 0),
            "num_comments": d.get("num_comments", 0),
            "created_utc": d.get("created_utc", 0),
        })
    return posts


def _fetch_top_comments(post_id: str, subreddit: str, limit: int = 10) -> list[dict]:
    """Fetch top comments for a post via .json endpoint."""
    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
    data = _safe_get(url)
    if not data or not isinstance(data, list) or len(data) < 2:
        return []

    comments = []
    children = data[1].get("data", {}).get("children", [])
    for child in children[:limit]:
        cd = child.get("data", {})
        body = cd.get("body", "")
        if body and body != "[deleted]" and body != "[removed]":
            comments.append({
                "body": body[:1000],
                "score": cd.get("score", 0),
                "author": cd.get("author", ""),
            })
    return comments


def scrape_reddit_for_college(
    college_name: str,
    max_posts_per_query: int = 25,
    fetch_comments: bool = True,
    top_n_for_comments: int = 5,
) -> dict[str, Any]:
    """Scrape Reddit for a college. Returns aggregated post and comment data.

    Uses cache if available.
    """
    cache_key = "reddit"
    if has_cache(college_name, cache_key):
        cached = read_cache(college_name, cache_key)
        if cached:
            logger.debug(f"Reddit cache hit for {college_name}")
            return cached

    queries = get_search_queries(college_name)
    all_posts: list[dict] = []
    seen_ids: set[str] = set()

    for query in queries:
        for sub in SUBREDDITS:
            url = f"https://www.reddit.com/r/{sub}/search.json"
            params = {
                "q": query, "sort": "top", "limit": max_posts_per_query,
                "t": "all", "restrict_sr": 1,
            }
            data = _safe_get(url, params)
            if not data:
                continue
            posts = _extract_posts(data)
            for p in posts:
                if p["id"] not in seen_ids:
                    seen_ids.add(p["id"])
                    all_posts.append(p)

        # Also search across all of Reddit (restrict_sr=0)
        url = "https://www.reddit.com/search.json"
        params = {"q": query, "sort": "top", "limit": max_posts_per_query, "t": "all"}
        data = _safe_get(url, params)
        if data:
            for p in _extract_posts(data):
                if p["id"] not in seen_ids:
                    seen_ids.add(p["id"])
                    all_posts.append(p)

    # Sort by score and fetch comments for top posts
    all_posts.sort(key=lambda x: x["score"], reverse=True)

    if fetch_comments:
        for post in all_posts[:top_n_for_comments]:
            post["top_comments"] = _fetch_top_comments(
                post["id"], post["subreddit"]
            )

    result = {
        "college": college_name,
        "total_posts": len(all_posts),
        "posts": all_posts[:100],  # cap at 100 most relevant
    }

    write_cache(college_name, cache_key, result)
    logger.info(f"Reddit: {college_name} → {len(all_posts)} posts found")
    return result

