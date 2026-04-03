"""Orchestrate scraping of official college websites.

For each college:
1. Fetch the homepage to discover navigation links.
2. Try to find and fetch section pages (placements, research, faculty, etc.).
3. Parse each section using official_parser extractors.
4. Optionally crawl individual faculty profile pages.
5. Return a flat dict to be merged with CollegePravesh data.
"""

from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup
from loguru import logger

from config.official_urls import OFFICIAL_URLS, SECTION_PATHS
from scraper.official_fetcher import fetch_official_page, discover_section_url
from scraper.official_parser import (
    parse_official_section,
    extract_faculty,
    extract_faculty_profile,
    extract_departments,
)


# Maximum number of individual faculty profile pages to crawl per college
_MAX_PROFILE_PAGES = 30

# Sections to scrape in order
_SECTIONS = [
    "placements",
    "research",
    "academics",
    "infrastructure",
    "student_life",
    "international",
]


def _build_dept_faculty(
    dept_pages: list[str],
    slug: str,
    base_url: str,
    *,
    force_refresh: bool,
    from_cache: bool,
) -> list[dict]:
    """Crawl individual department pages to collect faculty data."""
    all_faculty: list[dict] = []
    seen_names: set[str] = set()

    for dept_url in dept_pages[:15]:  # cap at 15 dept pages
        dept_soup = fetch_official_page(dept_url, slug, force_refresh=force_refresh, from_cache=from_cache)
        if dept_soup is None:
            continue
        members = extract_faculty(dept_soup, base_url=base_url)
        for m in members:
            if m.get("name") and m["name"] not in seen_names:
                seen_names.add(m["name"])
                all_faculty.append(m)

    return all_faculty


def _crawl_faculty_profiles(
    faculty_list: list[dict],
    slug: str,
    base_url: str,
    *,
    force_refresh: bool,
    from_cache: bool,
) -> list[dict]:
    """Enrich faculty dicts by visiting individual profile pages."""
    enriched: list[dict] = []
    crawled = 0
    for member in faculty_list:
        profile_url = member.get("profile_url")
        if not profile_url or crawled >= _MAX_PROFILE_PAGES:
            enriched.append(member)
            continue
        from urllib.parse import urljoin
        full_url = urljoin(base_url, profile_url)
        profile_soup = fetch_official_page(full_url, slug, force_refresh=force_refresh, from_cache=from_cache)
        if profile_soup:
            details = extract_faculty_profile(profile_soup, base_url=base_url)
            member = {**member, **{k: v for k, v in details.items() if v}}
            crawled += 1
        enriched.append(member)
    return enriched


def _group_faculty_by_dept(faculty_list: list[dict]) -> list[dict]:
    """Group flat faculty list into Department objects."""
    from collections import defaultdict
    groups: dict[str, list[dict]] = defaultdict(list)
    for m in faculty_list:
        dept = m.get("department") or "General"
        groups[dept].append({k: v for k, v in m.items() if k != "department"})

    depts: list[dict] = []
    for dept_name, members in groups.items():
        depts.append({
            "name": dept_name,
            "faculty_count": len(members),
            "faculty": members,
        })
    return depts


def scrape_official_site(
    college_name: str,
    slug: str,
    *,
    force_refresh: bool = False,
    from_cache: bool = False,
    crawl_profiles: bool = True,
) -> dict[str, Any]:
    """Scrape the official website for a college and return structured data.

    Args:
        college_name: Exact name matching OFFICIAL_URLS key.
        slug:         College slug (used for cache filenames).
        force_refresh: Re-fetch even if cached.
        from_cache:   Only use cache, no HTTP.
        crawl_profiles: Whether to follow individual faculty profile links.

    Returns:
        Dict with official-site data fields (to be merged with CP data).
    """
    base_url = OFFICIAL_URLS.get(college_name)
    if not base_url:
        logger.info(f"[{slug}] No official URL configured — skipping official scrape")
        return {}

    logger.info(f"[{slug}] Official scrape → {base_url}")
    result: dict[str, Any] = {"official_website": base_url}

    # ── Fetch homepage ────────────────────────────────────────
    homepage = fetch_official_page(base_url, slug, force_refresh=force_refresh, from_cache=from_cache)
    if homepage is None:
        logger.warning(f"[{slug}] Could not fetch official homepage")
        return result

    # ── Scrape each section ───────────────────────────────────
    for section in _SECTIONS:
        section_url = discover_section_url(
            base_url, slug, section,
            nav_soup=homepage,
            force_refresh=force_refresh,
            from_cache=from_cache,
        )
        if not section_url:
            logger.debug(f"[{slug}] Section '{section}' not found")
            continue

        soup = fetch_official_page(section_url, slug, force_refresh=force_refresh, from_cache=from_cache)
        if soup is None:
            continue

        extracted = parse_official_section(section, soup, base_url=base_url)
        result.update(extracted)
        logger.info(f"[{slug}] Extracted '{section}' section — {len(extracted)} keys")

    # ── Faculty / Departments ────────────────────────────────
    faculty_url = discover_section_url(
        base_url, slug, "faculty",
        nav_soup=homepage,
        force_refresh=force_refresh,
        from_cache=from_cache,
    )

    faculty_list: list[dict] = []

    if faculty_url:
        fac_soup = fetch_official_page(faculty_url, slug, force_refresh=force_refresh, from_cache=from_cache)
        if fac_soup:
            # Try to extract departments from this page
            dept_links_raw = fac_soup.find_all("a", href=True)
            dept_links = []
            for a in dept_links_raw:
                href = a.get("href", "")
                txt  = a.get_text(strip=True).lower()
                if any(kw in txt or kw in href.lower() for kw in ["department", "dept", "school of"]):
                    from urllib.parse import urljoin
                    dept_links.append(urljoin(base_url, href))

            if dept_links:
                faculty_list = _build_dept_faculty(
                    dept_links, slug, base_url,
                    force_refresh=force_refresh, from_cache=from_cache,
                )
            else:
                faculty_list = extract_faculty(fac_soup, base_url=base_url)

    # Enrich with profile page data
    if faculty_list and crawl_profiles:
        faculty_list = _crawl_faculty_profiles(
            faculty_list, slug, base_url,
            force_refresh=force_refresh, from_cache=from_cache,
        )

    if faculty_list:
        result["departments"] = _group_faculty_by_dept(faculty_list)
        result["total_faculty_count"] = len(faculty_list)

    # ── Rankings from official site ───────────────────────────
    rank_extracted = parse_official_section("rankings", homepage, base_url=base_url)
    result.update(rank_extracted)

    logger.info(f"[{slug}] Official scrape complete — {len(result)} total keys collected")
    return result

