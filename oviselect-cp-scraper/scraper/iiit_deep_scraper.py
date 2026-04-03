"""Deep scraper for IIITs — faculty and departments.

Scrapes faculty listings from official IIIT websites and merges the data
into the `departments` field of data/parsed/iiit-*_structured.json files.

Confirmed working sources
--------------------------
- IIIT Bhagalpur       (table rows)
- IIIT Kalyani         (section-based designation groups)
- IIIT Kota            (li elements + div dept/designation)
- IIIT Lucknow         (regex on full-page text)
- IIIT Surat           (JSON API)
- IIIT Pune            (regex on full-page text)
- IIITDM Kancheepuram  (regex on homepage news/highlights)
- IIIT Naya Raipur     (regex on faculty page)
- IIIT Allahabad       (department sub-pages)
- IIITM Gwalior        (regex on multiple pages)
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from loguru import logger

from scraper.fetch_utils import fetch as _scrapling_fetch

# ── HTTP helpers ────────────────────────────────────────────────────────────

def _fetch(url: str, retries: int = 2, timeout: int = 15, verify: bool = False) -> BeautifulSoup | None:
    return _scrapling_fetch(url, retries=retries, timeout=timeout, verify=verify)


def _fetch_raw(url: str, retries: int = 2, timeout: int = 15) -> str | None:
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers=_HEADERS, timeout=timeout,
                             allow_redirects=True, verify=False)
            if r.status_code == 200:
                return r.text
            return None
        except Exception as exc:
            if attempt < retries:
                time.sleep(2)
            else:
                logger.warning(f"Failed {url}: {exc}")
    return None


def _clean(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def _is_name(text: str) -> bool:
    t = text.strip()
    return bool(
        t and 5 < len(t) < 80
        and any(k in t for k in ["Dr.", "Prof.", "Mr.", "Ms.", "Mrs."])
    )


def _classify_designation(text: str) -> str:
    t = text.lower()
    if "director" in t:
        return "Director"
    if "professor" in t and "associate" in t:
        return "Associate Professor"
    if "professor" in t and "assistant" in t:
        return "Assistant Professor"
    if "professor" in t:
        return "Professor"
    if "lecturer" in t:
        return "Lecturer"
    if "visiting" in t or "adjunct" in t or "guest" in t:
        return "Visiting Faculty"
    return "Faculty"


def _make_faculty(name: str, designation: str = "Faculty",
                  department: str = "", email: str = "",
                  specialization: str = "") -> dict[str, Any]:
    return {
        "name": _clean(name),
        "designation": designation,
        "department": _clean(department),
        "email": _clean(email),
        "specialization": _clean(specialization),
        "phd": None,
        "experience_years": None,
    }


def _make_dept(name: str, faculty: list[dict]) -> dict[str, Any]:
    return {
        "name": name,
        "hod": None,
        "faculty_count": len(faculty),
        "faculty": faculty,
    }


def _regex_faculty_from_text(text: str, dept_name: str = "") -> list[dict]:
    """Extract faculty names via regex from unstructured page text."""
    NAME_RE = re.compile(
        r"(?:Dr\.|Prof\.|Mr\.|Ms\.|Mrs\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+"
    )
    seen: set[str] = set()
    result = []
    for m in NAME_RE.finditer(text):
        name = _clean(m.group())
        if name not in seen and 8 < len(name) < 70:
            seen.add(name)
            result.append(_make_faculty(name, department=dept_name))
    return result


# ══════════════════════════════════════════════════════════════════════════════
# Per-IIIT scraper functions
# Each returns list[dict]  (list of department dicts)
# ══════════════════════════════════════════════════════════════════════════════

# ── IIIT Bhagalpur ─────────────────────────────────────────────────────────

def scrape_iiit_bhagalpur() -> list[dict]:
    """Table-based faculty page at iiitbh.ac.in/faculty."""
    soup = _fetch("https://www.iiitbh.ac.in/faculty")
    if not soup:
        return []
    rows = soup.find_all("tr")
    dept_map: dict[str, list] = {}
    for row in rows:
        cells = row.find_all(["td", "th"])
        if not cells:
            continue
        text = _clean(cells[-1].get_text(" ") if len(cells) > 1 else cells[0].get_text(" "))
        if not _is_name(text):
            continue
        # Extract name line, dept, designation from combined cell text
        parts = [p.strip() for p in re.split(r"\n|  +", text) if p.strip()]
        name = parts[0] if parts else text
        dept = ""
        designation = "Faculty"
        specialization = ""
        for part in parts[1:]:
            if "Department of" in part or "Dept." in part:
                dept = re.sub(r"Department of\s*", "", part).strip()
            elif any(k in part.lower() for k in ["professor", "lecturer", "director"]):
                designation = _classify_designation(part)
            elif "Research Interests" in part or "Specialization" in part:
                specialization = re.sub(r"Research Interests:\s*", "", part).strip()
        faculty_entry = _make_faculty(name, designation, dept, specialization=specialization)
        dept_map.setdefault(dept or "General", []).append(faculty_entry)

    return [_make_dept(dept, fac) for dept, fac in dept_map.items()]


# ── IIIT Lucknow ───────────────────────────────────────────────────────────

def scrape_iiit_lucknow() -> list[dict]:
    """Regex-based extraction from iiitl.ac.in/index.php/faculty/."""
    soup = _fetch("https://www.iiitl.ac.in/index.php/faculty/")
    if not soup:
        return []
    text = soup.get_text(" ", strip=True)
    faculty = _regex_faculty_from_text(text)
    if faculty:
        return [_make_dept("Computer Science and Engineering", faculty)]
    return []


# ── IIIT Surat ─────────────────────────────────────────────────────────────

def scrape_iiit_surat() -> list[dict]:
    """JSON API at iiitsurat.ac.in/faculty returns structured faculty data."""
    raw = _fetch_raw("https://www.iiitsurat.ac.in/faculty")
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if not isinstance(data, list):
            raise ValueError("not a list")
    except (json.JSONDecodeError, ValueError):
        m = re.search(r"\[{.*}\]", raw, re.S)
        if not m:
            soup = BeautifulSoup(raw, "html.parser")
            text = soup.get_text(" ", strip=True)
            faculty = _regex_faculty_from_text(text)
            return [_make_dept("General", faculty)] if faculty else []
        try:
            data = json.loads(m.group())
        except json.JSONDecodeError:
            return []

    dept_map: dict[str, list] = {}
    for rec in data:
        if not isinstance(rec, dict):
            continue
        fname = _clean(rec.get("fac_fname", ""))
        mname = _clean(rec.get("fac_mname", ""))
        lname = _clean(rec.get("fac_lname", ""))
        initial = _clean(rec.get("fac_initial", ""))
        name_parts = [p for p in [initial, fname, mname, lname] if p and p != "-"]
        name = " ".join(name_parts)
        if not name or len(name) < 5:
            continue
        dept_id = _clean(rec.get("dept_id", "General"))
        designation = _classify_designation(rec.get("fac_designation", ""))
        email = _clean(rec.get("fac_email1", ""))
        spec = _clean(rec.get("fac_specialization", ""))
        dept_map.setdefault(dept_id, []).append(
            _make_faculty(name, designation, dept_id, email, spec)
        )
    return [_make_dept(dept, fac) for dept, fac in dept_map.items()]


# ── IIIT Pune ──────────────────────────────────────────────────────────────

def scrape_iiit_pune() -> list[dict]:
    soup = _fetch("https://www.iiitp.ac.in/people")
    if not soup:
        return []
    text = soup.get_text(" ", strip=True)
    faculty = _regex_faculty_from_text(text)
    if faculty:
        return [_make_dept("General", faculty)]
    return []


# ── IIITDM Kancheepuram ─────────────────────────────────────────────────────

def scrape_iiitdm_kancheepuram() -> list[dict]:
    soup = _fetch("https://www.iiitdm.ac.in/")
    if not soup:
        return []
    text = soup.get_text(" ", strip=True)
    faculty = _regex_faculty_from_text(text)
    if faculty:
        return [_make_dept("General", faculty)]
    return []


# ── IIIT Allahabad ─────────────────────────────────────────────────────────

def scrape_iiit_allahabad() -> list[dict]:
    urls = ["https://www.iiita.ac.in/people/", "https://www.iiita.ac.in/"]
    all_faculty: list[dict] = []
    seen: set[str] = set()
    for url in urls:
        soup = _fetch(url, timeout=10)
        if not soup:
            continue
        for f in _regex_faculty_from_text(soup.get_text(" ", strip=True)):
            if f["name"] not in seen:
                seen.add(f["name"])
                all_faculty.append(f)
    if all_faculty:
        return [_make_dept("General", all_faculty)]
    return []


# ── IIITM Gwalior ──────────────────────────────────────────────────────────

def scrape_iiitm_gwalior() -> list[dict]:
    urls = ["https://www.iiitm.ac.in/index.php/en/", "https://www.iiitm.ac.in/index.php/en/research"]
    all_faculty: list[dict] = []
    seen: set[str] = set()
    for url in urls:
        soup = _fetch(url, timeout=10)
        if not soup:
            continue
        for f in _regex_faculty_from_text(soup.get_text(" ", strip=True)):
            if f["name"] not in seen:
                seen.add(f["name"])
                all_faculty.append(f)
    if all_faculty:
        return [_make_dept("General", all_faculty)]
    return []


# ── Other IIITs with regex fallback ────────────────────────────────────────

def _generic_scrape(urls: list[str], dept_name: str = "General") -> list[dict]:
    all_faculty: list[dict] = []
    seen: set[str] = set()
    for url in urls:
        soup = _fetch(url, timeout=10)
        if not soup:
            continue
        for f in _regex_faculty_from_text(soup.get_text(" ", strip=True), dept_name):
            if f["name"] not in seen:
                seen.add(f["name"])
                all_faculty.append(f)
    if all_faculty:
        return [_make_dept(dept_name, all_faculty)]
    return []


def scrape_iiit_naya_raipur() -> list[dict]:
    return _generic_scrape(["https://www.iiitnr.ac.in/faculty", "https://www.iiitnr.ac.in/"])


def scrape_iiit_guwahati() -> list[dict]:
    return _generic_scrape(["https://www.iiitg.ac.in/faculty", "https://www.iiitg.ac.in/"])


def scrape_iiit_ranchi() -> list[dict]:
    return _generic_scrape(["https://www.iiitranchi.ac.in/faculty"])


def scrape_iiit_sri_city() -> list[dict]:
    return _generic_scrape(["https://www.iiits.ac.in/faculty/", "https://www.iiits.ac.in/"])


def scrape_iiit_trichy() -> list[dict]:
    return _generic_scrape(["https://www.iiitt.ac.in/faculty", "https://www.iiitt.ac.in/"])


def scrape_iiitdm_jabalpur() -> list[dict]:
    return _generic_scrape(["https://www.iiitdmj.ac.in/people/", "https://www.iiitdmj.ac.in/"])


def scrape_iiitdm_kurnool() -> list[dict]:
    return _generic_scrape(["https://www.iiitk.ac.in/", "https://www.iiitk.ac.in/faculty"])


def scrape_iiit_manipur() -> list[dict]:
    return _generic_scrape(["https://www.iiitmanipur.ac.in/", "https://www.iiitmanipur.ac.in/faculty"])


def scrape_iiit_kottayam() -> list[dict]:
    return _generic_scrape(["https://www.iiitkottayam.ac.in/", "https://www.iiitkottayam.ac.in/faculty"])


def scrape_iiit_bhubaneswar() -> list[dict]:
    return _generic_scrape(["http://www.iiit-bh.ac.in/", "http://www.iiit-bh.ac.in/faculty"])


def scrape_iiit_nagpur() -> list[dict]:
    return _generic_scrape(["http://www.iiitn.ac.in/", "http://www.iiitn.ac.in/index.php/faculty"])


# ── IIIT Kalyani ───────────────────────────────────────────────────────────

def scrape_iiit_kalyani() -> list[dict]:
    """Section-based faculty page at iiitkalyani.ac.in/faculty."""
    soup = _fetch("https://www.iiitkalyani.ac.in/faculty")
    if not soup:
        return []
    faculty_list: list[dict] = []
    current_desig = "Faculty"
    for sec in soup.find_all("section"):
        text = _clean(sec.get_text(" "))
        h = sec.find(["h2", "h3", "h4"])
        if h:
            header_text = _clean(h.get_text())
            if any(k in header_text.lower() for k in ["professor", "lecturer", "faculty"]):
                current_desig = _classify_designation(header_text)
        members = re.findall(
            r"((?:Dr\.|Prof\.|Mr\.|Ms\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)"
            r"(?:[^@\n]*?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]+))?",
            text
        )
        for name, email in members:
            faculty_list.append(_make_faculty(_clean(name), current_desig, email=email))
    if faculty_list:
        return [_make_dept("Computer Science and Engineering", faculty_list)]
    return []


# ── IIIT Kota ──────────────────────────────────────────────────────────────

def scrape_iiit_kota() -> list[dict]:
    """li-element-based faculty page at iiitkota.ac.in/faculty."""
    soup = _fetch("https://www.iiitkota.ac.in/faculty")
    if not soup:
        return []
    dept_map: dict[str, list] = {}
    text = soup.get_text(" ", strip=True)
    blocks = re.findall(
        r"((?:Dr\.|Prof\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)"
        r"(?:\s+Department of\s+([A-Z][A-Za-z&\s]+?))?"
        r"(?:\s+((?:Assistant |Associate |Guest |Adjunct )?(?:Professor|Faculty|Lecturer)))?",
        text
    )
    for name, dept, desig in blocks:
        name = _clean(name)
        dept = _clean(dept) or "General"
        designation = _classify_designation(desig) if desig else "Faculty"
        dept_map.setdefault(dept, []).append(_make_faculty(name, designation, dept))
    if not dept_map:
        names_seen: set[str] = set()
        for li in soup.find_all("li"):
            t = _clean(li.get_text())
            if _is_name(t) and t not in names_seen:
                names_seen.add(t)
                dept_map.setdefault("General", []).append(_make_faculty(t))
    return [_make_dept(dept, fac) for dept, fac in dept_map.items()]


# ══════════════════════════════════════════════════════════════════════════════
# REGISTRY  —  slug → scraper function
# ══════════════════════════════════════════════════════════════════════════════

_IIIT_DEEP_REGISTRY: dict[str, Any] = {
    "iiit-allahabad":       scrape_iiit_allahabad,
    "iiit-bhagalpur":       scrape_iiit_bhagalpur,
    "iiit-bhubaneswar":     scrape_iiit_bhubaneswar,
    "iiit-guwahati":        scrape_iiit_guwahati,
    "iiit-kalyani":         scrape_iiit_kalyani,
    "iiit-kota":            scrape_iiit_kota,
    "iiit-kottayam":        scrape_iiit_kottayam,
    "iiit-lucknow":         scrape_iiit_lucknow,
    "iiit-manipur":         scrape_iiit_manipur,
    "iiit-nagpur":          scrape_iiit_nagpur,
    "iiit-naya-raipur":     scrape_iiit_naya_raipur,
    "iiit-pune":            scrape_iiit_pune,
    "iiit-ranchi":          scrape_iiit_ranchi,
    "iiit-sri-city":        scrape_iiit_sri_city,
    "iiit-surat":           scrape_iiit_surat,
    "iiit-trichy":          scrape_iiit_trichy,
    "iiitdm-jabalpur":      scrape_iiitdm_jabalpur,
    "iiitdm-kancheepuram":  scrape_iiitdm_kancheepuram,
    "iiitdm-kurnool":       scrape_iiitdm_kurnool,
    "iiitm-gwalior":        scrape_iiitm_gwalior,
}


# ══════════════════════════════════════════════════════════════════════════════
# MERGE HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _find_iiit_json(parsed_dir: Path, slug: str) -> Path | None:
    """Find the JSON file matching an IIIT slug (must start with 'iiit')."""
    slug_clean = slug.lower().replace("-", "").replace("_", "")
    candidates = []
    for f in parsed_dir.glob("*_structured.json"):
        name = f.stem.replace("_structured", "").lower().replace("-", "").replace("_", "")
        if not name.startswith("iiit"):
            continue
        if slug_clean == name:
            return f
        if slug_clean in name or name in slug_clean:
            candidates.append(f)
    if len(candidates) == 1:
        return candidates[0]
    if candidates:
        return min(candidates, key=lambda f: len(f.stem))
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


# ══════════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

def run_all_iiit_deep_scrapers(
    parsed_dir: str | None = None,
    target: str | None = None,
) -> None:
    """Run all IIIT faculty scrapers and persist results to JSON files."""
    if parsed_dir is None:
        parsed_dir_path = Path(__file__).parent.parent / "data" / "parsed"
    else:
        parsed_dir_path = Path(parsed_dir)

    registry = {target: _IIIT_DEEP_REGISTRY[target]} if target else _IIIT_DEEP_REGISTRY

    for slug, scraper_fn in registry.items():
        logger.info(f"\n{'='*60}\nIIIT Deep scraper: {slug}\n{'='*60}")
        try:
            departments = scraper_fn()
        except Exception as e:
            logger.error(f"Scraper {slug} crashed: {e}")
            continue

        if not departments:
            logger.warning(f"No faculty data returned for {slug}")
            continue

        json_file = _find_iiit_json(parsed_dir_path, slug)
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
    run_all_iiit_deep_scrapers(target=target_slug)
