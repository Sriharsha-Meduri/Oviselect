"""Generic parser for official college websites.

Extracts structured data from diverse institutional HTML layouts using
keyword-based section detection and common HTML patterns (tables, lists,
cards, headings).  Returns a dict that is then merged with CollegePravesh
data (official data takes priority).
"""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag
from loguru import logger


# ── Helpers ───────────────────────────────────────────────────────────────────

def _text(el) -> str:
    return el.get_text(separator=" ", strip=True) if el else ""


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _find_number(text: str) -> int | None:
    m = re.search(r"[\d,]+", text.replace(",", ""))
    if m:
        try:
            return int(m.group().replace(",", ""))
        except ValueError:
            return None
    return None


def _find_float(text: str) -> float | None:
    m = re.search(r"[\d]+\.?[\d]*", text.replace(",", ""))
    if m:
        try:
            return float(m.group())
        except ValueError:
            return None
    return None


def _section_soup(soup: BeautifulSoup, *keywords: str) -> Tag | None:
    """Find the first heading/section whose text matches any of the keywords."""
    for tag in soup.find_all(re.compile(r"^h[1-6]$")):
        txt = _text(tag).lower()
        if any(kw in txt for kw in keywords):
            # Return the parent or next sibling container
            parent = tag.parent
            return parent
    return None


def _links_with_keywords(soup: BeautifulSoup, *keywords: str, base_url: str = "") -> list[str]:
    """Return hrefs of links whose text or href matches any keyword."""
    urls: list[str] = []
    for a in soup.find_all("a", href=True):
        txt = _text(a).lower()
        href = a["href"].lower()
        if any(kw in txt or kw in href for kw in keywords):
            full = urljoin(base_url, a["href"]) if base_url else a["href"]
            if full not in urls:
                urls.append(full)
    return urls


# ── Faculty extraction ────────────────────────────────────────────────────────

_DESIG_KEYWORDS = [
    "professor", "associate professor", "assistant professor",
    "lecturer", "reader", "scientist", "research fellow",
]

_DESIG_RE = re.compile(
    r"(professor|associate professor|assistant professor|lecturer|reader|scientist)",
    re.IGNORECASE,
)


def _parse_faculty_card(card: Tag) -> dict | None:
    """Parse a single faculty card/row into a dict."""
    text = _text(card)
    if not text or len(text) < 5:
        return None

    # Name: usually the first <strong>, <b>, or prominent link
    name_el = card.find(["strong", "b", "h3", "h4", "h5"])
    name = _clean(_text(name_el)) if name_el else ""
    if not name:
        # Fallback: first non-empty line
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        name = lines[0] if lines else ""

    # Designation
    desig_m = _DESIG_RE.search(text)
    designation = _clean(desig_m.group()) if desig_m else None

    # Specializations — look for "Specialization", "Research Interest", "Area"
    spec_m = re.search(
        r"(?:speciali[sz]ation|research interest|area of interest)[s:]*\s*(.+?)(?:\n|$)",
        text, re.IGNORECASE,
    )
    specs = (
        [s.strip() for s in re.split(r"[,;|]", spec_m.group(1)) if s.strip()]
        if spec_m else None
    )

    # Qualifications
    qual_m = re.search(
        r"(?:qualification|education|degree)[s:]*\s*(.+?)(?:\n|$)",
        text, re.IGNORECASE,
    )
    qual_raw = _clean(qual_m.group(1)) if qual_m else None
    qualifications = [{"degree": q.strip()} for q in re.split(r"[,;]", qual_raw) if q.strip()] if qual_raw else None

    # Profile URL
    profile_url = None
    for a in card.find_all("a", href=True):
        href = a["href"]
        if any(kw in href.lower() for kw in ["profile", "faculty", "people", "staff"]):
            profile_url = href
            break

    if not name or not designation:
        return None

    return {
        "name": name,
        "designation": designation,
        "qualifications": qualifications,
        "specializations": specs,
        "profile_url": profile_url,
    }


def extract_faculty(soup: BeautifulSoup, base_url: str = "") -> list[dict]:
    """Extract a list of faculty member dicts from a page."""
    faculty: list[dict] = []
    seen: set[str] = set()

    # Strategy 1: look for table rows with faculty-like content
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        for row in rows[1:]:  # skip header
            f = _parse_faculty_card(row)
            if f and f["name"] not in seen:
                seen.add(f["name"])
                faculty.append(f)

    # Strategy 2: look for div/li cards
    if len(faculty) < 3:
        for container in soup.find_all(
            ["div", "li", "article"],
            class_=re.compile(r"faculty|people|member|staff|profile", re.I),
        ):
            f = _parse_faculty_card(container)
            if f and f["name"] not in seen:
                seen.add(f["name"])
                faculty.append(f)

    logger.debug(f"Extracted {len(faculty)} faculty members")
    return faculty


def extract_faculty_profile(soup: BeautifulSoup, base_url: str = "") -> dict:
    """Extract detailed data from a single faculty profile page."""
    text = _text(soup)

    # Publications
    pubs: list[str] = []
    for section in soup.find_all(["section", "div"], id=re.compile(r"pub|paper|journal", re.I)):
        for li in section.find_all("li"):
            p = _clean(_text(li))
            if len(p) > 20:
                pubs.append(p)
    if not pubs:
        # Fallback: list items that look like citations
        for li in soup.find_all("li"):
            t = _clean(_text(li))
            if len(t) > 60 and re.search(r"\d{4}", t):
                pubs.append(t)
        pubs = pubs[:30]  # cap

    # Patents
    patents: list[str] = []
    for section in soup.find_all(["section", "div"], id=re.compile(r"patent", re.I)):
        for li in section.find_all("li"):
            patents.append(_clean(_text(li)))

    # Funded projects
    projects: list[str] = []
    for section in soup.find_all(["section", "div"], id=re.compile(r"project|grant|fund", re.I)):
        for li in section.find_all("li"):
            projects.append(_clean(_text(li)))

    # PhD students
    phd_students: list[str] = []
    for section in soup.find_all(["section", "div"], id=re.compile(r"phd|scholar|student", re.I)):
        for li in section.find_all("li"):
            phd_students.append(_clean(_text(li)))

    # Awards / fellowships
    awards: list[str] = []
    for section in soup.find_all(["section", "div"], id=re.compile(r"award|honour|honor|fellow", re.I)):
        for li in section.find_all("li"):
            awards.append(_clean(_text(li)))
    if not awards:
        award_m = re.findall(
            r"(?:Fellow|Award|Prize|Medal)[^.]{5,80}", text, re.IGNORECASE
        )
        awards = [_clean(a) for a in award_m[:10]]

    return {
        "publications": pubs or None,
        "patents": patents or None,
        "funded_projects": projects or None,
        "phd_students_supervised": phd_students or None,
        "awards": awards or None,
    }


# ── Department extraction ─────────────────────────────────────────────────────

def extract_departments(soup: BeautifulSoup, base_url: str = "") -> list[dict]:
    """Extract department list with HOD names."""
    depts: list[dict] = []
    seen: set[str] = set()

    # Look for department tables or lists
    for table in soup.find_all("table"):
        for row in table.find_all("tr")[1:]:
            cells = [_clean(_text(td)) for td in row.find_all(["td", "th"])]
            if not cells:
                continue
            dept_name = cells[0] if cells else None
            hod = cells[1] if len(cells) > 1 else None
            if dept_name and dept_name not in seen and len(dept_name) > 2:
                seen.add(dept_name)
                depts.append({"name": dept_name, "hod_name": hod})

    # Fallback: look for headings or links that mention departments
    if not depts:
        for a in soup.find_all("a", href=True):
            txt = _clean(_text(a))
            if re.search(r"department|dept\.?\s+of", txt, re.IGNORECASE) and txt not in seen:
                seen.add(txt)
                depts.append({"name": txt, "hod_name": None})

    logger.debug(f"Extracted {len(depts)} departments")
    return depts


# ── Programme extraction ──────────────────────────────────────────────────────

def extract_programmes(soup: BeautifulSoup) -> dict:
    """Extract UG, PG, and PhD programme data."""
    ug: list[dict] = []
    pg: list[dict] = []
    dual: list[dict] = []
    phd_available = False
    phd_seats: int | None = None

    for row in soup.find_all("tr"):
        cells = [_clean(_text(td)) for td in row.find_all(["td", "th"])]
        if len(cells) < 2:
            continue
        row_text = " ".join(cells).lower()

        # Detect level
        level = None
        if re.search(r"\bm\.?tech\b|\bm\.?e\b|\bm\.?sc\b|\bpg\b|\bmba\b|\bm\.?plan\b", row_text):
            level = "PG"
        elif re.search(r"\bphd\b|\bdoctorate\b|\bph\.d\b", row_text):
            level = "PhD"
        elif re.search(r"\bdual\b|\bintegrated\b|\bb\.?tech.*m\.?tech\b", row_text):
            level = "Dual"
        elif re.search(r"\bb\.?tech\b|\bb\.?e\b|\bb\.?arch\b|\bb\.?plan\b|\bug\b", row_text):
            level = "UG"

        if level is None:
            continue

        prog = {"name": cells[0], "level": level}
        # Intake seats
        for cell in cells[1:]:
            n = _find_number(cell)
            if n and 5 <= n <= 500:
                prog["intake_seats"] = n
                break

        if level == "PhD":
            phd_available = True
            if "intake_seats" in prog:
                phd_seats = prog["intake_seats"]
        elif level == "PG":
            pg.append(prog)
        elif level == "Dual":
            dual.append(prog)
        else:
            ug.append(prog)

    # Fallback: search for PhD mention in page text
    if not phd_available:
        text = soup.get_text()
        if re.search(r"\bphd\b|\bph\.d\b|\bdoctoral\b", text, re.IGNORECASE):
            phd_available = True

    return {
        "ug_programmes": ug or None,
        "pg_programmes": pg or None,
        "dual_degree_programmes": dual or None,
        "phd_available": phd_available,
        "phd_seats": phd_seats,
    }


# ── Placement extraction ──────────────────────────────────────────────────────

_PACKAGE_RE = re.compile(r"([\d]+\.?[\d]*)\s*(?:lpa|l\.?p\.?a|lakhs?|crores?)", re.IGNORECASE)
_PCT_RE     = re.compile(r"([\d]+\.?[\d]*)\s*%")
_YEAR_RE    = re.compile(r"\b(20[12][0-9])\b")


def extract_placements(soup: BeautifulSoup) -> dict:
    """Extract placement statistics from a placement/T&P page."""
    result: dict = {}
    text = _text(soup)

    # Placement officer contact
    email_m = re.search(r"[\w.+%-]+@[\w.-]+\.[a-zA-Z]{2,}", text)
    phone_m = re.search(r"[+\d][\d\s-]{8,13}", text)
    officer: dict = {}
    if email_m:
        officer["email"] = email_m.group()
    if phone_m:
        officer["phone"] = phone_m.group().strip()
    if officer:
        result["placement_officer"] = officer

    # Year-wise stats from tables
    year_wise: list[dict] = []
    for table in soup.find_all("table"):
        headers = [_clean(_text(th)).lower() for th in table.find_all("th")]
        for row in table.find_all("tr")[1:]:
            cells = [_clean(_text(td)) for td in row.find_all(["td", "th"])]
            if not cells:
                continue
            row_text = " ".join(cells)
            year_m = _YEAR_RE.search(row_text)
            if not year_m:
                continue
            yr_dict: dict = {"year": int(year_m.group())}
            for i, cell in enumerate(cells):
                hdr = headers[i] if i < len(headers) else ""
                if re.search(r"avg|average|mean", hdr):
                    yr_dict["avg_package_lpa"] = _find_float(cell)
                elif re.search(r"median", hdr):
                    yr_dict["median_package_lpa"] = _find_float(cell)
                elif re.search(r"highest|max|top", hdr):
                    yr_dict["highest_package_lpa"] = _find_float(cell)
                elif re.search(r"placed|placement\s*%|pct", hdr):
                    yr_dict["overall_pct"] = _find_float(cell)
                elif re.search(r"offers?|total", hdr):
                    yr_dict["total_offers"] = _find_number(cell)
            year_wise.append(yr_dict)

    if year_wise:
        result["year_wise_placements"] = year_wise

    # Top recruiters
    recruiters: list[str] = []
    for el in soup.find_all(["img", "span", "li", "td"]):
        if el.name == "img":
            alt = el.get("alt", "").strip()
            if alt and 2 < len(alt) < 60 and alt not in recruiters:
                recruiters.append(alt)
        else:
            txt = _clean(_text(el))
            if 2 < len(txt) < 60 and txt not in recruiters:
                parent_txt = _text(el.parent).lower() if el.parent else ""
                if re.search(r"recruit|compan|employer|sponsor|visit", parent_txt):
                    recruiters.append(txt)
    if recruiters:
        result["top_recruiters"] = recruiters[:60]

    # Sector-wise
    sector_wise: dict = {}
    for row in soup.find_all("tr"):
        cells = [_clean(_text(td)) for td in row.find_all(["td", "th"])]
        if len(cells) >= 2:
            pct_m = _PCT_RE.search(cells[-1])
            if pct_m and re.search(r"it|core|consult|finance|research|psu", cells[0], re.I):
                sector_wise[cells[0]] = float(pct_m.group(1))
    if sector_wise:
        result["sector_wise_placement"] = sector_wise

    return result


# ── Research extraction ───────────────────────────────────────────────────────

def extract_research(soup: BeautifulSoup) -> dict:
    """Extract research statistics from a research/R&D page."""
    text = _text(soup)
    result: dict = {}

    # Active projects
    proj_m = re.search(
        r"([\d,]+)\s*(?:active\s*)?(?:sponsored\s*)?(?:research\s*)?projects?",
        text, re.IGNORECASE,
    )
    if proj_m:
        result["active_projects"] = _find_number(proj_m.group())

    # Total funding
    fund_m = re.search(
        r"(?:total\s*funding|research\s*funding|grant)[^\d]*([\d,.]+)\s*(?:crore|cr\.?|lakh)?",
        text, re.IGNORECASE,
    )
    if fund_m:
        result["total_funding_crores"] = _find_float(fund_m.group())

    # Patents
    pat_filed = re.search(r"([\d,]+)\s*patents?\s*(?:filed|applied)", text, re.IGNORECASE)
    pat_granted = re.search(r"([\d,]+)\s*patents?\s*(?:granted|issued)", text, re.IGNORECASE)
    if pat_filed:
        result["patents_filed"] = _find_number(pat_filed.group())
    if pat_granted:
        result["patents_granted"] = _find_number(pat_granted.group())

    # PhD enrolled / awarded
    phd_enrol = re.search(r"([\d,]+)\s*ph\.?d\.?\s*(?:students?\s*)?(?:enrolled|registered|pursuing)", text, re.IGNORECASE)
    phd_awd   = re.search(r"([\d,]+)\s*ph\.?d\.?\s*(?:degrees?\s*)?(?:awarded|conferred)", text, re.IGNORECASE)
    if phd_enrol:
        result["phd_students_enrolled"] = _find_number(phd_enrol.group())
    if phd_awd:
        result["phds_awarded"] = _find_number(phd_awd.group())

    # Funding agencies
    agencies = []
    for agency in ["DST", "SERB", "DRDO", "ISRO", "DBT", "CSIR", "MHRD", "DAE", "ICAR", "MoE"]:
        if agency in text:
            agencies.append(agency)
    if agencies:
        result["funding_agencies"] = agencies

    # Research centres
    centres: list[str] = []
    for heading in soup.find_all(re.compile(r"^h[2-5]$")):
        ht = _clean(_text(heading))
        if re.search(r"centre|center|lab|facility|institute", ht, re.IGNORECASE) and len(ht) < 120:
            centres.append(ht)
    if centres:
        result["research_centres"] = centres

    # Publications per year
    pub_m = re.search(r"([\d,]+)\s*(?:research\s*)?publications?\s*(?:per\s*year|annually|in\s*20\d{2})", text, re.IGNORECASE)
    if pub_m:
        result["publications_per_year"] = _find_number(pub_m.group())

    return result


# ── Infrastructure extraction ─────────────────────────────────────────────────

def extract_infrastructure(soup: BeautifulSoup) -> dict:
    """Extract infrastructure / facilities data."""
    text = _text(soup)
    result: dict = {}

    # Labs — headings or list items mentioning "laboratory" or "lab"
    labs: list[str] = []
    for el in soup.find_all(re.compile(r"^(h[2-6]|li|td)$")):
        t = _clean(_text(el))
        if re.search(r"\blab(?:oratory)?\b", t, re.IGNORECASE) and 5 < len(t) < 150:
            labs.append(t)
    if labs:
        result["labs"] = list(dict.fromkeys(labs))  # deduplicate preserving order

    # Library
    lib: dict = {}
    vol_m   = re.search(r"([\d,]+)\s*(?:volumes?|books?|titles?)", text, re.IGNORECASE)
    jour_m  = re.search(r"([\d,]+)\s*(?:journals?|periodicals?)", text, re.IGNORECASE)
    if vol_m:
        lib["volumes"] = _find_number(vol_m.group())
    if jour_m:
        lib["journals_subscribed"] = _find_number(jour_m.group())
    db_matches = []
    for db in ["IEEE Xplore", "ScienceDirect", "Scopus", "Web of Science", "JSTOR", "ACM", "Springer", "Elsevier"]:
        if db.lower() in text.lower():
            db_matches.append(db)
    if db_matches:
        lib["digital_databases"] = db_matches
    if lib:
        result["library"] = lib

    # Sports
    sports: list[str] = []
    for kw in ["cricket", "football", "basketball", "tennis", "badminton", "volleyball",
                "swimming pool", "squash", "hockey", "table tennis", "athletics", "gymnasium", "gym"]:
        if re.search(rf"\b{kw}\b", text, re.IGNORECASE):
            sports.append(kw.title())
    if sports:
        result["sports_facilities"] = sports

    # Hostels
    boy_m  = re.search(r"(\d+)\s*boys?\s*hostel", text, re.IGNORECASE)
    girl_m = re.search(r"(\d+)\s*girls?\s*hostel", text, re.IGNORECASE)
    cap_m  = re.search(r"hostel\s*capacity[^\d]*([\d,]+)", text, re.IGNORECASE)
    if boy_m:
        result["hostel_count_boys"] = int(boy_m.group(1))
    if girl_m:
        result["hostel_count_girls"] = int(girl_m.group(1))
    if cap_m:
        result["total_hostel_capacity"] = _find_number(cap_m.group())

    # Medical centre
    med: dict = {}
    bed_m = re.search(r"(\d+)\s*beds?\b", text, re.IGNORECASE)
    if bed_m:
        med["beds"] = int(bed_m.group(1))
    if re.search(r"full.?time doctor|resident doctor|medical officer", text, re.IGNORECASE):
        med["full_time_doctor"] = True
    if med:
        result["medical_centre"] = med

    # Amenities
    result["has_bank_atm"] = bool(re.search(r"\batm\b|\bbank\b", text, re.IGNORECASE))
    result["has_post_office"] = bool(re.search(r"post\s*office", text, re.IGNORECASE))

    bus_m = re.search(r"(\d+)\s*buses?", text, re.IGNORECASE)
    if bus_m:
        result["transport_buses"] = int(bus_m.group(1))

    return result


# ── Student activities extraction ─────────────────────────────────────────────

def extract_student_activities(soup: BeautifulSoup) -> dict:
    """Extract student clubs, fests, NSS/NCC info."""
    text = _text(soup)
    result: dict = {}

    # Clubs / societies
    clubs: list[str] = []
    for el in soup.find_all(["li", "h3", "h4", "h5", "strong", "b"]):
        t = _clean(_text(el))
        if re.search(r"\bclub\b|\bsociet\b|\bcell\b|\bteam\b|\bgroup\b", t, re.IGNORECASE) and 3 < len(t) < 100:
            clubs.append(t)
    if clubs:
        result["clubs"] = list(dict.fromkeys(clubs))

    # Fests
    tech_fests = []
    cult_fests = []
    for el in soup.find_all(["li", "h3", "h4", "strong"]):
        t = _clean(_text(el))
        if re.search(r"tech(?:nical)?\s*fest|techno|symposium|hackathon", t, re.IGNORECASE):
            tech_fests.append(t)
        elif re.search(r"cultural\s*fest|cult\s*fest|cultural\s*event", t, re.IGNORECASE):
            cult_fests.append(t)
    if tech_fests:
        result["technical_fests"] = list(dict.fromkeys(tech_fests))
    if cult_fests:
        result["cultural_fests"] = list(dict.fromkeys(cult_fests))

    result["has_nss"] = bool(re.search(r"\bnss\b|national service scheme", text, re.IGNORECASE))
    result["has_ncc"] = bool(re.search(r"\bncc\b|national cadet corps", text, re.IGNORECASE))

    return result


# ── International relations extraction ────────────────────────────────────────

def extract_international(soup: BeautifulSoup) -> dict:
    """Extract MoU list and international stats."""
    text = _text(soup)
    result: dict = {}

    # MoU count
    mou_count_m = re.search(r"(\d+)\s*mo[uu]s?", text, re.IGNORECASE)
    if mou_count_m:
        result["mou_count"] = int(mou_count_m.group(1))

    # MoU list from tables or lists
    mous: list[dict] = []
    for row in soup.find_all("tr"):
        cells = [_clean(_text(td)) for td in row.find_all(["td", "th"])]
        if len(cells) >= 2:
            univ = cells[0] if cells else None
            country = cells[1] if len(cells) > 1 else None
            if univ and len(univ) > 3 and not re.search(r"university|country|institution", univ, re.IGNORECASE):
                mous.append({"university": univ, "country": country})

    if not mous:
        for li in soup.find_all("li"):
            t = _clean(_text(li))
            if re.search(r"university|institute|college", t, re.IGNORECASE) and len(t) < 200:
                mous.append({"university": t, "country": None})
    if mous:
        result["mous"] = mous

    # Exchange / foreign students
    ex_m   = re.search(r"(\d+)\s*students?\s*(?:went|participated|exchange)", text, re.IGNORECASE)
    for_m  = re.search(r"(\d+)\s*(?:foreign|international)\s*students?", text, re.IGNORECASE)
    if ex_m:
        result["exchange_students_outgoing"] = int(ex_m.group(1))
    if for_m:
        result["foreign_students_on_campus"] = int(for_m.group(1))

    return result


# ── NIRF / ranking extraction ─────────────────────────────────────────────────

def extract_rankings(soup: BeautifulSoup) -> dict:
    """Extract NIRF and other rankings mentioned on the official site."""
    text = _text(soup)
    result: dict = {}
    history: dict = {}

    for m in re.finditer(
        r"nirf\s*(?:overall\s*)?rank[^\d]*([\d]+)(?:[^\d]*(20[12][0-9]))?",
        text, re.IGNORECASE,
    ):
        rank = int(m.group(1))
        year = m.group(2)
        if year:
            history[year] = rank
        else:
            result.setdefault("nirf_overall_rank", rank)
    if history:
        result["nirf_overall_rank_history"] = history

    return result


# ── Main entry point ──────────────────────────────────────────────────────────

def parse_official_section(
    section: str,
    soup: BeautifulSoup,
    base_url: str = "",
) -> dict:
    """Dispatch to the right extractor for a given section name."""
    if section == "faculty":
        return {"_faculty_raw": extract_faculty(soup, base_url=base_url)}
    if section == "placements":
        return extract_placements(soup)
    if section == "research":
        return {"research": extract_research(soup)}
    if section == "infrastructure":
        return {"infrastructure": extract_infrastructure(soup)}
    if section == "student_life":
        return {"student_activities": extract_student_activities(soup)}
    if section == "international":
        return {"international_relations": extract_international(soup)}
    if section == "academics":
        return extract_programmes(soup)
    if section == "rankings":
        return extract_rankings(soup)
    return {}

