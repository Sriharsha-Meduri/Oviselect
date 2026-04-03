"""Targeted deep probe for faculty URL/DOM patterns."""
import requests, warnings
from bs4 import BeautifulSoup
from urllib.parse import urljoin
warnings.filterwarnings("ignore")
S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0 (compatible; OviBot/1.0)"


def fetch(url, timeout=15, verify=True):
    try:
        r = S.get(url, timeout=timeout, verify=verify, allow_redirects=True)
        if r.status_code == 200:
            return BeautifulSoup(r.text, "html.parser"), r.url
        print(f"  HTTP {r.status_code}: {url}")
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {url}")
    return None, url


# ─── NIT CALICUT: look for faculty links from dept page ──────────────────
print("\n=== NIT CALICUT: faculty links on dept page ===")
soup, final_url = fetch("https://nitc.ac.in/department/civil-engineering")
if soup:
    links = [(a.get_text().strip(), a["href"]) for a in soup.find_all("a", href=True)
             if any(k in a["href"].lower() for k in ["faculty","people","staff","member"])]
    print(f"  Faculty-related links ({len(links)}):")
    for t, h in links[:10]:
        print(f"    [{t[:40]}] -> {h}")
    # Also check all anchors
    all_links = [(a.get_text().strip(), a["href"]) for a in soup.find_all("a", href=True)]
    print(f"  All links ({len(all_links)}) - first 10:")
    for t, h in all_links[:10]:
        print(f"    [{t[:40]}] -> {h}")

# ─── NIT PATNA: look at all links on dept page for faculty ──────────────
print("\n=== NIT PATNA: links on /Department/CSE ===")
soup, _ = fetch("https://www.nitp.ac.in/Department/CSE", timeout=12)
if soup:
    links = [(a.get_text().strip(), a.get("href","")) for a in soup.find_all("a", href=True)]
    print(f"  All links ({len(links)}) - searching for faculty/people:")
    for t, h in links:
        if any(k in h.lower() or k in t.lower() for k in ["faculty","people","staff","member","academic"]):
            print(f"    [{t[:40]}] -> {h}")

# ─── NIT ROURKELA: follow faculty links ─────────────────────────────────
print("\n=== NIT ROURKELA: faculty links from /FacultyStaff/Faculty/ ===")
soup, _ = fetch("https://nitrkl.ac.in/FacultyStaff/Faculty/", timeout=10)
if soup:
    links = [a.get("href","") for a in soup.find_all("a", href=True)
             if "faculty" in a.get("href","").lower()]
    print(f"  Faculty links ({len(links)}) - first 5:")
    for h in links[:5]:
        print(f"    -> {h}")
    # fetch one faculty profile to see structure
    if links:
        href = links[0]
        full = urljoin("https://nitrkl.ac.in", href)
        fsoup, _ = fetch(full, timeout=10)
        if fsoup:
            print(f"\n  Profile page {full}:")
            for tag in ["h1","h2","h3","h4"]:
                els = fsoup.find_all(tag)
                if els:
                    print(f"    {tag}: {[e.get_text().strip()[:50] for e in els[:5]]}")

# ─── NIT SRINAGAR: find faculty table within 41 rows ────────────────────
print("\n=== NIT SRINAGAR: row content analysis ===")
url = "https://www.nitsri.ac.in/Department/Deptindex.aspx?page=a&ItemID=cs&nDeptID=cs"
soup, _ = fetch(url, timeout=15)
if soup:
    rows = soup.find_all("tr")
    print(f"  Total rows: {len(rows)}")
    for i, r in enumerate(rows):
        cells = r.find_all("td")
        text = " | ".join(c.get_text().strip()[:40] for c in cells[:3])
        if text.strip():
            print(f"  Row {i}: {text[:100]}")
    # also check FacultyList.aspx
    print("\n  Trying FacultyList.aspx:")
    url2 = "https://www.nitsri.ac.in/Department/Pages/FacultyList.aspx?nDeptID=cs"
    s2, _ = fetch(url2, timeout=15)
    if s2:
        rows2 = s2.find_all("tr")
        print(f"  rows={len(rows2)}")
        for r in rows2[:10]:
            cells = r.find_all("td")
            text = " | ".join(c.get_text().strip()[:40] for c in cells[:3])
            if text.strip():
                print(f"    {text[:100]}")
        # Look for any name-like content
        print(f"  Page text sample: {s2.get_text()[:500]}")

print("\nDone.")

