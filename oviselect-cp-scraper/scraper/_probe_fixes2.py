"""Deep probe for NIT Calicut, Patna, Rourkela, Srinagar."""
import requests, warnings
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")
S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0 (compatible; OviBot/1.0)"


def fetch(url, timeout=15, verify=True):
    try:
        r = S.get(url, timeout=timeout, verify=verify, allow_redirects=True)
        if r.status_code == 200:
            return BeautifulSoup(r.text, "html.parser")
        print(f"  HTTP {r.status_code}: {url}")
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {url}")
    return None


# ─── NIT CALICUT: find actual tag structure ───────────────────────────────
print("\n=== NIT CALICUT faculty page tags ===")
soup = fetch("https://nitc.ac.in/department/civil-engineering")
if soup:
    # Show all heading tags
    for tag in ["h1","h2","h3","h4","h5","h6"]:
        els = soup.find_all(tag)
        print(f"  {tag}: {len(els)} — first: {els[0].get_text().strip()[:60] if els else 'none'}")
    # Look for any divs with class containing 'faculty' or 'people'
    for cls_kw in ["faculty","people","staff","member","card","profile"]:
        els = soup.find_all(class_=lambda c: c and cls_kw in " ".join(c).lower())
        if els:
            print(f"  class~={cls_kw}: {len(els)} — first: {els[0].get_text().strip()[:60]}")

# ─── NIT PATNA: probe /Department/CSE for faculty ────────────────────────
print("\n=== NIT PATNA /Department/CSE ===")
soup = fetch("https://www.nitp.ac.in/Department/CSE", timeout=12)
if soup:
    for tag in ["h1","h2","h3","h4","h5"]:
        els = soup.find_all(tag)
        print(f"  {tag}: {len(els)} — {[e.get_text().strip()[:40] for e in els[:3]]}")
    # Table rows
    rows = soup.find_all("tr")
    print(f"  <tr>: {len(rows)}")
    for r in rows[:5]:
        cells = r.find_all("td")
        if cells:
            print(f"    > {' | '.join(c.get_text().strip()[:25] for c in cells[:3])}")

# ─── NIT ROURKELA: try alternate URLs with short timeout ─────────────────
print("\n=== NIT ROURKELA alternates ===")
for path in [
    "/FacultyStaff/Faculty/",
    "/Academics/Departments/",
    "/Research/Faculty/",
    "/pages/faculty-list",
    "/departments",
]:
    soup = fetch("https://nitrkl.ac.in" + path, timeout=8)
    if soup:
        rows = soup.find_all("tr")
        h3s = soup.find_all("h3")
        links = [a.get("href","") for a in soup.find_all("a", href=True) if "faculty" in a.get("href","").lower()]
        print(f"  {path}: OK rows={len(rows)} h3={len(h3s)} faculty-links={len(links)}")
    else:
        print(f"  {path}: FAILED")

# ─── NIT SRINAGAR: probe the actual page content ─────────────────────────
print("\n=== NIT SRINAGAR faculty page content ===")
url = "https://www.nitsri.ac.in/Department/Deptindex.aspx?page=a&ItemID=cs&nDeptID=cs"
soup = fetch(url, timeout=15)
if soup:
    for tag in ["h1","h2","h3","h4","h5"]:
        els = soup.find_all(tag)
        print(f"  {tag}: {len(els)} — {[e.get_text().strip()[:40] for e in els[:3]]}")
    rows = soup.find_all("tr")
    print(f"  <tr>: {len(rows)}")
    for r in rows[:5]:
        cells = r.find_all("td")
        if cells:
            print(f"    > {' | '.join(c.get_text().strip()[:25] for c in cells[:3])}")
    # Look for faculty listing pattern
    body = soup.get_text()
    print(f"  body_sample: {body[200:500].strip()[:200]}")

print("\nDone.")

