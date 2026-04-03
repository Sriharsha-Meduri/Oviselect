"""Deep scraper for SVNIT (Sardar Vallabhbhai NIT, Surat).

Crawls all 12 departments from their official sub-pages:
  hod-message.php  → HoD name / designation
  faculty.php (or faculty-achievements.php) → full faculty list
  project.php / research.php → R&D projects
  laboratories.php → lab names
  patents.php → patent list
  publication.php → publications count

Returns a list of Department dicts compatible with the CollegeInfo schema.
"""

from __future__ import annotations

import re
import time
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from loguru import logger

# ── Department registry ───────────────────────────────────────────────────────

SVNIT_BASE = "https://www.svnit.ac.in"

DEPARTMENTS: dict[str, dict[str, str]] = {
    "Artificial Intelligence": {
        "base": f"{SVNIT_BASE}/web/department/ai/",
        "faculty": "faculty.php",
        "hod": "hod-message.php",
        "labs": "laboratories.php",
    },
    "Chemical Engineering": {
        "base": f"{SVNIT_BASE}/web/department/chemical/",
        "faculty": "faculty.php",
        "hod": "hod-message.php",
        "research": "project.php",
        "labs": "laboratories.php",
        "patents": "patents.php",
        "publications": "publication.php",
    },
    "Chemistry": {
        "base": f"{SVNIT_BASE}/web/department/chemistry/",
        "faculty": "faculty.php",
        "hod": "hod-message.php",
        "research": "project.php",
        "labs": "laboratories.php",
        "patents": "patents.php",
        "publications": "publication.php",
    },
    "Civil Engineering": {
        "base": f"{SVNIT_BASE}/web/department/civil/",
        "faculty": "faculty.php",
        "hod": "hod-message.php",
        "research": "research.php",
        "labs": "laboratories.php",
        "publications": "publication.php",
    },
    "Computer Science and Engineering": {
        "base": f"{SVNIT_BASE}/web/department/computer/",
        "faculty": "faculty.php",
        "hod": "hod-message.php",
        "research": "rd-projects.php",
        "labs": "laboratories.php",
        "patents": "patent-detail.php",
        "publications": "faculty-achievement.php",
    },
    "Electrical Engineering": {
        "base": f"{SVNIT_BASE}/web/department/Electrical/",
        "faculty": "faculty.php",
        "hod": "hod-message.php",
        "research": "research.php",
        "labs": "laboratories.php",
        "patents": "patent.php",
        "publications": "publication.php",
    },
    "Electronics Engineering": {
        "base": f"{SVNIT_BASE}/web/department/Electronics/",
        "faculty": "faculty.php",
        "hod": "hod-message.php",
        "research": "project-new.php",
        "labs": "laboratories.php",
        "patents": "patents.php",
        "publications": "journals.php",
    },
    "Humanities and Social Sciences": {
        "base": f"{SVNIT_BASE}/web/department/humanities/",
        "faculty": "faculty.php",
        "hod": "hod-message.php",
    },
    "Management Studies": {
        "base": f"{SVNIT_BASE}/web/department/management/",
        "hod": "hod-message.php",
        "faculty": "faculty.php",
    },
    "Mathematics": {
        "base": f"{SVNIT_BASE}/web/department/maths/",
        "faculty": "faculty.php",
        "hod": "hod-message.php",
        "research": "project.php",
        "labs": "laboratories.php",
        "patents": "patents.php",
        "publications": "publication.php",
    },
    "Mechanical Engineering": {
        "base": f"{SVNIT_BASE}/web/department/Mechanical/",
        "faculty": "faculty.php",
        "hod": "hod-message.php",
        "research": "project.php",
        "patents": "patent.php",
    },
    "Physics": {
        "base": f"{SVNIT_BASE}/web/department/physics/",
        "faculty": "faculty.php",
        "hod": "hod-message.php",
        "research": "project.php",
        "labs": "laboratories.php",
        "patents": "patent.php",
        "publications": "publication_journal.php",
    },
}

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# ── HTTP helpers ──────────────────────────────────────────────────────────────


def _fetch(url: str, retries: int = 2) -> BeautifulSoup | None:
    """Fetch a URL and return BeautifulSoup, or None on failure."""
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers=_HEADERS, timeout=20)
            if r.status_code == 200:
                return BeautifulSoup(r.text, "html.parser")
            logger.warning(f"[SVNIT] HTTP {r.status_code} for {url}")
            return None
        except Exception as exc:
            if attempt < retries:
                time.sleep(2)
            else:
                logger.warning(f"[SVNIT] Failed to fetch {url}: {exc}")
    return None


def _decode_email(raw: str) -> str:
    """Convert SVNIT obfuscated email like 'dcj[at]svnit[dot]ac[dot]in'."""
    return raw.replace("[at]", "@").replace("[dot]", ".").strip()


# ── Helper: extract name + designation from an info-column div ────────────────

_SKIP_TEXTS = {"webpage", "pdf", "profile", ""}


def _parse_info_div(info_div: BeautifulSoup, group: str) -> dict[str, Any]:
    """Parse the right-column (info) div of one faculty row."""
    member: dict[str, Any] = {}

    # ── Name ─────────────────────────────────────────────────────
    # May have several <h4 class="author-name"> – first non-link one is the name
    for h4 in info_div.find_all("h4", class_="author-name"):
        txt = h4.get_text(strip=True)
        if txt.lower() not in _SKIP_TEXTS and len(txt) > 3:
            member["name"] = txt
            break

    if not member.get("name"):
        return member

    # ── Profile URL ───────────────────────────────────────────────
    # Find an <a> inside any "Webpage" h4, or in name h4 itself
    for h4 in info_div.find_all("h4", class_="author-name"):
        a = h4.find("a", href=True)
        if a:
            href = a["href"]
            txt = h4.get_text(strip=True).lower()
            if txt in _SKIP_TEXTS or "scholar.google" in href or "http" in href:
                member["profile_url"] = href
                break

    # ── Designation & Research Area from <p> tags ─────────────────
    for p in info_div.find_all("p"):
        if "author-name" in p.get("class", []):
            continue  # skip webpage / pdf <p> labels

        # Check for research area first (has <b>Research Area:</b>)
        b_tag = p.find("b")
        if b_tag and "research" in b_tag.get_text(strip=True).lower():
            import copy
            p_copy = copy.copy(p)
            for b in p_copy.find_all("b"):
                b.decompose()
            research_text = p_copy.get_text(separator=" ", strip=True)
            research_text = re.sub(r"^[:\-\s]+", "", research_text).strip()
            areas = [a.strip() for a in re.split(r"[,;]", research_text)
                     if a.strip() and len(a.strip()) > 2]
            if areas:
                member["specializations"] = areas
        elif not member.get("designation"):
            # First plain <p> has "Professor, Ph. D." pattern
            p_text = p.get_text(separator=" ", strip=True)
            parts = [x.strip() for x in p_text.split(",")]
            desig = parts[0] if parts else ""
            if desig and len(desig) > 1:
                member["designation"] = desig
                if len(parts) > 1:
                    qual = parts[1].strip()
                    if qual:
                        member["qualifications"] = [{"degree": qual}]

    # ── Email ─────────────────────────────────────────────────────
    for strong in info_div.find_all("strong"):
        txt = strong.get_text(strip=True)
        if "[at]" in txt or "@" in txt:
            member["email"] = _decode_email(txt)
            break

    if not member.get("designation"):
        member["designation"] = group

    return member


# ── HoD extraction ─────────────────────────────────────────────────────────────

# Known designation keywords — used to validate/clean extracted strings
_DESIG_KEYWORDS = re.compile(
    r"^(Professor|Associate Professor|Assistant Professor|Head of Department|"
    r"HoD|Lecturer|Principal|Director|Visiting Faculty)",
    re.IGNORECASE,
)


def _clean_designation(raw: str | None) -> str:
    """Return a clean, short designation string.

    Strips trailing department-name phrases, welcome messages, and other
    noise that appears after the designation on SVNIT HoD pages.
    """
    if not raw:
        return "Head of Department"
    # Cut off at these noise markers (order matters — earlier markers take priority)
    noise_markers = [
        "Dept.", "S.V.N.I.T", "Department of", "Our ", "Welcome",
        "\n", "SVNIT", "Surat",
    ]
    for marker in noise_markers:
        idx = raw.find(marker)
        if idx > 0:
            raw = raw[:idx]
    raw = raw.strip().rstrip(".,;:").strip()
    # Reject if too long (full sentence) or empty
    if not raw or len(raw) > 60:
        return "Head of Department"
    return raw


def _extract_hod(hod_soup: BeautifulSoup) -> tuple[str | None, str | None]:
    """Return (hod_name, hod_designation) from a hod-message.php page.
    Searches within <main> to avoid navigation sidebar false-positives.
    """
    main = hod_soup.find("main")
    if not main:
        return None, None

    teachers_divs = main.find_all("div", class_="teachers")
    if not teachers_divs:
        # Fallback: look for first h4.author-name in main
        h4 = main.find("h4", class_="author-name")
        if h4:
            name = h4.get_text(strip=True)
            if name.lower() not in _SKIP_TEXTS:
                # Try to get designation from the immediate next <p> sibling
                desig_raw = None
                el = h4.next_sibling
                while el:
                    if hasattr(el, "name") and el.name == "p":
                        desig_raw = el.get_text(separator=" ", strip=True)
                        break
                    # If we hit a block div, stop looking
                    if hasattr(el, "name") and el.name == "div":
                        break
                    el = el.next_sibling
                return name, _clean_designation(desig_raw)
        return None, None

    # First .teachers div → first row → info div
    first_div = teachers_divs[0]
    rows = first_div.find_all("div", class_="row", recursive=False)
    for row in rows:
        info_divs = row.find_all("div", recursive=False)
        info_div = info_divs[1] if len(info_divs) > 1 else row
        member = _parse_info_div(info_div, "Head of Department")
        if member.get("name"):
            desig = _clean_designation(member.get("designation"))
            return member.get("name"), desig
    return None, None


# ── Faculty extraction ─────────────────────────────────────────────────────────


def _extract_faculty(fac_soup: BeautifulSoup) -> tuple[list[dict], str | None, str | None]:
    """Parse faculty page → (faculty_list, hod_name, hod_designation).

    Structure: <main> contains multiple <div class="teachers"> blocks, one per
    designation group. Each block holds multiple <div class="row"> faculty entries.
    """
    faculty: list[dict] = []
    hod_name: str | None = None
    hod_desig: str | None = None

    main = fac_soup.find("main")
    if not main:
        return faculty, hod_name, hod_desig

    teachers_divs = main.find_all("div", class_="teachers")

    for teachers_div in teachers_divs:
        # Determine designation group from the preceding <h3>
        prev_h3 = teachers_div.find_previous("h3")
        group = prev_h3.get_text(strip=True) if prev_h3 else "Faculty"
        is_hod_group = "head of department" in group.lower()

        # Each direct .row is one faculty member
        rows = teachers_div.find_all("div", class_="row", recursive=False)
        for row in rows:
            child_divs = row.find_all("div", recursive=False)
            # Info div is typically the second column (index 1)
            info_div = child_divs[1] if len(child_divs) > 1 else row
            member = _parse_info_div(info_div, group)

            if not member.get("name"):
                continue

            if is_hod_group:
                hod_name = member.get("name")
                hod_desig = member.get("designation")
            else:
                faculty.append(member)

    return faculty, hod_name, hod_desig


# ── Lab extraction ─────────────────────────────────────────────────────────────


def _extract_labs(labs_soup: BeautifulSoup) -> list[str]:
    """Extract lab names from laboratories.php."""
    labs: list[str] = []
    for tag in labs_soup.find_all(["h3", "h4", "td", "li"]):
        txt = tag.get_text(strip=True)
        if txt and "lab" in txt.lower() and len(txt) < 120:
            labs.append(txt)
    return list(dict.fromkeys(labs))  # deduplicate preserving order


# ── Research project extraction ────────────────────────────────────────────────


def _extract_projects(proj_soup: BeautifulSoup) -> list[str]:
    """Extract project titles from project.php / research.php."""
    projects: list[str] = []
    for tag in proj_soup.find_all(["td", "li", "h4", "p"]):
        txt = tag.get_text(strip=True)
        if txt and 10 < len(txt) < 300:
            projects.append(txt)
    return list(dict.fromkeys(projects))[:50]  # cap at 50


# ── Per-department scrape ──────────────────────────────────────────────────────


def _scrape_department(dept_name: str, dept_cfg: dict[str, str]) -> dict[str, Any]:
    """Scrape one SVNIT department and return a Department-compatible dict."""
    base = dept_cfg["base"]
    result: dict[str, Any] = {"name": dept_name}

    logger.info(f"[SVNIT] Scraping department: {dept_name}")

    # 1. HoD page
    hod_page = dept_cfg.get("hod")
    if hod_page:
        hod_soup = _fetch(urljoin(base, hod_page))
        if hod_soup:
            hod_name, hod_desig = _extract_hod(hod_soup)
            if hod_name:
                result["hod_name"] = hod_name
                result["hod_designation"] = hod_desig or "Head of Department"

    # 2. Faculty page
    fac_page = dept_cfg.get("faculty")
    if fac_page:
        fac_soup = _fetch(urljoin(base, fac_page))
        if fac_soup:
            faculty, h_name, h_desig = _extract_faculty(fac_soup)
            if faculty:
                result["faculty"] = faculty
                result["faculty_count"] = len(faculty)
            # Use HoD from faculty page if not already set from hod-message.php
            if h_name and not result.get("hod_name"):
                result["hod_name"] = h_name
                result["hod_designation"] = h_desig or "Head of Department"

    time.sleep(0.8)  # polite crawl delay

    # 3. Labs
    labs_page = dept_cfg.get("labs")
    if labs_page:
        labs_soup = _fetch(urljoin(base, labs_page))
        if labs_soup:
            labs = _extract_labs(labs_soup)
            if labs:
                result["labs"] = labs

    # 4. Research/Projects
    proj_page = dept_cfg.get("research")
    if proj_page:
        proj_soup = _fetch(urljoin(base, proj_page))
        if proj_soup:
            projects = _extract_projects(proj_soup)
            if projects:
                result["research_projects"] = projects

    time.sleep(0.8)

    return result


# ── Public entry point ─────────────────────────────────────────────────────────


def scrape_svnit_departments() -> list[dict[str, Any]]:
    """Scrape all 12 SVNIT departments. Returns list of Department dicts."""
    all_depts: list[dict[str, Any]] = []

    for dept_name, dept_cfg in DEPARTMENTS.items():
        try:
            dept_data = _scrape_department(dept_name, dept_cfg)
            all_depts.append(dept_data)
            fac_count = dept_data.get("faculty_count", 0)
            hod = dept_data.get("hod_name", "N/A")
            logger.info(
                f"[SVNIT] {dept_name}: HoD={hod}, Faculty={fac_count}"
            )
        except Exception as exc:
            logger.error(f"[SVNIT] Error scraping {dept_name}: {exc}")
            all_depts.append({"name": dept_name})

    return all_depts


