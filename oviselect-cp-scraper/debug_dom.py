"""Investigate DOM structure around headings."""
from bs4 import BeautifulSoup, NavigableString

html = open("data/cache/iit-bombay.html", "r").read()
soup = BeautifulSoup(html, "lxml")

# Find Overview heading and examine siblings
overview = soup.find("p", class_="cp-clg-h", string=lambda t: t and "overview" in t.lower())
if overview:
    print("Overview heading parent:", overview.parent.name, overview.parent.get("class", []))
    print("\nSiblings after Overview heading:")
    count = 0
    for sib in overview.next_siblings:
        if isinstance(sib, NavigableString):
            s = sib.strip()
            if s:
                print(f"  TEXT: {repr(s[:60])}")
            continue
        cls = sib.get("class", [])
        tag = sib.name
        txt = sib.get_text(strip=True)[:60]
        print(f"  <{tag}> class={cls} text='{txt}'")
        count += 1
        if count > 8:
            break

# Try find_next instead of next_siblings
print("\n--- Using find_next('table') from Overview ---")
tbl = overview.find_next("table")
if tbl:
    print("Found table!")
    parent_chain = []
    p = tbl
    for _ in range(5):
        p = p.parent
        if p:
            parent_chain.append(f"{p.name}.{p.get('class', [])}")
    print("  Parent chain:", " > ".join(parent_chain))
    for tr in tbl.find_all("tr")[:3]:
        cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
        print(f"  {cells}")

# Check if heading and table share the same parent
print("\n--- Heading vs Table parents ---")
print(f"Overview heading parent: {overview.parent.name}.{overview.parent.get('class', [])}")
if tbl:
    print(f"Table parent: {tbl.parent.name}.{tbl.parent.get('class', [])}")
    print(f"Same parent? {overview.parent == tbl.parent}")

