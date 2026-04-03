"""Probe script to fix NIT Calicut, Patna, Rourkela, and Srinagar scrapers."""
import requests
import warnings
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")
SESSION = requests.Session()
SESSION.headers["User-Agent"] = "Mozilla/5.0 (compatible; OviBot/1.0)"


def fetch(url, timeout=15, verify=True):
    try:
        r = SESSION.get(url, timeout=timeout, verify=verify)
        if r.status_code == 200:
            return BeautifulSoup(r.text, "html.parser")
        print(f"  HTTP {r.status_code}: {url}")
    except Exception as e:
        print(f"  ERROR: {e} -> {url}")
    return None


# ─── NIT CALICUT ────────────────────────────────────────────────────────────
print("\n=== NIT CALICUT ===")
base = "https://nitc.ac.in"
slug = "civil-engineering"
for path in [
    f"/department/{slug}",
    f"/department/{slug}/faculty",
    f"/department/{slug}/people",
]:
    soup = fetch(base + path)
    if soup:
        h3s = soup.find_all("h3")
        h4s = soup.find_all("h4")
        print(f"  {path}: h3={len(h3s)}, h4={len(h4s)}")
        for t in (h3s + h4s)[:5]:
            print(f"    > {t.get_text().strip()[:80]}")
    else:
        print(f"  {path}: FAILED")


# ─── NIT PATNA ──────────────────────────────────────────────────────────────
print("\n=== NIT PATNA ===")
base = "https://www.nitp.ac.in"
for path in [
    "/dept/cse",
    "/dept/CSE",
    "/department/cse",
    "/Department/CSE",
    "/faculty/cse",
    "/academics/department/cse",
    "/",
]:
    soup = fetch(base + path, timeout=10)
    if soup:
        links = [(a.get_text().strip(), a["href"]) for a in soup.find_all("a", href=True) if "dept" in a["href"].lower() or "department" in a["href"].lower() or "faculty" in a["href"].lower()]
        print(f"  {path}: OK, dept/faculty links: {len(links)}")
        for t, h in links[:5]:
            print(f"    [{t[:40]}] -> {h}")
    else:
        print(f"  {path}: FAILED")


# ─── NIT ROURKELA ────────────────────────────────────────────────────────────
print("\n=== NIT ROURKELA ===")
base = "https://nitrkl.ac.in"
for path in [
    "/FacultyStaff/Faculty/",
    "/faculty",
    "/departments/cse/faculty",
    "/",
]:
    soup = fetch(base + path, timeout=12)
    if soup:
        rows = soup.find_all("tr")
        print(f"  {path}: OK, table rows={len(rows)}")
        for r in rows[:3]:
            cells = r.find_all("td")
            if cells:
                print(f"    > {' | '.join(c.get_text().strip()[:30] for c in cells[:3])}")
    else:
        print(f"  {path}: FAILED")


# ─── NIT SRINAGAR ────────────────────────────────────────────────────────────
print("\n=== NIT SRINAGAR ===")
base = "https://nitsri.ac.in"
for (dept, item_id, dept_id) in [
    ("CS", "cs", "cs"),
    ("EE", "ee", "ee"),
    ("CE", "ce", "c"),
]:
    url1 = f"{base}/Department/Pages/FacultyList.aspx?nDeptID={dept_id}"
    url2 = f"{base}/Department/Deptindex.aspx?page=a&ItemID={item_id}&nDeptID={dept_id}"
    for url in [url1, url2]:
        soup = fetch(url, timeout=12)
        if soup:
            rows = soup.find_all("tr")
            links = soup.find_all("a", href=True)
            print(f"  {dept} {url[-50:]}: rows={len(rows)}, links={len(links)}")
            for r in rows[:3]:
                cells = r.find_all("td")
                if cells:
                    print(f"    > {' | '.join(c.get_text().strip()[:30] for c in cells[:3])}")
            break
        else:
            print(f"  {dept} {url[-50:]}: FAILED")

print("\nDone.")

