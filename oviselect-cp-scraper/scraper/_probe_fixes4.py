"""Final targeted probe."""
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


# ─── NIT CALICUT: faculty page structure ─────────────────────────────────
print("\n=== NIT CALICUT faculty-and-staff/faculty ===")
soup, final = fetch("https://nitc.ac.in/department/civil-engineering/faculty-and-staff/faculty")
if soup:
    print(f"  Final URL: {final}")
    for tag in ["h1","h2","h3","h4","h5","h6","p","li"]:
        els = soup.find_all(tag)
        if els:
            sample = [e.get_text().strip()[:60] for e in els[:3]]
            print(f"  {tag}: {len(els)} -> {sample}")
    # look for name patterns in the full text
    text = soup.get_text()
    lines = [l.strip() for l in text.split("\n") if l.strip() and len(l.strip()) > 5]
    print(f"  Text lines (first 20): {lines[:20]}")
else:
    print("  FAILED")

# ─── NIT PATNA: /Department/CSE/faculty ──────────────────────────────────
print("\n=== NIT PATNA /Department/CSE/faculty ===")
soup, _ = fetch("https://www.nitp.ac.in/Department/CSE/faculty", timeout=12)
if soup:
    for tag in ["h1","h2","h3","h4","h5","table","tr"]:
        els = soup.find_all(tag)
        if els:
            sample = [e.get_text().strip()[:50] for e in els[:3]]
            print(f"  {tag}: {len(els)} -> {sample}")
    # Check for cards or divs with names
    for cls_kw in ["faculty","card","profile","member","name"]:
        els = soup.find_all(class_=lambda c: c and cls_kw in " ".join(c).lower())
        if els:
            print(f"  class~={cls_kw}: {len(els)} -> {[e.get_text().strip()[:50] for e in els[:3]]}")
    text = soup.get_text()
    lines = [l.strip() for l in text.split("\n") if l.strip() and 3 < len(l.strip()) < 60]
    print(f"  Clean text lines (first 20): {lines[:20]}")
else:
    print("  FAILED")

# ─── NIT ROURKELA: dept-specific faculty pages ───────────────────────────
print("\n=== NIT ROURKELA: dept faculty pages ===")
for dept_path in [
    "/Department/CS/",
    "/Department/CSE/",
    "/Department/EE/",
    "/Departments/CS/People/",
    "/Departments/CSE/Faculty/",
    "/cs/",
]:
    soup, _ = fetch("https://nitrkl.ac.in" + dept_path, timeout=8)
    if soup:
        rows = soup.find_all("tr")
        h3s = soup.find_all("h3")
        print(f"  {dept_path}: OK rows={len(rows)} h3={len(h3s)}")
    else:
        print(f"  {dept_path}: FAILED")

# ─── NIT SRINAGAR: follow Faculty link in navigation ─────────────────────
print("\n=== NIT SRINAGAR: get actual faculty link ===")
url = "https://www.nitsri.ac.in/Department/Deptindex.aspx?page=a&ItemID=cs&nDeptID=cs"
soup, _ = fetch(url, timeout=15)
if soup:
    all_links = [(a.get_text().strip(), a.get("href","")) for a in soup.find_all("a", href=True)]
    print(f"  All links ({len(all_links)}):")
    for t, h in all_links:
        print(f"    [{t[:40]}] -> {h}")

print("\nDone.")

