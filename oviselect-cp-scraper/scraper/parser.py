"""Parse CollegePravesh HTML pages into structured dictionaries.

CollegePravesh uses `p.cp-clg-h` for section headings with sibling
content blocks (tables, paragraphs, etc.) following each heading.
"""

from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup, Tag, NavigableString
from loguru import logger


def _text(el: Tag | None) -> str | None:
    """Extract cleaned text from a BS4 element."""
    if el is None:
        return None
    t = el.get_text(separator=" ", strip=True)
    return t if t else None


def _extract_number(text: str | None) -> float | None:
    """Extract first number from text, stripping ₹ and commas."""
    if not text:
        return None
    clean = text.replace("₹", "").replace(",", "").strip()
    m = re.search(r"[\d]+\.?\d*", clean)
    if m:
        try:
            return float(m.group())
        except ValueError:
            return None
    return None


def _extract_int(text: str | None) -> int | None:
    v = _extract_number(text)
    return int(v) if v is not None else None


def _find_heading(soup: BeautifulSoup, keyword: str) -> Tag | None:
    """Find a `p.cp-clg-h` heading whose text matches keyword (case-insensitive)."""
    for p in soup.find_all("p", class_="cp-clg-h"):
        txt = _text(p) or ""
        if keyword.lower() in txt.lower():
            return p
    return None


def _next_table(heading: Tag) -> Tag | None:
    """Find the table associated with a ``p.cp-clg-h`` heading.

    CollegePravesh uses this DOM pattern::

        div.box-card
          div.box-h  →  contains the  p.cp-clg-h  heading
          div.box-p  →  contains the  <table>

    So we first try the structural approach (heading → box-card → table).
    If that fails we fall back to ``find_next("table")`` with a proximity
    guard so we don't accidentally grab a table from the next section.
    """
    # ── Structural approach ────────────────────────────────────
    box_h = heading.find_parent("div", class_="box-h")
    if box_h:
        box_card = box_h.find_parent("div", class_="box-card")
        if box_card:
            box_p = box_card.find("div", class_="box-p")
            if box_p:
                tbl = box_p.find("table")
                if tbl:
                    return tbl

    # ── Fallback: find_next with section-boundary guard ────────
    tbl = heading.find_next("table")
    if tbl is None:
        return None

    # Make sure there is no other cp-clg-h heading between us and the table
    next_heading = heading.find_next("p", class_="cp-clg-h")
    if next_heading and next_heading != heading:
        # If the next heading appears before the table in the source,
        # the table belongs to a different section.
        if next_heading.sourceline is not None and tbl.sourceline is not None:
            if next_heading.sourceline < tbl.sourceline:
                return None

    return tbl


def _parse_table_rows(table: Tag) -> list[dict[str, str]]:
    """Parse an HTML table into a list of dicts (header → value)."""
    rows = []
    all_rows = table.find_all("tr")
    if not all_rows:
        return rows

    # Extract headers from first row
    headers = []
    first_row = all_rows[0]
    for cell in first_row.find_all(["th", "td"]):
        headers.append(_text(cell) or "")

    for tr in all_rows[1:]:
        cells = tr.find_all(["td", "th"])
        if not cells:
            continue
        if headers:
            row = {headers[i]: _text(cells[i]) for i in range(min(len(headers), len(cells)))}
        else:
            row = {str(i): _text(c) for i, c in enumerate(cells)}
        rows.append(row)
    return rows


# ── Overview ─────────────────────────────────────────────────
def _parse_overview(soup: BeautifulSoup) -> dict[str, Any]:
    """Extract data from the overview table and nearby headings."""
    data: dict[str, Any] = {}

    # The first table after "Overview" heading has key-value rows:
    # Institute Name | …, Also Known As | …, Institute Type | …,
    # Established | …, Location | …
    heading = _find_heading(soup, "Overview")
    if not heading:
        return data

    tbl = _next_table(heading)
    if tbl:
        for tr in tbl.find_all("tr"):
            cells = tr.find_all(["td", "th"])
            if len(cells) < 2:
                continue
            label = (_text(cells[0]) or "").lower()
            value = _text(cells[1])
            if not value:
                continue

            if "also known" in label:
                data["also_known_as"] = value
            elif "institute type" in label or "type" in label:
                data["institute_type"] = value
            elif "established" in label:
                data["established_year"] = _extract_int(value)
            elif "location" in label:
                # "Mumbai, Maharashtra" → city + state
                if "," in value:
                    parts = [p.strip() for p in value.split(",")]
                    data["city"] = parts[0]
                    data["state"] = parts[-1]
                else:
                    data["city"] = value

    return data


# ── Address ──────────────────────────────────────────────────
def _parse_address(soup: BeautifulSoup) -> dict[str, Any]:
    """Extract full postal address from the ADDRESS section."""
    data: dict[str, Any] = {}
    heading = _find_heading(soup, "ADDRESS")
    if not heading:
        return data
    box_h = heading.find_parent("div", class_="box-h")
    if box_h:
        card = box_h.find_parent("div", class_="box-card")
        if card:
            box_p = card.find("div", class_="box-p")
            if box_p:
                addr = _text(box_p)
                if addr:
                    data["address"] = addr
    return data


# ── Nearest Transport ─────────────────────────────────────────
def _parse_nearby_transport(soup: BeautifulSoup) -> dict[str, Any]:
    """Extract nearest airport and railway station from .nearby-box divs.

    CollegePravesh uses icons (fa-plane / fa-train) inside .nearby-box
    divs to distinguish airport and railway entries.
    """
    data: dict[str, Any] = {}
    heading = _find_heading(soup, "Nearest Airport")
    if not heading:
        return data
    box_h = heading.find_parent("div", class_="box-h")
    if not box_h:
        return data
    card = box_h.find_parent("div", class_="box-card")
    if not card:
        return data
    box_p = card.find("div", class_="box-p")
    if not box_p:
        return data

    for nearby in box_p.find_all("div", class_="nearby-box"):
        icon = nearby.find("i")
        name_el = nearby.find("div", class_="nearby-name")
        dist_el = nearby.find("div", class_="nearby-distance")
        if not icon or not name_el:
            continue
        icon_classes = icon.get("class", [])
        name = _text(name_el)
        dist = _extract_number(_text(dist_el))

        if "fa-plane" in icon_classes:
            if name and "nearest_airport" not in data:
                data["nearest_airport"] = name
            if dist is not None and "nearest_airport_km" not in data:
                data["nearest_airport_km"] = dist
        elif "fa-train" in icon_classes:
            if name and "nearest_railway_station" not in data:
                data["nearest_railway_station"] = name
            if dist is not None and "nearest_railway_km" not in data:
                data["nearest_railway_km"] = dist

    return data


# ── Rankings ─────────────────────────────────────────────────
def _parse_rankings(soup: BeautifulSoup) -> dict[str, Any]:
    """Extract from the RANKING table (Body / Category / Latest / Previous).

    The table can have 3 or 4 columns per data row:
      4-col: [body_or_empty, category, latest_rank, prev_rank]
      3-col: [category, latest_rank, prev_rank]
    Rows with fewer than 3 cells are headers/separators and are skipped.
    """
    data: dict[str, Any] = {}
    heading = _find_heading(soup, "RANKING")
    if not heading:
        return data

    tbl = _next_table(heading)
    if not tbl:
        return data

    for tr in tbl.find_all("tr"):
        cells = [(_text(c) or "") for c in tr.find_all(["td", "th"])]
        n = len(cells)

        # Determine category text and rank value based on column count
        if n >= 4:
            # [body_or_empty, category, latest_rank, prev_rank]
            category = cells[1]
            rank_val = cells[2]
        elif n == 3:
            # [category, latest_rank, prev_rank]
            category = cells[0]
            rank_val = cells[1]
        else:
            continue  # skip header rows and section separators

        # Skip empty, placeholder, or header values
        if not category or not rank_val or rank_val in ("--", "Latest", "Previous", "Rank (Year)"):
            continue
        if category in ("Body", "Category", "Latest", "Previous"):
            continue

        cat_lower = category.lower()

        if "nirf" in cat_lower:
            if "overall" in cat_lower:
                data.setdefault("nirf_overall_rank", _extract_int(rank_val))
            elif "engineering" in cat_lower:
                data.setdefault("nirf_engineering_rank", _extract_int(rank_val))
            elif "research" in cat_lower:
                data.setdefault("nirf_research_rank", _extract_int(rank_val))
            elif "innovation" in cat_lower:
                data.setdefault("nirf_innovation_rank", rank_val)
        elif cat_lower == "qs world university rankings":
            data.setdefault("qs_world_rank", rank_val)
        elif cat_lower == "qs asia university rankings":
            data.setdefault("qs_asia_rank", rank_val)
        elif "times higher education" in cat_lower and "asia" in cat_lower:
            data.setdefault("the_asia_rank", rank_val)
        elif "times higher education" in cat_lower:
            data.setdefault("the_world_rank", rank_val)
        elif "outlook" in cat_lower:
            data.setdefault("outlook_rank", _extract_int(rank_val))
        elif "india today" in cat_lower:
            data.setdefault("india_today_rank", _extract_int(rank_val))
        elif "week" in cat_lower:
            data.setdefault("the_week_rank", _extract_int(rank_val))

    return data


# ── Fees ─────────────────────────────────────────────────────
def _parse_fee_table(heading: Tag, data: dict[str, Any], is_hostel: bool) -> None:
    """Parse a fee table (Institute Fee or Hostel Fee)."""
    tbl = _next_table(heading)
    if not tbl:
        return

    for tr in tbl.find_all("tr"):
        cells = tr.find_all(["td", "th"])
        if len(cells) < 2:
            continue
        label = (_text(cells[0]) or "").lower()
        amount_txt = _text(cells[1])

        if "tuition" in label:
            data.setdefault("tuition_fee_per_sem", _extract_int(amount_txt))
        elif "caution" in label or "security" in label:
            # "Caution Money (One-Time, Refundable)" → caution_money, not one_time_fees
            data.setdefault("caution_money", _extract_int(amount_txt))
        elif "mess" in label:
            data.setdefault("mess_advance_per_sem", _extract_int(amount_txt))
        elif "hostel" in label and "total" not in label:
            data.setdefault("hostel_fee_per_sem", _extract_int(amount_txt))
        elif "one time" in label or "one-time" in label:
            data.setdefault("one_time_fees", _extract_int(amount_txt))
        elif "annual" in label:
            data.setdefault("annual_fees", _extract_int(amount_txt))
        elif "total" in label:
            if is_hostel:
                data.setdefault("total_hostel_fee", _extract_int(amount_txt))
            else:
                data.setdefault("total_institute_fee", _extract_int(amount_txt))


def _parse_fees(soup: BeautifulSoup) -> dict[str, Any]:
    """Extract from fee tables.

    Some pages use separate "Institute Fee" / "Hostel Fee" headings;
    others use a single "FEE STRUCTURE", "Fees", or "Fee Structure" heading
    with one combined table.  We try both patterns.
    """
    data: dict[str, Any] = {}

    # Pattern 1: separate Institute Fee / Hostel Fee headings
    inst_h = _find_heading(soup, "Institute Fee")
    if inst_h:
        _parse_fee_table(inst_h, data, is_hostel=False)

    hostel_h = _find_heading(soup, "Hostel Fee")
    if hostel_h:
        _parse_fee_table(hostel_h, data, is_hostel=True)

    # Pattern 2: combined heading ("FEE STRUCTURE", "Fees", "Fee Structure")
    if not data:
        for keyword in ("FEE STRUCTURE", "Fee Structure", "Fees"):
            h = _find_heading(soup, keyword)
            if h and (_text(h) or "").strip().upper() != "FEE WAIVERS":
                _parse_fee_table(h, data, is_hostel=False)
                if data:
                    break

    # Fee waivers — list items inside the Fee Waivers section
    waiver_h = _find_heading(soup, "Fee Waivers") or _find_heading(soup, "FEE WAIVERS")
    if waiver_h:
        box_h = waiver_h.find_parent("div", class_="box-h")
        if box_h:
            card = box_h.find_parent("div", class_="box-card")
            if card:
                box_p = card.find("div", class_="box-p")
                if box_p:
                    waivers = [_text(li) for li in box_p.find_all("li") if _text(li)]
                    if waivers:
                        data["fee_waivers"] = waivers

    return data


# ── Placements ───────────────────────────────────────────────
def _get_best_toggle(soup: BeautifulSoup) -> Tag | None:
    """Return the toggle-content div that has the richest placement data.

    CollegePravesh has year toggles (2023, 2022, …).  The most recent one
    often only has placement-% stats; the one before it (e.g. 2022) may
    have median/avg/highest CTC tables.  We pick the first toggle that
    contains at least **two** box-card children with tables.  If none
    qualifies, return the first toggle.
    """
    toggles = soup.find_all("h3", class_="toggle-head")
    if not toggles:
        return None

    best: Tag | None = None
    for toggle in toggles:
        parent = toggle.parent
        if not parent:
            continue
        content = parent.find("div", class_="toggle-content")
        if not content:
            continue
        if best is None:
            best = content  # fallback = first toggle
        # Count box-cards that actually have a table in their box-p
        cards_with_tables = 0
        for card in content.find_all("div", class_="box-card"):
            bp = card.find("div", class_="box-p")
            if bp and bp.find("table"):
                cards_with_tables += 1
        if cards_with_tables >= 2:
            return content  # rich enough

    return best


def _extract_branchwise(tbl: Tag) -> dict[str, float]:
    """Turn a 2-column branch table into {branch: value}."""
    result: dict[str, float] = {}
    for tr in tbl.find_all("tr"):
        cells = tr.find_all(["td", "th"])
        if len(cells) < 2:
            continue
        branch = (_text(cells[0]) or "").strip()
        val = _extract_number(_text(cells[1]))
        if branch and val is not None:
            result[branch] = val
    return result


def _parse_placements(soup: BeautifulSoup) -> dict[str, Any]:
    """Extract placement stats from top-level tables and latest year toggle."""
    data: dict[str, Any] = {}

    # ── Top-level placement stats (branch-wise placed %) ──────
    # The "Placement Statistics" heading NOT inside a toggle has overall %
    for p in soup.find_all("p", class_="cp-clg-h"):
        if p.find_parent(class_="toggle-content"):
            continue
        txt = (_text(p) or "").strip()
        if txt == "Placement Statistics":
            tbl = _next_table(p)
            if tbl:
                bw = _extract_branchwise(tbl)
                # Look for the "Overall" row for overall_placement_pct
                for k, v in bw.items():
                    if "overall" in k.lower():
                        data["overall_placement_pct"] = v
                        break
                data["branch_wise_placement_pct"] = bw
            break

    # ── Year-toggle data (median, avg, highest CTC) ──────────
    toggle = _get_best_toggle(soup)

    # Identify the placement year from the toggle head that matches the selected toggle
    if toggle:
        for h3 in soup.find_all("h3", class_="toggle-head"):
            parent = h3.parent
            if parent:
                content = parent.find("div", class_="toggle-content")
                if content == toggle:
                    year = _extract_int(_text(h3))
                    if year:
                        data["placement_year"] = year
                    break

    if toggle:
        for p in toggle.find_all("p", class_="cp-clg-h"):
            heading_text = (_text(p) or "").lower()
            tbl = _next_table(p)
            if not tbl:
                continue

            if "median" in heading_text and "package" in heading_text:
                bw = _extract_branchwise(tbl)
                if bw:
                    data["branch_wise_median_ctc"] = bw
                    # Compute overall median as average of branch medians
                    vals = [v for v in bw.values() if v > 0]
                    if vals:
                        data["median_package_lpa"] = round(
                            sum(vals) / len(vals), 2
                        )

            elif "highest" in heading_text and "domestic" in heading_text:
                bw = _extract_branchwise(tbl)
                if bw:
                    data["branch_wise_highest_ctc"] = bw
                    data["highest_package_lpa"] = max(bw.values())

            elif "average" in heading_text and "package" in heading_text:
                # Skip "(Branchwise)" duplicate — take the first one
                if "avg_package_lpa" in data:
                    continue
                bw = _extract_branchwise(tbl)
                if bw:
                    data["branch_wise_avg_ctc"] = bw
                    vals = [v for v in bw.values() if v > 0]
                    if vals:
                        data["avg_package_lpa"] = round(
                            sum(vals) / len(vals), 2
                        )

            elif "placement statistics" in heading_text:
                # Course-level placement %
                bw = _extract_branchwise(tbl)
                if bw and "overall_placement_pct" not in data:
                    for k, v in bw.items():
                        if "b.tech" in k.lower():
                            data["overall_placement_pct"] = v
                            break

    return data


# ── Courses ──────────────────────────────────────────────────
def _parse_courses(soup: BeautifulSoup) -> dict[str, Any]:
    """Extract course names from headings between COURSES OFFERED and SEAT MATRIX."""
    data: dict[str, Any] = {}
    courses: list[str] = []

    found_start = False
    for p in soup.find_all("p", class_="cp-clg-h"):
        txt = (_text(p) or "").strip()
        if "COURSES OFFERED" in txt.upper():
            found_start = True
            continue
        if found_start:
            upper = txt.upper()
            # Stop at next major section
            if any(s in upper for s in ["SEAT MATRIX", "CUTOFF", "FEE STRUCTURE"]):
                break
            if txt:
                courses.append(txt)

    if courses:
        data["courses_offered"] = courses
    return data


# ── Main parse function ─────────────────────────────────────
def parse_college_page(
    soup: BeautifulSoup,
    slug: str,
    institute_name: str,
) -> dict[str, Any]:
    """Extract all structured data from a CollegePravesh page.

    Args:
        soup: Parsed HTML.
        slug: URL slug for logging.
        institute_name: Exact name from the database.

    Returns:
        Dictionary of parsed fields (may contain None values).
    """
    logger.info(f"[{slug}] Parsing page for {institute_name}")

    result: dict[str, Any] = {"institute": institute_name}

    # Parse each section
    parsers = [
        ("overview", _parse_overview),
        ("address", _parse_address),
        ("nearby_transport", _parse_nearby_transport),
        ("rankings", _parse_rankings),
        ("fees", _parse_fees),
        ("placements", _parse_placements),
        ("courses", _parse_courses),
    ]

    for section_name, parser_fn in parsers:
        try:
            section_data = parser_fn(soup)
            result.update(section_data)
            if section_data:
                logger.debug(f"[{slug}] {section_name}: extracted {len(section_data)} fields")
            else:
                logger.warning(f"[{slug}] {section_name}: no data found")
        except Exception as e:
            logger.error(f"[{slug}] {section_name}: parse error — {e}")

    return result
