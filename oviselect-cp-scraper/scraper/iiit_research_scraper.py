"""IIIT Research Data Scraper.

Scrapes research metrics (patents, projects, labs, research centres)
from official IIIT websites and merges the data into the `research` and
`infrastructure.labs` fields of the existing data/parsed/iiit-*_structured.json files.
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

# ── Helpers ───────────────────────────────────────────────────────────────────

def _fetch(url: str, retries: int = 1, timeout: int = 10) -> BeautifulSoup | None:
    return _scrapling_fetch(url, retries=retries, timeout=timeout, verify=False)


def _clean(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def _extract_int(text: str, pattern: str) -> int | None:
    m = re.search(pattern, text, re.I)
    if m:
        try:
            val = int(m.group(1).replace(",", "").strip())
            # Reject year-like numbers (1990–2030) as false positives
            if 1990 <= val <= 2030:
                return None
            return val
        except ValueError:
            return None
    return None


def _extract_float(text: str, pattern: str) -> float | None:
    m = re.search(pattern, text, re.I)
    if m:
        try:
            return float(m.group(1).replace(",", "").strip())
        except ValueError:
            return None
    return None


_NAV_JUNK = {
    "research", "centres", "facilities", "center", "lab", "laboratory",
    "research highlights", "research areas", "research programmes",
    "research facilities", "about", "home", "contact", "menu",
    "laboratories", "labs", "virtual labs", "health centre", "medical centre",
    "computer centre", "health care center",
}


def _is_junk(text: str) -> bool:
    t = text.strip().lower()
    if t in _NAV_JUNK:
        return True
    if len(t) < 8:
        return True
    if "click to collapse" in t or t.startswith("+ -"):
        return True
    return False


def _clean_lab(text: str) -> str:
    t = re.sub(r"^\+\s*-\s*", "", text).strip()
    t = re.sub(r"\s*Click to collapse.*$", "", t, flags=re.I).strip()
    t = re.sub(r"\s*\|.*$", "", t).strip()
    t = re.sub(r"\s*\(PDF\)$", "", t, flags=re.I).strip()
    return t


def _empty_result() -> dict[str, Any]:
    return {"research": {}, "infrastructure": {}}


def _scrape_iiit(urls: list[str], name: str, extra_kw: list[str] | None = None) -> dict[str, Any]:
    """Generic scraper that covers most IIITs: tries each URL, extracts metrics + centre links."""
    result = _empty_result()
    research: dict[str, Any] = {}
    kw = ["centre", "center", "incubation", "innovation"] + (extra_kw or [])
    for url in urls:
        soup = _fetch(url)
        if not soup:
            continue
        text = soup.get_text(" ", strip=True)
        v = _extract_int(text, r"(\d[\d,]*)\s*patents?")
        if v and not research.get("patents_filed"):
            research["patents_filed"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*(?:sponsored|active|ongoing)?\s*projects?")
        if v and not research.get("active_projects"):
            research["active_projects"] = v
        v = _extract_int(text, r"(\d[\d,]*)\s*Ph\.?D")
        if v and not research.get("phd_students_enrolled"):
            research["phd_students_enrolled"] = v
        v = _extract_float(text, r"(\d[\d,.]*)\s*crore")
        if v and not research.get("total_funding_crores"):
            research["total_funding_crores"] = v
        centres = [_clean_lab(_clean(a.get_text())) for a in soup.find_all("a")
                   if any(k in _clean(a.get_text()).lower() for k in kw)
                   and 8 < len(_clean(a.get_text())) < 90]
        existing = research.get("research_centres", [])
        for c in centres:
            if not _is_junk(c) and c not in existing:
                existing.append(c)
        if existing:
            research["research_centres"] = existing[:15]
    result["research"] = research
    logger.info(f"[{name}] research: {research}")
    return result



# ══════════════════════════════════════════════════════════════════════════════
# Per-IIIT scraper functions
# ══════════════════════════════════════════════════════════════════════════════

def research_iiit_agartala() -> dict[str, Any]:
    return _scrape_iiit(["http://www.iiit-agartala.ac.in/"], "IIIT Agartala")

def research_iiit_allahabad() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiita.ac.in/research/",
        "https://www.iiita.ac.in/research/labs/",
        "https://www.iiita.ac.in/",
    ], "IIIT Allahabad", extra_kw=["lab", "group"])

def research_iiit_bhagalpur() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitbh.ac.in/research",
        "https://www.iiitbh.ac.in/",
    ], "IIIT Bhagalpur", extra_kw=["lab", "group"])

def research_iiit_bhopal() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitbhopal.ac.in/",
        "https://www.iiitbhopal.ac.in/research",
    ], "IIIT Bhopal")

def research_iiit_bhubaneswar() -> dict[str, Any]:
    return _scrape_iiit([
        "http://www.iiit-bh.ac.in/research/",
        "http://www.iiit-bh.ac.in/",
    ], "IIIT Bhubaneswar")

def research_iiit_dharwad() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitdwd.ac.in/",
        "https://www.iiitdwd.ac.in/research",
    ], "IIIT Dharwad")

def research_iiit_guwahati() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitg.ac.in/research",
        "https://www.iiitg.ac.in/",
    ], "IIIT Guwahati", extra_kw=["lab", "group"])

def research_iiit_kalyani() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitkalyani.ac.in/research",
        "https://www.iiitkalyani.ac.in/",
    ], "IIIT Kalyani")

def research_iiit_kota() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitkota.ac.in/research",
        "https://www.iiitkota.ac.in/",
    ], "IIIT Kota")

def research_iiit_kottayam() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitkottayam.ac.in/",
        "https://www.iiitkottayam.ac.in/research",
    ], "IIIT Kottayam", extra_kw=["group"])

def research_iiit_lucknow() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitl.ac.in/index.php/research/",
        "https://www.iiitl.ac.in/",
    ], "IIIT Lucknow", extra_kw=["incubation"])

def research_iiit_manipur() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitmanipur.ac.in/",
        "https://www.iiitmanipur.ac.in/research",
    ], "IIIT Manipur")

def research_iiit_nagpur() -> dict[str, Any]:
    return _scrape_iiit([
        "http://www.iiitn.ac.in/",
        "http://www.iiitn.ac.in/index.php/research",
    ], "IIIT Nagpur")

def research_iiit_naya_raipur() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitnr.ac.in/",
        "https://www.iiitnr.ac.in/research",
    ], "IIIT Naya Raipur")

def research_iiit_pune() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitp.ac.in/",
        "https://www.iiitp.ac.in/index.php/research",
    ], "IIIT Pune", extra_kw=["lab"])

def research_iiit_raichur() -> dict[str, Any]:
    return _scrape_iiit([
        "http://www.iiitrl.ac.in/",
    ], "IIIT Raichur")

def research_iiit_ranchi() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitranchi.ac.in/",
        "https://www.iiitranchi.ac.in/research",
    ], "IIIT Ranchi")

def research_iiit_sonepat() -> dict[str, Any]:
    return _scrape_iiit([
        "http://www.iiitkl.ac.in/",
    ], "IIIT Sonepat")

def research_iiit_sri_city() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiits.ac.in/research/",
        "https://www.iiits.ac.in/",
    ], "IIIT Sri City", extra_kw=["lab", "group"])

def research_iiit_surat() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitsurat.ac.in/",
        "https://www.iiitsurat.ac.in/research",
    ], "IIIT Surat")

def research_iiit_trichy() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitt.ac.in/",
        "https://www.iiitt.ac.in/research",
    ], "IIIT Trichy")

def research_iiit_una() -> dict[str, Any]:
    return _scrape_iiit([
        "http://www.iiituna.ac.in/",
    ], "IIIT Una")

def research_iiit_vadodara() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitvadodara.ac.in/",
        "http://www.iiitvadodara.ac.in/",
    ], "IIIT Vadodara")

def research_iiitdm_jabalpur() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitdmj.ac.in/research/",
        "https://www.iiitdmj.ac.in/",
    ], "IIITDM Jabalpur", extra_kw=["lab"])

def research_iiitdm_kancheepuram() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitdm.ac.in/",
        "https://www.iiitdm.ac.in/research/",
    ], "IIITDM Kancheepuram", extra_kw=["lab"])

def research_iiitdm_kurnool() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitk.ac.in/",
        "https://www.iiitk.ac.in/research",
    ], "IIITDM Kurnool", extra_kw=["lab"])

def research_iiitm_gwalior() -> dict[str, Any]:
    return _scrape_iiit([
        "https://www.iiitm.ac.in/index.php/en/",
        "https://www.iiitm.ac.in/index.php/en/research",
    ], "IIITM Gwalior", extra_kw=["lab", "excellence"])



# ══════════════════════════════════════════════════════════════════════════════
# REGISTRY  —  slug → scraper function
# ══════════════════════════════════════════════════════════════════════════════

_IIIT_REGISTRY: dict[str, Any] = {
    "iiit-agartala":         research_iiit_agartala,
    "iiit-allahabad":        research_iiit_allahabad,
    "iiit-bhagalpur":        research_iiit_bhagalpur,
    "iiit-bhopal":           research_iiit_bhopal,
    "iiit-bhubaneswar":      research_iiit_bhubaneswar,
    "iiit-dharwad":          research_iiit_dharwad,
    "iiit-guwahati":         research_iiit_guwahati,
    "iiit-kalyani":          research_iiit_kalyani,
    "iiit-kota":             research_iiit_kota,
    "iiit-kottayam":         research_iiit_kottayam,
    "iiit-lucknow":          research_iiit_lucknow,
    "iiit-manipur":          research_iiit_manipur,
    "iiit-nagpur":           research_iiit_nagpur,
    "iiit-naya-raipur":      research_iiit_naya_raipur,
    "iiit-pune":             research_iiit_pune,
    "iiit-raichur":          research_iiit_raichur,
    "iiit-ranchi":           research_iiit_ranchi,
    "iiit-sonepat":          research_iiit_sonepat,
    "iiit-sri-city":         research_iiit_sri_city,
    "iiit-surat":            research_iiit_surat,
    "iiit-trichy":           research_iiit_trichy,
    "iiit-una":              research_iiit_una,
    "iiit-vadodara":         research_iiit_vadodara,
    "iiitdm-jabalpur":       research_iiitdm_jabalpur,
    "iiitdm-kancheepuram":   research_iiitdm_kancheepuram,
    "iiitdm-kurnool":        research_iiitdm_kurnool,
    "iiitm-gwalior":         research_iiitm_gwalior,
}


# ══════════════════════════════════════════════════════════════════════════════
# MERGE HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _find_iiit_json(parsed_dir: Path, slug: str) -> Path | None:
    """Find the JSON file matching the given IIIT slug.
    Requires the file to start with 'iiit' (not just 'iit') to avoid
    accidental matches against IIT files (e.g. iiit-dharwad vs iit-dharwad).
    """
    slug_clean = slug.lower().replace("-", "").replace("_", "")
    candidates = []
    for f in parsed_dir.glob("*_structured.json"):
        name = f.stem.replace("_structured", "").lower().replace("-", "").replace("_", "")
        # Only consider files that are clearly IIIT files
        if not name.startswith("iiit"):
            continue
        if slug_clean == name:          # exact match wins immediately
            return f
        if slug_clean in name or name in slug_clean:
            candidates.append(f)
    if len(candidates) == 1:
        return candidates[0]
    if candidates:
        # prefer the shortest name (closest match)
        return min(candidates, key=lambda f: len(f.stem))
    return None


def _merge_research(existing: dict | None, scraped: dict) -> dict:
    merged = dict(existing or {})
    for key, val in scraped.items():
        if val is None or val == [] or val == {}:
            continue
        if key not in merged or merged[key] is None:
            merged[key] = val
        elif isinstance(val, list) and isinstance(merged[key], list):
            seen = set(merged[key])
            for item in val:
                if item not in seen:
                    merged[key].append(item)
                    seen.add(item)
    return merged


# ══════════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

def run_all_iiit_research_scrapers(
    parsed_dir: str | None = None,
    target: str | None = None,
) -> None:
    """Run all IIIT research scrapers and persist results to JSON files."""
    if parsed_dir is None:
        parsed_dir_path = Path(__file__).parent.parent / "data" / "parsed"
    else:
        parsed_dir_path = Path(parsed_dir)

    registry = {target: _IIIT_REGISTRY[target]} if target else _IIIT_REGISTRY

    for slug, scraper_fn in registry.items():
        logger.info(f"\n{'='*60}\nIIIT Research scraper: {slug}\n{'='*60}")
        try:
            result = scraper_fn()
        except Exception as exc:
            logger.error(f"Scraper {slug} crashed: {exc}")
            continue

        research_data = result.get("research", {})
        infra_data    = result.get("infrastructure", {})

        if not research_data and not infra_data:
            logger.warning(f"No data returned for {slug}")
            continue

        json_file = _find_iiit_json(parsed_dir_path, slug)
        if not json_file:
            logger.warning(f"No JSON file found for slug '{slug}'")
            continue

        with open(json_file, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        if research_data:
            data["research"] = _merge_research(data.get("research"), research_data)

        if infra_data.get("labs"):
            existing_infra = data.get("infrastructure") or {}
            existing_labs  = existing_infra.get("labs") or []
            merged_labs    = list(dict.fromkeys(existing_labs + infra_data["labs"]))
            existing_infra["labs"] = merged_labs
            data["infrastructure"] = existing_infra

        with open(json_file, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)

        logger.info(
            f"✅ {json_file.name}: research_keys={list(research_data.keys())}"
        )
