"""Load the list of colleges to scrape from cp_slugs.py."""

from __future__ import annotations

from config.cp_slugs import COLLEGE_PRAVESH_SLUGS
from loguru import logger


def classify_institute(name: str) -> str:
    """Classify an institute name into IIT/NIT/IIIT/GFTI."""
    lo = name.lower()
    if lo.startswith("iit ") or lo.startswith("iit("):
        return "IIT"
    if "national institute of technology" in lo or lo.startswith("nit ") or lo.startswith("nit,"):
        return "NIT"
    if lo.startswith("mnit") or lo.startswith("manit") or lo.startswith("mnnit") or lo.startswith("svnit") or lo.startswith("vnit"):
        return "NIT"
    if lo.startswith("dr.bramnit"):
        return "NIT"
    if "indian institute of engineering science" in lo:
        return "NIT"
    if lo.startswith("iiit") or lo.startswith("abv-iiit") or "indian institute of information technology" in lo:
        return "IIIT"
    if lo.startswith("intiiit"):
        return "IIIT"
    if "pt. dwarka" in lo and "jabalpur" in lo:
        return "IIIT"
    return "GFTI"


def get_colleges(
    type_filter: str = "ALL",
    single_college: str | None = None,
) -> list[tuple[str, str, str]]:
    """Return list of (institute_name, slug, institute_type) to process.

    Args:
        type_filter: One of IIT, NIT, IIIT, GFTI, ALL.
        single_college: If set, only return this one college.

    Returns:
        List of (name, slug, type) tuples.
    """
    colleges: list[tuple[str, str, str]] = []

    for name, slug in COLLEGE_PRAVESH_SLUGS.items():
        if slug is None:
            continue  # No CollegePravesh page

        inst_type = classify_institute(name)

        if single_college:
            if name == single_college:
                return [(name, slug, inst_type)]
            continue

        if type_filter != "ALL" and inst_type != type_filter:
            continue

        colleges.append((name, slug, inst_type))

    if single_college:
        logger.warning(f"College '{single_college}' not found in slug mapping")
        return []

    logger.info(f"Loaded {len(colleges)} colleges (filter={type_filter})")
    return colleges

