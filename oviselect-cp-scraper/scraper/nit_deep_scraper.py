"""Deep scraper for multiple NITs.

Scrapes departments and faculty from:
- NIT Trichy (nitt.edu)
- NITK Surathkal (nitk.ac.in) - subdomain structure
- NIT Calicut (nitc.ac.in)
- NIT Rourkela (nitrkl.ac.in)
- NIT Goa (nitgoa.ac.in)
- NIT Raipur (nitrr.ac.in)
- MNNIT Allahabad (mnnit.ac.in)
- MNIT Jaipur (mnit.ac.in)
- NIT Patna (nitp.ac.in)
- NIT Srinagar (nitsri.ac.in)
- MANIT Bhopal (manit.ac.in)
- VNIT Nagpur (vnit.ac.in)
- NIT Durgapur (nitdgp.ac.in)
- NIT Jamshedpur (nitjsr.ac.in)
- NIT Jalandhar (nitj.ac.in)
- NIT Warangal (nitw.ac.in)
- NIT Puducherry (nitpy.ac.in)
- NIT Andhra Pradesh (nitandhra.ac.in)
"""

from __future__ import annotations

import asyncio
import re
import time
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from loguru import logger

from scraper.fetch_utils import fetch as _scrapling_fetch

# ── HTTP helpers ───────────────────────────────────────────────────────────────


def _fetch(url: str, retries: int = 2, verify: bool = False, timeout: int = 20) -> BeautifulSoup | None:
    return _scrapling_fetch(url, retries=retries, timeout=timeout, verify=verify)


def _clean(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def _is_name(text: str) -> bool:
    """Check if text looks like a faculty name."""
    t = text.strip()
    return bool(t and len(t) > 3 and len(t) < 80 and
                any(k in t for k in ["Dr.", "Prof.", "Mr.", "Ms.", "Mrs.", "Sh."]))


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
    return text.strip()[:60]


# ══════════════════════════════════════════════════════════════════════════════
# NIT TRICHY
# ══════════════════════════════════════════════════════════════════════════════

_NITT_BASE = "https://www.nitt.edu"
_NITT_DEPARTMENTS = {
    "Architecture": "architecture",
    "Chemical Engineering": "chem",
    "Chemistry": "chemistry",
    "Civil Engineering": "civil",
    "Computer Applications": "ca",
    "Computer Science & Engineering": "cse",
    "Electrical & Electronics Engineering": "eee",
    "Electronics & Communication Engineering": "ece",
    "Humanities": "humanities",
    "Instrumentation & Control Engineering": "ice",
    "Management Studies": "management",
    "Mathematics": "maths",
    "Mechanical Engineering": "mech",
    "Metallurgical & Materials Engineering": "meta",
    "Physics": "physics",
    "Production Engineering": "prod",
}


def _scrape_nitt_dept(dept_name: str, slug: str) -> dict[str, Any]:
    fac_url = f"{_NITT_BASE}/home/academics/departments/{slug}/faculty/"
    soup = _fetch(fac_url)
    if not soup:
        return {"name": dept_name}

    dept: dict[str, Any] = {"name": dept_name}
    faculty = []

    # Faculty links from the list
    seen = set()
    fac_links = []
    for a in soup.find_all("a", href=True):
        text = _clean(a.get_text())
        if _is_name(text) and text not in seen:
            seen.add(text)
            href = a["href"]
            if not href.startswith("http"):
                href = urljoin(fac_url, href)
            fac_links.append((text, href))

    logger.info(f"[NIT Trichy] {dept_name}: {len(fac_links)} faculty found")

    for name, profile_url in fac_links[:40]:  # cap per dept
        member: dict[str, Any] = {"name": name, "profile_url": profile_url}
        # Optionally fetch individual profile
        prof_soup = _fetch(profile_url)
        if prof_soup:
            rows = prof_soup.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    label = _clean(cells[0].get_text()).lower()
                    value = _clean(cells[1].get_text())
                    if "designation" in label and value:
                        member["designation"] = _classify_designation(value)
                    elif "qualification" in label and value:
                        member["qualifications"] = [{"degree": q.strip()} for q in value.split(",") if q.strip()]
                    elif "specialization" in label or "research area" in label or "research interest" in label:
                        areas = [a.strip() for a in re.split(r"[,;]", value) if a.strip()]
                        if areas:
                            member["specializations"] = areas
                    elif "email" in label and value and "@" in value:
                        member["email"] = value
        if not member.get("designation"):
            member["designation"] = "Faculty"
        faculty.append(member)
        time.sleep(0.4)

    if faculty:
        dept["faculty"] = faculty
        dept["faculty_count"] = len(faculty)
    return dept


def scrape_nit_trichy() -> list[dict[str, Any]]:
    logger.info("[NIT Trichy] Starting scrape...")
    departments = []
    for dept_name, slug in _NITT_DEPARTMENTS.items():
        try:
            dept = _scrape_nitt_dept(dept_name, slug)
            departments.append(dept)
            time.sleep(1)
        except Exception as e:
            logger.error(f"[NIT Trichy] Error scraping {dept_name}: {e}")
            departments.append({"name": dept_name})
    return departments


# ══════════════════════════════════════════════════════════════════════════════
# NITK SURATHKAL  (each dept has its own subdomain)
# ══════════════════════════════════════════════════════════════════════════════

_NITK_DEPARTMENTS = {
    "Chemical Engineering": "chemical",
    "Civil Engineering": "civil",
    "Computer Science & Engineering": "cse",
    "Electrical & Electronics Engineering": "eee",
    "Electronics & Communication Engineering": "ece",
    "Information Technology": "it",
    "Mathematical & Computational Sciences": "maths",
    "Mechanical Engineering": "mech",
    "Metallurgical & Materials Engineering": "mme",
    "Mining Engineering": "mining",
    "Physics": "physics",
    "Chemistry": "chemistry",
    "Humanities, Social Sciences & Management": "hssm",
}


def _scrape_nitk_dept(dept_name: str, subdomain: str) -> dict[str, Any]:
    base = f"http://{subdomain}.nitk.ac.in"
    dept: dict[str, Any] = {"name": dept_name}
    faculty = []

    for path in ["/people", "/faculty", "/faculty-members", "/people/faculty"]:
        soup = _fetch(base + path)
        if soup:
            names_found = []
            for tag in soup.find_all(["h3", "h4", "h5", "a", "td", "p"]):
                text = _clean(tag.get_text())
                if _is_name(text) and text not in [f["name"] for f in faculty]:
                    href = None
                    if tag.name == "a" and tag.get("href"):
                        href = urljoin(base, tag["href"])
                    # Try to get designation from sibling/parent
                    desig = "Faculty"
                    parent = tag.parent
                    if parent:
                        for sib in parent.find_all(["p", "span", "small", "div"]):
                            sib_text = _clean(sib.get_text())
                            if any(k in sib_text.lower() for k in ["professor", "lecturer", "scientist"]):
                                desig = _classify_designation(sib_text)
                                break
                    member: dict[str, Any] = {"name": text, "designation": desig}
                    if href:
                        member["profile_url"] = href
                    faculty.append(member)
            if faculty:
                logger.info(f"[NITK] {dept_name}: {len(faculty)} faculty at {path}")
                break

    if faculty:
        dept["faculty"] = faculty
        dept["faculty_count"] = len(faculty)
    return dept


def scrape_nitk_surathkal() -> list[dict[str, Any]]:
    logger.info("[NITK Surathkal] Starting scrape...")
    departments = []
    for dept_name, sub in _NITK_DEPARTMENTS.items():
        try:
            dept = _scrape_nitk_dept(dept_name, sub)
            departments.append(dept)
            time.sleep(1)
        except Exception as e:
            logger.error(f"[NITK] Error scraping {dept_name}: {e}")
            departments.append({"name": dept_name})
    return departments


# ══════════════════════════════════════════════════════════════════════════════
# NIT CALICUT
# ══════════════════════════════════════════════════════════════════════════════

_NITC_BASE = "https://nitc.ac.in"
_NITC_DEPARTMENTS = {
    "Architecture and Planning": "architecture-and-planning",
    "Bioscience and Engineering": "bioscience-and-engineering",
    "Chemical Engineering": "chemical-engineering",
    "Chemistry": "chemistry",
    "Civil Engineering": "civil-engineering",
    "Computer Science & Engineering": "computer-science-amp-engineering",
    "Electrical Engineering": "electrical-engineering",
    "Electronics & Communication Engineering": "electronics-amp-communication-engineering",
    "Humanities, Arts and Social Sciences": "humanities-arts-and-social-sciences",
    "Materials Science and Engineering": "materials-science-and-engineering",
    "Mathematics": "mathematics",
    "Management Studies": "management-studies",
    "Mechanical Engineering": "mechanical-engineering",
    "Physics": "physics",
}


_NITC_SKIP_HEADERS = {"IMPORTANT NOTIFICATIONS", "DEPARTMENTS", "HEAD OF THE DEPARTMENT", "QUICK LINKS"}


def _is_nitc_name(text: str) -> bool:
    """Broader name check for NITC faculty: allows names without Dr./Prof. titles.
    Excludes all-caps section headers and short nav items."""
    t = text.strip()
    if not t or len(t) < 4 or len(t) > 80:
        return False
    if t.upper() in _NITC_SKIP_HEADERS or t.isupper():
        return False
    # Must contain at least one letter and a space (names have multiple words)
    if " " not in t:
        return False
    # Skip items that look like navigation (single-word uppercase fragments)
    words = t.split()
    if len(words) < 2:
        return False
    return True


def _scrape_nitc_dept(dept_name: str, slug: str) -> dict[str, Any]:
    dept: dict[str, Any] = {"name": dept_name}
    # Correct URL: /department/{slug}/faculty-and-staff/faculty
    soup = _fetch(f"{_NITC_BASE}/department/{slug}/faculty-and-staff/faculty")
    if not soup:
        return dept

    faculty = []
    seen = set()
    # NIT Calicut faculty pages list names in <h6> tags (confirmed by probing)
    # Some departments use "Dr." prefixes, others have bare names — use broad filter
    for tag in soup.find_all("h6"):
        text = _clean(tag.get_text())
        if _is_nitc_name(text) and text not in seen:
            seen.add(text)
            member: dict[str, Any] = {"name": text}
            # Try to get designation from nearby siblings
            parent = tag.find_parent(["div", "article", "section", "li"])
            if parent:
                for sib in parent.find_all(["p", "span", "small", "h5"]):
                    sib_text = _clean(sib.get_text())
                    if any(k in sib_text.lower() for k in ["professor", "lecturer", "associate", "assistant"]) \
                            and sib_text != text and len(sib_text) < 60:
                        member["designation"] = _classify_designation(sib_text)
                        break
            if not member.get("designation"):
                member["designation"] = "Faculty"
            faculty.append(member)

    if faculty:
        dept["faculty"] = faculty
        dept["faculty_count"] = len(faculty)
        logger.info(f"[NIT Calicut] {dept_name}: {len(faculty)} faculty")
    else:
        logger.warning(f"[NIT Calicut] {dept_name}: 0 faculty found (JS-rendered?)")
    return dept


def scrape_nit_calicut() -> list[dict[str, Any]]:
    logger.info("[NIT Calicut] Starting scrape...")
    departments = []
    for dept_name, slug in _NITC_DEPARTMENTS.items():
        try:
            dept = _scrape_nitc_dept(dept_name, slug)
            departments.append(dept)
            time.sleep(1)
        except Exception as e:
            logger.error(f"[NIT Calicut] Error {dept_name}: {e}")
            departments.append({"name": dept_name})
    return departments




# ══════════════════════════════════════════════════════════════════════════════
# NIT ROURKELA
# ══════════════════════════════════════════════════════════════════════════════

_NITR_BASE = "https://nitrkl.ac.in"
_NITR_DEPT_SLUGS = {
    "Architecture": "AR",
    "Biotechnology & Medical Engineering": "BM",
    "Chemical Engineering": "CH",
    "Chemistry": "CY",
    "Civil Engineering": "CE",
    "Computer Science & Engineering": "CS",
    "Electrical Engineering": "EE",
    "Electronics & Communication Engineering": "EC",
    "Humanities & Social Sciences": "HS",
    "Industrial Design": "ID",
    "Life Science": "LS",
    "Mathematics": "MA",
    "Mechanical Engineering": "ME",
    "Metallurgical & Materials Engineering": "MM",
    "Mining Engineering": "MN",
    "Physics": "PH",
    "School of Management": "SM",
}


async def _scrape_nitr_playwright() -> list[dict[str, Any]]:
    """Use Playwright to scrape the JS-rendered NIT Rourkela faculty directory.

    The page renders faculty as ``div.fac-item.card`` elements only after JS
    executes, so a plain HTTP fetch returns empty results.  We iterate through
    all 26 alphabetical letter pages to collect the full faculty list and infer
    the department from the profile URL (e.g. /BM/~name/ → Biotechnology & ME).
    """
    from playwright.async_api import async_playwright

    # slug → dept name (reverse of _NITR_DEPT_SLUGS)
    slug_to_dept = {v: k for k, v in _NITR_DEPT_SLUGS.items()}
    departments: dict[str, dict] = {name: {"name": name, "faculty": []} for name in _NITR_DEPT_SLUGS}
    seen: set[str] = set()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            url = f"https://www.nitrkl.ac.in/FacultyStaff/Faculty/?SearchAlpha={letter}"
            logger.info(f"[NIT Rourkela] Scraping letter {letter} …")

            html = ""
            for attempt in range(3):  # retry up to 3 times for flaky connectivity
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
                except Exception as exc:
                    logger.warning(f"[NIT Rourkela] Nav warning {letter} (attempt {attempt+1}): {exc}")
                    await asyncio.sleep(3)

                # Wait for JS to inject the faculty cards
                await page.wait_for_timeout(8_000)

                try:
                    html = await page.content()
                    break  # success — stop retrying
                except Exception as exc:
                    logger.warning(f"[NIT Rourkela] content() error {letter} (attempt {attempt+1}): {exc}")
                    await asyncio.sleep(3)

            if not html:
                logger.warning(f"[NIT Rourkela] Skipping letter {letter} after all retries")
                continue

            soup = BeautifulSoup(html, "html.parser")
            cards = soup.find_all("div", class_=lambda c: c and "fac-item" in c and "card" in c if c else False)
            logger.info(f"[NIT Rourkela] Letter {letter}: {len(cards)} cards")

            for card in cards:
                # Name + designation are in the card-body
                body = card.find("div", class_="card-body")
                if not body:
                    body = card

                # Profile link contains the department slug, e.g. /BM/~name/
                profile_url = ""
                link_tag = body.find("a", href=True)
                if link_tag:
                    href = link_tag.get("href", "")
                    profile_url = urljoin("https://www.nitrkl.ac.in", href) if href else ""

                # Extract text nodes: typically [name, designation, "View Profile"]
                texts = [t.strip() for t in body.get_text(separator="\n").splitlines() if t.strip()]
                # Remove "View Profile" and blank lines
                texts = [t for t in texts if t.lower() not in ("view profile", "")]

                if not texts:
                    continue
                name = _clean(texts[0])
                designation = _classify_designation(texts[1]) if len(texts) > 1 else "Faculty"

                if not name or name in seen:
                    continue
                seen.add(name)

                member: dict[str, Any] = {"name": name, "designation": designation}
                if profile_url:
                    member["profile_url"] = profile_url

                # Infer department from the URL path segment (e.g. /BM/ or /CS/)
                dept_key = "Computer Science & Engineering"  # fallback
                if profile_url:
                    path_parts = [p for p in urlparse(profile_url).path.split("/") if p]
                    for part in path_parts:
                        slug_upper = part.upper()
                        if slug_upper in slug_to_dept:
                            dept_key = slug_to_dept[slug_upper]
                            break

                departments[dept_key]["faculty"].append(member)

        await browser.close()

    result = []
    for dept_name, dept_data in departments.items():
        fac = dept_data.get("faculty", [])
        if fac:
            dept_data["faculty_count"] = len(fac)
            logger.info(f"[NIT Rourkela] {dept_name}: {len(fac)} faculty")
        result.append(dept_data)
    return result


def scrape_nit_rourkela() -> list[dict[str, Any]]:
    """Entry point — runs the async Playwright scraper synchronously."""
    logger.info("[NIT Rourkela] Starting Playwright-based scrape (JS-rendered site)...")
    try:
        return asyncio.run(_scrape_nitr_playwright())
    except Exception as exc:
        logger.error(f"[NIT Rourkela] Playwright scrape failed: {exc}")
        # Return empty department shells so the pipeline doesn't break
        return [{"name": name} for name in _NITR_DEPT_SLUGS]


# ══════════════════════════════════════════════════════════════════════════════
# NIT GOA
# ══════════════════════════════════════════════════════════════════════════════

_NITGOA_BASE = "https://www.nitgoa.ac.in"


def scrape_nit_goa() -> list[dict[str, Any]]:
    logger.info("[NIT Goa] Starting scrape...")
    soup = _fetch(f"{_NITGOA_BASE}/People/frontend/people_faculty.html")
    if not soup:
        return []

    # Parse faculty list - find all faculty links
    all_faculty: list[dict] = []
    seen = set()
    for a in soup.find_all("a", href=True):
        text = _clean(a.get_text())
        if _is_name(text) and text not in seen:
            seen.add(text)
            href = a["href"]
            if not href.startswith("http"):
                href = urljoin(f"{_NITGOA_BASE}/People/frontend/", href)
            member: dict[str, Any] = {"name": text, "profile_url": href}
            all_faculty.append(member)

    # Group by dept - scrape individual pages to get dept + designation
    dept_map: dict[str, list] = {}
    for member in all_faculty[:100]:
        prof_soup = _fetch(member["profile_url"])
        dept = "General"
        if prof_soup:
            text_content = prof_soup.get_text()
            for tag in prof_soup.find_all(["td", "th", "dt", "strong", "b"]):
                label = _clean(tag.get_text()).lower()
                if "designation" in label or "designation:" in label:
                    val_tag = tag.find_next(["td", "dd", "span"])
                    if val_tag:
                        member["designation"] = _classify_designation(_clean(val_tag.get_text()))
                if "department" in label:
                    val_tag = tag.find_next(["td", "dd", "span"])
                    if val_tag:
                        dept = _clean(val_tag.get_text())
            # Try from table rows
            for row in prof_soup.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 2:
                    label = _clean(cells[0].get_text()).lower()
                    value = _clean(cells[1].get_text())
                    if "designation" in label and value:
                        member["designation"] = _classify_designation(value)
                    elif "department" in label and value:
                        dept = value
                    elif "specialization" in label or "research" in label:
                        areas = [a.strip() for a in re.split(r"[,;]", value) if a.strip() and len(a.strip()) > 3]
                        if areas:
                            member["specializations"] = areas[:8]
        if not member.get("designation"):
            member["designation"] = "Faculty"
        if dept not in dept_map:
            dept_map[dept] = []
        dept_map[dept].append(member)
        time.sleep(0.5)

    result = []
    for dept_name, faculty in dept_map.items():
        result.append({
            "name": dept_name,
            "faculty": faculty,
            "faculty_count": len(faculty),
        })
        logger.info(f"[NIT Goa] {dept_name}: {len(faculty)} faculty")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# NIT RAIPUR
# ══════════════════════════════════════════════════════════════════════════════

_NITRR_BASE = "https://nitrr.ac.in"
_NITRR_DEPT_PAGES = {
    "Applied Geology": "aplgeo",
    "Architecture": "arch",
    "Biochemical Engineering": "bio",
    "Chemical Engineering": "chem",
    "Chemistry": "chem_dept",
    "Civil Engineering": "civil",
    "Computer Science & Engineering": "cs",
    "Electrical Engineering": "elec",
    "Electronics & Telecom Engineering": "etc",
    "Information Technology": "it",
    "Mathematics": "maths",
    "Mechanical Engineering": "mech",
    "Metallurgical Engineering": "meta",
    "Mining Engineering": "mining",
    "Physics": "phy",
}


def scrape_nit_raipur() -> list[dict[str, Any]]:
    logger.info("[NIT Raipur] Starting scrape from global faculty page (SSL verify=False)...")
    soup = _fetch(f"{_NITRR_BASE}/fac_rnc_new.php", verify=False)
    if not soup:
        return []

    dept_map: dict[str, list] = {}
    seen = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = _clean(a.get_text())
        if "viewdetails.php?q=" in href and _is_name(text) and text not in seen:
            seen.add(text)
            # Parse dept from URL: viewdetails.php?q={dept_code}.{person}
            q_part = href.split("q=")[-1]
            dept_code = q_part.split(".")[0] if "." in q_part else "general"
            member: dict[str, Any] = {
                "name": text,
                "profile_url": urljoin(_NITRR_BASE, href),
            }
            # Fetch individual profile for designation
            prof_soup = _fetch(member["profile_url"], verify=False)
            if prof_soup:
                for row in prof_soup.find_all("tr"):
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        label = _clean(cells[0].get_text()).lower()
                        value = _clean(cells[1].get_text())
                        if "designation" in label and value:
                            member["designation"] = _classify_designation(value)
                        elif "department" in label and value and "dept" not in value.lower():
                            dept_code = value
                        elif ("specialization" in label or "research" in label or "interest" in label) and value:
                            areas = [a.strip() for a in re.split(r"[,;]", value) if a.strip() and len(a.strip()) > 3]
                            if areas:
                                member["specializations"] = areas[:8]
                        elif "qualification" in label and value:
                            member["qualifications"] = [{"degree": q.strip()} for q in value.split(",") if q.strip()]
            if not member.get("designation"):
                member["designation"] = "Faculty"
            if dept_code not in dept_map:
                dept_map[dept_code] = []
            dept_map[dept_code].append(member)
            time.sleep(0.3)

    # Build proper dept names
    result = []
    code_to_name = {v: k for k, v in _NITRR_DEPT_PAGES.items()}
    for code, faculty in dept_map.items():
        dept_name = code_to_name.get(code, code.upper())
        result.append({
            "name": dept_name,
            "faculty": faculty,
            "faculty_count": len(faculty),
        })
        logger.info(f"[NIT Raipur] {dept_name}: {len(faculty)} faculty")
    return result



# ══════════════════════════════════════════════════════════════════════════════
# MNNIT ALLAHABAD
# ══════════════════════════════════════════════════════════════════════════════

_MNNIT_BASE = "https://www.mnnit.ac.in"
_MNNIT_DEPARTMENTS = {
    "Applied Mechanics": "am",
    "Biotechnology": "biotech",
    "Chemical Engineering": "cm",
    "Chemistry": "chem",
    "Civil Engineering": "ce",
    "Computer Science & Engineering": "csed",
    "Electrical Engineering": "ee",
    "Electronics & Communication Engineering": "ec",
    "Humanities & Social Sciences": "hss",
    "Mathematics": "maths",
    "Mechanical Engineering": "me",
    "Physics": "phy",
    "Information Technology": "it",
}


def _scrape_mnnit_dept(dept_name: str, slug: str) -> dict[str, Any]:
    dept: dict[str, Any] = {"name": dept_name}
    soup = _fetch(f"{_MNNIT_BASE}/index.php/department/engineering/{slug}")
    if not soup:
        soup = _fetch(f"{_MNNIT_BASE}/index.php/department/science/{slug}")
    if not soup:
        return dept

    faculty = []
    seen = set()

    # Check for "faculty profile" links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = _clean(a.get_text())
        if "faculty" in href.lower() and "profile" in text.lower():
            # This is a link to faculty profile page
            profile_url = urljoin(_MNNIT_BASE, href) if not href.startswith("http") else href
            fac_soup = _fetch(profile_url)
            if fac_soup:
                for tag in fac_soup.find_all(["h3", "h4", "h5", "strong", "b", "td"]):
                    name_text = _clean(tag.get_text())
                    if _is_name(name_text) and name_text not in seen:
                        seen.add(name_text)
                        member: dict[str, Any] = {"name": name_text, "designation": "Faculty"}
                        # Try sibling for designation
                        nxt = tag.find_next(["p", "span", "small", "td"])
                        if nxt:
                            nt = _clean(nxt.get_text())
                            if any(k in nt.lower() for k in ["professor", "lecturer", "scientist", "assistant"]):
                                member["designation"] = _classify_designation(nt)
                        faculty.append(member)
            break

    # Fallback: find faculty names directly on dept page
    if not faculty:
        for tag in soup.find_all(["h3", "h4", "h5", "td"]):
            text = _clean(tag.get_text())
            if _is_name(text) and text not in seen:
                seen.add(text)
                member = {"name": text, "designation": "Faculty"}
                nxt = tag.find_next(["p", "span", "small"])
                if nxt:
                    nt = _clean(nxt.get_text())
                    if any(k in nt.lower() for k in ["professor", "lecturer"]):
                        member["designation"] = _classify_designation(nt)
                faculty.append(member)

    if faculty:
        dept["faculty"] = faculty
        dept["faculty_count"] = len(faculty)
        logger.info(f"[MNNIT] {dept_name}: {len(faculty)} faculty")
    return dept


def scrape_mnnit_allahabad() -> list[dict[str, Any]]:
    logger.info("[MNNIT Allahabad] Starting scrape...")
    departments = []
    for dept_name, slug in _MNNIT_DEPARTMENTS.items():
        try:
            dept = _scrape_mnnit_dept(dept_name, slug)
            departments.append(dept)
            time.sleep(1)
        except Exception as e:
            logger.error(f"[MNNIT] Error {dept_name}: {e}")
            departments.append({"name": dept_name})
    return departments


# ══════════════════════════════════════════════════════════════════════════════
# MNIT JAIPUR
# ══════════════════════════════════════════════════════════════════════════════

_MNIT_BASE = "https://www.mnit.ac.in"
_MNIT_DEPARTMENTS = {
    "Architecture & Planning": "dept_arch",
    "Chemical Engineering": "dept_chemical",
    "Chemistry": "dept_chemistry",
    "Civil Engineering": "dept_civil",
    "Computer Science & Engineering": "dept_cse",
    "Electrical Engineering": "dept_ee",
    "Electronics & Communication Engineering": "dept_ece",
    "Humanities & Social Sciences": "dept_hss",
    "Mathematics & Scientific Computing": "dept_maths",
    "Mechanical Engineering": "dept_mech",
    "Metallurgical & Materials Engineering": "dept_meta",
    "Physics": "dept_physics",
    "Structural Engineering": "dept_structural",
}


def _scrape_mnit_dept(dept_name: str, slug: str) -> dict[str, Any]:
    dept: dict[str, Any] = {"name": dept_name}
    # MNIT uses people.php or faculty.php pattern
    faculty = []
    seen = set()

    for path in [f"/{slug}/people.php", f"/{slug}/faculty.php", f"/{slug}/"]:
        soup = _fetch(_MNIT_BASE + path)
        if not soup:
            continue
        text_page = soup.get_text()
        if not any(k in text_page for k in ["Dr.", "Prof.", "Assistant Professor"]):
            continue

        for tag in soup.find_all(["h3", "h4", "h5", "strong", "b", "td", "a"]):
            text = _clean(tag.get_text())
            if _is_name(text) and text not in seen and len(text) < 70:
                seen.add(text)
                member: dict[str, Any] = {"name": text, "designation": "Faculty"}
                # Look for designation in parent/siblings
                parent = tag.parent
                if parent:
                    parent_text = _clean(parent.get_text())
                    desig_match = re.search(
                        r"(Professor|Lecturer|Scientist|Assistant|Associate)[^\n,;]{0,40}",
                        parent_text, re.IGNORECASE
                    )
                    if desig_match:
                        member["designation"] = _classify_designation(desig_match.group(0))
                faculty.append(member)
        if faculty:
            logger.info(f"[MNIT] {dept_name}: {len(faculty)} faculty at {path}")
            break

    if faculty:
        dept["faculty"] = faculty
        dept["faculty_count"] = len(faculty)
    return dept


def scrape_mnit_jaipur() -> list[dict[str, Any]]:
    logger.info("[MNIT Jaipur] Starting scrape...")
    departments = []
    for dept_name, slug in _MNIT_DEPARTMENTS.items():
        try:
            dept = _scrape_mnit_dept(dept_name, slug)
            departments.append(dept)
            time.sleep(1)
        except Exception as e:
            logger.error(f"[MNIT] Error {dept_name}: {e}")
            departments.append({"name": dept_name})
    return departments



# ══════════════════════════════════════════════════════════════════════════════
# NIT PATNA
# ══════════════════════════════════════════════════════════════════════════════

_NITP_BASE = "https://www.nitp.ac.in"
_NITP_DEPARTMENTS = {
    "Architecture": "AR",
    "Chemical Engineering": "CH",
    "Chemistry": "CY",
    "Civil Engineering": "CE",
    "Computer Science & Engineering": "CSE",
    "Electrical Engineering": "EE",
    "Electronics & Communication Engineering": "EC",
    "Humanities & Social Sciences": "HS",
    "Mathematics": "MA",
    "Mechanical Engineering": "ME",
    "Physics": "PH",
}


def _scrape_nitp_dept(dept_name: str, slug: str) -> dict[str, Any]:
    dept: dict[str, Any] = {"name": dept_name}
    # Correct URL: /Department/{slug}/faculty (confirmed by probing)
    soup = _fetch(f"{_NITP_BASE}/Department/{slug}/faculty")
    if not soup:
        # Fallback to department index page
        soup = _fetch(f"{_NITP_BASE}/Department/{slug}")
    if not soup:
        return dept

    faculty = []
    seen = set()

    # NIT Patna uses table rows for faculty listing
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) >= 2:
            name_text = _clean(cells[0].get_text())
            if _is_name(name_text) and name_text not in seen:
                seen.add(name_text)
                member: dict[str, Any] = {"name": name_text}
                if len(cells) > 1:
                    desig_text = _clean(cells[1].get_text())
                    member["designation"] = _classify_designation(desig_text) if desig_text else "Faculty"
                if len(cells) > 2:
                    email_text = _clean(cells[2].get_text())
                    if "@" in email_text:
                        member["email"] = email_text
                faculty.append(member)

    # Fallback: look for named elements in heading/inline tags
    if not faculty:
        for tag in soup.find_all(["h3", "h4", "h5", "h6", "strong", "b"]):
            text = _clean(tag.get_text())
            if _is_name(text) and text not in seen and len(text) < 80:
                seen.add(text)
                faculty.append({"name": text, "designation": "Faculty"})

    if faculty:
        dept["faculty"] = faculty
        dept["faculty_count"] = len(faculty)
        logger.info(f"[NIT Patna] {dept_name}: {len(faculty)} faculty")
    else:
        logger.warning(f"[NIT Patna] {dept_name}: 0 faculty found (JS-rendered?)")
    return dept


def scrape_nit_patna() -> list[dict[str, Any]]:
    logger.info("[NIT Patna] Starting scrape...")
    departments = []
    for dept_name, slug in _NITP_DEPARTMENTS.items():
        try:
            dept = _scrape_nitp_dept(dept_name, slug)
            departments.append(dept)
            time.sleep(1)
        except Exception as e:
            logger.error(f"[NIT Patna] Error {dept_name}: {e}")
            departments.append({"name": dept_name})
    return departments


# ══════════════════════════════════════════════════════════════════════════════
# NIT SRINAGAR
# ══════════════════════════════════════════════════════════════════════════════

_NITSRI_BASE = "https://nitsri.ac.in"
# Department IDs discovered from the website
_NITSRI_DEPARTMENTS = {
    "Chemical Engineering": ("che", "che"),
    "Civil Engineering": ("ce", "c"),
    "Computer Science & Engineering": ("cs", "cs"),
    "Electrical Engineering": ("ee", "ee"),
    "Electronics & Communication Engineering": ("ece", "ec"),
    "Humanities & Social Sciences": ("hss", "hss"),
    "Mathematics": ("maths", "m"),
    "Mechanical Engineering": ("me", "me"),
    "Metallurgical Engineering": ("met", "mt"),
    "Physics": ("phy", "phy"),
    "Chemical Technology": ("ct", "ct"),
    "Computer Applications": ("ca", "ca"),
}


def _scrape_nitsri_dept(dept_name: str, item_id: str, dept_id: str) -> dict[str, Any]:
    dept: dict[str, Any] = {"name": dept_name}
    # NIT Srinagar uses ASPX with obfuscated IDs
    url = f"{_NITSRI_BASE}/Department/Pages/FacultyList.aspx?nDeptID={dept_id}"
    soup = _fetch(url)
    if not soup:
        # Try alternate form
        url2 = f"{_NITSRI_BASE}/Department/Deptindex.aspx?page=a&ItemID={item_id}&nDeptID={dept_id}"
        soup = _fetch(url2)
    if not soup:
        return dept

    faculty = []
    seen = set()

    for tag in soup.find_all(["td", "h3", "h4", "h5", "strong", "a"]):
        text = _clean(tag.get_text())
        if _is_name(text) and text not in seen and "404" not in text:
            seen.add(text)
            member: dict[str, Any] = {"name": text, "designation": "Faculty"}
            # Try to find designation nearby
            parent = tag.parent
            if parent:
                for sib in parent.find_all(["td", "span", "p"]):
                    sib_t = _clean(sib.get_text())
                    if any(k in sib_t.lower() for k in ["professor", "lecturer", "assistant"]) and sib_t != text:
                        member["designation"] = _classify_designation(sib_t)
                        break
            faculty.append(member)

    if faculty:
        dept["faculty"] = faculty
        dept["faculty_count"] = len(faculty)
        logger.info(f"[NIT Srinagar] {dept_name}: {len(faculty)} faculty")
    return dept


def scrape_nit_srinagar() -> list[dict[str, Any]]:
    logger.info("[NIT Srinagar] Starting scrape...")
    departments = []
    for dept_name, (item_id, dept_id) in _NITSRI_DEPARTMENTS.items():
        try:
            dept = _scrape_nitsri_dept(dept_name, item_id, dept_id)
            departments.append(dept)
            time.sleep(1.5)
        except Exception as e:
            logger.error(f"[NIT Srinagar] Error {dept_name}: {e}")
            departments.append({"name": dept_name})
    return departments


# ══════════════════════════════════════════════════════════════════════════════
# MANIT BHOPAL
# ══════════════════════════════════════════════════════════════════════════════

_MANIT_BASE = "https://www.manit.ac.in"
_MANIT_DEPT_PATHS = {
    "Architecture & Town Planning": "/architecture-town-planning-department",
    "Chemical Engineering": "/chemical-engineering-department",
    "Chemistry": "/chemistry-department",
    "Civil Engineering": "/civil-engineering-department",
    "Computer Science & Engineering": "/content/computer-science-engineering",
    "Electrical Engineering": "/electrical-engineering-department",
    "Electronics & Communication Engineering": "/electronics-communication-engineering-department",
    "Humanities & Social Sciences": "/humanities-social-sciences-department",
    "Mathematics": "/mathematics-department",
    "Mechanical Engineering": "/mechanical-engineering-department",
    "Metallurgical & Materials Engineering": "/metallurgical-materials-engineering-department",
    "Physics": "/physics-department",
    "Bioinformatics & Biotechnology": "/bioinformatics-biotechnology-department",
    "Management Studies": "/management-studies-department",
    "Information Technology": "/information-technology-department",
}


def _scrape_manit_dept(dept_name: str, path: str) -> dict[str, Any]:
    dept: dict[str, Any] = {"name": dept_name}
    soup = _fetch(_MANIT_BASE + path, verify=False)
    if not soup:
        return dept

    faculty = []
    seen = set()

    # MANIT faculty listing is usually in div/table structures
    for tag in soup.find_all(["h3", "h4", "h5", "strong", "b", "td", "a"]):
        text = _clean(tag.get_text())
        if _is_name(text) and text not in seen and len(text) < 70:
            seen.add(text)
            member: dict[str, Any] = {"name": text, "designation": "Faculty"}
            parent = tag.parent
            if parent:
                for sib in parent.find_all(["p", "span", "small", "td"]):
                    sib_t = _clean(sib.get_text())
                    if any(k in sib_t.lower() for k in ["professor", "lecturer", "associate", "assistant"]) and sib_t != text:
                        member["designation"] = _classify_designation(sib_t)
                        break
            faculty.append(member)

    if faculty:
        dept["faculty"] = faculty
        dept["faculty_count"] = len(faculty)
        logger.info(f"[MANIT] {dept_name}: {len(faculty)} faculty")
    return dept


def scrape_manit_bhopal() -> list[dict[str, Any]]:
    logger.info("[MANIT Bhopal] Starting scrape...")
    departments = []
    for dept_name, path in _MANIT_DEPT_PATHS.items():
        try:
            dept = _scrape_manit_dept(dept_name, path)
            departments.append(dept)
            time.sleep(1)
        except Exception as e:
            logger.error(f"[MANIT] Error {dept_name}: {e}")
            departments.append({"name": dept_name})
    return departments


# ══════════════════════════════════════════════════════════════════════════════
# VNIT NAGPUR  (SSL verify=False required)
# ══════════════════════════════════════════════════════════════════════════════

_VNIT_BASE = "https://vnit.ac.in"
# Faculty pages discovered by probing vnit.ac.in navigation
_VNIT_DEPT_PATHS = {
    "Civil Engineering": "/engineering/civil/faculty/",
    "Computer Science & Engineering": "/engineering/cse/faculty/",
    "Chemical Engineering": "/engineering/chemical/faculty/",
    "Electrical Engineering": "/engineering/electrical/faculty/",
    "Electronics & Communication Engineering": "/engineering/ece/faculty/",
    "Mathematics": "/basic_science/maths/faculty/",
    "Mechanical Engineering": "/engineering/mech/faculty/",
    "Metallurgical & Materials Engineering": "/engineering/meta/faculty/",
    "Physics": "/basic_science/phy/faculty/",
    "Chemistry": "/basic_science/chemistry/faculty/",
    "Applied Mechanics": "/engineering/apm/faculty/",
}


def _scrape_vnit_dept(dept_name: str, path: str) -> dict[str, Any]:
    dept: dict[str, Any] = {"name": dept_name}
    # path already points to the /faculty/ page
    soup = _fetch(_VNIT_BASE + path, verify=False)
    if not soup:
        return dept

    faculty = []
    seen = set()

    # VNIT faculty pages use <h3> for faculty names (confirmed by probing)
    for tag in soup.find_all("h3"):
        text = _clean(tag.get_text())
        if _is_name(text) and text not in seen and len(text) < 80:
            seen.add(text)
            member: dict[str, Any] = {"name": text, "designation": "Faculty"}
            # Look for designation in nearby siblings/parent content
            parent = tag.find_parent(["div", "article", "section"])
            if parent:
                for sib in parent.find_all(["p", "span", "small", "h4", "h5"]):
                    sib_t = _clean(sib.get_text())
                    if any(k in sib_t.lower() for k in ["professor", "lecturer", "associate", "assistant"]) and sib_t != text and len(sib_t) < 60:
                        member["designation"] = _classify_designation(sib_t)
                        break
            faculty.append(member)

    if faculty:
        dept["faculty"] = faculty
        dept["faculty_count"] = len(faculty)
        logger.info(f"[VNIT] {dept_name}: {len(faculty)} faculty")
    else:
        logger.warning(f"[VNIT] {dept_name}: 0 faculty found at {path}")
    return dept


def scrape_vnit_nagpur() -> list[dict[str, Any]]:
    logger.info("[VNIT Nagpur] Starting scrape (SSL verify=False)...")
    departments = []
    for dept_name, path in _VNIT_DEPT_PATHS.items():
        try:
            dept = _scrape_vnit_dept(dept_name, path)
            departments.append(dept)
            time.sleep(1)
        except Exception as e:
            logger.error(f"[VNIT] Error {dept_name}: {e}")
            departments.append({"name": dept_name})
    return departments


# ══════════════════════════════════════════════════════════════════════════════
# NIT DURGAPUR
# ══════════════════════════════════════════════════════════════════════════════

_NITDGP_BASE = "https://www.nitdgp.ac.in"
_NITDGP_DEPT_PATHS = {
    "Biotechnology": "/department/bt",
    "Chemical Engineering": "/department/ch",
    "Chemistry": "/department/cy",
    "Civil Engineering": "/department/ce",
    "Computer Science & Engineering": "/department/cs",
    "Earth & Environmental Science": "/department/ee_env",
    "Electrical Engineering": "/department/ee",
    "Electronics & Communication Engineering": "/department/ec",
    "Humanities & Social Sciences": "/department/hs",
    "Mathematics": "/department/ma",
    "Mechanical Engineering": "/department/me",
    "Metallurgical & Materials Engineering": "/department/mm",
    "Physics": "/department/ph",
    "Management Studies": "/department/ms",
}


def _scrape_nitdgp_dept(dept_name: str, path: str) -> dict[str, Any]:
    dept: dict[str, Any] = {"name": dept_name}
    soup = _fetch(_NITDGP_BASE + path, retries=0, timeout=6)
    if not soup:
        return dept

    faculty = []
    seen = set()

    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) >= 2:
            text = _clean(cells[0].get_text())
            if _is_name(text) and text not in seen:
                seen.add(text)
                member: dict[str, Any] = {"name": text}
                desig_text = _clean(cells[1].get_text())
                member["designation"] = _classify_designation(desig_text) if desig_text else "Faculty"
                faculty.append(member)

    if not faculty:
        for tag in soup.find_all(["h3", "h4", "h5", "strong", "b"]):
            text = _clean(tag.get_text())
            if _is_name(text) and text not in seen:
                seen.add(text)
                faculty.append({"name": text, "designation": "Faculty"})

    if faculty:
        dept["faculty"] = faculty
        dept["faculty_count"] = len(faculty)
        logger.info(f"[NIT Durgapur] {dept_name}: {len(faculty)} faculty")
    return dept


def scrape_nit_durgapur() -> list[dict[str, Any]]:
    logger.info("[NIT Durgapur] Starting scrape...")
    departments = []
    for dept_name, path in _NITDGP_DEPT_PATHS.items():
        try:
            dept = _scrape_nitdgp_dept(dept_name, path)
            departments.append(dept)
            time.sleep(1.5)
        except Exception as e:
            logger.error(f"[NIT Durgapur] Error {dept_name}: {e}")
            departments.append({"name": dept_name})
    return departments


# ══════════════════════════════════════════════════════════════════════════════
# NIT JAMSHEDPUR
# ══════════════════════════════════════════════════════════════════════════════

_NITJSR_BASE = "https://www.nitjsr.ac.in"
_NITJSR_DEPT_PATHS = {
    "Chemical Engineering": "/department/ch",
    "Chemistry": "/department/cy",
    "Civil Engineering": "/department/ce",
    "Computer Science & Engineering": "/department/cs",
    "Electrical Engineering": "/department/ee",
    "Electronics & Communication Engineering": "/department/ec",
    "Humanities & Social Sciences": "/department/hss",
    "Mathematics": "/department/ma",
    "Mechanical Engineering": "/department/me",
    "Metallurgical & Materials Engineering": "/department/mm",
    "Physics": "/department/phy",
    "Production & Industrial Engineering": "/department/pi",
}


def _scrape_nitjsr_dept(dept_name: str, path: str) -> dict[str, Any]:
    dept: dict[str, Any] = {"name": dept_name}
    soup = _fetch(_NITJSR_BASE + path, timeout=25)
    if not soup:
        return dept

    faculty = []
    seen = set()

    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) >= 2:
            text = _clean(cells[0].get_text())
            if _is_name(text) and text not in seen:
                seen.add(text)
                member: dict[str, Any] = {"name": text}
                desig_text = _clean(cells[1].get_text())
                member["designation"] = _classify_designation(desig_text) if desig_text else "Faculty"
                faculty.append(member)

    if not faculty:
        for tag in soup.find_all(["h3", "h4", "strong"]):
            text = _clean(tag.get_text())
            if _is_name(text) and text not in seen:
                seen.add(text)
                faculty.append({"name": text, "designation": "Faculty"})

    if faculty:
        dept["faculty"] = faculty
        dept["faculty_count"] = len(faculty)
        logger.info(f"[NIT Jamshedpur] {dept_name}: {len(faculty)} faculty")
    return dept


def scrape_nit_jamshedpur() -> list[dict[str, Any]]:
    logger.info("[NIT Jamshedpur] Starting scrape...")
    departments = []
    for dept_name, path in _NITJSR_DEPT_PATHS.items():
        try:
            dept = _scrape_nitjsr_dept(dept_name, path)
            departments.append(dept)
            time.sleep(1.5)
        except Exception as e:
            logger.error(f"[NIT Jamshedpur] Error {dept_name}: {e}")
            departments.append({"name": dept_name})
    return departments


# ══════════════════════════════════════════════════════════════════════════════
# NIT WARANGAL  (JavaScript-heavy; we do best-effort static scrape)
# ══════════════════════════════════════════════════════════════════════════════

_NITW_BASE = "https://www.nitw.ac.in"
_NITW_DEPT_PATHS = {
    "Biotechnology": "/page/?url=BTdeptpage",
    "Chemical Engineering": "/page/?url=CEDeptpage",
    "Chemistry": "/page/?url=CHdeptpage",
    "Civil Engineering": "/page/?url=CLdeptpage",
    "Computer Science & Engineering": "/page/?url=CSEdeptpage",
    "Electrical Engineering": "/page/?url=EEdeptpage",
    "Electronics & Communication Engineering": "/page/?url=ECEdeptpage",
    "Humanities & Social Sciences": "/page/?url=HSSdeptpage",
    "Mathematics": "/page/?url=MAdeptpage",
    "Mechanical Engineering": "/page/?url=MEdeptpage",
    "Metallurgical & Materials Engineering": "/page/?url=MEdeptpageMM",
    "Physics": "/page/?url=PHdeptpage",
    "Management Studies": "/page/?url=MSdeptpage",
}


def _scrape_nitw_dept(dept_name: str, path: str) -> dict[str, Any]:
    dept: dict[str, Any] = {"name": dept_name}
    soup = _fetch(_NITW_BASE + path, timeout=25)
    if not soup:
        return dept

    faculty = []
    seen = set()

    for tag in soup.find_all(["h3", "h4", "h5", "strong", "b", "td", "a"]):
        text = _clean(tag.get_text())
        if _is_name(text) and text not in seen and len(text) < 70:
            seen.add(text)
            member: dict[str, Any] = {"name": text, "designation": "Faculty"}
            parent = tag.parent
            if parent:
                for sib in parent.find_all(["p", "span", "small", "td"]):
                    sib_t = _clean(sib.get_text())
                    if any(k in sib_t.lower() for k in ["professor", "lecturer"]) and sib_t != text:
                        member["designation"] = _classify_designation(sib_t)
                        break
            faculty.append(member)

    if faculty:
        dept["faculty"] = faculty
        dept["faculty_count"] = len(faculty)
        logger.info(f"[NIT Warangal] {dept_name}: {len(faculty)} faculty")
    return dept


def scrape_nit_warangal() -> list[dict[str, Any]]:
    logger.info("[NIT Warangal] Starting scrape (static HTML; JS may limit data)...")
    departments = []
    for dept_name, path in _NITW_DEPT_PATHS.items():
        try:
            dept = _scrape_nitw_dept(dept_name, path)
            departments.append(dept)
            time.sleep(1)
        except Exception as e:
            logger.error(f"[NIT Warangal] Error {dept_name}: {e}")
            departments.append({"name": dept_name})
    return departments


# ══════════════════════════════════════════════════════════════════════════════
# NIT JALANDHAR
# ══════════════════════════════════════════════════════════════════════════════

_NITJ_BASE = "https://www.nitj.ac.in"
_NITJ_DEPT_PATHS = {
    "Biotechnology": "/index.php/nitj_bt/Faculty",
    "Chemical Engineering": "/index.php/nitj_che/Faculty",
    "Chemistry": "/index.php/nitj_cy/Faculty",
    "Civil Engineering": "/index.php/nitj_ce/Faculty",
    "Computer Science & Engineering": "/index.php/nitj_cse/Faculty",
    "Electrical Engineering": "/index.php/nitj_ee/Faculty",
    "Electronics & Communication Engineering": "/index.php/nitj_ece/Faculty",
    "Humanities & Social Sciences": "/index.php/nitj_hss/Faculty",
    "Industrial & Production Engineering": "/index.php/nitj_ipe/Faculty",
    "Mathematics": "/index.php/nitj_ma/Faculty",
    "Mechanical Engineering": "/index.php/nitj_me/Faculty",
    "Physics": "/index.php/nitj_phy/Faculty",
    "Textile Technology": "/index.php/nitj_tt/Faculty",
}


def _scrape_nitj_dept(dept_name: str, path: str) -> dict[str, Any]:
    dept: dict[str, Any] = {"name": dept_name}
    soup = _fetch(_NITJ_BASE + path, timeout=25)
    if not soup:
        return dept

    faculty = []
    seen = set()

    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) >= 2:
            text = _clean(cells[0].get_text())
            if _is_name(text) and text not in seen:
                seen.add(text)
                member: dict[str, Any] = {"name": text}
                desig_text = _clean(cells[1].get_text())
                member["designation"] = _classify_designation(desig_text) if desig_text else "Faculty"
                if len(cells) > 2:
                    email_text = _clean(cells[2].get_text())
                    if "@" in email_text:
                        member["email"] = email_text
                faculty.append(member)

    if not faculty:
        for tag in soup.find_all(["h3", "h4", "strong", "b"]):
            text = _clean(tag.get_text())
            if _is_name(text) and text not in seen:
                seen.add(text)
                faculty.append({"name": text, "designation": "Faculty"})

    if faculty:
        dept["faculty"] = faculty
        dept["faculty_count"] = len(faculty)
        logger.info(f"[NIT Jalandhar] {dept_name}: {len(faculty)} faculty")
    return dept


def scrape_nit_jalandhar() -> list[dict[str, Any]]:
    logger.info("[NIT Jalandhar] Starting scrape...")
    departments = []
    for dept_name, path in _NITJ_DEPT_PATHS.items():
        try:
            dept = _scrape_nitj_dept(dept_name, path)
            departments.append(dept)
            time.sleep(1)
        except Exception as e:
            logger.error(f"[NIT Jalandhar] Error {dept_name}: {e}")
            departments.append({"name": dept_name})
    return departments


# ══════════════════════════════════════════════════════════════════════════════
# NIT PUDUCHERRY
# ══════════════════════════════════════════════════════════════════════════════

_NITPY_BASE = "https://www.nitpy.ac.in"
_NITPY_DEPT_PATHS = {
    "Chemical Engineering": "/department/chemical",
    "Chemistry": "/department/chemistry",
    "Civil Engineering": "/department/civil",
    "Computer Science & Engineering": "/department/cse",
    "Electrical Engineering": "/department/eee",
    "Electronics & Communication Engineering": "/department/ece",
    "Humanities & Social Sciences": "/department/hss",
    "Mathematics": "/department/maths",
    "Mechanical Engineering": "/department/mech",
    "Physics": "/department/physics",
}


def _scrape_nitpy_dept(dept_name: str, path: str) -> dict[str, Any]:
    dept: dict[str, Any] = {"name": dept_name}
    # NIT Puducherry has SSL cert issues — use verify=False
    soup = _fetch(_NITPY_BASE + path, timeout=20, verify=False)
    if not soup:
        return dept

    faculty = []
    seen = set()

    for tag in soup.find_all(["h3", "h4", "h5", "strong", "b", "td"]):
        text = _clean(tag.get_text())
        if _is_name(text) and text not in seen and len(text) < 70:
            seen.add(text)
            member: dict[str, Any] = {"name": text, "designation": "Faculty"}
            parent = tag.parent
            if parent:
                for sib in parent.find_all(["p", "span", "small", "td"]):
                    sib_t = _clean(sib.get_text())
                    if any(k in sib_t.lower() for k in ["professor", "lecturer"]) and sib_t != text:
                        member["designation"] = _classify_designation(sib_t)
                        break
            faculty.append(member)

    if faculty:
        dept["faculty"] = faculty
        dept["faculty_count"] = len(faculty)
        logger.info(f"[NIT Puducherry] {dept_name}: {len(faculty)} faculty")
    return dept


def scrape_nit_puducherry() -> list[dict[str, Any]]:
    logger.info("[NIT Puducherry] Starting scrape...")
    departments = []
    for dept_name, path in _NITPY_DEPT_PATHS.items():
        try:
            dept = _scrape_nitpy_dept(dept_name, path)
            departments.append(dept)
            time.sleep(1)
        except Exception as e:
            logger.error(f"[NIT Puducherry] Error {dept_name}: {e}")
            departments.append({"name": dept_name})
    return departments


# ══════════════════════════════════════════════════════════════════════════════
# NIT ANDHRA PRADESH
# ══════════════════════════════════════════════════════════════════════════════

_NITAP_BASE = "https://www.nitandhra.ac.in"
_NITAP_DEPT_PATHS = {
    "Chemical Engineering": "/dept/che",
    "Civil Engineering": "/dept/civil",
    "Computer Science & Engineering": "/dept/cse",
    "Electrical Engineering": "/dept/eee",
    "Electronics & Communication Engineering": "/dept/ece",
    "Mathematics": "/dept/maths",
    "Mechanical Engineering": "/dept/mech",
    "Physics": "/dept/physics",
    "Chemistry": "/dept/chemistry",
}


def _scrape_nitap_dept(dept_name: str, path: str) -> dict[str, Any]:
    dept: dict[str, Any] = {"name": dept_name}
    soup = _fetch(_NITAP_BASE + path, timeout=20)
    if not soup:
        return dept

    faculty = []
    seen = set()

    for tag in soup.find_all(["h3", "h4", "h5", "strong", "b", "td"]):
        text = _clean(tag.get_text())
        if _is_name(text) and text not in seen and len(text) < 70:
            seen.add(text)
            member: dict[str, Any] = {"name": text, "designation": "Faculty"}
            parent = tag.parent
            if parent:
                for sib in parent.find_all(["p", "span", "td"]):
                    sib_t = _clean(sib.get_text())
                    if any(k in sib_t.lower() for k in ["professor", "lecturer"]) and sib_t != text:
                        member["designation"] = _classify_designation(sib_t)
                        break
            faculty.append(member)

    if faculty:
        dept["faculty"] = faculty
        dept["faculty_count"] = len(faculty)
        logger.info(f"[NIT Andhra] {dept_name}: {len(faculty)} faculty")
    return dept


def scrape_nit_andhra() -> list[dict[str, Any]]:
    logger.info("[NIT Andhra Pradesh] Starting scrape...")
    departments = []
    for dept_name, path in _NITAP_DEPT_PATHS.items():
        try:
            dept = _scrape_nitap_dept(dept_name, path)
            departments.append(dept)
            time.sleep(1)
        except Exception as e:
            logger.error(f"[NIT Andhra] Error {dept_name}: {e}")
            departments.append({"name": dept_name})
    return departments


# ══════════════════════════════════════════════════════════════════════════════
# MASTER REGISTRY  — maps JSON file slug → scraper function
# ══════════════════════════════════════════════════════════════════════════════

import json
import os
from pathlib import Path

_SCRAPER_REGISTRY: dict[str, Any] = {
    "nit-trichy": scrape_nit_trichy,
    "nit-surathkal": scrape_nitk_surathkal,
    "nit-calicut": scrape_nit_calicut,
    "nit-rourkela": scrape_nit_rourkela,
    "nit-goa": scrape_nit_goa,
    "nit-raipur": scrape_nit_raipur,
    "mnnit-allahabad": scrape_mnnit_allahabad,
    "mnit-jaipur": scrape_mnit_jaipur,
    "nit-patna": scrape_nit_patna,
    "nit-srinagar": scrape_nit_srinagar,
    "manit-bhopal": scrape_manit_bhopal,
    "vnit-nagpur": scrape_vnit_nagpur,
    "nit-durgapur": scrape_nit_durgapur,
    "nit-jamshedpur": scrape_nit_jamshedpur,
    "nit-warangal": scrape_nit_warangal,
    "nit-jalandhar": scrape_nit_jalandhar,
    "nit-puducherry": scrape_nit_puducherry,
    "nit-andhra-pradesh": scrape_nit_andhra,
}


def _find_json_file(parsed_dir: Path, slug: str) -> Path | None:
    """Find the _structured.json file for the given slug (fuzzy match)."""
    slug_clean = slug.lower().replace("-", "")
    for f in parsed_dir.glob("*_structured.json"):
        name = f.stem.replace("_structured", "").lower().replace("-", "").replace("_", "")
        if slug_clean in name or name in slug_clean:
            return f
    return None


def _merge_departments(existing: list, scraped: list) -> list:
    """Merge scraped departments into existing list, prioritizing scraped data."""
    existing = existing or []
    scraped = scraped or []
    existing_by_name = {d.get("name", "").lower(): d for d in existing if d}
    for dept in scraped:
        key = dept.get("name", "").lower()
        if key in existing_by_name:
            # Update existing with scraped data (scraped takes priority for faculty)
            if dept.get("faculty"):
                existing_by_name[key]["faculty"] = dept["faculty"]
                existing_by_name[key]["faculty_count"] = dept.get("faculty_count", len(dept["faculty"]))
        else:
            existing_by_name[key] = dept
    return list(existing_by_name.values())


def run_all_scrapers(parsed_dir: str | None = None, target: str | None = None) -> None:
    """Run all NIT scrapers and update the corresponding _structured.json files.

    Args:
        parsed_dir: Path to the parsed data directory (auto-detected if None).
        target: If given, only run scraper for this slug (e.g. 'nit-trichy').
    """
    if parsed_dir is None:
        # Resolve relative to this file
        here = Path(__file__).parent
        parsed_dir_path = here.parent / "data" / "parsed"
    else:
        parsed_dir_path = Path(parsed_dir)

    registry = {target: _SCRAPER_REGISTRY[target]} if target else _SCRAPER_REGISTRY

    for slug, scraper_fn in registry.items():
        logger.info(f"\n{'='*60}\nRunning scraper: {slug}\n{'='*60}")
        try:
            departments = scraper_fn()
        except Exception as e:
            logger.error(f"Scraper {slug} crashed: {e}")
            continue

        if not departments:
            logger.warning(f"No data returned for {slug}")
            continue

        # Find JSON file
        json_file = _find_json_file(parsed_dir_path, slug)
        if not json_file:
            logger.warning(f"No JSON file found for {slug} in {parsed_dir_path}")
            # List available files to help debug
            available = [f.name for f in parsed_dir_path.glob("*_structured.json")]
            logger.info(f"  Available files: {available[:10]}")
            continue

        # Load existing data
        with open(json_file, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        # Merge departments
        existing_depts = data.get("departments") or []
        merged = _merge_departments(existing_depts, departments)
        data["departments"] = merged
        data["department_count"] = len(merged)

        # Compute total faculty
        total_fac = sum(len(d.get("faculty", [])) for d in merged)
        data["total_faculty"] = total_fac

        # Save back
        with open(json_file, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)

        logger.info(f"✅ Updated {json_file.name}: {len(merged)} depts, {total_fac} faculty total")


if __name__ == "__main__":
    import sys
    target_slug = sys.argv[1] if len(sys.argv) > 1 else None
    run_all_scrapers(target=target_slug)
