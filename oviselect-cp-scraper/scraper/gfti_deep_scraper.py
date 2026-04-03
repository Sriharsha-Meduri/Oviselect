"""Deep scraper for GFTIs — faculty and departments.

Scrapes faculty listings from official GFTI websites and merges the data
into the `departments` field of data/parsed/gfti-*_structured.json files.

Institutes covered
------------------
- BIT Mesra       (edudepartment/facultyList/{id} pattern)
- SOE Tezpur      (department-specific faculty pages)
- PEC Chandigarh  (sponsored-research PI names + department stubs)
- NIFTEM Thanjavur (departments.php + carfaculty.php)
- IIEST Shibpur   (DNS unreachable — keep existing data)
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from loguru import logger

from scraper.fetch_utils import fetch as _fetch  # Scrapling-backed, requests fallback


def _clean(text: str | None) -> str:
    if not text:
        return ""
    return " ".join(text.split())


def _dept(name: str, faculty: list[dict]) -> dict:
    return {
        "name": name,
        "faculty": faculty,
        "faculty_count": len(faculty),
    }


# ══════════════════════════════════════════════════════════════════════════════
# BIT MESRA
# ══════════════════════════════════════════════════════════════════════════════

# Academic department IDs extracted from homepage navigation
_BIT_DEPT_IDS: dict[int, str] = {
    49: "Architecture and Planning",
    50: "Civil and Environmental Engineering",
    51: "Bioengineering and Biotechnology",
    69: "Chemical Engineering",
    70: "Computer Science and Engineering",
    71: "Electrical and Electronics Engineering",
    72: "Electronics and Communication Engineering",
    73: "Hotel Management and Catering Technology",
    74: "Mechanical Engineering",
    75: "Management Studies",
    76: "Production and Industrial Engineering",
    77: "Pharmaceutical Sciences and Technology",
    78: "Remote Sensing and Geoinformatics",
    140: "Chemistry",
    167: "Space Engineering and Rocketry",
    168: "Mathematics",
    169: "Physics",
    423: "Quantitative Economics and Data Science",
    500: "Food Engineering and Technology",
    505: "Humanities and Social Sciences",
}


def _parse_bit_faculty_page(soup: BeautifulSoup) -> list[dict]:
    """Parse BIT Mesra's facultyList page."""
    text = soup.get_text(" ", strip=True)
    faculty: list[dict] = []

    # Each faculty entry is separated by "Joined :" date blocks
    # Pattern: "Joined : DD-Mon-YYYY  Designation  Dr./Prof. Name  : phone  : email"
    blocks = re.split(r"Joined\s*:\s*\d{1,2}-[A-Za-z]+-\d{4}", text)
    for block in blocks[1:]:  # first is page header
        block = block.strip()
        if not block:
            continue

        # Extract designation (first line-ish)
        desig_match = re.match(
            r"^(Professor[^D]*?|Associate Professor[^D]*?|Assistant Professor[^D]*?"
            r"|Lecturer[^D]*?|Reader[^D]*?)\s+(Dr\.|Prof\.|Mr\.|Ms\.)",
            block,
        )
        designation = _clean(desig_match.group(1)) if desig_match else ""

        # Extract name
        name_match = re.search(
            r"(Dr\.|Prof\.|Mr\.|Ms\.)\s+([A-Z][a-zA-Z\s\.]+?)(?=\s*:|\s+Qualification|\s+Area)",
            block,
        )
        name = ""
        if name_match:
            name = _clean(name_match.group(1) + " " + name_match.group(2))

        # Extract phone
        phone_match = re.search(r":\s*(\d{7,12})\s*:", block)
        phone = phone_match.group(1) if phone_match else None

        # Extract email
        email_match = re.search(r":\s*([\w.\-]+@[\w.\-]+\.\w+)", block)
        email = email_match.group(1) if email_match else None

        # Extract qualification
        qual_match = re.search(r"Qualification\s*[→:]\s*([^A-Z]+?)(?=Area|Field|View|$)", block)
        qualification = _clean(qual_match.group(1)) if qual_match else None

        # Extract area of interest
        area_match = re.search(r"Area of Interest\s*[→:]\s*(.+?)(?=Field of Interest|View Profile|$)", block)
        research_interests = []
        if area_match:
            raw = _clean(area_match.group(1))
            research_interests = [x.strip() for x in re.split(r"[,\n]", raw) if x.strip()]

        if name:
            faculty.append({
                "name": name,
                "designation": designation or None,
                "email": email,
                "phone": phone,
                "qualification": qualification,
                "research_interests": research_interests or None,
            })

    return faculty


def scrape_bit_mesra() -> list[dict]:
    """Scrape all academic departments from BIT Mesra."""
    logger.info("Scraping BIT Mesra faculty...")
    departments: list[dict] = []

    for dept_id, dept_name in _BIT_DEPT_IDS.items():
        url = f"https://www.bitmesra.ac.in/edudepartment/facultyList/1/{dept_id}"
        soup = _fetch(url)
        if not soup:
            logger.warning(f"  Skipping dept {dept_id} ({dept_name}) — fetch failed")
            departments.append(_dept(dept_name, []))
            continue

        faculty = _parse_bit_faculty_page(soup)
        logger.info(f"  {dept_name}: {len(faculty)} faculty")
        departments.append(_dept(dept_name, faculty))
        time.sleep(0.3)

    return departments


# ══════════════════════════════════════════════════════════════════════════════
# SOE TEZPUR (Tezpur University School of Engineering)
# ══════════════════════════════════════════════════════════════════════════════

def _parse_tezpur_civil(soup: BeautifulSoup) -> list[dict]:
    """Parse Civil dept regular_faculty.php — field-labelled format.

    Format: Dr. Name Designation: X Specialization: Y Research Interest: Z
            Date of joining: YYYY-MM-DD Qualification: Q  : phone : email Profile
    """
    text = soup.get_text(" ", strip=True)
    faculty: list[dict] = []
    # Split on "Dr." occurrences after the page header
    blocks = re.split(r"(?=Dr\.\s+[A-Z])", text)
    email_re = re.compile(r"[\w.\-]+@[\w.\-]+\.\w+")
    phone_re = re.compile(r"\b0\d{9,11}\b|\b\+91[\s\-]\d+")

    for block in blocks:
        block = block.strip()
        if not block.startswith("Dr."):
            continue
        nm = re.match(r"(Dr\.\s+[A-Z][a-zA-Z\s\.]+?)(?=\s+Designation|\s+Professor|\s+Associate|\s+Assistant)", block)
        if not nm:
            continue
        name = _clean(nm.group(1))
        desig_m = re.search(r"Designation\s*:\s*([^S]+?)(?=\s+Specialization|\s+Research|\s+Date)", block)
        desig = _clean(desig_m.group(1)) if desig_m else None
        interest_m = re.search(r"Research Interest\s*:\s*(.+?)(?=\s+Date of joining|\s+Qualification|\s*$)", block)
        interests = []
        if interest_m:
            raw = _clean(interest_m.group(1))
            interests = [x.strip() for x in re.split(r"[,;]", raw) if x.strip()]
        qual_m = re.search(r"Qualification\s*:\s*(.+?)(?=\s*:\s*\d|\s*$)", block)
        qual = _clean(qual_m.group(1)) if qual_m else None
        emails = email_re.findall(block)
        email = emails[0] if emails else None
        faculty.append({
            "name": name,
            "designation": desig,
            "email": email,
            "qualification": qual,
            "research_interests": interests or None,
        })
    return faculty


def _parse_tezpur_ece(soup: BeautifulSoup) -> list[dict]:
    """Parse ECE people.html — card-based without Dr. prefix.

    Each card div: 'Name  Professor [& Head]  email  +phone  Room: X  Research Areas: Y'
    """
    faculty: list[dict] = []
    seen: set[str] = set()
    email_re = re.compile(r"[\w.\-]+@[\w.\-]+\.\w+")
    desig_re = re.compile(r"(Professor[^+\n@]+?|Associate Professor[^+\n@]+?|Assistant Professor[^+\n@]+?|Lecturer[^+\n@]+?)(?=\s+[\w.]+@|\s*\+91|\s*$)")
    area_re = re.compile(r"Research Areas?\s*:\s*(.+?)(?=\s+Profile|\s*$)")

    for div in soup.find_all("div"):
        text = _clean(div.get_text())
        # Must have email and designation keyword, and be a leaf-ish card
        if not email_re.search(text):
            continue
        if not any(k in text for k in ["Professor", "Lecturer"]):
            continue
        if len(text) < 30 or len(text) > 600:
            continue

        emails = email_re.findall(text)
        desig_m = desig_re.search(text)
        area_m = area_re.search(text)

        # Name is the part before the first designation keyword
        desig_pos = re.search(r"\b(Professor|Lecturer|Associate|Assistant)\b", text)
        if not desig_pos:
            continue
        name_raw = text[:desig_pos.start()].strip()
        # Clean up stray prefixes
        name = re.sub(r"\s+", " ", name_raw).strip()
        if not name or name in seen or len(name) < 5:
            continue
        seen.add(name)

        research = []
        if area_m:
            research = [x.strip() for x in re.split(r"[;,]", _clean(area_m.group(1))) if x.strip()]

        faculty.append({
            "name": name,
            "designation": _clean(desig_m.group(1)) if desig_m else None,
            "email": emails[0] if emails else None,
            "research_interests": research or None,
        })
    return faculty


def _parse_tezpur_mech(soup: BeautifulSoup) -> list[dict]:
    """Parse Mech faculty.html — numbered list format.

    Format: '1. Name, degree (Institute) Professor Specialization: X
             Extn No: N E-Mail: email Homepage: ...'
    """
    text = soup.get_text(" ", strip=True)
    faculty: list[dict] = []
    seen: set[str] = set()
    email_re = re.compile(r"E-Mail\s*:\s*([\w.\-]+@[\w.\-]+\.\w+)")
    desig_re = re.compile(r"\b(Professor|Associate Professor|Assistant Professor|Lecturer)\b")
    spec_re = re.compile(r"Specialization\s*[:\s]+(.+?)(?=\s+Extn|\s+E-Mail|\s+Homepage|\s+Date|\s+\d+\.|\s*$)")

    # Split by numbered items "1. ", "2. ", etc.
    blocks = re.split(r"\b\d+\.\s+", text)
    for block in blocks[1:]:
        block = block.strip()
        # Name is "FirstLast, degree..." up to first comma or Professor keyword
        # pattern: "Tapan Kumar Gogoi, PhD (Tezpur University) Professor ..."
        nm_match = re.match(r"([A-Z][a-zA-Z\s]+?)(?:,\s*(?:PhD|MTech|ME|MSc|BE|BTech)|(?=\s+Professor|\s+Associate|\s+Assistant))", block)
        if not nm_match:
            continue
        name = _clean(nm_match.group(1))
        if name in seen or len(name) < 5:
            continue
        seen.add(name)
        email_m = email_re.search(block)
        desig_m = desig_re.search(block)
        spec_m = spec_re.search(block)
        specialization = [_clean(spec_m.group(1))] if spec_m else None
        faculty.append({
            "name": name,
            "designation": desig_m.group(1) if desig_m else None,
            "email": email_m.group(1) if email_m else None,
            "research_interests": specialization,
        })
    return faculty


_TEZPUR_DEPTS: list[tuple[str, str, str, str]] = [
    # (dept_name, base_url, faculty_page, parser_key)
    ("Civil Engineering",                   "http://www.tezu.ernet.in/dcivil/", "regular_faculty.php", "civil"),
    ("Electronics and Communication Engg",  "http://www.tezu.ernet.in/delect/", "people.html",         "ece"),
    ("Mechanical Engineering",              "http://www.tezu.ernet.in/dmech/",  "faculty.html",        "mech"),
    ("Electrical Engineering",              "http://www.tezu.ernet.in/dee/",    "people.html",         "ece"),
    ("Computer Science and Engineering",    "http://www.tezu.ernet.in/dcompsc/","people.html",         "ece"),
    ("Energy",                              "http://www.tezu.ernet.in/dener/",  "people.html",         "ece"),
    ("Food Engineering and Technology",     "http://www.tezu.ernet.in/dfpt/",   "people.html",         "ece"),
    ("Design",                              "http://www.tezu.ernet.in/design/", "people.html",         "ece"),
]

_TEZPUR_PARSERS = {
    "civil": _parse_tezpur_civil,
    "ece":   _parse_tezpur_ece,
    "mech":  _parse_tezpur_mech,
}

_TEZPUR_ALT_PAGES = ["people.html", "faculty.html", "regular_faculty.php", "faculty.php", "people.php"]


def scrape_soe_tezpur() -> list[dict]:
    """Scrape faculty from Tezpur University School of Engineering departments."""
    logger.info("Scraping SOE Tezpur faculty...")
    departments: list[dict] = []

    for dept_name, base, page, parser_key in _TEZPUR_DEPTS:
        soup = _fetch(base + page, timeout=12)
        if not soup:
            for alt in _TEZPUR_ALT_PAGES:
                if alt == page:
                    continue
                soup = _fetch(base + alt, timeout=8)
                if soup:
                    break
        if not soup:
            logger.warning(f"  {dept_name}: no faculty page found")
            departments.append(_dept(dept_name, []))
            continue

        parser = _TEZPUR_PARSERS[parser_key]
        faculty = parser(soup)
        logger.info(f"  {dept_name}: {len(faculty)} faculty")
        departments.append(_dept(dept_name, faculty))
        time.sleep(0.3)

    return departments


# ══════════════════════════════════════════════════════════════════════════════
# PEC CHANDIGARH
# ══════════════════════════════════════════════════════════════════════════════

_PEC_DEPTS = [
    ("Aerospace Engineering",           "aero"),
    ("Chemistry",                        "chemistry"),
    ("Civil Engineering",               "civil"),
    ("Computer Science and Engineering","cse"),
    ("Electrical Engineering",          "ee"),
    ("Electronics and Communication",   "ece"),
    ("Mathematics",                     "mathematics"),
    ("Physics",                         "physics"),
]


def _parse_pec_dept_page(soup: BeautifulSoup) -> list[dict]:
    """Extract faculty names from PEC department page text."""
    faculty: list[dict] = []
    text = soup.get_text(" ", strip=True)
    seen: set[str] = set()
    name_re = re.compile(r"(Dr\.|Prof\.|Mr\.|Ms\.)\s+([A-Z][a-zA-Z\s\.]{3,40}?)(?=\s{2,}|\s+(?:Professor|Associate|Assistant|Lecturer|HOD|Head|$))")
    email_re = re.compile(r"[\w.\-]+@[\w.\-]+\.\w+")
    desig_re = re.compile(r"(Professor[^,\n]*|Associate Professor[^,\n]*|Assistant Professor[^,\n]*|Lecturer[^,\n]*|HOD[^,\n]*)")

    for m in name_re.finditer(text):
        name = _clean(m.group(1) + " " + m.group(2))
        if name in seen or len(name) < 8:
            continue
        seen.add(name)
        surrounding = text[max(0, m.start()-50):m.end()+200]
        email_m = email_re.search(surrounding)
        desig_m = desig_re.search(surrounding)
        faculty.append({
            "name": name,
            "designation": _clean(desig_m.group(1)) if desig_m else None,
            "email": email_m.group() if email_m else None,
        })
    return faculty


def scrape_pec_chandigarh() -> list[dict]:
    """Scrape PEC Chandigarh departments and faculty."""
    logger.info("Scraping PEC Chandigarh faculty...")
    departments: list[dict] = []

    for dept_name, slug in _PEC_DEPTS:
        faculty: list[dict] = []
        # Try sub-page patterns
        for suffix in ["faculty", "people", "academics/faculty"]:
            soup = _fetch(f"https://www.pec.ac.in/{slug}/{suffix}", timeout=10)
            if soup:
                fac = _parse_pec_dept_page(soup)
                if fac:
                    faculty = fac
                    break

        # Fallback: main dept page
        if not faculty:
            soup = _fetch(f"https://www.pec.ac.in/{slug}", timeout=10)
            if soup:
                faculty = _parse_pec_dept_page(soup)

        logger.info(f"  {dept_name}: {len(faculty)} faculty")
        departments.append(_dept(dept_name, faculty))
        time.sleep(0.3)

    # Also scrape sponsored research for PI names as supplementary
    soup = _fetch("https://www.pec.ac.in/sponsored-research", timeout=12)
    if soup:
        text = soup.get_text(" ", strip=True)
        pi_matches = re.findall(r"(Dr\.|Prof\.)\s+([A-Z][a-zA-Z\s\.]{3,35}?)(?=\s*,|\s*\(|\s*Dept|\s{2,})", text)
        pi_names = {_clean(p[0] + " " + p[1]) for p in pi_matches if len(_clean(p[0] + " " + p[1])) > 8}
        if pi_names:
            logger.info(f"  PEC sponsored research PIs: {len(pi_names)} names found")

    return departments


# ══════════════════════════════════════════════════════════════════════════════
# NIFTEM THANJAVUR
# ══════════════════════════════════════════════════════════════════════════════

# Each tuple: (dept_name, page_slug)
_NIFTEM_DEPTS: list[tuple[str, str]] = [
    ("Food Process Engineering",            "food_process_engineering.php"),
    ("Food Process Technology",             "food_process_technology.php"),
    ("Food Safety and Quality Assurance",   "food_safety_and_quality_assurance.php"),
    ("Food Business Management",            "food_busniess_management.php"),
    ("Food Packaging and Storage Tech",     "food_package_storage_tech.php"),
    ("Food Plant Operations",               "fpo_incubation.php"),
]


def _parse_niftem_dept(soup: BeautifulSoup) -> list[dict]:
    """Parse NIFTEM dept page.

    Format: 'Dr. Name  Professor/Associate Professor email  Specialization: X'
    All faculty info is in a flat text block after the page header.
    """
    text = soup.get_text(" ", strip=True)
    # Find start after 'Faculty Members' marker
    idx = text.find("Faculty Members")
    if idx > 0:
        text = text[idx:]
    faculty: list[dict] = []
    seen: set[str] = set()
    email_re = re.compile(r"[\w.\-]+@[\w.\-]+\.\w+")
    desig_re = re.compile(r"(Professor[^@\n]*?|Associate Professor[^@\n]*?|Assistant Professor[^@\n]*?|Teaching Faculty[^@\n]*?|Lecturer[^@\n]*?)(?=\s+[\w.\-]+@|\s*$)")
    spec_re = re.compile(r"Specialization\s*:\s*([^\n]+?)(?=\s+(?:Dr\.|Staff|Shri|\Z))")

    # Split by name tokens "Dr. " occurrences
    blocks = re.split(r"(?=Dr\.\s+[A-Z])", text)
    for block in blocks:
        block = block.strip()
        if not block.startswith("Dr."):
            continue
        # Name ends before designation keyword
        nm_end = re.search(r"\b(Professor|Associate|Assistant|Teaching Faculty|Lecturer|Faculty)\b", block)
        if not nm_end:
            continue
        name_raw = block[:nm_end.start()].strip()
        # Remove trailing qualification bits like "(C)"
        name = re.sub(r"\s*\([^)]+\)\s*$", "", name_raw).strip()
        name = re.sub(r"\s+", " ", name)
        if name in seen or len(name) < 8:
            continue
        seen.add(name)
        emails = email_re.findall(block)
        desig_m = desig_re.search(block)
        spec_m = spec_re.search(block)
        faculty.append({
            "name": name,
            "designation": _clean(desig_m.group(1)) if desig_m else None,
            "email": emails[0] if emails else None,
            "research_interests": [_clean(spec_m.group(1))] if spec_m else None,
        })
    return faculty


def scrape_niftem_thanjavur() -> list[dict]:
    """Scrape NIFTEM-T faculty and departments."""
    logger.info("Scraping NIFTEM Thanjavur...")
    departments: list[dict] = []
    base = "https://www.niftem-t.ac.in/"

    for dept_name, slug in _NIFTEM_DEPTS:
        soup = _fetch(base + slug, timeout=15)
        if not soup:
            logger.warning(f"  {dept_name}: page not accessible")
            departments.append(_dept(dept_name, []))
            continue
        faculty = _parse_niftem_dept(soup)
        logger.info(f"  {dept_name}: {len(faculty)} faculty")
        departments.append(_dept(dept_name, faculty))
        time.sleep(0.3)

    return departments


# ══════════════════════════════════════════════════════════════════════════════
# IIEST SHIBPUR (DNS unreachable — no-op)
# ══════════════════════════════════════════════════════════════════════════════

def scrape_iiest_shibpur() -> list[dict]:
    """IIEST Shibpur is DNS-unreachable; return empty list to preserve existing data."""
    logger.warning("IIEST Shibpur: DNS resolution fails — skipping (existing data preserved)")
    return []


# ══════════════════════════════════════════════════════════════════════════════
# REGISTRY + MERGE + ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

_GFTI_REGISTRY: dict[str, Any] = {
    "bit-mesra":        scrape_bit_mesra,
    "soe-tezpur":       scrape_soe_tezpur,
    "pec-chandigarh":   scrape_pec_chandigarh,
    "niftem-thanjavur": scrape_niftem_thanjavur,
    "iiest-shibpur":    scrape_iiest_shibpur,
}


def _find_gfti_json(parsed_dir: Path, slug: str) -> Path | None:
    for candidate in parsed_dir.glob(f"*{slug}*_structured.json"):
        return candidate
    for candidate in parsed_dir.glob(f"{slug}*_structured.json"):
        return candidate
    # Fuzzy: match any file containing slug words
    parts = slug.replace("-", " ").split()
    for candidate in parsed_dir.glob("*_structured.json"):
        name = candidate.stem.lower()
        if all(p in name for p in parts):
            return candidate
    return None


def _merge_departments(existing: list[dict], scraped: list[dict]) -> list[dict]:
    existing_by_name = {d.get("name", "").lower(): d for d in existing}
    for dept in scraped:
        key = dept.get("name", "").lower()
        if key in existing_by_name:
            if dept.get("faculty"):
                existing_by_name[key]["faculty"] = dept["faculty"]
                existing_by_name[key]["faculty_count"] = dept.get("faculty_count", len(dept["faculty"]))
        else:
            existing_by_name[key] = dept
    return list(existing_by_name.values())


def run_all_gfti_deep_scrapers(
    parsed_dir: str | None = None,
    target: str | None = None,
) -> None:
    """Run all GFTI faculty scrapers and persist results to JSON files."""
    if parsed_dir is None:
        parsed_dir_path = Path(__file__).parent.parent / "data" / "parsed"
    else:
        parsed_dir_path = Path(parsed_dir)

    registry = {target: _GFTI_REGISTRY[target]} if target else _GFTI_REGISTRY

    for slug, scraper_fn in registry.items():
        logger.info(f"\n{'='*60}\nGFTI Deep scraper: {slug}\n{'='*60}")
        try:
            departments = scraper_fn()
        except Exception as e:
            logger.error(f"Scraper {slug} crashed: {e}")
            continue

        if not departments:
            logger.warning(f"No data returned for {slug} — existing JSON unchanged")
            continue

        json_file = _find_gfti_json(parsed_dir_path, slug)
        if not json_file:
            logger.warning(f"No JSON file found for slug '{slug}'")
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

        logger.info(f"✅ Updated {json_file.name}: {len(merged)} depts, {total_fac} faculty")


if __name__ == "__main__":
    import sys
    target_slug = sys.argv[1] if len(sys.argv) > 1 else None
    run_all_gfti_deep_scrapers(target=target_slug)

