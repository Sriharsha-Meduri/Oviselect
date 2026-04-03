"""IIT Research Data Scraper.

Scrapes research metrics (patents, projects, labs, research centres, workshops)
from official IIT websites and merges the data into the `research` and
`infrastructure.labs` fields of the existing data/parsed/iit-*_structured.json files.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from loguru import logger

from scraper.fetch_utils import fetch as _scrapling_fetch

# ── Helpers ────────────────────────────────────────────────────────────────────

def _fetch(url: str, retries: int = 2, timeout: int = 15) -> BeautifulSoup | None:
    return _scrapling_fetch(url, retries=retries, timeout=timeout, verify=False)


def _clean(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def _extract_int(text: str, pattern: str) -> int | None:
    m = re.search(pattern, text, re.I)
    if m:
        raw = m.group(1).replace(",", "").strip()
        try:
            return int(raw)
        except ValueError:
            return None
    return None


def _extract_float(text: str, pattern: str) -> float | None:
    m = re.search(pattern, text, re.I)
    if m:
        raw = m.group(1).replace(",", "").strip()
        try:
            return float(raw)
        except ValueError:
            return None
    return None


_NAV_JUNK = {
    "research", "centres", "facilities", "center", "lab", "laboratory",
    "research highlights", "research areas", "research programmes",
    "national research centres", "institute research centres",
    "research facilities", "about", "home", "contact", "menu",
}


def _is_junk(text: str) -> bool:
    """True if the text is too generic/short to be a meaningful centre or lab name."""
    t = text.strip().lower()
    if t in _NAV_JUNK:
        return True
    if len(t) < 6:
        return True
    if t.startswith("+ -") or "click to collapse" in t:
        return True
    return False


def _clean_lab(text: str) -> str:
    """Strip collapsible-section artefacts like '+ - Name Click to collapse'."""
    t = re.sub(r"^\+\s*-\s*", "", text).strip()
    t = re.sub(r"\s*Click to collapse.*$", "", t, flags=re.I).strip()
    t = re.sub(r"\s*\|.*$", "", t).strip()       # strip '| (PDF)' suffixes
    t = re.sub(r"\s*\(PDF\)$", "", t, flags=re.I).strip()
    t = re.sub(r"\s*\(WEB\)$", "", t, flags=re.I).strip()
    return t


def _links_matching(soup: BeautifulSoup, keywords: list[str], base: str = "") -> list[str]:
    """Return unique, cleaned link-text values whose text matches any keyword."""
    seen: set[str] = set()
    results: list[str] = []
    for a in soup.find_all("a"):
        raw = _clean(a.get_text())
        t = _clean_lab(raw)
        if not t or _is_junk(t) or len(t) > 100:
            continue
        if any(kw.lower() in t.lower() for kw in keywords):
            if t not in seen:
                seen.add(t)
                results.append(t)
    return results


def _empty_result() -> dict[str, Any]:
    return {"research": {}, "infrastructure": {}}


# ══════════════════════════════════════════════════════════════════════════════
# IIT MADRAS  –  https://www.iitm.ac.in/node/1097
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_madras() -> dict[str, Any]:
    result = _empty_result()
    soup = _fetch("https://www.iitm.ac.in/node/1097")
    if not soup:
        logger.warning("[IIT Madras] research page unreachable")
        return result
    text = soup.get_text(" ", strip=True)
    research: dict[str, Any] = {}
    v = _extract_int(text, r"(\d[\d,]*)\s*patents?\s*(filed|granted|awarded)?")
    if v:
        research["patents_filed"] = v
    v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active|ongoing)?\s*(?:research)?\s*projects?")
    if v:
        research["active_projects"] = v
    v = _extract_int(text, r"(\d[\d,]*)\s*Ph\.?D")
    if v:
        research["phd_students_enrolled"] = v

    # Research centres from the research areas page
    soup2 = _fetch("https://www.iitm.ac.in/research/research-highlights")
    centres: list[str] = []
    if soup2:
        for a in soup2.find_all("a"):
            t = _clean_lab(_clean(a.get_text()))
            if any(k in t.lower() for k in ["centre", "center", "lab", "park"]) and 8 < len(t) < 80:
                if not _is_junk(t) and t not in centres:
                    centres.append(t)
    if centres:
        research["research_centres"] = centres[:30]

    result["research"] = research
    logger.info(f"[IIT Madras] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT KANPUR  –  https://www.iitk.ac.in/dord/
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_kanpur() -> dict[str, Any]:
    result = _empty_result()
    soup = _fetch("https://www.iitk.ac.in/dord/")
    if not soup:
        logger.warning("[IIT Kanpur] DORD page unreachable")
        return result
    text = soup.get_text(" ", strip=True)
    research: dict[str, Any] = {}

    # Centres
    centres = [_clean_lab(_clean(a.get_text())) for a in soup.find_all("a")
               if any(k in _clean(a.get_text()).lower() for k in ["centre", "center"])
               and 5 < len(_clean(a.get_text())) < 80]
    centres = [c for c in centres if not _is_junk(c)]
    if centres:
        research["research_centres"] = list(dict.fromkeys(centres))[:20]

    # Facilities/labs from /dord/facilities
    labs: list[str] = []
    soup2 = _fetch("https://www.iitk.ac.in/dord/facilities")
    if soup2:
        for a in soup2.find_all("a"):
            raw = _clean(a.get_text())
            t = _clean_lab(raw)
            if any(k in t.lower() for k in ["lab", "facility", "facilit", "center", "centre", "wind tunnel", "imaging"]) and 4 < len(t) < 90:
                if not _is_junk(t) and t not in labs:
                    labs.append(t)
    if labs:
        result["infrastructure"]["labs"] = labs[:30]

    # Try to get patent count
    soup3 = _fetch("https://www.iitk.ac.in/dord/patents")
    if soup3:
        t3 = soup3.get_text(" ", strip=True)
        v = _extract_int(t3, r"(\d[\d,]*)\s*patents?")
        if v:
            research["patents_filed"] = v

    result["research"] = research
    logger.info(f"[IIT Kanpur] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT KHARAGPUR  –  https://www.iitkgp.ac.in/sric
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_kharagpur() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    # SRIC portal has working project snapshot and research activities pages
    for url in ["https://sric.iitkgp.ac.in/web4/", "https://sric.iitkgp.ac.in/web4/rsact",
                "https://www.iitkgp.ac.in/research-home"]:
        soup = _fetch(url)
        if not soup:
            continue
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v and not research.get("patents_filed"):
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v and not research.get("active_projects"):
            research["active_projects"] = v
        v = _extract_float(text, r"(\d[\d,.]*)\s*crore")
        if v and not research.get("total_funding_crores"):
            research["total_funding_crores"] = v
        centres = [_clean_lab(_clean(a.get_text())) for a in soup.find_all("a")
                   if any(k in _clean(a.get_text()).lower() for k in ["centre", "center", "lab", "institute"])
                   and 8 < len(_clean(a.get_text())) < 80]
        for c in centres:
            if _is_junk(c):
                continue
            existing = research.get("research_centres", [])
            if c not in existing:
                existing.append(c)
            research["research_centres"] = existing

    if research.get("research_centres"):
        research["research_centres"] = list(dict.fromkeys(research["research_centres"]))[:25]
    result["research"] = research
    logger.info(f"[IIT Kharagpur] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT DELHI  –  https://ird.iitd.ac.in/
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_delhi() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    for url in ["https://ird.iitd.ac.in/", "https://ird.iitd.ac.in/node/1197",
                "https://ird.iitd.ac.in/content/research-highlights"]:
        soup = _fetch(url)
        if not soup:
            continue
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v and not research.get("patents_filed"):
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v and not research.get("active_projects"):
            research["active_projects"] = v
        v = _extract_float(text, r"(\d[\d,.]*)\s*crore")
        if v and not research.get("total_funding_crores"):
            research["total_funding_crores"] = v
        centres = [_clean(a.get_text()) for a in soup.find_all("a")
                   if any(k in _clean(a.get_text()).lower() for k in ["centre", "center", "lab"])
                   and 5 < len(_clean(a.get_text())) < 80]
        existing = research.get("research_centres", [])
        for c in centres:
            if c not in existing:
                existing.append(c)
        if existing:
            research["research_centres"] = existing[:20]

    result["research"] = research
    logger.info(f"[IIT Delhi] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT ROORKEE  –  https://www.iitr.ac.in/sric/
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_roorkee() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    # SRIC research page is accessible; main site has "09 CENTRE" stat
    for url in ["https://www.iitr.ac.in/sric/pages/research.html",
                "https://www.iitr.ac.in/", "https://www.iitr.ac.in/research/"]:
        soup = _fetch(url)
        if not soup:
            continue
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v and not research.get("patents_filed"):
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v and not research.get("active_projects"):
            research["active_projects"] = v
        v = _extract_float(text, r"(\d[\d,.]*)\s*crore")
        if v and not research.get("total_funding_crores"):
            research["total_funding_crores"] = v
        v = _extract_int(text, r"(\d+)\s*CENTRE", )
        if v and not research.get("research_centres_count"):
            research["research_centres_count"] = v
        centres = [_clean_lab(_clean(a.get_text())) for a in soup.find_all("a")
                   if any(k in _clean(a.get_text()).lower() for k in ["centre", "center", "lab", "facility"])
                   and 8 < len(_clean(a.get_text())) < 80]
        existing = research.get("research_centres", [])
        for c in centres:
            if not _is_junk(c) and c not in existing:
                existing.append(c)
        if existing:
            research["research_centres"] = existing[:20]

    result["research"] = research
    logger.info(f"[IIT Roorkee] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT GUWAHATI  –  https://www.iitg.ac.in/dric/
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_guwahati() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    # Main page has rich research links; dric subpages are 404
    for url in ["https://www.iitg.ac.in/", "https://www.iitg.ac.in/rnd/ongoingProj.html",
                "https://www.iitg.ac.in/rnd/ongoingProjCoE.html"]:
        soup = _fetch(url)
        if not soup:
            continue
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v and not research.get("patents_filed"):
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v and not research.get("active_projects"):
            research["active_projects"] = v
        centres = [_clean_lab(_clean(a.get_text())) for a in soup.find_all("a")
                   if any(k in _clean(a.get_text()).lower() for k in ["centre", "center", "lab", "research", "incubation"])
                   and 8 < len(_clean(a.get_text())) < 80]
        existing = research.get("research_centres", [])
        for c in centres:
            if not _is_junk(c) and c not in existing:
                existing.append(c)
        if existing:
            research["research_centres"] = existing[:20]

    result["research"] = research
    logger.info(f"[IIT Guwahati] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT BOMBAY  –  https://www.ircc.iitb.ac.in/
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_bombay() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    # rnd.iitb.ac.in redirects properly; ircc.iitb.ac.in is the working IRCC portal
    for url in ["https://rnd.iitb.ac.in", "https://rnd.iitb.ac.in/glimpses",
                "https://instruments.iitb.ac.in/"]:
        soup = _fetch(url)
        if not soup:
            continue
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v and not research.get("patents_filed"):
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v and not research.get("active_projects"):
            research["active_projects"] = v
        v = _extract_float(text, r"(\d[\d,.]*)\s*crore")
        if v and not research.get("total_funding_crores"):
            research["total_funding_crores"] = v
        centres = [_clean_lab(_clean(a.get_text())) for a in soup.find_all("a")
                   if any(k in _clean(a.get_text()).lower() for k in ["centre", "center", "lab", "research"])
                   and 8 < len(_clean(a.get_text())) < 80]
        existing = research.get("research_centres", [])
        for c in centres:
            if not _is_junk(c) and c not in existing:
                existing.append(c)
        if existing:
            research["research_centres"] = existing[:20]

    result["research"] = research
    logger.info(f"[IIT Bombay] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT BHUBANESWAR  –  https://www.iitbbs.ac.in/research.php
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_bhubaneswar() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}
    labs: list[str] = []

    soup = _fetch("https://www.iitbbs.ac.in/research.php")
    if soup:
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v:
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v:
            research["active_projects"] = v

        # Known sub-sections from the nav
        known_centres = [
            "Sponsored Research & Industrial Consultancy (SRIC)",
            "Research & Entrepreneurship Park (REP)",
            "AI & HPC Research Center (AHRC)",
            "Central Research Instrumentation Facility (CRIF)",
        ]
        research["research_centres"] = known_centres

    # Probe SRIC subpage for more stats
    soup2 = _fetch("https://www.iitbbs.ac.in/sric.php")
    if soup2:
        text2 = soup2.get_text(" ", strip=True)
        v = _extract_int(text2, r"(\d[\d,]*)\s*patents?")
        if v and not research.get("patents_filed"):
            research["patents_filed"] = v
        v = _extract_int(text2, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v and not research.get("active_projects"):
            research["active_projects"] = v

    if labs:
        result["infrastructure"]["labs"] = labs
    result["research"] = research
    logger.info(f"[IIT Bhubaneswar] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT ISM DHANBAD  –  https://www.iitism.ac.in/research
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_ism() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    for url in ["https://www.iitism.ac.in/research", "https://www.iitism.ac.in/index.php/rd-cell/about"]:
        soup = _fetch(url)
        if not soup:
            continue
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v and not research.get("patents_filed"):
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v and not research.get("active_projects"):
            research["active_projects"] = v
        v = _extract_float(text, r"(\d[\d,.]*)\s*crore")
        if v and not research.get("total_funding_crores"):
            research["total_funding_crores"] = v
        centres = [_clean(a.get_text()) for a in soup.find_all("a")
                   if any(k in _clean(a.get_text()).lower() for k in ["centre", "center", "lab", "research cell"])
                   and 5 < len(_clean(a.get_text())) < 80]
        existing = research.get("research_centres", [])
        for c in centres:
            if c not in existing:
                existing.append(c)
        if existing:
            research["research_centres"] = existing[:20]

    result["research"] = research
    logger.info(f"[IIT ISM] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT GANDHINAGAR  –  https://www.iitgn.ac.in/research
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_gandhinagar() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    soup = _fetch("https://www.iitgn.ac.in/research")
    if soup:
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v:
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v:
            research["active_projects"] = v
        v = _extract_float(text, r"(\d[\d,.]*)\s*crore")
        if v:
            research["total_funding_crores"] = v
        # Labs + workshops mentioned in links
        labs = [_clean(a.get_text()) for a in soup.find_all("a")
                if any(k in _clean(a.get_text()).lower() for k in ["lab", "workshop", "centre", "center"])
                and 4 < len(_clean(a.get_text())) < 80]
        if labs:
            result["infrastructure"]["labs"] = list(dict.fromkeys(labs))[:20]

    result["research"] = research
    logger.info(f"[IIT Gandhinagar] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT GOA  –  https://iitgoa.ac.in/research
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_goa() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    soup = _fetch("https://iitgoa.ac.in/research")
    if soup:
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v:
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v:
            research["active_projects"] = v
        centres = [_clean(a.get_text()) for a in soup.find_all("a")
                   if any(k in _clean(a.get_text()).lower() for k in ["centre", "center", "lab", "research"])
                   and 5 < len(_clean(a.get_text())) < 80]
        if centres:
            research["research_centres"] = list(dict.fromkeys(centres))[:20]

    result["research"] = research
    logger.info(f"[IIT Goa] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT JODHPUR  –  https://iitj.ac.in/research/
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_jodhpur() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    for url in ["https://iitj.ac.in/research/", "https://iitj.ac.in/research/centres-and-labs"]:
        soup = _fetch(url)
        if not soup:
            continue
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v and not research.get("patents_filed"):
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v and not research.get("active_projects"):
            research["active_projects"] = v
        labs = [_clean(a.get_text()) for a in soup.find_all("a")
                if any(k in _clean(a.get_text()).lower() for k in ["lab", "centre", "center"])
                and 4 < len(_clean(a.get_text())) < 80]
        existing = result["infrastructure"].get("labs", [])
        for l in labs:
            if l not in existing:
                existing.append(l)
        if existing:
            result["infrastructure"]["labs"] = existing[:20]

    result["research"] = research
    logger.info(f"[IIT Jodhpur] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT DHARWAD  –  https://iitdh.ac.in/node/36
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_dharwad() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    soup = _fetch("https://iitdh.ac.in/node/36")
    if soup:
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v:
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v:
            research["active_projects"] = v
        labs = [_clean(a.get_text()) for a in soup.find_all("a")
                if any(k in _clean(a.get_text()).lower() for k in ["lab", "centre", "center"])
                and 4 < len(_clean(a.get_text())) < 80]
        if labs:
            result["infrastructure"]["labs"] = list(dict.fromkeys(labs))[:20]

    result["research"] = research
    logger.info(f"[IIT Dharwad] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT JAMMU  –  https://www.iitjammu.ac.in/research
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_jammu() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    soup = _fetch("https://www.iitjammu.ac.in/research")
    if soup:
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v:
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v:
            research["active_projects"] = v
        centres = [_clean(a.get_text()) for a in soup.find_all("a")
                   if any(k in _clean(a.get_text()).lower() for k in ["centre", "center", "lab"])
                   and 5 < len(_clean(a.get_text())) < 80]
        if centres:
            research["research_centres"] = list(dict.fromkeys(centres))[:20]

    result["research"] = research
    logger.info(f"[IIT Jammu] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT BHILAI  –  https://www.iitbhilai.ac.in/index.php?pid=research
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_bhilai() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    soup = _fetch("https://www.iitbhilai.ac.in/index.php?pid=research")
    if soup:
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v:
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active|ongoing)?\s*projects?")
        if v:
            research["active_projects"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*Ph\.?D")
        if v:
            research["phd_students_enrolled"] = v
        centres = [_clean(a.get_text()) for a in soup.find_all("a")
                   if any(k in _clean(a.get_text()).lower() for k in ["centre", "center", "lab"])
                   and 5 < len(_clean(a.get_text())) < 80]
        if centres:
            research["research_centres"] = list(dict.fromkeys(centres))[:15]

    result["research"] = research
    logger.info(f"[IIT Bhilai] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT ROPAR  –  https://www.iitrpr.ac.in/research
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_ropar() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    for url in ["https://www.iitrpr.ac.in/research", "https://www.iitrpr.ac.in/research/"]:
        soup = _fetch(url)
        if not soup:
            continue
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v and not research.get("patents_filed"):
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v and not research.get("active_projects"):
            research["active_projects"] = v
        centres = [_clean(a.get_text()) for a in soup.find_all("a")
                   if any(k in _clean(a.get_text()).lower() for k in ["centre", "center", "lab"])
                   and 5 < len(_clean(a.get_text())) < 80]
        existing = research.get("research_centres", [])
        for c in centres:
            if c not in existing:
                existing.append(c)
        if existing:
            research["research_centres"] = existing[:15]

    result["research"] = research
    logger.info(f"[IIT Ropar] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT HYDERABAD  –  https://iith.ac.in/research/ (403 – try alternate)
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_hyderabad() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    # research/ returns 403; use main and research-centres page instead
    for url in ["https://iith.ac.in/", "https://iith.ac.in/research-centres/"]:
        soup = _fetch(url)
        if not soup:
            continue
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v and not research.get("patents_filed"):
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v and not research.get("active_projects"):
            research["active_projects"] = v
        # PhD count from main page (1576 PhDs visible)
        v = _extract_int(text, r"(\d[\d,]*)\s*Ph\.?D")
        if v and not research.get("phd_students_enrolled"):
            research["phd_students_enrolled"] = v
        centres = [_clean_lab(_clean(a.get_text())) for a in soup.find_all("a")
                   if any(k in _clean(a.get_text()).lower() for k in ["centre", "center", "incubation"])
                   and 8 < len(_clean(a.get_text())) < 80]
        existing = research.get("research_centres", [])
        for c in centres:
            if not _is_junk(c) and c not in existing:
                existing.append(c)
        if existing:
            research["research_centres"] = existing[:15]

    result["research"] = research
    logger.info(f"[IIT Hyderabad] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT INDORE  –  https://www.iiti.ac.in/research
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_indore() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    # /research returns 500; /page/research and main page work
    for url in ["https://www.iiti.ac.in/page/research", "https://www.iiti.ac.in/"]:
        soup = _fetch(url)
        if not soup:
            continue
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v and not research.get("patents_filed"):
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v and not research.get("active_projects"):
            research["active_projects"] = v
        centres = [_clean_lab(_clean(a.get_text())) for a in soup.find_all("a")
                   if any(k in _clean(a.get_text()).lower() for k in ["centre", "center", "lab", "instrumentation", "entrepreneurship"])
                   and 8 < len(_clean(a.get_text())) < 100]
        existing = research.get("research_centres", [])
        for c in centres:
            if not _is_junk(c) and c not in existing:
                existing.append(c)
        if existing:
            research["research_centres"] = existing[:15]

    result["research"] = research
    logger.info(f"[IIT Indore] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT MANDI  –  https://www.iitmandi.ac.in/research
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_mandi() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    # /research returns 404; main page has 8+ named research centres; /sric works too
    for url in ["https://www.iitmandi.ac.in/", "https://www.iitmandi.ac.in/sric"]:
        soup = _fetch(url)
        if not soup:
            continue
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v and not research.get("patents_filed"):
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v and not research.get("active_projects"):
            research["active_projects"] = v
        centres = [_clean_lab(_clean(a.get_text())) for a in soup.find_all("a")
                   if any(k in _clean(a.get_text()).lower() for k in ["centre", "center", "lab", "biox"])
                   and 8 < len(_clean(a.get_text())) < 100]
        existing = research.get("research_centres", [])
        for c in centres:
            if not _is_junk(c) and c not in existing:
                existing.append(c)
        if existing:
            research["research_centres"] = existing[:20]

    result["research"] = research
    logger.info(f"[IIT Mandi] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT PATNA  –  https://www.iitp.ac.in/index.php/research
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_patna() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    # /research/r&d-home has research stats; /index.php/research redirects
    for url in ["https://www.iitp.ac.in/research/r&d-home",
                "https://www.iitp.ac.in/", "https://www.iitp.ac.in/index.php/research"]:
        soup = _fetch(url)
        if not soup:
            continue
        text = soup.get_text(" ", strip=True)
        # Skip 4-digit numbers that look like phone/year fragments for patents
        for m in re.finditer(r"(\d[\d,]*)\s*patents?", text, re.I):
            raw = int(m.group(1).replace(",", ""))
            if raw < 5000 and not research.get("patents_filed"):   # filter phone-like false positives
                research["patents_filed"] = raw
                break
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v and not research.get("active_projects"):
            research["active_projects"] = v
        centres = [_clean_lab(_clean(a.get_text())) for a in soup.find_all("a")
                   if any(k in _clean(a.get_text()).lower() for k in ["centre", "center", "lab", "incubation"])
                   and 8 < len(_clean(a.get_text())) < 80]
        existing = research.get("research_centres", [])
        for c in centres:
            if not _is_junk(c) and c not in existing:
                existing.append(c)
        if existing:
            research["research_centres"] = existing[:15]

    result["research"] = research
    logger.info(f"[IIT Patna] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT TIRUPATI  –  https://www.iittirupati.ac.in/research/
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_tirupati() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    for url in ["https://www.iittirupati.ac.in/research/", "https://iittirupati.ac.in/research"]:
        soup = _fetch(url)
        if not soup:
            continue
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v and not research.get("patents_filed"):
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v and not research.get("active_projects"):
            research["active_projects"] = v
        centres = [_clean(a.get_text()) for a in soup.find_all("a")
                   if any(k in _clean(a.get_text()).lower() for k in ["centre", "center", "lab"])
                   and 5 < len(_clean(a.get_text())) < 80]
        if centres:
            research["research_centres"] = list(dict.fromkeys(centres))[:15]

    result["research"] = research
    logger.info(f"[IIT Tirupati] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT PALAKKAD  –  https://iitpkd.ac.in/research
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_palakkad() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    # Main page and central-labs page work; /research is 404
    for url in ["https://iitpkd.ac.in/", "https://iitpkd.ac.in/central-labs"]:
        soup = _fetch(url)
        if not soup:
            continue
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v and not research.get("patents_filed"):
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active)?\s*projects?")
        if v and not research.get("active_projects"):
            research["active_projects"] = v
        centres = [_clean_lab(_clean(a.get_text())) for a in soup.find_all("a")
                   if any(k in _clean(a.get_text()).lower() for k in ["centre", "center", "lab", "environmental", "innovation", "csquare"])
                   and 8 < len(_clean(a.get_text())) < 100]
        existing = research.get("research_centres", [])
        for c in centres:
            if not _is_junk(c) and c not in existing:
                existing.append(c)
        if existing:
            research["research_centres"] = list(dict.fromkeys(existing))[:15]

    result["research"] = research
    logger.info(f"[IIT Palakkad] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# IIT BHU VARANASI  –  https://www.iitbhu.ac.in/research
# ══════════════════════════════════════════════════════════════════════════════

def research_iit_bhu() -> dict[str, Any]:
    result = _empty_result()
    research: dict[str, Any] = {}

    # Main page shows "575 Sponsored" projects and many centre links; /research is 404
    for url in ["https://www.iitbhu.ac.in/", "https://www.iitbhu.ac.in/dean/dord"]:
        soup = _fetch(url)
        if not soup:
            continue
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v and not research.get("patents_filed"):
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*Sponsored")
        if v and not research.get("active_projects"):
            research["active_projects"] = v
        v = _extract_float(text, r"(\d[\d,.]*)\s*crore")
        if v and not research.get("total_funding_crores"):
            research["total_funding_crores"] = v
        centres = [_clean_lab(_clean(a.get_text())) for a in soup.find_all("a")
                   if any(k in _clean(a.get_text()).lower() for k in ["centre", "center", "lab", "incubation"])
                   and 8 < len(_clean(a.get_text())) < 80]
        existing = research.get("research_centres", [])
        for c in centres:
            if not _is_junk(c) and c not in existing:
                existing.append(c)
        if existing:
            research["research_centres"] = existing[:20]

    result["research"] = research
    logger.info(f"[IIT BHU] research data: {research}")
    return result


# ══════════════════════════════════════════════════════════════════════════════
# REGISTRY
# ══════════════════════════════════════════════════════════════════════════════

_RESEARCH_REGISTRY: dict[str, Any] = {
    "iit-madras":       research_iit_madras,
    "iit-kanpur":       research_iit_kanpur,
    "iit-kharagpur":    research_iit_kharagpur,
    "iit-delhi":        research_iit_delhi,
    "iit-roorkee":      research_iit_roorkee,
    "iit-guwahati":     research_iit_guwahati,
    "iit-bombay":       research_iit_bombay,
    "iit-bhubaneswar":  research_iit_bhubaneswar,
    "iit-ism-dhanbad":  research_iit_ism,
    "iit-gandhinagar":  research_iit_gandhinagar,
    "iit-goa":          research_iit_goa,
    "iit-jodhpur":      research_iit_jodhpur,
    "iit-dharwad":      research_iit_dharwad,
    "iit-jammu":        research_iit_jammu,
    "iit-bhilai":       research_iit_bhilai,
    "iit-ropar":        research_iit_ropar,
    "iit-hyderabad":    research_iit_hyderabad,
    "iit-indore":       research_iit_indore,
    "iit-mandi":        research_iit_mandi,
    "iit-patna":        research_iit_patna,
    "iit-tirupati":     research_iit_tirupati,
    "iit-palakkad":     research_iit_palakkad,
    "iit-bhu-varanasi": research_iit_bhu,
}


# ══════════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

def _find_json_file(parsed_dir: Path, slug: str) -> Path | None:
    slug_clean = slug.lower().replace("-", "")
    for f in parsed_dir.glob("*_structured.json"):
        name = f.stem.replace("_structured", "").lower().replace("-", "").replace("_", "")
        if slug_clean in name or name in slug_clean:
            return f
    return None


def _merge_research(existing_research: dict | None, scraped: dict) -> dict:
    """Merge scraped research dict into existing, keeping existing non-None values."""
    merged = dict(existing_research or {})
    for key, val in scraped.items():
        if val is not None and val != [] and val != {}:
            if key not in merged or merged[key] is None:
                merged[key] = val
            elif isinstance(val, list) and isinstance(merged[key], list):
                # extend without duplicates
                existing_set = set(merged[key])
                for item in val:
                    if item not in existing_set:
                        merged[key].append(item)
                        existing_set.add(item)
    return merged


def run_all_research_scrapers(parsed_dir: str | None = None, target: str | None = None) -> None:
    """Run all IIT research scrapers and merge results into _structured.json files."""
    if parsed_dir is None:
        here = Path(__file__).parent
        parsed_dir_path = here.parent / "data" / "parsed"
    else:
        parsed_dir_path = Path(parsed_dir)

    registry = {target: _RESEARCH_REGISTRY[target]} if target else _RESEARCH_REGISTRY

    for slug, scraper_fn in registry.items():
        logger.info(f"\n{'='*60}\nResearch scraper: {slug}\n{'='*60}")
        try:
            result = scraper_fn()
        except Exception as exc:
            logger.error(f"Scraper {slug} crashed: {exc}")
            continue

        research_data = result.get("research", {})
        infra_data    = result.get("infrastructure", {})

        if not research_data and not infra_data:
            logger.warning(f"No research data returned for {slug}")
            continue

        json_file = _find_json_file(parsed_dir_path, slug)
        if not json_file:
            logger.warning(f"No JSON file found for {slug}")
            continue

        with open(json_file, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        # Merge research field
        if research_data:
            data["research"] = _merge_research(data.get("research"), research_data)

        # Merge infrastructure.labs
        if infra_data.get("labs"):
            existing_infra = data.get("infrastructure") or {}
            existing_labs  = existing_infra.get("labs") or []
            new_labs       = infra_data["labs"]
            merged_labs    = list(dict.fromkeys(existing_labs + new_labs))
            existing_infra["labs"] = merged_labs
            if infra_data.get("central_instruments"):
                existing_infra["central_instruments"] = infra_data["central_instruments"]
            data["infrastructure"] = existing_infra

        with open(json_file, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)

        logger.info(
            f"✅ Updated {json_file.name}: "
            f"research keys={list(research_data.keys())}, "
            f"labs={len(infra_data.get('labs', []))}"
        )


