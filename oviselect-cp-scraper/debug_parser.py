"""Debug the parser against the cached IIT Bombay HTML."""
from bs4 import BeautifulSoup, NavigableString
import sys
sys.path.insert(0, ".")

html = open("data/cache/iit-bombay.html", "r").read()
soup = BeautifulSoup(html, "lxml")

from scraper.parser import (
    _find_heading, _next_table, _text,
    _parse_overview, _parse_rankings, _parse_fees,
    _parse_placements, _parse_courses,
)

print("=== _find_heading tests ===")
for kw in ["Overview", "RANKING", "Institute Fee", "Hostel Fee", "PLACEMENTS", "COURSES OFFERED"]:
    h = _find_heading(soup, kw)
    if h:
        print(f"  '{kw}' -> FOUND: '{_text(h)}'")
        tbl = _next_table(h)
        print(f"    _next_table -> {'FOUND' if tbl else 'NONE'}")
    else:
        print(f"  '{kw}' -> NOT FOUND")

print("\n=== _parse_overview ===")
d = _parse_overview(soup)
print(f"  {d}")

print("\n=== _parse_rankings ===")
d = _parse_rankings(soup)
print(f"  {d}")

print("\n=== _parse_fees ===")
d = _parse_fees(soup)
print(f"  {d}")

print("\n=== _parse_placements ===")
d = _parse_placements(soup)
for k, v in d.items():
    if isinstance(v, dict):
        print(f"  {k}: ({len(v)} branches)")
    else:
        print(f"  {k}: {v}")

print("\n=== _parse_courses ===")
d = _parse_courses(soup)
print(f"  {d}")

