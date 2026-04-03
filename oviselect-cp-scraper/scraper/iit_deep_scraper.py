"""Deep scraper for all 23 IITs.

Scrapes departments and faculty from official IIT websites.
- IIT Gandhinagar  (static HTML  – iitgn.ac.in/faculty/all)
- IIT Hyderabad    (static HTML  – iith.ac.in/people/faculty/)
- IIT BHU Varanasi (static HTML  – per-dept /dept/{code}/faculty)
- IIT Guwahati     (Playwright)
- IIT Roorkee      (Playwright)
- IIT Kanpur       (Playwright)
- IIT Kharagpur    (Playwright)
- IIT Ropar        (Playwright)
- IIT Tirupati     (Playwright)
- IIT Jodhpur      (Playwright)
- IIT Bombay       (stub – 502 at scrape time)
- IIT Delhi        (stub – connection refused at scrape time)
- IIT Madras       (stub)
- IIT Indore       (stub – 500 at scrape time)
- IIT Mandi        (stub)
- IIT Patna        (stub)
- IIT ISM Dhanbad  (stub)
- IIT Jammu        (stub)
- IIT Bhubaneswar  (stub)
- IIT Bhilai       (stub)
- IIT Goa          (stub)
- IIT Dharwad      (stub)
- IIT Palakkad     (stub)
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from loguru import logger

from scraper.fetch_utils import fetch as _scrapling_fetch
from scraper.fetch_utils import post as _scrapling_post

# ── HTTP helpers ───────────────────────────────────────────────────────────────


def _fetch(url: str, retries: int = 2, timeout: int = 20) -> BeautifulSoup | None:
    return _scrapling_fetch(url, retries=retries, timeout=timeout, verify=False)


def _clean(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def _classify_designation(text: str) -> str:
    t = text.lower()
    if "professor (hag)" in t or "hag" in t:
        return "Professor (HAG)"
    if "associate professor" in t:
        return "Associate Professor"
    if "assistant professor" in t or "asst" in t:
        return "Assistant Professor"
    if "professor" in t:
        return "Professor"
    if "lecturer" in t:
        return "Lecturer"
    if "visiting" in t:
        return "Visiting Faculty"
    if "adjunct" in t:
        return "Adjunct Faculty"
    if "emeritus" in t:
        return "Emeritus Professor"
    return text.strip()[:60]


def _make_dept(name: str, faculty: list[dict]) -> dict[str, Any]:
    d: dict[str, Any] = {"name": name}
    if faculty:
        d["faculty"] = faculty
        d["faculty_count"] = len(faculty)
    return d


# ══════════════════════════════════════════════════════════════════════════════
# IIT GANDHINAGAR
# URL: https://iitgn.ac.in/faculty/all
# Card structure: div.card-2.modal-instance > div.card__body.fac_box
#   h4 > a  → name + profile URL
#   first span  → qualifications
#   second span > strong > b → designation, text after b → department
# ══════════════════════════════════════════════════════════════════════════════

_IITGN_URL = "https://iitgn.ac.in/faculty/all"


def scrape_iit_gandhinagar() -> list[dict[str, Any]]:
    logger.info("[IIT Gandhinagar] Starting scrape from /faculty/all ...")
    soup = _fetch(_IITGN_URL, timeout=30)
    if not soup:
        logger.warning("[IIT Gandhinagar] Failed to fetch faculty page")
        return []

    cards = soup.find_all("div", class_=lambda c: c and "fac_box" in c if c else False)
    logger.info(f"[IIT Gandhinagar] Found {len(cards)} faculty cards")

    dept_map: dict[str, list[dict]] = {}

    for card in cards:
        # Name from h4 > a
        h4 = card.find("h4")
        if not h4:
            continue
        a_tag = h4.find("a", href=True)
        name = _clean(a_tag.get_text() if a_tag else h4.get_text())
        if not name:
            continue
        profile_url = a_tag["href"] if a_tag else ""
        if profile_url and not profile_url.startswith("http"):
            profile_url = urljoin(_IITGN_URL, profile_url)

        # Designation + Dept from second span > strong
        # NOTE: don't use recursive=False — the second span is not a direct child of fac_box
        spans = card.find_all("span")
        designation = ""
        dept_name = "General"
        for span in spans:
            strong = span.find("strong")
            if strong:
                b_tag = strong.find("b")
                if b_tag:
                    designation = _classify_designation(_clean(b_tag.get_text()))
                    # Department is text after the <b> tag in the strong
                    strong_text = _clean(strong.get_text())
                    b_text = _clean(b_tag.get_text())
                    after_b = strong_text.replace(b_text, "").strip().strip(",").strip()
                    if after_b and len(after_b) > 3:
                        dept_name = after_b
                break  # found the span with <strong>, stop looking

        member: dict[str, Any] = {
            "name": name,
            "designation": designation or "Faculty",
        }
        if profile_url:
            member["profile_url"] = profile_url

        dept_map.setdefault(dept_name, []).append(member)

    departments = [_make_dept(dept, fac) for dept, fac in dept_map.items()]
    total = sum(len(d.get("faculty", [])) for d in departments)
    logger.info(f"[IIT Gandhinagar] {len(departments)} depts, {total} faculty")
    return departments


# ══════════════════════════════════════════════════════════════════════════════
# IIT HYDERABAD
# URL: https://www.iith.ac.in/people/faculty/
# Card: div.filterDiv  – dept code at classes[2], name in h5
# ══════════════════════════════════════════════════════════════════════════════

_IITH_URL = "https://www.iith.ac.in/people/faculty/"

_IITH_DEPT_MAP: dict[str, str] = {
    "EE": "Electrical Engineering",
    "ME": "Mechanical & Aerospace Engineering",
    "LA": "Liberal Arts",
    "PH": "Physics",
    "CE": "Civil Engineering",
    "CSE": "Computer Science & Engineering",
    "CY": "Chemistry",
    "CH": "Chemical Engineering",
    "MS": "Materials Science & Metallurgical Engineering",
    "MA": "Mathematics",
    "BT": "Biotechnology",
    "DS": "Design",
    "BM": "Biomedical Engineering",
    "AI": "Artificial Intelligence",
    "HST": "Heritage Science and Technology",
    "EM": "Engineering Management",
    "CC": "Climate Change Studies",
    "CS": "Computer Science",
    "MSME": "Mechanical & Systems Engineering",
    "CHY": "Chemistry",
}


def scrape_iit_hyderabad() -> list[dict[str, Any]]:
    logger.info("[IIT Hyderabad] Starting scrape from /people/faculty/ ...")
    soup = _fetch(_IITH_URL, timeout=30)
    if not soup:
        logger.warning("[IIT Hyderabad] Failed to fetch faculty page")
        return []

    cards = soup.find_all("div", class_=lambda c: c and "filterDiv" in c if c else False)
    logger.info(f"[IIT Hyderabad] Found {len(cards)} filterDiv cards")

    dept_map: dict[str, list[dict]] = {}

    for card in cards:
        classes = card.get("class", [])
        # Dept code is at index 2 (filterDiv, A0/A1/A2, DEPT_CODE, ...)
        dept_code = classes[2].upper() if len(classes) >= 3 else ""
        # Unknown dept codes go to "General" rather than showing the raw code
        dept_name = _IITH_DEPT_MAP.get(dept_code, "General")

        # Name from h5
        h5 = card.find("h5")
        if not h5:
            continue
        name = _clean(h5.get_text())
        # Skip if it doesn't look like a person's name (must have a space, e.g. First Last)
        if not name or len(name) < 3 or " " not in name:
            continue

        # Profile URL
        a_tag = card.find("a", href=True)
        profile_url = ""
        if a_tag:
            href = a_tag["href"]
            if href and not href.startswith("http"):
                profile_url = urljoin(_IITH_URL, href)
            else:
                profile_url = href

        member: dict[str, Any] = {"name": name, "designation": "Faculty"}
        if profile_url:
            member["profile_url"] = profile_url

        dept_map.setdefault(dept_name, []).append(member)

    departments = [_make_dept(dept, fac) for dept, fac in dept_map.items()]
    total = sum(len(d.get("faculty", [])) for d in departments)
    logger.info(f"[IIT Hyderabad] {len(departments)} depts, {total} faculty")
    return departments


# ══════════════════════════════════════════════════════════════════════════════
# IIT BHU VARANASI
# URL pattern: https://www.iitbhu.ac.in/dept/{code}/faculty
# Card: div.card.profile-card-3  →  name in h6.card-text, designation in text
# ══════════════════════════════════════════════════════════════════════════════

_IITBHU_BASE = "https://www.iitbhu.ac.in"

_IITBHU_DEPARTMENTS: dict[str, str] = {
    "apd": "Applied Physics",
    "bce": "Biochemical Engineering",
    "bme": "Biomedical Engineering",
    "cer": "Ceramic Engineering",
    "che": "Chemical Engineering",
    "chy": "Chemistry",
    "civ": "Civil Engineering",
    "cse": "Computer Science & Engineering",
    "dse": "Data Science & Engineering",
    "ece": "Electronics Engineering",
    "eee": "Electrical Engineering",
    "hss": "Humanities & Social Sciences",
    "mat": "Mathematics",
    "mec": "Mechanical Engineering",
    "met": "Metallurgical Engineering",
    "min": "Mining Engineering",
    "mst": "Materials Science & Technology",
    "phe": "Pharmaceutical Engineering",
    "phy": "Physics",
}


def _scrape_iitbhu_dept(dept_name: str, slug: str) -> dict[str, Any]:
    url = f"{_IITBHU_BASE}/dept/{slug}/faculty"
    soup = _fetch(url, timeout=20)
    if not soup:
        return {"name": dept_name}

    cards = soup.find_all("div", class_=lambda c: c and "profile-card-3" in c)
    faculty = []
    for card in cards:
        # Name: h6 > a > b  (structure: <h6 class="card-text text-left"><a href="..."><b>Name</b></a></h6>)
        h6 = card.find("h6")
        if not h6:
            continue
        a_tag = h6.find("a", href=True)
        name = _clean(a_tag.get_text() if a_tag else h6.get_text())
        if not name or len(name) < 3:
            continue
        profile_url = ""
        if a_tag:
            href = a_tag["href"]
            profile_url = href if href.startswith("http") else urljoin(_IITBHU_BASE, href)

        # Designation from the second div.card-text > b tag
        # Structure: <div class="card-text text-left" style="font-size:12px"><b> Professor & HoD </b></div>
        card_content = card.find("div", class_=lambda c: c and "card-content" in c)
        designation = "Faculty"
        email = ""
        if card_content:
            text_divs = card_content.find_all("div", class_=lambda c: c and "card-text" in c)
            for div in text_divs:
                b_tag = div.find("b")
                if b_tag:
                    t = _clean(b_tag.get_text())
                    if t and any(k in t.lower() for k in ("professor", "lecturer", "visiting", "adjunct", "emeritus", "hod", "head")):
                        designation = _classify_designation(t)
                        break
                # Check for email in text divs
                div_text = _clean(div.get_text())
                if "@" in div_text and ("iitbhu" in div_text.lower() or "itbhu" in div_text.lower()):
                    email = div_text.replace("Email.:", "").strip()

        member: dict[str, Any] = {"name": name, "designation": designation}
        if profile_url:
            member["profile_url"] = profile_url
        if email:
            member["email"] = email
        faculty.append(member)

    logger.info(f"[IIT BHU] {dept_name}: {len(faculty)} faculty")
    return _make_dept(dept_name, faculty)


def scrape_iit_bhu() -> list[dict[str, Any]]:
    logger.info("[IIT BHU] Starting per-dept scrape ...")
    departments = []
    for slug, dept_name in _IITBHU_DEPARTMENTS.items():
        try:
            dept = _scrape_iitbhu_dept(dept_name, slug)
            departments.append(dept)
            time.sleep(0.8)
        except Exception as exc:
            logger.error(f"[IIT BHU] {dept_name}: {exc}")
            departments.append({"name": dept_name})
    total = sum(len(d.get("faculty", [])) for d in departments)
    logger.info(f"[IIT BHU] Done – {len(departments)} depts, {total} faculty")
    return departments


# ══════════════════════════════════════════════════════════════════════════════
# GENERIC PLAYWRIGHT HELPER
# Used by JS-heavy IITs where static HTML yields an empty DOM
# ══════════════════════════════════════════════════════════════════════════════

# Common CSS selectors tried in priority order when scraping an unknown IIT
_PW_FACULTY_SELECTORS = [
    "div.faculty-card",
    "div.faculty-member",
    "div.person-card",
    "div.staff-card",
    "div.people-card",
    "article.faculty",
    "li.faculty-item",
    "div.team-member",
    "div.card-body",
    "div.profile-card",
    "div[class*='faculty']",
    "div[class*='person']",
    "div[class*='staff']",
    "div[class*='people']",
]


async def _pw_scrape_generic(
    url: str,
    label: str,
    wait_selector: str | None = None,
    extra_wait: int = 6,
) -> list[dict[str, Any]]:
    """Generic Playwright-based faculty scraper.

    Tries common card selectors after rendering.  Returns a flat list of
    faculty dicts (not department-grouped) because the dept structure is
    unknown for fully-JS sites.
    """
    from playwright.async_api import async_playwright

    faculty: list[dict[str, Any]] = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent=_HEADERS["User-Agent"],
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        )
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
            if wait_selector:
                try:
                    await page.wait_for_selector(wait_selector, timeout=15_000)
                except Exception:
                    pass
            else:
                await asyncio.sleep(extra_wait)

            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")

            # Try each selector until we find cards
            cards = []
            for sel in _PW_FACULTY_SELECTORS:
                tag, _, cls = sel.partition(".")
                if "[" in sel:
                    # attribute selector — use find_all with attrs
                    attr_part = sel.split("[")[1].rstrip("]")
                    attr, _, val = attr_part.partition("*=")
                    val = val.strip("'\"")
                    cards = soup.find_all(lambda t, a=attr, v=val: t.has_attr(a) and v in t[a])
                elif "." in sel:
                    cards = soup.find_all(tag or True, class_=lambda c: c and cls in c)
                else:
                    cards = soup.find_all(tag)
                if len(cards) >= 3:
                    logger.info(f"[{label}] Selector '{sel}' matched {len(cards)} cards")
                    break

            for card in cards:
                # Try h3/h4/h5/h6 for name
                for htag in ["h3", "h4", "h5", "h6", "strong"]:
                    el = card.find(htag)
                    if el:
                        name = _clean(el.get_text())
                        if name and 3 < len(name) < 80:
                            # Try to get designation from next sibling text
                            desg_el = el.find_next_sibling(["p", "span", "small", "div"])
                            designation = "Faculty"
                            if desg_el:
                                desg_text = _clean(desg_el.get_text())
                                if any(k in desg_text.lower() for k in ("professor", "lecturer", "faculty")):
                                    designation = _classify_designation(desg_text)
                            a_tag = card.find("a", href=True)
                            member: dict[str, Any] = {"name": name, "designation": designation}
                            if a_tag:
                                href = a_tag["href"]
                                if href and not href.startswith("javascript"):
                                    member["profile_url"] = href if href.startswith("http") else urljoin(url, href)
                            faculty.append(member)
                            break
        except Exception as exc:
            logger.error(f"[{label}] Playwright error: {exc}")
        finally:
            await browser.close()

    logger.info(f"[{label}] Playwright scraped {len(faculty)} faculty from {url}")
    return faculty


def _pw_result_to_departments(faculty: list[dict], default_dept: str = "Faculty") -> list[dict[str, Any]]:
    """Wrap a flat faculty list into a single department dict."""
    if not faculty:
        return []
    return [_make_dept(default_dept, faculty)]


# ══════════════════════════════════════════════════════════════════════════════
# IIT ROORKEE  (Playwright)
# ══════════════════════════════════════════════════════════════════════════════

def scrape_iit_roorkee() -> list[dict[str, Any]]:
    logger.info("[IIT Roorkee] Starting Playwright scrape ...")
    try:
        faculty = asyncio.run(
            _pw_scrape_generic(
                "https://www.iitr.ac.in/faculty/en",
                "IIT Roorkee",
                extra_wait=8,
            )
        )
    except Exception as exc:
        logger.error(f"[IIT Roorkee] {exc}")
        faculty = []
    return _pw_result_to_departments(faculty, "Faculty")


# ══════════════════════════════════════════════════════════════════════════════
# IIT KANPUR  (Playwright)
# ══════════════════════════════════════════════════════════════════════════════

def scrape_iit_kanpur() -> list[dict[str, Any]]:
    logger.info("[IIT Kanpur] Starting Playwright scrape ...")
    try:
        faculty = asyncio.run(
            _pw_scrape_generic(
                "https://www.iitk.ac.in/academic-faculty",
                "IIT Kanpur",
                extra_wait=8,
            )
        )
    except Exception as exc:
        logger.error(f"[IIT Kanpur] {exc}")
        faculty = []
    return _pw_result_to_departments(faculty, "Faculty")


# ══════════════════════════════════════════════════════════════════════════════
# IIT KHARAGPUR  (Playwright – has loading-state div)
# ══════════════════════════════════════════════════════════════════════════════

def scrape_iit_kharagpur() -> list[dict[str, Any]]:
    logger.info("[IIT Kharagpur] Starting Playwright scrape ...")
    try:
        faculty = asyncio.run(
            _pw_scrape_generic(
                "https://www.iitkgp.ac.in/faculty",
                "IIT Kharagpur",
                wait_selector=".faculty-card, .person-card, .loading-div",
                extra_wait=10,
            )
        )
    except Exception as exc:
        logger.error(f"[IIT Kharagpur] {exc}")
        faculty = []
    return _pw_result_to_departments(faculty, "Faculty")


# ══════════════════════════════════════════════════════════════════════════════
# IIT GUWAHATI  (Static – POST to /resources/model/faculty-fetch)
# Card: div.left.media.bg-white → name in h3>a, designation in span.text-dark
# ══════════════════════════════════════════════════════════════════════════════

_IITG_BASE = "https://www.iitg.ac.in"
_IITG_FETCH_URL = "https://www.iitg.ac.in/resources/model/faculty-fetch"


def scrape_iit_guwahati() -> list[dict[str, Any]]:
    logger.info("[IIT Guwahati] Fetching from faculty-fetch endpoint ...")
    soup = _scrapling_post(_IITG_FETCH_URL, timeout=30, verify=False)
    if not soup:
        logger.warning("[IIT Guwahati] POST to faculty-fetch endpoint returned no data")
        return []

    cards = soup.find_all(
        "div",
        class_=lambda c: c and "left" in c and "media" in c if c else False,
    )
    logger.info(f"[IIT Guwahati] Found {len(cards)} faculty cards")

    faculty: list[dict[str, Any]] = []
    for card in cards:
        # Name from h3 > a
        h3 = card.find("h3")
        if not h3:
            continue
        a_tag = h3.find("a", href=True)
        name = _clean(a_tag.get_text() if a_tag else h3.get_text())
        if not name or len(name) < 3:
            continue

        # Profile URL
        profile_url = ""
        if a_tag:
            href = a_tag["href"]
            if href and not href.startswith("http"):
                href = f"{_IITG_BASE}/{href.lstrip('/')}"
            profile_url = href

        # Designation from span.text-dark
        designation = "Faculty"
        span_dark = card.find("span", class_=lambda c: c and "text-dark" in c if c else False)
        if span_dark:
            t = _clean(span_dark.get_text())
            if t:
                designation = _classify_designation(t)

        member: dict[str, Any] = {"name": name, "designation": designation}
        if profile_url:
            member["profile_url"] = profile_url
        faculty.append(member)

    departments = _pw_result_to_departments(faculty, "Faculty")
    total = sum(len(d.get("faculty", [])) for d in departments)
    logger.info(f"[IIT Guwahati] {total} faculty scraped")
    return departments


# ══════════════════════════════════════════════════════════════════════════════
# IIT ROPAR  (Playwright – confirmed JS-rendered)
# ══════════════════════════════════════════════════════════════════════════════

def scrape_iit_ropar() -> list[dict[str, Any]]:
    logger.info("[IIT Ropar] Starting Playwright scrape ...")
    try:
        faculty = asyncio.run(
            _pw_scrape_generic(
                "https://www.iitrpr.ac.in/faculty",
                "IIT Ropar",
                extra_wait=8,
            )
        )
    except Exception as exc:
        logger.error(f"[IIT Ropar] {exc}")
        faculty = []
    return _pw_result_to_departments(faculty, "Faculty")


# ══════════════════════════════════════════════════════════════════════════════
# IIT TIRUPATI  (Playwright – confirmed JS-rendered)
# ══════════════════════════════════════════════════════════════════════════════

def scrape_iit_tirupati() -> list[dict[str, Any]]:
    logger.info("[IIT Tirupati] Starting Playwright scrape ...")
    try:
        faculty = asyncio.run(
            _pw_scrape_generic(
                "https://www.iittirupati.ac.in/faculty",
                "IIT Tirupati",
                extra_wait=8,
            )
        )
    except Exception as exc:
        logger.error(f"[IIT Tirupati] {exc}")
        faculty = []
    return _pw_result_to_departments(faculty, "Faculty")


# ══════════════════════════════════════════════════════════════════════════════
# IIT JODHPUR  (Playwright – 5KB shell page, JS-rendered)
# ══════════════════════════════════════════════════════════════════════════════

def scrape_iit_jodhpur() -> list[dict[str, Any]]:
    logger.info("[IIT Jodhpur] Starting Playwright scrape ...")
    try:
        faculty = asyncio.run(
            _pw_scrape_generic(
                "https://iitj.ac.in/people/faculty",
                "IIT Jodhpur",
                extra_wait=8,
            )
        )
    except Exception as exc:
        logger.error(f"[IIT Jodhpur] {exc}")
        faculty = []
    return _pw_result_to_departments(faculty, "Faculty")


# ══════════════════════════════════════════════════════════════════════════════
# IIT BOMBAY  (stub – 502 at scrape time; Playwright fallback)
# ══════════════════════════════════════════════════════════════════════════════

def scrape_iit_bombay() -> list[dict[str, Any]]:
    logger.info("[IIT Bombay] Trying Playwright scrape (site had 502 on static fetch) ...")
    try:
        faculty = asyncio.run(
            _pw_scrape_generic(
                "https://www.iitb.ac.in/en/education/faculty",
                "IIT Bombay",
                extra_wait=10,
            )
        )
    except Exception as exc:
        logger.error(f"[IIT Bombay] {exc}")
        faculty = []
    return _pw_result_to_departments(faculty, "Faculty")


# ══════════════════════════════════════════════════════════════════════════════
# IIT DELHI  (Playwright – connection refused on static fetch)
# ══════════════════════════════════════════════════════════════════════════════

def scrape_iit_delhi() -> list[dict[str, Any]]:
    logger.info("[IIT Delhi] Trying Playwright scrape ...")
    try:
        faculty = asyncio.run(
            _pw_scrape_generic(
                "https://home.iitd.ac.in/faculty-iitd.php",
                "IIT Delhi",
                extra_wait=8,
            )
        )
    except Exception as exc:
        logger.error(f"[IIT Delhi] {exc}")
        faculty = []
    return _pw_result_to_departments(faculty, "Faculty")


# ══════════════════════════════════════════════════════════════════════════════
# IIT MADRAS  (Playwright)
# ══════════════════════════════════════════════════════════════════════════════

def scrape_iit_madras() -> list[dict[str, Any]]:
    logger.info("[IIT Madras] Trying Playwright scrape ...")
    try:
        faculty = asyncio.run(
            _pw_scrape_generic(
                "https://www.iitm.ac.in/research/faculty",
                "IIT Madras",
                extra_wait=8,
            )
        )
    except Exception as exc:
        logger.error(f"[IIT Madras] {exc}")
        faculty = []
    return _pw_result_to_departments(faculty, "Faculty")


# ══════════════════════════════════════════════════════════════════════════════
# REMAINING IITs  (Playwright best-effort stubs)
# ══════════════════════════════════════════════════════════════════════════════

def _pw_stub(label: str, url: str) -> list[dict[str, Any]]:
    logger.info(f"[{label}] Playwright stub scrape ...")
    try:
        faculty = asyncio.run(_pw_scrape_generic(url, label, extra_wait=8))
    except Exception as exc:
        logger.error(f"[{label}] {exc}")
        faculty = []
    return _pw_result_to_departments(faculty, "Faculty")


def scrape_iit_indore() -> list[dict[str, Any]]:
    return _pw_stub("IIT Indore", "https://www.iiti.ac.in/people/faculty")


def scrape_iit_mandi() -> list[dict[str, Any]]:
    return _pw_stub("IIT Mandi", "https://www.iitmandi.ac.in/people/faculty")


def scrape_iit_patna() -> list[dict[str, Any]]:
    return _pw_stub("IIT Patna", "https://www.iitp.ac.in/index.php/en-us/academics/faculties")


# ══════════════════════════════════════════════════════════════════════════════
# IIT ISM DHANBAD  (Static – /all-faculty, div.event-box-campus cards)
# Card: div.event-box-campus → name in h3, dept+designation in p (br-separated)
# ══════════════════════════════════════════════════════════════════════════════

_IITISM_ALL_FACULTY_URL = "https://www.iitism.ac.in/all-faculty"


def scrape_iit_ism() -> list[dict[str, Any]]:
    logger.info("[IIT ISM Dhanbad] Fetching from /all-faculty ...")
    soup = _fetch(_IITISM_ALL_FACULTY_URL, timeout=30)
    if not soup:
        logger.warning("[IIT ISM Dhanbad] Failed to fetch; falling back to Playwright stub")
        return _pw_stub("IIT ISM Dhanbad", "https://www.iitism.ac.in/faculty")

    cards = soup.find_all("div", class_=lambda c: c and "event-box-campus" in c if c else False)
    logger.info(f"[IIT ISM Dhanbad] Found {len(cards)} faculty cards")

    dept_map: dict[str, list[dict]] = {}
    for card in cards:
        # Name from h3 (e.g. " Prof. A Antony Selvan")
        h3 = card.find("h3")
        if not h3:
            continue
        raw_name = _clean(h3.get_text())
        # Strip honorifics
        name = re.sub(r"^(Dr\.?|Prof\.?|Mr\.?|Ms\.?|Mrs\.?)\s+", "", raw_name).strip()
        if not name or len(name) < 3:
            continue

        # Dept + Designation from <p> tag with <br/> separator
        # e.g. "Mathematics & Computing\nAssistant Professor"
        dept_name = "General"
        designation = "Faculty"
        p_tag = card.find("p")
        if p_tag:
            # Replace <br> with newline, then split
            for br in p_tag.find_all("br"):
                br.replace_with("\n")
            parts = [s.strip() for s in p_tag.get_text().split("\n") if s.strip()]
            if parts:
                dept_name = parts[0]
            if len(parts) > 1:
                designation = _classify_designation(parts[1])

        # Profile URL from a.view-more
        profile_url = ""
        a_tag = card.find("a", class_=lambda c: c and "view-more" in c if c else False)
        if not a_tag:
            a_tag = card.find("a", href=True)
        if a_tag:
            href = a_tag.get("href", "")
            if href and not href.startswith("http"):
                href = urljoin("https://www.iitism.ac.in/", href)
            profile_url = href

        member: dict[str, Any] = {"name": name, "designation": designation}
        if profile_url:
            member["profile_url"] = profile_url
        dept_map.setdefault(dept_name, []).append(member)

    departments = [_make_dept(dept, fac) for dept, fac in dept_map.items()]
    total = sum(len(d.get("faculty", [])) for d in departments)
    logger.info(f"[IIT ISM Dhanbad] {len(departments)} depts, {total} faculty")
    return departments


def scrape_iit_jammu() -> list[dict[str, Any]]:
    return _pw_stub("IIT Jammu", "https://www.iitjammu.ac.in/people/faculty")


def scrape_iit_bhubaneswar() -> list[dict[str, Any]]:
    return _pw_stub("IIT Bhubaneswar", "https://www.iitbbs.ac.in/people/faculty")


def scrape_iit_bhilai() -> list[dict[str, Any]]:
    return _pw_stub("IIT Bhilai", "https://www.iitbhilai.ac.in/index.php?pid=faculty")


def scrape_iit_goa() -> list[dict[str, Any]]:
    return _pw_stub("IIT Goa", "https://www.iitgoa.ac.in/index.php/faculty")


# ══════════════════════════════════════════════════════════════════════════════
# IIT DHARWAD  (Static – /faculty, Drupal views-row structure)
# Card: div.views-row → name in first text, dept+designation in second text
# ══════════════════════════════════════════════════════════════════════════════

_IITDH_BASE = "https://www.iitdh.ac.in"
_IITDH_FACULTY_URL = "https://www.iitdh.ac.in/faculty"


def scrape_iit_dharwad() -> list[dict[str, Any]]:
    logger.info("[IIT Dharwad] Fetching from /faculty ...")
    soup = _fetch(_IITDH_FACULTY_URL, timeout=25)
    if not soup:
        logger.warning("[IIT Dharwad] Failed to fetch faculty page")
        return []

    rows = soup.find_all("div", class_=lambda c: c and "views-row" in c if c else False)
    logger.info(f"[IIT Dharwad] Found {len(rows)} views-row entries")

    # Debug-comment keywords injected by Drupal's theme debug mode
    _DEBUG_MARKERS = ("THEME", "OUTPUT", "BEGIN", "END", "CUSTOM", "<!--", "💡")

    dept_map: dict[str, list[dict]] = {}
    for row in rows:
        # Collect all non-empty text nodes, filtering out Drupal theme-debug comments
        all_texts = [
            t.strip() for t in row.find_all(string=True)
            if t.strip() and len(t.strip()) > 2
            and not any(kw in t for kw in _DEBUG_MARKERS)
        ]
        if not all_texts:
            continue

        # First meaningful text is the name (e.g. "Prof Abhijit Kshirsagar")
        raw_name = all_texts[0]
        # Strip academic titles (case-insensitive, handles typos like "PRof")
        name = re.sub(r"^(Dr\.?|Prof\.?|Mr\.?|Ms\.?|Mrs\.?)\s*", "", raw_name, flags=re.IGNORECASE).strip()
        # IIT Dharwad uses [Ms]/[Mr] gender markers — strip them after the title
        name = re.sub(r"^\[(Ms|Mr|Mrs)\]\s*", "", name, flags=re.IGNORECASE).strip()
        if not name or len(name) < 3 or not any(v in name.lower() for v in "aeiou"):
            continue
        # Skip rows where the name still contains non-name artefact characters
        if any(ch in name for ch in "{}|<>"):
            continue

        # Second text has "Designation, Department (Abbreviation)"
        designation = "Faculty"
        dept_name = "General"
        if len(all_texts) > 1:
            second = all_texts[1]
            # Split on first comma: "Assistant Professor,  Electrical, Electronics..."
            comma_idx = second.find(",")
            if comma_idx > 0:
                designation = _classify_designation(second[:comma_idx].strip())
                dept_raw = second[comma_idx + 1:].strip()
                # Remove trailing abbreviations in parentheses e.g. "(EECE)"
                dept_name = re.sub(r"\s*\([^)]{1,10}\)\s*$", "", dept_raw).strip() or dept_raw
                # If dept still has junk characters (lien artefacts etc.), fall back to General
                if any(ch in dept_name for ch in "{}[]|<>") or "on-lien" in dept_name.lower():
                    dept_name = "General"
            else:
                designation = _classify_designation(second)

        # Profile URL: prefer /node/ link, fallback to personal page
        profile_url = ""
        for a_tag in row.find_all("a", href=True):
            href = a_tag["href"]
            if not href or href.startswith("mailto:"):
                continue
            if not href.startswith("http"):
                href = urljoin(_IITDH_BASE, href)
            if "/node/" in href or "iitdh.ac.in" in href:
                profile_url = href
                break

        member: dict[str, Any] = {"name": name, "designation": designation}
        if profile_url:
            member["profile_url"] = profile_url
        dept_map.setdefault(dept_name, []).append(member)

    departments = [_make_dept(dept, fac) for dept, fac in dept_map.items()]
    total = sum(len(d.get("faculty", [])) for d in departments)
    logger.info(f"[IIT Dharwad] {len(departments)} depts, {total} faculty")
    return departments


def scrape_iit_palakkad() -> list[dict[str, Any]]:
    return _pw_stub("IIT Palakkad", "https://iitpkd.ac.in/people/faculty")


# ══════════════════════════════════════════════════════════════════════════════
# REGISTRY + ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

_SCRAPER_REGISTRY: dict[str, Any] = {
    "iit-gandhinagar":  scrape_iit_gandhinagar,
    "iit-hyderabad":    scrape_iit_hyderabad,
    "iit-bhu-varanasi": scrape_iit_bhu,
    "iit-roorkee":      scrape_iit_roorkee,
    "iit-kanpur":       scrape_iit_kanpur,
    "iit-kharagpur":    scrape_iit_kharagpur,
    "iit-guwahati":     scrape_iit_guwahati,
    "iit-ropar":        scrape_iit_ropar,
    "iit-tirupati":     scrape_iit_tirupati,
    "iit-jodhpur":      scrape_iit_jodhpur,
    "iit-bombay":       scrape_iit_bombay,
    "iit-delhi":        scrape_iit_delhi,
    "iit-madras":       scrape_iit_madras,
    "iit-indore":       scrape_iit_indore,
    "iit-mandi":        scrape_iit_mandi,
    "iit-patna":        scrape_iit_patna,
    "iit-ism-dhanbad":  scrape_iit_ism,
    "iit-jammu":        scrape_iit_jammu,
    "iit-bhubaneswar":  scrape_iit_bhubaneswar,
    "iit-bhilai":       scrape_iit_bhilai,
    "iit-goa":          scrape_iit_goa,
    "iit-dharwad":      scrape_iit_dharwad,
    "iit-palakkad":     scrape_iit_palakkad,
}


def _find_json_file(parsed_dir: Path, slug: str) -> Path | None:
    slug_clean = slug.lower().replace("-", "")
    for f in parsed_dir.glob("*_structured.json"):
        name = f.stem.replace("_structured", "").lower().replace("-", "").replace("_", "")
        if slug_clean in name or name in slug_clean:
            return f
    return None


def _merge_departments(existing: list, scraped: list) -> list:
    existing = existing or []
    scraped = scraped or []
    existing_by_name = {d.get("name", "").lower(): d for d in existing if d}
    for dept in scraped:
        key = dept.get("name", "").lower()
        if key in existing_by_name:
            if dept.get("faculty"):
                existing_by_name[key]["faculty"] = dept["faculty"]
                existing_by_name[key]["faculty_count"] = dept.get("faculty_count", len(dept["faculty"]))
        else:
            existing_by_name[key] = dept
    return list(existing_by_name.values())


def run_all_scrapers(parsed_dir: str | None = None, target: str | None = None) -> None:
    """Run all IIT scrapers and update the corresponding _structured.json files."""
    if parsed_dir is None:
        here = Path(__file__).parent
        parsed_dir_path = here.parent / "data" / "parsed"
    else:
        parsed_dir_path = Path(parsed_dir)

    registry = {target: _SCRAPER_REGISTRY[target]} if target else _SCRAPER_REGISTRY

    for slug, scraper_fn in registry.items():
        logger.info(f"\n{'='*60}\nRunning scraper: {slug}\n{'='*60}")
        try:
            departments = scraper_fn()
        except Exception as exc:
            logger.error(f"Scraper {slug} crashed: {exc}")
            continue

        if not departments:
            logger.warning(f"No data returned for {slug}")
            continue

        json_file = _find_json_file(parsed_dir_path, slug)
        if not json_file:
            logger.warning(f"No JSON file found for {slug} in {parsed_dir_path}")
            available = [f.name for f in parsed_dir_path.glob("*_structured.json")]
            logger.info(f"  Available files: {available[:10]}")
            continue

        with open(json_file, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        existing_depts = data.get("departments") or []
        merged = _merge_departments(existing_depts, departments)
        data["departments"] = merged
        data["department_count"] = len(merged)
        total_fac = sum(len(d.get("faculty", [])) for d in merged)
        data["total_faculty"] = total_fac

        with open(json_file, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)

        logger.info(f"✅ Updated {json_file.name}: {len(merged)} depts, {total_fac} faculty total")


if __name__ == "__main__":
    import sys
    target_slug = sys.argv[1] if len(sys.argv) > 1 else None
    run_all_scrapers(target=target_slug)

